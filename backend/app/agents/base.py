from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel, Field
from app.llm.base import LLMMessage, LLMResponse, LLMStreamChunk
from app.llm.gateway import model_gateway


class AgentContext(BaseModel):
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    role: str = "student"
    memories: List[Dict[str, Any]] = Field(default_factory=list)
    rag_documents: List[Dict[str, Any]] = Field(default_factory=list)
    tool_results: Dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    agent_id: str
    content: str
    model: str
    provider: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    diagrams: List[str] = Field(default_factory=list)  # Mermaid diagram strings
    structured_data: Optional[Dict[str, Any]] = None
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0


class BaseAgent(ABC):
    agent_id: str
    name: str
    description: str
    purpose: str
    capabilities: List[str]
    allowed_tools: List[str]
    retrieval_domain: Optional[str] = None

    @abstractmethod
    def get_system_prompt(self, context: AgentContext) -> str:
        """Construct domain system prompt incorporating instructions and constraints."""
        pass

    def build_messages(
        self,
        user_message: str,
        history: List[LLMMessage],
        context: AgentContext
    ) -> List[LLMMessage]:
        """Construct token-budgeted prompt context conforming to Section 34."""
        messages: List[LLMMessage] = [
            LLMMessage(role="system", content=self.get_system_prompt(context))
        ]

        # Inject evidence from retrieved RAG documents if present
        if context.rag_documents:
            rag_context_parts = []
            for doc in context.rag_documents:
                chunk_text = doc.get("text", "")
                section = doc.get("section", "General")
                source = doc.get("source", "Document")
                rag_context_parts.append(f"[Source: {source} | Section: {section}]\n{chunk_text}")
            rag_block = "\n---\n".join(rag_context_parts)
            messages.append(
                LLMMessage(
                    role="system",
                    content=f"AUTHORITATIVE REFERENCE MATERIAL (Grounding Knowledge):\n{rag_block}\n"
                            f"Base your answers strictly on this verified knowledge where applicable. Always cite your sources."
                )
            )

        # Inject verified user memory if relevant
        if context.memories:
            memory_facts = [
                f"- {m.get('key')}: {m.get('value')} (confidence: {m.get('confidence', 'low')})"
                for m in context.memories
            ]
            messages.append(
                LLMMessage(
                    role="system",
                    content="VERIFIED USER MEMORY & PREFERENCES:\n" + "\n".join(memory_facts)
                )
            )

        # Inject recent conversation history (capped at recent 8 turns)
        messages.extend(history[-8:])

        # Current user request
        messages.append(LLMMessage(role="user", content=user_message))
        return messages

    async def execute(
        self,
        user_message: str,
        history: List[LLMMessage],
        context: AgentContext,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AgentOutput:
        messages = self.build_messages(user_message, history, context)
        response = await model_gateway.generate(messages=messages, provider=provider, model=model)

        return AgentOutput(
            agent_id=self.agent_id,
            content=response.content,
            model=response.model,
            provider=response.provider,
            latency_ms=response.latency_ms,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
        )

    async def stream(
        self,
        user_message: str,
        history: List[LLMMessage],
        context: AgentContext,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        messages = self.build_messages(user_message, history, context)
        async for chunk in model_gateway.stream(messages=messages, provider=provider, model=model):
            yield chunk

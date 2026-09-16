import json
import time
from typing import List, Optional, Any, AsyncGenerator
import httpx
from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse, LLMStreamChunk
from app.config.settings import settings


class OllamaProvider(BaseLLMProvider):
    provider_name: str = "ollama"

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")

    async def generate(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse:
        target_model = model or settings.OLLAMA_MODEL
        formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
        payload = {
            "model": target_model,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        start_time = time.perf_counter()
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        content = data.get("message", {}).get("content", "")
        prompt_eval_count = data.get("prompt_eval_count", 0)
        eval_count = data.get("eval_count", 0)

        return LLMResponse(
            content=content,
            model=target_model,
            provider=self.provider_name,
            input_tokens=prompt_eval_count,
            output_tokens=eval_count,
            estimated_cost_usd=0.0,  # Local Ollama is free
            latency_ms=latency_ms,
        )

    async def stream(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        target_model = model or settings.OLLAMA_MODEL
        formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
        payload = {
            "model": target_model,
            "messages": formatted_messages,
            "stream": True,
            "options": {"temperature": temperature}
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk_data = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    delta = chunk_data.get("message", {}).get("content", "")
                    done = chunk_data.get("done", False)
                    yield LLMStreamChunk(
                        delta=delta,
                        model=target_model,
                        provider=self.provider_name,
                        is_finished=done,
                        input_tokens=chunk_data.get("prompt_eval_count"),
                        output_tokens=chunk_data.get("eval_count"),
                    )

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        return 0.0

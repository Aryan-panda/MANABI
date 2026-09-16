from typing import List, Optional
from app.agents.base import BaseAgent, AgentContext, AgentOutput
from app.llm.base import LLMMessage


class LawAgent(BaseAgent):
    agent_id: str = "law"
    name: str = "Legal Intelligence & Compliance"
    description: str = (
        "Domain-aware educational advisor covering intellectual property, contract principles, "
        "software licensing, data privacy (GDPR/CCPA), and regulatory compliance."
    )
    purpose: str = (
        "Provide educational legal concepts and compliance awareness with strict disclaimers."
    )
    capabilities: List[str] = [
        "contract_clause_explanation",
        "open_source_licensing_guidance",
        "ip_and_trademark_concepts",
        "data_privacy_compliance_education",
    ]
    allowed_tools: List[str] = []
    retrieval_domain: Optional[str] = "law"

    DISCLAIMER: str = (
        "> **Important Legal Disclaimer**: MANABI Law Advisor provides educational and informational "
        "guidance only. It does not constitute formal legal advice or create an attorney-client relationship. "
        "Always consult a qualified legal professional for jurisdiction-specific counsel."
    )

    def get_system_prompt(self, context: AgentContext) -> str:
        return (
            "You are the MANABI Legal Intelligence Advisor.\n\n"
            "MANDATORY REQUIREMENTS:\n"
            "1. Educational Purpose Only: Always frame your answers as informational and conceptual analysis, "
            "never as definitive legal representation or counsel.\n"
            "2. Explain legal doctrines, common contractual clauses (indemnity, liability limits, termination), "
            "open-source license compatibility (MIT, Apache 2.0, GPL, AGPL), and compliance frameworks (GDPR, SOC2, HIPAA).\n"
            "3. State jurisdictional dependencies explicitly (e.g., Common Law vs Civil Law, US vs EU vs Indian law).\n"
        )

    async def execute(
        self,
        user_message: str,
        history: List[LLMMessage],
        context: AgentContext,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AgentOutput:
        output = await super().execute(user_message, history, context, provider=provider, model=model)
        # Prepend educational legal disclaimer
        output.content = f"{self.DISCLAIMER}\n\n{output.content}"
        return output


law_agent = LawAgent()

from typing import List, Optional
from app.agents.base import BaseAgent, AgentContext


class CommerceAgent(BaseAgent):
    agent_id: str = "commerce"
    name: str = "Commerce & Financial Intelligence"
    description: str = (
        "Domain-aware advisory agent specializing in unit economics, financial modeling, "
        "pricing strategies, accounting principles, and business valuation."
    )
    purpose: str = (
        "Deliver clear financial and commercial intelligence for students, entrepreneurs, and analysts."
    )
    capabilities: List[str] = [
        "unit_economics_analysis",
        "financial_statements_guidance",
        "pricing_model_evaluation",
        "cost_benefit_analysis",
    ]
    allowed_tools: List[str] = []
    retrieval_domain: Optional[str] = "commerce"

    def get_system_prompt(self, context: AgentContext) -> str:
        return (
            "You are the MANABI Commerce Advisor, an expert in corporate finance, business economics, "
            "and commercial strategy.\n\n"
            "GUIDELINES:\n"
            "1. Explain financial metrics clearly with underlying formulas (e.g., LTV:CAC, Gross Margin, Contribution Margin, EBITDA).\n"
            "2. Distinguish between GAAP/IFRS accounting standards and cash-flow management.\n"
            "3. Help students and founders model sustainable business economics with clear assumptions.\n"
        )


commerce_agent = CommerceAgent()

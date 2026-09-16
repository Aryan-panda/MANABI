import re
from typing import List, Optional, Dict, Any
from app.agents.base import BaseAgent, AgentContext, AgentOutput
from app.tools.calculator import (
    EngineeringCalculator,
    QPSCalculationInput,
    StorageCalculationInput,
    BandwidthCalculationInput,
    CacheSizingInput,
    LatencyBudgetInput,
)
from app.agents.engineering.diagram_generator import mermaid_generator
from app.llm.base import LLMMessage


class EngineeringArchitectAgent(BaseAgent):
    agent_id: str = "engineering"
    name: str = "Engineering Architect"
    description: str = (
        "Principal System Architect assisting with distributed systems design, data modeling, "
        "capacity planning, trade-off analysis, deterministic arithmetic calculations, and Mermaid diagramming."
    )
    purpose: str = (
        "Provide rigorous, production-ready software engineering architecture with verified calculations and diagrams."
    )
    capabilities: List[str] = [
        "system_design",
        "database_modeling",
        "capacity_estimation",
        "deterministic_calculations",
        "diagram_generation",
        "scalability_and_failure_analysis",
    ]
    allowed_tools: List[str] = [
        "engineering_calculator",
        "mermaid_generator",
    ]
    retrieval_domain: Optional[str] = "engineering"

    def get_system_prompt(self, context: AgentContext) -> str:
        return (
            "You are the MANABI Principal Engineering Architect.\n\n"
            "OPERATING GUIDELINES:\n"
            "1. Produce production-grade, battle-tested system architectures. Avoid superficial high-level fluff.\n"
            "2. Always follow a systematic architecture structure:\n"
            "   - Functional & Non-Functional Requirements\n"
            "   - Capacity & Resource Estimations\n"
            "   - High-Level Architecture (with Mermaid flowchart/diagram)\n"
            "   - Database Schema & Data Modeling (with Mermaid ERD where applicable)\n"
            "   - API Contract Design (REST/gRPC)\n"
            "   - Cache Strategy & Invalidation\n"
            "   - Failure Modes, Resilience & Mitigations\n"
            "   - Explicit Architectural Trade-offs\n"
            "3. NUMERICAL ACCURACY: Never fabricate unverified numbers or guess arithmetic. Use deterministic calculations.\n"
            "4. DIAGRAMS: Whenever describing an architecture, sequence, or data model, include clean, validated Mermaid diagrams "
            "enclosed within standard ```mermaid code blocks.\n"
            "5. Technology Stacks: Specialize in modern backends (Python/FastAPI, Java/Spring Boot), relational/vector data (PostgreSQL, pgvector), "
            "caching (Redis), and containerized deployments (Docker Compose, Nginx).\n"
        )

    def run_calculator(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic calculation execution."""
        if tool_name == "qps":
            res = EngineeringCalculator.calculate_qps(QPSCalculationInput(**params))
            return res.model_dump()
        elif tool_name == "storage":
            res = EngineeringCalculator.calculate_storage(StorageCalculationInput(**params))
            return res.model_dump()
        elif tool_name == "bandwidth":
            res = EngineeringCalculator.calculate_bandwidth(BandwidthCalculationInput(**params))
            return res.model_dump()
        elif tool_name == "cache":
            res = EngineeringCalculator.calculate_cache_size(CacheSizingInput(**params))
            return res.model_dump()
        elif tool_name == "latency":
            res = EngineeringCalculator.calculate_latency_budget(LatencyBudgetInput(**params))
            return res.model_dump()
        else:
            raise ValueError(f"Unknown calculation tool: {tool_name}")

    async def execute(
        self,
        user_message: str,
        history: List[LLMMessage],
        context: AgentContext,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AgentOutput:
        output = await super().execute(user_message, history, context, provider=provider, model=model)

        # Extract any embedded Mermaid diagrams from response
        mermaid_blocks = re.findall(r"```mermaid\n(.*?)\n```", output.content, re.DOTALL)
        if mermaid_blocks:
            output.diagrams.extend([block.strip() for block in mermaid_blocks])

        return output


engineering_agent = EngineeringArchitectAgent()

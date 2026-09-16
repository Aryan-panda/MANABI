from typing import Dict, Optional, List
from app.agents.base import BaseAgent
from app.agents.academic.agent import academic_agent
from app.agents.engineering.agent import engineering_agent
from app.agents.commerce.agent import commerce_agent
from app.agents.management.agent import management_agent
from app.agents.law.agent import law_agent

AGENT_REGISTRY: Dict[str, BaseAgent] = {
    academic_agent.agent_id: academic_agent,
    engineering_agent.agent_id: engineering_agent,
    commerce_agent.agent_id: commerce_agent,
    management_agent.agent_id: management_agent,
    law_agent.agent_id: law_agent,
}


def get_agent(agent_id: str) -> Optional[BaseAgent]:
    return AGENT_REGISTRY.get(agent_id.lower())


def list_agents() -> List[BaseAgent]:
    return list(AGENT_REGISTRY.values())


__all__ = [
    "BaseAgent",
    "AGENT_REGISTRY",
    "get_agent",
    "list_agents",
    "academic_agent",
    "engineering_agent",
    "commerce_agent",
    "management_agent",
    "law_agent",
]

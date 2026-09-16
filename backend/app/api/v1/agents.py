from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.agents import list_agents, get_agent

router = APIRouter(prefix="/agents", tags=["Agents"])


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    purpose: str
    capabilities: List[str]
    allowed_tools: List[str]
    retrieval_domain: str | None


@router.get("", response_model=List[AgentResponse])
async def get_all_agents():
    agents = list_agents()
    return [
        AgentResponse(
            id=a.agent_id,
            name=a.name,
            description=a.description,
            purpose=a.purpose,
            capabilities=a.capabilities,
            allowed_tools=a.allowed_tools,
            retrieval_domain=a.retrieval_domain,
        )
        for a in agents
    ]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent_by_id(agent_id: str):
    agent = get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found."
        )
    return AgentResponse(
        id=agent.agent_id,
        name=agent.name,
        description=agent.description,
        purpose=agent.purpose,
        capabilities=agent.capabilities,
        allowed_tools=agent.allowed_tools,
        retrieval_domain=agent.retrieval_domain,
    )

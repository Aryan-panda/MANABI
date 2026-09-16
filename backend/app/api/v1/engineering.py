from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.agents.engineering.agent import engineering_agent
from app.agents.engineering.diagram_generator import mermaid_generator
from app.security.deps import get_current_user
from app.database.models.auth import User

router = APIRouter(prefix="/engineering", tags=["Engineering"])


class CalculationRequest(BaseModel):
    tool: str  # 'qps', 'storage', 'bandwidth', 'cache', 'latency'
    parameters: Dict[str, Any]


class DiagramRequest(BaseModel):
    diagram_type: str = "system"  # 'system', 'erd'
    title: Optional[str] = "MANABI Architecture"


@router.post("/calculate")
async def run_calculation(
    payload: CalculationRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        result = engineering_agent.run_calculator(payload.tool, payload.parameters)
        return {"tool": payload.tool, "result": result}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation error: {str(exc)}"
        )


@router.post("/diagram")
async def generate_diagram(
    payload: DiagramRequest,
    current_user: User = Depends(get_current_user)
):
    if payload.diagram_type == "erd":
        diagram = mermaid_generator.generate_er_diagram()
    else:
        diagram = mermaid_generator.generate_system_architecture_diagram(payload.title or "Architecture")

    is_valid = mermaid_generator.validate_mermaid_syntax(diagram)
    return {
        "diagram_type": payload.diagram_type,
        "mermaid_code": diagram,
        "is_valid": is_valid,
    }

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.academic_data import get_academic_data_provider
from app.agents.academic.agent import academic_agent
from app.security.deps import get_current_user
from app.database.models.auth import User

router = APIRouter(prefix="/academic", tags=["Academic"])


class PlanReviewRequest(BaseModel):
    raw_plan: str
    student_id: Optional[str] = "STU1001"


@router.get("/profile")
async def get_profile(
    student_id: Optional[str] = "STU1001",
    current_user: User = Depends(get_current_user)
):
    provider = get_academic_data_provider()
    profile = await provider.get_student_profile(student_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found or institutional integration unavailable."
        )
    return profile.model_dump()


@router.get("/courses")
async def get_courses(
    student_id: Optional[str] = "STU1001",
    current_user: User = Depends(get_current_user)
):
    provider = get_academic_data_provider()
    courses = await provider.get_courses(student_id)
    return [c.model_dump() for c in courses]


@router.get("/attendance")
async def get_attendance(
    student_id: Optional[str] = "STU1001",
    current_user: User = Depends(get_current_user)
):
    provider = get_academic_data_provider()
    attendance = await provider.get_attendance(student_id)
    return [a.model_dump() for a in attendance]


@router.get("/results")
async def get_results(
    student_id: Optional[str] = "STU1001",
    current_user: User = Depends(get_current_user)
):
    provider = get_academic_data_provider()
    results = await provider.get_results(student_id)
    return [r.model_dump() for r in results]


@router.post("/plan/review")
async def review_academic_plan(
    payload: PlanReviewRequest,
    current_user: User = Depends(get_current_user)
):
    """Run LangGraph stateful plan review workflow."""
    review_output = await academic_agent.review_plan(
        raw_plan=payload.raw_plan,
        student_id=payload.student_id,
    )
    return review_output

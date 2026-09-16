from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.database.models.auth import User, Role
from app.security.deps import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    is_active: bool


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    role_stmt = select(Role).where(Role.id == current_user.role_id)
    role = (await db.execute(role_stmt)).scalar_one_or_none()
    role_name = role.name if role else "student"

    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=role_name,
        is_active=current_user.is_active,
    )


@router.patch("/me", response_model=UserProfileResponse)
async def update_me(
    update_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if update_data.name:
        current_user.name = update_data.name
        await db.commit()
        await db.refresh(current_user)

    role_stmt = select(Role).where(Role.id == current_user.role_id)
    role = (await db.execute(role_stmt)).scalar_one_or_none()
    role_name = role.name if role else "student"

    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=role_name,
        is_active=current_user.is_active,
    )

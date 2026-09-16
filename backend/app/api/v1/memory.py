import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.database.models.auth import User
from app.memory.manager import memory_manager
from app.security.deps import get_current_user

router = APIRouter(prefix="/memory", tags=["Memory"])


class MemoryCreate(BaseModel):
    key: str
    value: str
    type: Optional[str] = "preference"


class MemoryUpdate(BaseModel):
    value: str
    confidence: Optional[str] = None


class MemoryResponse(BaseModel):
    id: str
    type: str
    key: str
    value: str
    confidence: str
    evidence_count: int
    last_seen: str


@router.get("", response_model=List[MemoryResponse])
async def list_memories(
    type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    memories = await memory_manager.get_user_memories(db, current_user.id, memory_type=type)
    return [
        MemoryResponse(
            id=str(m.id),
            type=m.type,
            key=m.key,
            value=m.value,
            confidence=m.confidence,
            evidence_count=m.evidence_count,
            last_seen=m.last_seen.isoformat(),
        )
        for m in memories
    ]


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    payload: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    mem = await memory_manager.record_memory(
        db,
        user_id=current_user.id,
        key=payload.key,
        value=payload.value,
        memory_type=payload.type or "preference",
    )
    return MemoryResponse(
        id=str(mem.id),
        type=mem.type,
        key=mem.key,
        value=mem.value,
        confidence=mem.confidence,
        evidence_count=mem.evidence_count,
        last_seen=mem.last_seen.isoformat(),
    )


@router.patch("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    payload: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    mem_uuid = uuid.UUID(memory_id)
    mem = await memory_manager.update_memory(
        db,
        user_id=current_user.id,
        memory_id=mem_uuid,
        value=payload.value,
        confidence=payload.confidence,
    )
    if not mem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory record not found.")
    return MemoryResponse(
        id=str(mem.id),
        type=mem.type,
        key=mem.key,
        value=mem.value,
        confidence=mem.confidence,
        evidence_count=mem.evidence_count,
        last_seen=mem.last_seen.isoformat(),
    )


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    mem_uuid = uuid.UUID(memory_id)
    deleted = await memory_manager.delete_memory(db, current_user.id, mem_uuid)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory record not found.")
    return {"message": "Memory record deleted successfully."}

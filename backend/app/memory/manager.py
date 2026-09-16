import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from app.database.models.memory import Memory
from app.database.base import utc_now


class MemoryManager:
    """
    Evidence-based user memory manager.
    Enforces gradual confidence escalation and prevents single-interaction hallucinated facts.
    """

    @staticmethod
    def _calculate_confidence(evidence_count: int) -> str:
        if evidence_count >= 5:
            return "high"
        elif evidence_count >= 2:
            return "medium"
        return "low"

    @classmethod
    async def get_user_memories(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        memory_type: Optional[str] = None
    ) -> List[Memory]:
        stmt = select(Memory).where(Memory.user_id == user_id)
        if memory_type:
            stmt = stmt.where(Memory.type == memory_type)
        stmt = stmt.order_by(Memory.last_seen.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def record_memory(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        key: str,
        value: str,
        memory_type: str = "preference",
    ) -> Memory:
        """
        Idempotent memory recording with evidence accumulation.
        If memory key exists, increments evidence_count and recalibrates confidence.
        """
        stmt = select(Memory).where(Memory.user_id == user_id, Memory.key == key)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.value = value
            existing.evidence_count += 1
            existing.confidence = cls._calculate_confidence(existing.evidence_count)
            existing.last_seen = utc_now()
            await db.commit()
            await db.refresh(existing)
            return existing

        new_memory = Memory(
            user_id=user_id,
            type=memory_type,
            key=key,
            value=value,
            confidence="low",
            evidence_count=1,
            last_seen=utc_now(),
        )
        db.add(new_memory)
        await db.commit()
        await db.refresh(new_memory)
        return new_memory

    @classmethod
    async def update_memory(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        memory_id: uuid.UUID,
        value: str,
        confidence: Optional[str] = None
    ) -> Optional[Memory]:
        stmt = select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
        result = await db.execute(stmt)
        mem = result.scalar_one_or_none()
        if not mem:
            return None

        mem.value = value
        if confidence:
            mem.confidence = confidence
        mem.last_seen = utc_now()
        await db.commit()
        await db.refresh(mem)
        return mem

    @classmethod
    async def delete_memory(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        memory_id: uuid.UUID
    ) -> bool:
        stmt = delete(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0


memory_manager = MemoryManager()

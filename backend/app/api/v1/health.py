from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database.session import get_db
from app.config.settings import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def liveness_probe():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@router.get("/health/ready")
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    db_status = "unhealthy"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as exc:
        db_status = f"unhealthy ({type(exc).__name__})"

    return {
        "status": "ready" if db_status == "healthy" else "degraded",
        "database": db_status,
        "llm_provider": settings.LLM_PROVIDER,
        "academic_data_provider": settings.ACADEMIC_DATA_PROVIDER,
    }

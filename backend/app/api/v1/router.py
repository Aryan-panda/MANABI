from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.agents import router as agents_router
from app.api.v1.academic import router as academic_router
from app.api.v1.engineering import router as engineering_router
from app.api.v1.memory import router as memory_router
from app.api.v1.health import router as health_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(conversations_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(academic_router)
api_v1_router.include_router(engineering_router)
api_v1_router.include_router(memory_router)
api_v1_router.include_router(health_router)

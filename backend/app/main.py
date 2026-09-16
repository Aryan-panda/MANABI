import time
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from app.config.settings import settings
from app.api.v1.router import api_v1_router
from app.database.session import engine
from app.database.base import Base
from app.database.models import Role, Agent, Document, DocumentVersion, DocumentChunk
from app.rag.chunking.structure_aware import structure_chunker
from app.observability import registry, HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION_SECONDS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s (%(correlation_id)s): %(message)s"
)
logger = logging.getLogger("manabi")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist & seed baseline data
    logger.info("Starting MANABI Application Server...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema synchronized.")
    except Exception as exc:
        logger.warning(f"Database schema auto-sync encountered exception (ignorable if using Alembic or offline): {exc}")

    yield

    # Shutdown: Clean up connections
    logger.info("Shutting down MANABI Application Server...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-domain Agentic Intelligence & Learning Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time
    latency_ms = duration * 1000.0
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time-Ms"] = f"{latency_ms:.2f}"

    # Track Prometheus HTTP metrics
    HTTP_REQUESTS_TOTAL.inc(
        method=request.method,
        endpoint=request.url.path,
        status=str(response.status_code),
    )
    HTTP_REQUEST_DURATION_SECONDS.observe(
        duration,
        method=request.method,
        endpoint=request.url.path,
    )

    return response


# Mount API routers
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "platform": settings.APP_NAME,
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "operational",
    }


@app.get("/metrics")
async def metrics():
    """Prometheus exposition format metrics endpoint conforming to Section 38."""
    return PlainTextResponse(registry.generate_metrics_text(), media_type="text/plain; version=0.0.4")


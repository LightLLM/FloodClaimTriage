"""Main FastAPI application"""
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, events, properties, triage
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager"""
    logger.info("Starting Flood Triage API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Model version: {settings.MODEL_VERSION}")
    yield
    logger.info("Shutting down Flood Triage API")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(events.router, prefix=settings.API_V1_PREFIX)
app.include_router(properties.router, prefix=settings.API_V1_PREFIX)
app.include_router(triage.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "model_version": settings.MODEL_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }

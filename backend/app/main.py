"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables
from app.routers import orders, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create tables on startup."""
    await create_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-Driven Compliance Screening System — real-time order screening "
        "against sanctions, AML/KYC, and regulatory requirements."
    ),
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(orders.router)
app.include_router(reports.router)


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "mode": settings.AGENT_MODE,
    }


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "AI-Driven Compliance Screening System",
        "docs": "/docs",
        "health": "/health",
    }

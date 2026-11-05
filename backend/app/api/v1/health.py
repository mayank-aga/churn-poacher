"""
Deep Health & Observability API Endpoints.
Monitors operational health of Database, Redis, Background Worker, and LLM providers.
"""

import time
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as aioredis

from app.db.session import get_db
from app.core.config import settings
from app.core.llm import get_active_provider_status

router = APIRouter(prefix="/health", tags=["Observability & Health"])


@router.get("/deep")
async def deep_health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Executes real-time end-to-end operational probes across all platform dependencies.
    """
    results: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT,
        "checks": {},
    }

    # 1. Database Probe
    db_start = time.time()
    try:
        await db.execute(text("SELECT 1"))
        db_latency_ms = round((time.time() - db_start) * 1000, 2)
        results["checks"]["database"] = {
            "status": "healthy",
            "dialect": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql",
            "latency_ms": db_latency_ms,
        }
    except Exception as e:
        results["status"] = "degraded"
        results["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }

    # 2. Redis Probe
    redis_start = time.time()
    try:
        r = aioredis.from_url(settings.REDIS_URL, socket_timeout=2.0)
        await r.ping()
        # Check background worker heartbeat
        worker_heartbeat = await r.get("churn_poacher:worker:heartbeat")
        await r.aclose()
        redis_latency_ms = round((time.time() - redis_start) * 1000, 2)

        worker_status = "idle_or_unregistered"
        if worker_heartbeat:
            worker_time = float(worker_heartbeat)
            if time.time() - worker_time < 45:
                worker_status = "active_healthy"
            else:
                worker_status = "stale_heartbeat"

        results["checks"]["redis"] = {
            "status": "healthy",
            "latency_ms": redis_latency_ms,
            "worker_status": worker_status,
        }
    except Exception as e:
        # In local SQLite mode without Redis container, mark as unconfigured rather than fatal
        results["checks"]["redis"] = {
            "status": "unconfigured_or_unreachable",
            "note": "Redis is optional in standalone SQLite mode; required for distributed workers",
            "error": str(e),
        }

    # 3. LLM Provider Status
    try:
        llm_status = await get_active_provider_status()
        results["checks"]["llm_providers"] = {
            "status": "healthy",
            "active_provider": llm_status["active_provider"],
            "providers": llm_status["providers"],
        }
    except Exception as e:
        results["checks"]["llm_providers"] = {
            "status": "degraded",
            "error": str(e),
        }

    return results

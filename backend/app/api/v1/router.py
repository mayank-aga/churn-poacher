"""
API v1 Router aggregation.
"""

from fastapi import APIRouter
from app.api.v1.signals import router as signals_router
from app.api.v1.companies import router as companies_router
from app.api.v1.dossiers import router as dossiers_router
from app.api.v1.logs import router as logs_router
from app.api.v1.stats import router as stats_router

api_v1_router = APIRouter(prefix="/v1")
api_v1_router.include_router(signals_router)
api_v1_router.include_router(companies_router)
api_v1_router.include_router(dossiers_router)
api_v1_router.include_router(logs_router)
api_v1_router.include_router(stats_router)

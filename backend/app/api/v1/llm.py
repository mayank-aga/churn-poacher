"""
LLM Provider and Intelligence API Endpoints.
Allows status inspection and structured analysis operations across providers.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.llm import (
    get_active_provider_status,
    LLMIntelligenceService,
    SignalAnalysisResult,
    MigrationExplanationResult,
)

router = APIRouter(prefix="/llm", tags=["LLM Provider Intelligence"])


class AnalyzeSignalRequest(BaseModel):
    content: str
    source: str = "HACKERNEWS"
    provider: Optional[str] = None


class ExplainMigrationRequest(BaseModel):
    company_name: str
    target_backend: str = "SigNoz Cloud"
    current_setup: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None


@router.get("/status")
async def get_llm_status():
    """Returns the operational readiness and availability of all supported LLM providers."""
    return await get_active_provider_status()


@router.post("/analyze-signal", response_model=SignalAnalysisResult)
async def analyze_signal_with_llm(req: AnalyzeSignalRequest):
    """Executes structured LLM analysis of a public vendor complaint or status alert."""
    return await LLMIntelligenceService.analyze_signal(
        raw_content=req.content,
        source=req.source,
        provider_name=req.provider,
    )


@router.post("/explain-migration", response_model=MigrationExplanationResult)
async def explain_migration_with_llm(req: ExplainMigrationRequest):
    """Generates an engineering explanation of the OpenTelemetry dual-shipping architecture."""
    return await LLMIntelligenceService.explain_migration(
        company_name=req.company_name,
        current_setup=req.current_setup or {},
        target_backend=req.target_backend,
        provider_name=req.provider,
    )

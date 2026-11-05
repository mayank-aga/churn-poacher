"""
Unit and Integration Tests for LLM Provider Abstraction.
Verifies multi-provider support (OpenAI, Gemini, Claude, Deterministic Fallback)
and guarantees structured outputs with zero required external API keys.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import Response, Request

from app.core.llm import (
    BaseLLMProvider,
    get_llm_provider,
    get_active_provider_status,
    DeterministicFallbackProvider,
    OpenAIProvider,
    GeminiProvider,
    ClaudeProvider,
    LLMIntelligenceService,
    SignalAnalysisResult,
    EvidenceExtractionResult,
    CompanySummaryResult,
    MigrationExplanationResult,
    PersonalizedOutreachResult,
)


@pytest.mark.asyncio
async def test_deterministic_fallback_provider_availability():
    provider = DeterministicFallbackProvider()
    assert await provider.is_available() is True
    assert provider.name == "deterministic-fallback"


@pytest.mark.asyncio
async def test_deterministic_fallback_structured_signal_analysis():
    provider = DeterministicFallbackProvider()
    prompt = "Another month, another $45,000 custom metrics Datadog bill on our Kubernetes cluster!"
    
    result = await provider.generate_structured(
        prompt=prompt,
        response_model=SignalAnalysisResult,
    )
    
    assert isinstance(result, SignalAnalysisResult)
    assert result.distress_category == "PRICING_SHOCK"
    assert result.urgency_score >= 0.7
    assert len(result.key_pain_points) > 0
    assert "kubernetes" in result.technical_indicators or "custom metrics" in result.technical_indicators


@pytest.mark.asyncio
async def test_deterministic_fallback_evidence_extraction():
    provider = DeterministicFallbackProvider()
    prompt = "We got hit with a $50k invoice from Datadog for unindexed spans."
    
    result = await provider.generate_structured(
        prompt=prompt,
        response_model=EvidenceExtractionResult,
    )
    
    assert isinstance(result, EvidenceExtractionResult)
    assert len(result.verified_claims) > 0
    assert "$50k" in result.metrics_or_costs_mentioned or "$50K" in [m.upper() for m in result.metrics_or_costs_mentioned]


@pytest.mark.asyncio
async def test_deterministic_fallback_company_summary():
    provider = DeterministicFallbackProvider()
    prompt = "Company Name: Acme Cloud\nObserved Tech Stack: Kubernetes, AWS\nComplaint: Datadog pricing hike"
    
    result = await provider.generate_structured(
        prompt=prompt,
        response_model=CompanySummaryResult,
    )
    
    assert isinstance(result, CompanySummaryResult)
    assert "Acme Cloud" in result.company_name
    assert len(result.executive_brief) > 10


@pytest.mark.asyncio
async def test_deterministic_fallback_migration_explanation():
    provider = DeterministicFallbackProvider()
    result = await provider.generate_structured(
        prompt="Explain Datadog to SigNoz migration",
        response_model=MigrationExplanationResult,
    )
    
    assert isinstance(result, MigrationExplanationResult)
    assert "8126" in result.architecture_overview
    assert len(result.key_technical_advantages) >= 3


@pytest.mark.asyncio
async def test_deterministic_fallback_personalized_outreach():
    provider = DeterministicFallbackProvider()
    result = await provider.generate_structured(
        prompt="Refine executive email for Acme Corp",
        response_model=PersonalizedOutreachResult,
    )
    
    assert isinstance(result, PersonalizedOutreachResult)
    assert len(result.subject_lines) >= 3
    assert len(result.polished_body) > 50


@pytest.mark.asyncio
async def test_factory_auto_selection_when_keys_missing():
    # When no API keys are in settings, auto falls back to deterministic provider
    with patch("app.core.config.settings.OPENAI_API_KEY", None), \
         patch("app.core.config.settings.GEMINI_API_KEY", None), \
         patch("app.core.config.settings.ANTHROPIC_API_KEY", None), \
         patch("app.core.config.settings.LLM_PROVIDER", "auto"):
        
        provider = get_llm_provider()
        assert isinstance(provider, DeterministicFallbackProvider)


@pytest.mark.asyncio
async def test_factory_explicit_requested_providers():
    p_fallback = get_llm_provider("fallback")
    assert isinstance(p_fallback, DeterministicFallbackProvider)

    p_openai = get_llm_provider("openai")
    assert isinstance(p_openai, OpenAIProvider)

    p_gemini = get_llm_provider("gemini")
    assert isinstance(p_gemini, GeminiProvider)

    p_claude = get_llm_provider("claude")
    assert isinstance(p_claude, ClaudeProvider)


@pytest.mark.asyncio
async def test_mocked_openai_structured_generation():
    provider = OpenAIProvider(api_key="sk-mock-key-for-testing", model="gpt-4o-mini")
    assert await provider.is_available() is True

    mock_json = {
        "distress_category": "OUTAGE_DOWNTIME",
        "urgency_score": 0.95,
        "detected_company_mentions": ["Stripe"],
        "key_pain_points": ["APM was blind during primary database failover"],
        "vendor_mentioned": "Datadog",
        "technical_indicators": ["APM", "PostgreSQL"],
        "sentiment_summary": "Critical outage dissatisfaction",
    }

    mock_resp = Response(
        status_code=200,
        content=json.dumps({"choices": [{"message": {"content": json.dumps(mock_json)}}]}),
        request=Request("POST", "https://api.openai.com/v1/chat/completions"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await provider.generate_structured(
            prompt="Datadog APM went completely dark during our failover at Stripe",
            response_model=SignalAnalysisResult,
        )
        assert res.distress_category == "OUTAGE_DOWNTIME"
        assert res.urgency_score == 0.95
        assert "Stripe" in res.detected_company_mentions


@pytest.mark.asyncio
async def test_mocked_gemini_structured_generation():
    provider = GeminiProvider(api_key="mock-gemini-key", model="gemini-1.5-flash")
    assert await provider.is_available() is True

    mock_json = {
        "headline": "Zero-Downtime OTel Port 8126 Migration",
        "architecture_overview": "Drop-in receiver redirects dd-trace to ClickHouse via OpenTelemetry Contrib.",
        "key_technical_advantages": ["100% open standard", "Eliminate node tax", "Zero service code change"],
        "risk_mitigation_highlights": ["Dual-shipping 14 day parallel validation"],
    }

    mock_resp = Response(
        status_code=200,
        content=json.dumps({"candidates": [{"content": {"parts": [{"text": json.dumps(mock_json)}]}}]}),
        request=Request("POST", "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await provider.generate_structured(
            prompt="Explain OTel migration",
            response_model=MigrationExplanationResult,
        )
        assert "Zero-Downtime" in res.headline
        assert len(res.key_technical_advantages) == 3


@pytest.mark.asyncio
async def test_mocked_claude_structured_generation():
    provider = ClaudeProvider(api_key="mock-claude-key", model="claude-3-5-sonnet-20241022")
    assert await provider.is_available() is True

    mock_json = {
        "company_name": "FinTech Corp",
        "executive_brief": "FinTech Corp processes high-volume payments with strict latency SLA.",
        "dissatisfaction_context": "Annual Datadog bill increased 60% due to span indexing costs.",
        "challenger_fit_rationale": "SigNoz Cloud offers high-performance ClickHouse backend with usage-only pricing.",
    }

    mock_resp = Response(
        status_code=200,
        content=json.dumps({"content": [{"text": json.dumps(mock_json)}]}),
        request=Request("POST", "https://api.anthropic.com/v1/messages"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await provider.generate_structured(
            prompt="Summarize FinTech Corp",
            response_model=CompanySummaryResult,
        )
        assert res.company_name == "FinTech Corp"
        assert "ClickHouse" in res.challenger_fit_rationale


@pytest.mark.asyncio
async def test_llm_intelligence_service_graceful_fallback_on_network_error():
    # When an external provider raises a network timeout or 500 error, service gracefully falls back to deterministic output
    with patch("app.core.llm.openai_provider.OpenAIProvider.generate_structured", side_effect=Exception("API Timeout")):
        res = await LLMIntelligenceService.analyze_signal(
            raw_content="Datadog custom metric billing spiked 40% this quarter!",
            source="REDDIT",
            provider_name="openai",
        )
        assert isinstance(res, SignalAnalysisResult)
        assert res.distress_category == "PRICING_SHOCK"


@pytest.mark.asyncio
async def test_get_active_provider_status():
    status = await get_active_provider_status()
    assert "active_provider" in status
    assert "providers" in status
    assert "fallback" in status["providers"]
    assert status["providers"]["fallback"]["available"] is True

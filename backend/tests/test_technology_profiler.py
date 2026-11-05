"""
Tests for Technology Profiler.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.agents.profiler.technology_profiler import TechnologyProfiler
from app.agents.profiler.schemas import TechEvidence


@pytest.mark.asyncio
async def test_technology_profiling_from_github_and_text():
    mock_gh_evidence = [
        TechEvidence(
            technology="Datadog",
            category="Observability",
            classification="VERIFIED",
            source="GitHub",
            source_url="https://github.com/acme/infra/blob/main/datadog.yaml",
            confidence=0.90,
        )
    ]

    with patch("app.services.enrichment.github.GitHubEnrichmentService.search_org_technologies", new_callable=AsyncMock) as mock_gh:
        mock_gh.return_value = mock_gh_evidence

        result = await TechnologyProfiler.profile_company(
            company_name="Acme Cloud",
            domain="acmecloud.io",
            raw_signal_text="We run Kubernetes clusters on AWS with Datadog APM.",
        )

        assert result.has_datadog_evidence is True
        assert result.has_k8s_evidence is True
        assert result.technology_confidence >= 0.80
        assert "Datadog" in result.detected_technologies["observability"]
        assert "Kubernetes" in result.detected_technologies["containers"]
        assert "AWS" in result.detected_technologies["cloud"]


@pytest.mark.asyncio
async def test_technology_profiling_without_datadog_returns_low_confidence():
    with patch("app.services.enrichment.github.GitHubEnrichmentService.search_org_technologies", new_callable=AsyncMock) as mock_gh:
        mock_gh.return_value = []

        result = await TechnologyProfiler.profile_company(
            company_name="Generic Inc",
            domain="generic.io",
            raw_signal_text="Looking for an engineer to build a website in PHP.",
        )

        assert result.has_datadog_evidence is False
        assert result.technology_confidence <= 0.30

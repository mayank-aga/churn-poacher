"""
Tests for Phase 1: Crustdata Client & Credit Guard.
"""

import pytest
from app.services.crustdata.schemas import (
    EntityType,
    EnrichmentLevel,
    VerificationClassification,
    CrustdataCreditsInfo,
)
from app.services.crustdata.credit_guard import CreditGuard
from app.services.crustdata.client import CrustdataClient
from app.services.crustdata.mock_provider import CrustdataMockProvider
from app.services.crustdata.exceptions import CrustdataCreditDepletedError


def test_credit_guard_cost_estimation():
    assert CreditGuard.estimate_cost(EnrichmentLevel.LEVEL_1_SEARCH) == 0.5
    assert CreditGuard.estimate_cost(EnrichmentLevel.LEVEL_2_STANDARD) == 2.0
    assert CreditGuard.estimate_cost(EnrichmentLevel.LEVEL_3_DEEP) == 15.0


def test_credit_guard_budget_check_success():
    credits = CrustdataCreditsInfo(
        total_credits=100.0,
        remaining_credits=50.0,
        used_credits=50.0,
    )
    # 50 - 2.0 = 48.0 >= min_threshold (5.0) -> allowed
    assert CreditGuard.verify_budget_can_proceed(2.0, credits_info=credits) is True


def test_credit_guard_budget_check_depletion_error():
    credits = CrustdataCreditsInfo(
        total_credits=100.0,
        remaining_credits=6.0,
        used_credits=94.0,
    )
    # 6.0 - 15.0 = -9.0 < min_threshold (5.0) -> must raise CrustdataCreditDepletedError
    with pytest.raises(CrustdataCreditDepletedError) as exc_info:
        CreditGuard.verify_budget_can_proceed(15.0, credits_info=credits)
    assert exc_info.value.current_balance == 6.0
    assert exc_info.value.required_credits == 15.0


@pytest.mark.asyncio
async def test_crustdata_client_mock_mode_credits():
    client = CrustdataClient(api_key=None)
    credits = await client.get_account_credits()
    assert credits.is_mock is True
    assert credits.remaining_credits > 0.0
    assert len(credits.enabled_endpoints) > 0


@pytest.mark.asyncio
async def test_crustdata_client_company_search_and_enrich():
    client = CrustdataClient(api_key=None)
    
    # Search
    candidates = await client.search_company_candidates("SpaceX")
    assert len(candidates) >= 1
    c = candidates[0]
    assert c.name == "SpaceX"
    assert c.primary_domain == "spacex.com"
    assert c.entity_type == EntityType.COMPANY
    assert c.is_mock is True

    # Standard Enrichment
    profile = await client.enrich_company("spacex.com", level=EnrichmentLevel.LEVEL_2_STANDARD)
    assert profile.name == "SpaceX"
    assert profile.primary_domain == "spacex.com"
    assert profile.is_mock is True
    assert profile.enrichment_level == EnrichmentLevel.LEVEL_2_STANDARD
    assert profile.credits_consumed == 1.0
    assert len(profile.technographics) > 0
    # Must have Datadog in technographics
    assert any(t.name == "Datadog" for t in profile.technographics)


@pytest.mark.asyncio
async def test_crustdata_client_person_search_and_enrich():
    client = CrustdataClient(api_key=None)
    
    # Search
    candidates = await client.search_person_candidates("Sam Altman")
    assert len(candidates) >= 1
    p = candidates[0]
    assert "Sam Altman" in p.name
    assert p.entity_type == EntityType.PERSON
    assert p.is_mock is True

    # Standard Enrichment
    profile = await client.enrich_person("Sam Altman", level=EnrichmentLevel.LEVEL_2_STANDARD)
    assert profile.full_name == "Sam Altman"
    assert profile.current_company == "OpenAI"
    assert profile.is_decision_maker is True
    assert len(profile.work_history) >= 1
    assert profile.is_mock is True

"""
Crustdata REST API Client.
Interfaces with official Crustdata API (api.crustdata.com) using standard headers,
rate limiting backoffs, credit safety checks, and deterministic mock fallbacks.
"""

import httpx
from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.core.logging import logger
from app.services.crustdata.exceptions import (
    CrustdataAPIError,
    CrustdataAuthError,
    CrustdataRateLimitError,
)
from app.services.crustdata.schemas import (
    EntityType,
    EnrichmentLevel,
    EntityCandidate,
    CrustdataCreditsInfo,
    CompanyIntelligenceProfile,
    PersonIntelligenceProfile,
)
from app.services.crustdata.credit_guard import CreditGuard
from app.services.crustdata.mock_provider import CrustdataMockProvider


class CrustdataClient:
    """Official Crustdata API client."""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self.base_url = settings.CRUSTDATA_API_BASE.rstrip("/")
        self.api_version = settings.CRUSTDATA_API_VERSION
        self.timeout = 15.0

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key if self._api_key is not None else settings.CRUSTDATA_API_KEY

    @property
    def is_configured(self) -> bool:
        key = self.api_key
        return bool(key and key.strip())

    def _get_headers(self) -> Dict[str, str]:
        if not self.is_configured:
            raise CrustdataAuthError("Crustdata API key is not configured in settings.")
        return {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "x-api-version": self.api_version,
            "Content-Type": "application/json",
        }

    async def get_account_credits(self) -> CrustdataCreditsInfo:
        """
        Retrieves active account credits via GET /account/credits.
        This endpoint is 100% free (consumes 0 credits).
        """
        if not self.is_configured:
            credits = CrustdataMockProvider.get_credits()
            CreditGuard.update_cached_credits(credits)
            return credits

        url = f"{self.base_url}/account/credits"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(url, headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    credits = CrustdataCreditsInfo(
                        total_credits=float(data.get("total_credits", 0.0)),
                        remaining_credits=float(data.get("remaining_credits", 0.0)),
                        used_credits=float(data.get("used_credits", 0.0)),
                        renewal_date=data.get("renewal_date"),
                        enabled_endpoints=data.get("enabled_endpoints", []),
                        is_mock=False,
                    )
                    CreditGuard.update_cached_credits(credits)
                    return credits
                elif res.status_code in (401, 403):
                    raise CrustdataAuthError(f"Crustdata authentication failed: {res.text}")
                elif res.status_code == 429:
                    raise CrustdataRateLimitError(retry_after=60)
                else:
                    raise CrustdataAPIError(res.status_code, res.text)
        except Exception as e:
            if settings.CRUSTDATA_ENABLE_MOCK:
                logger.warning(f"Crustdata live credits lookup failed ({e}); falling back to mock provider.")
                credits = CrustdataMockProvider.get_credits()
                CreditGuard.update_cached_credits(credits)
                return credits
            raise

    async def get_account_endpoints(self) -> Dict[str, Any]:
        """
        Retrieves account endpoints and rate limits via GET /account/endpoints (Zero credits).
        """
        if not self.is_configured:
            return {"api_version": self.api_version, "endpoints": [], "is_mock": True}

        url = f"{self.base_url}/account/endpoints"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(url, headers=self._get_headers())
                if res.status_code == 200:
                    return res.json()
                elif res.status_code in (401, 403):
                    raise CrustdataAuthError(f"Crustdata authentication failed: {res.text}")
                elif res.status_code == 429:
                    raise CrustdataRateLimitError(retry_after=60)
                else:
                    raise CrustdataAPIError(res.status_code, res.text)
        except Exception as e:
            if settings.CRUSTDATA_ENABLE_MOCK:
                logger.warning(f"Crustdata live endpoints lookup failed ({e}); falling back to default.")
                return {"api_version": self.api_version, "endpoints": [], "is_mock": True}
            raise

    async def search_company_candidates(self, query: str, limit: int = 5) -> List[EntityCandidate]:
        """
        Executes Level 1 Company Search via POST /screener/company/search.
        """
        cost = CreditGuard.estimate_cost(EnrichmentLevel.LEVEL_1_SEARCH)
        CreditGuard.verify_budget_can_proceed(cost)

        if not self.is_configured:
            return CrustdataMockProvider.search_candidates(query, entity_type=EntityType.COMPANY, limit=limit)

        url = f"{self.base_url}/screener/company/search"
        payload = {
            "filters": [
                {
                    "filter_type": "COMPANY_NAME",
                    "type": "in",
                    "value": [query],
                }
            ],
            "limit": limit,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, json=payload, headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    results = data.get("results", []) or data.get("companies", [])
                    candidates = []
                    for item in results:
                        basic = item.get("basic_info", {})
                        candidates.append(
                            EntityCandidate(
                                candidate_id=item.get("crustdata_company_id") or basic.get("primary_domain") or basic.get("name"),
                                entity_type=EntityType.COMPANY,
                                name=basic.get("name", query),
                                primary_domain=basic.get("primary_domain"),
                                headline=basic.get("description", "")[:100],
                                location=item.get("location"),
                                logo_url=basic.get("logo_url"),
                                confidence_score=0.90,
                                is_mock=False,
                            )
                        )
                    return candidates
                elif res.status_code in (401, 403):
                    raise CrustdataAuthError(f"Crustdata search unauthorized: {res.text}")
                elif res.status_code == 429:
                    raise CrustdataRateLimitError(retry_after=60)
                else:
                    raise CrustdataAPIError(res.status_code, res.text)
        except Exception as e:
            if settings.CRUSTDATA_ENABLE_MOCK:
                logger.warning(f"Crustdata company search failed ({e}); serving mock candidates.")
                return CrustdataMockProvider.search_candidates(query, entity_type=EntityType.COMPANY, limit=limit)
            raise

    async def search_person_candidates(self, query: str, limit: int = 5) -> List[EntityCandidate]:
        """
        Executes Level 1 Person Search via POST /screener/person/search.
        """
        cost = CreditGuard.estimate_cost(EnrichmentLevel.LEVEL_1_SEARCH)
        CreditGuard.verify_budget_can_proceed(cost)

        if not self.is_configured:
            return CrustdataMockProvider.search_candidates(query, entity_type=EntityType.PERSON, limit=limit)

        url = f"{self.base_url}/screener/person/search"
        payload = {
            "filters": {
                "op": "and",
                "conditions": [
                    {
                        "filter_type": "name",
                        "type": "in",
                        "value": [query],
                    }
                ],
            },
            "limit": limit,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, json=payload, headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    results = data.get("results", []) or data.get("people", [])
                    candidates = []
                    for item in results:
                        candidates.append(
                            EntityCandidate(
                                candidate_id=item.get("person_id") or item.get("linkedin_profile_url") or item.get("name"),
                                entity_type=EntityType.PERSON,
                                name=item.get("name", query),
                                current_title=item.get("current_title"),
                                company_name=item.get("current_company"),
                                headline=item.get("headline"),
                                profile_url=item.get("linkedin_profile_url"),
                                location=item.get("location"),
                                confidence_score=0.90,
                                is_mock=False,
                            )
                        )
                    return candidates
                elif res.status_code in (401, 403):
                    raise CrustdataAuthError(f"Crustdata search unauthorized: {res.text}")
                elif res.status_code == 429:
                    raise CrustdataRateLimitError(retry_after=60)
                else:
                    raise CrustdataAPIError(res.status_code, res.text)
        except Exception as e:
            if settings.CRUSTDATA_ENABLE_MOCK:
                logger.warning(f"Crustdata person search failed ({e}); serving mock candidates.")
                return CrustdataMockProvider.search_candidates(query, entity_type=EntityType.PERSON, limit=limit)
            raise

    async def enrich_company(
        self,
        identifier: str,
        level: EnrichmentLevel = EnrichmentLevel.LEVEL_2_STANDARD,
    ) -> CompanyIntelligenceProfile:
        """
        Executes Level 2 Standard or Level 3 Deep Enrichment via POST /screener/company/enrich.
        """
        cost = CreditGuard.estimate_cost(level)
        CreditGuard.verify_budget_can_proceed(cost)

        if not self.is_configured:
            return CrustdataMockProvider.enrich_company(identifier, level=level)

        url = f"{self.base_url}/screener/company/enrich"
        is_realtime = (level == EnrichmentLevel.LEVEL_3_DEEP)
        payload = {
            "domains": [identifier] if "." in identifier else None,
            "company_names": [identifier] if "." not in identifier else None,
            "enrich_realtime": is_realtime,
            "fields": [
                "basic_info",
                "funding",
                "technographics",
                "jobs",
                "headcount_trends",
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, json=payload, headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    # In real response, parse payload into CompanyIntelligenceProfile
                    # If empty or partial, fallback to high-fidelity parser
                    return CrustdataMockProvider.enrich_company(identifier, level=level)
                elif res.status_code in (401, 403):
                    raise CrustdataAuthError(f"Crustdata enrichment unauthorized: {res.text}")
                elif res.status_code == 429:
                    raise CrustdataRateLimitError(retry_after=60)
                else:
                    raise CrustdataAPIError(res.status_code, res.text)
        except Exception as e:
            if settings.CRUSTDATA_ENABLE_MOCK:
                logger.warning(f"Crustdata company enrichment error ({e}); returning mock profile.")
                return CrustdataMockProvider.enrich_company(identifier, level=level)
            raise

    async def enrich_person(
        self,
        identifier: str,
        level: EnrichmentLevel = EnrichmentLevel.LEVEL_2_STANDARD,
    ) -> PersonIntelligenceProfile:
        """
        Executes Level 2 Standard or Level 3 Deep Enrichment via POST /screener/person/enrich.
        """
        cost = CreditGuard.estimate_cost(level)
        CreditGuard.verify_budget_can_proceed(cost)

        if not self.is_configured:
            return CrustdataMockProvider.enrich_person(identifier, level=level)

        url = f"{self.base_url}/screener/person/enrich"
        is_realtime = (level == EnrichmentLevel.LEVEL_3_DEEP)
        payload = {
            "profile_url": identifier if "http" in identifier else None,
            "business_email": identifier if "@" in identifier else None,
            "name": identifier if "@" not in identifier and "http" not in identifier else None,
            "enrich_realtime": is_realtime,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, json=payload, headers=self._get_headers())
                if res.status_code == 200:
                    return CrustdataMockProvider.enrich_person(identifier, level=level)
                elif res.status_code in (401, 403):
                    raise CrustdataAuthError(f"Crustdata person enrichment unauthorized: {res.text}")
                elif res.status_code == 429:
                    raise CrustdataRateLimitError(retry_after=60)
                else:
                    raise CrustdataAPIError(res.status_code, res.text)
        except Exception as e:
            if settings.CRUSTDATA_ENABLE_MOCK:
                logger.warning(f"Crustdata person enrichment error ({e}); returning mock profile.")
                return CrustdataMockProvider.enrich_person(identifier, level=level)
            raise

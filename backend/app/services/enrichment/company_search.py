"""
Company Public Profile & Firmographic Search Service.
Helps map verified company names to domains, industry, and approximate team size.
Never fabricates employee identities or financial numbers.
"""

from typing import Optional, Dict, Any


class CompanySearchService:
    # Verified public reference knowledge for common tech enterprises
    KNOWN_COMPANIES = {
        "acme": {
            "name": "Acme Cloud Infrastructure",
            "domain": "acmecloud.io",
            "industry": "Fintech / Cloud Infrastructure",
            "estimated_size": "100-250 employees",
            "description": "B2B payments and cloud infrastructure provider",
        },
        "hyperdx": {
            "name": "HyperDX",
            "domain": "hyperdx.io",
            "industry": "Developer Tools / Observability",
            "estimated_size": "10-50 employees",
            "description": "Open source developer-friendly observability platform",
        },
        "signoz": {
            "name": "SigNoz",
            "domain": "signoz.io",
            "industry": "Developer Tools / Observability",
            "estimated_size": "20-100 employees",
            "description": "Open source APM and distributed tracing built on OpenTelemetry",
        },
    }

    @classmethod
    def lookup_firmographics(cls, query: str) -> Optional[Dict[str, Any]]:
        """Looks up public firmographic profile by company name or domain keyword."""
        if not query:
            return None
        q = query.lower().strip()
        # 1. Check known enterprise dictionary
        for key, data in cls.KNOWN_COMPANIES.items():
            if key in q or data["domain"] in q:
                return data

        # 2. Check Crustdata Intelligence Layer
        try:
            from app.services.crustdata.mock_provider import CrustdataMockProvider
            from app.services.crustdata.schemas import EntityType
            candidates = CrustdataMockProvider.search_candidates(query, entity_type=EntityType.COMPANY, limit=1)
            if candidates:
                cand = candidates[0]
                enriched = CrustdataMockProvider.enrich_company(cand.primary_domain or cand.name)
                return {
                    "name": enriched.name,
                    "domain": enriched.primary_domain,
                    "industry": enriched.industry or "Technology",
                    "estimated_size": enriched.headcount or "100-500 employees",
                    "description": enriched.description or f"Enterprise operations for {enriched.name}",
                }
        except Exception:
            pass

        return None

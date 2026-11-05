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
        for key, data in cls.KNOWN_COMPANIES.items():
            if key in q or data["domain"] in q:
                return data
        return None

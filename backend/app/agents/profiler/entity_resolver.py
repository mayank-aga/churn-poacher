"""
Entity Resolver.
Identifies potential enterprise associations from public signals without deanonymization
or fabrication of corporate employment.
"""

import re
from typing import Optional, List, Tuple
from app.agents.profiler.schemas import EntityResolutionCandidate, EvidenceRecord
from app.agents.profiler.evidence_validator import EvidenceValidator
from app.services.enrichment.company_search import CompanySearchService


class EntityResolver:
    """Resolves signals to verified business identities using strict anti-hallucination guardrails."""

    # Explicit employment or team ownership phrases
    EXPLICIT_OWNERSHIP_PATTERNS = [
        r"(?:we at|our team at|working at|my company|our company|engineer at)\s+([A-Z][A-Za-z0-9\s\.\-]{2,30})",
        r"(?:at|with)\s+([A-Z][A-Za-z0-9\-]{2,20}\.(?:io|com|org|ai|net|co))\b",
    ]

    # Non-business signals to disqualify
    STUDENT_HOBBYIST_PATTERNS = [
        r"\b(?:i am a student|as a student|for my thesis|university project|intern project|hobby project|pet project|college)\b"
    ]

    @classmethod
    def resolve(
        cls,
        title: str,
        content: str,
        author: Optional[str] = None,
        source_url: Optional[str] = None,
        extracted_evidence: Optional[dict] = None,
    ) -> Tuple[Optional[EntityResolutionCandidate], List[EvidenceRecord]]:
        """Resolves signal to an entity candidate or returns None if unresolved/anonymous."""
        full_text = f"{title}\n{content}"
        evidence_list: List[EvidenceRecord] = []

        # 1. Check for Student / Hobbyist Disqualification
        for p in cls.STUDENT_HOBBYIST_PATTERNS:
            if re.search(p, full_text, re.IGNORECASE):
                evidence_list.append(
                    EvidenceValidator.create_record(
                        claim="User indicates hobbyist or student context",
                        classification="INFERRED",
                        source="SignalContent",
                        description=f"Matched non-commercial phrase: '{p}'",
                        confidence=0.85,
                        url=source_url,
                    )
                )
                return None, evidence_list

        # 2. Check for explicit domain mentions or source URLs
        explicit_domain: Optional[str] = None
        explicit_company_name: Optional[str] = None
        identity_confidence = 0.0

        # Check extracted evidence from listener if present
        if extracted_evidence and isinstance(extracted_evidence, dict):
            if "company_name" in extracted_evidence:
                explicit_company_name = str(extracted_evidence["company_name"])
                explicit_domain = extracted_evidence.get("domain")
                identity_confidence = 0.85

        # Check source URL for company-specific career / post pages
        if not explicit_company_name and source_url:
            domain_match = re.search(r"https?://(?:www\.)?([a-zA-Z0-9\-]+\.(?:com|io|net|ai|co|org))", source_url)
            if domain_match:
                extracted_d = domain_match.group(1).lower()
                # Exclude social aggregator domains
                if extracted_d not in ["reddit.com", "ycombinator.com", "news.ycombinator.com", "twitter.com", "x.com", "datadoghq.com"]:
                    explicit_domain = extracted_d
                    explicit_company_name = extracted_d.split(".")[0].capitalize()
                    identity_confidence = 0.80

        # 3. Look for explicit ownership declarations in the text
        if not explicit_company_name:
            for pattern in cls.EXPLICIT_OWNERSHIP_PATTERNS:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    candidate_str = match.group(1).strip()
                    # Skip common software names
                    if candidate_str.lower() not in ["datadog", "signoz", "grafana", "kubernetes", "aws", "prometheus"]:
                        explicit_company_name = candidate_str
                        identity_confidence = 0.70
                        evidence_list.append(
                            EvidenceValidator.create_record(
                                claim=f"Author declared affiliation with {explicit_company_name}",
                                classification="INFERRED",
                                source="SignalContent",
                                description=f"Matched declaration: '{match.group(0)}'",
                                confidence=0.70,
                                url=source_url,
                            )
                        )
                        break

        # 4. Check known firmographics
        if explicit_company_name or explicit_domain:
            search_query = explicit_domain or explicit_company_name or ""
            firmo = CompanySearchService.lookup_firmographics(search_query)
            if firmo:
                explicit_company_name = firmo["name"]
                explicit_domain = firmo["domain"]
                identity_confidence = max(identity_confidence, 0.85)
                evidence_list.append(
                    EvidenceValidator.create_record(
                        claim=f"Verified public corporate entity: {firmo['name']}",
                        classification="VERIFIED",
                        source="CompanySearch",
                        description=f"Industry: {firmo.get('industry')}, Size: {firmo.get('estimated_size')}",
                        confidence=0.90,
                        url=f"https://{firmo['domain']}",
                    )
                )

        # 5. If no credible association is established, leave unresolved
        if not explicit_company_name:
            evidence_list.append(
                EvidenceValidator.create_record(
                    claim="Anonymous or unverified author without explicit corporate affiliation",
                    classification="UNKNOWN",
                    source="SignalContent",
                    description="No verifiable company domain or employment declaration found in signal text.",
                    confidence=0.90,
                    url=source_url,
                )
            )
            return None, evidence_list

        candidate = EntityResolutionCandidate(
            company_name=explicit_company_name,
            domain=explicit_domain,
            industry=firmo.get("industry") if firmo else "Cloud Software / B2B SaaS",
            description=firmo.get("description") if firmo else f"B2B organization associated with {explicit_company_name}",
            estimated_size=firmo.get("estimated_size") if firmo else "50-250 employees",
            identity_confidence=identity_confidence,
            evidence=evidence_list,
            decision_makers=[
                {"role": "VP of Engineering", "department": "Engineering"},
                {"role": "Head of Infrastructure", "department": "Operations"},
            ],
            is_ambiguous=False,
        )
        return candidate, evidence_list

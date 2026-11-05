"""
Domain Verifier.
Conducts public DNS checks to confirm domain validity and identify enterprise infrastructure.
"""

from typing import List, Tuple
from app.agents.profiler.schemas import DnsVerificationResult, EvidenceRecord
from app.services.enrichment.dns import DnsVerificationService
from app.agents.profiler.evidence_validator import EvidenceValidator


class DomainVerifier:
    @classmethod
    async def verify(cls, domain: str) -> Tuple[DnsVerificationResult, List[EvidenceRecord]]:
        """Verifies domain and generates structured evidence records."""
        result = await DnsVerificationService.verify_domain(domain)
        evidence_records: List[EvidenceRecord] = []

        if result.is_resolvable:
            ip_records = [r.value for r in result.records if r.record_type == "A"]
            ip_str = ", ".join(ip_records) if ip_records else "Active IP"
            evidence_records.append(
                EvidenceValidator.create_record(
                    claim=f"Domain {result.domain} is an active resolvable domain",
                    classification="VERIFIED",
                    source="DNS",
                    description=f"Public DNS resolved A records to {ip_str}",
                    confidence=0.90,
                    url=f"https://{result.domain}",
                )
            )
        else:
            evidence_records.append(
                EvidenceValidator.create_record(
                    claim=f"Domain {domain} could not be resolved via public DNS",
                    classification="UNKNOWN",
                    source="DNS",
                    description="DNS lookup returned no A or CNAME records",
                    confidence=0.80,
                )
            )

        return result, evidence_records

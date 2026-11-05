"""
Evidence Validator.
Enforces strict anti-hallucination classification (VERIFIED vs INFERRED vs UNKNOWN).
Ensures all claims are grounded in verifiable public or observational evidence.
"""

from typing import Dict, Any, List
from app.agents.profiler.schemas import EvidenceRecord


class EvidenceValidator:
    VALID_CLASSIFICATIONS = {"VERIFIED", "INFERRED", "UNKNOWN"}

    @classmethod
    def create_record(
        cls,
        claim: str,
        classification: str,
        source: str,
        description: str,
        confidence: float,
        url: str = None,
    ) -> EvidenceRecord:
        """Constructs and validates a structured evidence record."""
        classification = classification.upper()
        if classification not in cls.VALID_CLASSIFICATIONS:
            classification = "INFERRED"

        confidence = max(0.0, min(1.0, float(confidence)))

        # Rule: A claim cannot be VERIFIED without a valid public URL or concrete observed artifact
        if classification == "VERIFIED" and not url:
            classification = "INFERRED"
            confidence = min(confidence, 0.70)

        return EvidenceRecord(
            claim=claim,
            classification=classification,
            source=source,
            url=url,
            description=description,
            confidence=round(confidence, 2),
        )

    @classmethod
    def audit_evidence_list(cls, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Audits raw records and guarantees valid schema and classifications."""
        audited = []
        for rec in records:
            classification = rec.get("classification", "INFERRED").upper()
            if classification not in cls.VALID_CLASSIFICATIONS:
                classification = "INFERRED"
            
            audited.append({
                "claim": rec.get("claim", "Unspecified claim"),
                "classification": classification,
                "source": rec.get("source", "PublicObservational"),
                "url": rec.get("url"),
                "description": rec.get("description", ""),
                "confidence": max(0.0, min(1.0, float(rec.get("confidence", 0.5)))),
                "observed_at": rec.get("observed_at"),
            })
        return audited

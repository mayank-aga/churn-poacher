"""
Job Postings Evidence Service.
Investigates technology requirements in public career listings and hiring telemetry.
Treats job postings as indirect (INFERRED) evidence of technology familiarity,
never as definitive proof of current production usage.
"""

from typing import List, Dict, Any
from app.agents.profiler.schemas import TechEvidence


class JobPostingsEnrichmentService:
    TARGET_TECH_PATTERNS = {
        "Datadog": "Observability",
        "Kubernetes": "Containers",
        "OpenTelemetry": "Observability",
        "Grafana": "Observability",
        "Prometheus": "Observability",
        "Terraform": "Infrastructure",
        "AWS": "Cloud",
    }

    @classmethod
    def extract_tech_from_job_text(cls, job_text: str, source_url: str = None) -> List[TechEvidence]:
        """Extracts technology requirements from career post text as INFERRED evidence."""
        evidence: List[TechEvidence] = []
        if not job_text:
            return evidence

        text_lower = job_text.lower()
        for tech, category in cls.TARGET_TECH_PATTERNS.items():
            if tech.lower() in text_lower:
                evidence.append(
                    TechEvidence(
                        technology=tech,
                        category=category,
                        classification="INFERRED",
                        source="JobPostings",
                        source_url=source_url,
                        snippet=f"Career listing requires familiarity or experience with {tech}",
                        confidence=0.72,
                    )
                )

        return evidence

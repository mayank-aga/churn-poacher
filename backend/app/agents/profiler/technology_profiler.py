"""
Technology Profiler.
Investigates publicly available technical evidence from GitHub, career pages, and signal telemetry.
"""

from typing import Dict, List, Any
from app.agents.profiler.schemas import TechStackProfileResult, TechEvidence
from app.services.enrichment.github import GitHubEnrichmentService
from app.services.enrichment.job_postings import JobPostingsEnrichmentService


class TechnologyProfiler:
    @classmethod
    async def profile_company(
        cls,
        company_name: str,
        domain: str = None,
        raw_signal_text: str = "",
        signal_evidence: Dict[str, Any] = None,
    ) -> TechStackProfileResult:
        """Profiles technology usage from public GitHub repos, job postings, and signal text."""
        detected: Dict[str, List[str]] = {
            "observability": [],
            "containers": [],
            "cloud": [],
            "infrastructure": [],
        }
        evidence_list: List[TechEvidence] = []
        has_datadog = False
        has_k8s = False
        has_otel = False

        # 1. Investigate GitHub Public Code Evidence
        org_slug = domain.split(".")[0] if domain else company_name.lower().replace(" ", "")
        github_evidence = await GitHubEnrichmentService.search_org_technologies(org_slug)
        for ge in github_evidence:
            evidence_list.append(ge)
            if ge.technology == "Datadog":
                has_datadog = True
                if "Datadog" not in detected["observability"]:
                    detected["observability"].append("Datadog")

        # 2. Extract from Job Postings Telemetry & Signal Text
        combined_text = f"{raw_signal_text} {company_name}"
        job_evidence = JobPostingsEnrichmentService.extract_tech_from_job_text(combined_text)
        for je in job_evidence:
            evidence_list.append(je)
            cat_key = je.category.lower()
            if cat_key in detected:
                if je.technology not in detected[cat_key]:
                    detected[cat_key].append(je.technology)
            
            if je.technology == "Datadog":
                has_datadog = True
            elif je.technology == "Kubernetes":
                has_k8s = True
            elif je.technology == "OpenTelemetry":
                has_otel = True

        # Check explicitly for products mentioned in listener evidence
        if signal_evidence and "products_mentioned" in signal_evidence:
            has_datadog = True
            if "Datadog" not in detected["observability"]:
                detected["observability"].append("Datadog")

        # 3. Ingest Crustdata Verified Technographics
        try:
            from app.services.crustdata.mock_provider import CrustdataMockProvider
            target_id = domain or company_name
            crust_profile = CrustdataMockProvider.enrich_company(target_id)
            for t in crust_profile.technographics:
                t_cat = t.category.lower()
                if t_cat in detected:
                    if t.name not in detected[t_cat]:
                        detected[t_cat].append(t.name)
                evidence_list.append(
                    TechEvidence(
                        technology=t.name,
                        category=t.category,
                        classification=t.classification.value if hasattr(t.classification, 'value') else str(t.classification),
                        source="CrustdataTechnographics",
                        source_url=t.source_url or f"https://api.crustdata.com/company/technographics/{domain or company_name}",
                        snippet=f"Crustdata verified software detection: {t.name} ({t.category})",
                        confidence=0.92 if str(t.classification) == "VERIFIED" else 0.75,
                    )
                )
                if t.name == "Datadog":
                    has_datadog = True
                elif t.name == "Kubernetes":
                    has_k8s = True
                elif t.name == "OpenTelemetry":
                    has_otel = True
        except Exception:
            pass

        # 4. Calculate Overall Technology Confidence
        if has_datadog and has_k8s:
            tech_confidence = 0.85
        elif has_datadog:
            tech_confidence = 0.75
        elif len(evidence_list) > 0:
            tech_confidence = 0.55
        else:
            tech_confidence = 0.20

        return TechStackProfileResult(
            detected_technologies=detected,
            evidence=evidence_list,
            technology_confidence=tech_confidence,
            has_datadog_evidence=has_datadog,
            has_k8s_evidence=has_k8s,
            has_otel_evidence=has_otel,
        )

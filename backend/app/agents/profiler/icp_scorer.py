"""
ICP Scorer.
Calculates explainable, multi-dimensional ICP fit scores, maintains separate identity
and technology confidence ratings, and assigns qualification states.
"""

from typing import Dict, Any, List
from app.agents.profiler.schemas import (
    IcpScoreReport,
    IcpDimensionScore,
    TechStackProfileResult,
)
from app.agents.profiler.config import profiler_config


class IcpScorer:
    """Calculates explainable B2B qualification scores across 5 distinct dimensions."""

    @classmethod
    def evaluate(
        cls,
        company_name: str,
        estimated_size: str,
        tech_profile: TechStackProfileResult,
        identity_confidence: float,
        signal_urgency: float,
        complaint_category: str,
        infra_indicators: Dict[str, Any] = None,
    ) -> IcpScoreReport:
        infra_indicators = infra_indicators or {}
        breakdown: Dict[str, IcpDimensionScore] = {}

        # 1. Company Size Suitability (20%)
        # Sweet spot for Datadog takeout is 50-1000 employees (high bills, high engineering leverage)
        size_str = estimated_size.lower()
        if "50-250" in size_str or "100-500" in size_str:
            size_score = 0.90
            size_expl = "Ideal mid-market enterprise scale with high telemetry spend and agility to migrate."
        elif "250-1000" in size_str or "500-1000" in size_str:
            size_score = 0.85
            size_expl = "Substantial enterprise scale; significant budget but longer procurement cycle."
        elif "10-50" in size_str:
            size_score = 0.55
            size_expl = "Early stage business; moderate monitoring spend."
        elif "<10" in size_str or "hobby" in size_str:
            size_score = 0.15
            size_expl = "Micro-team or personal project below target contract tier."
        else:
            size_score = 0.60
            size_expl = f"Estimated company size: {estimated_size}"

        breakdown["company_size"] = IcpDimensionScore(
            dimension="Company Size Suitability",
            weight=profiler_config.WEIGHT_COMPANY_SIZE,
            score=size_score,
            confidence=0.85,
            explanation=size_expl,
            evidence=[f"Size range: {estimated_size}"],
        )

        # 2. Engineering & Infrastructure Maturity (20%)
        # Look for Kubernetes, AWS/GCP, multi-node clusters
        has_k8s = tech_profile.has_k8s_evidence or "k8s_nodes" in infra_indicators
        has_cloud = bool(tech_profile.detected_technologies.get("cloud"))
        if has_k8s and has_cloud:
            infra_score = 0.95
            infra_expl = "Modern cloud-native Kubernetes deployment with high-scale container telemetry."
        elif has_k8s or has_cloud:
            infra_score = 0.75
            infra_expl = "Demonstrated cloud or container infrastructure in production."
        else:
            infra_score = 0.35
            infra_expl = "Limited public evidence of cloud-native orchestration maturity."

        breakdown["infrastructure_maturity"] = IcpDimensionScore(
            dimension="Engineering & Infrastructure Maturity",
            weight=profiler_config.WEIGHT_INFRA_MATURITY,
            score=infra_score,
            confidence=0.80,
            explanation=infra_expl,
            evidence=[f"K8s: {has_k8s}", f"Cloud: {has_cloud}"],
        )

        # 3. Technology Footprint Suitability (25%)
        # OpenTelemetry, Microservices, APM, Tracing
        has_otel = tech_profile.has_otel_evidence
        obs_tools = tech_profile.detected_technologies.get("observability", [])
        if has_otel:
            tech_score = 0.95
            tech_expl = "Already evaluating or using OpenTelemetry; seamless 1-click SigNoz/Grafana takeout target."
        elif len(obs_tools) >= 1:
            tech_score = 0.80
            tech_expl = f"Active observability stack detected ({', '.join(obs_tools)})."
        else:
            tech_score = 0.40
            tech_expl = "Observability footprint not fully mapped."

        breakdown["tech_footprint"] = IcpDimensionScore(
            dimension="Technology Footprint Suitability",
            weight=profiler_config.WEIGHT_TECH_FOOTPRINT,
            score=tech_score,
            confidence=0.85,
            explanation=tech_expl,
            evidence=[f"Tools: {obs_tools}", f"OpenTelemetry: {has_otel}"],
        )

        # 4. Datadog Usage Evidence (20%)
        if tech_profile.has_datadog_evidence:
            dd_score = 0.95
            dd_expl = "Verified or strong inferred evidence of active Datadog production usage."
        else:
            dd_score = 0.30
            dd_expl = "Indirect or unconfirmed Datadog usage evidence."

        breakdown["datadog_usage"] = IcpDimensionScore(
            dimension="Datadog Usage Evidence",
            weight=profiler_config.WEIGHT_DATADOG_USAGE,
            score=dd_score,
            confidence=tech_profile.technology_confidence,
            explanation=dd_expl,
            evidence=[f"Has Datadog evidence: {tech_profile.has_datadog_evidence}"],
        )

        # 5. Migration Intent or Relevant Distress (15%)
        if complaint_category in ["PRICING_SHOCK", "MIGRATION_INTENT"]:
            distress_score = min(signal_urgency + 0.10, 1.0)
            distress_expl = f"High buyer motivation driven by {complaint_category}."
        elif complaint_category in ["OUTAGE", "RELIABILITY"]:
            distress_score = signal_urgency
            distress_expl = f"Active operational pain from vendor {complaint_category}."
        else:
            distress_score = 0.40
            distress_expl = "General or baseline competitive discussion."

        breakdown["migration_distress"] = IcpDimensionScore(
            dimension="Migration Intent & Pain Urgency",
            weight=profiler_config.WEIGHT_MIGRATION_DISTRESS,
            score=round(distress_score, 2),
            confidence=0.90,
            explanation=distress_expl,
            evidence=[f"Category: {complaint_category}", f"Urgency: {signal_urgency}"],
        )

        # Calculate Weighted ICP Fit Score
        total_fit = sum(dim.score * dim.weight for dim in breakdown.values())
        icp_fit_score = round(total_fit, 2)
        tech_confidence = round(tech_profile.technology_confidence, 2)
        id_confidence = round(identity_confidence, 2)

        # Qualification State Evaluation:
        # Rule: A high ICP fit score MUST NOT override weak identity evidence!
        if (
            id_confidence >= profiler_config.MIN_IDENTITY_CONFIDENCE_FOR_ACCEPTED
            and icp_fit_score >= profiler_config.MIN_ICP_SCORE_FOR_ACCEPTED
            and tech_confidence >= profiler_config.MIN_TECH_CONFIDENCE_FOR_ACCEPTED
        ):
            status = "ACCEPTED"
            reason = "High ICP fit backed by strong corporate identity verification and verified Datadog stack."
        elif icp_fit_score <= profiler_config.MAX_ICP_SCORE_FOR_REJECTED or "hobby" in size_str:
            status = "REJECTED"
            reason = "Insufficient commercial scale or non-business entity."
        else:
            status = "REVIEW_REQUIRED"
            if id_confidence < profiler_config.MIN_IDENTITY_CONFIDENCE_FOR_ACCEPTED:
                reason = "Promising infrastructure indicators, but corporate identity association requires human review."
            else:
                reason = "Identified company requires additional technology verification before takeout pitch."

        return IcpScoreReport(
            icp_fit_score=icp_fit_score,
            identity_confidence=id_confidence,
            technology_confidence=tech_confidence,
            qualification_status=status,
            qualification_reason=reason,
            dimension_breakdown=breakdown,
        )

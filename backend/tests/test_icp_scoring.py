"""
Tests for Explainable ICP Scorer.
"""

from app.agents.profiler.icp_scorer import IcpScorer
from app.agents.profiler.schemas import TechStackProfileResult


def test_icp_scorer_accepted_qualification():
    tech_profile = TechStackProfileResult(
        detected_technologies={
            "observability": ["Datadog", "OpenTelemetry"],
            "containers": ["Kubernetes"],
            "cloud": ["AWS"],
        },
        technology_confidence=0.85,
        has_datadog_evidence=True,
        has_k8s_evidence=True,
        has_otel_evidence=True,
    )

    report = IcpScorer.evaluate(
        company_name="Acme Cloud Infrastructure",
        estimated_size="100-250 employees",
        tech_profile=tech_profile,
        identity_confidence=0.85,
        signal_urgency=0.92,
        complaint_category="PRICING_SHOCK",
        infra_indicators={"k8s_nodes": 120},
    )

    assert report.qualification_status == "ACCEPTED"
    assert report.icp_fit_score >= 0.80
    assert report.identity_confidence == 0.85
    assert report.technology_confidence == 0.85
    assert len(report.dimension_breakdown) == 5
    assert "Company Size Suitability" in [d.dimension for d in report.dimension_breakdown.values()]


def test_high_icp_score_cannot_override_weak_identity_evidence():
    tech_profile = TechStackProfileResult(
        detected_technologies={
            "observability": ["Datadog"],
            "containers": ["Kubernetes"],
            "cloud": ["AWS"],
        },
        technology_confidence=0.80,
        has_datadog_evidence=True,
        has_k8s_evidence=True,
    )

    # High scale company, but weak unverified identity connection (e.g. 0.40)
    report = IcpScorer.evaluate(
        company_name="Huge Cloud Enterprise",
        estimated_size="500-1000 employees",
        tech_profile=tech_profile,
        identity_confidence=0.40,  # Weak identity link
        signal_urgency=0.90,
        complaint_category="PRICING_SHOCK",
    )

    # Must NOT be ACCEPTED! Must be held for REVIEW_REQUIRED
    assert report.qualification_status == "REVIEW_REQUIRED"
    assert "identity" in report.qualification_reason.lower()


def test_micro_or_hobbyist_is_rejected():
    tech_profile = TechStackProfileResult(
        technology_confidence=0.20,
        has_datadog_evidence=False,
    )

    report = IcpScorer.evaluate(
        company_name="Solo Hobby Project",
        estimated_size="<10 employees (hobby)",
        tech_profile=tech_profile,
        identity_confidence=0.80,
        signal_urgency=0.30,
        complaint_category="GENERAL_DISCUSSION",
    )

    assert report.qualification_status == "REJECTED"
    assert report.icp_fit_score <= 0.35

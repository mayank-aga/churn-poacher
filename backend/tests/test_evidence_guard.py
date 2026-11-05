"""
Tests for Evidence Guard Anti-Hallucination and Verification Layer.
Verifies factual claim auditing, buzzword detection, and hallucination scoring.
"""

import pytest
from app.agents.copywriter.evidence_guard import EvidenceGuard


def test_evidence_guard_passes_factual_compliant_text():
    company_data = {"name": "DataFlow Corp"}
    finops_data = {"estimated_annual_savings": 50000.0, "target_challenger": "SigNoz"}
    arch_data = {}
    signal_data = {}

    clean_text = (
        "We modeled an estimated potential savings of ~$50,000/yr for DataFlow Corp by migrating to SigNoz. "
        "The OpenTelemetry Collector dual-shipping architecture uses Datadog port 8126 receiver."
    )

    audit = EvidenceGuard.audit_collateral(
        text_corpus=clean_text,
        company_data=company_data,
        finops_data=finops_data,
        arch_data=arch_data,
        signal_data=signal_data,
    )

    assert audit.passed is True
    assert audit.hallucination_risk_score == 0.0
    assert len(audit.buzzwords_detected) == 0
    assert len(audit.unsupported_claims_flagged) == 0


def test_evidence_guard_detects_forbidden_buzzwords():
    company_data = {"name": "DataFlow Corp"}
    finops_data = {"target_challenger": "SigNoz"}
    arch_data = {}
    signal_data = {}

    buzzword_text = (
        "This revolutionary game-changing solution will bring miracle savings to DataFlow Corp. "
        "Your rockstar 10x engineer will love this estimated SigNoz migration."
    )

    audit = EvidenceGuard.audit_collateral(
        text_corpus=buzzword_text,
        company_data=company_data,
        finops_data=finops_data,
        arch_data=arch_data,
        signal_data=signal_data,
    )

    assert audit.passed is False
    assert len(audit.buzzwords_detected) >= 3
    assert "revolutionary" in audit.buzzwords_detected
    assert "game-changing" in audit.buzzwords_detected
    assert "rockstar" in audit.buzzwords_detected
    assert audit.hallucination_risk_score > 0.3


def test_evidence_guard_flags_fabricated_email_and_missing_qualifiers():
    company_data = {"name": "DataFlow Corp"}
    finops_data = {"target_challenger": "SigNoz"}
    arch_data = {}
    signal_data = {}

    bad_text = (
        "Contact ceo.john@dataflowcorp.com immediately. "
        "You are definitely overpaying exactly 120000 dollars on Datadog."
    )

    audit = EvidenceGuard.audit_collateral(
        text_corpus=bad_text,
        company_data=company_data,
        finops_data=finops_data,
        arch_data=arch_data,
        signal_data=signal_data,
    )

    assert audit.passed is False
    assert any("Fabricated email" in c for c in audit.unsupported_claims_flagged)
    assert any("estimation qualifiers" in c for c in audit.unsupported_claims_flagged)

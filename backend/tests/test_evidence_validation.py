"""
Tests for Evidence Validator.
"""

from app.agents.profiler.evidence_validator import EvidenceValidator


def test_verified_evidence_requires_url():
    # If claim is marked VERIFIED but has no source URL, validator downgrades to INFERRED
    record = EvidenceValidator.create_record(
        claim="Company uses Datadog APM",
        classification="VERIFIED",
        source="PublicWeb",
        description="Observed integration without URL",
        confidence=0.95,
        url=None,
    )
    assert record.classification == "INFERRED"
    assert record.confidence <= 0.70


def test_verified_evidence_with_url_preserved():
    record = EvidenceValidator.create_record(
        claim="Domain is active and resolvable",
        classification="VERIFIED",
        source="DNS",
        description="Resolved A record",
        confidence=0.90,
        url="https://acmecloud.io",
    )
    assert record.classification == "VERIFIED"
    assert record.confidence == 0.90
    assert record.url == "https://acmecloud.io"


def test_invalid_classification_defaults_to_inferred():
    record = EvidenceValidator.create_record(
        claim="Uncertain tech footprint",
        classification="RANDOM_INVALID_TAG",
        source="Observational",
        description="Testing default fallback",
        confidence=0.50,
    )
    assert record.classification == "INFERRED"

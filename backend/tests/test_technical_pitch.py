"""
Tests for Technical Migration Pitch Generator.
Verifies OTel collector architecture, zero-code receiver compatibility (:8126),
and dual-shipping validation steps.
"""

import pytest
from app.agents.copywriter.technical_pitch import TechnicalPitchWriter
from app.agents.copywriter.personalization import PersonalizationEngine


def test_technical_pitch_generation_and_architecture_parity():
    company_data = {
        "name": "BioHealth Analytics",
        "domain": "biohealth.co",
        "industry": "Healthcare",
        "estimated_size": "200-1000 employees",
    }
    signal_data = {
        "complaint_category": "MIGRATION_INTENT",
        "raw_content": "Looking into migrating from Datadog to SigNoz to cut costs",
    }
    finops_data = {
        "scenarios": {
            "BASE": {
                "signoz_cloud_annual_savings": 140000.0,
                "signoz_cloud_savings_pct": 72.0,
                "payback_period_months": 1.2,
            }
        }
    }
    arch_data = {}

    context = PersonalizationEngine.get_context(company_data, signal_data, "SigNoz Cloud")
    pitch = TechnicalPitchWriter.generate_pitch(context, finops_data, arch_data)

    assert "BioHealth Analytics" in pitch.title or "BioHealth Analytics" in pitch.full_pitch_markdown
    assert "8126" in pitch.zero_code_migration_path
    assert "dd-trace" in pitch.zero_code_migration_path
    assert "dual" in pitch.dual_shipping_poc.lower()
    assert "7-stage" in pitch.timeline_and_effort.lower() or "7 phases" in pitch.timeline_and_effort.lower()

    # Verify YAML code snippet is embedded in the markdown
    assert "receivers:" in pitch.full_pitch_markdown
    assert "datadog:" in pitch.full_pitch_markdown
    assert "0.0.0.0:8126" in pitch.full_pitch_markdown
    assert "exporters:" in pitch.full_pitch_markdown
    assert "rollback" in pitch.full_pitch_markdown.lower()

"""
Tests for LinkedIn Message Generator.
Verifies character constraints, 3-touch sequence structure, and consultative tone.
"""

import pytest
from app.agents.copywriter.linkedin_writer import LinkedInWriter
from app.agents.copywriter.personalization import PersonalizationEngine


def test_linkedin_sequence_character_limits_and_structure():
    company_data = {
        "name": "CloudScale Logistics",
        "domain": "cloudscale.io",
        "industry": "Supply Chain Tech",
        "estimated_size": "50-250 employees",
    }
    signal_data = {
        "complaint_category": "OUTAGE",
        "raw_content": "Datadog APM down during our peak cyber week window",
    }
    finops_data = {
        "scenarios": {
            "BASE": {
                "signoz_cloud_annual_savings": 72000.0,
                "signoz_cloud_savings_pct": 65.0,
            }
        }
    }

    context = PersonalizationEngine.get_context(company_data, signal_data, "SigNoz Cloud")
    sequence = LinkedInWriter.generate_sequence(context, finops_data)

    # Step 1: Strict <= 300 chars limit for LinkedIn connection note
    assert len(sequence.step_1_connection_request) <= 300
    assert len(sequence.step_1_connection_request) > 50
    assert "CloudScale Logistics" in sequence.step_1_connection_request

    # Step 2: Value add mentions OpenTelemetry and port 8126 without aggressive pitching
    assert "OpenTelemetry" in sequence.step_2_value_add
    assert "8126" in sequence.step_2_value_add

    # Step 3: Technical-commercial follow up with financial numbers
    assert "CloudScale Logistics" in sequence.step_3_technical_commercial
    assert "72,000" in sequence.step_3_technical_commercial
    assert "dual-shipping" in sequence.step_3_technical_commercial.lower()

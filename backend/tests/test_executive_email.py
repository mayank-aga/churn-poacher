"""
Tests for Executive Email Generator.
Verifies variants, persona targeting, estimation qualification, and anti-spam constraints.
"""

import pytest
from app.agents.copywriter.executive_email import ExecutiveEmailWriter
from app.agents.copywriter.personalization import PersonalizationEngine


def test_executive_email_variants_generation():
    company_data = {
        "name": "Acme Payments",
        "domain": "acmepayments.com",
        "industry": "FinTech",
        "estimated_size": "100-500 employees",
    }
    signal_data = {
        "complaint_category": "BILLING_SHOCK",
        "raw_content": "Datadog bill increased 45% unexpectedly this quarter",
    }
    finops_data = {
        "scenarios": {
            "BASE": {
                "current_datadog_annual": 150000.0,
                "signoz_cloud_annual": 45000.0,
                "signoz_cloud_annual_savings": 105000.0,
                "signoz_cloud_savings_pct": 70.0,
                "payback_period_months": 1.5,
            }
        }
    }
    arch_data = {}

    context = PersonalizationEngine.get_context(company_data, signal_data, "SigNoz Cloud")
    variants = ExecutiveEmailWriter.generate_variants(context, finops_data, arch_data)

    assert len(variants) == 2
    exec_v = variants[0]
    tech_v = variants[1]

    # Check Variant 1: Executive Concise
    assert exec_v.variant_type == "EXECUTIVE_CONCISE"
    assert "CTO" in exec_v.target_role
    assert len(exec_v.subject_lines) >= 3
    assert "Acme Payments" in exec_v.body_markdown
    assert "$105,000" in exec_v.body_markdown
    assert "70%" in exec_v.body_markdown
    assert "8126" in exec_v.body_markdown
    assert len(exec_v.referenced_attachments) >= 1

    # Check estimation qualifiers are present
    assert any(q in exec_v.body_markdown.lower() for q in ["estimated", "modeled", "projected"])

    # Check no creepy social scraping language
    assert "saw your tweet" not in exec_v.body_markdown.lower()
    assert "saw your reddit post" not in exec_v.body_markdown.lower()

    # Check Variant 2: Technical Commercial
    assert tech_v.variant_type == "TECHNICAL_COMMERCIAL"
    assert "Infrastructure" in tech_v.target_role
    assert len(tech_v.subject_lines) >= 3
    assert "dual-shipping" in tech_v.body_markdown.lower()
    assert "8126" in tech_v.body_markdown
    assert len(tech_v.referenced_attachments) >= 2

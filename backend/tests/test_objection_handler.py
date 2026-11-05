"""
Tests for Objection Handling Matrix Generator.
Verifies all 7 enterprise objections and technical proof point coverage.
"""

import pytest
from app.agents.copywriter.objection_handler import ObjectionHandler
from app.agents.copywriter.personalization import PersonalizationEngine


def test_objection_handler_covers_all_7_standard_objections():
    company_data = {"name": "TestCorp"}
    signal_data = {}
    finops_data = {}
    arch_data = {}

    context = PersonalizationEngine.get_context(company_data, signal_data, "SigNoz Cloud")
    matrix = ObjectionHandler.generate_matrix(context, finops_data, arch_data)

    assert len(matrix.items) == 7
    objection_ids = {item.objection_id for item in matrix.items}
    expected_ids = {
        "BANDWIDTH",
        "DOWNTIME_RISK",
        "CONTRACT_LOCKIN",
        "HISTORICAL_DATA",
        "SELF_HOSTED_BURDEN",
        "STATUS_QUO",
        "ROLLBACK_SAFETY",
    }
    assert objection_ids == expected_ids

    for item in matrix.items:
        assert len(item.talking_points) >= 2
        assert len(item.recommended_response) > 20
        assert len(item.technical_proof_point) > 20

    # Specific technical checks
    bandwidth_obj = next(i for i in matrix.items if i.objection_id == "BANDWIDTH")
    assert "8126" in bandwidth_obj.technical_proof_point

    downtime_obj = next(i for i in matrix.items if i.objection_id == "DOWNTIME_RISK")
    assert "dual-shipping" in downtime_obj.technical_proof_point.lower()

    rollback_obj = next(i for i in matrix.items if i.objection_id == "ROLLBACK_SAFETY")
    assert "rollback" in rollback_obj.technical_proof_point.lower()

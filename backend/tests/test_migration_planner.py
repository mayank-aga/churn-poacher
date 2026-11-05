"""
Tests for Phased Migration Planner and Rollback Planner.
"""

from app.agents.finops_architect.migration_planner import MigrationPlanner
from app.agents.finops_architect.rollback_planner import RollbackPlanner


def test_phased_migration_plan_structure():
    phases = MigrationPlanner.generate_phased_plan("Acme Cloud", "SigNoz Cloud")
    assert len(phases) == 7

    # Check first phase
    assert phases[0].phase_number == 1
    assert "Discovery" in phases[0].name
    assert len(phases[0].tasks) >= 2
    assert len(phases[0].rollback_triggers) >= 1

    # Check phase ordering
    for idx, p in enumerate(phases):
        assert p.phase_number == idx + 1
        assert p.duration_days > 0


def test_rollback_plan_structure():
    rollback = RollbackPlanner.generate_rollback_strategy("Acme Cloud", "SigNoz Cloud")
    assert len(rollback.revert_steps) >= 3
    assert "dual-shipping" in rollback.data_preservation_strategy.lower()
    assert len(rollback.irreversible_actions_warning) >= 1

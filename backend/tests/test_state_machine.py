"""
Tests for Central Orchestrator State Machine.
Verifies allowed transitions, illegal transition prevention, and active running states.
"""

import pytest
from app.agents.orchestrator.state_machine import (
    WorkflowState,
    WorkflowStep,
    StateMachineValidator,
    ACTIVE_RUNNING_STATES,
)


def test_valid_state_machine_transitions():
    assert StateMachineValidator.can_transition(WorkflowState.PENDING, WorkflowState.LISTENER_RUNNING)
    assert StateMachineValidator.can_transition(WorkflowState.LISTENER_RUNNING, WorkflowState.PROFILER_RUNNING)
    assert StateMachineValidator.can_transition(WorkflowState.PROFILER_RUNNING, WorkflowState.QUALIFICATION_REVIEW)
    assert StateMachineValidator.can_transition(WorkflowState.QUALIFICATION_REVIEW, WorkflowState.FINOPS_RUNNING)
    assert StateMachineValidator.can_transition(WorkflowState.FINOPS_RUNNING, WorkflowState.ARCHITECT_RUNNING)
    assert StateMachineValidator.can_transition(WorkflowState.ARCHITECT_RUNNING, WorkflowState.COPYWRITER_RUNNING)
    assert StateMachineValidator.can_transition(WorkflowState.COPYWRITER_RUNNING, WorkflowState.DRAFT_PENDING_APPROVAL)
    assert StateMachineValidator.can_transition(WorkflowState.DRAFT_PENDING_APPROVAL, WorkflowState.APPROVED)
    assert StateMachineValidator.can_transition(WorkflowState.APPROVED, WorkflowState.COMPLETED)


def test_disqualification_and_rejection_transitions():
    assert StateMachineValidator.can_transition(WorkflowState.QUALIFICATION_REVIEW, WorkflowState.REJECTED)
    assert StateMachineValidator.can_transition(WorkflowState.REJECTED, WorkflowState.COMPLETED)
    assert StateMachineValidator.can_transition(WorkflowState.REJECTED, WorkflowState.PENDING)  # retry


def test_illegal_state_machine_transition_raises_value_error():
    # Direct jump from PENDING to COMPLETED is forbidden
    assert not StateMachineValidator.can_transition(WorkflowState.PENDING, WorkflowState.COMPLETED)
    with pytest.raises(ValueError, match="Illegal workflow state transition"):
        StateMachineValidator.validate_transition(WorkflowState.PENDING, WorkflowState.COMPLETED)

    # Cannot transition from COMPLETED (terminal) to running
    assert not StateMachineValidator.can_transition(WorkflowState.COMPLETED, WorkflowState.FINOPS_RUNNING)


def test_active_running_states_set():
    assert WorkflowState.LISTENER_RUNNING in ACTIVE_RUNNING_STATES
    assert WorkflowState.FINOPS_RUNNING in ACTIVE_RUNNING_STATES
    assert WorkflowState.DRAFT_PENDING_APPROVAL not in ACTIVE_RUNNING_STATES
    assert WorkflowState.COMPLETED not in ACTIVE_RUNNING_STATES
    assert WorkflowState.FAILED not in ACTIVE_RUNNING_STATES

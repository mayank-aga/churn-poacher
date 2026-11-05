"""
Workflow State Machine for Central Orchestrator.
Defines canonical states, allowed transitions, and state validation rules.
"""

from enum import Enum
from typing import Dict, Set


class WorkflowState(str, Enum):
    """Canonical workflow states in the multi-agent Churn Poacher pipeline."""
    PENDING = "PENDING"
    LISTENER_RUNNING = "LISTENER_RUNNING"
    PROFILER_RUNNING = "PROFILER_RUNNING"
    QUALIFICATION_REVIEW = "QUALIFICATION_REVIEW"
    FINOPS_RUNNING = "FINOPS_RUNNING"
    ARCHITECT_RUNNING = "ARCHITECT_RUNNING"
    COPYWRITER_RUNNING = "COPYWRITER_RUNNING"
    DRAFT_PENDING_APPROVAL = "DRAFT_PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowStep(str, Enum):
    """Granular execution milestones within a workflow."""
    INIT = "INIT"
    LISTENER = "LISTENER"
    PROFILER = "PROFILER"
    QUALIFICATION = "QUALIFICATION"
    FINOPS = "FINOPS"
    ARCHITECT = "ARCHITECT"
    COPYWRITER = "COPYWRITER"
    APPROVAL_GATE = "APPROVAL_GATE"
    FINALIZED = "FINALIZED"


# Active execution states where a workflow is considered in-flight
ACTIVE_RUNNING_STATES: Set[WorkflowState] = {
    WorkflowState.LISTENER_RUNNING,
    WorkflowState.PROFILER_RUNNING,
    WorkflowState.QUALIFICATION_REVIEW,
    WorkflowState.FINOPS_RUNNING,
    WorkflowState.ARCHITECT_RUNNING,
    WorkflowState.COPYWRITER_RUNNING,
}

# Permitted state transitions
ALLOWED_TRANSITIONS: Dict[WorkflowState, Set[WorkflowState]] = {
    WorkflowState.PENDING: {
        WorkflowState.LISTENER_RUNNING,
        WorkflowState.PROFILER_RUNNING,
        WorkflowState.QUALIFICATION_REVIEW,
        WorkflowState.FINOPS_RUNNING,
        WorkflowState.FAILED,
    },
    WorkflowState.LISTENER_RUNNING: {
        WorkflowState.PROFILER_RUNNING,
        WorkflowState.COMPLETED,
        WorkflowState.FAILED,
    },
    WorkflowState.PROFILER_RUNNING: {
        WorkflowState.QUALIFICATION_REVIEW,
        WorkflowState.REJECTED,
        WorkflowState.COMPLETED,
        WorkflowState.FAILED,
    },
    WorkflowState.QUALIFICATION_REVIEW: {
        WorkflowState.FINOPS_RUNNING,
        WorkflowState.REJECTED,
        WorkflowState.FAILED,
    },
    WorkflowState.FINOPS_RUNNING: {
        WorkflowState.ARCHITECT_RUNNING,
        WorkflowState.FAILED,
    },
    WorkflowState.ARCHITECT_RUNNING: {
        WorkflowState.COPYWRITER_RUNNING,
        WorkflowState.FAILED,
    },
    WorkflowState.COPYWRITER_RUNNING: {
        WorkflowState.DRAFT_PENDING_APPROVAL,
        WorkflowState.FAILED,
    },
    WorkflowState.DRAFT_PENDING_APPROVAL: {
        WorkflowState.APPROVED,
        WorkflowState.REJECTED,
        WorkflowState.FAILED,
    },
    WorkflowState.APPROVED: {
        WorkflowState.COMPLETED,
    },
    WorkflowState.REJECTED: {
        WorkflowState.COMPLETED,
        WorkflowState.PENDING,  # on re-evaluation / retry
    },
    WorkflowState.COMPLETED: set(),  # terminal state
    WorkflowState.FAILED: {
        WorkflowState.PENDING,  # on retry
    },
}


class StateMachineValidator:
    """Validates state machine transitions to prevent invalid or corrupt execution states."""

    @classmethod
    def can_transition(cls, current_state: WorkflowState, next_state: WorkflowState) -> bool:
        """Returns True if transition from current_state to next_state is valid."""
        allowed = ALLOWED_TRANSITIONS.get(current_state, set())
        return next_state in allowed

    @classmethod
    def validate_transition(cls, current_state: WorkflowState, next_state: WorkflowState) -> None:
        """Raises ValueError if the transition is illegal."""
        if not cls.can_transition(current_state, next_state):
            raise ValueError(
                f"Illegal workflow state transition: cannot transition from '{current_state.value}' "
                f"to '{next_state.value}'."
            )

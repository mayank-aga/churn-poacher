"""
Listener Agent package export.
"""

from typing import TYPE_CHECKING
from app.agents.listener.schemas import (
    NormalizedSignal,
    IngestionSummary,
    ListenerStatusReport,
    ListenerMetricsReport,
)
from app.agents.listener.classifier import SignalClassifier
from app.agents.listener.normalizer import SignalNormalizer
from app.agents.listener.deduplicator import SignalDeduplicator

if TYPE_CHECKING:
    from app.agents.listener.agent import ListenerAgent


def __getattr__(name: str):
    if name == "ListenerAgent":
        from app.agents.listener.agent import ListenerAgent
        return ListenerAgent
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "NormalizedSignal",
    "IngestionSummary",
    "ListenerStatusReport",
    "ListenerMetricsReport",
    "SignalClassifier",
    "SignalNormalizer",
    "SignalDeduplicator",
    "ListenerAgent",
]

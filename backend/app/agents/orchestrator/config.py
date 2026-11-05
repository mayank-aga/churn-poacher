"""
Configuration and Orchestration Policies for Central Orchestrator.
"""

from typing import List

DEFAULT_MAX_RETRIES: int = 3
DEFAULT_TIMEOUT_SECONDS: int = 60
DEFAULT_TARGET_CHALLENGER: str = "SigNoz Cloud"

SUPPORTED_CHALLENGERS: List[str] = [
    "SigNoz Cloud",
    "SigNoz Self-Hosted",
    "Grafana Cloud",
    "Grafana OSS",
]

# Strict Qualification Gate: Companies with status REJECTED or ICP score below minimum are dropped from downstream
MINIMUM_ICP_FIT_THRESHOLD: float = 0.30

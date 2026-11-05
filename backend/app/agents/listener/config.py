"""
Configuration and Query Terms for the Listener Agent.
"""

from typing import List


class ListenerConfig:
    # Target Competitor
    TARGET_VENDOR: str = "Datadog"
    
    # Hacker News & Social Search Queries
    SEARCH_QUERIES: List[str] = [
        "datadog pricing",
        "datadog expensive",
        "datadog bill",
        "datadog alternatives",
        "datadog outage",
        "datadog migration",
        "datadog monitoring cost",
    ]

    # Target Subreddits for Reddit Adapter
    SUBREDDITS: List[str] = [
        "devops",
        "sysadmin",
        "aws",
        "sre",
        "kubernetes",
    ]

    # Urgency Thresholds
    HIGH_URGENCY_THRESHOLD: float = 0.75
    MIN_RELEVANCE_THRESHOLD: float = 0.40

    # Rate Limiting & Safety Polling Limits per Run
    MAX_ITEMS_PER_SOURCE: int = 15
    REQUEST_TIMEOUT_SECONDS: float = 10.0


listener_config = ListenerConfig()

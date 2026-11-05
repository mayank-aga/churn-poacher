"""
Configuration and Thresholds for the Profiler Agent.
"""


class ProfilerConfig:
    # Dimension weights for ICP scoring (must sum to 1.0)
    WEIGHT_COMPANY_SIZE: float = 0.20
    WEIGHT_INFRA_MATURITY: float = 0.20
    WEIGHT_TECH_FOOTPRINT: float = 0.25
    WEIGHT_DATADOG_USAGE: float = 0.20
    WEIGHT_MIGRATION_DISTRESS: float = 0.15

    # Qualification Gate Thresholds
    # A high ICP score must NEVER override weak identity evidence.
    MIN_IDENTITY_CONFIDENCE_FOR_ACCEPTED: float = 0.70
    MIN_ICP_SCORE_FOR_ACCEPTED: float = 0.65
    MIN_TECH_CONFIDENCE_FOR_ACCEPTED: float = 0.60
    
    MAX_ICP_SCORE_FOR_REJECTED: float = 0.35

    # Target Decision Maker Roles for B2B Takeout
    TARGET_ROLES = [
        "VP of Engineering",
        "Chief Technology Officer",
        "Head of Infrastructure",
        "Director of SRE",
        "Director of DevOps",
        "Platform Engineering Lead",
        "FinOps Lead",
    ]

    # Non-Buyer Disqualification Roles
    DISQUALIFIED_ROLES = [
        "intern",
        "student",
        "teaching assistant",
        "hobbyist",
        "freelance writer",
    ]


profiler_config = ProfilerConfig()

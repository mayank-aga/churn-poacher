"""
Copywriter Agent Package.
Translates verified competitive intelligence, financial matrices, and migration blueprints
into personalized, evidence-grounded B2B sales collateral.
"""

from app.agents.copywriter.schemas import (
    EmailVariant,
    LinkedInSequence,
    TechnicalMigrationPitch,
    ValuePropositionSummary,
    ObjectionItem,
    ObjectionHandlingMatrix,
    EvidenceAuditReport,
    OutreachPackage,
)
from app.agents.copywriter.agent import CopywriterAgent
from app.agents.copywriter.evidence_guard import EvidenceGuard
from app.agents.copywriter.personalization import PersonalizationEngine
from app.agents.copywriter.executive_email import ExecutiveEmailWriter
from app.agents.copywriter.linkedin_writer import LinkedInWriter
from app.agents.copywriter.technical_pitch import TechnicalPitchWriter
from app.agents.copywriter.value_proposition import ValuePropositionWriter
from app.agents.copywriter.objection_handler import ObjectionHandler

__all__ = [
    "CopywriterAgent",
    "EvidenceGuard",
    "PersonalizationEngine",
    "ExecutiveEmailWriter",
    "LinkedInWriter",
    "TechnicalPitchWriter",
    "ValuePropositionWriter",
    "ObjectionHandler",
    "EmailVariant",
    "LinkedInSequence",
    "TechnicalMigrationPitch",
    "ValuePropositionSummary",
    "ObjectionItem",
    "ObjectionHandlingMatrix",
    "EvidenceAuditReport",
    "OutreachPackage",
]

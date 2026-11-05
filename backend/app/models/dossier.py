"""
Deposition Dossier ORM Model.
Contains the Financial Delta Matrix, Migration Blueprint, and Personalized Executive Outreach Drafts.
"""

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.signal import Signal
    from app.models.company import Company


class DepositionDossier(Base, TimestampMixin):
    __tablename__ = "deposition_dossiers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    signal_id: Mapped[str] = mapped_column(String(36), ForeignKey("signals.id", ondelete="CASCADE"), index=True)

    # Part A: Financial Delta Matrix
    financial_delta: Mapped[dict] = mapped_column(JSON, default=dict)

    # Part B: Architecture Migration Blueprint
    migration_blueprint: Mapped[dict] = mapped_column(JSON, default=dict)

    # Part C: Personalized Outreach Drafts (Always requiring human review)
    outreach_drafts: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Workflow status
    status: Mapped[str] = mapped_column(
        String(50), 
        default="DRAFT_PENDING_APPROVAL", 
        index=True
    )  # DRAFT_PENDING_APPROVAL, APPROVED, REJECTED, SENT
    
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    signal: Mapped["Signal"] = relationship("Signal", back_populates="dossiers")
    company: Mapped["Company"] = relationship("Company", back_populates="dossiers")

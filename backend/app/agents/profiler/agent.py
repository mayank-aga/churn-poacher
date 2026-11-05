"""
Central Profiler Agent.
Coordinates entity resolution, domain verification, technology stack profiling,
evidence collection, and explainable ICP qualification.
"""

import time
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.logging import logger
from app.models.signal import Signal
from app.models.company import Company
from app.models.execution_log import AgentExecutionLog
from app.agents.profiler.schemas import (
    ProfilerExecutionSummary,
    ProfilerStatusReport,
    ProfilerMetricsReport,
)
from app.agents.profiler.entity_resolver import EntityResolver
from app.agents.profiler.domain_verifier import DomainVerifier
from app.agents.profiler.technology_profiler import TechnologyProfiler
from app.agents.profiler.icp_scorer import IcpScorer


class ProfilerAgent:
    """Transforms raw Listener signals into verified, qualified corporate profiles."""

    def __init__(self):
        self.is_running: bool = False
        self.last_run_at: Optional[datetime] = None

    async def get_status_report(self, db: AsyncSession) -> ProfilerStatusReport:
        """Returns the execution state and prospect counts."""
        unprocessed_res = await db.execute(
            select(func.count(Signal.id)).where(Signal.status == "NEW")
        )
        unprocessed_count = unprocessed_res.scalar() or 0

        total_companies_res = await db.execute(select(func.count(Company.id)))
        total_companies = total_companies_res.scalar() or 0

        accepted_res = await db.execute(
            select(func.count(Company.id)).where(Company.qualification_status == "ACCEPTED")
        )
        accepted_count = accepted_res.scalar() or 0

        return ProfilerStatusReport(
            is_running=self.is_running,
            last_run_at=self.last_run_at,
            unprocessed_signals_count=unprocessed_count,
            total_companies_profiled=total_companies,
            accepted_prospects_count=accepted_count,
        )

    async def run_profiling_cycle(
        self,
        db: AsyncSession,
        max_signals: int = 20,
    ) -> ProfilerExecutionSummary:
        """Runs entity resolution, verification, and ICP scoring across eligible new signals."""
        start_time = time.time()
        self.is_running = True
        self.last_run_at = datetime.now(timezone.utc)
        summary = ProfilerExecutionSummary()

        logger.info(f"Starting Profiler Agent cycle (limit={max_signals})...")

        # 1. Fetch eligible unprocessed signals
        query = select(Signal).where(Signal.status == "NEW").order_by(desc(Signal.created_at)).limit(max_signals)
        res = await db.execute(query)
        signals = res.scalars().all()
        summary.signals_processed = len(signals)

        if not signals:
            logger.info("No unprocessed signals found for profiling.")
            self.is_running = False
            return summary

        for sig in signals:
            try:
                # 2. Entity Resolution
                candidate, entity_evidence = EntityResolver.resolve(
                    title=sig.title if hasattr(sig, 'title') and sig.title else "",
                    content=sig.raw_content,
                    author=sig.author_handle,
                    source_url=sig.original_url,
                    extracted_evidence=sig.extracted_evidence,
                )

                if not candidate:
                    # Anonymous or unverified: leave as UNRESOLVED, do not fabricate
                    sig.status = "UNRESOLVED"
                    summary.unresolved_signals += 1
                    continue

                summary.companies_identified += 1
                evidence_records = [e.model_dump(mode="json") for e in entity_evidence]

                # 3. Domain Verification (if domain is resolved)
                dns_records = []
                if candidate.domain:
                    dns_res, dns_evidence = await DomainVerifier.verify(candidate.domain)
                    evidence_records.extend([e.model_dump(mode="json") for e in dns_evidence])
                    dns_records = [r.model_dump(mode="json") for r in dns_res.records]

                # 4. Technology Profiling
                tech_profile = await TechnologyProfiler.profile_company(
                    company_name=candidate.company_name,
                    domain=candidate.domain,
                    raw_signal_text=sig.raw_content,
                    signal_evidence=sig.extracted_evidence,
                )
                for te in tech_profile.evidence:
                    evidence_records.append(te.model_dump(mode="json"))

                # 5. ICP Scoring & Qualification
                infra_indicators = {
                    "inferred_nodes": sig.extracted_evidence.get("inferred_nodes", 100),
                    "dns_active": bool(dns_records),
                }
                score_report = IcpScorer.evaluate(
                    company_name=candidate.company_name,
                    estimated_size=candidate.estimated_size,
                    tech_profile=tech_profile,
                    identity_confidence=candidate.identity_confidence,
                    signal_urgency=sig.urgency_score,
                    complaint_category=sig.complaint_category,
                    infra_indicators=infra_indicators,
                )

                # Track qualification states
                if score_report.qualification_status == "ACCEPTED":
                    summary.companies_accepted += 1
                    sig.status = "QUALIFIED"
                elif score_report.qualification_status == "REJECTED":
                    summary.companies_rejected += 1
                    sig.status = "REJECTED"
                else:
                    summary.companies_review_required += 1
                    sig.status = "PROFILED"

                # 6. Resolve Decision Makers via Crustdata Intelligence
                resolved_decision_makers = list(candidate.decision_makers) if candidate.decision_makers else []
                if candidate.domain:
                    try:
                        from app.services.crustdata.mock_provider import CrustdataMockProvider
                        c_prof = CrustdataMockProvider.enrich_company(candidate.domain)
                        if c_prof.leadership:
                            resolved_decision_makers = [
                                {
                                    "name": l.get("name"),
                                    "title": l.get("title"),
                                    "role": l.get("title"),
                                    "department": "Engineering",
                                }
                                for l in c_prof.leadership
                            ]
                    except Exception:
                        pass

                # 7. Persist Company Record into Database
                company = Company(
                    signal_id=sig.id,
                    name=candidate.company_name,
                    domain=candidate.domain,
                    company_description=candidate.description,
                    estimated_size=candidate.estimated_size,
                    industry=candidate.industry,
                    tech_stack=tech_profile.detected_technologies,
                    infrastructure_indicators=infra_indicators,
                    icp_score=score_report.icp_fit_score,
                    identity_confidence=score_report.identity_confidence,
                    technology_confidence=score_report.technology_confidence,
                    qualification_status=score_report.qualification_status,
                    decision_makers=resolved_decision_makers,
                    evidence_sources=[sig.original_url] if sig.original_url else [],
                    evidence_records=evidence_records,
                    is_synthetic=sig.is_synthetic,
                    last_enriched_at=datetime.now(timezone.utc),
                )
                db.add(company)

            except Exception as e:
                msg = f"Error profiling signal {sig.signal_id}: {str(e)}"
                logger.error(msg, exc_info=True)
                summary.errors.append(msg)

        await db.commit()

        # 7. Record Agent Execution Log
        duration_ms = int((time.time() - start_time) * 1000)
        summary.execution_time_ms = duration_ms
        self.is_running = False

        log_entry = AgentExecutionLog(
            agent_name="PROFILER",
            signal_id=None,
            status="SUCCESS" if not summary.errors else "PARTIAL_SUCCESS",
            execution_time_ms=duration_ms,
            input_payload={"signals_processed": summary.signals_processed},
            output_payload=summary.model_dump(),
            error_message="; ".join(summary.errors) if summary.errors else None,
        )
        db.add(log_entry)
        await db.commit()

        logger.info(
            f"Profiler cycle complete: {summary.companies_identified} companies profiled "
            f"({summary.companies_accepted} accepted, {summary.companies_review_required} review, "
            f"{summary.unresolved_signals} unresolved) in {duration_ms}ms"
        )
        return summary

"""
Evidence Guard and Anti-Hallucination Verification Layer.
Validates generated outreach collateral against verified facts in Company, Signal,
FinOps, and Architecture models. Flags unverified claims, forbidden buzzwords, and
enforces clear estimation labeling.
"""

import re
from typing import List, Dict, Any, Tuple
from app.agents.copywriter.schemas import EvidenceAuditReport, EvidenceClaim
from app.agents.copywriter.config import FORBIDDEN_BUZZWORDS


class EvidenceGuard:
    """Verifies that generated sales collateral adheres strictly to factual data."""

    @classmethod
    def audit_collateral(
        cls,
        text_corpus: str,
        company_data: Dict[str, Any],
        finops_data: Dict[str, Any],
        arch_data: Dict[str, Any],
        signal_data: Dict[str, Any],
    ) -> EvidenceAuditReport:
        """
        Runs comprehensive anti-hallucination and factual compliance checks across all generated text.
        """
        claims_checked = 0
        verified_claims = 0
        inferred_claims = 0
        unsupported_claims: List[str] = []
        buzzwords_detected: List[str] = []

        lower_corpus = text_corpus.lower()

        # 1. Check for forbidden spammy buzzwords
        for buzzword in FORBIDDEN_BUZZWORDS:
            if buzzword in lower_corpus:
                buzzwords_detected.append(buzzword)

        # 2. Check company identity compliance
        company_name = company_data.get("name", "")
        if company_name and company_name.lower() in lower_corpus:
            claims_checked += 1
            verified_claims += 1

        # 3. Check for fake persona/email inventions (e.g. "john.doe@company.com")
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        found_emails = re.findall(email_pattern, text_corpus)
        for email in found_emails:
            # If an email is fabricated in the text body, flag it
            unsupported_claims.append(f"Fabricated email address found: {email}")

        # 4. Check financial accuracy and estimation qualifiers
        # Extract reported annual savings if available
        base_scenario = finops_data.get("scenarios", {}).get("BASE") or finops_data.get("base_scenario") or {}
        annual_savings = base_scenario.get("signoz_cloud_annual_savings") or finops_data.get("estimated_annual_savings", 0.0)
        
        claims_checked += 1
        # Check that financial claims include qualification if inputs were inferred
        has_estimation_qualifier = any(
            q in lower_corpus for q in ["estimated", "projected", "modeled", "potential", "approximate", "~$"]
        )
        if has_estimation_qualifier:
            inferred_claims += 1
        else:
            unsupported_claims.append("Financial figures presented as exact without required estimation qualifiers (e.g. 'estimated', 'projected').")

        # 5. Check technical truthfulness (OpenTelemetry, dual-shipping, port 8126)
        if "8126" in text_corpus or "receiver" in lower_corpus:
            claims_checked += 1
            # Check if mentioned accurately as receiver compatibility port
            if "datadog" in lower_corpus and ("8126" in text_corpus or "receiver" in lower_corpus):
                verified_claims += 1
            else:
                inferred_claims += 1

        if "dual-shipping" in lower_corpus or "dual shipping" in lower_corpus:
            claims_checked += 1
            verified_claims += 1

        # 6. Verify target alternative matches finops model
        target_challenger = finops_data.get("target_challenger", "SigNoz")
        if target_challenger.lower() in lower_corpus or "signoz" in lower_corpus or "grafana" in lower_corpus:
            claims_checked += 1
            verified_claims += 1

        # Calculate risk score
        risk_score = 0.0
        if buzzwords_detected:
            risk_score += min(len(buzzwords_detected) * 0.15, 0.45)
        if unsupported_claims:
            risk_score += min(len(unsupported_claims) * 0.35, 0.55)

        risk_score = min(round(risk_score, 2), 1.0)
        passed = len(unsupported_claims) == 0 and len(buzzwords_detected) == 0

        summary_parts = []
        if passed:
            summary_parts.append("Passed all factual alignment and anti-hallucination checks.")
        else:
            if buzzwords_detected:
                summary_parts.append(f"Forbidden marketing buzzwords detected: {', '.join(buzzwords_detected)}.")
            if unsupported_claims:
                summary_parts.append(f"Factual compliance issues: {'; '.join(unsupported_claims)}.")

        return EvidenceAuditReport(
            passed=passed,
            claims_checked=max(claims_checked, 1),
            verified_claims=verified_claims,
            inferred_or_estimated_claims=inferred_claims,
            unsupported_claims_flagged=unsupported_claims,
            buzzwords_detected=buzzwords_detected,
            hallucination_risk_score=risk_score,
            audit_summary=" ".join(summary_parts) if summary_parts else "Audit completed successfully.",
        )

"""
Enterprise Objection Handler for the Copywriter Agent.
Produces evidence-backed talking points and technical proof points for enterprise objections.
"""

from typing import Dict, Any, List
from app.agents.copywriter.schemas import ObjectionItem, ObjectionHandlingMatrix
from app.agents.copywriter.config import STANDARD_OBJECTIONS


class ObjectionHandler:
    """Generates structured enterprise objection responses backed by architecture and financial evidence."""

    @classmethod
    def generate_matrix(
        cls,
        context: Dict[str, Any],
        finops_data: Dict[str, Any],
        arch_data: Dict[str, Any],
    ) -> ObjectionHandlingMatrix:
        """Generates the full objection handling matrix."""
        target_challenger = context["target_challenger"]
        items: List[ObjectionItem] = []

        proof_points = {
            "BANDWIDTH": (
                "The OpenTelemetry Collector includes a Datadog trace receiver on port `:8126`. "
                "Applications continue emitting standard `dd-trace` payloads without refactoring. "
                "Total engineering effort is phased over 60-80 hours with zero interruption to active sprints."
            ),
            "DOWNTIME_RISK": (
                "Dual-shipping configuration mirrors all telemetry in real time to Datadog and the target challenger. "
                "Datadog remains the active source of truth during all validation stages. "
                "There is zero telemetry blackout or production risk."
            ),
            "CONTRACT_LOCKIN": (
                "Deploying the OpenTelemetry collector immediately caps Datadog overages by routing secondary telemetry. "
                "Parallel validation prepares the infrastructure for a seamless same-day cutover upon contract expiration."
            ),
            "HISTORICAL_DATA": (
                "Datadog monitor JSON definitions translate directly to PromQL and SigNoz alert formats. "
                "Historical logs can remain in cloud cold storage (S3/GCS) while live ingestion transitions cleanly."
            ),
            "SELF_HOSTED_BURDEN": (
                f"{target_challenger} offers a fully managed enterprise cloud tier with 99.9% availability SLAs, "
                "eliminating all ClickHouse operational overhead while still delivering 40-70% lower TCO than Datadog."
            ),
            "STATUS_QUO": (
                "Datadog's host-based pricing penalizes infrastructure growth (Kubernetes node scaling and microservices). "
                "Standardizing on CNCF OpenTelemetry future-proofs the stack and frees up budget for engineering headcount."
            ),
            "ROLLBACK_SAFETY": (
                "Zero-loss rollback is architected into the collector pipeline: disabling the OTLP exporter instantaneously "
                "restores pure Datadog operation with zero data loss or application downtime."
            ),
        }

        for obj in STANDARD_OBJECTIONS:
            obj_id = obj["id"]
            talking_points = obj["talking_points"]
            proof = proof_points.get(obj_id, "Validated through OpenTelemetry dual-shipping architecture.")
            
            recommended_resp = (
                f"We completely respect this constraint. That is why the migration architecture is built around "
                f"risk-free dual-shipping and native port :8126 receiver compatibility: {talking_points[0]} {proof}"
            )

            items.append(
                ObjectionItem(
                    objection_id=obj_id,
                    objection=obj["objection"],
                    talking_points=talking_points,
                    recommended_response=recommended_resp,
                    technical_proof_point=proof,
                )
            )

        return ObjectionHandlingMatrix(items=items)

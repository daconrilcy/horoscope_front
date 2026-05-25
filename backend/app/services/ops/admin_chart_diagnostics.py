# Commentaire global: ce service assemble un diagnostic admin
# sans stocker de payload astrologique brut.
"""Service canonique de projection `admin_chart_diagnostics_v1`."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.auth_context import AuthenticatedUser
from app.core.datetime_provider import utc_now
from app.core.sensitive_data import PolicyAction, redact_value
from app.domain.astrology.runtime.natal_calculation_graph import (
    build_natal_calculation_graph_definition,
)
from app.infra.db.repositories.chart_result_repository import ChartResultRepository
from app.services.api_contracts.admin.chart_diagnostics import (
    AdminChartDiagnosticNode,
    AdminChartDiagnosticsGraph,
    AdminChartDiagnosticsLimits,
    AdminChartDiagnosticsRedaction,
    AdminChartDiagnosticsResponse,
    AdminChartDiagnosticsSummary,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

PROJECTION_ID = "admin_chart_diagnostics_v1"
POLICY_ID = "admin_chart_diagnostics_v1_policy"
AUDIT_ACTION = "admin_chart_diagnostics_consulted"
AUDIT_TARGET_TYPE = "chart_diagnostics"


class AdminChartDiagnosticsSourceMissingError(Exception):
    """Erreur levee quand le resultat de theme demande est absent."""

    def __init__(self, chart_reference: str) -> None:
        self.chart_reference = _masked_chart_reference(chart_reference)
        super().__init__(chart_reference)


class AdminChartDiagnosticsService:
    """Construit le diagnostic a partir des proprietaires runtime existants."""

    @staticmethod
    def get_chart_diagnostics(
        db: Session,
        *,
        chart_reference: str,
        request_id: str,
        current_user: AuthenticatedUser,
    ) -> AdminChartDiagnosticsResponse:
        """Retourne un diagnostic masque et journalise la consultation admin."""
        source = ChartResultRepository(db).get_by_chart_id(chart_reference)
        if source is None:
            AdminChartDiagnosticsService.record_failed_consultation(
                db,
                chart_reference=chart_reference,
                request_id=request_id,
                current_user=current_user,
                decision="failed",
                error_code="source_missing",
            )
            raise AdminChartDiagnosticsSourceMissingError(chart_reference)

        graph = build_natal_calculation_graph_definition()
        masked_reference = _masked_chart_reference(source.chart_id)
        nodes = [
            AdminChartDiagnosticNode(
                code=node.code,
                status="declared",
                source_versions={
                    "graph_version": graph.version,
                    "reference_version": source.reference_version,
                    "ruleset_version": source.ruleset_version,
                },
                proof_refs=[f"graph:{graph.graph_code}", f"node:{node.code}"],
            )
            for node in graph.nodes
        ]
        response = AdminChartDiagnosticsResponse(
            projection_id=PROJECTION_ID,
            chart_reference=masked_reference,
            calculation_graph=AdminChartDiagnosticsGraph(
                graph_family=graph.graph_code,
                graph_version=graph.version,
                nodes=nodes,
            ),
            diagnostic_summary=AdminChartDiagnosticsSummary(
                status="available",
                warnings=[],
                node_count=len(nodes),
                source_state="persisted_chart_result",
            ),
            redaction=AdminChartDiagnosticsRedaction(
                policy_id=POLICY_ID,
                applied=["chart_reference_hashed", "raw_birth_fields_omitted"],
                omitted_raw_field_categories=[
                    "raw_birth_data",
                    "precise_location",
                    "raw_graph_payload",
                    "provider_debug_dump",
                ],
            ),
            limits=AdminChartDiagnosticsLimits(
                statement=(
                    "Current calculation diagnostics only; replay, public fixed stars "
                    "and narrative answer audit are excluded."
                )
            ),
            generated_at=utc_now(),
            correlation_id=request_id,
        )
        _record_consultation(
            db,
            request_id=request_id,
            current_user=current_user,
            subject_reference_hash=masked_reference,
            status="success",
            decision="allowed",
            node_count=len(nodes),
        )
        return response

    @staticmethod
    def record_failed_consultation(
        db: Session,
        *,
        chart_reference: str,
        request_id: str,
        current_user: AuthenticatedUser,
        decision: str,
        error_code: str,
    ) -> None:
        """Journalise une tentative refusee ou impossible sans exposer la source."""
        _record_consultation(
            db,
            request_id=request_id,
            current_user=current_user,
            subject_reference_hash=_masked_chart_reference(chart_reference),
            status="failed",
            decision=decision,
            node_count=0,
            error_code=error_code,
        )


def _masked_chart_reference(chart_reference: str) -> str:
    """Hash une reference de theme via la politique sensible existante."""
    masked = redact_value(chart_reference, PolicyAction.HASHED)
    return str(masked)


def _record_consultation(
    db: Session,
    *,
    request_id: str,
    current_user: AuthenticatedUser,
    subject_reference_hash: str,
    status: str,
    decision: str,
    node_count: int,
    error_code: str | None = None,
) -> None:
    """Journalise la lecture sans copier le diagnostic dans l'audit."""
    details: dict[str, object] = {
        "contract_id": POLICY_ID,
        "projection_id": PROJECTION_ID,
        "route_family": "astrology",
        "action": "diagnostic_read",
        "decision": decision,
        "correlation_id": request_id,
        "subject_reference_hash": subject_reference_hash,
        "diagnostic_scope": "calculation_graph_metadata",
        "node_count": node_count,
    }
    if error_code is not None:
        details["error_code"] = error_code

    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action=AUDIT_ACTION,
            target_type=AUDIT_TARGET_TYPE,
            target_id=subject_reference_hash,
            status=status,
            details=details,
        ),
    )

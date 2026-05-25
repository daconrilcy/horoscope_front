# Commentaire global: ce module definit le contrat API admin du diagnostic de calcul astrologique.
"""Schemas Pydantic de la projection admin `admin_chart_diagnostics_v1`."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AdminChartDiagnosticNode(BaseModel):
    """Expose un node de calcul sans payload brut ni donnees de naissance."""

    code: str
    status: Literal["declared"]
    source_versions: dict[str, str]
    proof_refs: list[str] = Field(default_factory=list)


class AdminChartDiagnosticsGraph(BaseModel):
    """Decrit le graphe de calcul inspecte par la projection admin."""

    graph_family: str
    graph_version: str
    nodes: list[AdminChartDiagnosticNode]


class AdminChartDiagnosticsSummary(BaseModel):
    """Resume le diagnostic sans reconstruire un replay de calcul."""

    status: Literal["available"]
    warnings: list[str] = Field(default_factory=list)
    node_count: int
    source_state: Literal["persisted_chart_result"]


class AdminChartDiagnosticsRedaction(BaseModel):
    """Liste les traitements de masquage appliques au payload expose."""

    policy_id: Literal["admin_chart_diagnostics_v1_policy"]
    applied: list[str]
    omitted_raw_field_categories: list[str]


class AdminChartDiagnosticsLimits(BaseModel):
    """Declare les limites de la projection pour eviter tout amalgame replay/audit."""

    replay_included: Literal[False] = False
    public_fixed_stars_included: Literal[False] = False
    narrative_answer_audit_included: Literal[False] = False
    statement: str


class AdminChartDiagnosticsResponse(BaseModel):
    """Payload de reponse stable de `admin_chart_diagnostics_v1`."""

    projection_id: Literal["admin_chart_diagnostics_v1"]
    chart_reference: str
    calculation_graph: AdminChartDiagnosticsGraph
    diagnostic_summary: AdminChartDiagnosticsSummary
    redaction: AdminChartDiagnosticsRedaction
    limits: AdminChartDiagnosticsLimits
    generated_at: datetime
    correlation_id: str

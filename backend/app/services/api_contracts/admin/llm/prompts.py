"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field

from app.domain.llm.configuration.admin_models import (
    AdminUseCaseAudit,
    LlmOutputSchema,
    LlmPersona,
    LlmPromptVersion,
    LlmUseCaseConfig,
)
from app.domain.llm.prompting.persona_boundary import (
    PersonaBoundaryViolation,
)

AdminInspectionMode = Literal["assembly_preview", "runtime_preview", "live_execution"]
AdminSelectedComponentType = Literal[
    "domain_instructions",
    "use_case_overlay",
    "plan_overlay",
    "persona_overlay",
    "output_contract",
    "style_lexicon_rules",
    "error_handling_rules",
    "hard_policy",
]
AdminRuntimeArtifactType = Literal[
    "developer_prompt_assembled",
    "developer_prompt_after_persona",
    "developer_prompt_after_injectors",
    "system_prompt",
    "final_provider_payload",
]


class LlmUseCaseContract(LlmUseCaseConfig):
    """Contrat Pydantic exposé par l'API."""

    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None
    required_prompt_placeholders: List[str] = Field(default_factory=list)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str
    warnings: List[str] = Field(default_factory=list)
    boundary_violations: List[PersonaBoundaryViolation] = Field(default_factory=list)


class LlmUseCaseListResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: List[LlmUseCaseConfig]
    meta: ResponseMeta


class LlmUseCaseContractResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: LlmUseCaseContract
    meta: ResponseMeta


class LlmPersonaListResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: List[LlmPersona]
    meta: ResponseMeta


class LlmPersonaApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: LlmPersona
    meta: ResponseMeta


class LlmPersonaDetail(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    persona: LlmPersona
    use_cases: list[str]
    affected_users_count: int


class LlmPersonaDetailResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: LlmPersonaDetail
    meta: ResponseMeta


class LlmOutputSchemaListResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: List[LlmOutputSchema]
    meta: ResponseMeta


class LlmOutputSchemaApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: LlmOutputSchema
    meta: ResponseMeta


class UseCaseUpdatePayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    persona_id: Optional[str] = None
    persona_strategy: Optional[str] = None
    safety_profile: Optional[str] = None
    output_schema_id: Optional[str] = None
    eval_fixtures_path: Optional[str] = None
    eval_failure_threshold: Optional[float] = None
    golden_set_path: Optional[str] = None


class PersonaAssociationPayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    persona_id: Optional[str] = None


class LlmPromptHistoryResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: List[LlmPromptVersion]
    meta: ResponseMeta


class LlmPromptApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: LlmPromptVersion
    meta: ResponseMeta


class LlmPromptPublishResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: LlmPromptVersion
    meta: dict  # includes eval_report


class RollbackPromptPayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    target_version_id: uuid.UUID | None = None


class LlmCallLog(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: uuid.UUID
    use_case: str
    prompt_version_id: Optional[uuid.UUID]
    persona_id: Optional[uuid.UUID]
    model: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd_estimated: float
    validation_status: str
    repair_attempted: bool
    fallback_triggered: bool
    request_id: str
    trace_id: str
    environment: str
    timestamp: datetime
    evidence_warnings_count: int


class LlmCallLogListResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: List[LlmCallLog]
    meta: dict


class ReplayPayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str
    prompt_version_id: str


class LlmDashboardMetrics(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    use_case: str
    request_count: int
    avg_latency_ms: float
    p95_latency_ms: float
    total_tokens: int
    total_cost_usd: float
    validation_status_distribution: dict[str, float]  # % valid, repair, etc.
    repair_rate: float
    fallback_rate: float
    avg_tokens_per_request: float
    evidence_warning_rate: float


class LlmDashboardResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: List[LlmDashboardMetrics]
    meta: ResponseMeta


class AdminLlmCatalogEntry(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    manifest_entry_id: str
    feature: str
    subfeature: str | None = None
    plan: str | None = None
    locale: str | None = None
    assembly_id: str | None = None
    assembly_status: str
    execution_profile_id: str | None = None
    execution_profile_ref: str | None = None
    output_schema_id: str | None = None
    active_snapshot_id: str | None = None
    active_snapshot_version: str | None = None
    provider: str | None = None
    model: str | None = None
    source_of_truth_status: str
    release_health_status: str
    catalog_visibility_status: str
    runtime_signal_status: str
    execution_path_kind: str | None = None
    context_compensation_status: str | None = None
    max_output_tokens_source: str | None = None


class AdminLlmCatalogResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: List[AdminLlmCatalogEntry]
    meta: dict[str, Any]


class ResolvedCompositionSources(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    feature_template: dict[str, Any]
    subfeature_template: dict[str, Any] | None = None
    plan_rules: dict[str, Any] | None = None
    persona_block: dict[str, Any] | None = None
    hard_policy: dict[str, Any]
    execution_profile: dict[str, Any]


class ResolvedTransformationPipeline(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    assembled_prompt: str
    post_injectors_prompt: str
    rendered_prompt: str


class ResolvedPlaceholderView(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    name: str
    status: Literal[
        "resolved",
        "optional_missing",
        "fallback_used",
        "blocking_missing",
        "expected_missing_in_preview",
        "unknown",
    ]
    classification: str | None = None
    resolution_source: str | None = None
    reason: str | None = None
    safe_to_display: bool = False
    value_preview: str | None = None


class ResolvedResultView(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    provider_messages: dict[str, Any]
    placeholders: list[ResolvedPlaceholderView]
    context_quality_handled_by_template: bool
    context_quality_instruction_injected: bool
    context_compensation_status: str
    source_of_truth_status: str
    active_snapshot_id: str | None = None
    active_snapshot_version: str | None = None
    manifest_entry_id: str


class AdminResolvedActivationView(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    manifest_entry_id: str
    feature: str
    subfeature: str | None = None
    plan: str | None = None
    locale: str | None = None
    active_snapshot_id: str | None = None
    active_snapshot_version: str | None = None
    execution_profile: str | None = None
    provider_target: str
    policy_family: str
    output_schema: str | None = None
    injector_set: list[str] = Field(default_factory=list)
    persona_policy: str | None = None


class AdminSelectedComponentView(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    key: str
    component_type: AdminSelectedComponentType
    title: str
    content: str | None = None
    summary: str
    ref: str | None = None
    source_label: str | None = None
    version_label: str | None = None
    merge_mode: str | None = None
    impact_status: Literal["active", "inactive", "absent", "reference_only"] = "active"
    editable_use_case_key: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class AdminRuntimeArtifactView(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    key: str
    artifact_type: AdminRuntimeArtifactType
    title: str
    content: str | None = None
    summary: str
    change_status: Literal["changed", "unchanged", "absent"] = "changed"
    delta_note: str | None = None
    injection_point: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class AdminResolvedAssemblyView(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    manifest_entry_id: str
    feature: str
    subfeature: str | None = None
    plan: str | None = None
    locale: str | None = None
    use_case_key: str
    canonical_use_case_key: str | None = None
    runtime_use_case_key: str | None = None
    use_case_audit: AdminUseCaseAudit | None = None
    runtime_use_case_audit: AdminUseCaseAudit | None = None
    context_quality: str
    assembly_id: str | None = None
    inspection_mode: AdminInspectionMode
    source_of_truth_status: str
    active_snapshot_id: str | None = None
    active_snapshot_version: str | None = None
    activation: AdminResolvedActivationView
    selected_components: list[AdminSelectedComponentView]
    runtime_artifacts: list[AdminRuntimeArtifactView]
    composition_sources: ResolvedCompositionSources
    transformation_pipeline: ResolvedTransformationPipeline
    resolved_result: ResolvedResultView


class AdminResolvedAssemblyResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: AdminResolvedAssemblyView
    meta: ResponseMeta


class AdminCatalogManualExecutePayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    sample_payload_id: uuid.UUID


class AdminCatalogManualExecuteResponseData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    manifest_entry_id: str
    sample_payload_id: str
    use_case_key: str
    provider: str
    model: str
    request_id: str
    trace_id: str
    gateway_request_id: str
    prompt_sent: str
    resolved_runtime_parameters: dict[str, Any]
    raw_output: str
    structured_output: dict[str, Any] | None = None
    structured_output_parseable: bool = False
    validation_status: str
    execution_path: str = "nominal"
    meta_validation_errors: list[str] | None = None
    latency_ms: int
    admin_manual_execution: Literal[True] = True
    usage_input_tokens: int = 0
    usage_output_tokens: int = 0


class AdminCatalogManualExecuteResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: AdminCatalogManualExecuteResponseData
    meta: ResponseMeta


class ProofSummary(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    proof_type: Literal["qualification", "golden", "smoke", "readiness"]
    status: str
    verdict: str | None = None
    generated_at: str | None = None
    manifest_entry_id: str | None = None
    correlated: bool = False


class SnapshotTimelineItem(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    event_type: Literal[
        "created",
        "validated",
        "activated",
        "monitoring",
        "degraded",
        "rollback_recommended",
        "rolled_back",
        "backend_unmapped",
    ]
    snapshot_id: str
    snapshot_version: str
    occurred_at: str
    current_status: str
    release_health_status: str
    status_history: list[dict[str, Any]] = Field(default_factory=list)
    reason: str | None = None
    from_snapshot_id: str | None = None
    to_snapshot_id: str | None = None
    manifest_entry_count: int = 0
    proof_summaries: list[ProofSummary] = Field(default_factory=list)


class SnapshotTimelineResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[SnapshotTimelineItem]
    meta: ResponseMeta


class SnapshotDiffEntry(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    manifest_entry_id: str
    category: Literal["added", "removed", "changed", "unchanged"]
    assembly_changed: bool
    execution_profile_changed: bool
    output_contract_changed: bool
    from_snapshot_id: str
    to_snapshot_id: str


class SnapshotDiffResponsePayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    from_snapshot_id: str
    to_snapshot_id: str
    entries: list[SnapshotDiffEntry]


class SnapshotDiffResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: SnapshotDiffResponsePayload
    meta: ResponseMeta

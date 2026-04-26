"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

from datetime import datetime
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix="/v1/ops/entitlements", tags=["ops-entitlement-audits"])
WritableReviewStatusLiteral = Literal["acknowledged", "expected", "investigating", "closed"]
ReviewStatusLiteral = Literal[
    "pending_review", "acknowledged", "expected", "investigating", "closed"
]
PersistedReviewStatusLiteral = WritableReviewStatusLiteral
_DIFF_FILTER_MAX = 10_000


class ReviewState(BaseModel):
    status: ReviewStatusLiteral
    reviewed_by_user_id: int | None = None
    reviewed_at: datetime | None = None
    review_comment: str | None = None
    incident_key: str | None = None


class ReviewRequestBody(BaseModel):
    review_status: WritableReviewStatusLiteral
    review_comment: str | None = None
    incident_key: str | None = None


class ReviewResponse(BaseModel):
    audit_id: int
    review_status: WritableReviewStatusLiteral
    reviewed_by_user_id: int | None = None
    reviewed_at: datetime
    review_comment: str | None = None
    incident_key: str | None = None


class QuotaChangeSummarySchema(BaseModel):
    added: list[dict]
    removed: list[dict]
    updated: list[dict]


class MutationAuditItem(BaseModel):
    id: int
    occurred_at: datetime
    operation: str
    plan_id: int
    plan_code_snapshot: str
    feature_code: str
    actor_type: str
    actor_identifier: str
    request_id: str | None
    source_origin: str
    # Diff champs dérivés — TOUJOURS présents, non-optionnels
    change_kind: str
    changed_fields: list[str]
    risk_level: str
    quota_changes: QuotaChangeSummarySchema
    # Review — optionnel, omis si null via response_model_exclude_none=True
    review: ReviewState | None = None
    # Payloads bruts — conditionnels (include_payloads), omis par exclude_none
    before_payload: dict | None = None
    after_payload: dict | None = None


class AlertSuppressionRuleItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_kind: str
    feature_code: str | None = None
    plan_code: str | None = None
    actor_type: str | None = None
    suppression_key: str | None = None
    ops_comment: str | None = None
    is_active: bool
    created_by_user_id: int | None = None
    created_at: datetime
    updated_by_user_id: int | None = None
    updated_at: datetime


class CreateAlertSuppressionRuleRequestBody(BaseModel):
    alert_kind: str = Field(..., min_length=1, max_length=32)
    feature_code: str | None = Field(None, max_length=64)
    plan_code: str | None = Field(None, max_length=64)
    actor_type: str | None = Field(None, max_length=32)
    suppression_key: str | None = Field(None, max_length=64)
    ops_comment: str | None = None
    is_active: bool = True


class UpdateAlertSuppressionRuleRequestBody(BaseModel):
    is_active: bool | None = None
    ops_comment: str | None = None
    suppression_key: str | None = None


class AlertSuppressionRuleListResponse(BaseModel):
    data: "AlertSuppressionRuleListData"
    meta: ResponseMeta


class AlertSuppressionRuleApiResponse(BaseModel):
    data: AlertSuppressionRuleItem
    meta: ResponseMeta


class AlertSuppressionRuleListData(BaseModel):
    items: list[AlertSuppressionRuleItem]
    total_count: int
    page: int
    page_size: int


class MutationAuditListData(BaseModel):
    items: list[MutationAuditItem]
    total_count: int
    page: int
    page_size: int


class ResponseMeta(BaseModel):
    request_id: str


class MutationAuditListApiResponse(BaseModel):
    data: MutationAuditListData
    meta: ResponseMeta


class MutationAuditDetailApiResponse(BaseModel):
    data: MutationAuditItem
    meta: ResponseMeta


class ReviewApiResponse(BaseModel):
    data: ReviewResponse
    meta: ResponseMeta


class ReviewEventItem(BaseModel):
    id: int
    audit_id: int
    event_type: str
    previous_review_status: PersistedReviewStatusLiteral | None = None
    new_review_status: PersistedReviewStatusLiteral
    previous_review_comment: str | None = None
    new_review_comment: str | None = None
    previous_incident_key: str | None = None
    new_incident_key: str | None = None
    reviewed_by_user_id: int | None = None
    occurred_at: datetime
    request_id: str | None = None


class ReviewHistoryData(BaseModel):
    items: list[ReviewEventItem]
    total_count: int


class ReviewHistoryApiResponse(BaseModel):
    data: ReviewHistoryData
    meta: ResponseMeta


class ReviewQueueItem(MutationAuditItem):
    effective_review_status: ReviewStatusLiteral | None = None
    age_seconds: int
    age_hours: float
    is_pending: bool
    is_closed: bool
    sla_target_seconds: int | None = None
    due_at: datetime | None = None
    sla_status: Literal["within_sla", "due_soon", "overdue"] | None = None
    overdue_seconds: int | None = None


class ReviewQueueListData(BaseModel):
    items: list[ReviewQueueItem]
    total_count: int
    page: int
    page_size: int


class ReviewQueueApiResponse(BaseModel):
    data: ReviewQueueListData
    meta: ResponseMeta


class ReviewQueueSummaryData(BaseModel):
    pending_review_count: int
    investigating_count: int
    acknowledged_count: int
    closed_count: int
    expected_count: int
    no_review_count: int
    high_unreviewed_count: int
    total_count: int
    # Nouveaux champs SLA
    overdue_count: int
    due_soon_count: int
    oldest_pending_age_seconds: int | None = None


class ReviewQueueSummaryApiResponse(BaseModel):
    data: ReviewQueueSummaryData
    meta: ResponseMeta


class AlertAttemptItem(BaseModel):
    id: int
    alert_event_id: int
    attempt_number: int
    delivery_channel: str
    delivery_status: str
    delivery_error: str | None = None
    request_id: str | None = None
    created_at: datetime
    delivered_at: datetime | None = None


class AlertAttemptsListData(BaseModel):
    items: list[AlertAttemptItem]
    total_count: int


class AlertAttemptsApiResponse(BaseModel):
    data: AlertAttemptsListData
    meta: ResponseMeta


class AlertRetryRequestBody(BaseModel):
    dry_run: bool = False


class BatchRetryRequestBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    limit: int = Field(..., ge=1, le=100)
    dry_run: bool = False
    alert_kind: str | None = None
    audit_id: int | None = None
    feature_code: str | None = None
    plan_code: str | None = None
    actor_type: str | None = None
    request_id_filter: str | None = Field(default=None, alias="request_id")
    date_from: datetime | None = None
    date_to: datetime | None = None


class AlertRetryResponseData(BaseModel):
    alert_event_id: int
    attempted: bool
    delivery_status: str | None = None
    attempt_number: int | None = None
    request_id: str | None = None


class AlertRetryApiResponse(BaseModel):
    data: AlertRetryResponseData
    meta: ResponseMeta


class BatchRetryResultData(BaseModel):
    candidate_count: int
    retried_count: int
    sent_count: int
    failed_count: int
    skipped_count: int
    dry_run: bool
    alert_event_ids: list[int]


class BatchRetryApiResponse(BaseModel):
    data: BatchRetryResultData
    meta: ResponseMeta


class BatchHandleRequestBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    limit: int = Field(..., ge=1, le=200)
    handling_status: Literal["suppressed", "resolved"]
    dry_run: bool = False
    ops_comment: str | None = None
    suppression_key: str | None = None
    alert_kind: str | None = None
    audit_id: int | None = None
    feature_code: str | None = None
    plan_code: str | None = None
    actor_type: str | None = None
    request_id_filter: str | None = Field(default=None, alias="request_id")
    date_from: datetime | None = None
    date_to: datetime | None = None


class BatchHandleResultData(BaseModel):
    candidate_count: int
    handled_count: int
    skipped_count: int
    dry_run: bool
    alert_event_ids: list[int]


class BatchHandleApiResponse(BaseModel):
    data: BatchHandleResultData
    meta: ResponseMeta


class AlertHandlingState(BaseModel):
    handling_status: str
    source: Literal["manual", "rule", "virtual"]
    suppression_rule_id: int | None = None
    handled_by_user_id: int | None = None
    handled_at: datetime | None = None
    ops_comment: str | None = None
    suppression_key: str | None = None


class AlertEventItem(BaseModel):
    id: int
    audit_id: int
    dedupe_key: str
    alert_kind: str
    delivery_status: str
    delivery_channel: str
    delivery_error: str | None = None
    created_at: datetime
    delivered_at: datetime | None = None
    feature_code_snapshot: str
    plan_id_snapshot: int
    plan_code_snapshot: str
    risk_level_snapshot: str
    effective_review_status_snapshot: str | None = None
    actor_type_snapshot: str
    actor_identifier_snapshot: str
    age_seconds_snapshot: int
    sla_target_seconds_snapshot: int | None = None
    due_at_snapshot: datetime | None = None
    request_id: str | None = None
    attempt_count: int
    last_attempt_number: int | None = None
    last_attempt_status: str | None = None
    handling: AlertHandlingState | None = None
    retryable: bool


class AlertEventListData(BaseModel):
    items: list[AlertEventItem]
    total_count: int
    page: int
    page_size: int


class AlertEventListApiResponse(BaseModel):
    data: AlertEventListData
    meta: ResponseMeta


class AlertSummaryData(BaseModel):
    total_count: int
    failed_count: int
    sent_count: int
    retryable_count: int
    webhook_failed_count: int
    log_sent_count: int
    suppressed_count: int
    resolved_count: int


class HandleAlertRequestBody(BaseModel):
    handling_status: Literal["suppressed", "resolved"]
    ops_comment: str | None = None
    suppression_key: str | None = None


class HandleAlertResponseData(BaseModel):
    alert_event_id: int
    handling_status: str
    handled_by_user_id: int | None = None
    handled_at: datetime
    ops_comment: str | None = None
    suppression_key: str | None = None


class HandleAlertApiResponse(BaseModel):
    data: HandleAlertResponseData
    meta: ResponseMeta


class AlertHandlingHistoryItem(BaseModel):
    id: int
    alert_event_id: int
    event_type: str
    handling_status: str
    handled_by_user_id: int | None = None
    handled_at: datetime
    resolution_code: str | None = None
    incident_key: str | None = None
    requires_followup: bool = False
    followup_due_at: datetime | None = None
    ops_comment: str | None = None
    suppression_key: str | None = None
    request_id: str | None = None


class AlertHandlingHistoryData(BaseModel):
    items: list[AlertHandlingHistoryItem]
    total_count: int
    limit: int
    offset: int


class AlertHandlingHistoryApiResponse(BaseModel):
    data: AlertHandlingHistoryData
    meta: ResponseMeta


class AlertSummaryApiResponse(BaseModel):
    data: AlertSummaryData
    meta: ResponseMeta

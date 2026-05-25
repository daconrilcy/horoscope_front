"""Schemas Pydantic des endpoints admin d'audit."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AdminAuditLogItem(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: int
    timestamp: datetime
    actor_email_masked: str | None
    actor_role: str
    action: str
    target_type: str | None
    target_id_masked: str | None
    status: str
    details: dict

    model_config = ConfigDict(from_attributes=True)


class AdminAuditLogResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[AdminAuditLogItem]
    total: int
    page: int
    per_page: int


class AdminAuditExportRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    actor: str | None = None
    action: str | None = None
    target_type: str | None = None
    period: Literal["7d", "30d", "all"] | None = None


RejectedAnswerReviewStatus = Literal[
    "pending_review",
    "under_review",
    "resolved_prompt_followup",
    "resolved_contract_followup",
    "resolved_validation_followup",
    "dismissed",
]


class RejectedAnswerReviewAuditEvent(BaseModel):
    """Résumé de l'événement d'audit produit par le workflow de revue."""

    event_id: int
    action: str
    target_type: str
    target_id: str | None
    status: str
    created_at: datetime


class RejectedAnswerReviewItem(BaseModel):
    """Item admin listant une réponse narrative rejetée sans exposition client."""

    contract_id: Literal["admin_answer_audit_v1"] = "admin_answer_audit_v1"
    answer_id: str
    status: Literal["rejected"] = "rejected"
    review_status: RejectedAnswerReviewStatus
    rejection_reason: dict[str, object]
    missing_evidence_refs: list[str]
    prompt_version: str
    projection_version: str
    provider: str
    model: str
    created_at: datetime
    reviewed_at: datetime | None = None
    reviewed_by: int | None = None
    review_note: str | None = None


class RejectedAnswerReviewListResponse(BaseModel):
    """Réponse paginée du workflow admin de revue des réponses rejetées."""

    data: list[RejectedAnswerReviewItem]
    total: int
    page: int
    per_page: int


class RejectedAnswerReviewDetailResponse(RejectedAnswerReviewItem):
    """Détail admin d'une réponse rejetée avec contexte et preuve de journalisation."""

    manual_correction_limits: list[str]
    audit_event: RejectedAnswerReviewAuditEvent


class RejectedAnswerReviewUpdateRequest(BaseModel):
    """Payload de changement de statut interne pour une réponse rejetée."""

    review_status: str = Field(min_length=1, max_length=64)
    review_note: str | None = Field(default=None, max_length=500)

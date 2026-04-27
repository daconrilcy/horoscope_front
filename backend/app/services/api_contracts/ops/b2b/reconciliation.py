"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.b2b.reconciliation_service import (
    ReconciliationActionResultData,
    ReconciliationIssueDetailData,
    ReconciliationIssueListData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class ReconciliationIssueListApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: ReconciliationIssueListData
    meta: ResponseMeta


class ReconciliationIssueDetailApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: ReconciliationIssueDetailData
    meta: ResponseMeta


class ReconciliationActionApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: ReconciliationActionResultData
    meta: ResponseMeta

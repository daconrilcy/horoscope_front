from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.domain.astrology.natal_calculation import NatalResult
from app.domain.astrology.natal_preparation import BirthInput
from app.infra.db.repositories.chart_result_repository import ChartResultRepository


class ChartResultAuditRecord(BaseModel):
    chart_id: str
    reference_version: str
    ruleset_version: str
    input_hash: str
    result: NatalResult
    created_at: datetime


class ChartResultServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ChartResultService:
    @staticmethod
    def compute_input_hash(
        birth_input: BirthInput,
        reference_version: str,
        ruleset_version: str,
    ) -> str:
        payload = {
            "birth_input": birth_input.model_dump(mode="json"),
            "reference_version": reference_version,
            "ruleset_version": ruleset_version,
        }
        normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def persist_trace(
        db: Session,
        birth_input: BirthInput,
        natal_result: NatalResult,
        user_id: int | None = None,
    ) -> str:
        if not natal_result.reference_version:
            raise ChartResultServiceError(
                code="invalid_chart_result",
                message="reference version is required",
                details={"field": "reference_version"},
            )
        if not natal_result.ruleset_version:
            raise ChartResultServiceError(
                code="invalid_chart_result",
                message="ruleset version is required",
                details={"field": "ruleset_version"},
            )

        result_payload = natal_result.model_dump()
        if not result_payload:
            raise ChartResultServiceError(
                code="invalid_chart_result",
                message="result payload is required",
                details={"field": "result_payload"},
            )

        repo = ChartResultRepository(db)
        input_hash = ChartResultService.compute_input_hash(
            birth_input,
            natal_result.reference_version,
            natal_result.ruleset_version,
        )
        chart_id = str(uuid.uuid4())

        repo.create(
            user_id=user_id,
            chart_id=chart_id,
            reference_version=natal_result.reference_version,
            ruleset_version=natal_result.ruleset_version,
            input_hash=input_hash,
            result_payload=result_payload,
        )
        return chart_id

    @staticmethod
    def get_audit_record(db: Session, chart_id: str) -> ChartResultAuditRecord:
        model = ChartResultRepository(db).get_by_chart_id(chart_id)
        if model is None:
            raise ChartResultServiceError(
                code="chart_result_not_found",
                message="chart result not found",
                details={"chart_id": chart_id},
            )
        return ChartResultAuditRecord(
            chart_id=model.chart_id,
            reference_version=model.reference_version,
            ruleset_version=model.ruleset_version,
            input_hash=model.input_hash,
            result=NatalResult.model_validate(model.result_payload),
            created_at=model.created_at,
        )

from typing import Any

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.request_id import resolve_request_id
from app.domain.astrology.natal_calculation import NatalCalculationError
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparationError
from app.infra.db.session import get_db_session
from app.services.chart_result_service import (
    ChartResultAuditRecord,
    ChartResultService,
    ChartResultServiceError,
)
from app.services.natal_calculation_service import NatalCalculationService
from app.services.natal_preparation_service import NatalPreparationService


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class BirthPrepareResponse(BaseModel):
    data: dict[str, Any]
    meta: ResponseMeta


class NatalCalculateRequest(BirthInput):
    reference_version: str | None = None


class NatalCalculateResponse(BaseModel):
    data: dict[str, object]
    meta: ResponseMeta


class ChartResultAuditResponse(BaseModel):
    data: ChartResultAuditRecord
    meta: ResponseMeta


router = APIRouter(prefix="/v1/astrology-engine", tags=["astrology-engine"])


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )


@router.post(
    "/natal/prepare",
    response_model=BirthPrepareResponse,
    responses={422: {"model": ErrorEnvelope}},
)
def prepare_natal(request: Request, payload: dict[str, Any]) -> Any:
    request_id = resolve_request_id(request)
    try:
        parsed_payload = BirthInput.model_validate(payload)
        prepared = NatalPreparationService.prepare(parsed_payload)
        return {
            "data": prepared.model_dump(),
            "meta": {"request_id": request_id},
        }
    except ValidationError as error:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_birth_input",
            message="birth input validation failed",
            details={"errors": error.errors()},
        )
    except BirthPreparationError as error:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.post(
    "/natal/calculate",
    response_model=NatalCalculateResponse,
    responses={404: {"model": ErrorEnvelope}, 422: {"model": ErrorEnvelope}},
)
def calculate_natal(
    request: Request,
    payload: dict[str, Any],
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        parsed_payload = NatalCalculateRequest.model_validate(payload)
        birth_input = BirthInput(
            birth_date=parsed_payload.birth_date,
            birth_time=parsed_payload.birth_time,
            birth_place=parsed_payload.birth_place,
            birth_timezone=parsed_payload.birth_timezone,
        )
        result = NatalCalculationService.calculate(
            db=db,
            birth_input=birth_input,
            reference_version=parsed_payload.reference_version,
        )
        chart_id = ChartResultService.persist_trace(
            db=db,
            birth_input=birth_input,
            natal_result=result,
        )
        db.commit()
        return {
            "data": {"chart_id": chart_id, "result": result.model_dump()},
            "meta": {"request_id": request_id},
        }
    except ValidationError as error:
        db.rollback()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_birth_input",
            message="birth input validation failed",
            details={"errors": error.errors()},
        )
    except BirthPreparationError as error:
        db.rollback()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except NatalCalculationError as error:
        db.rollback()
        status_code = 404 if error.code == "reference_version_not_found" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except ChartResultServiceError as error:
        db.rollback()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.get(
    "/results/{chart_id}",
    response_model=ChartResultAuditResponse,
    responses={404: {"model": ErrorEnvelope}},
)
def get_chart_result(
    request: Request,
    chart_id: str,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if current_user.role not in {"support", "ops"}:
        return _error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "support,ops", "actual_role": current_user.role},
        )
    try:
        audit_record = ChartResultService.get_audit_record(db, chart_id=chart_id)
        return {"data": audit_record.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ChartResultServiceError as error:
        return _error_response(
            status_code=404 if error.code == "chart_result_not_found" else 422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )

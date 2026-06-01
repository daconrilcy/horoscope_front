# Commentaire global: routeur public des lectures natales historiques et readonly.
"""Expose les lectures natales publiques encore autorisees sans generation legacy."""

from __future__ import annotations

import logging
from typing import Any, Literal, Mapping, Optional

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.exceptions import ApplicationError
from app.core.request_id import resolve_request_id
from app.infra.db.models.pdf_template import PdfTemplateModel, PdfTemplateStatus
from app.infra.db.session import get_db_session
from app.services.api_contracts.common import ErrorEnvelope
from app.services.api_contracts.public.natal_interpretation import (
    InterpretationMeta,
    NatalInterpretationListResponse,
    NatalInterpretationResponse,
    NatalPdfTemplateListResponse,
)
from app.services.llm_generation.natal.interpretation_service import NatalInterpretationService
from app.services.llm_generation.natal.public_interpretation import _raise_error

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/natal", tags=["natal-interpretation"])


@router.post(
    "/interpretation",
    status_code=410,
    response_model=None,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        410: {"model": ErrorEnvelope},
        501: {"model": ErrorEnvelope},
        502: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        504: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)
async def interpret_natal_chart(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """Refuse l'ancien endpoint generateur avant tout acces provider, entitlement ou DB metier."""
    _ = (current_user, db)
    request_id = resolve_request_id(request)
    body = await _deprecated_request_body(request)
    raise ApplicationError(
        code="natal_interpretation_endpoint_gone",
        message="POST /v1/natal/interpretation is readonly; use POST /v1/theme-natal/readings.",
        details={
            "state": "readonly",
            "replacement": "/v1/theme-natal/readings",
            "chart_request_locale": _deprecated_request_locale(body),
        },
        request_id=request_id,
    )


def _deprecated_request_locale(body: Mapping[str, Any] | None) -> str | None:
    """Extrait la locale informative sans valider l'ancien contrat generateur."""
    if not body:
        return None
    locale = body.get("locale")
    return locale if isinstance(locale, str) else None


async def _deprecated_request_body(request: Request) -> Mapping[str, Any] | None:
    """Lit le JSON obsolete uniquement pour enrichir le message d'arret."""
    try:
        payload = await request.json()
    except Exception:
        return None
    return payload if isinstance(payload, Mapping) else None


@router.get(
    "/pdf-templates",
    response_model=NatalPdfTemplateListResponse,
    responses={
        401: {"model": ErrorEnvelope},
    },
)
async def list_natal_pdf_templates(
    request: Request,
    locale: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        stmt = select(PdfTemplateModel).where(PdfTemplateModel.status == PdfTemplateStatus.ACTIVE)
        if locale:
            stmt = stmt.where(PdfTemplateModel.locale == locale)
        stmt = stmt.order_by(PdfTemplateModel.is_default.desc(), PdfTemplateModel.key.asc())
        templates = db.execute(stmt).scalars().all()
        logger.info(
            "Listed active natal PDF templates user_id=%s locale=%s count=%s",
            current_user.id,
            locale,
            len(templates),
        )
        return {
            "items": [
                {
                    "key": item.key,
                    "name": item.name,
                    "description": item.description,
                    "locale": item.locale,
                    "is_default": item.is_default,
                }
                for item in templates
            ]
        }
    except Exception as e:
        logger.exception("Error listing natal PDF templates request_id=%s error=%s", request_id, e)
        return _raise_error(500, "internal_error", "Failed to list PDF templates", request_id)


@router.get(
    "/interpretations",
    response_model=NatalInterpretationListResponse,
    responses={
        401: {"model": ErrorEnvelope},
    },
)
async def list_natal_interpretations(
    request: Request,
    chart_id: Optional[str] = None,
    level: Optional[Literal["short", "complete"]] = None,
    persona_id: Optional[str] = None,
    module: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    from time import monotonic

    from app.infra.observability.metrics import observe_duration

    start_time = monotonic()
    try:
        items, total = NatalInterpretationService.list_interpretations(
            db=db,
            user_id=current_user.id,
            chart_id=chart_id,
            level=level,
            persona_id=persona_id,
            module=module,
            limit=limit,
            offset=offset,
        )

        observe_duration("natal_interpretations_list_latency", (monotonic() - start_time) * 1000)
        logger.info(
            "Listed natal interpretations user_id=%s chart_id=%s count=%s total=%s",
            current_user.id,
            chart_id,
            len(items),
            total,
        )

        return {
            "items": [
                {
                    "id": item.id,
                    "chart_id": item.chart_id,
                    "level": item.level.value,
                    "persona_id": str(item.persona_id) if item.persona_id else None,
                    "persona_name": item.persona_name,
                    "module": (
                        item.use_case
                        if item.use_case.startswith("natal_")
                        and item.use_case
                        not in {"natal_interpretation", "natal_interpretation_short"}
                        else None
                    ),
                    "created_at": item.created_at,
                    "use_case": item.use_case,
                    "prompt_version_id": str(item.prompt_version_id)
                    if item.prompt_version_id
                    else None,
                    "was_fallback": item.was_fallback,
                }
                for item in items
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.exception(f"Error listing interpretations: {e}")
        return _raise_error(500, "internal_error", "Failed to list interpretations", request_id)


@router.get(
    "/interpretations/{interpretation_id}",
    response_model=NatalInterpretationResponse,
    responses={
        401: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
    },
)
async def get_natal_interpretation(
    request: Request,
    interpretation_id: int,
    locale: str = "fr-FR",
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    from time import monotonic

    from app.infra.observability.metrics import observe_duration

    start_time = monotonic()

    item = NatalInterpretationService.get_interpretation_by_id(
        db=db,
        user_id=current_user.id,
        interpretation_id=interpretation_id,
    )
    if not item:
        return _raise_error(
            404, "interpretation_not_found", "Interpretation not found or access denied", request_id
        )

    from app.infra.db.models.user_natal_interpretation import InterpretationLevel

    meta = InterpretationMeta(
        level="short" if item.level == InterpretationLevel.SHORT else "complete",
        use_case=item.use_case,
        persona_id=str(item.persona_id) if item.persona_id else None,
        persona_name=item.persona_name,
        prompt_version_id=str(item.prompt_version_id) if item.prompt_version_id else None,
        schema_version="unknown",
        validation_status="valid",
        was_fallback=item.was_fallback,
        request_id=request_id,
        cached=True,
        persisted_at=item.created_at,
    )

    result = NatalInterpretationService.format_interpretation_response(item, meta, locale)
    observe_duration("natal_interpretation_get_latency", (monotonic() - start_time) * 1000)
    logger.info(
        "Fetched natal interpretation user_id=%s id=%s chart_id=%s",
        current_user.id,
        interpretation_id,
        item.chart_id,
    )
    return result


@router.delete(
    "/interpretations/{interpretation_id}",
    status_code=204,
    response_class=Response,
    response_model=None,
)
async def delete_natal_interpretation(
    request: Request,
    interpretation_id: int,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    from time import monotonic

    from app.infra.observability.metrics import observe_duration

    start_time = monotonic()

    success = NatalInterpretationService.delete_interpretation(
        db=db,
        user_id=current_user.id,
        interpretation_id=interpretation_id,
        request_id=request_id,
        actor_role=current_user.role,
    )
    if not success:
        logger.warning(
            "Failed to delete interpretation user_id=%s id=%s (not found or denied)",
            current_user.id,
            interpretation_id,
        )
        return _raise_error(
            404, "interpretation_not_found", "Interpretation not found or access denied", request_id
        )

    observe_duration("natal_interpretation_delete_latency", (monotonic() - start_time) * 1000)
    logger.info(
        "Deleted natal interpretation user_id=%s id=%s request_id=%s",
        current_user.id,
        interpretation_id,
        request_id,
    )
    return Response(status_code=204)


@router.get(
    "/interpretations/{interpretation_id}/pdf",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "The generated PDF file",
        },
        401: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
    },
)
async def download_natal_interpretation_pdf(
    request: Request,
    interpretation_id: int,
    template_key: Optional[str] = None,
    locale: str = "fr-FR",
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    from time import monotonic

    from app.infra.observability.metrics import observe_duration

    start_time = monotonic()

    item = NatalInterpretationService.get_interpretation_by_id(
        db=db,
        user_id=current_user.id,
        interpretation_id=interpretation_id,
    )
    if not item:
        return _raise_error(
            404, "interpretation_not_found", "Interpretation not found or access denied", request_id
        )

    try:
        from app.services.natal.pdf_export_service import NatalPdfExportService

        pdf_bytes = NatalPdfExportService.generate_pdf(
            db=db,
            interpretation=item,
            template_key=template_key,
            locale=locale,
        )

        filename = f"natal-{item.chart_id}-{item.created_at.strftime('%Y%m%d')}.pdf"

        observe_duration("natal_pdf_export_latency", (monotonic() - start_time) * 1000)
        logger.info(
            "Exported natal PDF user_id=%s id=%s chart_id=%s template=%s size=%s",
            current_user.id,
            interpretation_id,
            item.chart_id,
            template_key,
            len(pdf_bytes),
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.exception(f"Error generating PDF: {e}")
        return _raise_error(500, "pdf_generation_failed", "Failed to generate PDF", request_id)

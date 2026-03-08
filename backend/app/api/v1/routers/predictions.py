from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.config import settings
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
from app.infra.db.repositories.prediction_reference_repository import PredictionReferenceRepository
from app.infra.db.session import get_db_session
from app.prediction.context_loader import PredictionContextLoader
from app.prediction.persistence_service import PredictionPersistenceService
from app.services.daily_prediction_service import (
    ComputeMode,
    DailyPredictionService,
    DailyPredictionServiceError,
)


class DailyPredictionMeta(BaseModel):
    date_local: str
    timezone: str
    computed_at: str
    reference_version: str
    ruleset_version: str
    was_reused: bool
    house_system_effective: str | None


class DailyPredictionCategory(BaseModel):
    code: str
    note_20: float
    raw_score: float
    power: float
    volatility: float
    rank: int
    summary: str | None


class DailyPredictionTurningPoint(BaseModel):
    occurred_at_local: str
    severity: str
    summary: str | None
    drivers: list[dict[str, Any]]


class DailyPredictionTimeBlock(BaseModel):
    start_local: str
    end_local: str
    tone_code: str
    dominant_categories: list[str]
    summary: str | None
    turning_point: bool


class DailyPredictionSummary(BaseModel):
    overall_tone: str | None
    overall_summary: str | None
    top_categories: list[str]
    bottom_categories: list[str]
    best_window: dict[str, Any] | None
    main_turning_point: dict[str, Any] | None


class DailyPredictionResponse(BaseModel):
    meta: DailyPredictionMeta
    summary: DailyPredictionSummary
    categories: list[DailyPredictionCategory]
    timeline: list[DailyPredictionTimeBlock]
    turning_points: list[DailyPredictionTurningPoint]


router = APIRouter(prefix="/v1/predictions", tags=["predictions"])


def get_daily_prediction_service() -> DailyPredictionService:
    return DailyPredictionService(
        context_loader=PredictionContextLoader(),
        persistence_service=PredictionPersistenceService(),
    )


@router.get("/daily", response_model=DailyPredictionResponse)
def get_daily_prediction(
    date: str | None = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
    service: DailyPredictionService = Depends(get_daily_prediction_service),
) -> Any:
    parsed_date = None
    if date:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid date value. Use a real calendar date in YYYY-MM-DD.",
            )

    try:
        result = service.get_or_compute(
            user_id=current_user.id,
            db=db,
            date_local=parsed_date,
            mode=ComputeMode.compute_if_missing,
            ruleset_version=settings.ruleset_version,
        )
    except DailyPredictionServiceError as e:
        if e.code == "natal_missing":
            raise HTTPException(status_code=404, detail={"code": e.code, "message": e.message})
        raise HTTPException(status_code=422, detail={"code": e.code, "message": e.message})

    if result is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    repo = DailyPredictionRepository(db)
    full_run = repo.get_full_run(result.run.id)
    if not full_run:
        raise HTTPException(status_code=500, detail="Failed to load full prediction run")

    # Mappings
    ref_repo = PredictionReferenceRepository(db)
    categories_data = ref_repo.get_categories(result.run.reference_version_id)
    cat_id_to_code = {c.id: c.code for c in categories_data}

    # Timeline and turning points
    categories = sorted(
        [
            DailyPredictionCategory(
                code=cat_id_to_code.get(s["category_id"], "unknown"),
                note_20=float(s["note_20"] or 0),
                raw_score=float(s["raw_score"] or 0),
                power=float(s["power"] or 0),
                volatility=float(s["volatility"] or 0),
                rank=int(s["rank"] or 0),
                summary=s["summary"],
            )
            for s in full_run.get("category_scores", [])
        ],
        key=lambda c: c.rank,
    )

    turning_points = [
        DailyPredictionTurningPoint(
            occurred_at_local=tp["occurred_at_local"],
            severity=str(tp["severity"]),
            summary=tp["summary"],
            drivers=_load_json_list(
                tp.get("driver_json"),
                field_name="turning_points.driver_json",
            ),
        )
        for tp in full_run.get("turning_points", [])
    ]
    turning_point_times = [
        _parse_iso_datetime(tp.occurred_at_local)
        for tp in turning_points
        if tp.occurred_at_local is not None
    ]

    timeline = sorted(
        [
            DailyPredictionTimeBlock(
                start_local=b["start_at_local"],
                end_local=b["end_at_local"],
                tone_code=b["tone_code"] or "neutral",
                dominant_categories=_load_json_list(
                    b.get("dominant_categories_json"),
                    field_name="time_blocks.dominant_categories_json",
                ),
                summary=b["summary"],
                turning_point=_time_block_contains_turning_point(
                    b["start_at_local"],
                    b["end_at_local"],
                    turning_point_times,
                ),
            )
            for b in full_run.get("time_blocks", [])
        ],
        key=lambda b: _parse_iso_datetime(b.start_local),
    )

    # Build summary
    summary = _build_summary(result, full_run, cat_id_to_code)
    reference_version = settings.active_reference_version
    if result.run.reference_version_id is not None:
        version_model = db.get(ReferenceVersionModel, result.run.reference_version_id)
        if version_model is not None:
            reference_version = version_model.version

    house_system_effective = full_run.get("house_system_effective")
    if house_system_effective is None and result.engine_output is not None:
        house_system_effective = result.engine_output.effective_context.house_system_effective

    return DailyPredictionResponse(
        meta=DailyPredictionMeta(
            date_local=result.run.local_date.isoformat(),
            timezone=result.run.timezone,
            computed_at=result.run.computed_at.isoformat(),
            reference_version=reference_version,
            ruleset_version=settings.ruleset_version,
            was_reused=result.was_reused,
            house_system_effective=house_system_effective,
        ),
        summary=summary,
        categories=categories,
        timeline=timeline,
        turning_points=turning_points,
    )


def _build_summary(
    result, full_run: dict, cat_id_to_code: dict[int, str]
) -> DailyPredictionSummary:
    editorial = None
    if result.engine_output is not None:
        editorial = getattr(result.engine_output, "editorial", None)

    scores = sorted(full_run.get("category_scores", []), key=lambda s: s["rank"] or 99)
    top_categories = [cat_id_to_code.get(s["category_id"], "unknown") for s in scores[:3]]
    top_codes = set(top_categories)
    bottom_categories = [
        cat_id_to_code.get(s["category_id"], "unknown")
        for s in reversed(scores)
        if cat_id_to_code.get(s["category_id"], "unknown") not in top_codes
    ][:2]

    best_window = None
    if editorial and editorial.best_window:
        best_window = {
            "start_local": editorial.best_window.start_local.isoformat(),
            "end_local": editorial.best_window.end_local.isoformat(),
            "dominant_category": editorial.best_window.dominant_category,
        }

    # main_turning_point from DB (max severity)
    tps = sorted(
        full_run.get("turning_points", []), key=lambda t: t.get("severity") or 0, reverse=True
    )
    main_turning_point = (
        {
            "occurred_at_local": tps[0]["occurred_at_local"],
            "severity": tps[0]["severity"],
            "summary": tps[0].get("summary"),
        }
        if tps
        else None
    )

    return DailyPredictionSummary(
        overall_tone=full_run.get("overall_tone"),
        overall_summary=full_run.get("overall_summary"),
        top_categories=top_categories,
        bottom_categories=bottom_categories,
        best_window=best_window,
        main_turning_point=main_turning_point,
    )


def _load_json_list(raw_value: str | None, *, field_name: str) -> list[Any]:
    if not raw_value:
        return []
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "prediction_payload_invalid",
                "message": f"Malformed JSON payload for {field_name}",
            },
        ) from exc
    if isinstance(parsed, list):
        return parsed
    raise HTTPException(
        status_code=500,
        detail={
            "code": "prediction_payload_invalid",
            "message": f"Expected a JSON list for {field_name}",
        },
    )


def _parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _time_block_contains_turning_point(
    start_local: str,
    end_local: str,
    turning_point_times: list[datetime],
) -> bool:
    start_dt = _parse_iso_datetime(start_local)
    end_dt = _parse_iso_datetime(end_local)
    return any(
        start_dt <= turning_point_time <= end_dt for turning_point_time in turning_point_times
    )

from __future__ import annotations

import json
from datetime import date, datetime
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
    is_provisional_calibration: bool | None
    calibration_label: str | None


class DailyPredictionCategory(BaseModel):
    code: str
    note_20: float
    raw_score: float
    power: float
    volatility: float
    rank: int
    is_provisional: bool | None = None
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


class DailyPredictionDecisionWindow(BaseModel):
    start_local: str
    end_local: str
    window_type: str  # "favorable" | "prudence" | "pivot"
    score: float
    confidence: float
    dominant_categories: list[str]


class DailyPredictionSummary(BaseModel):
    overall_tone: str | None
    overall_summary: str | None
    calibration_note: str | None = None
    top_categories: list[str]
    bottom_categories: list[str]
    best_window: dict[str, Any] | None
    main_turning_point: dict[str, Any] | None
    low_score_variance: bool = False


class DailyPredictionResponse(BaseModel):
    meta: DailyPredictionMeta
    summary: DailyPredictionSummary
    categories: list[DailyPredictionCategory]
    timeline: list[DailyPredictionTimeBlock]
    turning_points: list[DailyPredictionTurningPoint]
    decision_windows: list[DailyPredictionDecisionWindow] | None = None


class DailyHistoryItem(BaseModel):
    date_local: str
    overall_tone: str | None
    categories: dict[str, float]
    pivot_count: int
    computed_at: str
    was_recomputed: bool | None = None


class DailyHistoryResponse(BaseModel):
    items: list[DailyHistoryItem]
    total: int


class DailyPredictionDebugCategory(BaseModel):
    code: str
    note_20: float
    raw_score: float
    power: float
    volatility: float
    rank: int
    is_provisional: bool | None = None
    contributors: list[dict[str, Any]]


class DailyPredictionDebugTurningPoint(BaseModel):
    occurred_at_local: str
    severity: float
    summary: str | None
    drivers: list[dict[str, Any]]


class DailyPredictionDebugResponse(BaseModel):
    meta: DailyPredictionMeta
    input_hash: str | None
    reference_version_id: int
    ruleset_id: int
    is_provisional_calibration: bool | None
    categories: list[DailyPredictionDebugCategory]
    turning_points: list[DailyPredictionDebugTurningPoint]


router = APIRouter(prefix="/v1/predictions", tags=["predictions"])


def get_daily_prediction_service() -> DailyPredictionService:
    return DailyPredictionService(
        context_loader=PredictionContextLoader(),
        persistence_service=PredictionPersistenceService(),
    )


def _raise_daily_prediction_service_error(
    error: DailyPredictionServiceError,
    *,
    not_found_codes: set[str] | None = None,
) -> None:
    if error.code in ("compute_failed", "timeout"):
        raise HTTPException(
            status_code=503,
            detail={
                "code": error.code,
                "message": (
                    "Service temporairement indisponible. "
                    "Veuillez réessayer dans quelques minutes."
                ),
            },
        )

    status_code = 404 if error.code in (not_found_codes or set()) else 422
    raise HTTPException(
        status_code=status_code,
        detail={"code": error.code, "message": error.message},
    )


@router.get("/daily/debug", response_model=DailyPredictionDebugResponse)
def debug_daily_prediction(
    target_user_id: int = Query(...),
    date: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
    service: DailyPredictionService = Depends(get_daily_prediction_service),
) -> DailyPredictionDebugResponse:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail={"code": "forbidden", "message": "Admin only"},
        )

    parsed_date = None
    if date:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid date format. Use YYYY-MM-DD.",
            )

    try:
        result = service.get_or_compute(
            user_id=target_user_id,
            db=db,
            date_local=parsed_date,
            mode=ComputeMode.read_only,
            ruleset_version=settings.ruleset_version,
        )
    except DailyPredictionServiceError as error:
        _raise_daily_prediction_service_error(
            error,
            not_found_codes={"natal_missing", "profile_missing"},
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": "Aucun run trouvé pour ce jour"},
        )

    repo = DailyPredictionRepository(db)
    full_run = repo.get_full_run(result.run.id)
    if not full_run:
        raise HTTPException(status_code=500, detail="Failed to load full prediction run")

    # Mappings
    ref_repo = PredictionReferenceRepository(db)
    categories_data = ref_repo.get_categories(result.run.reference_version_id)
    cat_id_to_code = {c.id: c.code for c in categories_data}

    debug_categories = [
        DailyPredictionDebugCategory(
            code=cat_id_to_code.get(s["category_id"], "unknown"),
            note_20=float(s["note_20"] or 0),
            raw_score=float(s["raw_score"] or 0),
            power=float(s["power"] or 0),
            volatility=float(s["volatility"] or 0),
            rank=int(s["rank"] or 0),
            is_provisional=s.get("is_provisional"),
            contributors=_load_json_list(
                s.get("contributors_json"), field_name="category_scores.contributors_json"
            ),
        )
        for s in full_run.get("category_scores", [])
    ]

    debug_turning_points = [
        DailyPredictionDebugTurningPoint(
            occurred_at_local=tp["occurred_at_local"],
            severity=float(tp["severity"] or 0),
            summary=tp["summary"],
            drivers=_load_json_list(tp.get("driver_json"), field_name="turning_points.driver_json"),
        )
        for tp in full_run.get("turning_points", [])
    ]

    # Resolve reference version string
    reference_version = settings.active_reference_version
    if result.run.reference_version_id is not None:
        version_model = db.get(ReferenceVersionModel, result.run.reference_version_id)
        if version_model is not None:
            reference_version = version_model.version

    house_system_effective = full_run.get("house_system_effective")
    if house_system_effective is None and result.engine_output is not None:
        house_system_effective = result.engine_output.effective_context.house_system_effective

    meta = DailyPredictionMeta(
        date_local=result.run.local_date.isoformat(),
        timezone=result.run.timezone,
        computed_at=result.run.computed_at.isoformat(),
        reference_version=reference_version,
        ruleset_version=settings.ruleset_version,
        was_reused=result.was_reused,
        house_system_effective=house_system_effective,
        is_provisional_calibration=result.run.is_provisional_calibration,
        calibration_label=result.run.calibration_label,
    )

    return DailyPredictionDebugResponse(
        meta=meta,
        input_hash=full_run.get("input_hash"),
        reference_version_id=result.run.reference_version_id,
        ruleset_id=full_run["ruleset_id"],
        is_provisional_calibration=full_run.get("is_provisional_calibration"),
        categories=debug_categories,
        turning_points=debug_turning_points,
    )


@router.get("/daily/history", response_model=DailyHistoryResponse)
def get_daily_history(
    from_date: date = Query(...),
    to_date: date = Query(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> DailyHistoryResponse:
    if from_date > to_date:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_date_range",
                "message": "from_date must be before or equal to to_date",
            },
        )

    delta = (to_date - from_date).days
    if delta > 90:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "range_too_large",
                "message": f"Requested range ({delta} days) exceeds the maximum of 90 days",
            },
        )

    repo = DailyPredictionRepository(db)
    runs = repo.get_user_history(current_user.id, from_date, to_date)

    if not runs:
        return DailyHistoryResponse(items=[], total=0)

    # Resolve category mapping for the reference versions found
    ref_repo = PredictionReferenceRepository(db)
    # Optimization: cache mappings per reference_version_id
    mappings: dict[int, dict[int, str]] = {}

    items = []
    for run in sorted(runs, key=lambda item: item.local_date, reverse=True):
        ref_id = run.reference_version_id
        if ref_id not in mappings:
            categories_data = ref_repo.get_categories(ref_id)
            mappings[ref_id] = {c.id: c.code for c in categories_data}

        cat_map = mappings[ref_id]
        categories_dict = {
            cat_map.get(score.category_id, "unknown"): float(score.note_20 or 0)
            for score in run.category_scores
        }

        items.append(
            DailyHistoryItem(
                date_local=run.local_date.isoformat(),
                overall_tone=run.overall_tone,
                categories=categories_dict,
                pivot_count=len(run.turning_points),
                computed_at=run.computed_at.isoformat(),
                was_recomputed=None,
            )
        )

    return DailyHistoryResponse(items=items, total=len(items))


@router.get("/daily", response_model=DailyPredictionResponse)
def get_daily_prediction(
    target_date: str | None = Query(None, alias="date", pattern=r"^\d{4}-\d{2}-\d{2}$"),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
    service: DailyPredictionService = Depends(get_daily_prediction_service),
) -> Any:
    parsed_date = None
    if target_date:
        try:
            parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
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
    except DailyPredictionServiceError as error:
        _raise_daily_prediction_service_error(error, not_found_codes={"natal_missing"})

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
                is_provisional=s.get("is_provisional"),
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

    # AC5: expose decision_windows from engine output when available (additive, non-breaking)
    decision_windows = None
    if result.engine_output is not None:
        raw_dws = getattr(result.engine_output, "decision_windows", None) or []
        if raw_dws:
            decision_windows = [
                DailyPredictionDecisionWindow(
                    start_local=dw.start_local.isoformat(),
                    end_local=dw.end_local.isoformat(),
                    window_type=dw.window_type,
                    score=dw.score,
                    confidence=dw.confidence,
                    dominant_categories=list(dw.dominant_categories),
                )
                for dw in raw_dws
            ]

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
            is_provisional_calibration=result.run.is_provisional_calibration,
            calibration_label=result.run.calibration_label,
        ),
        summary=summary,
        categories=categories,
        timeline=timeline,
        turning_points=turning_points,
        decision_windows=decision_windows,
    )


def _build_summary(
    result, full_run: dict, cat_id_to_code: dict[int, str]
) -> DailyPredictionSummary:
    editorial = None
    if result.engine_output is not None:
        editorial = getattr(result.engine_output, "editorial", None)

    scores = sorted(full_run.get("category_scores", []), key=lambda s: s["rank"] or 99)
    top_categories = [cat_id_to_code.get(s["category_id"], "unknown") for s in scores[:3]]
    bottom_scores = sorted(
        full_run.get("category_scores", []),
        key=lambda score: (
            float(score.get("note_20") or 0),
            int(score.get("rank") or 99),
        ),
    )
    bottom_categories = [
        cat_id_to_code.get(score["category_id"], "unknown") for score in bottom_scores
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

    # AC6 - Disclaimer for provisional calibration
    calibration_note = None
    low_score_variance = False
    if full_run.get("is_provisional_calibration"):
        calibration_note = (
            "Les scores sont calculés sans données historiques : ils reflètent des tendances"
            " relatives à la journée, pas des statistiques absolues."
        )
        top3_notes = [float(s.get("note_20") or 0) for s in scores[:3]]
        if top3_notes:
            spread = max(top3_notes) - min(top3_notes)
            if spread < 3:
                low_score_variance = True

    return DailyPredictionSummary(
        overall_tone=full_run.get("overall_tone"),
        overall_summary=full_run.get("overall_summary"),
        calibration_note=calibration_note,
        top_categories=top_categories,
        bottom_categories=bottom_categories,
        best_window=best_window,
        main_turning_point=main_turning_point,
        low_score_variance=low_score_variance,
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

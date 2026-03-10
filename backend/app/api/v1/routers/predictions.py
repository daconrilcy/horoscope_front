from __future__ import annotations

import json
from datetime import date, datetime
from types import SimpleNamespace
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
from app.prediction.decision_window_builder import DecisionWindowBuilder
from app.prediction.editorial_template_engine import EditorialTemplateEngine
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
MAJOR_ASPECT_NOTE_THRESHOLD = 7.0


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
    category_note_by_code = {category.code: category.note_20 for category in categories}
    decision_windows = _build_public_decision_windows(
        result,
        full_run,
        cat_id_to_code,
        category_note_by_code,
    )
    turning_points = _build_public_turning_points(
        decision_windows or [],
        full_run,
    )
    turning_point_times = [
        _parse_iso_datetime(tp.occurred_at_local)
        for tp in turning_points
        if tp.occurred_at_local is not None
    ]
    timeline = _build_public_timeline(
        full_run,
        category_note_by_code,
        turning_point_times,
    )

    # Build summary
    summary = _build_summary(
        result,
        full_run,
        cat_id_to_code,
        decision_windows=decision_windows,
        turning_points=turning_points,
    )
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
    result,
    full_run: dict,
    cat_id_to_code: dict[int, str],
    *,
    decision_windows: list[DailyPredictionDecisionWindow] | None,
    turning_points: list[DailyPredictionTurningPoint],
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

    if best_window is None and decision_windows:
        candidate = max(
            decision_windows,
            key=lambda window: (window.score, window.confidence),
        )
        if candidate.dominant_categories:
            best_window = {
                "start_local": candidate.start_local,
                "end_local": candidate.end_local,
                "dominant_category": candidate.dominant_categories[0],
            }

    tps = sorted(
        turning_points,
        key=lambda turning_point: float(turning_point.severity or 0),
        reverse=True,
    )
    main_turning_point = (
        {
            "occurred_at_local": tps[0].occurred_at_local,
            "severity": float(tps[0].severity),
            "summary": tps[0].summary,
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


def _build_decision_windows(
    result: Any,
    full_run: dict[str, Any],
    cat_id_to_code: dict[int, str],
) -> list[DailyPredictionDecisionWindow] | None:
    if result.engine_output is not None:
        raw_dws = getattr(result.engine_output, "decision_windows", None) or []
        if raw_dws:
            return [
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

    raw_blocks = full_run.get("time_blocks", [])
    if not raw_blocks:
        return None

    category_scores = {
        cat_id_to_code.get(score["category_id"], "unknown"): {
            "note_20": float(score.get("note_20") or 0),
            "volatility": float(score.get("volatility") or 0),
        }
        for score in full_run.get("category_scores", [])
        if score.get("category_id") in cat_id_to_code
    }

    blocks = [
        SimpleNamespace(
            start_local=_parse_iso_datetime(block["start_at_local"]),
            end_local=_parse_iso_datetime(block["end_at_local"]),
            tone_code=block.get("tone_code") or "neutral",
            dominant_categories=_load_json_list(
                block.get("dominant_categories_json"),
                field_name="time_blocks.dominant_categories_json",
            ),
        )
        for block in raw_blocks
        if block.get("start_at_local") and block.get("end_at_local")
    ]
    if not blocks:
        return None

    turning_points = [
        SimpleNamespace(local_time=_parse_iso_datetime(tp["occurred_at_local"]))
        for tp in full_run.get("turning_points", [])
        if tp.get("occurred_at_local")
    ]

    rebuilt = DecisionWindowBuilder().build(blocks, turning_points, category_scores)
    if not rebuilt:
        return None

    return [
        DailyPredictionDecisionWindow(
            start_local=window.start_local.isoformat(),
            end_local=window.end_local.isoformat(),
            window_type=window.window_type,
            score=window.score,
            confidence=window.confidence,
            dominant_categories=list(window.dominant_categories),
        )
        for window in rebuilt
    ]


def _build_public_decision_windows(
    result: Any,
    full_run: dict[str, Any],
    cat_id_to_code: dict[int, str],
    category_note_by_code: dict[str, float],
) -> list[DailyPredictionDecisionWindow] | None:
    raw_windows = _build_decision_windows(result, full_run, cat_id_to_code) or []
    if not raw_windows:
        return None

    normalized: list[DailyPredictionDecisionWindow] = []
    for window in sorted(raw_windows, key=lambda item: _parse_iso_datetime(item.start_local)):
        dominant_categories = _filter_major_categories(
            window.dominant_categories,
            category_note_by_code,
        )
        if not dominant_categories:
            continue

        if normalized:
            previous = normalized[-1]
            if (
                previous.end_local == window.start_local
                and previous.window_type == window.window_type
                and previous.dominant_categories == dominant_categories
            ):
                normalized[-1] = DailyPredictionDecisionWindow(
                    start_local=previous.start_local,
                    end_local=window.end_local,
                    window_type=previous.window_type,
                    score=max(previous.score, window.score),
                    confidence=max(previous.confidence, window.confidence),
                    dominant_categories=previous.dominant_categories,
                )
                continue

        normalized.append(
            DailyPredictionDecisionWindow(
                start_local=window.start_local,
                end_local=window.end_local,
                window_type=window.window_type,
                score=window.score,
                confidence=window.confidence,
                dominant_categories=dominant_categories,
            )
        )

    return normalized or None


def _build_public_turning_points(
    decision_windows: list[DailyPredictionDecisionWindow],
    full_run: dict[str, Any],
) -> list[DailyPredictionTurningPoint]:
    if not decision_windows:
        return [
            DailyPredictionTurningPoint(
                occurred_at_local=turning_point["occurred_at_local"],
                severity=str(turning_point["severity"]),
                summary=turning_point.get("summary"),
                drivers=_load_json_list(
                    turning_point.get("driver_json"),
                    field_name="turning_points.driver_json",
                ),
            )
            for turning_point in full_run.get("turning_points", [])
        ]

    sorted_windows = sorted(
        decision_windows,
        key=lambda window: _parse_iso_datetime(window.start_local),
    )
    boundaries = sorted(
        {
            window.start_local
            for window in sorted_windows
        }
        | {
            window.end_local
            for window in sorted_windows
        },
        key=_parse_iso_datetime,
    )

    raw_turning_points = full_run.get("turning_points", [])
    public_turning_points: list[DailyPredictionTurningPoint] = []
    for boundary in boundaries:
        previous_categories = _get_active_categories_at_boundary(
            sorted_windows,
            boundary,
            include_end=True,
            include_start=False,
        )
        next_categories = _get_active_categories_at_boundary(
            sorted_windows,
            boundary,
            include_end=False,
            include_start=True,
        )

        if previous_categories == next_categories:
            continue

        drivers = []
        for turning_point in raw_turning_points:
            if turning_point.get("occurred_at_local") != boundary:
                continue
            drivers.extend(
                _load_json_list(
                    turning_point.get("driver_json"),
                    field_name="turning_points.driver_json",
                )
            )

        public_turning_points.append(
            DailyPredictionTurningPoint(
                occurred_at_local=boundary,
                severity="1.0" if previous_categories and next_categories else "0.8",
                summary=_build_turning_point_summary(
                    boundary,
                    previous_categories,
                    next_categories,
                ),
                drivers=drivers,
            )
        )

    return public_turning_points


def _build_public_timeline(
    full_run: dict[str, Any],
    category_note_by_code: dict[str, float],
    turning_point_times: list[datetime],
) -> list[DailyPredictionTimeBlock]:
    blocks: list[DailyPredictionTimeBlock] = []
    for raw_block in full_run.get("time_blocks", []):
        dominant_categories = _filter_major_categories(
            _load_json_list(
                raw_block.get("dominant_categories_json"),
                field_name="time_blocks.dominant_categories_json",
            ),
            category_note_by_code,
        )
        blocks.append(
            DailyPredictionTimeBlock(
                start_local=raw_block["start_at_local"],
                end_local=raw_block["end_at_local"],
                tone_code=raw_block.get("tone_code") or "neutral",
                dominant_categories=dominant_categories,
                summary=_build_timeline_summary(
                    raw_block["start_at_local"],
                    raw_block["end_at_local"],
                    dominant_categories,
                    raw_block.get("tone_code"),
                ),
                turning_point=_time_block_contains_turning_point(
                    raw_block["start_at_local"],
                    raw_block["end_at_local"],
                    turning_point_times,
                ),
            )
        )

    return sorted(blocks, key=lambda block: _parse_iso_datetime(block.start_local))


def _filter_major_categories(
    categories: list[str],
    category_note_by_code: dict[str, float],
) -> list[str]:
    unique_categories: list[str] = []
    for category in categories:
        if category in unique_categories:
            continue
        if float(category_note_by_code.get(category, 10)) <= MAJOR_ASPECT_NOTE_THRESHOLD:
            continue
        unique_categories.append(category)
    return unique_categories[:3]


def _get_active_categories_at_boundary(
    windows: list[DailyPredictionDecisionWindow],
    boundary: str,
    *,
    include_start: bool,
    include_end: bool,
) -> list[str]:
    boundary_dt = _parse_iso_datetime(boundary)
    for window in windows:
        start_dt = _parse_iso_datetime(window.start_local)
        end_dt = _parse_iso_datetime(window.end_local)
        after_start = boundary_dt > start_dt or (include_start and boundary_dt == start_dt)
        before_end = boundary_dt < end_dt or (include_end and boundary_dt == end_dt)
        if after_start and before_end:
            return list(window.dominant_categories)
    return []


def _format_time_label(iso_value: str) -> str:
    parsed = _parse_iso_datetime(iso_value)
    return parsed.strftime("%H:%M")


def _build_turning_point_summary(
    occurred_at_local: str,
    previous_categories: list[str],
    next_categories: list[str],
) -> str:
    time_label = _format_time_label(occurred_at_local)
    next_labels = _format_category_labels(next_categories)
    previous_labels = _format_category_labels(previous_categories)
    if not previous_categories and next_categories:
        return f"À {time_label}, des aspects majeurs émergent : {next_labels}."
    if previous_categories and not next_categories:
        return f"À {time_label}, les aspects majeurs s'estompent : {previous_labels}."
    return f"À {time_label}, un basculement critique : {next_labels}."


def _build_timeline_summary(
    start_local: str,
    end_local: str,
    dominant_categories: list[str],
    tone_code: str | None = None,
) -> str:
    start_label = _format_time_label(start_local)
    end_label = _format_time_label(end_local)
    if not dominant_categories:
        return f"Entre {start_label} et {end_label}, pas d'aspect majeur."
    tone_label = EditorialTemplateEngine.TONE_LABELS["fr"].get(tone_code or "neutral", "équilibrée")
    return (
        f"Entre {start_label} et {end_label}, tonalité {tone_label} — "
        f"{_format_category_labels(dominant_categories)}."
    )


def _format_category_labels(categories: list[str]) -> str:
    labels = EditorialTemplateEngine.CATEGORY_LABELS["fr"]
    return ", ".join(labels.get(category, category) for category in categories)


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


def _to_local_wall_time(value: datetime) -> datetime:
    return value.replace(tzinfo=None) if value.tzinfo is not None else value


def _time_block_contains_turning_point(
    start_local: str,
    end_local: str,
    turning_point_times: list[datetime],
) -> bool:
    start_dt = _parse_iso_datetime(start_local)
    end_dt = _parse_iso_datetime(end_local)

    def contains(turning_point_time: datetime) -> bool:
        block_is_aware = start_dt.tzinfo is not None and end_dt.tzinfo is not None
        turning_point_is_aware = turning_point_time.tzinfo is not None
        if block_is_aware == turning_point_is_aware:
            return start_dt <= turning_point_time < end_dt

        local_start = _to_local_wall_time(start_dt)
        local_end = _to_local_wall_time(end_dt)
        local_turning_point = _to_local_wall_time(turning_point_time)
        return local_start <= local_turning_point < local_end

    return any(contains(turning_point_time) for turning_point_time in turning_point_times)

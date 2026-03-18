from __future__ import annotations

import json
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

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
from app.prediction.persisted_snapshot import PersistedPredictionSnapshot
from app.prediction.persistence_service import PredictionPersistenceService
from app.prediction.public_projection import PublicPredictionAssembler
from app.services.daily_prediction_service import DailyPredictionService
from app.services.daily_prediction_types import (
    ComputeMode,
    DailyPredictionServiceError,
)

if TYPE_CHECKING:
    pass


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
    score_20: float | None = None
    intensity_20: float | None = None
    confidence_20: float | None = None
    rarity_percentile: float | None = None
    rank: int
    is_provisional: bool | None = None
    summary: str | None


class DailyPredictionPublicDomainScore(BaseModel):
    key: str
    label: str
    internal_codes: list[str]
    display_order: int
    score_10: float
    level: str  # e.g., "favorable", "neutre", "exigeante"
    rank: int
    note_20_internal: float
    signal_label: str | None = None


class DailyPredictionTurningPoint(BaseModel):
    occurred_at_local: str
    severity: float
    summary: str | None
    drivers: list[dict[str, Any]]
    impacted_categories: list[str] | None = None
    change_type: str | None = None
    previous_categories: list[str] | None = None
    next_categories: list[str] | None = None
    primary_driver: dict[str, Any] | None = None
    movement: dict[str, Any] | None = None
    category_deltas: list[dict[str, Any]] | None = None


class DailyPredictionTurningPointPublic(BaseModel):
    time: str
    title: str
    change_type: str
    affected_domains: list[str]
    what_changes: str
    do: str
    avoid: str


class DailyPredictionTimeBlock(BaseModel):
    start_local: str
    end_local: str
    tone_code: str
    dominant_categories: list[str]
    summary: str | None
    turning_point: bool


class DailyPredictionTimeWindow(BaseModel):
    time_range: str
    label: str
    regime: str
    top_domains: list[str]
    action_hint: str


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

    # Story 41.14: Relative nuance fields
    flat_day: bool = False
    relative_top_categories: list[str] | None = None
    relative_summary: str | None = None


class DailyPredictionMicroTrend(BaseModel):
    category_code: str
    z_score: float | None = None
    percentile: float
    rank: int
    wording: str


class DailyPredictionDayClimate(BaseModel):
    label: str
    tone: str
    intensity: float
    stability: float
    summary: str
    top_domains: list[str]
    watchout: str | None = None
    best_window_ref: str | None = None


class DailyPredictionResponse(BaseModel):
    meta: DailyPredictionMeta
    summary: DailyPredictionSummary
    day_climate: DailyPredictionDayClimate | None = None
    categories: list[DailyPredictionCategory]
    categories_internal: list[DailyPredictionCategory] | None = None
    domain_ranking: list[DailyPredictionPublicDomainScore] | None = None
    turning_point: DailyPredictionTurningPointPublic | None = None
    time_windows: list[DailyPredictionTimeWindow] | None = None
    timeline: list[DailyPredictionTimeBlock]
    turning_points: list[DailyPredictionTurningPoint]
    decision_windows: list[DailyPredictionDecisionWindow] | None = None

    # Story 41.14: Micro trends for flat days
    micro_trends: list[DailyPredictionMicroTrend] | None = None


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
    score_20: float | None = None
    intensity_20: float | None = None
    confidence_20: float | None = None
    rarity_percentile: float | None = None
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
                    "Service temporairement indisponible. Veuillez réessayer dans quelques minutes."
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
    # AC1 Compliance: get_full_run now returns PersistedPredictionSnapshot
    snapshot = repo.get_full_run(result.run.run_id)
    if not snapshot:
        raise HTTPException(status_code=500, detail="Failed to load full prediction run snapshot")

    # Mappings
    ref_repo = PredictionReferenceRepository(db)
    categories_data = ref_repo.get_categories(snapshot.reference_version_id)
    cat_id_to_code = {c.id: c.code for c in categories_data}

    debug_categories = [
        DailyPredictionDebugCategory(
            code=cat_id_to_code.get(s.category_id, "unknown"),
            note_20=float(s.note_20 or 0),
            raw_score=float(s.raw_score or 0),
            power=float(s.power or 0),
            volatility=float(s.volatility or 0),
            score_20=float(s.score_20) if s.score_20 is not None else None,
            intensity_20=float(s.intensity_20) if s.intensity_20 is not None else None,
            confidence_20=float(s.confidence_20) if s.confidence_20 is not None else None,
            rarity_percentile=(
                float(s.rarity_percentile) if s.rarity_percentile is not None else None
            ),
            rank=int(s.rank or 0),
            is_provisional=s.is_provisional,
            contributors=s.contributors,
        )
        for s in snapshot.category_scores
    ]

    debug_turning_points = [
        DailyPredictionDebugTurningPoint(
            occurred_at_local=tp.occurred_at_local.isoformat(),
            severity=float(tp.severity or 0),
            summary=tp.summary,
            drivers=tp.drivers,
        )
        for tp in snapshot.turning_points
    ]

    # Resolve reference version string
    reference_version = settings.active_reference_version
    version_model = db.get(ReferenceVersionModel, snapshot.reference_version_id)
    if version_model is not None:
        reference_version = version_model.version

    house_system_effective = snapshot.house_system_effective
    if house_system_effective is None and result.bundle is not None:
        house_system_effective = result.bundle.core.effective_context.house_system_effective

    meta = DailyPredictionMeta(
        date_local=snapshot.local_date.isoformat(),
        timezone=snapshot.timezone,
        computed_at=snapshot.computed_at.isoformat(),
        reference_version=reference_version,
        ruleset_version=settings.ruleset_version,
        was_reused=result.was_reused,
        house_system_effective=house_system_effective,
        is_provisional_calibration=snapshot.is_provisional_calibration,
        calibration_label=snapshot.calibration_label,
    )

    return DailyPredictionDebugResponse(
        meta=meta,
        input_hash=snapshot.input_hash,
        reference_version_id=snapshot.reference_version_id,
        ruleset_id=snapshot.ruleset_id,
        is_provisional_calibration=snapshot.is_provisional_calibration,
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

    snapshot = result.run
    if not isinstance(snapshot, PersistedPredictionSnapshot):
        reloaded_snapshot = DailyPredictionRepository(db).get_full_run(result.run.run_id)
        if reloaded_snapshot is None:
            raise HTTPException(status_code=404, detail="Prediction not found")
        snapshot = reloaded_snapshot

    # Mappings
    ref_repo = PredictionReferenceRepository(db)
    categories_data = ref_repo.get_categories(snapshot.reference_version_id)
    cat_id_to_code = {c.id: c.code for c in categories_data}

    # Resolve reference version string
    reference_version = settings.active_reference_version
    version_model = db.get(ReferenceVersionModel, snapshot.reference_version_id)
    if version_model is not None:
        reference_version = version_model.version

    # AC1/AC2/AC4 - Call Assembler with typed snapshot
    assembler = PublicPredictionAssembler()
    try:
        assembled = assembler.assemble(
            snapshot=snapshot,
            cat_id_to_code=cat_id_to_code,
            engine_output=result.bundle,
            was_reused=result.was_reused,
            reference_version=reference_version,
            ruleset_version=settings.ruleset_version,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "prediction_payload_invalid",
                "message": str(exc),
            },
        )

    return DailyPredictionResponse(**assembled)


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

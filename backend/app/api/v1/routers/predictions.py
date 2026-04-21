from __future__ import annotations

import logging
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
from app.prediction.persisted_snapshot import PersistedPredictionSnapshot
from app.prediction.persistence_service import PredictionPersistenceService
from app.prediction.public_projection import PublicPredictionAssembler
from app.services.daily_prediction_service import DailyPredictionService
from app.services.daily_prediction_types import (
    ComputeMode,
    DailyPredictionServiceError,
)
from app.services.horoscope_daily_entitlement_gate import (
    HoroscopeDailyAccessDeniedError,
    HoroscopeDailyEntitlementGate,
)

logger = logging.getLogger(__name__)


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
    v3_evidence_version: str | None = None
    payload_version: str = "v3"


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
    narrative: str | None = None


class DailyPredictionTimeBlock(BaseModel):
    start_local: str
    end_local: str
    tone_code: str
    dominant_categories: list[str]
    summary: str | None
    turning_point: bool


class DailyPredictionTimeWindow(BaseModel):
    period_key: str
    time_range: str
    label: str
    regime: str
    top_domains: list[str]
    action_hint: str
    astro_events: list[str] = []
    narrative: str | None = None


class DailyPredictionDailyAdvice(BaseModel):
    advice: str
    emphasis: str


class DailyPredictionBestWindow(BaseModel):
    time_range: str
    label: str
    why: str
    recommended_actions: list[str]
    is_pivot: bool = False


class DailyPredictionKeyMovement(BaseModel):
    planet: str
    event_type: str
    target: str | None = None
    orb_deg: float | None = None
    effect_label: str


class DailyPredictionActivatedHouse(BaseModel):
    house_number: int
    house_label: str
    domain_label: str


class DailyPredictionDominantAspect(BaseModel):
    aspect_type: str
    planet_a: str
    planet_b: str | None = None
    tonality: str
    effect_label: str


class DailyPredictionIngress(BaseModel):
    text: str
    time: str | None


class DailyPredictionAstroDailyEvents(BaseModel):
    ingresses: list[DailyPredictionIngress]
    aspects: list[str]
    planet_positions: list[str] | None = None
    returns: list[str] | None = None
    progressions: list[str] | None = None
    nodes: list[str] | None = None
    sky_aspects: list[str] | None = None
    fixed_stars: list[str] | None = None


class DailyPredictionAstroFoundation(BaseModel):
    headline: str
    key_movements: list[DailyPredictionKeyMovement]
    activated_houses: list[DailyPredictionActivatedHouse]
    dominant_aspects: list[DailyPredictionDominantAspect]
    interpretation_bridge: str


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
    daily_synthesis: str | None = None
    astro_events_intro: str | None = None
    daily_advice: DailyPredictionDailyAdvice | None = None
    has_llm_narrative: bool = False
    categories: list[DailyPredictionCategory]
    categories_internal: list[DailyPredictionCategory] | None = None
    domain_ranking: list[DailyPredictionPublicDomainScore] | None = None
    turning_point: DailyPredictionTurningPointPublic | None = None
    best_window: DailyPredictionBestWindow | None = None
    time_windows: list[DailyPredictionTimeWindow] | None = None
    astro_foundation: DailyPredictionAstroFoundation | None = None
    astro_daily_events: DailyPredictionAstroDailyEvents | None = None
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
async def get_daily_prediction(
    target_date: str | None = Query(None, alias="date", pattern=r"^\d{4}-\d{2}-\d{2}$"),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
    service: DailyPredictionService = Depends(get_daily_prediction_service),
) -> DailyPredictionResponse:
    parsed_date = None
    if target_date:
        try:
            parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid date value. Use a real calendar date in YYYY-MM-DD.",
            )

    # 1. Obtenir les prédictions
    try:
        # Resolve variant_code (Story 64.2)
        try:
            entitlement = HoroscopeDailyEntitlementGate.check_and_get_variant(
                db, user_id=current_user.id
            )
            variant_code = entitlement.variant_code
        except HoroscopeDailyAccessDeniedError as exc:
            raise HTTPException(
                status_code=403,
                detail={"code": exc.reason_code, "message": str(exc)},
            )

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

    # Commit the prediction to DB before the async LLM call so concurrent requests
    # hit the cache instead of recomputing. Without this, the `async def` handler's
    # `await assembler.assemble()` pause allows many requests to start simultaneously,
    # all seeing a cache miss.
    if not result.was_reused:
        db.commit()

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

    # Fetch user profile for Story 60.16
    from app.infra.db.models.user import UserModel

    user_model = db.get(UserModel, current_user.id)
    astrologer_profile_key = (
        getattr(user_model, "astrologer_profile", "standard") if user_model else "standard"
    )

    # Build prompt context if LLM narration is enabled
    prompt_context = None
    if settings.llm_narrator_enabled:
        from app.domain.llm.prompting.context import CommonContextBuilder

        try:
            prompt_context = CommonContextBuilder.build(
                user_id=current_user.id, use_case_key="horoscope_daily", period="daily", db=db
            )
        except Exception as e:
            logger.warning("failed to build prompt context for daily prediction: %s", str(e))

    # AC1/AC2/AC4 - Call Assembler with typed snapshot
    assembler = PublicPredictionAssembler()

    try:
        assembled = await assembler.assemble(
            snapshot=snapshot,
            cat_id_to_code=cat_id_to_code,
            db=db,
            engine_output=result.bundle,
            was_reused=result.was_reused,
            reference_version=reference_version,
            ruleset_version=settings.ruleset_version,
            astrologer_profile_key=astrologer_profile_key,
            lang=current_user.lang if hasattr(current_user, "lang") else "fr",
            prompt_context=prompt_context,
            variant_code=variant_code,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "prediction_payload_invalid",
                "message": str(exc),
            },
        )

    if settings.llm_narrator_enabled and not getattr(snapshot, "llm_narrative", None):
        llm_payload = _extract_llm_narrative_payload(assembled)
        if llm_payload is not None:
            repo = DailyPredictionRepository(db)
            try:
                repo.update_llm_narrative(snapshot.run_id, llm_payload)
                db.commit()
            except Exception:
                db.rollback()
                logger.warning(
                    "failed to persist daily prediction llm narrative run_id=%s",
                    snapshot.run_id,
                    exc_info=True,
                )

    return DailyPredictionResponse(**assembled)


def _extract_llm_narrative_payload(assembled: dict[str, Any]) -> dict[str, Any] | None:
    if not assembled.get("has_llm_narrative"):
        return None

    payload: dict[str, Any] = {}
    daily_synthesis = assembled.get("daily_synthesis")
    if isinstance(daily_synthesis, str) and daily_synthesis.strip():
        payload["daily_synthesis"] = daily_synthesis.strip()

    astro_events_intro = assembled.get("astro_events_intro")
    if isinstance(astro_events_intro, str) and astro_events_intro.strip():
        payload["astro_events_intro"] = astro_events_intro.strip()

    time_window_narratives = {}
    for window in assembled.get("time_windows") or []:
        if not isinstance(window, dict):
            continue
        period_key = window.get("period_key")
        narrative = window.get("narrative")
        if isinstance(period_key, str) and isinstance(narrative, str) and narrative.strip():
            time_window_narratives[period_key] = narrative.strip()
    if time_window_narratives:
        payload["time_window_narratives"] = time_window_narratives

    turning_point_narratives = []
    for turning_point in assembled.get("turning_points") or []:
        if not isinstance(turning_point, dict):
            continue
        narrative = turning_point.get("narrative")
        if isinstance(narrative, str) and narrative.strip():
            turning_point_narratives.append(narrative.strip())
    if turning_point_narratives:
        payload["turning_point_narratives"] = turning_point_narratives

    main_turning_point = assembled.get("turning_point")
    if isinstance(main_turning_point, dict):
        narrative = main_turning_point.get("narrative")
        if isinstance(narrative, str) and narrative.strip():
            payload["main_turning_point_narrative"] = narrative.strip()

    daily_advice = assembled.get("daily_advice")
    if isinstance(daily_advice, dict):
        advice = daily_advice.get("advice")
        emphasis = daily_advice.get("emphasis")
        if (isinstance(advice, str) and advice.strip()) or (
            isinstance(emphasis, str) and emphasis.strip()
        ):
            payload["daily_advice"] = {
                "advice": advice.strip() if isinstance(advice, str) else "",
                "emphasis": emphasis.strip() if isinstance(emphasis, str) else "",
            }

    return payload or None

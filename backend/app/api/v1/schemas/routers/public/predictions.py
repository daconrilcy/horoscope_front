"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
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
from app.services.entitlement.horoscope_daily_entitlement_gate import (
    HoroscopeDailyAccessDeniedError,
    HoroscopeDailyEntitlementGate,
)
from app.services.prediction import DailyPredictionService
from app.services.prediction.types import (
    ComputeMode,
    DailyPredictionServiceError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/predictions", tags=["predictions"])


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

"""Résolution des codes de systèmes de maisons vers le référentiel SQL."""

from __future__ import annotations

from sqlalchemy import event, select
from sqlalchemy.orm import Session

from app.domain.astrology.house_system_codes import (
    HOUSE_SYSTEM_REFERENCE_ROWS,
    HouseSystemCode,
)
from app.infra.db.models.daily_prediction import DailyPredictionRunModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel
from app.infra.db.models.reference import AstralHouseSystemModel
from app.infra.db.models.user_prediction_baseline import UserPredictionBaselineModel


def _resolve_house_system(session: Session, code: str) -> AstralHouseSystemModel:
    """Retourne la ligne canonique d'un code de système de maisons."""
    house_system = session.scalar(
        select(AstralHouseSystemModel).where(AstralHouseSystemModel.code == code)
    )
    if house_system is None and code in HOUSE_SYSTEM_REFERENCE_ROWS:
        house_system = AstralHouseSystemModel(code=code, **HOUSE_SYSTEM_REFERENCE_ROWS[code])
        session.add(house_system)
    if house_system is None:
        raise ValueError(f"unknown astral house system code: {code!r}")
    return house_system


@event.listens_for(Session, "before_flush")
def _resolve_pending_house_system_codes(
    session: Session, flush_context: object, instances: object
) -> None:
    """Résout les propriétés code conservées pour compatibilité applicative."""
    del flush_context, instances
    for obj in (*session.new, *session.dirty):
        pending_code = getattr(obj, "_pending_house_system_code", None)
        if (
            pending_code is None
            and obj in session.new
            and isinstance(obj, PredictionRulesetModel)
            and obj.house_system_id is None
            and obj.house_system_reference is None
        ):
            pending_code = HouseSystemCode.PLACIDUS
        if pending_code is None:
            continue
        house_system = _resolve_house_system(session, str(pending_code))
        if isinstance(obj, PredictionRulesetModel):
            obj.house_system_reference = house_system
        elif isinstance(obj, (DailyPredictionRunModel, UserPredictionBaselineModel)):
            obj.house_system_effective_reference = house_system
        if hasattr(obj, "_pending_house_system_code"):
            delattr(obj, "_pending_house_system_code")

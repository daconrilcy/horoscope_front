"""Résolution des codes de systèmes de maisons vers le référentiel SQL."""

from __future__ import annotations

from sqlalchemy import event, inspect, select
from sqlalchemy.orm import Session

from app.domain.astrology.house_system_codes import HouseSystemCode
from app.infra.db.models.daily_prediction import DailyPredictionRunModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel
from app.infra.db.models.reference import AstralHouseSystemModel
from app.infra.db.models.user_prediction_baseline import UserPredictionBaselineModel
from app.infra.db.seed.house_system_reference import sync_house_system_seed_data


def _resolve_house_system(session: Session, code: str) -> AstralHouseSystemModel:
    """Retourne la ligne canonique d'un code de système de maisons."""
    sync_house_system_seed_data(session)
    house_system = session.scalar(
        select(AstralHouseSystemModel).where(AstralHouseSystemModel.code == code)
    )
    if house_system is None:
        house_system = next(
            (
                pending
                for pending in session.new
                if isinstance(pending, AstralHouseSystemModel) and pending.code == code
            ),
            None,
        )
    if house_system is None:
        raise ValueError(f"unknown astral house system code: {code!r}")
    return house_system


def resolve_house_system_id(session: Session, code: str) -> int:
    """Retourne l'identifiant SQL canonique, en seedant la ligne si besoin."""
    house_system = _resolve_house_system(session, code)
    if house_system.id is None:
        session.flush()
    return int(house_system.id)


def _has_house_system_reference_table(session: Session) -> bool:
    """Détecte si le schéma courant supporte le référentiel canonique."""
    return inspect(session.connection()).has_table(AstralHouseSystemModel.__tablename__)


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
        if not _has_house_system_reference_table(session):
            continue
        house_system = _resolve_house_system(session, str(pending_code))
        if isinstance(obj, PredictionRulesetModel):
            obj.house_system_reference = house_system
        elif isinstance(obj, (DailyPredictionRunModel, UserPredictionBaselineModel)):
            obj.house_system_effective_reference = house_system
        if hasattr(obj, "_pending_house_system_code"):
            delattr(obj, "_pending_house_system_code")

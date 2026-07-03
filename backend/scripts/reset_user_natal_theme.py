# Commentaire global: utilitaire local pour purger un thème natal et réinitialiser son quota.
"""Supprime le thème natal enregistré d'un utilisateur et remet son quota à zéro."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from sqlalchemy import delete, select

from app.infra.db.models.product_entitlements import (
    FeatureUsageCounterModel,
    PeriodUnit,
    ResetMode,
)
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_astral_natal_theme import UserAstralNatalThemeModel
from app.infra.db.session import SessionLocal

_NATAL_LONG_FEATURE_CODE = "natal_chart_long"
_NATAL_LONG_QUOTA_KEY = "interpretations"
_REUSABLE_THEME_STATUSES = ("queued", "running", "completed")


def reset_user_natal_theme(email: str) -> None:
    """Supprime les thèmes natals stockés pour un email et réinitialise le compteur associé."""
    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == email))
        if user is None:
            raise SystemExit(f"Utilisateur introuvable: {email}")

        deleted_themes = db.execute(
            delete(UserAstralNatalThemeModel).where(
                UserAstralNatalThemeModel.user_id == user.id,
                UserAstralNatalThemeModel.status.in_(_REUSABLE_THEME_STATUSES),
            )
        ).rowcount

        counter = db.scalar(
            select(FeatureUsageCounterModel).where(
                FeatureUsageCounterModel.user_id == user.id,
                FeatureUsageCounterModel.feature_code == _NATAL_LONG_FEATURE_CODE,
                FeatureUsageCounterModel.quota_key == _NATAL_LONG_QUOTA_KEY,
                FeatureUsageCounterModel.period_unit == PeriodUnit.LIFETIME,
                FeatureUsageCounterModel.period_value == 1,
                FeatureUsageCounterModel.reset_mode == ResetMode.LIFETIME,
            )
        )
        if counter is None:
            counter = FeatureUsageCounterModel(
                user_id=user.id,
                feature_code=_NATAL_LONG_FEATURE_CODE,
                quota_key=_NATAL_LONG_QUOTA_KEY,
                period_unit=PeriodUnit.LIFETIME,
                period_value=1,
                reset_mode=ResetMode.LIFETIME,
                window_start=datetime(1970, 1, 1, tzinfo=timezone.utc),
                window_end=None,
                used_count=0,
            )
            # Le compteur natal long est de type lifetime, donc la fenêtre canonique est fixe.
            db.add(counter)
        else:
            counter.used_count = 0

        db.commit()
        print(
            "OK "
            f"user_id={user.id} email={email} deleted_themes={deleted_themes or 0} "
            f"natal_long_used_count=0"
        )


def main() -> None:
    """Point d'entrée CLI du script PowerShell ou Python local."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--email",
        default="daconrilcy@hotmail.com",
        help="Email de l'utilisateur à purger",
    )
    args = parser.parse_args()
    reset_user_natal_theme(args.email)


if __name__ == "__main__":
    main()

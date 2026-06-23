# Commentaire global: accès persistant aux thèmes natals Astral produits.
"""Repository SQLAlchemy des thèmes natals Astral mis en cache."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.infra.db.models.user_astral_natal_theme import UserAstralNatalThemeModel


class UserAstralNatalThemeRepository:
    """Centralise les lectures et écritures des résultats natals Astral."""

    def __init__(self, db: Session) -> None:
        """Conserve la session SQLAlchemy injectée par la couche applicative."""
        self.db = db

    def list_limited_themes(
        self,
        *,
        user_id: int,
        birth_profile_id: int,
        theme_level: str,
        birth_fingerprint: str,
    ) -> list[UserAstralNatalThemeModel]:
        """Retourne les jobs existants pour un slot natal limité donné."""
        return list(
            self.db.scalars(
                select(UserAstralNatalThemeModel)
                .where(
                    UserAstralNatalThemeModel.user_id == user_id,
                    UserAstralNatalThemeModel.birth_profile_id == birth_profile_id,
                    UserAstralNatalThemeModel.theme_level == theme_level,
                    UserAstralNatalThemeModel.birth_fingerprint == birth_fingerprint,
                    UserAstralNatalThemeModel.status.in_(["queued", "running", "completed"]),
                )
                .order_by(
                    UserAstralNatalThemeModel.created_at.desc(),
                    UserAstralNatalThemeModel.id.desc(),
                )
            )
        )

    def get_by_run_id(self, run_id: str) -> UserAstralNatalThemeModel | None:
        """Retrouve un thème stocké via son identifiant de job Astral."""
        return self.db.scalar(
            select(UserAstralNatalThemeModel).where(UserAstralNatalThemeModel.run_id == run_id)
        )

    def upsert_response(
        self,
        *,
        user_id: int,
        birth_profile_id: int,
        birth_fingerprint: str,
        theme_level: str,
        requested_product: str,
        requested_plan: str,
        service_code: str,
        status: str,
        run_id: str,
        client_request_id: str,
        response_payload: dict[str, Any],
    ) -> UserAstralNatalThemeModel:
        """Crée ou actualise la ligne associée à un run Astral terminal."""
        model = self.get_by_run_id(run_id)
        if model is None:
            model = UserAstralNatalThemeModel(
                user_id=user_id,
                birth_profile_id=birth_profile_id,
                birth_fingerprint=birth_fingerprint,
                theme_level=theme_level,
                requested_product=requested_product,
                requested_plan=requested_plan,
                service_code=service_code,
                status=status,
                run_id=run_id,
                client_request_id=client_request_id,
                response_payload=response_payload,
            )
            self.db.add(model)
            self.db.flush()
            return model

        model.status = status
        model.service_code = service_code
        model.birth_fingerprint = birth_fingerprint
        model.response_payload = response_payload
        self.db.flush()
        return model

    def mark_limited_theme_superseded(
        self,
        *,
        user_id: int,
        birth_profile_id: int,
        theme_level: str,
        active_birth_fingerprint: str,
    ) -> None:
        """Désactive les anciens slots limités remplacés par des données natales récentes."""
        self.db.execute(
            update(UserAstralNatalThemeModel)
            .where(
                UserAstralNatalThemeModel.user_id == user_id,
                UserAstralNatalThemeModel.birth_profile_id == birth_profile_id,
                UserAstralNatalThemeModel.theme_level == theme_level,
                UserAstralNatalThemeModel.birth_fingerprint != active_birth_fingerprint,
                UserAstralNatalThemeModel.status.in_(["queued", "running", "completed"]),
            )
            .values(status="superseded")
        )
        self.db.flush()

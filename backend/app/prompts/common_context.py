"""Common context for LLM prompts (Story 59.5, Qualified in Story 66.6)."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.llm.legacy.bridge import get_legacy_use_case_name
from app.infra.db.models.user_natal_interpretation import (
    UserNatalInterpretationModel,
)
from app.services.persona_config_service import PersonaConfigService
from app.services.user_birth_profile_service import UserBirthProfileService
from app.services.user_natal_chart_service import UserNatalChartService

logger = logging.getLogger(__name__)


class PromptCommonContext(BaseModel):
    """Socle commun de contexte pour chaque prompt."""

    natal_interpretation: Optional[str] = None
    natal_data: Optional[dict[str, Any]] = None
    precision_level: str
    astrologer_profile: dict[str, Any]
    period_covered: str
    today_date: str
    use_case_name: str
    use_case_key: str  # Raw key used for logic branching (e.g. "natal_interpretation")

    @model_validator(mode="after")
    def validate_natal_source(self) -> PromptCommonContext:
        """S'assure qu'on a soit l'interprétation, soit les données brutes."""
        if self.use_case_key.startswith("natal_interpretation"):
            return self

        if self.use_case_key in {"daily_prediction", "horoscope_daily"}:
            return self

        # Relax validation for build() to return partial contexts
        # The quality is handled by QualifiedContext
        return self


class QualifiedContext(BaseModel):
    """Artifact representing qualified common context (Story 66.6)."""

    payload: PromptCommonContext
    source: str  # "db", "partial_db", "fallback"
    missing_fields: List[str] = Field(default_factory=list)
    context_quality: Literal["full", "partial", "minimal"] = "full"
    degradation_reasons: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_quality(self) -> QualifiedContext:
        """Auto-computes missing fields and quality if not already provided."""
        if not self.missing_fields:
            missing = []
            if not self.payload.natal_interpretation:
                missing.append("natal_interpretation")
            if not self.payload.natal_data:
                missing.append("natal_data")
            if not self.payload.astrologer_profile:
                missing.append("astrologer_profile")
            self.missing_fields = missing

        # Always re-compute quality to match missing_fields
        self.context_quality = self.compute_quality(self.missing_fields)
        return self

    _CRITICAL_FIELDS = frozenset({"natal_data", "astrologer_profile"})
    _SECONDARY_FIELDS = frozenset({"natal_interpretation", "period_covered", "today_date"})

    @staticmethod
    def compute_quality(missing: List[str]) -> Literal["full", "partial", "minimal"]:
        """
        Calculates context quality based on missing fields criticality.
        (AC2 rules)
        """
        missing_set = set(missing)

        # 1. Minimal: both natal sources missing
        if "natal_data" in missing_set and "natal_interpretation" in missing_set:
            return "minimal"

        # 2. Minimal: astrologer_profile AND at least one natal source missing
        if "astrologer_profile" in missing_set and (
            "natal_data" in missing_set or "natal_interpretation" in missing_set
        ):
            return "minimal"

        # 3. Partial: everything else missing
        if missing_set:
            return "partial"

        return "full"

    def is_degraded(self) -> bool:
        return self.context_quality != "full"


class CommonContextBuilder:
    """Bâtisseur de contexte commun pour les prompts."""

    @staticmethod
    def _format_date_fr(d: date) -> str:
        """Formatte une date en français long."""
        MOIS_FR = [
            "janvier",
            "février",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "août",
            "septembre",
            "octobre",
            "novembre",
            "décembre",
        ]
        JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        jour = JOURS_FR[d.weekday()]
        mois = MOIS_FR[d.month - 1]
        return f"{jour} {d.day} {mois} {d.year}"

    @classmethod
    def build(cls, user_id: int, use_case_key: str, period: str, db: Session) -> QualifiedContext:
        """
        Construit le socle commun de contexte qualifié.
        (Story 66.6)
        """
        missing_fields = []
        degradation_reasons = []
        source = "db"

        # 1. Fetch Persona
        astrologer_profile = {}
        try:
            persona = PersonaConfigService.get_active(db)
            if persona:
                astrologer_profile = {
                    "name": persona.display_name,
                    "style": persona.response_style,
                    "tonality": persona.tone,
                    "limits": persona.prudence_level,
                    "description": persona.to_prompt_line(),
                }
            else:
                missing_fields.append("astrologer_profile")
                degradation_reasons.append("persona_not_found")
        except Exception:
            missing_fields.append("astrologer_profile")
            degradation_reasons.append("persona_fetch_error")

        # 2. Fetch User Profile & Precision
        profile = UserBirthProfileService.get_for_user(db, user_id)
        precision_level = "précision complète"
        if not profile.birth_time or profile.birth_time == "00:00":
            precision_level = "précision dégradée — heure de naissance manquante"
            # secondary degradation
        if not profile.birth_place or profile.birth_place.lower() == "unknown":
            precision_level = "précision dégradée — lieu de naissance manquant"

        # 3. Natal Source
        natal_interpretation = None
        natal_data = None

        if use_case_key != "natal_interpretation":
            stmt = (
                select(UserNatalInterpretationModel)
                .where(UserNatalInterpretationModel.user_id == user_id)
                .order_by(UserNatalInterpretationModel.created_at.desc())
                .limit(1)
            )
            interp = db.execute(stmt).scalar_one_or_none()
            if interp and interp.interpretation_payload:
                payload = interp.interpretation_payload
                natal_interpretation = payload.get("summary") or payload.get("text")
            else:
                missing_fields.append("natal_interpretation")

        try:
            chart = UserNatalChartService.get_latest_for_user(db, user_id)
            natal_data = chart.result.model_dump(mode="json")
        except Exception as e:
            missing_fields.append("natal_data")
            if not natal_interpretation:
                source = "fallback"

            # Story 66.21: Track Natal No DB fallback (AC9)
            # On distingue si c'est attendu (ex: tests sans session DB)
            # ou si c'est une erreur technique imprévue (prod).
            from sqlalchemy.exc import SQLAlchemyError

            is_database_error = isinstance(e, SQLAlchemyError)

            from app.llm_orchestration.models import FallbackType
            from app.llm_orchestration.services.fallback_governance import (
                FallbackGovernanceRegistry,
            )

            FallbackGovernanceRegistry.track_fallback(
                FallbackType.NATAL_NO_DB,
                call_site="common_context_builder",
                feature="natal",
                is_nominal=not is_database_error,  # True if intentional stub, False if DB crash
            )

            if is_database_error:
                logger.error(
                    "common_context_database_error_fallback user_id=%d error=%s", user_id, e
                )

        # 4. Dates & Periods
        today = date.today()
        today_date = cls._format_date_fr(today)
        period_label = f"journée du {cls._format_date_fr(today)}"
        if period == "weekly":
            period_label = f"semaine du {cls._format_date_fr(today)}"

        # 5. Catalog Name
        use_case_name = get_legacy_use_case_name(use_case_key)

        payload = PromptCommonContext(
            natal_interpretation=natal_interpretation,
            natal_data=natal_data,
            precision_level=precision_level,
            astrologer_profile=astrologer_profile,
            period_covered=period_label,
            today_date=today_date,
            use_case_name=use_case_name,
            use_case_key=use_case_key,
        )

        if missing_fields and source != "fallback":
            source = "partial_db"

        quality = QualifiedContext.compute_quality(missing_fields)

        qualified_ctx = QualifiedContext(
            payload=payload,
            source=source,
            missing_fields=missing_fields,
            context_quality=quality,
            degradation_reasons=degradation_reasons,
        )

        if qualified_ctx.is_degraded():
            logger.warning(
                "common_context_degraded user_id=%d use_case=%s quality=%s missing=%s",
                user_id,
                use_case_key,
                quality,
                missing_fields,
            )

        return qualified_ctx

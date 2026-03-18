"""Common context for LLM prompts (Story 59.5)."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.user_natal_interpretation import (
    UserNatalInterpretationModel,
)
from app.prompts.catalog import PROMPT_CATALOG
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
        """S'assure qu'on a soit l'interprétation, soit les données brutes.

        Les use_cases de type 'natal_interpretation*' produisent l'interprétation
        — ils ne la consomment pas — donc la contrainte ne s'applique pas.
        """
        if self.use_case_key.startswith("natal_interpretation"):
            return self

        if self.natal_interpretation is None and self.natal_data is None:
            raise ValueError("Either natal_interpretation or natal_data must be provided")
        return self

class CommonContextBuilder:
    """Bâtisseur de contexte commun pour les prompts."""

    @staticmethod
    def _format_date_fr(d: date) -> str:
        """Formatte une date en français long."""
        MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin",
                   "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        jour = JOURS_FR[d.weekday()]
        mois = MOIS_FR[d.month - 1]
        return f"{jour} {d.day} {mois} {d.year}"

    @classmethod
    def build(
        cls, user_id: int, use_case_key: str, period: str, db: Session
    ) -> PromptCommonContext:
        """
        Construit le socle commun de contexte.
        """
        # 1. Fetch Persona
        persona = PersonaConfigService.get_active(db)
        astrologer_profile = {
            "name": persona.name,
            "style": ", ".join(persona.style_markers),
            "tonality": persona.tone,
            "limits": ", ".join(persona.boundaries),
            "description": persona.description,
        }
        
        # 2. Fetch User Profile & Precision
        profile = UserBirthProfileService.get_for_user(db, user_id)
        precision_level = "précision complète"
        if not profile.birth_time or profile.birth_time == "00:00":
            precision_level = "précision dégradée — heure de naissance manquante"
        elif not profile.birth_place or profile.birth_place.lower() == "unknown":
            precision_level = "précision dégradée — lieu de naissance manquant"
            
        # 3. Natal Source
        natal_interpretation = None
        natal_data = None
        
        # Special case: if generating natal interpretation, we don't consume it
        if use_case_key != "natal_interpretation":
            # Try to get existing interpretation
            stmt = select(UserNatalInterpretationModel).where(
                UserNatalInterpretationModel.user_id == user_id
            ).order_by(UserNatalInterpretationModel.created_at.desc()).limit(1)
            interp = db.execute(stmt).scalar_one_or_none()
            
            if interp and interp.interpretation_payload:
                # Extract summary/text from payload
                payload = interp.interpretation_payload
                natal_interpretation = payload.get("summary") or payload.get("text")
        
        if not natal_interpretation:
            # Fallback to raw data
            try:
                chart = UserNatalChartService.get_latest_for_user(db, user_id)
                natal_data = chart.result.model_dump(mode="json")
            except Exception:
                logger.warning("common_context_no_natal_data user_id=%d", user_id)
                
        # 4. Dates & Periods
        today = date.today()
        today_date = cls._format_date_fr(today)
        
        period_label = f"journée du {cls._format_date_fr(today)}"
        if period == "weekly":
            period_label = f"semaine du {cls._format_date_fr(today)}"
            
        # 5. Catalog Name
        catalog_entry = PROMPT_CATALOG.get(use_case_key)
        use_case_name = catalog_entry.name if catalog_entry else use_case_key
        
        return PromptCommonContext(
            natal_interpretation=natal_interpretation,
            natal_data=natal_data,
            precision_level=precision_level,
            astrologer_profile=astrologer_profile,
            period_covered=period_label,
            today_date=today_date,
            use_case_name=use_case_name,
            use_case_key=use_case_key,
        )

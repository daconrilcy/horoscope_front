"""
Service d'interprétation textuelle du thème natal via AI Engine.

Ce module génère des interprétations textuelles riches et personnalisées
des thèmes natals en utilisant le AI Engine.
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.application.llm.ai_engine_adapter import AIEngineAdapter, AIEngineAdapterError
from app.services.current_context import build_current_prompt_context
from app.services.user_birth_profile_service import UserBirthProfileData
from app.services.user_natal_chart_service import UserNatalChartReadData

if TYPE_CHECKING:
    from app.domain.astrology.natal_calculation import NatalResult

logger = logging.getLogger(__name__)

SIGNS = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]

SIGN_NAMES_FR = {
    "aries": "Bélier",
    "taurus": "Taureau",
    "gemini": "Gémeaux",
    "cancer": "Cancer",
    "leo": "Lion",
    "virgo": "Vierge",
    "libra": "Balance",
    "scorpio": "Scorpion",
    "sagittarius": "Sagittaire",
    "capricorn": "Capricorne",
    "aquarius": "Verseau",
    "pisces": "Poissons",
}

PLANET_NAMES_FR = {
    "sun": "Soleil",
    "moon": "Lune",
    "mercury": "Mercure",
    "venus": "Vénus",
    "mars": "Mars",
    "jupiter": "Jupiter",
    "saturn": "Saturne",
    "uranus": "Uranus",
    "neptune": "Neptune",
    "pluto": "Pluton",
}

ASPECT_NAMES_FR = {
    "conjunction": "conjonction",
    "opposition": "opposition",
    "trine": "trigone",
    "square": "carré",
    "sextile": "sextile",
}

MAJOR_ASPECTS = {"conjunction", "opposition", "trine", "square", "sextile"}

USE_CASE = "natal_chart_interpretation"

UNKNOWN_BIRTH_TIME_SENTINEL = "00:00"
UNKNOWN_LOCATION_SENTINELS = {"", "unknown", "non spécifié"}


class NatalInterpretationMetadata(BaseModel):
    """Métadonnées de l'interprétation."""

    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cached: bool = False
    degraded_mode: str | None = None
    tokens_used: int = 0
    latency_ms: int = 0


class NatalInterpretationData(BaseModel):
    """Données d'interprétation du thème natal."""

    chart_id: str
    text: str
    summary: str
    key_points: list[str]
    advice: list[str]
    disclaimer: str
    metadata: NatalInterpretationMetadata


class NatalInterpretationServiceError(Exception):
    """Exception levée lors d'erreurs d'interprétation."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def _longitude_to_sign(longitude: float) -> str:
    """Convertit une longitude en signe zodiacal."""
    index = int(longitude / 30) % 12
    return SIGNS[index]


def _format_longitude(longitude: float) -> str:
    """Formate une longitude en degrés et minutes."""
    sign_longitude = longitude % 30
    degrees = int(sign_longitude)
    minutes = int((sign_longitude - degrees) * 60)
    return f"{degrees}°{minutes:02d}'"


def _detect_degraded_mode(birth_profile: UserBirthProfileData) -> str | None:
    """
    Détecte si le thème natal est en mode dégradé.

    Le mode dégradé est activé quand l'heure ou le lieu de naissance n'est pas connu.
    L'heure inconnue est indiquée par la valeur sentinelle "00:00".
    Le lieu inconnu est indiqué par une chaîne vide ou une valeur sentinelle.

    Args:
        birth_profile: Profil de naissance de l'utilisateur.

    Returns:
        Mode dégradé ("no_time", "no_location", "no_location_no_time") ou None si complet.
    """
    no_time = birth_profile.birth_time == UNKNOWN_BIRTH_TIME_SENTINEL
    no_location = (
        not birth_profile.birth_place or birth_profile.birth_place in UNKNOWN_LOCATION_SENTINELS
    )

    if no_time and no_location:
        return "no_location_no_time"
    if no_time:
        return "no_time"
    if no_location:
        return "no_location"
    return None


def build_natal_chart_summary(
    natal_result: "NatalResult",
    birth_place: str,
    birth_date: str,
    birth_time: str,
    degraded_mode: str | None = None,
) -> str:
    """
    Construit un résumé textuel du thème natal pour le prompt AI.

    Args:
        natal_result: Résultat du calcul natal.
        birth_place: Lieu de naissance.
        birth_date: Date de naissance.
        birth_time: Heure de naissance.
        degraded_mode: Mode dégradé éventuel.

    Returns:
        Résumé formaté pour le AI Engine.
    """
    lines: list[str] = []

    time_display = birth_time
    place_display = birth_place
    if degraded_mode == "no_time":
        time_display = "Non connue (interprétation des maisons approximative)"
    elif degraded_mode == "no_location":
        place_display = "Non connu (Ascendant non disponible)"
    elif degraded_mode == "no_location_no_time":
        time_display = "Non connue"
        place_display = "Non connu"

    lines.append(f"Thème natal né(e) le {birth_date} à {time_display} à {place_display}:")
    lines.append("")

    sun_position = next((p for p in natal_result.planet_positions if p.planet_code == "sun"), None)
    if sun_position:
        sign_name = SIGN_NAMES_FR.get(sun_position.sign_code, sun_position.sign_code)
        lon_fmt = _format_longitude(sun_position.longitude)
        lines.append(f"SOLEIL: {sign_name} à {lon_fmt} (Maison {sun_position.house_number})")

    moon_position = next(
        (p for p in natal_result.planet_positions if p.planet_code == "moon"), None
    )
    if moon_position:
        sign_name = SIGN_NAMES_FR.get(moon_position.sign_code, moon_position.sign_code)
        lon_fmt = _format_longitude(moon_position.longitude)
        lines.append(f"LUNE: {sign_name} à {lon_fmt} (Maison {moon_position.house_number})")

    house1 = next((h for h in natal_result.houses if h.number == 1), None)
    if house1:
        asc_sign = _longitude_to_sign(house1.cusp_longitude)
        asc_sign_name = SIGN_NAMES_FR.get(asc_sign, asc_sign)
        asc_lon_fmt = _format_longitude(house1.cusp_longitude)
        lines.append(f"ASCENDANT: {asc_sign_name} à {asc_lon_fmt}")

    lines.append("")
    lines.append("ASPECTS MAJEURS:")
    major_aspects = [a for a in natal_result.aspects if a.aspect_code in MAJOR_ASPECTS]
    for aspect in major_aspects[:6]:
        planet_a_name = PLANET_NAMES_FR.get(aspect.planet_a, aspect.planet_a)
        planet_b_name = PLANET_NAMES_FR.get(aspect.planet_b, aspect.planet_b)
        aspect_name = ASPECT_NAMES_FR.get(aspect.aspect_code, aspect.aspect_code)
        orb_rounded = round(aspect.orb, 1)
        lines.append(f"- {planet_a_name} {aspect_name} {planet_b_name} (orbe {orb_rounded}°)")

    lines.append("")
    lines.append("MAISONS ANGULAIRES:")
    angular_houses = {1: "Ascendant", 4: "Fond du Ciel", 7: "Descendant", 10: "Milieu du Ciel"}
    for house_num, house_label in angular_houses.items():
        house = next((h for h in natal_result.houses if h.number == house_num), None)
        if house:
            sign = _longitude_to_sign(house.cusp_longitude)
            sign_name = SIGN_NAMES_FR.get(sign, sign)
            lines.append(f"- Maison {house_num} ({house_label}): {sign_name}")

    return "\n".join(lines)


def build_chat_natal_hint(
    natal_result: "NatalResult",
    degraded_mode: str | None = None,
) -> str:
    """Résumé ultra-court (≤ 600 chars) du thème natal pour le contexte de chat.

    Contient uniquement les 3 piliers (Soleil, Lune, Ascendant) et les 3 aspects
    les plus serrés (orbe minimal). N'expose PAS les détails de maisons angulaires
    ni tous les aspects — ceux-ci restent réservés au use-case d'interprétation natal.

    Args:
        natal_result: Résultat du calcul natal.
        degraded_mode: Mode dégradé éventuel (no_time, no_location, etc.).

    Returns:
        Hint compact séparé par " · ", ex:
        "Soleil en Bélier (Maison 1) · Lune en Taureau · Ascendant Capricorne
         · Soleil conjonction Vénus · Jupiter trigone Lune · Mars carré Saturne"
    """
    parts: list[str] = []

    sun = next((p for p in natal_result.planet_positions if p.planet_code == "sun"), None)
    moon = next((p for p in natal_result.planet_positions if p.planet_code == "moon"), None)
    house1 = next((h for h in natal_result.houses if h.number == 1), None)

    if sun:
        sign_name = SIGN_NAMES_FR.get(sun.sign_code, sun.sign_code)
        parts.append(f"Soleil en {sign_name} (Maison {sun.house_number})")
    if moon:
        sign_name = SIGN_NAMES_FR.get(moon.sign_code, moon.sign_code)
        parts.append(f"Lune en {sign_name} (Maison {moon.house_number})")
    if house1 and degraded_mode not in ("no_location", "no_location_no_time"):
        asc_sign = _longitude_to_sign(house1.cusp_longitude)
        asc_name = SIGN_NAMES_FR.get(asc_sign, asc_sign)
        parts.append(f"Ascendant {asc_name}")

    # Top 3 major aspects by tightest orb
    major = sorted(
        [a for a in natal_result.aspects if a.aspect_code in MAJOR_ASPECTS],
        key=lambda a: a.orb,
    )[:3]
    for asp in major:
        pa = PLANET_NAMES_FR.get(asp.planet_a, asp.planet_a)
        pb = PLANET_NAMES_FR.get(asp.planet_b, asp.planet_b)
        asp_name = ASPECT_NAMES_FR.get(asp.aspect_code, asp.aspect_code)
        parts.append(f"{pa} {asp_name} {pb}")

    return " · ".join(parts)


class NatalInterpretationService:
    """Service d'interprétation textuelle du thème natal."""

    @staticmethod
    async def interpret_chart(
        natal_chart: UserNatalChartReadData,
        birth_profile: UserBirthProfileData,
        user_id: int,
        request_id: str,
        trace_id: str | None = None,
        persona_id: str | None = None,
        db: Session | None = None,
    ) -> NatalInterpretationData:
        """
        Génère une interprétation textuelle du thème natal.

        Args:
            natal_chart: Données du thème natal.
            birth_profile: Profil de naissance de l'utilisateur.
            user_id: Identifiant de l'utilisateur.
            request_id: Identifiant de requête pour le logging.
            trace_id: Identifiant de trace pour le tracing distribué.

        Returns:
            Interprétation textuelle avec métadonnées.

        Raises:
            NatalInterpretationServiceError: En cas d'erreur AI Engine.
        """
        degraded_mode = _detect_degraded_mode(birth_profile)

        natal_chart_summary = build_natal_chart_summary(
            natal_result=natal_chart.result,
            birth_place=birth_profile.birth_place,
            birth_date=birth_profile.birth_date,
            birth_time=birth_profile.birth_time,
            degraded_mode=degraded_mode,
        )

        current_context = build_current_prompt_context(birth_profile)
        current_context_payload = asdict(current_context)

        birth_data = {
            "date": birth_profile.birth_date,
            "time": birth_profile.birth_time
            if degraded_mode not in {"no_time", "no_location_no_time"}
            else "Non connue (interprétation des maisons approximative)",
            "place": birth_profile.birth_place
            if degraded_mode not in {"no_location", "no_location_no_time"}
            else "Non connu (Ascendant non disponible)",
        }

        try:
            user_plan = "free"
            if db is not None:
                # Story 66.15: resolve user plan for assembly when DB context is available.
                from app.services.effective_entitlement_resolver_service import (
                    EffectiveEntitlementResolverService,
                )

                snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
                    db,
                    app_user_id=user_id,
                )
                user_plan = snapshot.plan_code

            if db is None:
                # Legacy compatibility path used by unit tests and lightweight callers.
                result = await AIEngineAdapter.generate_guidance(
                    use_case=USE_CASE,
                    context={
                        "natal_chart_summary": natal_chart_summary,
                        "current_context": str(current_context_payload),
                        "birth_data": str(birth_data),
                    },
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id or request_id,
                    db=db,
                    plan=user_plan,
                )
            else:
                from app.domain.llm.runtime.contracts import NatalExecutionInput

                natal_input = NatalExecutionInput(
                    use_case_key="natal_interpretation",
                    user_id=user_id,
                    request_id=request_id,
                    trace_id=trace_id or request_id,
                    level="complete",
                    chart_json=natal_chart.chart_id,  # Should probably be the actual JSON or ID
                    natal_data=birth_profile.model_dump(),
                    evidence_catalog=[],
                    persona_id=persona_id,
                    plan=user_plan,
                    astro_context=str(current_context_payload),
                )

                # Generate interpretation via Gateway V2
                result = await AIEngineAdapter.generate_natal_interpretation(
                    natal_input=natal_input,
                    db=db,
                )

            # Extract structured sections or fallback to raw
            if result.structured_output:
                s = result.structured_output
                summary = s.get("summary") or s.get("text") or result.raw_output
                key_points = s.get("key_points") or []
                advice = s.get("actionable_advice") or s.get("advice") or []
                disclaimer = s.get("disclaimer") or ""
            else:
                summary = result.raw_output
                key_points = []
                advice = []
                disclaimer = ""

            return NatalInterpretationData(
                chart_id=natal_chart.chart_id,
                text=result.raw_output,
                summary=summary,
                key_points=key_points,
                advice=advice,
                disclaimer=disclaimer,
                metadata=NatalInterpretationMetadata(
                    cached=getattr(result.meta, "cached", False),
                    degraded_mode=degraded_mode,
                    tokens_used=getattr(result.usage, "total_tokens", 0)
                    if hasattr(result, "usage")
                    else 0,
                    latency_ms=getattr(result.meta, "latency_ms", 0),
                ),
            )
        except (AIEngineAdapterError, TimeoutError) as error:
            raise NatalInterpretationServiceError(
                code="ai_engine_timeout",
                message="AI Engine timeout during interpretation",
                details={"request_id": request_id},
            ) from error
        except Exception as error:
            error_code = getattr(error, "code", "ai_engine_error")
            raise NatalInterpretationServiceError(
                code=str(error_code),
                message=f"AI Engine error: {error}",
                details={"request_id": request_id},
            ) from error

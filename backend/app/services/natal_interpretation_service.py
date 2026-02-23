"""
Service d'interprétation textuelle du thème natal via AI Engine.

Ce module génère des interprétations textuelles riches et personnalisées
des thèmes natals en utilisant le AI Engine.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from app.ai_engine.schemas import GenerateContext, GenerateInput, GenerateRequest
from app.ai_engine.services.generate_service import generate_text
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

    def __init__(
        self, code: str, message: str, details: dict[str, str] | None = None
    ) -> None:
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
        not birth_profile.birth_place
        or birth_profile.birth_place in UNKNOWN_LOCATION_SENTINELS
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

    sun_position = next(
        (p for p in natal_result.planet_positions if p.planet_code == "sun"), None
    )
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


def _parse_interpretation_sections(text: str) -> tuple[str, list[str], list[str], str]:
    """
    Parse le texte structuré retourné par l'IA.

    Le template impose 4 sections numérotées :
    1. Synthèse (2-3 phrases)
    2. Points clés (Soleil, Lune, Ascendant, aspects majeurs)
    3. Conseils actionnables et positifs
    4. Note de prudence

    Args:
        text: Texte brut retourné par l'IA.

    Returns:
        Tuple (summary, key_points, advice, disclaimer).
    """
    section_pattern = re.compile(r"^\d+\.\s*", re.MULTILINE)
    parts = section_pattern.split(text)

    if len(parts) < 2:
        logger.warning(
            "interpretation_parse_failed sections_found=0 text_length=%d",
            len(text),
        )
        return text.strip(), [], [], ""

    parts = [p.strip() for p in parts if p.strip()]

    if len(parts) < 4:
        logger.warning(
            "interpretation_parse_partial sections_found=%d expected=4",
            len(parts),
        )

    summary = parts[0] if len(parts) > 0 else ""

    key_points: list[str] = []
    if len(parts) > 1:
        key_points_raw = parts[1]
        bullet_pattern = re.compile(r"[-•]\s*")
        bullets = bullet_pattern.split(key_points_raw)
        key_points = [b.strip() for b in bullets if b.strip()]
        if not key_points:
            key_points = [line.strip() for line in key_points_raw.split("\n") if line.strip()]

    advice: list[str] = []
    if len(parts) > 2:
        advice_raw = parts[2]
        bullet_pattern = re.compile(r"[-•]\s*")
        bullets = bullet_pattern.split(advice_raw)
        advice = [b.strip() for b in bullets if b.strip()]
        if not advice:
            advice = [line.strip() for line in advice_raw.split("\n") if line.strip()]

    disclaimer = parts[3].strip() if len(parts) > 3 else ""

    return summary, key_points, advice, disclaimer


class NatalInterpretationService:
    """Service d'interprétation textuelle du thème natal."""

    @staticmethod
    async def interpret_chart(
        natal_chart: UserNatalChartReadData,
        birth_profile: UserBirthProfileData,
        user_id: int,
        request_id: str,
        trace_id: str | None = None,
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

        birth_data = {
            "date": birth_profile.birth_date,
            "time": birth_profile.birth_time
            if degraded_mode not in {"no_time", "no_location_no_time"}
            else "Non connue (interprétation des maisons approximative)",
            "place": birth_profile.birth_place
            if degraded_mode not in {"no_location", "no_location_no_time"}
            else "Non connu (Ascendant non disponible)",
        }

        generate_request = GenerateRequest(
            use_case=USE_CASE,
            locale="fr-FR",
            request_id=request_id,
            trace_id=trace_id or request_id,
            input=GenerateInput(tone="warm"),
            context=GenerateContext(
                natal_chart_summary=natal_chart_summary,
                birth_data=birth_data,
            ),
        )

        try:
            response = await generate_text(
                request=generate_request,
                request_id=request_id,
                trace_id=trace_id or request_id,
                user_id=user_id,
            )
        except TimeoutError as error:
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

        summary, key_points, advice, disclaimer = _parse_interpretation_sections(
            response.text
        )

        return NatalInterpretationData(
            chart_id=natal_chart.chart_id,
            text=response.text,
            summary=summary,
            key_points=key_points,
            advice=advice,
            disclaimer=disclaimer,
            metadata=NatalInterpretationMetadata(
                cached=response.meta.cached,
                degraded_mode=degraded_mode,
                tokens_used=response.usage.total_tokens,
                latency_ms=response.meta.latency_ms,
            ),
        )

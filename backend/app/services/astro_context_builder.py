"""Astro Context Builder for LLM prompts."""

from __future__ import annotations

import logging
from datetime import date, datetime, time
from typing import Literal, Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.services.daily_prediction_service import DailyPredictionService
from app.services.user_birth_profile_service import UserBirthProfileService

logger = logging.getLogger(__name__)


class TransitEntry(BaseModel):
    """Transit data for a planet over a natal point."""

    planet: str
    natal_point: str
    aspect: str
    orb: float
    applying: bool


class AspectEntry(BaseModel):
    """Major aspect data for the day."""

    planet_a: str
    planet_b: str
    aspect_type: str
    orb: float
    exact_time: Optional[datetime] = None


class PeriodCovered(BaseModel):
    """Information about the period covered by the context."""

    date_start: date
    date_end: date
    label: str


class AstroContextData(BaseModel):
    """Aggregated astro data for LLM injection."""

    user_id: int
    computed_at: datetime = Field(default_factory=lambda: datetime_provider.utcnow())
    period_covered: PeriodCovered
    precision_level: Literal["full", "degraded"]
    lunar_phase: str
    transits_active: list[TransitEntry]
    dominant_aspects: list[AspectEntry]


class AstroContextBuilder:
    """
    Builds astrological context for LLM prompts by reusing existing computation engines.
    """

    @staticmethod
    def _get_lunar_phase_label(jdut: float) -> str:
        """Calculate human-readable lunar phase."""
        from app.domain.astrology.ephemeris_provider import calculate_planets
        from app.services.llm_generation.natal.prompt_context import _longitude_to_sign

        res = calculate_planets(jdut)
        sun = next(p for p in res.planets if p.planet_id == "sun")
        moon = next(p for p in res.planets if p.planet_id == "moon")

        # Distance Moon - Sun
        dist = (moon.longitude - sun.longitude) % 360

        moon_sign = _longitude_to_sign(moon.longitude)
        # Translation map for signs
        SIGN_FR = {
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
        sign_label = SIGN_FR.get(moon_sign, moon_sign)

        illumination = abs(180 - abs(dist - 180)) / 180.0 * 100

        if dist < 45:
            phase = "Nouvelle Lune"
        elif dist < 90:
            phase = "Premier Croissant"
        elif dist < 135:
            phase = "Premier Quartier"
        elif dist < 180:
            phase = "Lune Gibbeuse Croissante"
        elif dist < 225:
            phase = "Pleine Lune"
        elif dist < 270:
            phase = "Lune Gibbeuse Décroissante"
        elif dist < 315:
            phase = "Dernier Quartier"
        else:
            phase = "Dernier Croissant"

        return f"{phase} en {sign_label}, {illumination:.0f}% d'illumination"

    @classmethod
    def build_daily(
        cls, user_id: int, target_date: date, timezone: str, db: Session
    ) -> Optional[AstroContextData]:
        """Build astro context for a specific day."""
        try:
            # 1. Get birth profile
            profile = UserBirthProfileService.get_for_user(db, user_id)
            if not profile:
                return None

            precision = "full"
            if (
                not profile.birth_time
                or profile.birth_time == "00:00"
                or not profile.birth_place
                or profile.birth_place.lower() == "unknown"
            ):
                precision = "degraded"

            # 2. Get predictions (reusing DailyPredictionService)
            # We need to initialize the service with its dependencies
            from app.prediction.context_loader import PredictionContextLoader
            from app.prediction.engine_orchestrator import EngineOrchestrator
            from app.prediction.persistence_service import PredictionPersistenceService

            loader = PredictionContextLoader()
            persistence = PredictionPersistenceService()
            orchestrator = EngineOrchestrator()

            service = DailyPredictionService(
                context_loader=loader, persistence_service=persistence, orchestrator=orchestrator
            )

            # Compute or get existing
            res = service.get_or_compute(
                user_id=user_id, db=db, date_local=target_date, timezone_override=timezone
            )

            if not res or not res.run:
                return None

            # 3. Extract Transits and Aspects
            transits: list[TransitEntry] = []
            aspects: list[AspectEntry] = []

            # Extract from contributors of the first category score (usually 'global' or similar)
            # Actually, let's aggregate all top contributors
            seen_transits = set()
            for score in res.run.category_scores:
                for c in score.contributors:
                    # Contributor format:
                    # {'body': 'jupiter', 'target': 'sun', 'aspect': 'trine',
                    #  'orb_deg': 1.2, 'phase': 'applying'}
                    key = (c.get("body"), c.get("target"), c.get("aspect"))
                    if key not in seen_transits:
                        transits.append(
                            TransitEntry(
                                planet=str(c.get("body")).capitalize(),
                                natal_point=f"{str(c.get('target')).capitalize()} natal",
                                aspect=str(c.get("aspect")),
                                orb=round(float(c.get("orb_deg", 0)), 1),
                                applying=c.get("phase") == "applying",
                            )
                        )
                        seen_transits.add(key)

            # Limit to top 7 transits
            transits = transits[:7]

            # Dominant aspects (between transiting planets)
            # These are less easy to get directly from contributors which are transit-to-natal
            # But they might be in 'dominant_aspects' if we had them.
            # For now, we'll focus on transits as they are the most personalized part.

            # 4. Lunar Phase
            # Approx JD at noon local
            dt_noon = datetime.combine(target_date, time(12, 0))
            timestamp = dt_noon.timestamp()
            jd = 2440587.5 + timestamp / 86400.0
            lunar_phase = cls._get_lunar_phase_label(jd)

            return AstroContextData(
                user_id=user_id,
                period_covered=PeriodCovered(
                    date_start=target_date,
                    date_end=target_date,
                    label=f"journée du {target_date.strftime('%d %B %Y')}",
                ),
                precision_level=precision,
                lunar_phase=lunar_phase,
                transits_active=transits,
                dominant_aspects=aspects,  # Empty for now, or extracted if available
            )

        except Exception as e:
            logger.warning("astro_context_build_failed user_id=%d error=%s", user_id, str(e))
            return None

    @classmethod
    def build_weekly(
        cls, user_id: int, week_start: date, timezone: str, db: Session
    ) -> Optional[AstroContextData]:
        """Build astro context for a week."""
        from datetime import timedelta

        all_transits: list[TransitEntry] = []
        # Aggregate over 7 days
        # This is a bit heavy, but AC says to reuse build_daily

        precision: str | None = None  # Will be set from first successful day
        lunar_phase_mid = ""

        try:
            seen_keys = {}
            for i in range(7):
                day = week_start + timedelta(days=i)
                day_data = cls.build_daily(user_id, day, timezone, db)
                if day_data:
                    if precision is None:
                        precision = day_data.precision_level  # Same for all days of a given user
                    if i == 3:  # Mid-week phase
                        lunar_phase_mid = day_data.lunar_phase

                    for t in day_data.transits_active:
                        key = (t.planet, t.natal_point, t.aspect)
                        if key not in seen_keys or t.orb < seen_keys[key].orb:
                            seen_keys[key] = t

            all_transits = sorted(seen_keys.values(), key=lambda x: x.orb)[:10]

            return AstroContextData(
                user_id=user_id,
                period_covered=PeriodCovered(
                    date_start=week_start,
                    date_end=week_start + timedelta(days=6),
                    label=f"semaine du {week_start.strftime('%d %B %Y')}",
                ),
                precision_level=precision or "degraded",
                lunar_phase=lunar_phase_mid or "Phase variable",
                transits_active=all_transits,
                dominant_aspects=[],
            )
        except Exception as e:
            logger.warning("astro_context_weekly_build_failed user_id=%d error=%s", user_id, str(e))
            return None

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING

from app.prediction.contribution_calculator import ContributionCalculator
from app.prediction.event_detector import EventDetector

if TYPE_CHECKING:
    from app.prediction.context_loader import LoadedPredictionContext
    from app.prediction.schemas import NatalChart, StepAstroState

logger = logging.getLogger(__name__)


class TransitSignalBuilder:
    """
    Builder for continuous transit signal T(c,t) in engine v3 (AC1, AC2, AC3).
    """

    ORB_MAX_DEFAULT = 8.0

    def __init__(self, contribution_calculator: ContributionCalculator | None = None):
        self._contribution_calculator = contribution_calculator or ContributionCalculator()

    def build_timeline(
        self,
        steps: list[StepAstroState],
        natal: NatalChart,
        ctx: LoadedPredictionContext,
    ) -> dict[str, dict[datetime, float]]:
        """
        Builds a continuous transit signal timeline for each enabled theme (AC3).

        Budget (AC6): Target < 100ms for 96 steps on a standard day.
        """
        start_perf = time.perf_counter()

        enabled_themes = [c.code for c in ctx.prediction_context.categories if c.is_enabled]

        # Result: theme_code -> {time: score}
        timeline: dict[str, dict[datetime, float]] = {theme: {} for theme in enabled_themes}

        # Pre-cache routing and weights for performance
        # significators: theme -> list of (planet_code, weight)
        theme_significators: dict[str, list[tuple[str, float]]] = {
            theme: [] for theme in enabled_themes
        }
        for w in ctx.prediction_context.planet_category_weights:
            if w.category_code in theme_significators and w.weight > 0:
                theme_significators[w.category_code].append((w.planet_code.lower(), w.weight))

        # house_routing: theme -> set of house numbers
        theme_houses: dict[str, set[int]] = {theme: set() for theme in enabled_themes}
        for w in ctx.prediction_context.house_category_weights:
            if w.category_code in theme_houses and w.weight > 0:
                theme_houses[w.category_code].add(w.house_number)

        # Pre-cache orbs and aspect profiles
        aspects = EventDetector.ASPECTS_V1

        # Track orbs for applying/separating detection (AC2)
        prev_orbs: dict[tuple[str, str, int], float] = {}

        for step in steps:
            # Theme scores for THIS step
            step_scores: dict[str, float] = {t: 0.0 for t in enabled_themes}

            for body_code, planet_state in step.planets.items():
                transit_lon = planet_state.longitude
                body_lower = body_code.lower()

                # Nature of transit planet (AC2)
                w_planet = self._contribution_calculator._w_planet(body_code, ctx)

                for target_code, natal_lon in natal.planet_positions.items():
                    target_lower = target_code.lower()

                    # Nature of target (AC2)
                    f_target = self._contribution_calculator._f_target(target_code)
                    target_house = natal.planet_houses.get(target_code)

                    for aspect_deg, aspect_name in aspects.items():
                        key = (body_lower, target_lower, aspect_deg)

                        # 1. Continuous orb (AC1)
                        diff = abs(transit_lon - natal_lon) % 360
                        if diff > 180:
                            diff = 360 - diff
                        orb = abs(diff - aspect_deg)

                        orb_max = self.ORB_MAX_DEFAULT
                        if orb <= orb_max:
                            # 2. Applying vs Separating (AC2)
                            f_phase = 1.0
                            if key in prev_orbs:
                                if orb < prev_orbs[key]:
                                    f_phase = 1.1  # Applying
                                else:
                                    f_phase = 0.9  # Separating
                            prev_orbs[key] = orb

                            # 3. Continuous orb factor (AC1)
                            # Parabolic decay: 1 - (orb/orb_max)^2
                            f_orb = 1.0 - (orb / orb_max) ** 2

                            # 4. Aspect weight and Polarity (AC2)
                            w_aspect = self._contribution_calculator._w_aspect(aspect_name, ctx)

                            # Contextual polarity (simplified for T layer)
                            pol_val = self._get_polarity(aspect_name, body_code, ctx)

                            base_contrib = (
                                w_planet * f_target * w_aspect * f_orb * f_phase * pol_val
                            )

                            # 5. Routing to themes (AC2)
                            for theme in enabled_themes:
                                routed = False
                                # Target routing
                                if target_lower in [s[0] for s in theme_significators[theme]]:
                                    routed = True
                                elif target_house in theme_houses[theme]:
                                    routed = True

                                if routed:
                                    step_scores[theme] += base_contrib

            # Store step results
            for theme in enabled_themes:
                # Clamp T(c,t) to a reasonable range [ -2.0, 2.0 ]
                timeline[theme][step.local_time] = max(-2.0, min(2.0, step_scores[theme]))

        duration_ms = (time.perf_counter() - start_perf) * 1000
        logger.info(
            "transit_signal_built steps=%d duration_ms=%.2f AC6_budget_ok=%s",
            len(steps),
            duration_ms,
            duration_ms < 100,
        )

        return timeline

    def _get_polarity(
        self, aspect_name: str, body_code: str, ctx: LoadedPredictionContext
    ) -> float:
        """Helper to get contextual polarity without full AstroEvent overhead."""
        aspect_profile = self._contribution_calculator._lookup_mapping_value(
            ctx.prediction_context.aspect_profiles, aspect_name
        )
        if aspect_profile is None:
            return 0.0

        valence = aspect_profile.default_valence
        if valence == "positive":
            return 1.0
        if valence == "negative":
            return -1.0
        if valence == "neutral":
            return 0.0

        # Contextual
        planet_profile = self._contribution_calculator._lookup_mapping_value(
            ctx.prediction_context.planet_profiles, body_code
        )
        if planet_profile:
            if planet_profile.typical_polarity == "negative":
                return -0.5
            if planet_profile.typical_polarity == "positive":
                return 0.5
        return 0.0

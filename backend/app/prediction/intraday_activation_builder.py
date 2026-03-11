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
    from app.prediction.temporal_sampler import DayGrid

logger = logging.getLogger(__name__)


class IntradayActivationBuilder:
    """
    Builder for continuous intraday activation signal A(c,t) in engine v3 (AC1, AC2, AC3).
    Focuses on Moon and Angles as fast-moving modulators.
    """

    # Moon orb is typically larger for these fast activations
    MOON_ORB_MAX = 5.0
    
    # Activation Weights (AC1, AC2)
    W_MOON_ASPECT = 0.5
    W_HOUSE_BOOST = 0.1
    W_ANGLE_INGRESS = 0.05
    W_PLANETARY_HOUR = 0.03
    W_NATAL_ANGLE_ASPECT = 0.4

    def __init__(self, contribution_calculator: ContributionCalculator | None = None):
        self._contribution_calculator = contribution_calculator or ContributionCalculator()

    def build_timeline(
        self,
        steps: list[StepAstroState],
        natal: NatalChart,
        ctx: LoadedPredictionContext,
        day_grid: DayGrid | None = None,
    ) -> dict[str, dict[datetime, float]]:
        """
        Builds a continuous activation timeline for each enabled theme (AC3).
        
        Budget (AC6): Target < 50ms for 96 steps.
        """
        start_perf = time.perf_counter()

        enabled_themes = [
            c.code for c in ctx.prediction_context.categories if c.is_enabled
        ]
        
        timeline: dict[str, dict[datetime, float]] = {
            theme: {} for theme in enabled_themes
        }

        # Pre-cache routing
        theme_significators: dict[str, set[str]] = {
            theme: {
                w.planet_code.lower() 
                for w in ctx.prediction_context.planet_category_weights 
                if w.category_code == theme and w.weight > 0
            } 
            for theme in enabled_themes
        }
        
        theme_houses: dict[str, set[int]] = {
            theme: {
                w.house_number 
                for w in ctx.prediction_context.house_category_weights 
                if w.category_code == theme and w.weight > 0
            } 
            for theme in enabled_themes
        }

        aspects = EventDetector.ASPECTS_V1
        
        # Planetary Hours (AC2)
        planetary_hour_changes = []
        if day_grid:
            # Re-use logic from EventDetector to find hour change times
            ph_events = EventDetector(ctx, natal)._detect_planetary_hours(day_grid)
            planetary_hour_changes = [(e.local_time, e.body) for e in ph_events]
        
        # Track for changes
        prev_asc_sign = None
        prev_mc_sign = None
        
        for step in steps:
            step_scores: dict[str, float] = {t: 0.0 for t in enabled_themes}
            
            # 1. MOON ACTIVATIONS (AC1)
            moon = step.planets.get("Moon")
            if moon:
                # Moon-Natal aspects
                for target_code, natal_lon in natal.planet_positions.items():
                    target_lower = target_code.lower()
                    
                    for aspect_deg, aspect_name in aspects.items():
                        diff = abs(moon.longitude - natal_lon) % 360
                        if diff > 180:
                            diff = 360 - diff
                        orb = abs(diff - aspect_deg)
                        
                        if orb <= self.MOON_ORB_MAX:
                            f_orb = 1.0 - (orb / self.MOON_ORB_MAX)
                            w_aspect = self._contribution_calculator._w_aspect(aspect_name, ctx)
                            
                            # Polarity
                            pol_val = self._get_polarity(aspect_name, "Moon", ctx)
                            
                            # Angles drive local relief more strongly than regular planets.
                            w_base = self.W_MOON_ASPECT
                            if target_code in ("Asc", "MC"):
                                w_base = self.W_NATAL_ANGLE_ASPECT
                            
                            contrib = w_base * w_aspect * f_orb * pol_val
                            
                            # Route if target is significator or in linked house
                            target_house = natal.planet_houses.get(target_code)
                            for theme in enabled_themes:
                                if (target_lower in theme_significators[theme] or 
                                    target_house in theme_houses[theme]):
                                    step_scores[theme] += contrib

                # Moon in Natal House activation
                moon_house = moon.natal_house_transited
                if moon_house:
                    for theme in enabled_themes:
                        if moon_house in theme_houses[theme]:
                            step_scores[theme] += self.W_HOUSE_BOOST

            # 2. ANGLE MODULATORS (AC1, AC2)
            # Ascendant sign change
            curr_asc_sign = int(step.ascendant_deg // 30)
            if prev_asc_sign is not None and curr_asc_sign != prev_asc_sign:
                for theme in enabled_themes:
                    step_scores[theme] += self.W_ANGLE_INGRESS
            prev_asc_sign = curr_asc_sign

            # MC sign change (AC1)
            curr_mc_sign = int(step.mc_deg // 30)
            if prev_mc_sign is not None and curr_mc_sign != prev_mc_sign:
                for theme in enabled_themes:
                    step_scores[theme] += self.W_ANGLE_INGRESS
            prev_mc_sign = curr_mc_sign

            # 3. PLANETARY HOUR (AC2)
            # Check if this step is at or just after a planetary hour change
            for change_time, ruler in planetary_hour_changes:
                # 15 min tolerance for grid match
                if 0 <= (step.local_time - change_time).total_seconds() < 900:
                    ruler_lower = ruler.lower()
                    for theme in enabled_themes:
                        if ruler_lower in theme_significators[theme]:
                            step_scores[theme] += self.W_PLANETARY_HOUR
                    break
            
            # Store step results [ -1.0, 1.0 ]
            for theme in enabled_themes:
                timeline[theme][step.local_time] = max(-1.0, min(1.0, step_scores[theme]))

        duration_ms = (time.perf_counter() - start_perf) * 1000
        logger.info(
            "intraday_activation_built steps=%d duration_ms=%.2f",
            len(steps),
            duration_ms
        )
        
        return timeline

    def _get_polarity(
        self, aspect_name: str, body_code: str, ctx: LoadedPredictionContext
    ) -> float:
        """Helper to get contextual polarity."""
        aspect_profile = self._contribution_calculator._lookup_mapping_value(
            ctx.prediction_context.aspect_profiles,
            aspect_name,
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
            ctx.prediction_context.planet_profiles,
            body_code,
        )
        if planet_profile:
            if planet_profile.typical_polarity == "negative":
                return -0.5
            if planet_profile.typical_polarity == "positive":
                return 0.5
        return 0.0

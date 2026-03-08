import logging

from app.prediction.context_loader import LoadedPredictionContext
from app.prediction.schemas import AstroEvent

logger = logging.getLogger(__name__)


class ContributionCalculator:
    """
    Service to calculate the weighted and bounded contribution of each event for each category.
    Contribution(e,c,t) = clamp(
        w_event × w_planet × w_aspect × f_orb × f_phase × f_target × NS(c) × D(e,c) × Pol(e,c),
        -1.0, +1.0
    )
    """

    TARGET_CLASS_MAP: dict[str, str] = {
        "Asc": "angle",
        "MC": "angle",
        "Sun": "luminary",
        "Moon": "luminary",
        "Mercury": "personal",
        "Venus": "personal",
        "Mars": "personal",
        "Jupiter": "social",
        "Saturn": "social",
        "Uranus": "transpersonal",
        "Neptune": "transpersonal",
        "Pluto": "transpersonal",
    }

    TARGET_CLASS_WEIGHTS: dict[str, float] = {
        "angle": 1.30,
        "luminary": 1.20,
        "personal": 1.10,
        "social": 1.00,
        "transpersonal": 0.90,
    }

    PHASE_WEIGHTS: dict[str, float] = {
        "applying": 1.05,
        "exact": 1.15,
        "separating": 0.95,
    }

    def compute(
        self,
        event: AstroEvent,
        ns_map: dict[str, float],
        d_map: dict[str, float],
        ctx: LoadedPredictionContext,
    ) -> dict[str, float]:
        """
        Calculates the contribution vector for an event across all categories.
        """
        f_orb = self._f_orb(event, ctx)
        if f_orb < 1e-9:  # AC7: out-of-orb → zero for all categories
            return {cat: 0.0 for cat in d_map.keys()}

        w_event = self._w_event(event)
        w_planet = self._w_planet(event.body, ctx)
        w_aspect = self._w_aspect(event.aspect, ctx)
        f_phase = self._f_phase(event)
        f_target = self._f_target(event.target)

        base_contribution = w_event * w_planet * w_aspect * f_orb * f_phase * f_target

        results: dict[str, float] = {}
        for cat_code, d_val in d_map.items():
            ns_val = ns_map.get(cat_code, 1.0)
            pol_val = self._pol(event, cat_code, ctx)

            contribution = base_contribution * ns_val * d_val * pol_val

            # AC8 - Clamp to [-1.0, 1.0]
            results[cat_code] = max(-1.0, min(1.0, contribution))

        return results

    def _w_event(self, event: AstroEvent) -> float:
        """AC1 - base_weight already computed by EventDetector from EventTypeData."""
        return event.base_weight

    def _w_planet(self, planet_code: str | None, ctx: LoadedPredictionContext) -> float:
        """AC1 - weight_intraday from PlanetProfileData."""
        if not planet_code:
            return 1.0
        profile = self._lookup_mapping_value(ctx.prediction_context.planet_profiles, planet_code)
        if profile:
            return profile.weight_intraday
        return 1.0

    def _w_aspect(self, aspect_code: str | None, ctx: LoadedPredictionContext) -> float:
        """AC2 - intensity_weight from AspectProfileData."""
        if not aspect_code:
            return 1.0
        profile = self._lookup_mapping_value(ctx.prediction_context.aspect_profiles, aspect_code)
        if profile:
            return profile.intensity_weight
        return 1.0

    def _f_orb(self, event: AstroEvent, ctx: LoadedPredictionContext) -> float:
        """AC3 - parabolic orb factor: 1 - (orb/orb_max)^2."""
        if event.orb_deg is None:
            return 0.0
        if event.aspect is None:
            return 1.0

        orb_max = self._get_orb_max(event, ctx)

        if orb_max <= 0 or event.orb_deg > orb_max:
            return 0.0

        return 1.0 - (event.orb_deg / orb_max) ** 2

    def _get_orb_max(self, event: AstroEvent, ctx: LoadedPredictionContext) -> float:
        """Helper to resolve orb_max for the event."""
        if "orb_max" in event.metadata:
            return float(event.metadata["orb_max"])

        if event.aspect:
            param_key = f"orb_max_{event.aspect.lower()}"
            orb_max = ctx.ruleset_context.parameters.get(param_key)
            if orb_max is not None:
                return float(orb_max)

        logger.warning(
            "orb_max not found for aspect '%s' on event '%s', using default 10.0",
            event.aspect,
            event.event_type,
        )
        return 10.0

    def _f_phase(self, event: AstroEvent) -> float:
        """AC4 - phase factor."""
        phase = event.metadata.get("phase", "exact")
        return self.PHASE_WEIGHTS.get(phase, 1.0)

    def _f_target(self, target_code: str | None) -> float:
        """AC5 - target class factor."""
        if not target_code:
            return 1.0
        target_class = self.TARGET_CLASS_MAP.get(target_code)
        if target_class is None:
            return 1.0  # Unknown target: neutral weight
        return self.TARGET_CLASS_WEIGHTS[target_class]

    def _pol(self, event: AstroEvent, cat_code: str, ctx: LoadedPredictionContext) -> float:
        """AC6 - contextual valence.

        V1: polarity is event-level only per AC6 spec (read from AspectProfileData.default_valence
        and planet type). cat_code is accepted for API compatibility and future category-specific
        valence support.
        """
        aspect_profile = self._lookup_mapping_value(
            ctx.prediction_context.aspect_profiles,
            event.aspect or "",
        )
        if aspect_profile is None:
            return 0.0  # Unknown aspect: no signal

        valence = aspect_profile.default_valence  # "positive", "negative", "neutral", "contextual"
        if valence == "positive":
            return 1.0
        elif valence == "negative":
            return -1.0
        elif valence == "neutral":
            return 0.0
        else:  # "contextual" — use planet profile
            planet_profile = self._lookup_mapping_value(
                ctx.prediction_context.planet_profiles,
                event.body or "",
            )
            if planet_profile:
                if planet_profile.typical_polarity == "negative":
                    return -0.5
                elif planet_profile.typical_polarity == "positive":
                    return 0.5
            return 0.0

    def _lookup_mapping_value(self, mapping: dict, key: str) -> object | None:
        candidates = (key, key.lower(), key.upper(), key.title())
        for candidate in candidates:
            if candidate in mapping:
                return mapping[candidate]
        return None

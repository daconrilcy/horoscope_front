"""Routage produit des evenements astrologiques vers les categories."""

from typing import Any

from app.domain.prediction.context import LoadedPredictionContext
from app.domain.prediction.schemas import AstroEvent


class DomainRouter:
    """
    Service to calculate the distribution vector of an astrological event
    towards different life categories (D(e,c)).
    """

    def route(self, event: AstroEvent, ctx: LoadedPredictionContext) -> dict[str, float]:
        """
        Calculates the category distribution vector for a given event.
        """
        active_categories = [c.code for c in ctx.prediction_context.categories if c.is_enabled]

        # Build indexes once per route() call — not reconstructed in each helper.
        house_to_cat = self._build_house_index(ctx)
        planet_to_cat = self._build_planet_index(ctx)

        if event.event_type == "fixed_star_conjunction":
            return self._route_fixed_star_event(ctx, active_categories)

        house_vector = self._build_house_vector(event)
        planet_blend = self._compute_planet_blend(event.body, planet_to_cat, active_categories)

        if not house_vector:
            # AC5 - events without house target (planetary hours, ingresses)
            # routing via planet blend only.
            return planet_blend

        house_projection = self._project_houses_to_categories(
            house_vector,
            house_to_cat,
            active_categories,
        )

        # Combine: D(e,c) = house_projection[c] * planet_blend[c]
        return {cat: house_projection[cat] * planet_blend[cat] for cat in active_categories}

    # ------------------------------------------------------------------
    # Index builders (called once per route() invocation)
    # ------------------------------------------------------------------

    def _build_house_index(self, ctx: LoadedPredictionContext) -> dict[int, dict[str, float]]:
        index: dict[int, dict[str, float]] = {}
        for w in ctx.prediction_context.house_category_weights:
            index.setdefault(w.house_number, {})[w.category_code] = w.weight
        return index

    def _build_planet_index(self, ctx: LoadedPredictionContext) -> dict[str, dict[str, float]]:
        """Returns planet weights keyed by lowercase planet code."""
        index: dict[str, dict[str, float]] = {}
        for w in ctx.prediction_context.planet_category_weights:
            index.setdefault(w.planet_code.lower(), {})[w.category_code] = w.weight
        return index

    # ------------------------------------------------------------------
    # Core helpers
    # ------------------------------------------------------------------

    def _build_house_vector(self, event: AstroEvent) -> dict[int, float]:
        """
        AC1 - Normalized house vector (70/30 or 1.0).
        """
        metadata = event.metadata or {}
        natal_house = self._extract_house_number(
            metadata.get("natal_house_runtime_target", metadata.get("natal_house_target"))
        )
        transit_house = self._extract_house_number(
            metadata.get("natal_house_runtime_transited", metadata.get("natal_house_transited"))
        )

        if natal_house is None:
            return {}

        if transit_house is None or transit_house == natal_house:
            return {natal_house: 1.0}

        return {natal_house: 0.70, transit_house: 0.30}

    def _extract_house_number(self, raw_house: Any) -> int | None:
        """Extrait un numero depuis un fait runtime maison ou une valeur brute."""
        if raw_house is None:
            return None
        if isinstance(raw_house, int):
            return raw_house
        if isinstance(raw_house, str):
            return self._parse_house_number(raw_house)
        number = getattr(raw_house, "number", None)
        if isinstance(number, int):
            return number
        if isinstance(number, str):
            return self._parse_house_number(number)
        if isinstance(raw_house, dict):
            dict_number = raw_house.get("number") or raw_house.get("house")
            if isinstance(dict_number, int):
                return dict_number
            if isinstance(dict_number, str):
                return self._parse_house_number(dict_number)
        return None

    def _parse_house_number(self, raw_number: str) -> int | None:
        """Normalise un numero maison issu d'une metadata JSON."""
        try:
            house_number = int(raw_number)
        except ValueError:
            return None
        if 1 <= house_number <= 12:
            return house_number
        return None

    def _project_houses_to_categories(
        self,
        house_vector: dict[int, float],
        house_to_cat: dict[int, dict[str, float]],
        active_categories: list[str],
    ) -> dict[str, float]:
        """
        AC2 - Project houses to categories via HouseCategoryWeightData.
        """
        projection = {cat: 0.0 for cat in active_categories}

        for house, weight in house_vector.items():
            for cat, house_cat_weight in house_to_cat.get(house, {}).items():
                if cat in projection:
                    projection[cat] += weight * house_cat_weight

        return projection

    def _compute_planet_blend(
        self,
        planet_code: str | None,
        planet_to_cat: dict[str, dict[str, float]],
        active_categories: list[str],
    ) -> dict[str, float]:
        """
        AC3 - Planet blend [0.5, 1.0].
        D_planet(c) = 0.50 + 0.50 * W_planet_to_cat(c).
        Absent or unknown planet → floor 0.5 (no amplification).
        """
        cat_weights = planet_to_cat.get(planet_code.lower(), {}) if planet_code else {}
        return {cat: 0.50 + 0.50 * cat_weights.get(cat, 0.0) for cat in active_categories}

    def _route_fixed_star_event(
        self,
        ctx: LoadedPredictionContext,
        active_categories: list[str],
    ) -> dict[str, float]:
        """Route les étoiles fixes par pondération explicite du ruleset."""
        raw_weights = getattr(ctx.ruleset_context, "parameters", {}).get(
            "fixed_star_category_weights"
        )
        if not isinstance(raw_weights, dict):
            return {cat: 0.0 for cat in active_categories}
        return {
            cat: self._coerce_category_weight(raw_weights.get(cat, raw_weights.get(cat.lower())))
            for cat in active_categories
        }

    def _coerce_category_weight(self, raw_value: Any) -> float:
        """Normalise une pondération de catégorie issue du JSON de ruleset."""
        try:
            weight = float(raw_value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, weight))

from app.prediction.context_loader import LoadedPredictionContext
from app.prediction.schemas import AstroEvent


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

        house_vector = self._build_house_vector(event)
        planet_blend = self._compute_planet_blend(event.body, planet_to_cat, active_categories)

        if not house_vector:
            # AC5 - events without house target (planetary hours, ingresses)
            # routing via planet blend only.
            return planet_blend

        house_projection = self._project_houses_to_categories(house_vector, house_to_cat, active_categories)

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
        natal_house = metadata.get("natal_house_target")
        transit_house = metadata.get("natal_house_transited")

        if natal_house is None:
            return {}

        if transit_house is None or transit_house == natal_house:
            return {natal_house: 1.0}

        return {natal_house: 0.70, transit_house: 0.30}

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

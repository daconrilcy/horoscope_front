from collections.abc import Mapping
from dataclasses import dataclass

from app.prediction.context_loader import LoadedPredictionContext
from app.prediction.schemas import NatalChart


@dataclass(frozen=True)
class BComponent:
    """Explaining component of B(c) for V3 (AC1, AC4)."""

    factor: str
    weight: float
    contribution: float
    description: str


@dataclass(frozen=True)
class V3NatalStructuralOutput:
    """Structure of B(c) for a specific theme (AC1, AC2)."""

    theme_code: str
    total_score: float
    components: list[BComponent]


class NatalSensitivityCalculator:
    """
    Service to calculate category sensitivity NS(c) based on natal chart.
    NS(c) = clip(
        1.0 + w_occ * Occ(c) + w_rul * Rul(c) + w_ang * Ang(c) + w_dom * Dom(c),
        0.75,
        1.25,
    )
    """

    NS_MIN = 0.75
    NS_MAX = 1.25
    ANGULAR_HOUSES = {1, 4, 7, 10}

    def compute(self, natal: NatalChart, ctx: LoadedPredictionContext) -> dict[str, float]:
        """
        Computes sensitivity for all enabled categories (V2).
        """
        params = ctx.ruleset_context.parameters
        w_occ = float(params.get("ns_weight_occ", 0.15))
        w_rul = float(params.get("ns_weight_rul", 0.10))
        w_ang = float(params.get("ns_weight_ang", 0.10))
        w_dom = float(params.get("ns_weight_dom", 0.0))

        pc = ctx.prediction_context
        results: dict[str, float] = {}

        for category in pc.categories:
            if not category.is_enabled:
                continue

            cat_code = category.code
            occ = self._compute_occ(natal, cat_code, pc)
            rul = self._compute_rul(natal, cat_code, pc)
            ang = self._compute_ang(natal, cat_code, pc)
            dom = self._compute_dom(natal, cat_code, pc) if w_dom != 0 else 0.0

            ns_val = 1.0 + (w_occ * occ) + (w_rul * rul) + (w_ang * ang) + (w_dom * dom)

            # Clip between [0.75, 1.25]
            results[cat_code] = max(self.NS_MIN, min(self.NS_MAX, ns_val))

        return results

    def compute_v3(
        self, natal: NatalChart, ctx: LoadedPredictionContext
    ) -> dict[str, V3NatalStructuralOutput]:
        """
        Computes robust structural susceptibility B(c) for all enabled themes (AC1, AC2).
        """
        params = ctx.ruleset_context.parameters
        # AC1: Extract weights from ruleset
        w_occ = float(params.get("v3_b_weight_occ", 0.15))
        w_rul = float(params.get("v3_b_weight_rul", 0.10))
        w_ang = float(params.get("v3_b_weight_ang", 0.10))
        w_asp = float(params.get("v3_b_weight_asp", 0.05))

        pc = ctx.prediction_context
        results: dict[str, V3NatalStructuralOutput] = {}

        for category in pc.categories:
            if not category.is_enabled:
                continue

            theme_code = category.code
            components = []

            # 1. Occupation (AC1)
            occ_val = self._compute_occ(natal, theme_code, pc)
            components.append(
                BComponent(
                    factor="occupation",
                    weight=w_occ,
                    contribution=occ_val * w_occ,
                    description=f"Occupation natal des maisons liées: {occ_val:.2f}",
                )
            )

            # 2. Rulership (AC1)
            rul_val = self._compute_rul(natal, theme_code, pc)
            components.append(
                BComponent(
                    factor="rulership",
                    weight=w_rul,
                    contribution=rul_val * w_rul,
                    description=f"État natal des maîtres des maisons: {rul_val:.2f}",
                )
            )

            # 3. Angularity (AC1)
            ang_val = self._compute_ang(natal, theme_code, pc)
            components.append(
                BComponent(
                    factor="angularity",
                    weight=w_ang,
                    contribution=ang_val * w_ang,
                    description=f"Angularité des significateurs thématiques: {ang_val:.2f}",
                )
            )

            # 4. Aspects (AC1)
            asp_val = self._compute_natal_aspects_contribution(natal, theme_code, pc)
            components.append(
                BComponent(
                    factor="aspects",
                    weight=w_asp,
                    contribution=asp_val * w_asp,
                    description=f"Dignité par aspects natals: {asp_val:.2f}",
                )
            )

            # AC2: Bounded and Centered
            # Formula: B = 1.0 + Σ contributions
            # Center at 1.0, typical range [0.5, 1.5]
            total_contrib = sum(c.contribution for c in components)
            total_score = 1.0 + total_contrib

            # Clip between [0.5, 1.5] for V3
            total_score = max(0.5, min(1.5, total_score))

            results[theme_code] = V3NatalStructuralOutput(
                theme_code=theme_code, total_score=total_score, components=components
            )

        return results

    def _compute_natal_aspects_contribution(
        self, natal: NatalChart, theme_code: str, pc
    ) -> float:
        """Computes contribution from natal aspects involving significators of the theme (AC1)."""
        # Find significators for this theme
        significators = {
            self._normalize_code(w.planet_code)
            for w in pc.planet_category_weights
            if w.category_code == theme_code and w.weight > 0
        }

        total = 0.0
        for aspect in natal.natal_aspects:
            if aspect.body is None or aspect.target is None or aspect.orb_deg is None:
                continue

            b1 = self._normalize_code(aspect.body)
            b2 = self._normalize_code(aspect.target)

            # If one of the bodies is a significator
            if b1 in significators or b2 in significators:
                # Any major aspect is a sign of "strength" or "focus"
                # Standardize max orb to 5.0 for this contribution logic
                orb_weight = max(0.0, 1.0 - (aspect.orb_deg / 5.0))
                
                if aspect.aspect in ("conjunction", "trine", "sextile"):
                    total += 1.0 * orb_weight
                elif aspect.aspect in ("square", "opposition"):
                    total += 0.5 * orb_weight

        return total

    def _compute_occ(self, natal: NatalChart, cat_code: str, pc) -> float:
        # Trouver les maisons associées à cette catégorie
        associated_houses = {
            w.house_number
            for w in pc.house_category_weights
            if w.category_code == cat_code and w.weight > 0
        }
        total = 0.0
        for planet_code, house_num in natal.planet_houses.items():
            if house_num in associated_houses:
                profile = self._lookup_mapping_value(pc.planet_profiles, planet_code)
                if profile:
                    total += profile.weight_day_climate
        return total

    def _compute_rul(self, natal: NatalChart, cat_code: str, pc) -> float:
        # AC4: If the ruler of the cusp sign for a linked house is angular, it contributes.
        associated_houses = {
            w.house_number
            for w in pc.house_category_weights
            if w.category_code == cat_code and w.weight > 0
        }

        total = 0.0
        for house_num in associated_houses:
            cusp_sign_or_ruler = natal.house_sign_rulers.get(house_num)
            ruler_code = self._resolve_house_ruler_code(cusp_sign_or_ruler, pc.sign_rulerships)
            if ruler_code:
                ruler_house = self._lookup_mapping_value(natal.planet_houses, ruler_code)
                if ruler_house in self.ANGULAR_HOUSES:
                    total += 1.0

        return total

    def _compute_ang(self, natal: NatalChart, cat_code: str, pc) -> float:
        planet_cat_weights = {
            self._normalize_code(w.planet_code): w.weight
            for w in pc.planet_category_weights
            if w.category_code == cat_code
        }
        total = 0.0
        for planet_code, house_num in natal.planet_houses.items():
            if house_num in self.ANGULAR_HOUSES:
                weight = planet_cat_weights.get(self._normalize_code(planet_code), 0.0)
                total += weight
        return total

    def _compute_dom(self, natal: NatalChart, cat_code: str, pc) -> float:
        # Domination optionnelle - Non implémenté en V1
        return 0.0

    def _resolve_house_ruler_code(
        self,
        cusp_sign_or_ruler: str | None,
        sign_rulerships: Mapping[str, str],
    ) -> str | None:
        if cusp_sign_or_ruler is None:
            return None

        normalized = self._normalize_code(cusp_sign_or_ruler)
        for sign_code, planet_code in sign_rulerships.items():
            if self._normalize_code(sign_code) == normalized:
                return planet_code

        return cusp_sign_or_ruler

    def _lookup_mapping_value(self, mapping: Mapping, key: str) -> object | None:
        candidates = (key, key.lower(), key.upper(), key.title())
        for candidate in candidates:
            if candidate in mapping:
                return mapping[candidate]
        return None

    def _normalize_code(self, value: str) -> str:
        return value.strip().lower()

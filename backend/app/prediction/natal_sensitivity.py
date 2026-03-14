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
    PRIMARY_ROLE_MULTIPLIER = 1.0
    SECONDARY_ROLE_MULTIPLIER = 0.6
    HOUSE_KIND_SCORES = {
        "angular": 1.0,
        "succedent": 0.2,
        "cadent": -0.5,
    }
    FAST_PLANET_CLASSES = {"luminary", "personal"}
    FAST_PLANET_SPEED_CLASSES = {"fast", "variable"}

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
            occ = self._compute_occ_legacy(natal, cat_code, pc)
            rul = self._compute_rul_legacy(natal, cat_code, pc)
            ang = self._compute_ang_legacy(natal, cat_code, pc)
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

    def _compute_natal_aspects_contribution(self, natal: NatalChart, theme_code: str, pc) -> float:
        """Computes contribution from natal aspects involving significators of the theme (AC1)."""
        significators = self._significator_weight_map(theme_code, pc)
        if not significators:
            return 0.0

        weighted_total = 0.0
        total_weight = 0.0
        for aspect in natal.natal_aspects:
            if aspect.body is None or aspect.target is None or aspect.orb_deg is None:
                continue

            b1 = self._normalize_code(aspect.body)
            b2 = self._normalize_code(aspect.target)
            involvement = significators.get(b1, 0.0) + significators.get(b2, 0.0)
            if involvement <= 0.0:
                continue

            aspect_profile = self._lookup_mapping_value(pc.aspect_profiles, aspect.aspect or "")
            orb_max = 5.0
            intensity = 1.0
            valence = self._aspect_valence(aspect.aspect or "", None)
            if aspect_profile is not None:
                orb_max *= float(getattr(aspect_profile, "orb_multiplier", 1.0) or 1.0)
                intensity = float(getattr(aspect_profile, "intensity_weight", 1.0) or 1.0)
                valence = self._aspect_valence(
                    aspect.aspect or "",
                    getattr(aspect_profile, "default_valence", None),
                )

            orb_weight = max(0.0, 1.0 - (aspect.orb_deg / orb_max))
            weighted_total += involvement * intensity * valence * orb_weight
            total_weight += involvement * intensity

        return self._normalize_component(weighted_total, total_weight)

    def _compute_occ(self, natal: NatalChart, cat_code: str, pc) -> float:
        house_weights = self._house_weight_map(cat_code, pc)
        if not house_weights:
            return 0.0

        weighted_total = 0.0
        total_weight = 0.0
        for planet_code, house_num in natal.planet_houses.items():
            house_weight = house_weights.get(house_num)
            if house_weight is None:
                continue
            profile = self._lookup_mapping_value(pc.planet_profiles, planet_code)
            if profile is None or not self._is_personal_or_rapid(profile):
                continue

            speed_factor = self._speed_factor(profile)
            climate_weight = float(getattr(profile, "weight_day_climate", 1.0) or 1.0)
            weighted_total += house_weight * speed_factor * climate_weight
            total_weight += 1.0

        return self._normalize_component(weighted_total, total_weight)

    def _compute_rul(self, natal: NatalChart, cat_code: str, pc) -> float:
        house_weights = self._house_weight_map(cat_code, pc)
        if not house_weights:
            return 0.0

        weighted_total = 0.0
        total_weight = 0.0
        for house_num, house_weight in house_weights.items():
            cusp_sign_or_ruler = natal.house_sign_rulers.get(house_num)
            ruler_code = self._resolve_house_ruler_code(cusp_sign_or_ruler, pc.sign_rulerships)
            if ruler_code is None:
                continue

            ruler_house = self._lookup_mapping_value(natal.planet_houses, ruler_code)
            placement_score = self._house_placement_score(ruler_house, pc)
            if ruler_house == house_num:
                placement_score += 0.25
            elif ruler_house in house_weights:
                placement_score += 0.1

            weighted_total += house_weight * max(-1.0, min(1.0, placement_score))
            total_weight += 1.0

        return self._normalize_component(weighted_total, total_weight)

    def _compute_ang(self, natal: NatalChart, cat_code: str, pc) -> float:
        planet_cat_weights = self._significator_weight_map(cat_code, pc)
        if not planet_cat_weights:
            return 0.0

        weighted_total = 0.0
        total_weight = 0.0
        for planet_code, house_num in natal.planet_houses.items():
            weight = planet_cat_weights.get(self._normalize_code(planet_code))
            if weight is None:
                continue
            weighted_total += weight * self._house_placement_score(house_num, pc)
            total_weight += abs(weight)
        return self._normalize_component(weighted_total, total_weight)

    def _compute_dom(self, natal: NatalChart, cat_code: str, pc) -> float:
        # Domination optionnelle - Non implémenté en V1
        return 0.0

    def _compute_occ_legacy(self, natal: NatalChart, cat_code: str, pc) -> float:
        relevant_houses = {
            house_weight.house_number
            for house_weight in pc.house_category_weights
            if house_weight.category_code == cat_code and house_weight.weight > 0
        }
        if not relevant_houses:
            return 0.0

        occ = 0.0
        for planet_code, house_num in natal.planet_houses.items():
            if house_num not in relevant_houses:
                continue
            profile = self._lookup_mapping_value(getattr(pc, "planet_profiles", {}), planet_code)
            if profile is None:
                continue
            occ += float(getattr(profile, "weight_day_climate", 1.0) or 1.0)
        return occ

    def _compute_rul_legacy(self, natal: NatalChart, cat_code: str, pc) -> float:
        relevant_houses = {
            house_weight.house_number
            for house_weight in pc.house_category_weights
            if house_weight.category_code == cat_code and house_weight.weight > 0
        }
        if not relevant_houses:
            return 0.0

        rul = 0.0
        for house_num in relevant_houses:
            cusp_sign_or_ruler = natal.house_sign_rulers.get(house_num)
            ruler_code = self._resolve_house_ruler_code(cusp_sign_or_ruler, pc.sign_rulerships)
            if ruler_code is None:
                continue
            ruler_house = self._lookup_mapping_value(natal.planet_houses, ruler_code)
            if ruler_house in self.ANGULAR_HOUSES:
                rul += 1.0
        return rul

    def _compute_ang_legacy(self, natal: NatalChart, cat_code: str, pc) -> float:
        ang = 0.0
        for planet_weight in pc.planet_category_weights:
            if planet_weight.category_code != cat_code or planet_weight.weight <= 0:
                continue
            house_num = self._lookup_mapping_value(natal.planet_houses, planet_weight.planet_code)
            if house_num in self.ANGULAR_HOUSES:
                ang += float(planet_weight.weight)
        return ang

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

    def _lookup_mapping_value(self, mapping: Mapping, key: object) -> object | None:
        if not isinstance(key, str):
            candidates = (key,)
        else:
            candidates = (key, key.lower(), key.upper(), key.title())
        for candidate in candidates:
            if candidate in mapping:
                return mapping[candidate]
        return None

    def _normalize_code(self, value: str) -> str:
        return value.strip().lower()

    def _house_weight_map(self, cat_code: str, pc) -> dict[int, float]:
        weights: dict[int, float] = {}
        for house_weight in pc.house_category_weights:
            if house_weight.category_code != cat_code or house_weight.weight <= 0:
                continue
            role_factor = self._role_multiplier(getattr(house_weight, "routing_role", None))
            weights[house_weight.house_number] = house_weight.weight * role_factor
        return weights

    def _significator_weight_map(self, cat_code: str, pc) -> dict[str, float]:
        weights: dict[str, float] = {}
        for planet_weight in pc.planet_category_weights:
            if planet_weight.category_code != cat_code or planet_weight.weight <= 0:
                continue
            role_factor = self._role_multiplier(getattr(planet_weight, "influence_role", None))
            weights[self._normalize_code(planet_weight.planet_code)] = (
                planet_weight.weight * role_factor
            )
        return weights

    def _role_multiplier(self, raw_role: str | None) -> float:
        if raw_role is None:
            return self.PRIMARY_ROLE_MULTIPLIER
        role = self._normalize_code(raw_role)
        if role == "primary":
            return self.PRIMARY_ROLE_MULTIPLIER
        if role == "secondary":
            return self.SECONDARY_ROLE_MULTIPLIER
        return self.PRIMARY_ROLE_MULTIPLIER

    def _normalize_component(self, weighted_total: float, total_weight: float) -> float:
        if total_weight <= 0.0:
            return 0.0
        normalized = weighted_total / total_weight
        return max(-1.0, min(1.0, normalized))

    def _house_placement_score(self, house_num: int | None, pc) -> float:
        if house_num is None:
            return -0.25
        house_profiles = getattr(pc, "house_profiles", {})
        house_profile = self._lookup_mapping_value(house_profiles, house_num)
        house_kind = getattr(house_profile, "house_kind", None) if house_profile else None
        if house_kind is not None:
            return self.HOUSE_KIND_SCORES.get(self._normalize_code(house_kind), 0.0)
        if house_num in self.ANGULAR_HOUSES:
            return self.HOUSE_KIND_SCORES["angular"]
        if house_num in {2, 5, 8, 11}:
            return self.HOUSE_KIND_SCORES["succedent"]
        return self.HOUSE_KIND_SCORES["cadent"]

    def _is_personal_or_rapid(self, profile: object) -> bool:
        class_code = self._normalize_code(getattr(profile, "class_code", ""))
        speed_class = self._normalize_code(getattr(profile, "speed_class", ""))
        speed_rank = getattr(profile, "speed_rank", None)
        return (
            class_code in self.FAST_PLANET_CLASSES
            or speed_class in self.FAST_PLANET_SPEED_CLASSES
            or (isinstance(speed_rank, int) and speed_rank <= 5)
        )

    def _speed_factor(self, profile: object) -> float:
        class_code = self._normalize_code(getattr(profile, "class_code", ""))
        speed_class = self._normalize_code(getattr(profile, "speed_class", ""))
        if class_code == "luminary":
            return 1.0
        if class_code == "personal":
            return 0.9
        if speed_class == "fast":
            return 0.8
        if speed_class == "variable":
            return 0.7
        return 0.0

    def _aspect_valence(self, aspect_name: str, default_valence: str | None) -> float:
        normalized_valence = self._normalize_code(default_valence or "")
        if normalized_valence == "positive":
            return 1.0
        if normalized_valence == "negative":
            return -1.0
        if normalized_valence == "neutral":
            return 0.0

        normalized_aspect = self._normalize_code(aspect_name)
        if normalized_aspect in {"trine", "sextile", "conjunction"}:
            return 1.0
        if normalized_aspect in {"square", "opposition"}:
            return -1.0
        return 0.0

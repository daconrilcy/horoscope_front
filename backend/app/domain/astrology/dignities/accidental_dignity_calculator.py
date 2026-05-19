"""Calcul des dignites accidentelles depuis les regles runtime."""

from __future__ import annotations

from app.domain.astrology.dignities.contracts import (
    AccidentalDignityMatch,
    DignityWeight,
    PlanetDignityInput,
)
from app.domain.astrology.runtime.runtime_reference import (
    AccidentalDignityRuleReferenceData,
    DignityScoreWeightReferenceData,
    PlanetDignityReferenceSet,
)


class AccidentalDignityCalculator:
    """Detecte les dignites accidentelles objectives sans dependance infra."""

    def calculate(
        self,
        planet: PlanetDignityInput,
        *,
        all_planets: tuple[PlanetDignityInput, ...],
        dignity_reference: PlanetDignityReferenceSet,
        score_profile: str,
        tradition: str,
    ) -> tuple[AccidentalDignityMatch, ...]:
        """Retourne les dignites accidentelles couvertes par la story."""
        weights = self._weights(dignity_reference, score_profile)
        matches: list[AccidentalDignityMatch] = []
        for rule in dignity_reference.accidental_rules:
            if rule.system_code != tradition:
                continue
            if rule.planet_code is not None and rule.planet_code != planet.planet_code:
                continue
            if rule.dignity_type_code not in weights:
                continue
            if self._rule_matches(rule, planet, all_planets):
                matches.append(
                    AccidentalDignityMatch(
                        dignity_type_code=rule.dignity_type_code,
                        score_value=weights[rule.dignity_type_code].score_value,
                        source=rule.condition_schema_code,
                        reason=self._reason(rule, planet),
                        condition=self._condition_label(rule),
                    )
                )
        return tuple(self._deduplicate_solar_conditions(matches))

    def _rule_matches(
        self,
        rule: AccidentalDignityRuleReferenceData,
        planet: PlanetDignityInput,
        all_planets: tuple[PlanetDignityInput, ...],
    ) -> bool:
        """Evalue les conditions accidentelles supportees."""
        conditions = {item.key: item.value for item in rule.conditions}
        if "house_codes" in conditions:
            return planet.house_number in {int(value) for value in conditions["house_codes"]}
        if "house_code" in conditions:
            return planet.house_number == int(conditions["house_code"])
        if "motion_state_code" in conditions:
            motion = str(conditions["motion_state_code"])
            return (motion == "retrograde" and planet.is_retrograde is True) or (
                motion == "direct" and planet.is_retrograde is False
            )
        if "relative_planet_code" in conditions and "angular_distance_max_deg" in conditions:
            relative_planet_code = str(conditions["relative_planet_code"])
            if relative_planet_code == planet.planet_code:
                return False
            relative = self._planet_by_code(all_planets, relative_planet_code)
            if relative is None:
                return False
            distance = self._angular_distance(planet.longitude, relative.longitude)
            min_distance = float(conditions.get("angular_distance_min_deg", 0))
            max_distance = float(conditions["angular_distance_max_deg"])
            return min_distance <= distance < max_distance
        return False

    def _deduplicate_solar_conditions(
        self, matches: list[AccidentalDignityMatch]
    ) -> tuple[AccidentalDignityMatch, ...]:
        """Conserve une seule condition solaire exclusive selon l'ordre runtime."""
        solar_types = {"cazimi", "combust", "under_sunbeams", "free_from_sunbeams"}
        selected_solar: AccidentalDignityMatch | None = None
        result: list[AccidentalDignityMatch] = []
        for match in matches:
            if match.dignity_type_code in solar_types:
                if selected_solar is None:
                    selected_solar = match
                continue
            result.append(match)
        if selected_solar is not None:
            result.append(selected_solar)
        return tuple(result)

    def _weights(
        self, dignity_reference: PlanetDignityReferenceSet, score_profile: str
    ) -> dict[str, DignityWeight]:
        """Indexe les poids accidentels du profil demande."""
        return {
            item.dignity_type_code: self._weight(item)
            for item in dignity_reference.accidental_weights[score_profile]
        }

    def _weight(self, item: DignityScoreWeightReferenceData) -> DignityWeight:
        """Convertit le poids runtime en contrat domaine."""
        return DignityWeight(
            dignity_type_code=item.dignity_type_code,
            score_value=item.score_value,
            functional_weight=item.functional_weight,
            expression_weight=item.expression_weight,
            intensity_weight=item.intensity_weight,
        )

    def _planet_by_code(
        self, planets: tuple[PlanetDignityInput, ...], planet_code: str
    ) -> PlanetDignityInput | None:
        """Retourne une planete deja calculee par son code."""
        for planet in planets:
            if planet.planet_code == planet_code:
                return planet
        return None

    def _condition_label(self, rule: AccidentalDignityRuleReferenceData) -> str:
        """Produit une etiquette technique de condition sans narration."""
        return ";".join(f"{item.key}={item.value}" for item in rule.conditions)

    def _reason(
        self,
        rule: AccidentalDignityRuleReferenceData,
        planet: PlanetDignityInput,
    ) -> str:
        """Produit une explication factuelle courte du score accidentel."""
        return (
            f"{planet.planet_code} matches {rule.dignity_type_code}: {self._condition_label(rule)}"
        )

    def _angular_distance(self, first: float, second: float) -> float:
        """Retourne la plus courte distance angulaire entre deux longitudes."""
        distance = abs((first % 360.0) - (second % 360.0))
        return min(distance, 360.0 - distance)

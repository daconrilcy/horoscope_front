"""Calcul pur des conditions de secte avancees."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from app.domain.astrology.advanced_conditions.contracts import AdvancedPlanetaryCondition
from app.domain.astrology.dignities.contracts import PlanetDignityResult
from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference


class HayzCalculator:
    """Projette les conditions de secte depuis les faits canoniques calcules."""

    def calculate(
        self,
        positions: Sequence[Any],
        dignities_by_planet: Mapping[str, PlanetDignityResult],
        runtime_reference: AstrologyRuntimeReference,
        emit_condition,
    ) -> tuple[AdvancedPlanetaryCondition, ...]:
        """Retourne hayz et hors-secte sans recalculer la doctrine de secte."""
        conditions: list[AdvancedPlanetaryCondition] = []
        for position in positions:
            dignity = dignities_by_planet.get(position.planet_code)
            if dignity is None:
                continue
            sect_condition = dignity.sect_condition
            if sect_condition is None:
                raise ValueError(
                    "PlanetSectCondition is required for sect-dependent advanced conditions: "
                    f"{position.planet_code}"
                )
            if sect_condition.is_out_of_sect:
                conditions.append(
                    emit_condition(
                        condition_code="out_of_sect",
                        condition_type_code="out_of_sect",
                        source_planet_code=position.planet_code,
                        target_planet_code=None,
                        reason=(
                            f"{position.planet_code} is out of sect according to "
                            "PlanetSectCondition."
                        ),
                    )
                )
            hayz_facts = self.hayz_component_facts(
                position,
                dignity,
                runtime_reference,
            )
            if sect_condition.is_in_sect and all(
                (
                    hayz_facts["hemisphere_match"],
                    hayz_facts["sign_gender_match"],
                )
            ):
                conditions.append(
                    emit_condition(
                        condition_code="hayz",
                        condition_type_code="hayz",
                        source_planet_code=position.planet_code,
                        target_planet_code=None,
                        reason=(
                            f"{position.planet_code} matches PlanetSectCondition and "
                            "non-sect hayz factors."
                        ),
                        calculation_facts={
                            "sect_match": True,
                            **hayz_facts,
                            "calculation_basis": "sect_hemisphere_sign_gender",
                            "reference_system": dignity.tradition,
                        },
                    )
                )
        return tuple(conditions)

    def non_sect_hayz_factors(
        self,
        position: Any,
        dignity: PlanetDignityResult,
        runtime_reference: AstrologyRuntimeReference,
    ) -> dict[str, bool]:
        """Evalue les facteurs hayz hors precondition de secte."""
        component_facts = self.hayz_component_facts(position, dignity, runtime_reference)
        return {
            "hemisphere_match": bool(component_facts["hemisphere_match"]),
            "sign_gender_match": bool(component_facts["sign_gender_match"]),
        }

    def hayz_component_facts(
        self,
        position: Any,
        dignity: PlanetDignityResult,
        runtime_reference: AstrologyRuntimeReference,
    ) -> dict[str, object]:
        """Retourne les composants explicatifs hayz sans recalculer la secte."""
        facts: dict[str, object] = {
            "hemisphere_match": False,
            "sign_gender_match": False,
            "planet_horizon_position": self._planet_horizon_position(
                position,
                runtime_reference,
                system_code=dignity.tradition,
            ),
            "sign_gender": self._sign_gender(position, runtime_reference),
        }
        for rule in runtime_reference.dignity_reference.accidental_rules:
            if rule.system_code != dignity.tradition:
                continue
            if rule.dignity_type_code != "hayz":
                continue
            if rule.planet_code is not None and rule.planet_code != position.planet_code:
                continue
            conditions = {item.key: item.value for item in rule.conditions}
            candidate_facts: dict[str, object] = {
                **facts,
                "hemisphere_match": (
                    "horizon_position_code" not in conditions
                    or self._horizon_matches(
                        str(conditions["horizon_position_code"]),
                        position,
                        runtime_reference,
                        system_code=rule.system_code,
                    )
                ),
                "sign_gender_match": (
                    "sign_gender_code" not in conditions
                    or self._sign_gender_matches(
                        str(conditions["sign_gender_code"]),
                        position,
                        runtime_reference,
                    )
                ),
            }
            if bool(candidate_facts["hemisphere_match"]) and bool(
                candidate_facts["sign_gender_match"]
            ):
                return candidate_facts
            facts = candidate_facts
        return facts

    def _horizon_matches(
        self,
        horizon_code: str,
        position: Any,
        runtime_reference: AstrologyRuntimeReference,
        *,
        system_code: str,
    ) -> bool:
        """Verifie l'hemisphere hayz depuis les regles runtime d'horizon."""
        dignity_type_code = f"{horizon_code}_horizon"
        for rule in runtime_reference.dignity_reference.accidental_rules:
            if rule.system_code != system_code:
                continue
            if rule.dignity_type_code != dignity_type_code:
                continue
            for condition in rule.conditions:
                if condition.key == "house_codes" and isinstance(condition.value, tuple):
                    return position.house_number in {int(value) for value in condition.value}
            raise ValueError(f"missing house_codes for horizon dignity rule: {dignity_type_code}")
        return False

    def _sign_gender_matches(
        self,
        sign_gender_code: str,
        position: Any,
        runtime_reference: AstrologyRuntimeReference,
    ) -> bool:
        """Verifie la polarite du signe requise par les facteurs hayz."""
        polarity_by_sign = {item.code: item.polarity for item in runtime_reference.signs.items}
        expected_polarity = {"masculine": "yang", "feminine": "yin"}.get(sign_gender_code)
        return (
            expected_polarity is not None
            and polarity_by_sign.get(position.sign_code) == expected_polarity
        )

    def _planet_horizon_position(
        self,
        position: Any,
        runtime_reference: AstrologyRuntimeReference,
        *,
        system_code: str,
    ) -> str:
        """Resolve l'hemisphere de la planete depuis les regles runtime d'horizon."""
        for horizon_code in ("above", "below"):
            if self._horizon_matches(
                horizon_code,
                position,
                runtime_reference,
                system_code=system_code,
            ):
                return f"{horizon_code}_horizon"
        return "unknown"

    def _sign_gender(self, position: Any, runtime_reference: AstrologyRuntimeReference) -> str:
        """Traduit la polarite runtime du signe en genre traditionnel public."""
        sign_code = getattr(position, "sign_code", None)
        if sign_code is None:
            return "unknown"
        polarity_by_sign = {item.code: item.polarity for item in runtime_reference.signs.items}
        return {
            "yang": "masculine",
            "yin": "feminine",
            "neutral": "neutral",
        }.get(str(polarity_by_sign.get(sign_code, "")), "unknown")

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
            if sect_condition.is_in_sect and self._non_sect_hayz_factors_match(
                position,
                dignity,
                runtime_reference,
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
                    )
                )
        return tuple(conditions)

    def _non_sect_hayz_factors_match(
        self,
        position: Any,
        dignity: PlanetDignityResult,
        runtime_reference: AstrologyRuntimeReference,
    ) -> bool:
        """Evalue les facteurs hayz hors precondition de secte."""
        for rule in runtime_reference.dignity_reference.accidental_rules:
            if rule.system_code != dignity.tradition:
                continue
            if rule.dignity_type_code != "hayz":
                continue
            if rule.planet_code is not None and rule.planet_code != position.planet_code:
                continue
            conditions = {item.key: item.value for item in rule.conditions}
            if "horizon_position_code" in conditions and not self._horizon_matches(
                str(conditions["horizon_position_code"]),
                position,
                runtime_reference,
                system_code=rule.system_code,
            ):
                continue
            if "sign_gender_code" in conditions and not self._sign_gender_matches(
                str(conditions["sign_gender_code"]),
                position,
                runtime_reference,
            ):
                continue
            return True
        return False

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

"""Calcul pur des receptions mutuelles planetaires."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from app.domain.astrology.advanced_conditions.contracts import AdvancedPlanetaryCondition
from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference


class MutualReceptionCalculator:
    """Detecte les receptions mutuelles par domicile ou exaltation runtime."""

    def calculate(
        self,
        positions: Sequence[Any],
        runtime_reference: AstrologyRuntimeReference,
        emit_condition,
    ) -> tuple[AdvancedPlanetaryCondition, ...]:
        """Retourne les receptions mutuelles detectees entre planetes."""
        domicile = dict(runtime_reference.dignities.sign_rulerships)
        exaltation = {
            rule.sign_code: rule.planet_code
            for rule in runtime_reference.dignity_reference.essential_rules
            if rule.dignity_type_code == "exaltation"
        }
        conditions: list[AdvancedPlanetaryCondition] = []
        for source in positions:
            for target in positions:
                if source.planet_code >= target.planet_code:
                    continue
                for code, rulers in (
                    ("mutual_reception_by_domicile", domicile),
                    ("mutual_reception_by_exaltation", exaltation),
                ):
                    if (
                        rulers.get(source.sign_code) == target.planet_code
                        and rulers.get(target.sign_code) == source.planet_code
                    ):
                        conditions.extend(
                            (
                                emit_condition(
                                    condition_code=code,
                                    condition_type_code="mutual_reception",
                                    source_planet_code=source.planet_code,
                                    target_planet_code=target.planet_code,
                                    reason=(
                                        f"{source.planet_code} and {target.planet_code} "
                                        f"exchange {code.removeprefix('mutual_reception_by_')}."
                                    ),
                                ),
                                emit_condition(
                                    condition_code=code,
                                    condition_type_code="mutual_reception",
                                    source_planet_code=target.planet_code,
                                    target_planet_code=source.planet_code,
                                    reason=(
                                        f"{target.planet_code} and {source.planet_code} "
                                        f"exchange {code.removeprefix('mutual_reception_by_')}."
                                    ),
                                ),
                            )
                        )
        return tuple(conditions)

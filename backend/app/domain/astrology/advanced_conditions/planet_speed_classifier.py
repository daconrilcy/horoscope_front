"""Classification pure des conditions de vitesse planetaire."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from app.domain.astrology.advanced_conditions._dignity_rule_helpers import accidental_matches
from app.domain.astrology.advanced_conditions.contracts import AdvancedPlanetaryCondition
from app.domain.astrology.dignities.contracts import PlanetDignityResult


class PlanetSpeedClassifier:
    """Traduit les dignites accidentelles de mouvement en conditions avancees."""

    def calculate(
        self,
        positions: Sequence[Any],
        dignities_by_planet: Mapping[str, PlanetDignityResult],
        emit_condition,
    ) -> tuple[AdvancedPlanetaryCondition, ...]:
        """Retourne les conditions de vitesse V1."""
        conditions: list[AdvancedPlanetaryCondition] = []
        for position in positions:
            dignity = dignities_by_planet.get(position.planet_code)
            for code in accidental_matches(
                dignity,
                frozenset({"stationary", "stationary_direct", "stationary_retrograde"}),
            ):
                emitted_code = (
                    "stationary_retrograde" if position.is_retrograde else "stationary_direct"
                )
                conditions.append(
                    emit_condition(
                        condition_code=emitted_code if code == "stationary" else code,
                        condition_type_code="stationary",
                        source_planet_code=position.planet_code,
                        target_planet_code=None,
                        reason=f"{position.planet_code} matches stationary motion.",
                    )
                )
            for code in accidental_matches(dignity, frozenset({"swift_motion", "slow_motion"})):
                emitted_code = "fast_motion" if code == "swift_motion" else code
                conditions.append(
                    emit_condition(
                        condition_code=emitted_code,
                        condition_type_code=emitted_code,
                        source_planet_code=position.planet_code,
                        target_planet_code=None,
                        reason=f"{position.planet_code} matches {code}.",
                    )
                )
        return tuple(conditions)

"""Calcul de secte diurne ou nocturne pour les dignites accidentelles."""

from __future__ import annotations

from collections.abc import Iterable

from app.domain.astrology.dignities.contracts import ChartSectResult, PlanetDignityInput
from app.domain.astrology.runtime.runtime_reference import PlanetDignityReferenceSet

_SECT_CALCULATION_BASIS = "sun_house_horizon_rule"


class SectCalculator:
    """Determine la secte du theme depuis la position objective du Soleil."""

    def calculate(
        self,
        planets: Iterable[PlanetDignityInput],
        dignity_reference: PlanetDignityReferenceSet,
    ) -> ChartSectResult:
        """Retourne le contrat de secte depuis les regles horizon du runtime."""
        above_horizon_houses, above_reference_system = self._houses_for_rule(
            dignity_reference, "above_horizon"
        )
        below_horizon_houses, below_reference_system = self._houses_for_rule(
            dignity_reference, "below_horizon"
        )
        if above_reference_system != below_reference_system:
            raise ValueError("horizon dignity rules must share the same reference system")
        for planet in planets:
            if planet.planet_code == "sun":
                if planet.house_number in above_horizon_houses:
                    return ChartSectResult(
                        chart_sect="day",
                        sun_horizon_position="above_horizon",
                        sun_above_horizon=True,
                        calculation_basis=_SECT_CALCULATION_BASIS,
                        reference_system=above_reference_system,
                    )
                if planet.house_number in below_horizon_houses:
                    return ChartSectResult(
                        chart_sect="night",
                        sun_horizon_position="below_horizon",
                        sun_above_horizon=False,
                        calculation_basis=_SECT_CALCULATION_BASIS,
                        reference_system=below_reference_system,
                    )
                raise ValueError("sun house is outside configured horizon dignity rules")
        raise ValueError("sect calculation requires sun position")

    def _houses_for_rule(
        self,
        dignity_reference: PlanetDignityReferenceSet,
        dignity_type_code: str,
    ) -> tuple[frozenset[int], str]:
        """Extrait les maisons d'horizon depuis les conditions runtime."""
        for rule in dignity_reference.accidental_rules:
            if rule.dignity_type_code != dignity_type_code:
                continue
            for condition in rule.conditions:
                if condition.key == "house_codes" and isinstance(condition.value, tuple):
                    houses = frozenset(int(value) for value in condition.value)
                    if not houses:
                        raise ValueError(f"empty horizon dignity rule: {dignity_type_code}")
                    if not rule.system_code.strip():
                        raise ValueError(
                            f"missing horizon rule reference system: {dignity_type_code}"
                        )
                    return houses, rule.system_code
        raise ValueError(f"missing horizon dignity rule: {dignity_type_code}")

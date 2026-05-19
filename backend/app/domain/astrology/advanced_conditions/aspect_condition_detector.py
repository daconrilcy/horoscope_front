"""Detection pure des conditions avancees liees aux aspects."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from app.domain.astrology.advanced_conditions._dignity_rule_helpers import accidental_matches
from app.domain.astrology.advanced_conditions.contracts import AdvancedPlanetaryCondition
from app.domain.astrology.dignities.contracts import PlanetDignityResult
from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference


class AspectConditionDetector:
    """Detecte bonification, maltreatment et besiegement depuis les faits natals."""

    def calculate(
        self,
        positions: Sequence[Any],
        aspects: Sequence[Any],
        dignities_by_planet: Mapping[str, PlanetDignityResult],
        runtime_reference: AstrologyRuntimeReference,
        emit_condition,
        *,
        condition_type_codes: frozenset[str] | None = None,
    ) -> tuple[AdvancedPlanetaryCondition, ...]:
        """Retourne les conditions aspectuelles V1."""
        conditions: list[AdvancedPlanetaryCondition] = []
        for position in positions:
            dignity = dignities_by_planet.get(position.planet_code)
            dignity_codes = accidental_matches(
                dignity,
                frozenset(
                    {
                        "benefic_aspected",
                        "malefic_aspected",
                        "besieged_by_benefics",
                        "besieged_by_malefics",
                    }
                ),
            )
            for code in dignity_codes:
                condition_code, condition_type_code = self._condition_codes(code)
                conditions.append(
                    emit_condition(
                        condition_code=condition_code,
                        condition_type_code=condition_type_code,
                        source_planet_code=position.planet_code,
                        target_planet_code=self._aspect_partner_for_condition(
                            position.planet_code, code, aspects, runtime_reference
                        ),
                        reason=f"{position.planet_code} matches aspect condition {code}.",
                    )
                )
            if dignity_codes:
                continue
            conditions.extend(
                self._conditions_from_aspects(
                    position.planet_code,
                    aspects,
                    runtime_reference,
                    emit_condition,
                    condition_type_codes or frozenset(),
                )
            )
        return tuple(conditions)

    def _condition_codes(self, dignity_type_code: str) -> tuple[str, str]:
        """Convertit un type accidentel gouverne en code avance public."""
        if dignity_type_code in {"benefic_aspected", "besieged_by_benefics"}:
            return ("bonification", "bonification")
        if dignity_type_code == "besieged_by_malefics":
            return ("besiegement", "besiegement")
        return ("maltreatment", "maltreatment")

    def _aspect_partner_for_condition(
        self,
        planet_code: str,
        dignity_type_code: str,
        aspects: Sequence[Any],
        runtime_reference: AstrologyRuntimeReference,
    ) -> str | None:
        """Retourne un partenaire compatible avec la condition aspectuelle."""
        expected_nature = self._expected_partner_nature(dignity_type_code)
        for aspect in aspects:
            if (
                aspect.planet_a == planet_code
                and runtime_reference.planet_natures.nature_for_planet(aspect.planet_b)
                == expected_nature
            ):
                return aspect.planet_b
            if (
                aspect.planet_b == planet_code
                and runtime_reference.planet_natures.nature_for_planet(aspect.planet_a)
                == expected_nature
            ):
                return aspect.planet_a
        return None

    def _conditions_from_aspects(
        self,
        planet_code: str,
        aspects: Sequence[Any],
        runtime_reference: AstrologyRuntimeReference,
        emit_condition,
        condition_type_codes: frozenset[str],
    ) -> tuple[AdvancedPlanetaryCondition, ...]:
        """Produit les conditions aspectuelles directement depuis les aspects natals."""
        conditions: list[AdvancedPlanetaryCondition] = []
        for aspect in aspects:
            partner = self._partner(planet_code, aspect)
            if partner is None:
                continue
            nature = runtime_reference.planet_natures.nature_for_planet(partner)
            condition_code = self._condition_for_partner_nature(nature)
            if condition_code is None or condition_code not in condition_type_codes:
                continue
            conditions.append(
                emit_condition(
                    condition_code=condition_code,
                    condition_type_code=condition_code,
                    source_planet_code=planet_code,
                    target_planet_code=partner,
                    reason=f"{planet_code} receives {condition_code} from {partner}.",
                )
            )
        return tuple(conditions)

    def _partner(self, planet_code: str, aspect: Any) -> str | None:
        """Retourne l'autre planete d'un aspect si elle existe."""
        if aspect.planet_a == planet_code:
            return aspect.planet_b
        if aspect.planet_b == planet_code:
            return aspect.planet_a
        return None

    def _expected_partner_nature(self, dignity_type_code: str) -> str:
        """Derive la nature attendue depuis le code de dignite accidentelle."""
        if "benefic" in dignity_type_code:
            return "benefic"
        return "malefic"

    def _condition_for_partner_nature(self, nature: str | None) -> str | None:
        """Derive la condition avancee depuis la nature planetaire."""
        if nature == "benefic":
            return "bonification"
        if nature == "malefic":
            return "maltreatment"
        return None

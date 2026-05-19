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
                    positions,
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
        positions: Sequence[Any],
        aspects: Sequence[Any],
        runtime_reference: AstrologyRuntimeReference,
        emit_condition,
        condition_type_codes: frozenset[str],
    ) -> tuple[AdvancedPlanetaryCondition, ...]:
        """Produit les conditions aspectuelles directement depuis les aspects natals."""
        conditions: list[AdvancedPlanetaryCondition] = []
        besiegement = self._besiegement_condition(
            planet_code,
            positions,
            runtime_reference,
            emit_condition,
            condition_type_codes,
        )
        if besiegement is not None:
            conditions.append(besiegement)
        for aspect in aspects:
            if not self._aspect_is_configured(aspect):
                continue
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

    def _besiegement_condition(
        self,
        planet_code: str,
        positions: Sequence[Any],
        runtime_reference: AstrologyRuntimeReference,
        emit_condition,
        condition_type_codes: frozenset[str],
    ) -> AdvancedPlanetaryCondition | None:
        """Detecte l'encadrement longitudinal par deux malefiques runtime."""
        if "besiegement" not in condition_type_codes:
            return None
        position = self._position(planet_code, positions)
        if position is None:
            return None
        malefics = tuple(
            item
            for item in positions
            if item.planet_code != planet_code
            and runtime_reference.planet_natures.nature_for_planet(item.planet_code) == "malefic"
        )
        for first_index, first in enumerate(malefics):
            for second in malefics[first_index + 1 :]:
                if self._between_short_arc(
                    position.longitude,
                    first.longitude,
                    second.longitude,
                ):
                    return emit_condition(
                        condition_code="besiegement",
                        condition_type_code="besiegement",
                        source_planet_code=planet_code,
                        target_planet_code=f"{first.planet_code},{second.planet_code}",
                        reason=(
                            f"{planet_code} is longitudinally enclosed by "
                            f"{first.planet_code} and {second.planet_code}."
                        ),
                    )
        return None

    def _partner(self, planet_code: str, aspect: Any) -> str | None:
        """Retourne l'autre planete d'un aspect si elle existe."""
        if aspect.planet_a == planet_code:
            return aspect.planet_b
        if aspect.planet_b == planet_code:
            return aspect.planet_a
        return None

    def _position(self, planet_code: str, positions: Sequence[Any]) -> Any | None:
        """Retourne une position planetaire par code."""
        for position in positions:
            if position.planet_code == planet_code:
                return position
        return None

    def _aspect_is_configured(self, aspect: Any) -> bool:
        """Verifie que l'aspect a deja passe les orbes runtime configurees."""
        orb_used = getattr(aspect, "orb_used", None)
        orb_max = getattr(aspect, "orb_max", None)
        if orb_used is None or orb_max is None:
            return False
        return float(orb_used) <= float(orb_max)

    def _between_short_arc(self, target: float, first: float, second: float) -> bool:
        """Indique si une longitude tombe entre deux bornes sur leur arc court."""
        direct_arc = (second - first) % 360.0
        if direct_arc == 0.0:
            return False
        if direct_arc <= 180.0:
            return 0.0 < ((target - first) % 360.0) < direct_arc
        reverse_arc = 360.0 - direct_arc
        return 0.0 < ((target - second) % 360.0) < reverse_arc

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

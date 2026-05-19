"""Calcul des dignites essentielles depuis le referentiel runtime."""

from __future__ import annotations

from app.domain.astrology.dignities.contracts import (
    DignityWeight,
    EssentialDignityMatch,
    PlanetDignityInput,
)
from app.domain.astrology.runtime.runtime_reference import (
    DignityScoreWeightReferenceData,
    PlanetDignityReferenceSet,
    SignReferenceSet,
)


class EssentialDignityCalculator:
    """Detecte les dignites essentielles sans acces DB ni scoring local."""

    def calculate(
        self,
        planet: PlanetDignityInput,
        *,
        signs: SignReferenceSet,
        dignity_reference: PlanetDignityReferenceSet,
        score_profile: str,
        sect: str,
        tradition: str,
    ) -> tuple[EssentialDignityMatch, ...]:
        """Retourne les dignites essentielles applicables a une planete."""
        weights = self._weights(dignity_reference, score_profile)
        matches: list[EssentialDignityMatch] = []
        degree = planet.degree_in_sign
        for rule in dignity_reference.essential_rules:
            if (
                rule.system_code == tradition
                and rule.planet_code == planet.planet_code
                and rule.sign_code == planet.sign_code
                and self._contains(degree, rule.degree_start, rule.degree_end)
            ):
                matches.append(
                    self._match(
                        rule.dignity_type_code,
                        weights,
                        "essential_rule",
                        f"{planet.planet_code} in {planet.sign_code}: {rule.dignity_type_code}",
                        planet.sign_code,
                        rule.degree_start,
                        rule.degree_end,
                    )
                )
        sign = next(item for item in signs.items if item.code == planet.sign_code)
        for ruler in dignity_reference.triplicity_rulers:
            if (
                ruler.system_code == tradition
                and ruler.element_code == sign.element
                and ruler.planet_code == planet.planet_code
                and ruler.sect_code in {sect, "all"}
            ):
                matches.append(
                    self._match(
                        "triplicity",
                        weights,
                        "triplicity",
                        f"{planet.planet_code} rules {sign.element} triplicity for {sect} sect",
                        planet.sign_code,
                        0,
                        30,
                    )
                )
        for bound in dignity_reference.term_bounds:
            if (
                bound.sign_code == planet.sign_code
                and bound.planet_code == planet.planet_code
                and self._contains(degree, bound.degree_start, bound.degree_end)
            ):
                matches.append(
                    self._match(
                        "term",
                        weights,
                        "term_bound",
                        f"{planet.planet_code} rules the configured term in {planet.sign_code}",
                        planet.sign_code,
                        bound.degree_start,
                        bound.degree_end,
                    )
                )
        for decan in dignity_reference.face_decans:
            if (
                decan.sign_code == planet.sign_code
                and decan.planet_code == planet.planet_code
                and self._contains(degree, decan.degree_start, decan.degree_end)
            ):
                matches.append(
                    self._match(
                        "face",
                        weights,
                        "face_decan",
                        (
                            f"{planet.planet_code} rules decan {decan.decan_index} "
                            f"in {planet.sign_code}"
                        ),
                        planet.sign_code,
                        decan.degree_start,
                        decan.degree_end,
                    )
                )
        if not self._has_positive_essential_match(matches):
            matches.append(
                self._match(
                    "peregrine",
                    weights,
                    "no_positive_essential_match",
                    f"{planet.planet_code} has no positive essential dignity in {planet.sign_code}",
                    planet.sign_code,
                    0,
                    30,
                )
            )
        return tuple(matches)

    def _weights(
        self, dignity_reference: PlanetDignityReferenceSet, score_profile: str
    ) -> dict[str, DignityWeight]:
        """Indexe les poids du profil demande."""
        return {
            item.dignity_type_code: self._weight(item)
            for item in dignity_reference.essential_weights[score_profile]
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

    def _match(
        self,
        dignity_type_code: str,
        weights: dict[str, DignityWeight],
        source: str,
        reason: str,
        sign_code: str,
        degree_start: float,
        degree_end: float,
    ) -> EssentialDignityMatch:
        """Construit un match score depuis le profil runtime."""
        weight = weights[dignity_type_code]
        return EssentialDignityMatch(
            dignity_type_code=dignity_type_code,
            score_value=weight.score_value,
            source=source,
            reason=reason,
            sign_code=sign_code,
            degree_start=degree_start,
            degree_end=degree_end,
        )

    def _has_positive_essential_match(self, matches: list[EssentialDignityMatch]) -> bool:
        """Verifie si au moins une dignite essentielle positive est detectee."""
        return any(match.score_value > 0 for match in matches)

    def _contains(self, degree: float, start: float, end: float) -> bool:
        """Teste une plage de degres semi-ouverte."""
        return start <= degree < end or (degree == 30 and end == 30)

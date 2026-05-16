"""Assemblage runtime des signes natals.

Le builder derive les signes depuis les placements et le referentiel runtime,
sans recreer le vocabulaire zodiacal localement.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from app.domain.astrology.celestial_runtime_catalog import CelestialRuntimeCatalog
from app.domain.astrology.runtime.runtime_reference import (
    DignityReferenceSet,
    SignReferenceData,
    SignReferenceSet,
)
from app.domain.astrology.runtime.sign_runtime_data import (
    SignDignityRuntimeData,
    SignDominanceReason,
    SignOccupantRuntimeData,
    SignRuntimeData,
)


class PlanetSignRuntimeData(Protocol):
    """Contrat minimal d'un placement planetaire pour le runtime signe."""

    planet_code: str
    longitude: float
    sign_code: str
    house_number: int


def build_sign_runtime_data(
    *,
    signs: SignReferenceSet,
    planets: Iterable[PlanetSignRuntimeData],
    dignities: DignityReferenceSet,
    celestial_catalog: CelestialRuntimeCatalog | None = None,
) -> list[SignRuntimeData]:
    """Construit les douze signes runtime dans l'ordre du referentiel."""
    catalog = celestial_catalog or CelestialRuntimeCatalog.empty()
    ordered_signs = tuple(signs.items)
    occupants_by_sign = {sign.code: [] for sign in ordered_signs}
    for planet in planets:
        occupant = SignOccupantRuntimeData(
            planet=planet.planet_code,
            longitude=planet.longitude,
            house=planet.house_number,
        )
        occupants_by_sign.setdefault(planet.sign_code, []).append(occupant)

    max_occupants = max((len(items) for items in occupants_by_sign.values()), default=0)
    runtime_signs: list[SignRuntimeData] = []
    for sign in ordered_signs:
        occupants = tuple(occupants_by_sign.get(sign.code, ()))
        active_dignities = _active_dignities(sign.code, occupants, dignities)
        reasons = _dominance_reasons(
            occupants=occupants,
            active_dignities=active_dignities,
            celestial_catalog=catalog,
            sign=sign,
        )
        weight = _normalized_weight(
            occupants=occupants,
            active_dignities=active_dignities,
            max_occupants=max_occupants,
            celestial_catalog=catalog,
        )
        runtime_signs.append(
            SignRuntimeData(
                sign=sign.code,
                occupants=occupants,
                weight=weight,
                dominant=weight >= 0.6,
                active_dignities=active_dignities,
                reasons=reasons,
                synthesis_role=_synthesis_role(weight, occupants),
                element=sign.element,
                modality=sign.modality,
                polarity=sign.polarity,
            )
        )
    return runtime_signs


def _active_dignities(
    sign_code: str,
    occupants: tuple[SignOccupantRuntimeData, ...],
    dignities: DignityReferenceSet,
) -> tuple[SignDignityRuntimeData, ...]:
    """Filtre les dignites du referentiel actives par les occupants."""
    occupant_codes = {occupant.planet for occupant in occupants}
    return tuple(
        SignDignityRuntimeData(
            planet=item.planet_code,
            dignity_type=item.dignity_type,
            system=item.system,
            weight=item.weight,
            is_primary=item.is_primary,
        )
        for item in dignities.items
        if item.sign_code == sign_code and item.planet_code in occupant_codes
    )


def _dominance_reasons(
    *,
    occupants: tuple[SignOccupantRuntimeData, ...],
    active_dignities: tuple[SignDignityRuntimeData, ...],
    celestial_catalog: CelestialRuntimeCatalog,
    sign: SignReferenceData,
) -> tuple[SignDominanceReason, ...]:
    """Enumere les facteurs structurels contribuant au poids du signe."""
    reasons: list[SignDominanceReason] = []
    if occupants:
        reasons.append(SignDominanceReason.OCCUPANTS_PRESENT)
    if len(occupants) >= 3:
        reasons.append(SignDominanceReason.STELLIUM_PRESENT)
    if any(celestial_catalog.is_luminary(occupant.planet) for occupant in occupants):
        reasons.append(SignDominanceReason.LUMINARY_PRESENT)
    if active_dignities:
        reasons.append(SignDominanceReason.ACTIVE_DIGNITY)
    if sign.element is not None or sign.modality is not None or sign.polarity is not None:
        reasons.append(SignDominanceReason.REFERENCE_PROFILE)
    return tuple(reasons)


def _normalized_weight(
    *,
    occupants: tuple[SignOccupantRuntimeData, ...],
    active_dignities: tuple[SignDignityRuntimeData, ...],
    max_occupants: int,
    celestial_catalog: CelestialRuntimeCatalog,
) -> float:
    """Calcule un poids astrologique borne depuis les faits runtime."""
    score = 0.0
    if max_occupants:
        score += 0.45 * (len(occupants) / max_occupants)
    if len(occupants) >= 3:
        score += 0.2
    if any(celestial_catalog.is_luminary(occupant.planet) for occupant in occupants):
        score += 0.2
    if active_dignities:
        score += min(0.15, sum(abs(item.weight) for item in active_dignities) * 0.05)
    return round(min(score, 1.0), 4)


def _synthesis_role(
    weight: float,
    occupants: tuple[SignOccupantRuntimeData, ...],
) -> str | None:
    """Retourne un role synthetique court sans narration editoriale."""
    if not occupants:
        return None
    if weight >= 0.6:
        return "dominant_focus"
    return "active_support"

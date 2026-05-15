"""Mapping infra vers contrats runtime astrologiques.

Ce module confine les payloads SQL/JSON a la couche infra et retourne au domaine
une photographie immutable du referentiel astrologique.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.domain.astrology.runtime.runtime_reference import (
    AnglePointReferenceData,
    AnglePointReferenceSet,
    AspectOrbRuleReferenceData,
    AspectReferenceData,
    AspectReferenceSet,
    AstrologyRuntimeReference,
    AstrologySystemReferenceData,
    AstrologySystemReferenceSet,
    DignityReferenceData,
    DignityReferenceSet,
    HouseAxisReferenceData,
    HouseReferenceData,
    HouseReferenceSet,
    HouseSystemReferenceData,
    HouseSystemReferenceSet,
    PlanetReferenceData,
    PlanetReferenceSet,
    SignReferenceData,
    SignReferenceSet,
)


class AstrologyRuntimeReferenceMapper:
    """Convertit les donnees chargees par l'infra en contrats immutables."""

    def map_payload(
        self,
        *,
        reference_version_id: int,
        reference_version: str,
        payload: Mapping[str, object],
        dignities: Sequence[Mapping[str, object]],
        sign_rulerships: Mapping[str, str],
        planet_definitions: Mapping[str, Mapping[str, object]],
        angle_points: Sequence[Mapping[str, object]],
        house_systems: Sequence[Mapping[str, object]],
    ) -> AstrologyRuntimeReference:
        """Retourne la photographie runtime complete attendue par le domaine."""
        return AstrologyRuntimeReference(
            reference_version_id=reference_version_id,
            reference_version=reference_version,
            planets=PlanetReferenceSet(
                tuple(
                    PlanetReferenceData(
                        code=str(item["code"]),
                        name=str(item["name"]),
                        swe_id=int(item["swe_id"]),
                        body_class=self._optional_str(
                            planet_definitions.get(str(item["code"]), {}).get("body_class")
                        ),
                        is_luminary=bool(
                            planet_definitions.get(str(item["code"]), {}).get("is_luminary")
                        ),
                    )
                    for item in self._items(payload, "planets")
                )
            ),
            signs=SignReferenceSet(
                tuple(
                    SignReferenceData(code=str(item["code"]), name=str(item["name"]))
                    for item in self._items(payload, "signs")
                )
            ),
            houses=HouseReferenceSet(
                tuple(
                    HouseReferenceData(number=int(item["number"]), name=str(item["name"]))
                    for item in self._items(payload, "houses")
                )
            ),
            house_axes=tuple(
                HouseAxisReferenceData(
                    house_number=int(item["house_number"]),
                    opposite_house=int(item["opposite_house"]),
                    theme=str(item["theme"]),
                )
                for item in self._items(payload, "house_axes")
            ),
            aspects=AspectReferenceSet(
                items=tuple(
                    AspectReferenceData(
                        code=str(item["code"]),
                        name=str(item["name"]),
                        angle=float(item["angle"]),
                        family=str(item["family"]),
                        is_enabled=bool(item["is_enabled"]),
                        is_major=bool(item["is_major"]),
                        is_minor=bool(item["is_minor"]),
                        default_orb_deg=self._optional_float(item.get("default_orb_deg")),
                        default_valence=str(item["default_valence"]),
                        interpretive_valence=str(item["interpretive_valence"]),
                        energy_type=str(item["energy_type"]),
                        legacy_orb_fields=self._legacy_orb_fields(item),
                    )
                    for item in self._items(payload, "aspects")
                ),
                orb_rules=tuple(
                    AspectOrbRuleReferenceData(
                        aspect_code=str(item["aspect_code"]),
                        system_code=str(item["system_code"]),
                        calculation_context=str(item["calculation_context"]),
                        source_body_type=str(item["source_body_type"]),
                        source_planet_code=self._optional_str(item.get("source_planet_code")),
                        source_point_code=self._optional_str(item.get("source_point_code")),
                        target_body_type=str(item["target_body_type"]),
                        target_planet_code=self._optional_str(item.get("target_planet_code")),
                        target_point_code=self._optional_str(item.get("target_point_code")),
                        orb_deg=float(item["orb_deg"]),
                        priority=int(item["priority"]),
                        is_enabled=bool(item["is_enabled"]),
                    )
                    for item in self._items(payload, "aspect_orb_rules")
                ),
            ),
            dignities=DignityReferenceSet(
                items=tuple(
                    DignityReferenceData(
                        sign_code=str(item["sign_code"]),
                        planet_code=str(item["planet_code"]),
                        dignity_type=str(item["dignity_type"]),
                        system=str(item["system"]),
                        weight=float(item["weight"]),
                        is_primary=bool(item["is_primary"]),
                    )
                    for item in dignities
                ),
                sign_rulerships={str(key): str(value) for key, value in sign_rulerships.items()},
            ),
            angle_points=AnglePointReferenceSet(
                tuple(
                    AnglePointReferenceData(
                        code=str(item["code"]),
                        short_label=str(item["short_label"]),
                        full_name=str(item["full_name"]),
                        axis=str(item["axis"]),
                        associated_house=int(item["associated_house"]),
                    )
                    for item in angle_points
                )
            ),
            house_systems=HouseSystemReferenceSet(
                tuple(
                    HouseSystemReferenceData(
                        code=str(item["code"]),
                        name=str(item["name"]),
                        is_active=bool(item["is_active"]),
                    )
                    for item in house_systems
                )
            ),
            systems=AstrologySystemReferenceSet(
                tuple(
                    AstrologySystemReferenceData(
                        code=str(item["code"]),
                        inherits_from_system_code=self._optional_str(
                            item.get("inherits_from_system_code")
                        ),
                    )
                    for item in self._items(payload, "astral_systems")
                )
            ),
        )

    def _items(self, payload: Mapping[str, object], key: str) -> tuple[Mapping[str, object], ...]:
        """Extrait une liste de mappings du payload infra."""
        raw = payload.get(key)
        if not isinstance(raw, list):
            return ()
        return tuple(item for item in raw if isinstance(item, Mapping))

    def _optional_str(self, value: object) -> str | None:
        """Convertit une valeur optionnelle en chaine normalisee."""
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _optional_float(self, value: object) -> float | None:
        """Convertit une valeur optionnelle en flottant."""
        if value is None:
            return None
        return float(value)

    def _legacy_orb_fields(self, item: Mapping[str, object]) -> tuple[str, ...]:
        """Liste les anciens champs d'orbe interdits encore presents."""
        forbidden_fields = {
            "orb_" + "luminaries_override_deg",
            "orb_" + "pair_overrides",
            "orb_" + "luminaries",
            "orb_" + "pairs",
            "orb_" + "overrides",
        }
        return tuple(sorted(forbidden_fields & set(item)))

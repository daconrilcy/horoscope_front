"""Mapping infra vers contrats runtime astrologiques.

Ce module confine les payloads SQL/JSON a la couche infra et retourne au domaine
une photographie immutable du referentiel astrologique.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.domain.astrology.planet_catalog import planet_swe_ids_by_code
from app.domain.astrology.runtime.runtime_reference import (
    AnglePointReferenceData,
    AnglePointReferenceSet,
    AspectOrbRuleReferenceData,
    AspectReferenceData,
    AspectReferenceSet,
    AstralPointAliasRuntime,
    AstralPointReferenceSet,
    AstralPointRuntime,
    AstralPointVariantRuntime,
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

    _DEFAULT_PLANET_SWE_IDS = planet_swe_ids_by_code()

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
        astral_points: Sequence[Mapping[str, object]],
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
                        name=self._display_name(item),
                        swe_id=self._planet_swe_id(item),
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
                    SignReferenceData(
                        code=str(item["code"]),
                        name=self._display_name(item),
                        element=self._required_str(item, "element"),
                        modality=self._required_str(item, "modality"),
                        polarity=self._required_str(item, "polarity"),
                    )
                    for item in self._items(payload, "signs")
                )
            ),
            houses=HouseReferenceSet(
                tuple(
                    HouseReferenceData(
                        number=int(item["number"]),
                        name=self._display_name(item, fallback=f"House {item['number']}"),
                    )
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
                        name=self._display_name(item),
                        angle=float(item["angle"]),
                        family=str(item.get("family", "major")),
                        is_enabled=bool(item.get("is_enabled", True)),
                        is_major=bool(item.get("is_major", True)),
                        is_minor=bool(item.get("is_minor", False)),
                        default_orb_deg=self._optional_float(item.get("default_orb_deg")),
                        default_valence=str(item.get("default_valence", "contextual")),
                        interpretive_valence=str(item.get("interpretive_valence", "contextual")),
                        energy_type=str(item.get("energy_type", "neutral")),
                        legacy_orb_fields=self._legacy_orb_fields(item),
                    )
                    for item in self._items(payload, "aspects")
                ),
                orb_rules=tuple(
                    AspectOrbRuleReferenceData(
                        aspect_code=str(item["aspect_code"]),
                        system_code=str(item.get("system_code", "modern")),
                        calculation_context=str(item.get("calculation_context", "natal")),
                        source_body_type=str(item.get("source_body_type", "any")),
                        source_planet_code=self._optional_str(item.get("source_planet_code")),
                        source_point_code=self._optional_str(item.get("source_point_code")),
                        target_body_type=str(item.get("target_body_type", "any")),
                        target_planet_code=self._optional_str(item.get("target_planet_code")),
                        target_point_code=self._optional_str(item.get("target_point_code")),
                        orb_deg=float(item["orb_deg"]),
                        priority=int(item.get("priority", 1)),
                        is_enabled=bool(item.get("is_enabled", True)),
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
            astral_points=self._map_astral_points(astral_points),
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

    def _map_astral_points(
        self,
        rows: Sequence[Mapping[str, object]],
    ) -> AstralPointReferenceSet:
        """Convertit les points astraux DB en contrats runtime typés."""
        items: list[AstralPointRuntime] = []
        for item in rows:
            variants = tuple(
                AstralPointVariantRuntime(
                    variant_code=str(variant["variant_code"]),
                    display_name=str(variant["display_name"]),
                    calculation_mode=str(variant["calculation_mode"]),
                    engine_key=self._optional_str(variant.get("engine_key")),
                    is_default=bool(variant["is_default"]),
                )
                for variant in self._nested_items(item, "variants")
            )
            aliases = tuple(
                AstralPointAliasRuntime(
                    alias=str(alias["alias"]),
                    language_code=str(alias["language_code"]),
                    source=str(alias["source"]),
                    variant_code=self._optional_str(alias.get("variant_code")),
                    engine_key=self._optional_str(alias.get("engine_key")),
                    is_primary=bool(alias["is_primary"]),
                )
                for alias in self._nested_items(item, "aliases")
            )
            default_variants = tuple(
                variant.variant_code for variant in variants if variant.is_default
            )
            if len(default_variants) > 1:
                raise ValueError(f"multiple default variants for astral point {item['code']}")
            items.append(
                AstralPointRuntime(
                    code=str(item["code"]),
                    display_name=str(item["display_name"]),
                    family_code=str(item["family_code"]),
                    astronomical_type=str(item["astronomical_type"]),
                    is_physical_body=bool(item["is_physical_body"]),
                    default_variant_code=default_variants[0] if default_variants else None,
                    variants=variants,
                    aliases=aliases,
                )
            )
        return AstralPointReferenceSet(tuple(items))

    def _items(self, payload: Mapping[str, object], key: str) -> tuple[Mapping[str, object], ...]:
        """Extrait une liste de mappings du payload infra."""
        raw = payload.get(key)
        if not isinstance(raw, list):
            return ()
        return tuple(item for item in raw if isinstance(item, Mapping))

    def _nested_items(
        self,
        payload: Mapping[str, object],
        key: str,
    ) -> tuple[Mapping[str, object], ...]:
        """Extrait une liste imbriquee de mappings deja confinée à l'infra."""
        raw = payload.get(key)
        if not isinstance(raw, (list, tuple)):
            return ()
        return tuple(item for item in raw if isinstance(item, Mapping))

    def _optional_str(self, value: object) -> str | None:
        """Convertit une valeur optionnelle en chaine normalisee."""
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _required_str(self, item: Mapping[str, object], field_name: str) -> str:
        """Exige un champ texte source par le payload infra."""
        value = self._optional_str(item.get(field_name))
        if value is None:
            code = str(item.get("code") or "<unknown>")
            raise ValueError(f"missing required sign profile field {field_name} for {code}")
        return value

    def _optional_float(self, value: object) -> float | None:
        """Convertit une valeur optionnelle en flottant."""
        if value is None:
            return None
        return float(value)

    def _display_name(self, item: Mapping[str, object], fallback: str | None = None) -> str:
        """Retourne le nom humain en conservant les fixtures historiques minimales."""
        raw = item.get("name")
        if raw is None:
            raw = fallback or str(item.get("code", "")).replace("_", " ").title()
        return str(raw)

    def _planet_swe_id(self, item: Mapping[str, object]) -> int:
        """Résout l'identifiant SwissEph depuis le payload ou le catalogue canonique."""
        raw = item.get("swe_id")
        if raw is not None:
            return int(raw)
        code = str(item["code"]).strip().lower()
        return int(self._DEFAULT_PLANET_SWE_IDS.get(code, 0))

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

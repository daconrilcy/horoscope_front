"""Mapping infra vers contrats runtime astrologiques.

Ce module confine les payloads SQL/JSON a la couche infra et retourne au domaine
une photographie immutable du referentiel astrologique.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.domain.astrology.planet_catalog import planet_swe_ids_by_code
from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectInterpretiveProfileRuntimeData,
    AspectStructuralDefinitionRuntimeData,
)
from app.domain.astrology.runtime.runtime_reference import (
    AccidentalDignityRuleReferenceData,
    AdvancedConditionReferenceSet,
    AdvancedConditionScoreProfileReferenceData,
    AdvancedConditionTypeReferenceData,
    AdvancedConditionWeightReferenceData,
    AnglePointReferenceData,
    AnglePointReferenceSet,
    AspectOrbRuleReferenceData,
    AspectReferenceSet,
    AstralPointAliasRuntime,
    AstralPointReferenceSet,
    AstralPointRuntime,
    AstralPointVariantRuntime,
    AstrologyRuntimeReference,
    AstrologySystemReferenceData,
    AstrologySystemReferenceSet,
    DignityConditionValue,
    DignityReferenceData,
    DignityReferenceSet,
    DignityScoreProfileReferenceData,
    DignityScoreWeightReferenceData,
    DignitySystemReferenceData,
    DignityTypeReferenceData,
    DominanceFactorTypeReferenceData,
    DominanceReferenceSet,
    DominanceScoreProfileReferenceData,
    DominanceScoreWeightReferenceData,
    EssentialDignityRuleReferenceData,
    FaceDecanReferenceData,
    FixedStarReferenceData,
    FixedStarReferenceSet,
    HouseAxisReferenceData,
    HouseReferenceData,
    HouseReferenceSet,
    HouseSystemReferenceData,
    HouseSystemReferenceSet,
    InterpretationAdapterReferenceSet,
    InterpretationAdapterRuleReferenceData,
    InterpretationConditionValue,
    InterpretationSignalTypeReferenceData,
    InterpretationThemeReferenceData,
    PlanetConditionSignalProfileReferenceData,
    PlanetDignityReferenceSet,
    PlanetNatureReferenceData,
    PlanetNatureReferenceSet,
    PlanetReferenceData,
    PlanetReferenceSet,
    SignReferenceData,
    SignReferenceSet,
    TermBoundReferenceData,
    TriplicityRulerReferenceData,
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
        dignity_reference: Mapping[str, object],
        condition_signal_profiles: Sequence[Mapping[str, object]],
        dominance_factor_types: Sequence[Mapping[str, object]],
        dominance_score_profiles: Sequence[Mapping[str, object]],
        dominance_score_weights: Sequence[Mapping[str, object]],
        advanced_condition_types: Sequence[Mapping[str, object]],
        advanced_condition_score_profiles: Sequence[Mapping[str, object]],
        advanced_condition_weights: Sequence[Mapping[str, object]],
        interpretation_signal_types: Sequence[Mapping[str, object]],
        interpretation_themes: Sequence[Mapping[str, object]],
        interpretation_adapter_rules: Sequence[Mapping[str, object]],
        planet_natures: Sequence[Mapping[str, object]],
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
            planet_natures=PlanetNatureReferenceSet(
                tuple(
                    PlanetNatureReferenceData(
                        code=str(item["code"]),
                        label=str(item["label"]),
                        planet_codes=tuple(
                            str(code) for code in item.get("planet_codes", ()) if str(code).strip()
                        ),
                        sort_order=int(item["sort_order"]),
                    )
                    for item in planet_natures
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
                        seasonal_quadrant=self._required_str(item, "seasonal_quadrant"),
                        fertility=self._required_str(item, "fertility"),
                        voice=self._required_str(item, "voice"),
                        form=self._required_str(item, "form"),
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
                structural_definitions=tuple(
                    AspectStructuralDefinitionRuntimeData(
                        code=str(item["code"]),
                        name=self._display_name(item),
                        angle=float(item["angle"]),
                        family=str(item.get("family", "major")),
                        default_orb_deg=self._required_float(item, "default_orb_deg"),
                        is_enabled=bool(item.get("is_enabled", True)),
                        is_major=bool(item.get("is_major", True)),
                        is_minor=bool(item.get("is_minor", False)),
                        system_code=str(item.get("system_code", "modern")),
                        legacy_orb_fields=self._legacy_orb_fields(item),
                    )
                    for item in self._items(payload, "aspects")
                ),
                interpretive_profiles=tuple(
                    AspectInterpretiveProfileRuntimeData(
                        aspect_code=str(item["code"]),
                        default_valence=self._required_runtime_str(item, "default_valence"),
                        interpretive_valence=self._required_runtime_str(
                            item, "interpretive_valence"
                        ),
                        energy_type=self._required_runtime_str(item, "energy_type"),
                        source_profile_code=self._display_name(item),
                        reference_version=reference_version,
                        system_code=str(item.get("system_code", "modern")),
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
            dignity_reference=self.map_dignity_reference(dignity_reference or {}),
            condition_signal_profiles=tuple(
                PlanetConditionSignalProfileReferenceData(
                    condition_axis=str(item["condition_axis"]),
                    level_min=float(item["level_min"]),
                    level_max=float(item["level_max"]),
                    signal_code=str(item["signal_code"]),
                    signal_label=str(item["signal_label"]),
                    signal_level=str(item["signal_level"]),
                    interpretation_use=str(item["interpretation_use"]),
                    priority_weight=float(item["priority_weight"]),
                    signal_hint=str(item["prompt_hint"]),
                    reference_version=str(item["reference_version"]),
                )
                for item in condition_signal_profiles
            ),
            dominance_factor_types=tuple(
                DominanceFactorTypeReferenceData(
                    code=str(item["code"]),
                    label=str(item["label"]),
                    category=str(item["category"]),
                    default_weight=float(item["default_weight"]),
                    sort_order=int(item["sort_order"]),
                    is_active=bool(item["is_active"]),
                    description=str(item["description"]),
                    reference_version=str(item["reference_version"]),
                )
                for item in dominance_factor_types
            ),
            dominance_reference=DominanceReferenceSet(
                factor_types=tuple(
                    DominanceFactorTypeReferenceData(
                        code=str(item["code"]),
                        label=str(item["label"]),
                        category=str(item["category"]),
                        default_weight=float(item["default_weight"]),
                        sort_order=int(item["sort_order"]),
                        is_active=bool(item["is_active"]),
                        description=str(item["description"]),
                        reference_version=str(item["reference_version"]),
                    )
                    for item in dominance_factor_types
                ),
                score_profiles=tuple(
                    DominanceScoreProfileReferenceData(
                        code=str(item["code"]),
                        label=str(item["label"]),
                        tradition_code=str(item["tradition_code"]),
                        description=str(item["description"]),
                        reference_version_code=str(item["reference_version_code"]),
                        is_active=bool(item["is_active"]),
                    )
                    for item in dominance_score_profiles
                ),
                score_weights=tuple(
                    DominanceScoreWeightReferenceData(
                        score_profile_code=str(item["score_profile_code"]),
                        factor_type_code=str(item["factor_type_code"]),
                        weight=float(item["weight"]),
                        min_value=float(item["min_value"]),
                        max_value=float(item["max_value"]),
                        normalization_method=str(item["normalization_method"]),
                        notes=str(item["notes"]),
                    )
                    for item in dominance_score_weights
                ),
            ),
            advanced_condition_reference=AdvancedConditionReferenceSet(
                condition_types=tuple(
                    AdvancedConditionTypeReferenceData(
                        code=str(item["code"]),
                        label=str(item["label"]),
                        category=str(item["category"]),
                        description=str(item["description"]),
                        functional_effect=str(item["functional_effect"]),
                        expression_effect=str(item["expression_effect"]),
                        intensity_effect=str(item["intensity_effect"]),
                        visibility_effect=str(item["visibility_effect"]),
                        default_weight=float(item["default_weight"]),
                        sort_order=int(item["sort_order"]),
                        is_active=bool(item["is_active"]),
                        reference_version=str(item["reference_version"]),
                    )
                    for item in advanced_condition_types
                ),
                score_profiles=tuple(
                    AdvancedConditionScoreProfileReferenceData(
                        code=str(item["code"]),
                        label=str(item["label"]),
                        tradition_code=str(item["tradition_code"]),
                        description=str(item["description"]),
                        reference_version_code=str(item["reference_version_code"]),
                        is_active=bool(item["is_active"]),
                    )
                    for item in advanced_condition_score_profiles
                ),
                score_weights=tuple(
                    AdvancedConditionWeightReferenceData(
                        score_profile_code=str(item["score_profile_code"]),
                        condition_type_code=str(item["condition_type_code"]),
                        functional_strength_weight=float(item["functional_strength_weight"]),
                        visibility_weight=float(item["visibility_weight"]),
                        stability_weight=float(item["stability_weight"]),
                        intensity_weight=float(item["intensity_weight"]),
                        coherence_weight=float(item["coherence_weight"]),
                        support_weight=float(item["support_weight"]),
                        constraint_weight=float(item["constraint_weight"]),
                        ranking_weight=float(item["ranking_weight"]),
                        uses_default_weight=bool(item["uses_default_weight"]),
                        notes=str(item["notes"]),
                    )
                    for item in advanced_condition_weights
                ),
            ),
            interpretation_adapter_reference=InterpretationAdapterReferenceSet(
                signal_types=tuple(
                    InterpretationSignalTypeReferenceData(
                        code=str(item["code"]),
                        label=str(item["label"]),
                        category=str(item["category"]),
                        theme_code=str(item["theme_code"]),
                        description=str(item["description"]),
                        priority_default=str(item["priority_default"]),
                        priority_default_rank=int(item["priority_default_rank"]),
                        is_active=bool(item["is_active"]),
                        sort_order=int(item["sort_order"]),
                        reference_version=str(item["reference_version"]),
                    )
                    for item in interpretation_signal_types
                ),
                themes=tuple(
                    InterpretationThemeReferenceData(
                        code=str(item["code"]),
                        label=str(item["label"]),
                        category=str(item["category"]),
                        description=str(item["description"]),
                        is_active=bool(item["is_active"]),
                        reference_version=str(item["reference_version"]),
                    )
                    for item in interpretation_themes
                ),
                adapter_rules=tuple(
                    InterpretationAdapterRuleReferenceData(
                        code=str(item["code"]),
                        source_type=str(item["source_type"]),
                        source_code=str(item["source_code"]),
                        conditions=tuple(
                            InterpretationConditionValue(
                                key=str(condition["key"]),
                                value=self._condition_value(condition.get("value")),
                            )
                            for condition in self._nested_items(item, "conditions")
                        ),
                        signal_code=str(item["signal_code"]),
                        priority_override=self._optional_str(item.get("priority_override")),
                        priority_override_rank=(
                            None
                            if item.get("priority_override_rank") is None
                            else int(item["priority_override_rank"])
                        ),
                        weight=float(item["weight"]),
                        is_active=bool(item["is_active"]),
                        reference_version_code=str(item["reference_version_code"]),
                    )
                    for item in interpretation_adapter_rules
                ),
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
            astral_points=self.map_astral_points(astral_points),
            fixed_stars=self.map_fixed_stars(self._items(payload, "fixed_stars")),
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

    def map_dignity_reference(
        self,
        payload: Mapping[str, object],
    ) -> PlanetDignityReferenceSet:
        """Convertit le referentiel avance des dignites en contrats immutables."""
        return PlanetDignityReferenceSet(
            essential_types=self._map_dignity_types(payload, "essential_types"),
            accidental_types=self._map_dignity_types(payload, "accidental_types"),
            term_systems=self._map_dignity_systems(payload, "term_systems"),
            decan_systems=self._map_dignity_systems(payload, "decan_systems"),
            score_profiles=tuple(
                DignityScoreProfileReferenceData(
                    code=str(item["code"]),
                    tradition=str(item["tradition"]),
                    is_default=bool(item["is_default"]),
                )
                for item in self._items(payload, "score_profiles")
            ),
            essential_weights=self._map_weight_groups(payload, "essential_weights"),
            accidental_weights=self._map_weight_groups(payload, "accidental_weights"),
            essential_rules=tuple(
                EssentialDignityRuleReferenceData(
                    planet_code=str(item["planet_code"]),
                    sign_code=str(item["sign_code"]),
                    dignity_type_code=str(item["dignity_type_code"]),
                    degree_start=float(item["degree_start"]),
                    degree_end=float(item["degree_end"]),
                    system_code=str(item["system_code"]),
                )
                for item in self._items(payload, "essential_rules")
            ),
            triplicity_rulers=tuple(
                TriplicityRulerReferenceData(
                    element_code=str(item["element_code"]),
                    sect_code=str(item["sect_code"]),
                    planet_code=str(item["planet_code"]),
                    role_code=str(item["role_code"]),
                    system_code=str(item["system_code"]),
                )
                for item in self._items(payload, "triplicity_rulers")
            ),
            term_bounds=tuple(
                TermBoundReferenceData(
                    term_system_code=str(item["term_system_code"]),
                    sign_code=str(item["sign_code"]),
                    planet_code=str(item["planet_code"]),
                    degree_start=float(item["degree_start"]),
                    degree_end=float(item["degree_end"]),
                    order_index=int(item["order_index"]),
                )
                for item in self._items(payload, "term_bounds")
            ),
            face_decans=tuple(
                FaceDecanReferenceData(
                    decan_system_code=str(item["decan_system_code"]),
                    sign_code=str(item["sign_code"]),
                    planet_code=str(item["planet_code"]),
                    decan_index=int(item["decan_index"]),
                    degree_start=float(item["degree_start"]),
                    degree_end=float(item["degree_end"]),
                )
                for item in self._items(payload, "face_decans")
            ),
            accidental_rules=tuple(
                AccidentalDignityRuleReferenceData(
                    dignity_type_code=str(item["dignity_type_code"]),
                    planet_code=self._optional_str(item.get("planet_code")),
                    condition_schema_code=str(item["condition_schema_code"]),
                    conditions=tuple(
                        DignityConditionValue(
                            key=str(condition["key"]),
                            value=self._condition_value(condition.get("value")),
                        )
                        for condition in self._nested_items(item, "conditions")
                    ),
                    system_code=str(item["system_code"]),
                )
                for item in self._items(payload, "accidental_rules")
            ),
        )

    def map_astral_points(
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

    def map_fixed_stars(
        self,
        rows: Sequence[Mapping[str, object]],
    ) -> FixedStarReferenceSet:
        """Convertit les etoiles fixes en contrats runtime typés."""
        return FixedStarReferenceSet(
            tuple(
                FixedStarReferenceData(
                    code=str(item["code"]),
                    display_name=self._display_name(item),
                    longitude=float(item["longitude"]),
                    reference_system=str(item.get("reference_system", "catalog")),
                    source_code=str(item.get("source_code", "runtime_reference")),
                    constellation_code=self._optional_str(item.get("constellation_code")),
                    magnitude=self._optional_float(item.get("magnitude")),
                    reference_epoch=self._optional_str(item.get("reference_epoch")),
                    categories=tuple(
                        str(category)
                        for category in item.get("categories", ())
                        if str(category).strip()
                    ),
                )
                for item in rows
            )
        )

    def _items(self, payload: Mapping[str, object], key: str) -> tuple[Mapping[str, object], ...]:
        """Extrait une liste de mappings du payload infra."""
        raw = payload.get(key)
        if not isinstance(raw, (list, tuple)):
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

    def _map_weight_groups(
        self,
        payload: Mapping[str, object],
        key: str,
    ) -> dict[str, tuple[DignityScoreWeightReferenceData, ...]]:
        """Convertit les poids groupes par profil de scoring."""
        raw = payload.get(key)
        if not isinstance(raw, Mapping):
            return {}
        groups: dict[str, tuple[DignityScoreWeightReferenceData, ...]] = {}
        for profile_code, rows in raw.items():
            if not isinstance(rows, (list, tuple)):
                continue
            groups[str(profile_code)] = tuple(
                DignityScoreWeightReferenceData(
                    dignity_type_code=str(item["dignity_type_code"]),
                    score_value=float(item["score_value"]),
                    functional_weight=float(item["functional_weight"]),
                    expression_weight=float(item["expression_weight"]),
                    intensity_weight=float(item["intensity_weight"]),
                    condition_visibility=float(item["visibility_weight"]),
                    condition_stability=float(item["stability_weight"]),
                    condition_coherence=float(item["coherence_weight"]),
                    condition_support=float(item["support_weight"]),
                    condition_constraint=float(item["constraint_weight"]),
                )
                for item in rows
                if isinstance(item, Mapping)
            )
        return groups

    def _map_dignity_types(
        self,
        payload: Mapping[str, object],
        key: str,
    ) -> tuple[DignityTypeReferenceData, ...]:
        """Convertit les types de dignites en contrats runtime."""
        return tuple(
            DignityTypeReferenceData(
                code=str(item["code"]),
                label=str(item["label"]),
                description=str(item["description"]),
                sort_order=int(item["sort_order"]),
            )
            for item in self._items(payload, key)
        )

    def _map_dignity_systems(
        self,
        payload: Mapping[str, object],
        key: str,
    ) -> tuple[DignitySystemReferenceData, ...]:
        """Convertit les systemes de termes et decans en contrats runtime."""
        return tuple(
            DignitySystemReferenceData(
                code=str(item["code"]),
                label=str(item["label"]),
                description=self._optional_str(item.get("description")),
                sort_order=int(item["sort_order"]),
            )
            for item in self._items(payload, key)
        )

    def _condition_value(self, value: object) -> str | int | float | tuple[str | int | float, ...]:
        """Normalise une valeur de condition en scalaire ou tuple immutable."""
        if isinstance(value, (str, int, float)):
            return value
        if isinstance(value, (list, tuple)):
            return tuple(item for item in value if isinstance(item, (str, int, float)))
        return str(value)

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

    def _required_runtime_str(self, item: Mapping[str, object], field_name: str) -> str:
        """Exige un champ texte source pour un contrat runtime non signe."""
        value = self._optional_str(item.get(field_name))
        if value is None:
            code = str(item.get("code") or "<unknown>")
            raise ValueError(f"missing required runtime field {field_name} for {code}")
        return value

    def _required_float(self, item: Mapping[str, object], field_name: str) -> float:
        """Exige un champ numerique source par le payload infra."""
        value = item.get(field_name)
        if value is None:
            code = str(item.get("code") or "<unknown>")
            raise ValueError(f"missing required runtime field {field_name} for {code}")
        return float(value)

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

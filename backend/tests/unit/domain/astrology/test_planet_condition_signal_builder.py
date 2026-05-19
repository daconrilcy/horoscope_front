"""Tests du builder de signaux de conditions planetaires."""

from dataclasses import replace

from app.domain.astrology.condition.contracts import (
    PlanetConditionProfile,
    PlanetConditionSignal,
    PlanetConditionSignalSet,
)
from app.domain.astrology.condition.planet_condition_signal_builder import (
    PlanetConditionSignalBuilder,
)
from app.domain.astrology.runtime.runtime_reference import (
    PlanetConditionSignalProfileReferenceData,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference


def _profile(planet_code: str = "sun") -> PlanetConditionProfile:
    """Construit un profil conditionnel stable pour les signaux."""
    return PlanetConditionProfile(
        planet_code=planet_code,
        score_profile="traditional_standard",
        tradition="traditional",
        reference_version="test",
        sect="day",
        functional_strength=1.0,
        visibility=0.5,
        stability=0.49,
        intensity=1.2,
        coherence=0.0,
        support=0.7,
        constraint=0.5,
        ranking_score=3.4,
        condition_level="strong",
        breakdown=(),
        explanation_facts=(),
    )


def _signal_profile(
    *,
    axis: str,
    level_min: float,
    level_max: float,
    code: str,
    priority_weight: float,
) -> PlanetConditionSignalProfileReferenceData:
    """Construit une ligne runtime de signal sans redefinir la logique du builder."""
    return PlanetConditionSignalProfileReferenceData(
        condition_axis=axis,
        level_min=level_min,
        level_max=level_max,
        signal_code=code,
        signal_label=code.replace("_", " ").title(),
        signal_level="matched",
        interpretation_use=f"use_{axis}",
        priority_weight=priority_weight,
        prompt_hint=f"{axis}_hint",
        reference_version="test",
    )


def _reference_with_signal_profiles(
    signal_profiles: tuple[PlanetConditionSignalProfileReferenceData, ...],
):
    """Remplace uniquement les profils de signaux dans la fixture runtime."""
    return replace(complete_reference(), condition_signal_profiles=signal_profiles)


def test_builder_selects_inclusive_runtime_ranges_without_local_table() -> None:
    """Les bornes inclusives du runtime gouvernent les signaux retenus."""
    reference = _reference_with_signal_profiles(
        (
            _signal_profile(
                axis="functional_strength",
                level_min=1.0,
                level_max=1.0,
                code="functional_exact",
                priority_weight=20.0,
            ),
            _signal_profile(
                axis="visibility",
                level_min=0.5,
                level_max=0.5,
                code="visibility_exact",
                priority_weight=10.0,
            ),
            _signal_profile(
                axis="stability",
                level_min=0.5,
                level_max=1.0,
                code="stability_outside",
                priority_weight=30.0,
            ),
        )
    )

    result = PlanetConditionSignalBuilder().build((_profile(),), reference)

    assert result == (
        PlanetConditionSignalSet(
            planet_code="sun",
            score_profile="traditional_standard",
            tradition="traditional",
            reference_version="test",
            signals=(
                PlanetConditionSignal(
                    code="visibility_exact",
                    label="Visibility Exact",
                    axis="visibility",
                    level="matched",
                    level_min=0.5,
                    level_max=0.5,
                    axis_value=0.5,
                    interpretation_use="use_visibility",
                    priority_weight=10.0,
                    prompt_hint="visibility_hint",
                ),
                PlanetConditionSignal(
                    code="functional_exact",
                    label="Functional Exact",
                    axis="functional_strength",
                    level="matched",
                    level_min=1.0,
                    level_max=1.0,
                    axis_value=1.0,
                    interpretation_use="use_functional_strength",
                    priority_weight=20.0,
                    prompt_hint="functional_strength_hint",
                ),
            ),
        ),
    )


def test_builder_sorts_signals_by_priority_axis_and_code() -> None:
    """Le tri reste stable et independant de l'ordre des lignes runtime."""
    reference = _reference_with_signal_profiles(
        (
            _signal_profile(
                axis="visibility",
                level_min=0.0,
                level_max=1.0,
                code="visibility_b",
                priority_weight=10.0,
            ),
            _signal_profile(
                axis="functional_strength",
                level_min=0.0,
                level_max=2.0,
                code="functional_a",
                priority_weight=10.0,
            ),
            _signal_profile(
                axis="visibility",
                level_min=0.0,
                level_max=1.0,
                code="visibility_a",
                priority_weight=10.0,
            ),
        )
    )

    signals = PlanetConditionSignalBuilder().build((_profile(),), reference)[0].signals

    assert [signal.code for signal in signals] == [
        "functional_a",
        "visibility_a",
        "visibility_b",
    ]


def test_builder_keeps_payload_non_editorial_and_technical() -> None:
    """Le payload contient uniquement codes, niveaux, axes et usages techniques."""
    reference = _reference_with_signal_profiles(
        (
            _signal_profile(
                axis="constraint",
                level_min=0.5,
                level_max=0.5,
                code="constraint_exact",
                priority_weight=1.0,
            ),
        )
    )

    signal = PlanetConditionSignalBuilder().build((_profile(),), reference)[0].signals[0]

    assert signal.code == "constraint_exact"
    assert signal.axis == "constraint"
    assert signal.label == "Constraint Exact"
    assert signal.prompt_hint == "constraint_hint"

"""Profils V1 des modificateurs accidentels issus des conditions avancees."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AdvancedConditionModifierProfile:
    """Associe une cle de condition a un delta accidentel configurable."""

    condition_key: str
    score_delta: float
    category: str


ADVANCED_CONDITION_MODIFIER_PROFILES: dict[str, AdvancedConditionModifierProfile] = {
    "cazimi_bonus": AdvancedConditionModifierProfile(
        condition_key="cazimi_bonus",
        score_delta=5,
        category="solar_condition",
    ),
    "combust_penalty": AdvancedConditionModifierProfile(
        condition_key="combust_penalty",
        score_delta=-5,
        category="solar_condition",
    ),
    "under_beams_penalty": AdvancedConditionModifierProfile(
        condition_key="under_beams_penalty",
        score_delta=-2,
        category="solar_condition",
    ),
    "retrograde_penalty": AdvancedConditionModifierProfile(
        condition_key="retrograde_penalty",
        score_delta=-3,
        category="motion_condition",
    ),
    "stationary_bonus": AdvancedConditionModifierProfile(
        condition_key="stationary_bonus",
        score_delta=2,
        category="motion_condition",
    ),
    "very_fast_bonus": AdvancedConditionModifierProfile(
        condition_key="very_fast_bonus",
        score_delta=1,
        category="motion_condition",
    ),
    "very_slow_penalty": AdvancedConditionModifierProfile(
        condition_key="very_slow_penalty",
        score_delta=-1,
        category="motion_condition",
    ),
    "invisible_penalty": AdvancedConditionModifierProfile(
        condition_key="invisible_penalty",
        score_delta=-4,
        category="visibility_condition",
    ),
    "emerging_bonus": AdvancedConditionModifierProfile(
        condition_key="emerging_bonus",
        score_delta=2,
        category="visibility_condition",
    ),
    "oriental_superior_bonus": AdvancedConditionModifierProfile(
        condition_key="oriental_superior_bonus",
        score_delta=1,
        category="solar_phase_condition",
    ),
    "occidental_superior_penalty": AdvancedConditionModifierProfile(
        condition_key="occidental_superior_penalty",
        score_delta=-1,
        category="solar_phase_condition",
    ),
    "full_moon_bonus": AdvancedConditionModifierProfile(
        condition_key="full_moon_bonus",
        score_delta=2,
        category="lunar_condition",
    ),
    "new_moon_penalty": AdvancedConditionModifierProfile(
        condition_key="new_moon_penalty",
        score_delta=-2,
        category="lunar_condition",
    ),
}

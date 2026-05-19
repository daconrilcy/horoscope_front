"""Construction pure des signaux de conditions planetaires."""

from __future__ import annotations

from app.domain.astrology.condition.contracts import (
    PlanetConditionProfile,
    PlanetConditionSignal,
    PlanetConditionSignalSet,
)
from app.domain.astrology.runtime.runtime_reference import (
    AstrologyRuntimeReference,
    PlanetConditionSignalProfileReferenceData,
)


class PlanetConditionSignalBuilder:
    """Traduit des profils conditionnels en signaux gouvernes par le runtime."""

    def build(
        self,
        profiles: tuple[PlanetConditionProfile, ...],
        runtime_reference: AstrologyRuntimeReference,
    ) -> tuple[PlanetConditionSignalSet, ...]:
        """Produit les signaux pour chaque profil de planete."""
        signal_profiles = runtime_reference.condition_signal_profiles
        return tuple(
            self._build_for_profile(profile, signal_profiles)
            for profile in sorted(profiles, key=lambda item: item.planet_code)
        )

    def _build_for_profile(
        self,
        profile: PlanetConditionProfile,
        signal_profiles: tuple[PlanetConditionSignalProfileReferenceData, ...],
    ) -> PlanetConditionSignalSet:
        """Selectionne les signaux dont la plage runtime couvre l'axe du profil."""
        signals = [
            PlanetConditionSignal(
                code=signal_profile.signal_code,
                label=signal_profile.signal_label,
                axis=signal_profile.condition_axis,
                level=signal_profile.signal_level,
                level_min=round(signal_profile.level_min, 6),
                level_max=round(signal_profile.level_max, 6),
                axis_value=round(axis_value, 6),
                interpretation_use=signal_profile.interpretation_use,
                priority_weight=round(signal_profile.priority_weight, 6),
                prompt_hint=signal_profile.prompt_hint,
            )
            for signal_profile in signal_profiles
            for axis_value in (self._axis_value(profile, signal_profile.condition_axis),)
            if signal_profile.level_min <= axis_value <= signal_profile.level_max
        ]
        return PlanetConditionSignalSet(
            planet_code=profile.planet_code,
            score_profile=profile.score_profile,
            tradition=profile.tradition,
            reference_version=profile.reference_version,
            signals=tuple(
                sorted(
                    signals,
                    key=lambda item: (item.priority_weight, item.axis, item.code),
                    reverse=False,
                )
            ),
        )

    def _axis_value(self, profile: PlanetConditionProfile, axis: str) -> float:
        """Lit un axe declare par le contrat de profil conditionnel."""
        return float(getattr(profile, axis))

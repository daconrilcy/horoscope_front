"""Contrats purs des profils symboliques de conditions planetaires avancees."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class InterpretationPolarity(StrEnum):
    """Polarite symbolique portee par un profil pre-narratif."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    MIXED = "mixed"
    NEUTRAL = "neutral"


class InterpretationIntensity(StrEnum):
    """Intensite symbolique portee par un profil pre-narratif."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass(frozen=True, slots=True)
class AdvancedConditionInterpretationProfile:
    """Bloc symbolique court associe a une condition planetaire deja calculee."""

    condition_key: str
    polarity: InterpretationPolarity
    intensity: InterpretationIntensity
    keywords: tuple[str, ...]
    themes: tuple[str, ...]
    manifestations: tuple[str, ...]
    psychological_axes: tuple[str, ...]
    behavioral_axes: tuple[str, ...]
    notes: tuple[str, ...] = ()
    planet_key: str | None = None
    tradition_key: str | None = None

    def __post_init__(self) -> None:
        """Normalise les collections pour garantir un contrat immutable."""
        if not self.condition_key.strip():
            raise ValueError("condition_key is required")
        for field_name in (
            "keywords",
            "themes",
            "manifestations",
            "psychological_axes",
            "behavioral_axes",
        ):
            values = self._validated_fragments(
                tuple(getattr(self, field_name)),
                field_name=field_name,
                required=True,
            )
            object.__setattr__(self, field_name, values)
        object.__setattr__(
            self,
            "notes",
            self._validated_fragments(
                tuple(self.notes),
                field_name="notes",
                required=False,
            ),
        )

    @staticmethod
    def _validated_fragments(
        values: tuple[str, ...],
        *,
        field_name: str,
        required: bool,
    ) -> tuple[str, ...]:
        """Valide les fragments symboliques courts sans produire de narration."""
        if required and not values:
            raise ValueError(f"{field_name} must contain short non-empty fragments")
        if any(not value.strip() or len(value) > 40 for value in values):
            raise ValueError(f"{field_name} must contain short non-empty fragments")
        return values

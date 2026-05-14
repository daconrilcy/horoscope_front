"""Contrat semantique pur des interpretations d'aspects.

La couche semantique expose des taxonomies et references courtes; elle ne
porte ni narration, ni persona, ni langue editoriale.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.domain.astrology.runtime.aspect_runtime_data import AspectRuntimeData

from .aspect_semantic_provenance import (
    AspectSemanticCandidate,
    SemanticProvenance,
    prioritize_semantic_candidates,
)


@dataclass(frozen=True, slots=True)
class AspectInterpretationFacts:
    """Faits semantiques purs derives d'un runtime et d'un profil aspect."""

    symbolic_primitives: tuple[str, ...]
    semantic_axes: tuple[str, ...]
    growth_axes: tuple[str, ...]
    editorial_theme_refs: tuple[str, ...] = ()
    relationship_axes: tuple[str, ...] = ()
    shadow_axes: tuple[str, ...] = ()
    source_profile_code: str | None = None
    semantic_candidates: tuple[AspectSemanticCandidate, ...] = field(default_factory=tuple)

    @classmethod
    def from_profile(
        cls,
        *,
        runtime: AspectRuntimeData,
        profile: dict[str, Any],
    ) -> AspectInterpretationFacts:
        """Construit les faits semantiques depuis un profil documentaire."""
        aspect_code = str(profile.get("aspect_code") or runtime.aspect.code)
        primitives = (
            runtime.aspect.code,
            runtime.aspect.family,
            runtime.participants.planet_a,
            runtime.participants.planet_b,
        )
        semantic_axes = _require_list(profile, "core_keywords_json")
        growth_axes = _require_list(profile, "growth_patterns_json")
        relationship_axes = _optional_list(profile, "relationship_keywords_json")
        shadow_axes = _optional_list(profile, "shadow_keywords_json")
        candidates = prioritize_semantic_candidates(
            (
                AspectSemanticCandidate(
                    semantic_axes=semantic_axes,
                    provenance=SemanticProvenance(
                        source_system=str(profile.get("astral_system_code") or "modern"),
                        source_tradition="reference_profile",
                        source_authority="astral_aspect_interpretation_profiles",
                        origin_reference=aspect_code,
                    ),
                    confidence=0.86,
                    context_weight=1.0,
                ),
            )
        )
        return cls(
            symbolic_primitives=tuple(primitives),
            semantic_axes=semantic_axes,
            growth_axes=growth_axes,
            editorial_theme_refs=(str(profile.get("title") or aspect_code),),
            relationship_axes=relationship_axes,
            shadow_axes=shadow_axes,
            source_profile_code=aspect_code,
            semantic_candidates=candidates,
        )


def _require_list(profile: dict[str, Any], field_name: str) -> tuple[str, ...]:
    """Extrait une liste semantique obligatoire depuis un profil."""
    values = profile.get(field_name)
    if not isinstance(values, list) or not values:
        raise ValueError(f"aspect interpretation profile misses {field_name}")
    normalized_values = tuple(str(value).strip() for value in values)
    if any(not value for value in normalized_values):
        raise ValueError(f"aspect interpretation profile misses {field_name}")
    return normalized_values


def _optional_list(profile: dict[str, Any], field_name: str) -> tuple[str, ...]:
    """Extrait une liste semantique optionnelle depuis un profil."""
    values = profile.get(field_name)
    if not isinstance(values, list):
        return ()
    return tuple(str(value).strip() for value in values if str(value).strip())

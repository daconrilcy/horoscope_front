"""Builder editorial deterministe des interpretations d'aspects.

Le builder assemble runtime, faits semantiques et profil; les textes longs
restent fournis par les profils de reference.
"""

from __future__ import annotations

from typing import Any

from app.domain.astrology.runtime.aspect_runtime_data import AspectRuntimeData

from .aspect_interpretation_contracts import AspectEditorialInterpretation
from .aspect_interpretation_facts import AspectInterpretationFacts
from .profile_fields import required_profile_values


class AspectInterpretationBuilder:
    """Assemble une interpretation aspect depuis un profil explicite."""

    def build(
        self,
        *,
        runtime: AspectRuntimeData,
        facts: AspectInterpretationFacts,
        profile: dict[str, Any] | None,
    ) -> AspectEditorialInterpretation:
        """Produit les champs editoriaux ou leve une erreur si le profil manque."""
        if profile is None:
            raise ValueError(f"missing aspect interpretation profile: {runtime.aspect.code}")
        summary = profile.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            raise ValueError("aspect interpretation profile misses summary")
        return AspectEditorialInterpretation(
            summary=summary,
            psychological_meaning=required_profile_values(profile, "psychological_keywords_json"),
            relationship_expression=required_profile_values(profile, "relationship_keywords_json"),
            shadow_expression=facts.shadow_axes,
            growth_path=facts.growth_axes,
            source_profile_code=facts.source_profile_code,
        )

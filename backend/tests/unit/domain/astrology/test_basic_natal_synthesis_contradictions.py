# Commentaire global: ces tests couvrent les contradictions astrologiques
# representatives du mode Basic.
"""Tests adversariaux des syntheses natales Basic a signaux mixtes."""

from __future__ import annotations

from app.domain.astrology.interpretation.basic_natal_eligibility import EligibilityContext
from app.domain.astrology.interpretation.natal_synthesis_resolver import SynthesisResolver
from app.domain.astrology.interpretation.natal_theme_taxonomy import (
    BasicThemeCode,
    ThemeModel,
)


def test_venus_strong_but_combust_is_nuanced() -> None:
    """Venus forte et combuste produit une integration nuancee."""
    synthesis = _resolve(
        _theme(
            BasicThemeCode.RESOURCES_AND_VALUES,
            resources=("venus-taurus", "venus-house-2"),
            constraints=("venus-combust",),
            tensions=("venus-square-mars",),
            activation_score=142.0,
            matched_objects=("venus", "taurus", "house:2", "combust"),
        )
    )

    assert synthesis.section_eligible is True
    assert "nuance explicite" in synthesis.integration_statement
    assert synthesis.confidence == "medium"


def test_constrained_moon_keeps_resource_and_constraint_separate() -> None:
    """Une Lune centrale et contrainte garde deux lignes distinctes."""
    synthesis = _resolve(
        _theme(
            BasicThemeCode.EMOTIONAL_PATTERN,
            resources=("moon-cancer", "water-balance"),
            constraints=("moon-fall",),
            tensions=("moon-square-saturn",),
            activation_score=158.0,
            matched_objects=("moon", "water", "fall", "saturn"),
        )
    )

    assert "ressource" in synthesis.resource_statement
    assert "contrainte" in synthesis.constraint_statement
    assert "nuance explicite" in synthesis.integration_statement


def test_jupiter_square_luminaires_is_integrated_without_absolute_tone() -> None:
    """Jupiter fort et carre aux luminaires reste une entree editoriale controlee."""
    synthesis = _resolve(
        _theme(
            BasicThemeCode.GROWTH_DIRECTION,
            resources=("jupiter-sagittarius", "jupiter-angular"),
            constraints=("jupiter-square-sun",),
            tensions=("jupiter-square-moon",),
            activation_score=136.0,
            matched_objects=("jupiter", "sagittarius", "sun", "moon", "square"),
        )
    )

    payload = synthesis.to_internal_payload()
    assert payload["section_eligible"] is True
    assert "nuance explicite" in payload["integration_statement"]
    assert "toujours" not in " ".join(str(value) for value in payload.values()).casefold()


def test_mixed_relationship_theme_links_support_and_tension() -> None:
    """Un theme relationnel mixte relie explicitement appui et tension."""
    synthesis = _resolve(
        _theme(
            BasicThemeCode.RELATIONSHIP_PATTERN,
            resources=("venus-libra", "venus-house-7"),
            constraints=("venus-retrograde",),
            tensions=("venus-square-mars",),
            activation_score=149.0,
            matched_objects=("venus", "libra", "house:7", "retrograde", "mars"),
        )
    )

    assert synthesis.theme_code == BasicThemeCode.RELATIONSHIP_PATTERN
    assert "appui fort et la limite forte" in synthesis.integration_statement
    assert synthesis.omission_reason is None


def _resolve(theme: ThemeModel):
    """Resout un theme unique dans un contexte horaire complet."""
    return SynthesisResolver().resolve((theme,), eligibility_context=_full_birth_time())[0]


def _theme(
    theme_code: BasicThemeCode,
    *,
    resources: tuple[str, ...],
    constraints: tuple[str, ...],
    tensions: tuple[str, ...],
    activation_score: float,
    matched_objects: tuple[str, ...],
) -> ThemeModel:
    """Cree un ThemeModel actif pour les cas adversariaux."""
    selected_fact_ids = tuple(dict.fromkeys((*resources, *constraints, *tensions)))
    return ThemeModel(
        taxonomy_version="basic-theme-taxonomy.v1",
        theme_code=theme_code,
        activation_score=activation_score,
        priority_level=20,
        resources=resources,
        constraints=constraints,
        tensions=tensions,
        must_mention=selected_fact_ids,
        may_mention=(),
        do_not_mention=(),
        availability=("full_birth_time", "approximate_birth_time", "date_only"),
        compatible_sections=("test_section",),
        advised_vocabulary=("nuance",),
        forbidden_formulations=("formulation interdite",),
        activation_metadata={
            "matched_fact_count": len(selected_fact_ids),
            "matched_objects": matched_objects,
        },
    )


def _full_birth_time() -> EligibilityContext:
    """Autorise les maisons et angles pour les contradictions representatifs."""
    return EligibilityContext(
        birth_time_status="full_birth_time",
        can_use_houses=True,
        can_use_angles=True,
        can_use_house_rulers=True,
        can_use_lunar_nodes_by_house=True,
    )

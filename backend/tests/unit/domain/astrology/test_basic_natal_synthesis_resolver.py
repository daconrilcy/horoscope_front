# Commentaire global: ces tests verrouillent le contrat interne du resolver de synthese Basic.
"""Tests contractuels du resolver de synthese des themes natals Basic."""

from __future__ import annotations

import ast
import inspect

import pytest

from app.domain.astrology.interpretation.basic_natal_eligibility import EligibilityContext
from app.domain.astrology.interpretation.natal_synthesis_resolver import (
    ResolvedThemeSynthesis,
    SynthesisResolver,
    _ensure_controlled_wording,
)
from app.domain.astrology.interpretation.natal_theme_taxonomy import (
    BasicThemeCode,
    ThemeModel,
)


def test_resolver_consumes_active_themes_and_emits_contract_fields() -> None:
    """Le resolver transforme un ThemeModel actif en payload editorial structure."""
    theme = _theme(
        BasicThemeCode.CORE_IDENTITY,
        resources=("sun", "sun-sign"),
        constraints=("sun-combust",),
        tensions=("sun-square-moon",),
        activation_score=162.0,
        matched_objects=("sun", "moon", "combust", "square"),
    )

    resolved = SynthesisResolver().resolve((theme,), eligibility_context=_full_birth_time())

    assert len(resolved) == 1
    payload = resolved[0].to_internal_payload()
    assert payload["theme_code"] == "core_identity"
    assert payload["core_statement"].startswith("core_identity:")
    assert "2 fait(s) de ressource" in payload["resource_statement"]
    assert "1 fait(s) de contrainte" in payload["constraint_statement"]
    assert "nuance explicite" in payload["integration_statement"]
    assert payload["confidence"] == "high"
    assert payload["section_eligible"] is True


def test_one_weak_fact_cannot_be_autonomous_section_candidate() -> None:
    """Un signal faible isole reste rattache a un theme mieux documente."""
    theme = _theme(
        BasicThemeCode.TALENTS_AND_SUPPORTS,
        resources=("air-balance",),
        activation_score=42.0,
        matched_objects=("air",),
    )

    resolved = SynthesisResolver().resolve((theme,), eligibility_context=_full_birth_time())[0]

    assert resolved.section_eligible is False
    assert resolved.omission_reason == "weak_single_fact"
    assert "section autonome" in resolved.constraint_statement


def test_redundant_themes_are_linked_by_shared_facts() -> None:
    """Deux themes appuyes sur les memes faits recoivent un groupe de fusion stable."""
    first = _theme(
        BasicThemeCode.RELATIONSHIP_PATTERN,
        resources=("venus", "venus-house"),
        constraints=("venus-combust",),
        activation_score=132.0,
        matched_objects=("venus", "house:7", "combust"),
    )
    second = _theme(
        BasicThemeCode.RESOURCES_AND_VALUES,
        resources=("venus", "venus-house"),
        constraints=("venus-combust",),
        activation_score=126.0,
        matched_objects=("venus", "house:7", "combust"),
    )

    resolved = SynthesisResolver().resolve((first, second), eligibility_context=_full_birth_time())
    merge_groups = {item.merge_group for item in resolved}

    assert len(merge_groups) == 1
    assert merge_groups.pop() == "shared:venus+venus-combust+venus-house"


def test_date_only_context_downgrades_house_angle_and_mc_surfaces() -> None:
    """Une synthese date-only retire les surfaces maisons, Ascendant et MC."""
    theme = _theme(
        BasicThemeCode.PUBLIC_VOCATION,
        resources=("mc", "house-10"),
        constraints=("saturn-square-mc",),
        activation_score=130.0,
        matched_objects=("mc", "house:10", "angular"),
    )

    resolved = SynthesisResolver().resolve((theme,), eligibility_context=_date_only())[0]

    assert resolved.section_eligible is False
    assert resolved.omission_reason == "birth_time_surface_unavailable"
    assert "maisons, angles et maitres de maisons" in resolved.constraint_statement
    assert "signes, luminaires, aspects et equilibres" in resolved.integration_statement


def test_forbidden_wording_is_denied_before_downstream_narrative() -> None:
    """La denylist rejette les formulations absolues avant tout usage aval."""
    synthesis = ResolvedThemeSynthesis(
        theme_code=BasicThemeCode.CORE_IDENTITY,
        core_statement="core_identity: " + "doit " + "absolument guider la suite.",
        resource_statement="core_identity: ressource controlee.",
        constraint_statement="core_identity: contrainte controlee.",
        integration_statement="core_identity: integration controlee.",
        confidence="medium",
    )

    with pytest.raises(ValueError, match="uncontrolled wording"):
        _ensure_controlled_wording(synthesis)


def test_resolver_keeps_domain_boundary_without_public_renderer_imports() -> None:
    """Le guard AST verifie que le resolver reste un proprietaire domaine pur."""
    import app.domain.astrology.interpretation.natal_synthesis_resolver as resolver_module

    tree = ast.parse(inspect.getsource(resolver_module))
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_modules.update(
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    )

    assert not any("llm_generation" in module for module in imported_modules)
    assert not any(".api" in module for module in imported_modules)


def _theme(
    theme_code: BasicThemeCode,
    *,
    resources: tuple[str, ...] = (),
    constraints: tuple[str, ...] = (),
    tensions: tuple[str, ...] = (),
    activation_score: float = 100.0,
    matched_objects: tuple[str, ...] = (),
) -> ThemeModel:
    """Cree un ThemeModel actif minimal sans refaire l'activation CS-413."""
    selected_fact_ids = tuple(dict.fromkeys((*resources, *constraints, *tensions)))
    return ThemeModel(
        taxonomy_version="basic-theme-taxonomy.v1",
        theme_code=theme_code,
        activation_score=activation_score,
        priority_level=10,
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
    """Autorise les surfaces horaires pour les tests."""
    return EligibilityContext(
        birth_time_status="full_birth_time",
        can_use_houses=True,
        can_use_angles=True,
        can_use_house_rulers=True,
        can_use_lunar_nodes_by_house=True,
    )


def _date_only() -> EligibilityContext:
    """Interdit les surfaces horaires pour les tests date-only."""
    return EligibilityContext(
        birth_time_status="date_only",
        can_use_houses=False,
        can_use_angles=False,
        can_use_house_rulers=False,
        can_use_lunar_nodes_by_house=False,
    )

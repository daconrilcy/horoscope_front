# Commentaire global: ces tests verrouillent le contrat et l'ordre du BasicNatalReadingPlan.
"""Tests du builder de plan natal Basic inspectable."""

from __future__ import annotations

import ast
from pathlib import Path

from app.domain.astrology.interpretation.natal_fact_graph import NatalFactFamily
from app.domain.astrology.interpretation.natal_theme_taxonomy import BasicThemeCode
from tests.unit.domain.astrology.basic_natal_reading_plan_helpers import (
    build_plan,
    date_only_context,
    fact,
    theme,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
PLAN_MODULE = REPO_ROOT / "app/domain/astrology/interpretation/basic_natal_reading_plan.py"


def test_plan_exposes_basic_identity_and_inspectable_sections() -> None:
    """Le plan expose les champs Basic et des sections inspectables."""
    plan = build_plan(_full_facts(), _full_themes())
    payload = plan.to_payload()

    assert payload["level"] == "basic"
    assert payload["locale"] == "fr-FR"
    assert payload["engine_version"] == "basic-natal-reading-v1"
    assert payload["style_constraints"]
    assert [section["section_code"] for section in payload["sections"]] == [
        "synthesis",
        "identity",
        "inner_life",
        "vocation",
        "relationships",
        "talents",
        "tensions",
        "growth",
    ]
    assert len(payload["sections"]) == 8
    assert all(section["required_fact_ids"] for section in payload["sections"])
    assert all(section["supporting_evidence_ids"] for section in payload["sections"])


def test_date_only_plan_omits_houses_angles_mc_asc_and_house_rulers() -> None:
    """Le contexte date-only retire toutes les surfaces dependantes de l'heure."""
    plan = build_plan(_full_facts(), _date_only_themes(), date_only_context())
    payload = plan.to_payload()
    section_codes = [section["section_code"] for section in payload["sections"]]
    required_ids = {
        fact_id for section in payload["sections"] for fact_id in section["required_fact_ids"]
    }

    assert section_codes == ["synthesis", "identity", "inner_life", "values", "action"]
    assert "vocation" not in section_codes
    assert "relationships" not in section_codes
    assert not {"asc", "mc", "house-10", "house-7", "ruler-1"}.intersection(required_ids)
    assert all(
        "angle_fact" in section["forbidden_fact_families"]
        and "house_emphasis_fact" in section["forbidden_fact_families"]
        and "rulership_fact" in section["forbidden_fact_families"]
        for section in payload["sections"]
    )
    assert payload["limitations"][0].startswith("Lecture sans heure de naissance")


def test_salience_controls_section_priority_when_budget_is_tight() -> None:
    """Le budget garde la section optionnelle la mieux documentee par salience."""
    plan = build_plan(_priority_facts(), _priority_themes(), max_sections=4)
    section_codes = [section.section_code for section in plan.sections]

    assert section_codes == ["synthesis", "identity", "inner_life", "action"]
    assert "values" not in section_codes
    action = next(section for section in plan.sections if section.section_code == "action")
    assert action.required_fact_ids[0] == "mars"


def test_forbidden_fact_ids_are_kept_out_of_required_facts() -> None:
    """Les faits voisins interdits restent tracables sans nourrir la section."""
    plan = build_plan(
        (
            fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            fact("venus-square", NatalFactFamily.ASPECT, ("venus", "mars", "square")),
            fact("venus-trine", NatalFactFamily.ASPECT, ("venus", "mars", "trine")),
        ),
        (
            theme(BasicThemeCode.CORE_IDENTITY, ("sun",)),
            theme(
                BasicThemeCode.TENSION_TO_INTEGRATE,
                ("venus-square",),
                do_not_mention=("venus-trine",),
            ),
        ),
    )
    tension = next(section for section in plan.sections if section.section_code == "tensions")

    assert tension.required_fact_ids == ("venus-square",)
    assert tension.forbidden_fact_ids == ("venus-trine",)


def test_reading_plan_builder_stays_in_domain_without_provider_or_api_imports() -> None:
    """AST guard: le plan reste dans le domaine sans import applicatif externe."""
    tree = ast.parse(PLAN_MODULE.read_text(encoding="utf-8"))
    forbidden_import_prefixes = (
        "app.api",
        "app.infra",
        "app.services",
        "fastapi",
        "sqlalchemy",
    )
    forbidden_names = {
        "legacy",
        "compat",
        "shim",
        "fallback",
        "provider",
        "llm_client",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            assert not any(
                node.module == prefix or node.module.startswith(f"{prefix}.")
                for prefix in forbidden_import_prefixes
            )
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert not forbidden_names.intersection(node.value.casefold().split())


def _full_facts():
    """Assemble les faits couvrant l'ordre complet attendu."""
    return (
        fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
        fact("moon", NatalFactFamily.LUMINARY, ("moon", "water")),
        fact("mc", NatalFactFamily.ANGLE, ("mc", "angular"), requires_birth_time=True),
        fact("house-10", NatalFactFamily.HOUSE_EMPHASIS, ("house:10", "angular")),
        fact("venus", NatalFactFamily.PLANET_POSITION, ("venus", "taurus")),
        fact("house-7", NatalFactFamily.HOUSE_EMPHASIS, ("house:7", "venus")),
        fact("jupiter-trine", NatalFactFamily.ASPECT, ("jupiter", "saturn", "trine")),
        fact("venus-square", NatalFactFamily.ASPECT, ("venus", "mars", "square")),
        fact("north-node", NatalFactFamily.NODE, ("north_node", "taurus")),
        fact("node-aspect", NatalFactFamily.ASPECT, ("north_node", "sun", "trine")),
    )


def _full_themes():
    """Assemble les themes canoniques de l'ordre full birth-time."""
    return (
        theme(BasicThemeCode.CORE_IDENTITY, ("sun",), objects=("sun",)),
        theme(BasicThemeCode.EMOTIONAL_PATTERN, ("moon",), objects=("moon", "water")),
        theme(BasicThemeCode.PUBLIC_VOCATION, ("mc", "house-10"), objects=("mc", "house:10")),
        theme(BasicThemeCode.RELATIONSHIP_PATTERN, ("venus", "house-7"), objects=("house:7",)),
        theme(BasicThemeCode.TALENTS_AND_SUPPORTS, ("jupiter-trine",), objects=("trine",)),
        theme(BasicThemeCode.TENSION_TO_INTEGRATE, ("venus-square",), objects=("square",)),
        theme(
            BasicThemeCode.GROWTH_DIRECTION, ("north-node", "node-aspect"), objects=("north_node",)
        ),
    )


def _date_only_themes():
    """Assemble les themes autorises pour un plan date-only."""
    return (
        theme(BasicThemeCode.CORE_IDENTITY, ("sun",), objects=("sun",)),
        theme(BasicThemeCode.EMOTIONAL_PATTERN, ("moon",), objects=("moon", "water")),
        theme(BasicThemeCode.PUBLIC_VOCATION, ("mc", "house-10"), objects=("mc", "house:10")),
        theme(BasicThemeCode.RELATIONSHIP_PATTERN, ("venus", "house-7"), objects=("house:7",)),
        theme(BasicThemeCode.RESOURCES_AND_VALUES, ("venus",), objects=("venus", "taurus")),
        theme(BasicThemeCode.ACTION_AND_DRIVE, ("sun",), objects=("sun",)),
    )


def _priority_facts():
    """Assemble une fixture ou l'action est plus saillante que les valeurs."""
    return (
        fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
        fact("moon", NatalFactFamily.LUMINARY, ("moon",)),
        fact("venus", NatalFactFamily.PLANET_POSITION, ("venus", "taurus")),
        fact("mars", NatalFactFamily.PLANET_POSITION, ("mars", "aries")),
        fact("mars-house", NatalFactFamily.HOUSE_EMPHASIS, ("mars", "house:1")),
        fact("mars-domicile", NatalFactFamily.CONDITION, ("mars", "domicile")),
    )


def _priority_themes():
    """Assemble les themes concurrents du test de budget."""
    return (
        theme(BasicThemeCode.CORE_IDENTITY, ("sun",), objects=("sun",)),
        theme(BasicThemeCode.EMOTIONAL_PATTERN, ("moon",), objects=("moon",)),
        theme(BasicThemeCode.RESOURCES_AND_VALUES, ("venus",), activation_score=70.0),
        theme(
            BasicThemeCode.ACTION_AND_DRIVE,
            ("mars", "mars-house", "mars-domicile"),
            activation_score=180.0,
            objects=("mars", "house:1", "domicile"),
        ),
    )

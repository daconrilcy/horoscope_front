# Commentaire global: ces tests verrouillent le contrat de taxonomie narrative Basic.
"""Tests unitaires du catalogue versionne des themes natals Basic."""

from __future__ import annotations

import ast
from pathlib import Path

from app.domain.astrology.interpretation.natal_theme_taxonomy import (
    NATAL_NARRATIVE_THEME_TAXONOMY_VERSION,
    BasicThemeCode,
    NatalNarrativeThemeTaxonomy,
)
from app.domain.astrology.reading.basic_natal_contracts import (
    BASIC_NATAL_THEME_TAXONOMY_VERSION,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
TAXONOMY_MODULE = REPO_ROOT / "app/domain/astrology/interpretation/natal_theme_taxonomy.py"
PUBLIC_BOUNDARY_MODULES = (
    REPO_ROOT / "app/domain/astrology/interpretation/llm_astrology_input_v1.py",
    REPO_ROOT / "app/services/llm_generation/natal/narrative_natal_reading_builder.py",
)
RAW_PUBLIC_FIELDS = (
    "theme_code",
    "activation_score",
    "must_mention",
    "may_mention",
    "do_not_mention",
)


def test_taxonomy_exposes_version_and_ten_canonical_basic_codes() -> None:
    """Le catalogue Basic expose uniquement les dix codes versionnes attendus."""
    payload = NatalNarrativeThemeTaxonomy().to_contract_payload()

    assert NATAL_NARRATIVE_THEME_TAXONOMY_VERSION == BASIC_NATAL_THEME_TAXONOMY_VERSION
    assert payload["taxonomy_version"] == NATAL_NARRATIVE_THEME_TAXONOMY_VERSION
    assert payload["theme_codes"] == [theme_code.value for theme_code in BasicThemeCode]
    assert len(payload["themes"]) == 10


def test_each_theme_declares_contractual_sections_vocabulary_and_availability() -> None:
    """Chaque theme porte les champs editoriaux requis par le contrat."""
    for definition in NatalNarrativeThemeTaxonomy().catalog:
        payload = definition.to_contract_payload()

        assert payload["triggers"]["families"]
        assert payload["exclusions"]
        assert payload["availability"]
        assert payload["compatible_sections"]
        assert payload["advised_vocabulary"]
        assert payload["forbidden_formulations"]
        assert all(item != "" for item in payload["forbidden_formulations"])


def test_taxonomy_owner_does_not_recalculate_astrology_runtime_data() -> None:
    """AST guard: la taxonomie consomme les faits existants sans moteur astrologique."""
    tree = ast.parse(TAXONOMY_MODULE.read_text(encoding="utf-8"))
    forbidden_calls = {
        "calculate_" + "as" + "pect",
        "calculate_" + "house",
        "calculate_" + "dig" + "nity",
        "Swiss" + "Eph",
        "s" + "we",
        "House" + "RulerResolver",
    }
    forbidden_import_prefixes = ("app.api", "app.infra", "app.services", "fastapi", "sqlalchemy")

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            assert _call_name(node.func) not in forbidden_calls
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            assert not any(
                node.module == prefix or node.module.startswith(f"{prefix}.")
                for prefix in forbidden_import_prefixes
            )


def test_public_narrative_boundaries_do_not_reference_raw_theme_internals() -> None:
    """Les champs internes de theme restent absents des projections publiques."""
    for module_path in PUBLIC_BOUNDARY_MODULES:
        constants = _string_constants(module_path)
        for field in RAW_PUBLIC_FIELDS:
            assert field not in constants


def _string_constants(module_path: Path) -> set[str]:
    """Retourne les constantes chaine d'un module Python."""
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    return {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)}


def _call_name(node: ast.AST) -> str:
    """Retourne le nom simple appele par un noeud AST."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""

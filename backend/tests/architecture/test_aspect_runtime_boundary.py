"""Gardes d'architecture de la frontiere runtime aspectuelle CS-229."""

from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path

from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectStructuralDefinitionRuntimeData,
)
from app.domain.astrology.runtime.aspect_modifiers import AspectStructuralModifierRuntimeData
from app.domain.astrology.runtime.aspect_runtime_data import AspectStructuralRuntimeData

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent
DOC_PATH = REPO_ROOT / "docs/architecture/astrology-runtime-surfaces.md"
RUNTIME_ROOT = BACKEND_ROOT / "app/domain/astrology/runtime"
BUILDER_PATH = BACKEND_ROOT / "app/domain/astrology/builders/aspect_runtime_builder.py"
CALCULATOR_PATH = BACKEND_ROOT / "app/domain/astrology/calculators/aspects.py"

FORBIDDEN_STRUCTURAL_FIELDS = {
    "default_valence",
    "interpretive_valence",
    "energy_type",
    "interpretive_weight",
    "meaning",
    "narrative",
    "prompt",
    "llm",
}


def test_aspect_runtime_layers_are_documented() -> None:
    """La documentation definit les quatre couches runtime/projection."""
    content = DOC_PATH.read_text(encoding="utf-8")

    for expected in (
        "Aspect runtime layers",
        "Structural aspect runtime",
        "Interpretive aspect runtime",
        "Public aspect projection",
        "Legacy aspect projection",
        "structural runtime",
        "interpretive runtime",
        "public projection",
        "legacy projection",
    ):
        assert expected in content


def test_structural_contract_classes_do_not_declare_interpretive_fields() -> None:
    """Les contrats structurels ne portent aucun champ interpretatif."""
    for contract in (
        AspectStructuralRuntimeData,
        AspectStructuralDefinitionRuntimeData,
        AspectStructuralModifierRuntimeData,
    ):
        declared_fields = {field.name for field in fields(contract)}
        assert declared_fields.isdisjoint(FORBIDDEN_STRUCTURAL_FIELDS)


def test_structural_runtime_class_has_no_forbidden_annotations() -> None:
    """AST guard: la classe structurelle ne reference pas les termes interdits."""
    module_path = RUNTIME_ROOT / "aspect_runtime_data.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    class_node = _class_node(tree, "AspectStructuralRuntimeData")
    source_segment = ast.get_source_segment(module_path.read_text(encoding="utf-8"), class_node)

    assert source_segment is not None
    assert not any(forbidden in source_segment for forbidden in FORBIDDEN_STRUCTURAL_FIELDS)


def test_structural_modifiers_do_not_carry_interpretive_weight() -> None:
    """AST guard: les modifiers structurels ne portent pas de poids interpretatif."""
    modifier_fields = {field.name for field in fields(AspectStructuralModifierRuntimeData)}

    assert "interpretive_weight" not in modifier_fields


def test_runtime_builder_does_not_consume_interpretive_profile_contract() -> None:
    """Le builder structurel ne depend pas du profil interpretatif cible."""
    source = BUILDER_PATH.read_text(encoding="utf-8")

    assert "AspectInterpretiveProfileRuntimeData" not in source
    assert "AspectInterpretiveHintsRuntimeData" not in source


def test_structural_calculator_and_builder_do_not_reference_interpretive_fields() -> None:
    """AST guard CS-230: calculateur et builder restent structurels."""
    offenders: list[str] = []
    for path in (CALCULATOR_PATH, BUILDER_PATH):
        source = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRUCTURAL_FIELDS:
            if forbidden in source:
                offenders.append(f"{path}:{forbidden}")

    assert offenders == []


def test_structural_modules_do_not_produce_prompt_or_llm_calls() -> None:
    """AST guard: le runtime structurel ne produit ni prompt ni appel LLM."""
    checked_paths = (
        RUNTIME_ROOT / "aspect_runtime_data.py",
        RUNTIME_ROOT / "aspect_modifiers.py",
        BUILDER_PATH,
    )
    offenders: list[str] = []
    for path in checked_paths:
        source = path.read_text(encoding="utf-8")
        for forbidden in ("prompt", "llm", "OpenAI", "AIEngineAdapter", "chat.completions"):
            if forbidden in source:
                offenders.append(f"{path}:{forbidden}")

    assert offenders == []


def _class_node(tree: ast.AST, class_name: str) -> ast.ClassDef:
    """Retourne une classe par nom dans un module AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    raise AssertionError(f"class not found: {class_name}")

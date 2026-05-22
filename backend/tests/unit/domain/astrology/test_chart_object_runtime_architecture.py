"""Tests d'architecture du runtime chart-object unifie."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
NEW_MODULES = (
    REPO_ROOT / "app/domain/astrology/runtime/chart_object_runtime_data.py",
    REPO_ROOT / "app/domain/astrology/builders/chart_object_runtime_builder.py",
)
CALCULATOR_ROOTS = (
    REPO_ROOT / "app/domain/astrology/calculators",
    REPO_ROOT / "app/domain/astrology/dignities",
    REPO_ROOT / "app/domain/astrology/dominance",
    REPO_ROOT / "app/domain/astrology/advanced_conditions",
    REPO_ROOT / "app/domain/astrology/planetary_conditions",
    REPO_ROOT / "app/domain/astrology/interpretation",
    REPO_ROOT / "app/domain/astrology/interpretation_adapters",
)
ASPECT_ENGINE_MODULES = (
    REPO_ROOT / "app/domain/astrology/calculators/aspects.py",
    REPO_ROOT / "app/domain/astrology/calculators/aspect_inputs.py",
)
FORBIDDEN_ASPECT_BUILDERS = (
    "PlanetAspectBodyBuilder",
    "AngleAspectBodyBuilder",
    "AstralPointAspectBodyBuilder",
    "FixedStarAspectBodyBuilder",
)
FORBIDDEN_ASPECT_COLLECTION_NAMES = (
    "planet_positions",
    "astral_points",
    "angles",
    "fixed_stars",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "app.api",
    "app.infra",
    "app." + "infrastructure",
    "app.services",
    "sqlalchemy",
    "fastapi",
    "pydantic",
)


def test_new_chart_object_modules_keep_domain_pure_dependencies() -> None:
    """Les nouveaux modules restent hors API, DB, services et Pydantic."""
    for module_path in NEW_MODULES:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names = tuple(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_names = (node.module,)
            else:
                continue
            assert not any(
                imported_name == prefix or imported_name.startswith(f"{prefix}.")
                for imported_name in imported_names
                for prefix in FORBIDDEN_IMPORT_PREFIXES
            ), f"{module_path} imports forbidden dependency {imported_names}"


def test_business_calculators_do_not_branch_on_chart_object_type() -> None:
    """Les calculateurs metier ne selectionnent pas par `object_type`."""
    offenders: list[str] = []
    for root in CALCULATOR_ROOTS:
        if not root.exists():
            continue
        for module_path in root.rglob("*.py"):
            tree = ast.parse(module_path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if _branches_on_object_type(node):
                    offenders.append(f"{module_path}:{getattr(node, 'lineno', '?')}")

    assert offenders == []


def test_aspect_engine_does_not_reintroduce_specialized_inputs() -> None:
    """Le moteur d'aspects ne revient pas aux collections ou builders specialises."""
    offenders: list[str] = []
    for module_path in ASPECT_ENGINE_MODULES:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        source = module_path.read_text(encoding="utf-8")
        for node in ast.walk(tree):
            if _uses_forbidden_aspect_collection(node):
                offenders.append(f"{module_path}:{getattr(node, 'lineno', '?')}")
        for builder_name in FORBIDDEN_ASPECT_BUILDERS:
            if builder_name in source:
                offenders.append(f"{module_path}:builder:{builder_name}")

    assert offenders == []


def _branches_on_object_type(node: ast.AST) -> bool:
    """Detecte les comparaisons et match explicites sur `object_type`."""
    if isinstance(node, ast.Compare):
        return _is_object_type_reference(node.left) or any(
            _is_object_type_reference(comparator) for comparator in node.comparators
        )
    if isinstance(node, ast.Match):
        return _is_object_type_reference(node.subject)
    return False


def _is_object_type_reference(node: ast.AST) -> bool:
    """Reconnait `object_type` et `obj.object_type` dans un AST."""
    return (
        isinstance(node, ast.Name)
        and node.id == "object_type"
        or isinstance(node, ast.Attribute)
        and node.attr == "object_type"
    )


def _uses_forbidden_aspect_collection(node: ast.AST) -> bool:
    """Detecte les anciens noms de collections dans les modules d'aspects."""
    return isinstance(node, ast.Name) and node.id in FORBIDDEN_ASPECT_COLLECTION_NAMES

# Guards d'architecture pour la gouvernance doctrinale astrologique.
"""Bloque les nouveaux marqueurs de regles non classes dans le modele canonique."""

from __future__ import annotations

import ast
from pathlib import Path

from app.domain.astrology.runtime.astrology_doctrine_governance import (
    GOVERNED_RULE_SOURCE_SURFACES,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DOMAIN_ROOT = REPO_ROOT / "backend/app/domain/astrology"
RULE_MARKERS = ("threshold", "weight", "profile", "school", "doctrine")


def test_rule_marker_surfaces_are_declared_in_doctrine_governance() -> None:
    """Les surfaces contenant des marqueurs de regles restent classees."""
    offenders: list[str] = []
    for module_path in _python_files(DOMAIN_ROOT):
        relative_path = _repo_relative(module_path)
        if relative_path in GOVERNED_RULE_SOURCE_SURFACES:
            continue
        if _contains_rule_marker(module_path):
            offenders.append(relative_path)

    assert offenders == []


def test_unclassified_new_rule_marker_fails_guard() -> None:
    """Un nouveau fichier avec seuil, poids, profil ou ecole doit etre classe."""
    offender = _unclassified_rule_marker(
        path=REPO_ROOT / "backend/app/domain/astrology/runtime/new_school_weights.py",
        source="SCHOOL_WEIGHT = 1\n",
    )

    assert offender == "backend/app/domain/astrology/runtime/new_school_weights.py"


def _python_files(root: Path) -> tuple[Path, ...]:
    """Retourne les fichiers Python du domaine hors caches."""
    return tuple(
        path
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
        and ".ruff_cache" not in path.parts
    )


def _contains_rule_marker(module_path: Path) -> bool:
    """Analyse l'AST pour trouver un marqueur de regle gouvernee."""
    return _unclassified_rule_marker(path=module_path, source=module_path.read_text()) is not None


def _unclassified_rule_marker(path: Path, source: str) -> str | None:
    """Retourne le chemin non classe si un marqueur gouverne est detecte."""
    relative_path = _repo_relative(path)
    if relative_path in GOVERNED_RULE_SOURCE_SURFACES:
        return None
    tree = ast.parse(source)
    for node in ast.walk(tree):
        values = _node_marker_values(node)
        if any(_has_rule_marker(value) for value in values):
            return relative_path
    return None


def _node_marker_values(node: ast.AST) -> tuple[str, ...]:
    """Extrait les noms AST significatifs pour le guard."""
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        return (node.attr,)
    if isinstance(node, ast.arg):
        return (node.arg,)
    if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
        return (node.name,)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return (node.value,)
    return ()


def _has_rule_marker(value: str) -> bool:
    """Detecte un marqueur de gouvernance dans un nom ou libelle."""
    normalized = value.lower()
    return any(marker in normalized for marker in RULE_MARKERS)


def _repo_relative(path: Path) -> str:
    """Produit un chemin stable relatif au depot."""
    return path.relative_to(REPO_ROOT).as_posix()

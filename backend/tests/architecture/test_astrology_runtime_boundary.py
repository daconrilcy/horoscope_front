# Gardes d'architecture de la frontiere runtime structurel et interpretatif.
"""Verifie que les calculateurs structurels restent separes des adapters interpretatifs."""

from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path

from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectStructuralDefinitionRuntimeData,
)
from app.domain.astrology.runtime.runtime_reference import AspectReferenceData, AspectReferenceSet

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent
DOMAIN_ROOT = BACKEND_ROOT / "app/domain/astrology"
DOC_PATH = REPO_ROOT / "docs/architecture/astrology-runtime-surfaces.md"

STRUCTURAL_ROOTS = (
    DOMAIN_ROOT / "calculators",
    DOMAIN_ROOT / "runtime",
    DOMAIN_ROOT / "builders",
    DOMAIN_ROOT / "dominance",
    DOMAIN_ROOT / "fixed_stars",
    DOMAIN_ROOT / "dignities",
    DOMAIN_ROOT / "planetary_conditions",
    DOMAIN_ROOT / "advanced_conditions",
)
INTERPRETIVE_ROOTS = (
    DOMAIN_ROOT / "interpretation",
    DOMAIN_ROOT / "interpretation_adapters",
)
EXCLUDED_PATH_PARTS = frozenset(
    {"tests", "fixtures", "evidence", "__pycache__", ".pytest_cache", ".ruff_cache"}
)
FORBIDDEN_STRUCTURAL_TOKENS = frozenset(
    {
        "default_valence",
        "interpretive_valence",
        "energy_type",
        "interpretive_weight",
        "meaning",
        "narrative",
        "prompt",
        "llm",
        "OpenAI",
        "AIEngineAdapter",
    }
)
FORBIDDEN_RECALCULATION_SYMBOLS = frozenset(
    {
        "calculate_major_aspects",
        "calculate_interchart_aspects",
        "resolve_orb",
        "PlanetDominanceEngine",
        "FixedStarConjunctionCalculator",
        "EssentialDignityCalculator",
        "AccidentalDignityCalculator",
    }
)
INTERPRETIVE_TOKEN_ALLOWLIST = {
    (
        "runtime/aspect_calculation_contracts.py",
        "AspectInterpretiveProfileRuntimeData",
        "default_valence",
    ): ("Profil interpretatif separe de la definition structurelle.", "Permanent."),
    (
        "runtime/aspect_calculation_contracts.py",
        "AspectInterpretiveProfileRuntimeData",
        "interpretive_valence",
    ): ("Profil interpretatif separe de la definition structurelle.", "Permanent."),
    (
        "runtime/aspect_calculation_contracts.py",
        "AspectInterpretiveProfileRuntimeData",
        "energy_type",
    ): ("Profil interpretatif separe de la definition structurelle.", "Permanent."),
    (
        "runtime/aspect_calculation_contracts.py",
        "AspectInterpretiveProfileRuntimeData.__post_init__",
        "default_valence",
    ): ("Profil interpretatif separe de la definition structurelle.", "Permanent."),
    (
        "runtime/aspect_calculation_contracts.py",
        "AspectInterpretiveProfileRuntimeData.__post_init__",
        "interpretive_valence",
    ): ("Profil interpretatif separe de la definition structurelle.", "Permanent."),
    (
        "runtime/aspect_calculation_contracts.py",
        "AspectInterpretiveProfileRuntimeData.__post_init__",
        "energy_type",
    ): ("Profil interpretatif separe de la definition structurelle.", "Permanent."),
    (
        "runtime/aspect_runtime_data.py",
        "AspectInterpretiveHintsRuntimeData",
        "default_valence",
    ): ("Hints interpretatifs types pour adapters, sans recalcul structurel.", "Permanent."),
    (
        "runtime/aspect_runtime_data.py",
        "AspectInterpretiveHintsRuntimeData",
        "interpretive_valence",
    ): ("Hints interpretatifs types pour adapters, sans recalcul structurel.", "Permanent."),
    (
        "runtime/aspect_runtime_data.py",
        "AspectInterpretiveHintsRuntimeData",
        "energy_type",
    ): ("Hints interpretatifs types pour adapters, sans recalcul structurel.", "Permanent."),
    (
        "runtime/aspect_runtime_data.py",
        "AspectInterpretiveHintsRuntimeData",
        "interpretive_weight",
    ): ("Poids interpretatif optionnel reserve aux hints.", "Permanent."),
    (
        "runtime/aspect_runtime_data.py",
        "AspectInterpretiveHintsRuntimeData.__post_init__",
        "default_valence",
    ): ("Hints interpretatifs types pour adapters, sans recalcul structurel.", "Permanent."),
    (
        "runtime/aspect_runtime_data.py",
        "AspectInterpretiveHintsRuntimeData.__post_init__",
        "interpretive_valence",
    ): ("Hints interpretatifs types pour adapters, sans recalcul structurel.", "Permanent."),
    (
        "runtime/aspect_runtime_data.py",
        "AspectInterpretiveHintsRuntimeData.__post_init__",
        "energy_type",
    ): ("Hints interpretatifs types pour adapters, sans recalcul structurel.", "Permanent."),
    (
        "runtime/aspect_runtime_data.py",
        "AspectInterpretiveHintsRuntimeData.__post_init__",
        "interpretive_weight",
    ): ("Poids interpretatif optionnel reserve aux hints.", "Permanent."),
    (
        "runtime/aspect_runtime_data.py",
        "resolve_aspect_interpretive_hints",
        "default_valence",
    ): ("Resolver dedie aux hints depuis un profil interpretatif.", "Permanent."),
    (
        "runtime/aspect_runtime_data.py",
        "resolve_aspect_interpretive_hints",
        "interpretive_valence",
    ): ("Resolver dedie aux hints depuis un profil interpretatif.", "Permanent."),
    (
        "runtime/aspect_runtime_data.py",
        "resolve_aspect_interpretive_hints",
        "energy_type",
    ): ("Resolver dedie aux hints depuis un profil interpretatif.", "Permanent."),
}


def test_structural_runtime_does_not_expose_interpretive_fields() -> None:
    """AST guard: les zones structurelles ne portent pas de tokens interpretatifs."""
    offenders: list[str] = []
    for module_path in _python_files(STRUCTURAL_ROOTS):
        relative_path = _relative_domain_path(module_path)
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for occurrence in _token_occurrences(tree):
            key = (relative_path, occurrence.owner, occurrence.token)
            if key in INTERPRETIVE_TOKEN_ALLOWLIST:
                continue
            if occurrence.token in FORBIDDEN_STRUCTURAL_TOKENS:
                offenders.append(
                    f"{relative_path}:{occurrence.line}:{occurrence.owner}:{occurrence.token}"
                )

    assert offenders == []


def test_interpretive_adapters_do_not_recalculate_structural_facts() -> None:
    """Les adapters interpretatifs enrichissent les faits sans rappeler les calculateurs."""
    offenders: list[str] = []
    for module_path in _python_files(INTERPRETIVE_ROOTS):
        relative_path = _relative_domain_path(module_path)
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for occurrence in _token_occurrences(tree):
            if occurrence.token in FORBIDDEN_RECALCULATION_SYMBOLS:
                offenders.append(
                    f"{relative_path}:{occurrence.line}:{occurrence.owner}:{occurrence.token}"
                )

    assert offenders == []


def test_runtime_boundary_allowlist_entries_are_complete() -> None:
    """Chaque exception nomme chemin, champ, raison et sortie ou permanence."""
    assert INTERPRETIVE_TOKEN_ALLOWLIST
    for (relative_path, owner, field_name), (
        reason,
        decision,
    ) in INTERPRETIVE_TOKEN_ALLOWLIST.items():
        assert relative_path.endswith(".py")
        assert owner
        assert field_name
        assert reason
        assert decision == "Permanent."


def test_runtime_boundary_layers_are_documented() -> None:
    """La documentation declare les couches et les chemins autorises."""
    content = DOC_PATH.read_text(encoding="utf-8")
    for expected in (
        "Runtime boundary matrix CS-231",
        "structural runtime",
        "interpretive runtime",
        "public projection",
        "legacy projection",
        "Allowed interpretive field paths",
        "default_valence",
        "interpretive_valence",
        "energy_type",
        "interpretive_weight",
    ):
        assert expected in content


def test_historical_fixtures_are_excluded_by_explicit_paths() -> None:
    """Les chemins historiques sont exclus par parties de chemin explicites."""
    assert {"tests", "fixtures", "evidence"}.issubset(EXCLUDED_PATH_PARTS)
    for module_path in _python_files(STRUCTURAL_ROOTS + INTERPRETIVE_ROOTS):
        assert not (set(module_path.parts) & EXCLUDED_PATH_PARTS)


def test_structural_reference_contracts_do_not_require_interpretive_fields() -> None:
    """La vue referentielle structurelle ne force pas les champs interpretatifs."""
    structural_fields = {field.name for field in fields(AspectStructuralDefinitionRuntimeData)}
    reference_fields = {field.name for field in fields(AspectReferenceData)}
    reference_set_fields = {field.name for field in fields(AspectReferenceSet)}

    assert structural_fields.isdisjoint(
        {"default_valence", "interpretive_valence", "energy_type", "interpretive_weight"}
    )
    assert reference_fields.isdisjoint(
        {"default_valence", "interpretive_valence", "energy_type", "interpretive_weight"}
    )
    assert {"structural_definitions", "interpretive_profiles"}.issubset(reference_set_fields)


def test_aspect_interpretive_temporary_allowlists_are_removed() -> None:
    """AST guard: aucune exception Temporary aspectuelle ne reste active."""
    assert all(
        decision != "Temporary."
        for _key, (_reason, decision) in INTERPRETIVE_TOKEN_ALLOWLIST.items()
    )


def test_future_structural_calculators_are_covered_by_explicit_zones() -> None:
    """Les futurs calculateurs Python restent couverts par les racines structurelles."""
    calculator_root = DOMAIN_ROOT / "calculators"

    assert calculator_root in STRUCTURAL_ROOTS
    assert all(path.is_file() for path in _python_files((calculator_root,)))


class _Occurrence:
    """Occurrence AST d'un token utile au diagnostic d'architecture."""

    def __init__(self, token: str, owner: str, line: int) -> None:
        self.token = token
        self.owner = owner
        self.line = line


def _python_files(roots: tuple[Path, ...]) -> tuple[Path, ...]:
    """Retourne les modules Python couverts hors caches, tests et fixtures."""
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        files.extend(
            path for path in root.rglob("*.py") if not (set(path.parts) & EXCLUDED_PATH_PARTS)
        )
    return tuple(sorted(files))


def _relative_domain_path(path: Path) -> str:
    """Produit un chemin stable depuis le domaine astrology."""
    return path.relative_to(DOMAIN_ROOT).as_posix()


def _token_occurrences(tree: ast.AST) -> tuple[_Occurrence, ...]:
    """Extrait les noms, attributs et constantes textuelles porteurs de tokens."""
    visitor = _TokenVisitor()
    visitor.visit(tree)
    return tuple(visitor.occurrences)


class _TokenVisitor(ast.NodeVisitor):
    """Visiteur AST conservant le proprietaire courant d'une occurrence."""

    def __init__(self) -> None:
        self._owners: list[str] = ["module"]
        self.occurrences: list[_Occurrence] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visite une classe comme owner d'architecture."""
        self._with_owner(node.name, node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visite une fonction synchrone comme owner d'architecture."""
        self._with_owner(node.name, node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visite une fonction asynchrone comme owner d'architecture."""
        self._with_owner(node.name, node)

    def visit_Name(self, node: ast.Name) -> None:
        """Capture les noms directs."""
        self._add_tokens_from_text(node.id, node.lineno)

    def visit_arg(self, node: ast.arg) -> None:
        """Capture les arguments nommes."""
        self._add_tokens_from_text(node.arg, node.lineno)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Capture les attributs utilises."""
        self._add_tokens_from_text(node.attr, node.lineno)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        """Capture les tokens presents dans les constantes textuelles."""
        if isinstance(node.value, str):
            for token in FORBIDDEN_STRUCTURAL_TOKENS | FORBIDDEN_RECALCULATION_SYMBOLS:
                if token in node.value:
                    self._add(token, node.lineno)

    def _with_owner(self, owner: str, node: ast.AST) -> None:
        """Empile un owner AST pendant la visite."""
        parent = self._owners[-1]
        qualified_owner = owner if parent == "module" else f"{parent}.{owner}"
        self._owners.append(qualified_owner)
        self.generic_visit(node)
        self._owners.pop()

    def _add(self, token: str, line: int) -> None:
        """Ajoute une occurrence si le token est surveille."""
        if token in FORBIDDEN_STRUCTURAL_TOKENS or token in FORBIDDEN_RECALCULATION_SYMBOLS:
            self.occurrences.append(_Occurrence(token=token, owner=self._owners[-1], line=line))

    def _add_tokens_from_text(self, text: str, line: int) -> None:
        """Capture les tokens interdits meme inclus dans un identifiant."""
        watched_tokens = FORBIDDEN_STRUCTURAL_TOKENS | FORBIDDEN_RECALCULATION_SYMBOLS
        for token in watched_tokens:
            if token in text:
                self._add(token, line)

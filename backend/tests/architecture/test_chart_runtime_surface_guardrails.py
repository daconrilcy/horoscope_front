# Tests d'architecture contre le retour aux surfaces runtime legacy.
"""Controle les lectures directes et selections interdites hors allowlist."""

from __future__ import annotations

import ast
import re
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DOMAIN_ROOT = BACKEND_ROOT / "app/domain/astrology"

LEGACY_FIELDS = frozenset(
    {
        "planet_positions",
        "astral_points",
        "advanced_conditions",
        "dignity_results",
        "dignities",
        "fixed_star_conjunctions",
        "houses",
        "angles",
    }
)
LEGACY_ATTRIBUTE_ALLOWLIST = {
    ("interpretation/astral_point_interpretation.py", "astral_points"): (
        "Service interpretatif legacy existant; migration future vers chart_objects."
    ),
}
CHART_OBJECT_TYPE_ALLOWLIST = {
    "builders/chart_object_runtime_builder.py": "Owner canonique de projection vers types runtime.",
    "runtime/chart_object_capability_taxonomy.py": "Owner canonique de la matrice de familles.",
    "runtime/chart_object_runtime_data.py": "Declaration du contrat enum canonique.",
}
SPECIALIZED_BUILDER_ALLOWLIST = {
    ("condition/planet_condition_signal_builder.py", "PlanetConditionSignalBuilder"): (
        "Builder de signaux de conditions existant, non specialise par surface runtime."
    ),
}
FORBIDDEN_TYPE_MEMBERS = frozenset(
    {"PLANET", "ANGLE", "FIXED_STAR", "LUMINARY", "ASTRAL_POINT", "HOUSE_CUSP"}
)
FORBIDDEN_BUILDER_PREFIXES = ("Planet", "Angle", "AstralPoint", "FixedStar")
LOCAL_THRESHOLD_ALLOWLIST = {
    ("ephemeris_provider.py", "0.01"): "Tolerance d'audit ephemeride existante.",
    ("runtime/astronomical_proof.py", "0.01"): "Tolerance canonique CS-250 SwissEph.",
    ("runtime/astronomical_proof.py", "17"): "Jour ISO du cas golden topocentrique CS-250.",
    ("builders/aspect_runtime_builder.py", "0.01"): "Protection numerique de projection aspect.",
    ("interpretation/aspect_strength.py", "0.01"): "Protection numerique interpretative existante.",
    ("planetary_conditions/contracts.py", "17.0"): "Constante nommee de contrat cazimi.",
    ("planetary_conditions/contracts.py", "8.5"): "Constante nommee de contrat combustion.",
}
FORBIDDEN_THRESHOLD_PATTERN = re.compile(r"\b(?:17\.0|8\.5|0\.2833|0\.01|17)\b")


def test_domain_code_does_not_read_legacy_surfaces_from_natal_result() -> None:
    """Les nouveaux consommateurs ne lisent pas les collections historiques."""
    offenders: list[str] = []
    for module_path in _python_files(DOMAIN_ROOT):
        relative_path = _relative(module_path)
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        natal_result_names = _natal_result_names(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute) or node.attr not in LEGACY_FIELDS:
                continue
            if not isinstance(node.value, ast.Name) or node.value.id not in natal_result_names:
                continue
            if (relative_path, node.attr) in LEGACY_ATTRIBUTE_ALLOWLIST:
                continue
            offenders.append(f"{relative_path}:{node.lineno}:{node.attr}")

    assert offenders == []


def test_domain_code_does_not_route_business_logic_by_object_type() -> None:
    """La logique metier ne revient pas aux comparaisons `object_type`."""
    offenders: list[str] = []
    for module_path in _python_files(DOMAIN_ROOT):
        relative_path = _relative(module_path)
        if relative_path in CHART_OBJECT_TYPE_ALLOWLIST:
            continue
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if _branches_on_object_type(node) or _references_forbidden_chart_object_type(node):
                offenders.append(f"{relative_path}:{getattr(node, 'lineno', '?')}")

    assert offenders == []


def test_chart_object_capability_taxonomy_is_single_runtime_owner() -> None:
    """La matrice de capacites reste sous l'owner runtime canonique."""
    offenders: list[str] = []
    expected_owner = "runtime/chart_object_capability_taxonomy.py"
    for module_path in _python_files(DOMAIN_ROOT):
        relative_path = _relative(module_path)
        if relative_path == expected_owner:
            continue
        source = module_path.read_text(encoding="utf-8")
        if "CHART_OBJECT_CAPABILITY_TAXONOMY_DECLARATIONS" in source:
            offenders.append(relative_path)

    assert offenders == []


def test_domain_code_does_not_add_specialized_runtime_builders() -> None:
    """Les builders par famille d'objet restent interdits hors decision nommee."""
    offenders: list[str] = []
    for module_path in _python_files(DOMAIN_ROOT):
        relative_path = _relative(module_path)
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if not node.name.endswith("Builder") or not node.name.startswith(
                FORBIDDEN_BUILDER_PREFIXES
            ):
                continue
            if (relative_path, node.name) in SPECIALIZED_BUILDER_ALLOWLIST:
                continue
            offenders.append(f"{relative_path}:{node.lineno}:{node.name}")

    assert offenders == []


def test_domain_code_does_not_add_local_magic_thresholds() -> None:
    """Les seuils locaux couverts par CS-224 restent bornes aux owners existants."""
    offenders: list[str] = []
    for module_path in _python_files(DOMAIN_ROOT):
        relative_path = _relative(module_path)
        source = module_path.read_text(encoding="utf-8")
        for match in FORBIDDEN_THRESHOLD_PATTERN.finditer(source):
            threshold = match.group(0)
            if (relative_path, threshold) in LOCAL_THRESHOLD_ALLOWLIST:
                continue
            offenders.append(f"{relative_path}:{threshold}")

    assert offenders == []


def _python_files(root: Path) -> tuple[Path, ...]:
    """Retourne les fichiers Python du domaine hors caches."""
    return tuple(
        path
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
        and ".ruff_cache" not in path.parts
    )


def _relative(path: Path) -> str:
    """Produit un chemin stable pour les allowlists."""
    return path.relative_to(DOMAIN_ROOT).as_posix()


def _is_name(node: ast.AST, expected: str) -> bool:
    """Reconnait un nom AST exact."""
    return isinstance(node, ast.Name) and node.id == expected


def _natal_result_names(tree: ast.AST) -> frozenset[str]:
    """Identifie les variables locales qui portent explicitement un NatalResult."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.arg) and _annotation_names_natal_result(node.annotation):
            names.add(node.arg)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if _annotation_names_natal_result(node.annotation):
                names.add(node.target.id)
        if isinstance(node, ast.Assign) and _is_build_natal_result_call(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return frozenset(names)


def _annotation_names_natal_result(annotation: ast.AST | None) -> bool:
    """Reconnait les annotations directes ou chaînees vers NatalResult."""
    if isinstance(annotation, ast.Name):
        return annotation.id == "NatalResult"
    if isinstance(annotation, ast.Attribute):
        return annotation.attr == "NatalResult"
    if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        return annotation.value.endswith("NatalResult")
    return False


def _is_build_natal_result_call(node: ast.AST) -> bool:
    """Detecte les resultats produits par le builder natal public."""
    if not isinstance(node, ast.Call):
        return False
    return (
        isinstance(node.func, ast.Name)
        and node.func.id == "build_natal_result"
        or isinstance(node.func, ast.Attribute)
        and node.func.attr == "build_natal_result"
    )


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


def _references_forbidden_chart_object_type(node: ast.AST) -> bool:
    """Detecte les membres enum de famille hors owner de projection."""
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "ChartObjectType"
        and node.attr in FORBIDDEN_TYPE_MEMBERS
    )

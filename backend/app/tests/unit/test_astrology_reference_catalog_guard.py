"""Garde la convergence des référentiels astrologiques DB et JSON."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def _forbidden_file_name() -> str:
    """Construit le nom singulier interdit sans le réintroduire en clair."""
    return "astral_aspect_" + "family.json"


def _forbidden_symbols() -> set[str]:
    """Liste les anciens symboles de duplication que le code actif ne doit plus définir."""
    return {
        "ASPECT_FAMILY_" + "ROWS",
        "ASPECT_" + "ROWS",
        "DEFAULT_ASPECT_" + "ORBS",
        "MAJOR_" + "ASPECTS",
        "MINOR_" + "ASPECTS",
        "LUM" + "INARIES",
        "PLANET_CLASS_BY_" + "CODE",
        "ANGLE_" + "CODES",
        "ANGULAR_" + "HOUSES",
        "SUCCEDENT_" + "HOUSES",
        "DEFAULT_TRADITIONAL_SIGN_" + "RULERSHIPS",
        "_HOUSE_SYSTEM_" + "CODES",
        "HOUSE_SYSTEM_REFERENCE_" + "ROWS",
        "VALENCE_BY_" + "ASPECT",
        "ENERGY_BY_" + "ASPECT",
        "_STAR" + "_DATA",
        "_ASPECT" + "_TONES",
        "planet_" + "rows",
        "sign_" + "rows",
        "dignity_type_" + "rows",
        "house_" + "rows",
    }


def _forbidden_helpers() -> set[str]:
    """Liste les anciens helpers locaux remplacés par des owners uniques."""
    return {
        "_norm" + "360",
        "_normalize_" + "longitude",
        "_sign_from_" + "longitude",
        "_get_swe_" + "module",
        "_profile_" + "list",
        "_require_" + "list",
        "fixed_star_" + "longitudes",
        "fixed_star_" + "display_name",
    }


def _python_files() -> list[Path]:
    """Retourne les fichiers Python applicatifs collectés par la garde."""
    roots = (REPO_ROOT / "backend" / "app", REPO_ROOT / "backend" / "tests")
    return [path for root in roots for path in root.rglob("*.py")]


def test_removed_reference_file_name_is_not_used_by_active_sources() -> None:
    """Bloque le retour du chemin JSON singulier des familles d'aspects."""
    forbidden_name = _forbidden_file_name()
    checked_roots = (
        REPO_ROOT / "backend" / "app",
        REPO_ROOT / "backend" / "tests",
        REPO_ROOT / "docs" / "recherches astro",
    )
    hits: list[str] = []
    for root in checked_roots:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".md", ".json"}:
                if forbidden_name in path.read_text(encoding="utf-8"):
                    hits.append(str(path.relative_to(REPO_ROOT)))
    assert hits == []


def test_removed_catalog_symbols_are_not_defined_in_active_python() -> None:
    """Bloque les anciennes constantes catalogues et helpers dupliqués."""
    forbidden_names = _forbidden_symbols() | _forbidden_helpers()
    hits: list[str] = []
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name in forbidden_names:
                    hits.append(f"{path.relative_to(REPO_ROOT)}:{node.name}")
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in forbidden_names:
                        hits.append(f"{path.relative_to(REPO_ROOT)}:{target.id}")
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.target.id in forbidden_names:
                    hits.append(f"{path.relative_to(REPO_ROOT)}:{node.target.id}")
    assert hits == []


def test_runtime_helper_owners_are_unique() -> None:
    """Vérifie les owners retenus pour les helpers convergés."""
    owner_expectations = {
        "normalize_360": "backend/app/domain/astrology/zodiac.py",
        "sign_from_longitude": "backend/app/domain/astrology/zodiac.py",
        "load_swisseph": "backend/app/domain/astrology/swisseph_runtime.py",
        "required_profile_values": (
            "backend/app/domain/astrology/interpretation/profile_fields.py"
        ),
    }
    definitions: dict[str, list[str]] = {name: [] for name in owner_expectations}
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in definitions:
                definitions[node.name].append(str(path.relative_to(REPO_ROOT)).replace("\\", "/"))
    assert definitions == {name: [owner] for name, owner in owner_expectations.items()}


def test_legacy_aspect_orb_shapes_are_not_used_by_runtime_sources() -> None:
    """Bloque les anciennes formes d'entrée du calculateur d'aspects."""
    forbidden_fragments = {
        "tuple[str, float]",
        "orb_" + "luminaries_override_deg",
        "orb_" + "pair_overrides",
        "orb_" + "luminaries",
        "orb_" + "pairs",
        "orb_" + "overrides",
    }
    checked_roots = (
        REPO_ROOT / "backend" / "app" / "domain" / "astrology",
        REPO_ROOT / "backend" / "app" / "services" / "chart",
        REPO_ROOT / "backend" / "app" / "services" / "llm_generation",
    )
    hits: list[str] = []
    for root in checked_roots:
        for path in root.rglob("*.py"):
            content = path.read_text(encoding="utf-8")
            for fragment in forbidden_fragments:
                if fragment in content:
                    hits.append(f"{path.relative_to(REPO_ROOT)}:{fragment}")
    assert hits == []


def test_prediction_aspect_mappings_are_not_reintroduced() -> None:
    """Bloque les mappings d'aspects daily concurrents du référentiel DB."""
    forbidden_names = {"ASPECTS_V1", "ASPECTS"}
    aspect_codes = {"conjunction", "sextile", "square", "trine", "opposition"}
    aspect_angles = {0, 60, 90, 120, 180}
    checked_roots = (
        REPO_ROOT / "backend" / "app" / "domain" / "prediction",
        REPO_ROOT / "backend" / "app" / "services" / "prediction",
    )
    hits: list[str] = []
    for root in checked_roots:
        for path in root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id in forbidden_names:
                            hits.append(f"{path.relative_to(REPO_ROOT)}:{target.id}")
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    if node.target.id in forbidden_names:
                        hits.append(f"{path.relative_to(REPO_ROOT)}:{node.target.id}")
                elif isinstance(node, ast.ClassDef):
                    for statement in node.body:
                        if isinstance(statement, ast.Assign):
                            for target in statement.targets:
                                if isinstance(target, ast.Name) and target.id in forbidden_names:
                                    hits.append(f"{path.relative_to(REPO_ROOT)}:{target.id}")
                        elif (
                            isinstance(statement, ast.AnnAssign)
                            and isinstance(statement.target, ast.Name)
                            and statement.target.id in forbidden_names
                        ):
                            hits.append(f"{path.relative_to(REPO_ROOT)}:{statement.target.id}")
                elif isinstance(node, ast.Dict):
                    literal_keys = {
                        item.value
                        for item in node.keys
                        if isinstance(item, ast.Constant) and isinstance(item.value, int)
                    }
                    literal_values = {
                        str(item.value).lower()
                        for item in node.values
                        if isinstance(item, ast.Constant) and isinstance(item.value, str)
                    }
                    if (
                        len(literal_keys & aspect_angles) >= 3
                        and len(literal_values & aspect_codes) >= 3
                    ):
                        hits.append(f"{path.relative_to(REPO_ROOT)}:aspect-degree-dict")
                elif isinstance(node, (ast.Set, ast.List, ast.Tuple)):
                    literal_values = {
                        str(item.value).lower()
                        for item in node.elts
                        if isinstance(item, ast.Constant)
                    }
                    if len(literal_values & aspect_codes) >= 3:
                        hits.append(f"{path.relative_to(REPO_ROOT)}:aspect-code-literal-group")

    assert hits == []

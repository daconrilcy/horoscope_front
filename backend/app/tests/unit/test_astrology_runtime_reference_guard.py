"""Gardes anti-retour du runtime reference astrologique."""

from __future__ import annotations

import ast
import re
from pathlib import Path

FORBIDDEN_NATAL_FLOW_PATTERNS = (
    r"ReferenceDataService\.get_active_reference_data",
    r"reference_data\s*:\s*dict",
    r"\bPLANET_KEYWORDS\b",
    r"\bSIGN_RULERS\b",
    r"\bDEFAULT_ORB\b",
    r"\bASPECT_WEIGHTS\b",
    r"\bHOUSE_MEANINGS\b",
    r"\bUNKNOWN_SIGN\b",
    r"\bZODIAC_SIGNS\b",
    r"\bELEMENT_BY_SIGN\b",
    r"\bMODALITY_BY_SIGN\b",
    r"\bPOLARITY_BY_SIGN\b",
    r"\bSIGN_PROFILE_DATA\b",
    r"\bASTRAL_POINTS\s*=",
    r"\bPOINT_VARIANTS\s*=",
    r"\bNODE_VARIANTS\s*=",
    r"\bLILITH_VARIANTS\s*=",
    r"\btrue_node\b",
    r"\bmean_node\b",
    r"\bEXACT_ORB_DEG\b",
    r"\bTIGHT_RATIO\b",
    r"\bMODERATE_RATIO\b",
    r"_allows_simplified_fallback",
    r"if\s+engine\s*==\s*[\"']swisseph[\"'][\s\S]{0,500}engine\s*=\s*[\"']simplified[\"']",
    r"SwissEph\s+bootstrap[\s\S]{0,300}engine\s*=\s*[\"']simplified[\"']",
    r"calculation_engine\s*=\s*[\"']simplified[\"']",
)

BACKEND_ROOT = Path(__file__).resolve().parents[3]


def _source(path: str) -> str:
    """Retourne le contenu source d'un fichier backend."""
    return (BACKEND_ROOT / path).read_text(encoding="utf-8")


def test_natal_flow_does_not_use_legacy_reference_service_or_symbols() -> None:
    """Le flux natal ne depend plus des donnees reference legacy."""
    files = [
        *(BACKEND_ROOT / "app/domain/astrology").rglob("*.py"),
        *(BACKEND_ROOT / "app/services/natal").rglob("*.py"),
    ]
    hits: list[str] = []

    for pattern in FORBIDDEN_NATAL_FLOW_PATTERNS:
        compiled = re.compile(pattern)
        for path in files:
            if compiled.search(path.read_text(encoding="utf-8")):
                hits.append(f"{path}:{pattern}")

    assert hits == []


def test_runtime_sign_profile_fixtures_do_not_import_seed_mappings() -> None:
    """Les fixtures runtime ne doivent pas masquer la source DB par un mapping seed."""
    factory = BACKEND_ROOT / "tests/factories/astrology_runtime_reference_factory.py"
    content = factory.read_text(encoding="utf-8")

    assert "SIGN_PROFILE_DATA" not in content


def test_build_natal_result_signature_uses_runtime_reference_not_dict() -> None:
    """La fonction publique de calcul consomme le contrat runtime type."""
    tree = ast.parse(_source("app/domain/astrology/natal_calculation.py"))
    function = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "build_natal_result"
    )
    annotations = {
        arg.arg: ast.unparse(arg.annotation) if arg.annotation is not None else ""
        for arg in function.args.args
    }

    assert annotations["runtime_reference"] == "AstrologyRuntimeReference"
    assert "reference_data" not in annotations
    assert all("dict" not in annotation for annotation in annotations.values())


def test_astrology_domain_does_not_import_prediction_or_llm_runtime() -> None:
    """Le domaine astrology reste separe de prediction et du runtime LLM."""
    forbidden = ("app.domain.prediction", "app.services.prediction", "AIEngineAdapter", "OpenAI")
    hits: list[str] = []
    for path in (BACKEND_ROOT / "app/domain/astrology").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden:
            if pattern in text:
                hits.append(f"{path}:{pattern}")

    assert hits == []


def test_natal_result_exposes_points_collection_without_flat_point_fields() -> None:
    """Le contrat natal conserve uniquement la collection `astral_points[]`."""
    tree = ast.parse(_source("app/domain/astrology/natal_calculation.py"))
    natal_result = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name == "NatalResult"
    )
    field_names = {
        node.target.id
        for node in natal_result.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }

    assert "astral_points" in field_names
    assert "points" not in field_names
    assert "true_node" not in field_names
    assert "mean_node" not in field_names
    assert "lilith" not in field_names
    assert "summary" not in field_names
    assert "keywords" not in field_names
    assert "micro_note" not in field_names
    assert "prompt_hints" not in field_names


def test_calculation_modules_do_not_import_astral_point_interpretation_services() -> None:
    """Le calcul natal ne doit pas dépendre de l'éditorial des points astraux."""
    forbidden = (
        "astral_point_interpretation_profiles",
        "astral_point_interpretation_keywords",
        "AstralPointInterpretationProfileModel",
        "AstralPointInterpretationKeywordModel",
        "AstralPointInterpretationRepository",
        "AstralPointInterpretationService",
        "InterpretationService",
        "PromptContext",
    )
    roots = [
        BACKEND_ROOT / "app/domain/astrology/calculation",
        BACKEND_ROOT / "app/domain/astrology/calculators",
        BACKEND_ROOT / "app/infra/ephemeris",
        BACKEND_ROOT / "app/services/natal",
    ]
    paths = [
        BACKEND_ROOT / "app/domain/astrology/natal_calculation.py",
        BACKEND_ROOT / "app/domain/astrology/astral_point_calculation_resolver.py",
        BACKEND_ROOT / "app/domain/astrology/ephemeris_provider.py",
    ]
    for root in roots:
        if root.exists():
            paths.extend(root.rglob("*.py"))
    hits: list[str] = []

    for path in paths:
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden:
            if pattern in text:
                hits.append(f"{path}:{pattern}")

    assert hits == []

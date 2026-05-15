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
    r"\bEXACT_ORB_DEG\b",
    r"\bTIGHT_RATIO\b",
    r"\bMODERATE_RATIO\b",
    r"_allows_simplified_fallback",
    r"if\s+engine\s*==\s*[\"']swisseph[\"'][\s\S]{0,500}engine\s*=\s*[\"']simplified[\"']",
    r"SwissEph\s+bootstrap[\s\S]{0,300}engine\s*=\s*[\"']simplified[\"']",
    r"calculation_engine\s*=\s*[\"']simplified[\"']",
)


def _source(path: str) -> str:
    """Retourne le contenu source d'un fichier backend."""
    return Path(path).read_text(encoding="utf-8")


def test_natal_flow_does_not_use_legacy_reference_service_or_symbols() -> None:
    """Le flux natal ne depend plus des donnees reference legacy."""
    files = [
        *Path("app/domain/astrology").rglob("*.py"),
        *Path("app/services/natal").rglob("*.py"),
    ]
    hits: list[str] = []

    for pattern in FORBIDDEN_NATAL_FLOW_PATTERNS:
        compiled = re.compile(pattern)
        for path in files:
            if compiled.search(path.read_text(encoding="utf-8")):
                hits.append(f"{path}:{pattern}")

    assert hits == []


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
    for path in Path("app/domain/astrology").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden:
            if pattern in text:
                hits.append(f"{path}:{pattern}")

    assert hits == []

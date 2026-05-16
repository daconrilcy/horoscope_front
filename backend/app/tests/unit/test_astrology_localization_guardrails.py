"""Gardes anti-réintroduction des mappings locaux de signes astrologiques."""

from __future__ import annotations

import ast
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SERVICES_ROOT = BACKEND_ROOT / "services"
PDF_EXPORT_PATH = SERVICES_ROOT / "natal" / "pdf_export_service.py"
DOMAIN_ASTROLOGY_ROOT = BACKEND_ROOT / "domain" / "astrology"


def test_targeted_services_do_not_reintroduce_sign_name_mappings() -> None:
    """Les surfaces ciblées ne doivent plus porter de mapping local de signes."""
    forbidden_names = {"SIGN_NAMES_FR", "SIGN_LABELS", "SIGNS"}
    violations: list[str] = []
    for path in SERVICES_ROOT.rglob("*.py"):
        if path == PDF_EXPORT_PATH:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in forbidden_names:
                        violations.append(f"{path.relative_to(BACKEND_ROOT)}::{target.id}")
            if (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id in forbidden_names
            ):
                violations.append(f"{path.relative_to(BACKEND_ROOT)}::{node.target.id}")
            if isinstance(node, ast.ImportFrom):
                imported = {alias.name for alias in node.names}
                for forbidden_name in forbidden_names & imported:
                    violations.append(f"{path.relative_to(BACKEND_ROOT)} import {forbidden_name}")

    assert violations == []


def test_pdf_sign_labels_exception_is_documented_out_of_scope() -> None:
    """L'exception PDF reste explicite et hors périmètre de CS-174."""
    content = PDF_EXPORT_PATH.read_text(encoding="utf-8")

    assert "SIGN_LABELS" in content


def test_domain_astrology_does_not_import_translation_resolver_or_models() -> None:
    """Le domaine astrology pur ne dépend pas de la localisation applicative."""
    forbidden_fragments = {
        "astrology_translation_resolver",
        "AstrologyTranslationResolver",
        "translated_name",
        "LanguageModel",
    }
    violations: list[str] = []
    for path in DOMAIN_ASTROLOGY_ROOT.rglob("*.py"):
        content = path.read_text(encoding="utf-8")
        for fragment in forbidden_fragments:
            if fragment in content:
                violations.append(f"{path.relative_to(BACKEND_ROOT)}::{fragment}")

    assert violations == []

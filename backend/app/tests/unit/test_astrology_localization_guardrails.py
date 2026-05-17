"""Gardes anti-réintroduction des mappings locaux de libellés astrologiques."""

from __future__ import annotations

import ast
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SERVICES_ROOT = BACKEND_ROOT / "services"
PDF_EXPORT_PATH = SERVICES_ROOT / "natal" / "pdf_export_service.py"
DOMAIN_ASTROLOGY_ROOT = BACKEND_ROOT / "domain" / "astrology"
DOMAIN_PREDICTION_ROOT = BACKEND_ROOT / "domain" / "prediction"


def test_targeted_services_do_not_reintroduce_local_label_mappings() -> None:
    """Les surfaces ciblées ne doivent plus porter de mapping local de libellés."""
    forbidden_names = {
        "ASPECT_NAMES_FR",
        "PLANET_NAMES_FR",
        "SIGN_LABELS",
        "SIGN_NAMES_FR",
        "SIGNS",
    }
    violations: list[str] = []
    for path in SERVICES_ROOT.rglob("*.py"):
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


def test_pdf_sign_labels_exception_is_removed() -> None:
    """Le PDF ne doit plus conserver de mapping local de signes."""
    content = PDF_EXPORT_PATH.read_text(encoding="utf-8")

    assert "SIGN_LABELS" not in content


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


def test_domain_prediction_does_not_reintroduce_local_astro_label_mappings() -> None:
    """Prediction ne doit pas redevenir proprietaire des libelles astrologiques."""
    forbidden_fragments = {
        "PLANET_NAMES_FR",
        "SIGN_NAMES_FR",
        "SIGN_LABELS_FR",
        "PLANET_CODE_LABELS",
        "ASPECT_LABELS",
        "HOUSE_SIGNIFICATIONS",
        "EFFECT_LABELS",
        "get_planet_name_fr",
        "get_sign_name_fr",
        "get_aspect_label",
        "get_effect_label",
    }
    violations: list[str] = []
    for path in DOMAIN_PREDICTION_ROOT.rglob("*.py"):
        content = path.read_text(encoding="utf-8")
        for fragment in forbidden_fragments:
            if fragment in content:
                violations.append(f"{path.relative_to(BACKEND_ROOT)}::{fragment}")

    assert violations == []


def test_public_astro_legacy_vocabulary_is_removed_from_prediction_runtime() -> None:
    """Le vocabulaire astro public legacy ne doit plus exister dans le runtime."""
    forbidden_fragments = {
        "PublicAstro" + "Vocabulary",
        "public_astro_" + "vocabulary",
        "_STAR" + "_DATA",
        "_ASPECT" + "_TONES",
        "fixed_star_" + "longitudes",
        "fixed_star_" + "display_name",
    }
    violations: list[str] = []
    for path in DOMAIN_PREDICTION_ROOT.rglob("*.py"):
        content = path.read_text(encoding="utf-8")
        for fragment in forbidden_fragments:
            if fragment in content:
                violations.append(f"{path.relative_to(BACKEND_ROOT)}::{fragment}")

    assert violations == []

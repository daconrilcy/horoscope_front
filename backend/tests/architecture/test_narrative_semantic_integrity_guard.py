# Commentaire global: garde anti-retour pour l'integrite semantique narrative.
"""Verifie que le padding de source ne revient pas dans la projection natale."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NATAL_GENERATION_ROOT = ROOT / "app" / "services" / "llm_generation" / "natal"


def test_narrative_builder_does_not_reintroduce_first_section_padding() -> None:
    """Interdit la recopie de la premiere section LLM comme source de chapitre."""
    forbidden = "response.sections" + "[0]"
    offenders: list[str] = []
    for path in NATAL_GENERATION_ROOT.glob("*.py"):
        content = path.read_text(encoding="utf-8")
        if forbidden in content:
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []

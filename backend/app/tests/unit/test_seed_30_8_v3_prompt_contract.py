# Commentaire global: garde de suppression du seed GPT-5 natal legacy.
"""Verifie que le seed prompt `natal_interpretation` v3 ne redevient pas actif."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_seed_30_8_prompt_sources_are_removed() -> None:
    """Les anciens prompts provider `natal_interpretation` ne restent pas seedables."""

    assert not (REPO_ROOT / "scripts/seed_30_8_v3_prompts.py").exists()
    assert not (REPO_ROOT / "app/ops/llm/bootstrap/seed_30_8_v3_prompts.py").exists()

# Commentaire global: garde de suppression des anciens seeds prompts nataux.
"""Verifie que les seeds prompts nataux legacy ne redeviennent pas importables."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_seed_29_prompt_sources_are_removed() -> None:
    """Les anciens seeds `natal_interpretation` ne restent pas executables."""

    assert not (REPO_ROOT / "scripts/seed_29_prompts.py").exists()
    assert not (REPO_ROOT / "app/ops/llm/bootstrap/seed_29_prompts.py").exists()

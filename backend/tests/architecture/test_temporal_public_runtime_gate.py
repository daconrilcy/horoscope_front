# Garde d'architecture du gate temporel public CS-250/CS-253.
"""Empêche une surface temporelle publique de s'appuyer sur le mode simplifié."""

from __future__ import annotations

import ast
from pathlib import Path

from app.domain.astrology.runtime.astronomical_proof import (
    CS253_GATE_MARKER,
    build_public_temporal_gate,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
STORY_STATUS = REPO_ROOT.parent / "_condamad/stories/story-status.md"
ASTROLOGY_DOMAIN = REPO_ROOT / "app/domain/astrology"


def test_cs253_public_gate_stays_blocked_until_cs250_done() -> None:
    """Le registre garde CS-253 ferme tant que CS-250 n'est pas done."""
    status = _story_status("CS-250")
    gate = build_public_temporal_gate(cs250_status=status)

    assert gate.marker == CS253_GATE_MARKER
    if status != "done":
        assert gate.cs253_gate_state == "blocked"
        assert gate.authorized_public_temporal is False
    else:
        assert gate.cs253_gate_state == "proof-closed"
        assert gate.authorized_public_temporal is True


def test_no_public_temporal_runtime_qualifies_simplified_engine() -> None:
    """AST guard: aucun contrat temporel public ne qualifie `simplified`."""
    offenders: list[str] = []
    for path in _python_files(ASTROLOGY_DOMAIN):
        relative = path.relative_to(ASTROLOGY_DOMAIN).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            text = node.value.lower()
            if "simplified" in text and "public temporal" in text:
                offenders.append(f"{relative}:{node.lineno}")

    assert offenders == []


def test_astronomical_proof_declares_single_cs253_gate_marker() -> None:
    """Le marker gate est unique pour eviter les alias de contournement."""
    proof_path = ASTROLOGY_DOMAIN / "runtime/astronomical_proof.py"
    source = proof_path.read_text(encoding="utf-8")

    assert source.count(CS253_GATE_MARKER) == 1
    assert "risk-accepted-non-public" in source
    assert "selected-ready-after-cs250" not in source


def _story_status(story_id: str) -> str:
    """Extrait le statut d'une story depuis le registre CONDAMAD."""
    for line in STORY_STATUS.read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] == story_id:
            return cells[3]
    raise AssertionError(f"Story {story_id} not found")


def _python_files(root: Path) -> tuple[Path, ...]:
    """Retourne les modules Python du domaine hors caches."""
    excluded = {"__pycache__", ".pytest_cache", ".ruff_cache"}
    return tuple(
        sorted(path for path in root.rglob("*.py") if not excluded.intersection(path.parts))
    )

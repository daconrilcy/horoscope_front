# Commentaire global: garde d'architecture du contrat narratif public.
"""Verifie que la documentation et les modules narratifs n'exposent pas de carriers interdits."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_contract_doc_lists_public_denylist() -> None:
    contract = (ROOT / "docs" / "narrative-natal-reading-v1-contract.md").read_text(
        encoding="utf-8"
    )
    for token in ("chart_json", "audit_input", "interpretive_signal_ids", "evidence_refs"):
        assert token in contract


def test_examples_do_not_contain_forbidden_surfaces() -> None:
    examples_dir = ROOT / "docs" / "examples"
    forbidden = ("audit_input", "interpretive_signal_ids", "chart_json", "technical_scores")
    for path in examples_dir.glob("narrative-natal-reading-v1-*.json"):
        content = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in content, f"{token} found in {path.name}"


def test_legacy_narrative_migration_does_not_delete_user_history() -> None:
    migration = (
        ROOT
        / "migrations"
        / "versions"
        / "20260530_0141_purge_legacy_user_natal_interpretations.py"
    ).read_text(encoding="utf-8")
    assert "DELETE FROM" not in migration

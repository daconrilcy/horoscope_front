from pathlib import Path

import pytest

from app.llm_orchestration.golden_regression_registry import OBS_SNAPSHOT_CLASSIFICATION_DEFAULT
from app.llm_orchestration.services.doc_conformity_validator import DocConformityValidator


def _validator() -> DocConformityValidator:
    root = Path(__file__).resolve().parents[3]
    return DocConformityValidator(root)


def test_doc_conformity_validator_taxonomy() -> None:
    validator = _validator()
    content = validator.doc_path.read_text(encoding="utf-8")
    assert not validator.validate_taxonomy(content)


def test_doc_conformity_validator_providers() -> None:
    validator = _validator()
    content = validator.doc_path.read_text(encoding="utf-8")
    assert not validator.validate_providers(content)


def test_doc_conformity_validator_fallbacks() -> None:
    validator = _validator()
    content = validator.doc_path.read_text(encoding="utf-8")
    assert not validator.validate_fallbacks(content)


def test_doc_conformity_validator_obs_snapshot_classification() -> None:
    validator = _validator()
    content = validator.doc_path.read_text(encoding="utf-8")
    assert not validator.validate_obs_snapshot_classification(content)


def test_obs_snapshot_classification_default_is_explicit() -> None:
    assert OBS_SNAPSHOT_CLASSIFICATION_DEFAULT["strict"]
    assert OBS_SNAPSHOT_CLASSIFICATION_DEFAULT["thresholded"] == frozenset(
        {"max_output_tokens_final"}
    )
    assert "active_snapshot_id" in OBS_SNAPSHOT_CLASSIFICATION_DEFAULT["informational"]


def test_doc_conformity_is_update_required() -> None:
    validator = DocConformityValidator(Path("/tmp"))
    assert validator.is_update_required(["backend/app/llm_orchestration/gateway.py"])
    assert validator.is_update_required(["docs/llm-prompt-generation-by-feature.md"])
    assert validator.is_update_required(["backend/scripts/check_doc_conformity.py"])
    assert validator.is_update_required([".github/workflows/llm-doc-conformity.yml"])
    assert not validator.is_update_required(["backend/app/main.py"])
    assert not validator.is_update_required(["frontend/src/App.tsx"])


def test_doc_conformity_check_verification_reference_updated() -> None:
    validator = DocConformityValidator(Path("/tmp"))
    old_content = """
Dernière vérification manuelle contre le pipeline réel du gateway :
- **Date** : `2026-04-10`
- **Référence stable (Commit SHA)** : `abcdef1`
Si le code diverge
"""
    new_content_same = """
Dernière vérification manuelle contre le pipeline réel du gateway :
- **Date** : `2026-04-10`
- **Référence stable (Commit SHA)** : `abcdef1`
Si le code diverge
"""
    new_content_updated_date = """
Dernière vérification manuelle contre le pipeline réel du gateway :
- **Date** : `2026-04-13`
- **Référence stable (Commit SHA)** : `abcdef1`
Si le code diverge
"""
    new_content_updated_ref = """
Dernière vérification manuelle contre le pipeline réel du gateway :
- **Date** : `2026-04-10`
- **Référence stable (Commit SHA)** : `f123154`
Si le code diverge
"""

    assert not validator.check_verification_reference_updated(old_content, new_content_same)
    assert validator.check_verification_reference_updated(old_content, new_content_updated_date)
    assert validator.check_verification_reference_updated(old_content, new_content_updated_ref)


def test_doc_conformity_check_pr_template_justification() -> None:
    validator = DocConformityValidator(Path("/tmp"))
    assert validator.check_pr_template_justification("- [x] **OUI** : J'ai mis à jour doc.md")
    assert validator.check_pr_template_justification("- [x] `REF_ONLY` : Justification.")
    assert not validator.check_pr_template_justification("- [x] `REF_ONLY`\n- [x] `FIX_TYPO`")
    assert not validator.check_pr_template_justification("- [ ] `REF_ONLY`")
    assert not validator.check_pr_template_justification("- [x] `UNKNOWN_REASON`")


def test_validate_pr_template_state_accepts_oui_when_doc_updated() -> None:
    validator = DocConformityValidator(Path("/tmp"))
    assert (
        validator.validate_pr_template_state(
            "- [x] **OUI** : J'ai mis à jour doc.md",
            structural_change=True,
            doc_updated=True,
        )
        == []
    )


def test_validate_pr_template_state_rejects_empty_pr_content_for_structural_change() -> None:
    validator = DocConformityValidator(Path("/tmp"))
    errors = validator.validate_pr_template_state(
        "",
        structural_change=True,
        doc_updated=True,
    )
    assert errors


def test_validate_pr_template_state_rejects_reason_when_doc_updated() -> None:
    validator = DocConformityValidator(Path("/tmp"))
    errors = validator.validate_pr_template_state(
        "- [x] `REF_ONLY`",
        structural_change=True,
        doc_updated=True,
    )
    assert errors


def test_validate_pr_template_state_accepts_single_reason_without_doc_update() -> None:
    validator = DocConformityValidator(Path("/tmp"))
    assert (
        validator.validate_pr_template_state(
            "- [x] `NON_LLM`",
            structural_change=True,
            doc_updated=False,
        )
        == []
    )


def test_validate_pr_template_state_rejects_oui_without_doc_update() -> None:
    validator = DocConformityValidator(Path("/tmp"))
    errors = validator.validate_pr_template_state(
        "- [x] **OUI** : J'ai mis à jour doc.md",
        structural_change=True,
        doc_updated=False,
    )
    assert errors


def test_taxonomy_mismatch_fails_validation() -> None:
    validator = _validator()
    fake_content = "| `chat` | ... | `nominal_canonical` |\n"
    errors = validator.validate_taxonomy(fake_content)
    assert len(errors) >= 3
    assert any("guidance" in error for error in errors)
    assert any("natal" in error for error in errors)
    assert any("horoscope_daily" in error for error in errors)


def test_taxonomy_alias_mismatch_fails_validation() -> None:
    validator = _validator()
    fake_content = """
| `chat` | point d'entrée | taxonomie | `nominal_canonical` |
| `guidance` | point d'entrée | taxonomie | `nominal_canonical` |
| `natal` | point d'entrée | taxonomie | `nominal_canonical` |
| `horoscope_daily` | point d'entrée | taxonomie | `nominal_canonical` |
"""
    errors = validator.validate_taxonomy(fake_content)
    assert any("daily_prediction" in error for error in errors)
    assert any("natal_interpretation" in error for error in errors)


def test_provider_mismatch_fails_validation() -> None:
    validator = _validator()
    fake_content = "nominalement uniquement par `anthropic`"
    errors = validator.validate_providers(fake_content)
    assert any("openai" in error for error in errors)
    assert any("anthropic" in error for error in errors)


def test_fallback_perimeter_mismatch_fails_validation() -> None:
    validator = _validator()
    fake_content = """
- `USE_CASE_FIRST` est `à retirer` sur chat, guidance ;
- `RESOLVE_MODEL` est `à retirer` sur chat, guidance, natal, horoscope_daily ;
"""
    errors = validator.validate_fallbacks(fake_content)
    assert any("USE_CASE_FIRST" in error and "families mismatch" in error for error in errors)


def test_obs_snapshot_thresholded_mismatch_fails_validation() -> None:
    validator = _validator()
    fake_content = (
        "- `strict` : `pipeline_kind`, `execution_path_kind`, `fallback_kind`, "
        "triplet provider, `context_compensation_status`, `max_output_tokens_source` ;\n"
        "- `thresholded` : autre_chose ;\n"
        "- `informational` : `executed_provider_mode`, `attempt_count`, "
        "`provider_error_code`, `breaker_state`, `breaker_scope`, "
        "`active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id`.\n"
    )
    errors = validator.validate_obs_snapshot_classification(fake_content)
    assert any("max_output_tokens_final" in error for error in errors)


def test_script_pr_body_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    root = Path(__file__).resolve().parents[3]
    monkeypatch.syspath_prepend(str(root / "backend"))
    sys.modules.pop("scripts.check_doc_conformity", None)
    import scripts.check_doc_conformity as script

    monkeypatch.setattr(
        script,
        "resolve_git_context",
        lambda v: script.GitResolutionResult(
            mode="test",
            changed_files=["backend/app/llm_orchestration/gateway.py"],
            structural_files_detected=["backend/app/llm_orchestration/gateway.py"],
        ),
    )
    monkeypatch.delenv("DOC_CONFORMITY_PR_BODY", raising=False)
    assert script.main() == 1

    monkeypatch.setenv("DOC_CONFORMITY_PR_BODY", "- [x] `NON_LLM` : some refactoring")
    assert script.main() == 0

    monkeypatch.setenv("DOC_CONFORMITY_PR_BODY", "- [x] **OUI**")
    monkeypatch.setattr(script, "has_pr_context", lambda: True)
    assert script.main() == 1

    monkeypatch.setenv("DOC_CONFORMITY_PR_BODY", "- [ ] `REF_ONLY`")
    assert script.main() == 1


def test_script_requires_pr_section_when_doc_updated_and_pr_context_exists(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import sys

    monkeypatch.delenv("DOC_CONFORMITY_PR_BODY", raising=False)

    root = Path(__file__).resolve().parents[3]
    monkeypatch.syspath_prepend(str(root / "backend"))
    sys.modules.pop("scripts.check_doc_conformity", None)
    import scripts.check_doc_conformity as script

    monkeypatch.setattr(
        script,
        "resolve_git_context",
        lambda v: script.GitResolutionResult(
            mode="test",
            changed_files=[
                "backend/app/llm_orchestration/gateway.py",
                "docs/llm-prompt-generation-by-feature.md",
            ],
            structural_files_detected=["backend/app/llm_orchestration/gateway.py"],
        ),
    )

    pr_body_file = tmp_path / "pr_body.md"
    pr_body_file.write_text("", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["check_doc_conformity.py", str(pr_body_file)])

    assert script.main() == 1


def test_get_changed_files_prefers_merge_base_with_explicit_base_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import sys

    root = Path(__file__).resolve().parents[3]
    monkeypatch.syspath_prepend(str(root / "backend"))
    sys.modules.pop("scripts.check_doc_conformity", None)
    import scripts.check_doc_conformity as script

    monkeypatch.setenv("DOC_CONFORMITY_BASE_REF", "main")

    def fake_run_git_text(args: list[str]) -> str | None:
        if args == ["rev-parse", "--verify", "origin/main"]:
            return "origin-main-sha"
        if args == ["rev-parse", "--verify", "main"]:
            return "main-sha"
        if args == ["merge-base", "origin/main", "HEAD"]:
            return "merge-base-sha"
        return None

    def fake_run_git_lines(args: list[str]) -> list[str]:
        if args == ["diff", "--name-only", "merge-base-sha", "HEAD"]:
            return ["backend/app/llm_orchestration/gateway.py"]
        if args in (
            ["diff", "--name-only", "HEAD"],
            ["diff", "--cached", "--name-only"],
            ["ls-files", "--others", "--exclude-standard"],
        ):
            return []
        raise AssertionError(f"Unexpected git args: {args}")

    monkeypatch.setattr(script, "_run_git_text", fake_run_git_text)
    monkeypatch.setattr(script, "_run_git_lines", fake_run_git_lines)

    validator = DocConformityValidator(root)
    result = script.resolve_git_context(validator)
    assert result.mode == "merge_base"
    assert result.base_commit == "merge-base-sha"
    assert result.changed_files == ["backend/app/llm_orchestration/gateway.py"]

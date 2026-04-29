import re
from pathlib import Path

from app.ops.llm.doc_conformity_manifest import (
    STRUCTURAL_FILES,
    VERIFICATION_MARKER,
)


def test_source_of_truth_uniqueness() -> None:
    """AC1: Ensure no other file redefines the core constants."""
    root = Path(__file__).resolve().parents[3]
    backend_root = root / "backend"

    # Files to ignore (the manifest itself and this test)
    ignored_files = {
        "backend/app/ops/llm/doc_conformity_manifest.py",
        "backend/tests/integration/test_llm_doc_conformity_hardening.py",
    }

    patterns = {
        "STRUCTURAL_FILES": r"STRUCTURAL_FILES\s*=\s*{",
        "DOC_PATH": r"DOC_PATH\s*=\s*[\"']",
        "VERIFICATION_MARKER": rf"[\"']{VERIFICATION_MARKER}[\"']",
        "AUTHORIZED_PR_REASONS": r"AUTHORIZED_PR_REASONS\s*=\s*\(",
    }

    for file_path in backend_root.rglob("*.py"):
        rel_path = file_path.relative_to(root).as_posix()
        if rel_path in ignored_files:
            continue

        content = file_path.read_text(encoding="utf-8")
        for name, pattern in patterns.items():
            # We allow imports of these names
            if re.search(pattern, content):
                # Special cases for tests that might use these names locally for different purposes
                if "test_" in rel_path and name in ["DOC_PATH", "AUTHORIZED_PR_REASONS"]:
                    continue
                # If it's a direct assignment and not in manifest, it's a duplication
                if re.search(rf"^{pattern}", content, re.MULTILINE):
                    assert False, (
                        f"Duplication of {name} found in {rel_path}. "
                        "Import it from manifest instead."
                    )


def test_structural_files_existence() -> None:
    """Ensure all files listed in STRUCTURAL_FILES actually exist in the repo."""
    root = Path(__file__).resolve().parents[3]
    for file_rel_path in STRUCTURAL_FILES:
        full_path = root / file_rel_path
        assert full_path.exists(), f"Structural file {file_rel_path} does not exist."


def test_doc_conformity_check_verification_reference_updated_robustness() -> None:
    """AC4: Verify Date and Stable Ref block update robustness."""
    from app.ops.llm.doc_conformity_validator import DocConformityValidator

    validator = DocConformityValidator(Path("/tmp"))

    old_content = """
Dernière vérification manuelle contre le pipeline réel du gateway :
- **Date** : `2026-04-10`
- **Référence stable (Commit SHA)** : `abcdef1`
"""
    # Same
    assert not validator.check_verification_reference_updated(old_content, old_content)

    # Date changed
    new_date = old_content.replace("2026-04-10", "2026-04-11")
    assert validator.check_verification_reference_updated(old_content, new_date)

    # Ref changed
    new_ref = old_content.replace("abcdef1", "abcdef2")
    assert validator.check_verification_reference_updated(old_content, new_ref)

    # Missing date/ref in new content
    bad_content = "Just some text"
    assert not validator.check_verification_reference_updated(old_content, bad_content)


def test_validate_pr_template_state_semantic_checks() -> None:
    """AC5, AC6: PR template state with semantic checks."""
    from app.ops.llm.doc_conformity_validator import DocConformityValidator

    validator = DocConformityValidator(Path("/tmp"))

    # AC5: Reject contradictory states
    errors = validator.validate_pr_template_state(
        "- [x] **OUI**\n- [x] `FIX_TYPO`", structural_change=True, doc_updated=True
    )
    assert any("contradictory state" in e for e in errors)

    # AC6: TEST_ONLY check
    # TEST_ONLY with non-test files
    errors = validator.validate_pr_template_state(
        "- [x] `TEST_ONLY`",
        structural_change=True,
        doc_updated=False,
        changed_files=["backend/app/domain/llm/runtime/gateway.py"],
    )
    assert any("TEST_ONLY" in e and "invalid" in e for e in errors)

    # TEST_ONLY with test files only
    errors = validator.validate_pr_template_state(
        "- [x] `TEST_ONLY`",
        structural_change=True,
        doc_updated=False,
        changed_files=["backend/tests/integration/test_foo.py"],
    )
    assert not errors

    # AC6: DOC_ONLY check
    errors = validator.validate_pr_template_state(
        "- [x] `DOC_ONLY`", structural_change=True, doc_updated=False
    )
    assert any(
        "DOC_ONLY" in e and "requires the documentation file to be updated" in e for e in errors
    )

    errors = validator.validate_pr_template_state(
        "- [x] `NON_LLM`",
        structural_change=True,
        doc_updated=False,
        changed_files=["backend/scripts/check_doc_conformity.py"],
    )
    assert not errors

    errors = validator.validate_pr_template_state(
        "- [x] `FIX_TYPO`",
        structural_change=True,
        doc_updated=False,
        changed_files=["docs/llm-prompt-generation-by-feature.md"],
    )
    assert not errors

    errors = validator.validate_pr_template_state(
        "- [x] `REF_ONLY`",
        structural_change=True,
        doc_updated=False,
        changed_files=["backend/app/domain/llm/runtime/gateway.py"],
    )
    assert any("REF_ONLY" in e for e in errors)


def test_git_context_resolution_mocked(monkeypatch) -> None:
    """AC2, AC3: Test git context resolution under various conditions."""
    import scripts.check_doc_conformity as script
    from app.ops.llm.doc_conformity_validator import DocConformityValidator

    validator = DocConformityValidator(Path("/tmp"))

    def mock_run_git_text(args):
        if args == ["merge-base", "origin/main", "HEAD"]:
            return "base-sha"
        if args == ["rev-parse", "--verify", "origin/main"]:
            return "origin-main-sha"
        return None

    def mock_run_git_lines(args):
        if "diff" in args and "base-sha" in args:
            return ["backend/app/domain/llm/runtime/gateway.py"]
        return []

    monkeypatch.setattr(script, "_run_git_text", mock_run_git_text)
    monkeypatch.setattr(script, "_run_git_lines", mock_run_git_lines)
    monkeypatch.setenv("DOC_CONFORMITY_BASE_REF", "main")

    result = script.resolve_git_context(validator)
    assert result.mode == "merge_base"
    assert result.base_commit == "base-sha"
    assert "backend/app/domain/llm/runtime/gateway.py" in result.changed_files
    assert "backend/app/domain/llm/runtime/gateway.py" in result.structural_files_detected


def test_script_json_output(monkeypatch, capsys) -> None:
    """AC12: Test machine-readable JSON output."""
    import json
    import sys

    import scripts.check_doc_conformity as script

    monkeypatch.setattr(sys, "argv", ["check_doc_conformity.py", "--json"])
    # Mocking validator and git to avoid real execution
    monkeypatch.setattr(
        script, "resolve_git_context", lambda v: script.GitResolutionResult(mode="test")
    )

    class FakeValidator:
        def validate_all(self):
            return []

        def is_update_required(self, files):
            return False

    class FakeSemanticValidator:
        def validate_all(self):
            return []

    monkeypatch.setattr(
        script,
        "_load_validator_dependencies",
        lambda: (
            "docs/llm-prompt-generation-by-feature.md",
            lambda _: FakeValidator(),
            lambda _: FakeSemanticValidator(),
        ),
    )

    exit_code = script.main()
    assert exit_code == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["status"] == "ok"
    assert "git_context" in data
    assert data["git_context"]["mode"] == "test"
    assert "doc_changed" in data
    assert "verification_block_updated" in data
    assert "pr_section_status" in data
    assert "errors" in data
    assert "semantic_invariants_version" in data

import os
import subprocess
import sys
from pathlib import Path


def _ensure_backend_root_on_path() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def _run_git_lines(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _run_git_text(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
    except Exception:
        return None
    return result.stdout.strip() or None


def _existing_base_refs() -> list[str]:
    preferred_refs = [
        os.environ.get("DOC_CONFORMITY_BASE_REF"),
        os.environ.get("GITHUB_BASE_REF"),
        "origin/main",
        "main",
    ]
    candidates: list[str] = []
    for ref in preferred_refs:
        if not ref:
            continue
        normalized_candidates = [ref]
        if "/" not in ref:
            normalized_candidates.insert(0, f"origin/{ref}")
        for candidate in normalized_candidates:
            if candidate not in candidates and _run_git_text(["rev-parse", "--verify", candidate]):
                candidates.append(candidate)
    return candidates


def _get_branch_diff_files() -> list[str]:
    for base_ref in _existing_base_refs():
        merge_base = _run_git_text(["merge-base", base_ref, "HEAD"])
        if merge_base:
            try:
                return _run_git_lines(["diff", "--name-only", merge_base, "HEAD"])
            except Exception:
                continue

    for fallback_args in (
        ["diff", "--name-only", "HEAD~1", "HEAD"],
        ["diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
    ):
        try:
            return _run_git_lines(fallback_args)
        except Exception:
            continue

    return []


def _read_file_from_best_base(path: str) -> str | None:
    for base_ref in _existing_base_refs():
        content = _run_git_text(["show", f"{base_ref}:{path}"])
        if content is not None:
            return content

    for fallback_ref in ("HEAD~1",):
        content = _run_git_text(["show", f"{fallback_ref}:{path}"])
        if content is not None:
            return content

    return None


def get_changed_files() -> list[str]:
    """Return committed branch diff plus staged/unstaged/untracked working tree changes."""
    changed: set[str] = set()
    changed.update(_get_branch_diff_files())

    for args in (
        ["diff", "--name-only", "HEAD"],
        ["diff", "--cached", "--name-only"],
        ["ls-files", "--others", "--exclude-standard"],
    ):
        try:
            changed.update(_run_git_lines(args))
        except Exception:
            pass

    return sorted(changed)


def read_pr_body() -> str:
    if len(sys.argv) > 1:
        pr_body_file = Path(sys.argv[1])
        if pr_body_file.exists():
            return pr_body_file.read_text(encoding="utf-8")
    return os.environ.get("DOC_CONFORMITY_PR_BODY", "")


def has_pr_context() -> bool:
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).exists()
    return "DOC_CONFORMITY_PR_BODY" in os.environ


def main() -> int:
    _ensure_backend_root_on_path()
    from app.llm_orchestration.doc_conformity_manifest import DOC_PATH
    from app.llm_orchestration.services.doc_conformity_validator import DocConformityValidator

    root_path = Path(__file__).resolve().parents[2]
    validator = DocConformityValidator(root_path)

    print("==> Checking LLM Documentation conformity...")
    errors = validator.validate_all()
    if errors:
        print("[FAIL] Documentation is not conform to code:")
        for error in errors:
            print(f"  - {error}")
        return 1

    changed_files = get_changed_files()
    structural_change = validator.is_update_required(changed_files)
    normalized_changed_files = {
        changed_file.replace("\\", "/").lstrip("./") for changed_file in changed_files
    }
    doc_updated = DOC_PATH in normalized_changed_files

    if structural_change:
        print("Structural files changed. Checking documentation governance...")
        pr_context = has_pr_context()
        pr_body = read_pr_body()
        if doc_updated:
            try:
                old_content = _read_file_from_best_base(DOC_PATH)
                if old_content is not None:
                    new_content = (root_path / DOC_PATH).read_text(encoding="utf-8")
                    if not validator.check_verification_reference_updated(old_content, new_content):
                        print(f"[FAIL] {DOC_PATH} was touched but Date/Ref block was not updated.")
                        return 1
                else:
                    print(
                        f"[WARNING] Could not find base version of {DOC_PATH} "
                        "to verify Date/Ref update."
                    )
            except Exception as exc:
                print(f"[WARNING] Error during verification reference check: {exc}")
        else:
            print(f"[FAIL] Structural files changed but {DOC_PATH} was not updated.")
            print(
                "If this is intended, the PR workflow must provide a valid bounded justification "
                "for not updating the documentation."
            )
            if not pr_body:
                return 1

        if pr_context:
            pr_errors = validator.validate_pr_template_state(
                pr_body,
                structural_change=True,
                doc_updated=doc_updated,
            )
            if pr_errors:
                print("[FAIL] PR template / justification is invalid:")
                for error in pr_errors:
                    print(f"  - {error}")
                return 1

    print("[OK] Documentation is conform.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

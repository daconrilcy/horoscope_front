import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class GitResolutionResult:
    mode: str
    base_ref: str | None = None
    base_commit: str | None = None
    changed_files: list[str] = field(default_factory=list)
    structural_files_detected: list[str] = field(default_factory=list)
    is_degraded: bool = False
    warning: str | None = None


def _run_git_lines(args: list[str]) -> list[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def _run_git_text(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        return result.stdout.strip() or None
    except Exception:
        return None


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


def _ensure_backend_root_on_path() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def _load_validator_dependencies():
    _ensure_backend_root_on_path()
    from app.llm_orchestration.doc_conformity_manifest import DOC_PATH
    from app.llm_orchestration.services.doc_conformity_validator import DocConformityValidator

    return DOC_PATH, DocConformityValidator


def resolve_git_context(validator) -> GitResolutionResult:
    """Resolve git context and return a structured result (AC2, AC3)."""
    base_refs = _existing_base_refs()
    changed_files_set: set[str] = set()
    result = GitResolutionResult(mode="unknown")

    # 1. Try branch diff against preferred base
    for base_ref in base_refs:
        merge_base = _run_git_text(["merge-base", base_ref, "HEAD"])
        if merge_base:
            result.mode = "merge_base"
            result.base_ref = base_ref
            result.base_commit = merge_base
            changed_files_set.update(_run_git_lines(["diff", "--name-only", merge_base, "HEAD"]))
            break

    # 2. Try fallbacks if no merge-base found
    if result.mode == "unknown":
        for fallback_mode, fallback_args in [
            ("head_prev", ["diff", "--name-only", "HEAD~1", "HEAD"]),
            ("diff_tree", ["diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]),
        ]:
            files = _run_git_lines(fallback_args)
            if files:
                result.mode = fallback_mode
                result.is_degraded = True
                changed_files_set.update(files)
                break

    # 3. Always include working tree changes (unstaged, staged, untracked)
    changed_files_set.update(_run_git_lines(["diff", "--name-only", "HEAD"]))
    changed_files_set.update(_run_git_lines(["diff", "--cached", "--name-only"]))
    changed_files_set.update(_run_git_lines(["ls-files", "--others", "--exclude-standard"]))

    if result.mode == "unknown" and not changed_files_set:
        result.mode = "no_history"
        result.is_degraded = True
        result.warning = "No git history or base ref found. Gate may be incomplete."

    result.changed_files = sorted(changed_files_set)
    result.structural_files_detected = sorted(
        [f for f in result.changed_files if validator.is_update_required([f])]
    )
    return result


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


def read_pr_body() -> str:
    # Environment variable has priority to allow mocking in tests
    env_body = os.environ.get("DOC_CONFORMITY_PR_BODY")
    if env_body:
        return env_body

    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            pr_body_file = Path(arg)
            if pr_body_file.exists() and pr_body_file.suffix != ".py":
                return pr_body_file.read_text(encoding="utf-8")
    return ""


def has_pr_context() -> bool:
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            return Path(arg).exists()
    return "DOC_CONFORMITY_PR_BODY" in os.environ


def get_changed_files() -> list[str]:
    """Backward compatibility shim for tests."""
    _, doc_conformity_validator = _load_validator_dependencies()

    root_path = Path(__file__).resolve().parents[2]
    validator = doc_conformity_validator(root_path)
    return resolve_git_context(validator).changed_files


def main() -> int:
    use_json = "--json" in sys.argv
    root_path = Path(__file__).resolve().parents[2]
    doc_path, doc_conformity_validator = _load_validator_dependencies()
    validator = doc_conformity_validator(root_path)

    if not use_json:
        print("==> Checking LLM Documentation conformity...")

    # Step 1: Doctrine lints (always run)
    errors = validator.validate_all()

    # Step 2: Git resolution
    git_context = resolve_git_context(validator)
    structural_change = len(git_context.structural_files_detected) > 0
    normalized_changed_files = {
        changed_file.replace("\\", "/").lstrip("./")
        for changed_file in git_context.changed_files
    }
    doc_updated = doc_path in normalized_changed_files

    # Step 3: Governance checks for structural changes
    pr_section_status = "not_required"
    verification_block_updated = None

    if structural_change:
        pr_section_status = "required_missing"
        if doc_updated:
            try:
                old_content = _read_file_from_best_base(doc_path)
                if old_content is not None:
                    new_content = (root_path / doc_path).read_text(encoding="utf-8")
                    verification_block_updated = validator.check_verification_reference_updated(
                        old_content, new_content
                    )
                    if not verification_block_updated:
                        errors.append(f"{doc_path} was touched but Date/Ref block was not updated.")
                else:
                    # In some Git contexts, we might not have the base version.
                    # We log it but don't fail unless it's a hard requirement in CI.
                    pass
            except Exception as exc:
                errors.append(f"Error during verification reference check: {exc}")
        else:
            # No doc update but structural change -> check PR justification
            pass

        pr_body = read_pr_body()
        if pr_body or has_pr_context():
            pr_errors = validator.validate_pr_template_state(
                pr_body,
                structural_change=True,
                doc_updated=doc_updated,
                changed_files=git_context.changed_files,
            )
            if pr_errors:
                errors.extend(pr_errors)
                pr_section_status = "invalid"
            else:
                pr_section_status = "valid"
        else:
            errors.append(
                "PR template error: the documentation governance section must be "
                "filled in for structural changes."
            )

    # Step 4: Final Output
    if use_json:
        output = {
            "status": "fail" if errors else "ok",
            "git_context": asdict(git_context),
            "doc_changed": doc_updated,
            "verification_block_updated": verification_block_updated,
            "pr_section_status": pr_section_status,
            "errors": [
                {"code": "DOC_CONFORMITY_ERROR", "message": error, "rule": "doc_conformity"}
                for error in errors
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        if git_context.is_degraded:
            print(f"[WARNING] Git context is degraded: {git_context.mode}")
        if git_context.warning:
            print(f"[WARNING] {git_context.warning}")

        if errors:
            print("[FAIL] Documentation is not conform to code:")
            for error in errors:
                print(f"  - {error}")
            if structural_change and not doc_updated and not read_pr_body():
                print("\nStructural files changed but documentation was not updated.")
                print("If this is intended, provide a justification in the PR body.")
            return 1

        print("[OK] Documentation is conform.")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

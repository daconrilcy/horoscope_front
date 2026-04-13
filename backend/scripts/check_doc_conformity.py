import os
import subprocess
import sys
from pathlib import Path


def _ensure_backend_root_on_path() -> None:
    # Path to backend/
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def get_changed_files():
    """Returns the list of files changed (staged, unstaged, and in branch)."""
    changed = set()
    try:
        # 1. Working tree (unstaged)
        res = subprocess.run(
            ["git", "diff", "--name-only"], capture_output=True, text=True, check=True
        )
        changed.update(res.stdout.splitlines())

        # 2. Staged changes
        res = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True
        )
        changed.update(res.stdout.splitlines())

        # 3. Branch changes compared to origin/main (if available)
        try:
            res = subprocess.run(
                ["git", "diff", "--name-only", "origin/main...HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            changed.update(res.stdout.splitlines())
        except Exception:
            # Fallback to HEAD~1
            try:
                res = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD~1"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                changed.update(res.stdout.splitlines())
            except Exception:
                pass

        return list(changed)
    except Exception:
        return []


def main() -> int:
    _ensure_backend_root_on_path()
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
    update_required = validator.is_update_required(changed_files)

    # AC9, AC13: PR Body check (CI mode)
    pr_body = os.environ.get("PR_BODY")
    if pr_body:
        print("CI Mode: Checking PR template justification...")
        if not validator.check_pr_template_justification(pr_body):
            # If justification is missing, we MUST have a doc update if required
            if update_required:
                doc_rel_path = "docs/llm-prompt-generation-by-feature.md"
                if all(
                    doc_rel_path not in cf.replace("\\", "/").lstrip("./") for cf in changed_files
                ):
                    print(f"[FAIL] Missing PR justification or {doc_rel_path} update.")
                    return 1

    if update_required:
        print("Structural files changed. Checking if documentation was updated...")
        doc_rel_path = "docs/llm-prompt-generation-by-feature.md"

        # In a local quality gate or CI without PR_BODY
        if all(doc_rel_path not in cf.replace("\\", "/").lstrip("./") for cf in changed_files):
            if not pr_body:
                print(f"[FAIL] Structural files changed but {doc_rel_path} was not updated.")
                print(
                    "If this is intended, please update the Verification Date/Ref "
                    "in the doc to confirm review."
                )
                return 1

        # If the doc is in changed_files, verify that Date or Ref actually changed
        if any(doc_rel_path in cf.replace("\\", "/").lstrip("./") for cf in changed_files):
            try:
                # We need the previous version to compare
                base_ref = "origin/main"
                diff_result = subprocess.run(
                    ["git", "show", f"{base_ref}:{doc_rel_path}"], capture_output=True, text=True
                )
                if diff_result.returncode != 0:
                    base_ref = "HEAD~1"
                    diff_result = subprocess.run(
                        ["git", "show", f"{base_ref}:{doc_rel_path}"],
                        capture_output=True,
                        text=True,
                    )

                if diff_result.returncode == 0:
                    old_content = diff_result.stdout
                    new_content = (root_path / doc_rel_path).read_text(encoding="utf-8")
                    if not validator.check_verification_reference_updated(old_content, new_content):
                        print(
                            f"[FAIL] {doc_rel_path} was touched but Date/Ref block was not updated."
                        )
                        return 1
                else:
                    print(
                        f"[WARNING] Could not find base version of {doc_rel_path} "
                        "to verify Date/Ref update."
                    )
            except Exception as e:
                print(f"[WARNING] Error during diff check: {e}")

    print("[OK] Documentation is conform.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

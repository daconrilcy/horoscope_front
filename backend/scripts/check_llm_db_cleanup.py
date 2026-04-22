import json
import sys
from pathlib import Path


def _ensure_backend_root_on_path() -> Path:
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))
    return backend_root


def main() -> int:
    use_json = "--json" in sys.argv
    backend_root = _ensure_backend_root_on_path()

    from app.ops.llm.db_cleanup_validator import (
        LlmDbCleanupValidator,
        llm_db_cleanup_registry_version,
    )

    repo_root = backend_root.parent
    validator = LlmDbCleanupValidator(repo_root)
    violations = validator.validate_all()

    if use_json:
        payload = {
            "status": "fail" if violations else "ok",
            "registry_version": llm_db_cleanup_registry_version(repo_root),
            "violations": [
                {
                    "code": violation.code,
                    "message": violation.message,
                    "detail": violation.detail,
                }
                for violation in violations
            ],
        }
        print(json.dumps(payload, indent=2))
        return 1 if violations else 0

    print("==> Checking LLM DB cleanup registry...")
    if violations:
        print("[FAIL] LLM DB cleanup guard failed:")
        for violation in violations:
            print(f"  - {violation.as_user_string()}")
        return 1

    print(
        "[OK] LLM DB cleanup registry is aligned "
        f"(version {llm_db_cleanup_registry_version(repo_root)})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

import sys
from pathlib import Path


def _ensure_backend_root_on_path() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def main() -> int:
    _ensure_backend_root_on_path()
    from app.services.feature_registry_consistency_validator import (
        FeatureRegistryConsistencyError,
        FeatureRegistryConsistencyValidator,
    )

    try:
        FeatureRegistryConsistencyValidator.validate()
        print("[OK] Feature scope registry is consistent.")
        return 0
    except FeatureRegistryConsistencyError as exc:
        print(f"[ERROR] {exc}")
        return 1
    except Exception as exc:
        print(f"[CRITICAL] Unexpected error: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())

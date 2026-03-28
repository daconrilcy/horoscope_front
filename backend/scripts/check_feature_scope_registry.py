import os
import sys

# Ensure the app can be imported
sys.path.append(os.getcwd())

from app.services.feature_registry_consistency_validator import (
    FeatureRegistryConsistencyError,
    FeatureRegistryConsistencyValidator,
)

def main() -> int:
    try:
        FeatureRegistryConsistencyValidator.validate()
        print("[OK] Feature scope registry is consistent.")
        return 0
    except FeatureRegistryConsistencyError as exc:
        print(f"[ERROR] {exc}")
        return 1
    except Exception as e:
        print(f"[CRITICAL] Unexpected error: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())


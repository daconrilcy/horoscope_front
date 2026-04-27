#!/usr/bin/env python3
"""Execute la validation complete du package CONDAMAD Domain Auditor."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

SELF_VALIDATE_CHILD_ENV = "CONDAMAD_DOMAIN_AUDIT_SELF_VALIDATE_CHILD"


def main() -> int:
    """Lance la suite complete de self-tests sans sous-processus."""
    skill_root = Path(__file__).resolve().parents[1]
    os.environ[SELF_VALIDATE_CHILD_ENV] = "1"
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(skill_root / "scripts" / "self_tests"),
        pattern="*selftest.py",
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Smoke test manuel du wrapper de self-validation.

Ce fichier ne matche pas `*selftest.py` pour eviter une recursion pendant la
suite standard de self-tests.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]


def main() -> int:
    """Verifie que le wrapper officiel retourne 0 sans exposer les logs."""
    result = subprocess.run(
        [
            sys.executable,
            "-S",
            "-B",
            str(SCRIPT_DIR / "condamad_domain_audit_self_validate.py"),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        print(
            f"ERROR: wrapper smoke test failed with code {result.returncode}",
            file=sys.stderr,
        )
        return result.returncode
    print("Wrapper smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

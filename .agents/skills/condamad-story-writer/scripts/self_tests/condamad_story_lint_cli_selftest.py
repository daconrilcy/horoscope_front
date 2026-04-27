#!/usr/bin/env python3
"""Self-tests CLI du lint CONDAMAD Story Writer.

Ces tests couvrent le mode strict du lint et l'explication des contrats.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from condamad_story_validate_selftest import VALID_STORY  # noqa: E402


class CondamadStoryLintCliSelfTest(unittest.TestCase):
    """Verifie les comportements CLI ajoutes autour du lint."""

    def write_story(self, content: str) -> Path:
        """Ecrit une story temporaire pour les tests CLI."""
        directory = Path(tempfile.mkdtemp())
        path = directory / "00-story.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_lint_strict_fails_on_warning(self) -> None:
        """Le mode strict transforme les warnings anti-flou en erreur."""
        story = VALID_STORY.replace(
            "A guard test fails if the old root import returns.",
            "A guard test fails if the old root import returns and old imports stay absent.",
        ).replace(
            '| Billing imports | `backend/app/services/quota_usage_service.py` | `backend/app/services/billing/quota_runtime.py` | Backend service consumers | `backend/app/tests/unit/test_billing_imports.py` | `rg "app.services.quota_usage_service" backend/app backend/tests` returns no nominal import. | External consumer evidence appears. |',
            "| Billing imports | `old.py` | `new.py` | Backend consumers | `test.py` | No shim remains. | External evidence appears. |",
        )
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                "-B",
                str(SCRIPT_DIR / "condamad_story_lint.py"),
                "--strict",
                str(self.write_story(story)),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Strict warning", result.stdout)

    def test_validate_explain_contracts_reports_archetype(self) -> None:
        """Le validateur explique les contrats requis et presents."""
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                "-B",
                str(SCRIPT_DIR / "condamad_story_validate.py"),
                "--explain-contracts",
                str(self.write_story(VALID_STORY)),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Primary archetype: namespace-convergence", result.stdout)
        self.assertIn("Batch Migration", result.stdout)


if __name__ == "__main__":
    unittest.main()

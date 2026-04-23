# Ce module empeche la reintroduction d'acces directs a l'horloge backend.
"""Garde-fou Story 70-18 pour la centralisation des appels DateTime."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"
PROVIDER_FILE = APP_ROOT / "core" / "datetime_provider.py"
SCRIPT_ROOTS = (PROJECT_ROOT / "scripts", PROJECT_ROOT / "tools")


def test_backend_current_time_accesses_are_centralized() -> None:
    """Verifie que le code applicatif utilise le provider DateTime canonique."""
    forbidden_patterns = ("datetime.now(", "date.today(")
    offenders: list[str] = []

    roots = (APP_ROOT, *[root for root in SCRIPT_ROOTS if root.exists()])
    for root in roots:
        for path in root.rglob("*.py"):
            if path == PROVIDER_FILE:
                continue
            if "__pycache__" in path.parts or "tests" in path.parts:
                continue

            for line_number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if any(pattern in line for pattern in forbidden_patterns):
                    offenders.append(
                        f"{path.relative_to(PROJECT_ROOT)}:{line_number}:{line.strip()}"
                    )

    assert offenders == [], "Direct datetime access detected:\n" + "\n".join(offenders)

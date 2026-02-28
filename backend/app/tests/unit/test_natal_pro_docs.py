from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DOC_PATH = REPO_ROOT / "docs" / "natal-pro-dev-guide.md"


def test_natal_pro_doc_exists_and_covers_required_sections() -> None:
    content = DOC_PATH.read_text(encoding="utf-8")

    required_markers = [
        "Reglages pro figes",
        "Erreurs standardisees 422 et 503",
        "Guide de validation Golden Pro",
        "/v1/astrology-engine/natal/prepare",
        "/v1/astrology-engine/natal/calculate",
        "planets_deg = 0.01",
        "angles_deg = 0.05",
        "SWISSEPH_PRO_MODE",
        "ephemeris_path_version",
    ]
    for marker in required_markers:
        assert marker in content


def test_natal_pro_doc_local_markdown_links_are_resolvable() -> None:
    content = DOC_PATH.read_text(encoding="utf-8")
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", content)
    unresolved: list[str] = []

    for link in links:
        normalized = link.strip()
        if not normalized or normalized.startswith(("http://", "https://", "mailto:")):
            continue
        if normalized.startswith("#"):
            continue

        target_path = (DOC_PATH.parent / normalized).resolve()
        if not target_path.exists():
            unresolved.append(normalized)

    assert not unresolved, f"Liens locaux invalides dans {DOC_PATH}: {unresolved}"


def test_natal_pro_doc_contains_executable_style_curl_examples() -> None:
    content = DOC_PATH.read_text(encoding="utf-8")

    assert 'curl -sS -X POST "http://127.0.0.1:8000/v1/astrology-engine/natal/prepare"' in content
    assert 'curl -sS -X POST "http://127.0.0.1:8000/v1/astrology-engine/natal/calculate"' in content
    assert "--max-time 30" in content
    assert "--max-time 60" in content

    # Basic JSON validity check for examples (simplified extraction)
    import json

    json_blocks = re.findall(r"-d '({.*?})'", content, re.DOTALL)
    for block in json_blocks:
        try:
            json.loads(block)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in documentation example: {block}\nError: {e}")

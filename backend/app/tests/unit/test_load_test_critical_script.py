# Garde du manifest des scenarios de charge critique.
"""Verifie le routage explicite des scenarios PowerShell de charge critique."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = REPO_ROOT / "scripts" / "load-test-critical.ps1"
EXPECTED_GROUPS = {"smoke", "llm", "b2b", "destructive-privacy", "stress-incidents"}


def _script_text() -> str:
    """Charge le script PowerShell comme source de verite du manifest."""
    return SCRIPT_PATH.read_text(encoding="utf-8")


def _scenario_group_blocks() -> dict[str, str]:
    """Extrait les blocs de groupes du manifest PowerShell."""
    blocks: dict[str, list[str]] = {}
    current_group: str | None = None
    group_pattern = re.compile(r'^\s{4}("?[\w-]+"?) = @\($')

    for line in _script_text().splitlines():
        match = group_pattern.match(line)
        if match:
            current_group = match.group(1).strip('"')
            blocks[current_group] = []
            continue
        if current_group is not None:
            blocks[current_group].append(line)

    return {group: "\n".join(lines) for group, lines in blocks.items()}


def _scenario_names(group_block: str) -> set[str]:
    """Retourne les noms declares dans un bloc de groupe."""
    return set(re.findall(r'name = "([^"]+)"', group_block))


def _default_scenario_groups() -> set[str]:
    """Parse la selection de groupes utilisee sans parametre explicite."""
    match = re.search(
        r"\[string\[\]\]\$ScenarioGroups = @\((?P<groups>[^)]*)\)",
        _script_text(),
    )
    assert match is not None
    return set(re.findall(r'"([^"]+)"', match.group("groups")))


def test_expected_scenario_groups_exist() -> None:
    """Les responsabilites de charge critique sont separees par groupe canonique."""
    blocks = _scenario_group_blocks()

    assert set(blocks) == EXPECTED_GROUPS
    assert _scenario_names(blocks["smoke"]) == {
        "billing_quota",
        "privacy_export_status",
        "chat_conversations",
    }
    assert _scenario_names(blocks["llm"]) == {
        "llm_chat",
        "llm_guidance",
        "llm_natal",
        "llm_horoscope_daily",
    }
    assert _scenario_names(blocks["b2b"]) == {"b2b_weekly_by_sign"}
    assert _scenario_names(blocks["stress-incidents"]) == {
        "llm_stress_rate_limit",
        "llm_stress_timeout",
        "llm_recovery",
    }


def test_default_groups_exclude_privacy_delete_request() -> None:
    """Le scenario destructif privacy exige une selection explicite."""
    blocks = _scenario_group_blocks()
    default_groups = _default_scenario_groups()
    default_scenarios = set().union(*(_scenario_names(blocks[group]) for group in default_groups))

    assert "destructive-privacy" not in default_groups
    assert _scenario_names(blocks["destructive-privacy"]) == {"privacy_delete_request"}
    assert "privacy_delete_request" not in default_scenarios


def test_audited_story_and_obsolete_markers_are_absent() -> None:
    """Les libelles audites ne structurent plus le chemin actif."""
    content = _script_text()

    assert "Story 66.35" not in content
    assert "Legacy critical scenarios" not in content


def test_json_and_markdown_reports_remain_produced() -> None:
    """Le chemin existant continue d'ecrire le JSON puis de generer le Markdown."""
    content = _script_text()

    assert "($report | ConvertTo-Json -Depth 8) | Set-Content -Path $OutputPath" in content
    assert 'Join-Path $PSScriptRoot "generate-performance-report.ps1"' in content
    assert "-InputPath $OutputPath -OutputPath $mdReportPath" in content

# Garde du script de readiness release LLM.
"""Verifie que le cache pytest du script release LLM reste portable."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = REPO_ROOT / "scripts" / "llm-release-readiness.ps1"


def _script_content() -> str:
    """Retourne le contenu PowerShell du script readiness LLM."""
    return SCRIPT_PATH.read_text(encoding="utf-8")


def test_llm_release_readiness_cache_path_is_repo_relative_by_default() -> None:
    """Le cache pytest nominal doit etre calcule depuis le repo root."""
    content = _script_content()

    assert '[string]$PytestCachePath = ""' in content
    assert '$resolvedPytestCachePath = Join-Path $root ".pytest_cache_runtime"' in content
    assert "C:\\dev\\horoscope_front" not in content
    assert "-o cache_dir=" not in content


def test_llm_release_readiness_all_pytest_steps_reuse_cache_variable() -> None:
    """Chaque appel pytest release doit reutiliser la resolution canonique."""
    content = _script_content()

    assert content.count('-o "cache_dir=$resolvedPytestCachePath"') == 3


def test_llm_release_readiness_cache_override_is_explicit_only() -> None:
    """La surcharge doit etre un parametre explicite sans retour vers l'ancien chemin."""
    content = _script_content()

    assert "if (-not [string]::IsNullOrWhiteSpace($PytestCachePath))" in content
    assert "[System.IO.Path]::IsPathRooted($PytestCachePath)" in content
    assert "Join-Path $root $PytestCachePath" in content
    assert "C:\\dev\\horoscope_front" not in content


def test_llm_release_readiness_backend_steps_run_from_backend_root() -> None:
    """Les tests backend doivent charger la configuration pytest du backend."""
    content = _script_content()

    assert "function Invoke-BackendStep" in content
    assert "$backendAction = $Action" in content
    assert "& $backendAction" in content
    assert "Push-Location $backendRoot" in content
    assert r"pytest -q tests\integration\test_llm_release.py" in content
    assert r"tests\integration\test_llm_golden_regression.py" in content
    assert r"tests\integration\test_llm_provider_runtime_chaos.py" in content
    assert "backend\\tests\\integration" not in content
    assert "test_story_66_36_golden_regression.py" not in content
    assert "test_story_66_43_provider_runtime_chaos.py" not in content


def test_llm_release_readiness_stops_on_native_command_failure() -> None:
    """Un echec pytest ou python ne doit pas etre suivi d'un faux OK."""
    content = _script_content()

    assert "$global:LASTEXITCODE = 0" in content
    assert "if ($LASTEXITCODE -ne 0)" in content
    assert "failed with exit code $LASTEXITCODE" in content


def test_llm_release_readiness_rejects_no_go_report() -> None:
    """Le rapport agrege no-go doit faire echouer le script release."""
    content = _script_content()
    readiness_report_path = (
        '$readinessReportPath = Join-Path $resolvedOutputDir "llm-release-readiness.json"'
    )

    assert readiness_report_path in content
    assert "function Assert-ReadinessReportGo" in content
    assert "ConvertFrom-Json" in content
    assert '$report.decision -ne "go"' in content
    assert "LLM release readiness decision is" in content
    assert "Assert-ReadinessReportGo -ReportPath $readinessReportPath" in content

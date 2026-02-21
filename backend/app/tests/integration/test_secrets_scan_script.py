from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[4]
SCRIPTS_DIR = ROOT_DIR / "scripts"


def _powershell_executable() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def _run_ps_script(
    script: Path, args: list[str], env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    pwsh = _powershell_executable()
    if not pwsh:
        pytest.skip("PowerShell is required for secrets scan script tests.")
    return subprocess.run(
        [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *args],
        cwd=ROOT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_scan_secrets_passes_on_clean_source(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "backend" / "app").mkdir(parents=True, exist_ok=True)
    (repo / "backend" / "app" / "example.py").write_text(
        "JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    result = _run_ps_script(
        SCRIPTS_DIR / "scan-secrets.ps1",
        ["-RootPath", str(repo)],
        env,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "secrets_scan_ok" in result.stdout


def test_scan_secrets_fails_on_hardcoded_secret(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "backend" / "app").mkdir(parents=True, exist_ok=True)
    (repo / "backend" / "app" / "bad.py").write_text(
        "JWT_SECRET_KEY = 'prod-super-secret-key-value-1234567890'\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    result = _run_ps_script(
        SCRIPTS_DIR / "scan-secrets.ps1",
        ["-RootPath", str(repo)],
        env,
    )
    assert result.returncode != 0
    output = (result.stdout + result.stderr).lower()
    assert "secrets_scan_failed" in output
    assert "hardcoded_secret_assignment" in output


def test_scan_secrets_fails_on_openai_project_key_format(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "backend" / "app").mkdir(parents=True, exist_ok=True)
    (repo / "backend" / "app" / "bad_openai.py").write_text(
        "OPENAI_KEY = 'sk-proj-AbCdEfGhIjKlMnOpQrStUvWxYz0123456789'\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    result = _run_ps_script(
        SCRIPTS_DIR / "scan-secrets.ps1",
        ["-RootPath", str(repo)],
        env,
    )
    assert result.returncode != 0
    output = (result.stdout + result.stderr).lower()
    assert "secrets_scan_failed" in output
    assert "openai_key" in output


def test_scan_secrets_rejects_wildcard_allowlist_entry(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "backend" / "app").mkdir(parents=True, exist_ok=True)
    (repo / "backend" / "app" / "bad.py").write_text(
        "JWT_SECRET_KEY = 'prod-super-secret-key-value-1234567890'\n",
        encoding="utf-8",
    )
    allowlist = tmp_path / "allowlist.txt"
    allowlist.write_text("backend/app/*\n", encoding="utf-8")

    env = os.environ.copy()
    result = _run_ps_script(
        SCRIPTS_DIR / "scan-secrets.ps1",
        ["-RootPath", str(repo), "-AllowlistPath", str(allowlist)],
        env,
    )
    assert result.returncode != 0
    output = (result.stdout + result.stderr).lower()
    assert "wildcard entry" in output

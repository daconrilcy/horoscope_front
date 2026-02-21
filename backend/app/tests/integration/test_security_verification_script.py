from __future__ import annotations

import json
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
        pytest.skip("PowerShell is required for security verification script tests.")
    return subprocess.run(
        [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *args],
        cwd=ROOT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_security_verification_passes_with_non_blocking_findings(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    reports = repo / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    bandit_path = reports / "bandit.json"
    pip_audit_path = reports / "pip-audit.json"
    npm_audit_path = reports / "npm-audit.json"
    output_path = reports / "security-report.json"
    plan_path = reports / "security-plan.md"

    _write_json(bandit_path, {"results": []})
    _write_json(pip_audit_path, [])
    _write_json(
        npm_audit_path,
        {
            "vulnerabilities": {
                "left-pad": {"severity": "low", "fixAvailable": False},
            }
        },
    )

    env = os.environ.copy()
    result = _run_ps_script(
        SCRIPTS_DIR / "security-verification.ps1",
        [
            "-RootPath",
            str(repo),
            "-BanditReportPath",
            str(bandit_path),
            "-PipAuditReportPath",
            str(pip_audit_path),
            "-NpmAuditReportPath",
            str(npm_audit_path),
            "-OutputPath",
            str(output_path),
            "-RemediationPlanPath",
            str(plan_path),
        ],
        env,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert output_path.exists()
    assert plan_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8-sig"))
    assert payload["summary"]["findings_total"] == 1
    assert payload["summary"]["findings_by_severity"]["low"] == 1


def test_security_verification_fails_on_critical_finding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    reports = repo / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    bandit_path = reports / "bandit.json"
    pip_audit_path = reports / "pip-audit.json"
    npm_audit_path = reports / "npm-audit.json"

    _write_json(bandit_path, {"results": []})
    _write_json(pip_audit_path, [])
    _write_json(
        npm_audit_path,
        {
            "vulnerabilities": {
                "lodash": {"severity": "critical", "fixAvailable": True},
            }
        },
    )

    env = os.environ.copy()
    result = _run_ps_script(
        SCRIPTS_DIR / "security-verification.ps1",
        [
            "-RootPath",
            str(repo),
            "-BanditReportPath",
            str(bandit_path),
            "-PipAuditReportPath",
            str(pip_audit_path),
            "-NpmAuditReportPath",
            str(npm_audit_path),
        ],
        env,
    )
    assert result.returncode != 0
    output = (result.stdout + result.stderr).lower()
    assert "security_pack_failed" in output
    assert "npm-audit:npm:lodash" in output


def test_security_verification_allowlist_suppresses_finding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    reports = repo / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    bandit_path = reports / "bandit.json"
    pip_audit_path = reports / "pip-audit.json"
    npm_audit_path = reports / "npm-audit.json"
    allowlist_path = reports / "allowlist.txt"

    _write_json(bandit_path, {"results": []})
    _write_json(pip_audit_path, [])
    _write_json(
        npm_audit_path,
        {
            "vulnerabilities": {
                "lodash": {"severity": "critical", "fixAvailable": True},
            }
        },
    )
    allowlist_path.write_text("npm-audit:npm:lodash\n", encoding="utf-8")

    env = os.environ.copy()
    result = _run_ps_script(
        SCRIPTS_DIR / "security-verification.ps1",
        [
            "-RootPath",
            str(repo),
            "-BanditReportPath",
            str(bandit_path),
            "-PipAuditReportPath",
            str(pip_audit_path),
            "-NpmAuditReportPath",
            str(npm_audit_path),
            "-AllowlistPath",
            str(allowlist_path),
        ],
        env,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_security_verification_fails_on_pip_audit_without_severity(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    reports = repo / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    bandit_path = reports / "bandit.json"
    pip_audit_path = reports / "pip-audit.json"
    npm_audit_path = reports / "npm-audit.json"

    _write_json(bandit_path, {"results": []})
    _write_json(
        pip_audit_path,
        [{"name": "fastapi", "version": "0.129.0", "vulns": [{"id": "PYSEC-FAKE-1"}]}],
    )
    _write_json(npm_audit_path, {"vulnerabilities": {}})

    env = os.environ.copy()
    result = _run_ps_script(
        SCRIPTS_DIR / "security-verification.ps1",
        [
            "-RootPath",
            str(repo),
            "-BanditReportPath",
            str(bandit_path),
            "-PipAuditReportPath",
            str(pip_audit_path),
            "-NpmAuditReportPath",
            str(npm_audit_path),
        ],
        env,
    )
    assert result.returncode != 0
    output = (result.stdout + result.stderr).lower()
    assert "security_pack_failed" in output
    assert "pip-audit:pysec-fake-1:fastapi" in output

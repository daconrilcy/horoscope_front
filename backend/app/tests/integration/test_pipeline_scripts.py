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


def _write_mock_commands(mock_bin: Path) -> None:
    mock_bin.mkdir(parents=True, exist_ok=True)

    (mock_bin / "ruff.cmd").write_text(
        "@echo off\r\n"
        'echo ruff %*>>"%MOCK_LOG%"\r\n'
        'if /I "%MOCK_FAIL_STEP%"=="ruff" exit /b 1\r\n'
        "exit /b 0\r\n",
        encoding="utf-8",
    )
    (mock_bin / "pytest.cmd").write_text(
        "@echo off\r\n"
        'echo pytest %*>>"%MOCK_LOG%"\r\n'
        'if /I "%MOCK_FAIL_STEP%"=="pytest" exit /b 1\r\n'
        "exit /b 0\r\n",
        encoding="utf-8",
    )
    (mock_bin / "alembic.cmd").write_text(
        "@echo off\r\n"
        'echo alembic %*>>"%MOCK_LOG%"\r\n'
        'if /I "%MOCK_FAIL_STEP%"=="alembic" exit /b 1\r\n'
        'if /I "%1"=="heads" (\r\n'
        "  echo abc123 (head)\r\n"
        "  exit /b 0\r\n"
        ")\r\n"
        'if /I "%1"=="history" exit /b 0\r\n'
        "exit /b 0\r\n",
        encoding="utf-8",
    )
    (mock_bin / "npm.cmd").write_text(
        "@echo off\r\n"
        'echo npm %*>>"%MOCK_LOG%"\r\n'
        'if /I "%3"=="audit" (\r\n'
        '  echo {"vulnerabilities":{}}\r\n'
        "  exit /b 0\r\n"
        ")\r\n"
        'if /I "%4"=="lint" if /I "%MOCK_FAIL_STEP%"=="npm-lint" exit /b 1\r\n'
        'if /I "%4"=="test" if /I "%MOCK_FAIL_STEP%"=="npm-test" exit /b 1\r\n'
        'if /I "%4"=="build" if /I "%MOCK_FAIL_STEP%"=="npm-build" exit /b 1\r\n'
        "exit /b 0\r\n",
        encoding="utf-8",
    )
    (mock_bin / "bandit.cmd").write_text(
        "@echo off\r\n"
        'echo bandit %*>>"%MOCK_LOG%"\r\n'
        'if /I "%MOCK_FAIL_STEP%"=="bandit" exit /b 2\r\n'
        'echo {"results":[]}\r\n'
        "exit /b 0\r\n",
        encoding="utf-8",
    )
    (mock_bin / "pip-audit.cmd").write_text(
        "@echo off\r\n"
        'echo pip-audit %*>>"%MOCK_LOG%"\r\n'
        'if /I "%MOCK_FAIL_STEP%"=="pip-audit" exit /b 2\r\n'
        "echo []\r\n"
        "exit /b 0\r\n",
        encoding="utf-8",
    )
    (mock_bin / "docker.cmd").write_text(
        "@echo off\r\n"
        'echo docker %*>>"%MOCK_LOG%"\r\n'
        'if /I "%MOCK_FAIL_STEP%"=="docker" exit /b 1\r\n'
        "exit /b 0\r\n",
        encoding="utf-8",
    )


def _prepare_mock_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / ".venv" / "Scripts").mkdir(parents=True, exist_ok=True)
    (root / ".venv" / "Scripts" / "Activate.ps1").write_text(
        "$env:MOCK_VENV='1'\n", encoding="utf-8"
    )
    (root / "backend").mkdir(parents=True, exist_ok=True)
    (root / "frontend").mkdir(parents=True, exist_ok=True)
    return root


def _run_ps_script(script: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    pwsh = _powershell_executable()
    if not pwsh:
        pytest.skip("PowerShell is required for pipeline script tests.")
    return subprocess.run(
        [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
        cwd=ROOT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_quality_gate_success_executes_all_steps_in_order(tmp_path: Path) -> None:
    mock_root = _prepare_mock_root(tmp_path)
    mock_bin = tmp_path / "mock-bin"
    _write_mock_commands(mock_bin)
    log_file = tmp_path / "pipeline.log"

    env = os.environ.copy()
    env["QUALITY_GATE_ROOT"] = str(mock_root)
    env["MOCK_LOG"] = str(log_file)
    env["MOCK_FAIL_STEP"] = ""
    env["PATH"] = f"{mock_bin}{os.pathsep}{env.get('PATH', '')}"

    result = _run_ps_script(SCRIPTS_DIR / "quality-gate.ps1", env)

    assert result.returncode == 0, result.stderr + result.stdout
    assert "quality_gate_ok" in result.stdout
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert lines == [
        "bandit -r backend/app -x backend/app/tests -f json -q",
        "pip-audit --format json",
        "npm --prefix frontend audit --json",
        "ruff check backend",
        "pytest -q backend/app/tests",
        "alembic heads",
        "alembic history",
        "npm --prefix frontend run lint",
        "npm --prefix frontend run test -- --run",
        "npm --prefix frontend run build",
    ]


def test_quality_gate_stops_after_failure(tmp_path: Path) -> None:
    mock_root = _prepare_mock_root(tmp_path)
    mock_bin = tmp_path / "mock-bin"
    _write_mock_commands(mock_bin)
    log_file = tmp_path / "pipeline.log"

    env = os.environ.copy()
    env["QUALITY_GATE_ROOT"] = str(mock_root)
    env["MOCK_LOG"] = str(log_file)
    env["MOCK_FAIL_STEP"] = "pytest"
    env["PATH"] = f"{mock_bin}{os.pathsep}{env.get('PATH', '')}"

    result = _run_ps_script(SCRIPTS_DIR / "quality-gate.ps1", env)

    assert result.returncode != 0
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert lines == [
        "bandit -r backend/app -x backend/app/tests -f json -q",
        "pip-audit --format json",
        "npm --prefix frontend audit --json",
        "ruff check backend",
        "pytest -q backend/app/tests",
    ]


def test_predeploy_success_runs_quality_gate_then_docker(tmp_path: Path) -> None:
    mock_root = _prepare_mock_root(tmp_path)
    mock_bin = tmp_path / "mock-bin"
    _write_mock_commands(mock_bin)
    log_file = tmp_path / "pipeline.log"

    env = os.environ.copy()
    env["QUALITY_GATE_ROOT"] = str(mock_root)
    env["PREDEPLOY_ROOT"] = str(mock_root)
    env["PREDEPLOY_SKIP_STARTUP_SMOKE"] = "1"
    env["MOCK_LOG"] = str(log_file)
    env["MOCK_FAIL_STEP"] = ""
    env["PATH"] = f"{mock_bin}{os.pathsep}{env.get('PATH', '')}"

    result = _run_ps_script(SCRIPTS_DIR / "predeploy-check.ps1", env)

    assert result.returncode == 0, result.stderr + result.stdout
    assert "predeploy_check_ok" in result.stdout
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert lines[-1] == "docker compose config"
    assert lines[:5] == [
        "bandit -r backend/app -x backend/app/tests -f json -q",
        "pip-audit --format json",
        "npm --prefix frontend audit --json",
        "ruff check backend",
        "pytest -q backend/app/tests",
    ]


def test_predeploy_fails_if_docker_config_fails(tmp_path: Path) -> None:
    mock_root = _prepare_mock_root(tmp_path)
    mock_bin = tmp_path / "mock-bin"
    _write_mock_commands(mock_bin)
    log_file = tmp_path / "pipeline.log"

    env = os.environ.copy()
    env["QUALITY_GATE_ROOT"] = str(mock_root)
    env["PREDEPLOY_ROOT"] = str(mock_root)
    env["PREDEPLOY_SKIP_STARTUP_SMOKE"] = "1"
    env["MOCK_LOG"] = str(log_file)
    env["MOCK_FAIL_STEP"] = "docker"
    env["PATH"] = f"{mock_bin}{os.pathsep}{env.get('PATH', '')}"

    result = _run_ps_script(SCRIPTS_DIR / "predeploy-check.ps1", env)

    assert result.returncode != 0
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert "docker compose config" in lines

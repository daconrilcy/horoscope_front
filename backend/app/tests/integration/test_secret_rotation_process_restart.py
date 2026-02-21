from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[3]
RUNNER_MODULE = "app.tests.integration._subprocess.secret_rotation_restart_runner"


def _run_python_subprocess(phase: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", RUNNER_MODULE, phase],
        cwd=str(BACKEND_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=90,
    )


def _run_restart_flow_with_database(database_url: str) -> None:
    run_id = uuid4().hex

    old_jwt_secret = f"restart-old-jwt-{run_id}"
    new_jwt_secret = f"restart-new-jwt-{run_id}"
    old_credential_secret = f"restart-old-credential-{run_id}"
    new_credential_secret = f"restart-new-credential-{run_id}"

    phase1_env = os.environ.copy()
    phase1_env.update(
        {
            "APP_ENV": "development",
            "DATABASE_URL": database_url,
            "JWT_SECRET_KEY": old_jwt_secret,
            "JWT_PREVIOUS_SECRET_KEYS": "",
            "API_CREDENTIALS_SECRET_KEY": old_credential_secret,
            "API_CREDENTIALS_PREVIOUS_SECRET_KEYS": "",
        }
    )
    phase1_result = _run_python_subprocess("phase1", phase1_env)
    assert phase1_result.returncode == 0, phase1_result.stdout + phase1_result.stderr

    phase1_output = json.loads(phase1_result.stdout.strip().splitlines()[-1])

    phase2_env = os.environ.copy()
    phase2_env.update(
        {
            "APP_ENV": "development",
            "DATABASE_URL": database_url,
            "JWT_SECRET_KEY": new_jwt_secret,
            "JWT_PREVIOUS_SECRET_KEYS": old_jwt_secret,
            "API_CREDENTIALS_SECRET_KEY": new_credential_secret,
            "API_CREDENTIALS_PREVIOUS_SECRET_KEYS": old_credential_secret,
            "ROTATION_OLD_ACCESS_TOKEN": phase1_output["access_token"],
            "ROTATION_OLD_REFRESH_TOKEN": phase1_output["refresh_token"],
            "ROTATION_OLD_ENTERPRISE_CREDENTIAL": phase1_output["enterprise_credential"],
            "ROTATION_RUN_ID": run_id,
        }
    )
    phase2_result = _run_python_subprocess("phase2", phase2_env)
    assert phase2_result.returncode == 0, phase2_result.stdout + phase2_result.stderr


def test_rotation_survives_real_python_process_restart_with_http_flows(tmp_path: Path) -> None:
    database_file = tmp_path / f"rotation-restart-{uuid4().hex}.db"
    database_url = f"sqlite:///{database_file.as_posix()}"
    _run_restart_flow_with_database(database_url)


def test_rotation_survives_real_python_process_restart_with_http_flows_postgres() -> None:
    postgres_database_url = os.getenv("ROTATION_RESTART_POSTGRES_DATABASE_URL", "").strip()
    if not postgres_database_url:
        pytest.skip("ROTATION_RESTART_POSTGRES_DATABASE_URL is not set.")
    _run_restart_flow_with_database(postgres_database_url)

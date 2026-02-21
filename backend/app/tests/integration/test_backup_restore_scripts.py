from __future__ import annotations

import os
import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
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
        pytest.skip("PowerShell is required for backup/restore script tests.")
    return subprocess.run(
        [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *args],
        cwd=ROOT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def _run_external(command: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_sqlite_backup_and_restore_roundtrip(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    backend_dir = repo / "backend"
    backend_dir.mkdir(parents=True, exist_ok=True)
    original_db = backend_dir / "horoscope.db"
    original_db.write_bytes(b"version-1")

    env = os.environ.copy()
    env["BACKUP_REPO_ROOT"] = str(repo)
    env["RESTORE_ALLOW_NONINTERACTIVE"] = "1"
    env["BACKUP_METADATA_HMAC_KEY"] = "test-backup-integrity-key"

    runtime_env_file = backend_dir / ".env"
    runtime_env_file.write_text("APP_MODE=test\n", encoding="utf-8")
    compose_file = repo / "docker-compose.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")

    backup_result = _run_ps_script(
        SCRIPTS_DIR / "backup-db.ps1",
        ["-Mode", "sqlite"],
        env,
    )
    assert backup_result.returncode == 0, backup_result.stderr + backup_result.stdout
    assert "backup_ok mode=sqlite" in backup_result.stdout

    backup_files = sorted((repo / "backups" / "db").glob("sqlite-backup-*.db"))
    assert len(backup_files) == 1
    backup_file = backup_files[0]
    assert (Path(str(backup_file) + ".meta.json")).exists()
    runtime_files = sorted((repo / "backups" / "runtime").glob("runtime-backup-*.zip"))
    assert len(runtime_files) == 1
    runtime_backup_file = runtime_files[0]

    original_db.write_bytes(b"version-2")
    runtime_env_file.write_text("APP_MODE=broken\n", encoding="utf-8")

    restore_result = _run_ps_script(
        SCRIPTS_DIR / "restore-db.ps1",
        [
            "-BackupFile",
            str(backup_file),
            "-Mode",
            "sqlite",
            "-Force",
            "-RuntimeBackupFile",
            str(runtime_backup_file),
        ],
        env,
    )
    assert restore_result.returncode == 0, restore_result.stderr + restore_result.stdout
    assert "restore_ok mode=sqlite" in restore_result.stdout
    assert original_db.read_bytes() == b"version-1"
    assert runtime_env_file.read_text(encoding="utf-8") == "APP_MODE=test\n"


def test_backup_validate_fails_on_tampered_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    backend_dir = repo / "backend"
    backend_dir.mkdir(parents=True, exist_ok=True)
    db_file = backend_dir / "horoscope.db"
    db_file.write_bytes(b"seed")

    env = os.environ.copy()
    env["BACKUP_REPO_ROOT"] = str(repo)
    env["BACKUP_METADATA_HMAC_KEY"] = "test-backup-integrity-key"

    backup_result = _run_ps_script(
        SCRIPTS_DIR / "backup-db.ps1",
        ["-Mode", "sqlite"],
        env,
    )
    assert backup_result.returncode == 0, backup_result.stderr + backup_result.stdout

    backup_file = next((repo / "backups" / "db").glob("sqlite-backup-*.db"))
    backup_file.write_bytes(b"tampered")

    validate_result = _run_ps_script(
        SCRIPTS_DIR / "backup-validate.ps1",
        ["-BackupFile", str(backup_file)],
        env,
    )
    assert validate_result.returncode != 0
    assert "hash mismatch" in (validate_result.stderr + validate_result.stdout).lower()


def test_backup_validate_fails_without_integrity_key(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    backend_dir = repo / "backend"
    backend_dir.mkdir(parents=True, exist_ok=True)
    db_file = backend_dir / "horoscope.db"
    db_file.write_bytes(b"seed")

    env = os.environ.copy()
    env["BACKUP_REPO_ROOT"] = str(repo)
    env["BACKUP_METADATA_HMAC_KEY"] = "test-backup-integrity-key"

    backup_result = _run_ps_script(
        SCRIPTS_DIR / "backup-db.ps1",
        ["-Mode", "sqlite"],
        env,
    )
    assert backup_result.returncode == 0, backup_result.stderr + backup_result.stdout
    backup_file = next((repo / "backups" / "db").glob("sqlite-backup-*.db"))

    env_without_key = os.environ.copy()
    env_without_key["BACKUP_REPO_ROOT"] = str(repo)
    validate_result = _run_ps_script(
        SCRIPTS_DIR / "backup-validate.ps1",
        ["-BackupFile", str(backup_file)],
        env_without_key,
    )
    assert validate_result.returncode != 0
    assert (
        "backup_metadata_hmac_key is required"
        in (validate_result.stderr + validate_result.stdout).lower()
    )


def _write_fake_postgres_tools(tmp_path: Path) -> tuple[Path, Path]:
    tools_dir = tmp_path / "fake-pg-tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    restore_marker = tools_dir / "psql-restore-marker.txt"

    pg_dump_cmd = tools_dir / "pg_dump.cmd"
    pg_dump_cmd.write_text(
        "\n".join(
            [
                "@echo off",
                "setlocal EnableDelayedExpansion",
                "set out=",
                ":loop",
                'if "%~1"=="" goto done',
                'if "%~1"=="--file" (',
                "  set out=%~2",
                "  shift",
                "  shift",
                "  goto loop",
                ")",
                "shift",
                "goto loop",
                ":done",
                'if "%out%"=="" exit /b 2',
                '> "%out%" echo -- fake postgres dump',
                "exit /b 0",
            ]
        ),
        encoding="utf-8",
    )

    psql_cmd = tools_dir / "psql.cmd"
    psql_cmd.write_text(
        "\n".join(
            [
                "@echo off",
                "setlocal EnableDelayedExpansion",
                "set infile=",
                ":loop",
                'if "%~1"=="" goto done',
                'if "%~1"=="-f" (',
                "  set infile=%~2",
                "  shift",
                "  shift",
                "  goto loop",
                ")",
                "shift",
                "goto loop",
                ":done",
                'if "%infile%"=="" exit /b 2',
                'if not exist "%infile%" exit /b 3',
                f'> "{restore_marker}" echo %infile%',
                "exit /b 0",
            ]
        ),
        encoding="utf-8",
    )

    return tools_dir, restore_marker


def test_postgres_backup_and_restore_with_fake_cli(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["BACKUP_REPO_ROOT"] = str(repo)
    env["DATABASE_URL"] = "postgresql://demo:demo@localhost:5432/demo"
    env["BACKUP_METADATA_HMAC_KEY"] = "test-backup-integrity-key"
    tools_dir, restore_marker = _write_fake_postgres_tools(tmp_path)
    env["PATH"] = str(tools_dir) + os.pathsep + env.get("PATH", "")
    env["RESTORE_ALLOW_NONINTERACTIVE"] = "1"

    backup_result = _run_ps_script(
        SCRIPTS_DIR / "backup-db.ps1",
        ["-Mode", "postgres"],
        env,
    )
    assert backup_result.returncode == 0, backup_result.stderr + backup_result.stdout
    assert "backup_ok mode=postgres" in backup_result.stdout

    backup_files = sorted((repo / "backups" / "db").glob("postgres-backup-*.sql"))
    assert len(backup_files) == 1
    backup_file = backup_files[0]
    assert (Path(str(backup_file) + ".meta.json")).exists()

    restore_result = _run_ps_script(
        SCRIPTS_DIR / "restore-db.ps1",
        ["-BackupFile", str(backup_file), "-Mode", "postgres", "-Force"],
        env,
    )
    assert restore_result.returncode == 0, restore_result.stderr + restore_result.stdout
    assert "restore_ok mode=postgres" in restore_result.stdout
    assert restore_marker.exists()
    pre_restore_files = sorted(
        (repo / "backups" / "db" / "pre-restore").glob("postgres-pre-restore-*.sql")
    )
    assert len(pre_restore_files) == 1


def test_restore_sqlite_with_post_restore_health_check(tmp_path: Path) -> None:
    class _HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

    server = HTTPServer(("127.0.0.1", 0), _HealthHandler)
    server_port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        repo = tmp_path / "repo"
        backend_dir = repo / "backend"
        backend_dir.mkdir(parents=True, exist_ok=True)
        original_db = backend_dir / "horoscope.db"
        original_db.write_bytes(b"version-1")

        env = os.environ.copy()
        env["BACKUP_REPO_ROOT"] = str(repo)
        env["RESTORE_ALLOW_NONINTERACTIVE"] = "1"
        env["BACKUP_METADATA_HMAC_KEY"] = "test-backup-integrity-key"

        backup_result = _run_ps_script(
            SCRIPTS_DIR / "backup-db.ps1",
            ["-Mode", "sqlite"],
            env,
        )
        assert backup_result.returncode == 0, backup_result.stderr + backup_result.stdout
        backup_file = next((repo / "backups" / "db").glob("sqlite-backup-*.db"))

        restore_result = _run_ps_script(
            SCRIPTS_DIR / "restore-db.ps1",
            [
                "-BackupFile",
                str(backup_file),
                "-Mode",
                "sqlite",
                "-Force",
                "-PostRestoreHealthUrl",
                f"http://127.0.0.1:{server_port}/health",
            ],
            env,
        )
        assert restore_result.returncode == 0, restore_result.stderr + restore_result.stdout
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def test_postgres_backup_and_restore_real_cli_opt_in(tmp_path: Path) -> None:
    """Real E2E test with pg_dump/psql on a disposable Postgres DB.

    This test is opt-in and intentionally guarded because restore is destructive.
    """
    if os.getenv("RUN_POSTGRES_BACKUP_RESTORE_E2E") != "1":
        pytest.skip("Set RUN_POSTGRES_BACKUP_RESTORE_E2E=1 to enable real Postgres E2E test.")
    if os.getenv("BACKUP_RESTORE_E2E_ALLOW_DESTRUCTIVE") != "YES":
        pytest.skip(
            "Set BACKUP_RESTORE_E2E_ALLOW_DESTRUCTIVE=YES to acknowledge destructive restore."
        )

    database_url = os.getenv("BACKUP_RESTORE_E2E_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip(
            "Set BACKUP_RESTORE_E2E_DATABASE_URL (or DATABASE_URL) for real Postgres E2E test."
        )

    if not shutil.which("psql") or not shutil.which("pg_dump"):
        pytest.skip("psql and pg_dump are required for real Postgres E2E test.")

    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["BACKUP_REPO_ROOT"] = str(repo)
    env["DATABASE_URL"] = database_url
    env["RESTORE_ALLOW_NONINTERACTIVE"] = "1"
    env["BACKUP_METADATA_HMAC_KEY"] = "test-backup-integrity-key"

    setup_sql = (
        "CREATE TABLE IF NOT EXISTS backup_restore_e2e_table (id integer PRIMARY KEY);"
        "TRUNCATE backup_restore_e2e_table;"
        "INSERT INTO backup_restore_e2e_table (id) VALUES (1), (2);"
    )
    setup_result = _run_external(
        ["psql", database_url, "-v", "ON_ERROR_STOP=1", "-c", setup_sql],
        env,
    )
    assert setup_result.returncode == 0, setup_result.stderr + setup_result.stdout

    backup_result = _run_ps_script(
        SCRIPTS_DIR / "backup-db.ps1",
        ["-Mode", "postgres"],
        env,
    )
    assert backup_result.returncode == 0, backup_result.stderr + backup_result.stdout

    mutate_sql = "TRUNCATE backup_restore_e2e_table;"
    mutate_result = _run_external(
        ["psql", database_url, "-v", "ON_ERROR_STOP=1", "-c", mutate_sql],
        env,
    )
    assert mutate_result.returncode == 0, mutate_result.stderr + mutate_result.stdout

    backup_file = next((repo / "backups" / "db").glob("postgres-backup-*.sql"))
    restore_result = _run_ps_script(
        SCRIPTS_DIR / "restore-db.ps1",
        ["-BackupFile", str(backup_file), "-Mode", "postgres", "-Force"],
        env,
    )
    assert restore_result.returncode == 0, restore_result.stderr + restore_result.stdout

    count_result = _run_external(
        [
            "psql",
            database_url,
            "-t",
            "-A",
            "-v",
            "ON_ERROR_STOP=1",
            "-c",
            "SELECT COUNT(*) FROM backup_restore_e2e_table;",
        ],
        env,
    )
    assert count_result.returncode == 0, count_result.stderr + count_result.stdout
    assert count_result.stdout.strip() == "2"

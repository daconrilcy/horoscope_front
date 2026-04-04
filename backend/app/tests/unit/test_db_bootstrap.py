from pathlib import Path

from app.infra.db import bootstrap


def test_should_skip_auto_upgrade_under_pytest() -> None:
    assert bootstrap._should_auto_upgrade_local_sqlite() is False


def test_alembic_config_targets_current_database_url(monkeypatch: object, tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'bootstrap-test.db').as_posix()}"
    monkeypatch.setattr(bootstrap.settings, "database_url", database_url)

    config = bootstrap._alembic_config()

    assert config.get_main_option("sqlalchemy.url") == database_url
    assert Path(config.get_main_option("script_location")).name == "migrations"


def test_resolve_backend_root_falls_back_to_cwd_backend(
    monkeypatch: object, tmp_path: Path
) -> None:
    backend_root = tmp_path / "backend"
    backend_root.mkdir()
    (backend_root / "migrations").mkdir()
    (backend_root / "alembic.ini").write_text(
        "[alembic]\nscript_location = migrations\n",
        encoding="utf-8",
    )

    fake_module_file = (
        tmp_path
        / ".venv"
        / "Lib"
        / "site-packages"
        / "app"
        / "infra"
        / "db"
        / "bootstrap.py"
    )
    fake_module_file.parent.mkdir(parents=True)
    fake_module_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(bootstrap, "__file__", str(fake_module_file))
    monkeypatch.chdir(tmp_path)

    assert bootstrap._resolve_backend_root() == backend_root

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

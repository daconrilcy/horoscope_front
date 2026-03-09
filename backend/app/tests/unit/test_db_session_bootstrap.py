from app.infra.db import session as db_session_module


def test_get_db_session_bootstraps_local_schema_once(monkeypatch: object) -> None:
    calls: list[str] = []

    monkeypatch.setattr(db_session_module, "_local_schema_ready", False)

    def fake_bootstrap() -> None:
        calls.append("called")

    monkeypatch.setattr(
        db_session_module,
        "_ensure_local_sqlite_schema_ready_once",
        fake_bootstrap,
    )

    first_session = next(db_session_module.get_db_session())
    first_session.close()

    second_session = next(db_session_module.get_db_session())
    second_session.close()

    assert calls == ["called", "called"]


def test_ensure_local_sqlite_schema_ready_once_is_idempotent(monkeypatch: object) -> None:
    calls: list[str] = []
    monkeypatch.setattr(db_session_module, "_local_schema_ready", False)

    def fake_bootstrap() -> None:
        calls.append("called")

    monkeypatch.setattr(
        "app.infra.db.bootstrap.ensure_local_sqlite_schema_ready",
        fake_bootstrap,
    )

    db_session_module._ensure_local_sqlite_schema_ready_once()
    db_session_module._ensure_local_sqlite_schema_ready_once()

    assert calls == ["called"]

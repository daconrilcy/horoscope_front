# Commentaire global: ces tests comparent le schema runtime et la migration de l'audit narratif.
"""Controle les colonnes et contraintes DB de `narrative_answer_audit_v1`."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import CheckConstraint, create_engine, inspect, text

from app.core.config import settings
from app.infra.db.models.user_natal_interpretation import UserNatalInterpretationModel

BACKEND_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_PATH = (
    BACKEND_ROOT
    / "migrations"
    / "versions"
    / "20260525_0139_extend_user_natal_interpretations_audit_v1.py"
)


def _alembic_config() -> Config:
    """Construit une configuration Alembic backend pour les tests de migration."""
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "migrations"))
    return config


def test_user_natal_interpretation_schema_exposes_audit_columns() -> None:
    """Le schema SQLAlchemy charge les colonnes d'audit sur la table existante."""
    table = UserNatalInterpretationModel.__table__
    columns = set(table.columns.keys())
    checks = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert {
        "answer_id",
        "answer_type",
        "plan",
        "projection_version",
        "projection_hash",
        "llm_input_version",
        "llm_input_hash",
        "prompt_version",
        "prompt_ref",
        "prompt_snapshot_ref",
        "provider",
        "model",
        "grounding_status",
        "evidence_refs",
    } <= columns
    assert "ck_user_natal_interpretations_answer_type" in checks
    assert "ck_user_natal_interpretations_grounding_status" in checks


def test_migration_extends_existing_table_without_new_audit_table() -> None:
    """La migration cible la table existante et ne cree pas de table doublon."""
    content = MIGRATION_PATH.read_text(encoding="utf-8")

    assert 'down_revision: Union[str, Sequence[str], None] = "20260524_0138"' in content
    assert "op.create_table" not in content
    assert 'TABLE_NAME = "user_natal_interpretations"' in content
    assert "answer_type IN" in content
    assert "grounding_status IN" in content


def test_migration_extends_partial_sqlite_when_answer_id_already_exists(
    monkeypatch: object, tmp_path: Path
) -> None:
    """La migration reprend une base partiellement modifiee sans dupliquer `answer_id`."""
    db_path = tmp_path / "narrative-answer-audit-partial.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.upgrade(config, "20260524_0138")

    engine = create_engine(database_url, future=True)
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE TABLE user_natal_interpretations (
                        id INTEGER NOT NULL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        chart_id VARCHAR(36) NOT NULL,
                        level VARCHAR(16) NOT NULL,
                        created_at DATETIME NOT NULL,
                        prompt_version_id VARCHAR(36) NULL
                    )
                    """
                )
            )
            connection.execute(
                text(
                    "ALTER TABLE user_natal_interpretations "
                    "ADD COLUMN answer_id VARCHAR(96) DEFAULT 'legacy' NOT NULL"
                )
            )
            connection.execute(
                text(
                    """
                    INSERT INTO user_natal_interpretations (
                        id, user_id, chart_id, level, created_at, prompt_version_id, answer_id
                    ) VALUES
                        (1, 10, 'chart-1', 'short', CURRENT_TIMESTAMP, NULL, 'legacy'),
                        (2, 10, 'chart-2', 'complete', CURRENT_TIMESTAMP, NULL, 'answer-kept')
                    """
                )
            )

        command.upgrade(config, "head")

        with engine.connect() as connection:
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
            columns = {
                column["name"]
                for column in inspect(connection).get_columns("user_natal_interpretations")
            }
            checks = {
                check["name"]
                for check in inspect(connection).get_check_constraints("user_natal_interpretations")
            }
            rows = connection.execute(
                text(
                    """
                    SELECT id, answer_id, answer_type
                    FROM user_natal_interpretations
                    ORDER BY id
                    """
                )
            ).all()

        assert revision == ScriptDirectory.from_config(config).get_current_head()
        assert {
            "answer_id",
            "answer_type",
            "projection_hash",
            "llm_input_hash",
            "grounding_status",
            "evidence_refs",
        } <= columns
        assert "ck_user_natal_interpretations_answer_type" in checks
        assert "ck_user_natal_interpretations_grounding_status" in checks
        assert rows == [
            (1, "user_natal_interpretation:1", "basic"),
            (2, "answer-kept", "premium"),
        ]
    finally:
        engine.dispose()

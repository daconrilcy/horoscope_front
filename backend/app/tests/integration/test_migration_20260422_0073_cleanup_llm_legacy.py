"""Valide la migration 0073 sans reintroduire les champs runtime legacy supprimes ensuite."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from app.core.config import settings


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def test_cleanup_migration_archives_and_drops_prompt_fallback_and_use_case_index(
    monkeypatch: object, tmp_path: Path
) -> None:
    db_path = tmp_path / "migration-20260422-0073-cleanup.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.upgrade(config, "20260422_0072")

    engine = create_engine(database_url, future=True)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO llm_use_case_configs (
                    key,
                    display_name,
                    description,
                    output_schema_id,
                    allowed_persona_ids,
                    input_schema,
                    required_prompt_placeholders,
                    interaction_mode,
                    user_question_policy,
                    persona_strategy,
                    safety_profile,
                    fallback_use_case_key
                ) VALUES (
                    :key,
                    :display_name,
                    :description,
                    NULL,
                    '[]',
                    NULL,
                    '[]',
                    'structured',
                    'none',
                    'optional',
                    'astrology',
                    NULL
                )
                """
            ),
            {
                "key": "guidance_daily",
                "display_name": "Guidance Daily",
                "description": "Test",
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO llm_prompt_versions (
                    id,
                    use_case_key,
                    status,
                    developer_prompt,
                    model,
                    temperature,
                    max_output_tokens,
                    fallback_use_case_key,
                    created_by,
                    created_at,
                    published_at
                ) VALUES (
                    :id,
                    :use_case_key,
                    :status,
                    :developer_prompt,
                    :model,
                    :temperature,
                    :max_output_tokens,
                    :fallback_use_case_key,
                    :created_by,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                """
            ),
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "use_case_key": "guidance_daily",
                "status": "published",
                "developer_prompt": "Bonjour {{locale}}",
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "max_output_tokens": 256,
                "fallback_use_case_key": "natal_interpretation_short",
                "created_by": "test",
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO llm_call_logs (
                    id,
                    use_case,
                    provider,
                    model,
                    latency_ms,
                    tokens_in,
                    tokens_out,
                    cost_usd_estimated,
                    validation_status,
                    repair_attempted,
                    fallback_triggered,
                    request_id,
                    trace_id,
                    input_hash,
                    environment,
                    evidence_warnings_count,
                    timestamp,
                    expires_at
                ) VALUES (
                    :id,
                    :use_case,
                    :provider,
                    :model,
                    :latency_ms,
                    :tokens_in,
                    :tokens_out,
                    :cost_usd_estimated,
                    :validation_status,
                    :repair_attempted,
                    :fallback_triggered,
                    :request_id,
                    :trace_id,
                    :input_hash,
                    :environment,
                    :evidence_warnings_count,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                """
            ),
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "use_case": "guidance_daily",
                "provider": "openai",
                "model": "gpt-4o-mini",
                "latency_ms": 100,
                "tokens_in": 10,
                "tokens_out": 20,
                "cost_usd_estimated": 0.001,
                "validation_status": "VALID",
                "repair_attempted": 0,
                "fallback_triggered": 0,
                "request_id": "req-cleanup",
                "trace_id": "trace-cleanup",
                "input_hash": "hash-cleanup",
                "environment": "test",
                "evidence_warnings_count": 0,
            },
        )

    command.upgrade(config, "20260422_0073")

    with engine.connect() as connection:
        prompt_columns = {
            column["name"] for column in inspect(connection).get_columns("llm_prompt_versions")
        }
        call_log_indexes = {
            index["name"] for index in inspect(connection).get_indexes("llm_call_logs")
        }
        archive_row = (
            connection.execute(
                text(
                    """
                    SELECT prompt_version_id, fallback_use_case_key
                    FROM llm_prompt_version_fallback_archives
                    WHERE prompt_version_id = :prompt_version_id
                    """
                ),
                {"prompt_version_id": "11111111-1111-1111-1111-111111111111"},
            )
            .mappings()
            .one()
        )

    assert "fallback_use_case_key" not in prompt_columns
    assert "ix_llm_call_logs_use_case_timestamp" not in call_log_indexes
    assert archive_row["fallback_use_case_key"] == "natal_interpretation_short"

    command.upgrade(config, "head")

    command.downgrade(config, "20260422_0072")

    with engine.connect() as connection:
        prompt_columns_after_downgrade = {
            column["name"] for column in inspect(connection).get_columns("llm_prompt_versions")
        }
        call_log_indexes_after_downgrade = {
            index["name"] for index in inspect(connection).get_indexes("llm_call_logs")
        }
        restored_value = connection.execute(
            text(
                """
                SELECT fallback_use_case_key
                FROM llm_prompt_versions
                WHERE id = :prompt_version_id
                """
            ),
            {"prompt_version_id": "11111111-1111-1111-1111-111111111111"},
        ).scalar_one()

    assert "fallback_use_case_key" in prompt_columns_after_downgrade
    assert "ix_llm_call_logs_use_case_timestamp" in call_log_indexes_after_downgrade
    assert restored_value == "natal_interpretation_short"

    engine.dispose()

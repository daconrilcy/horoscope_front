"""Verifie la migration 20260424_0082 sur le retrait controle du legacy LLM."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from app.core.config import settings


def _alembic_config() -> Config:
    """Construit la configuration Alembic du backend pour les tests."""
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def _assert_json_empty_array(value: object) -> None:
    """Accepte la representation SQLite brute ou deserailisee d un JSON vide."""
    assert value in ("[]", [])


def test_migration_0082_archives_prompt_version_legacy_columns_before_drop(
    monkeypatch: object, tmp_path: Path
) -> None:
    """L upgrade archive les champs runtime legacy des prompt versions avant suppression."""
    db_path = tmp_path / "migration-20260424-0082-non-empty-prompt-legacy.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.upgrade(config, "20260423_0081")

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
                    fallback_use_case_key,
                    eval_failure_threshold
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
                    NULL,
                    :eval_failure_threshold
                )
                """
            ),
            {
                "key": "guidance_daily",
                "display_name": "Guidance Daily",
                "description": "Test",
                "eval_failure_threshold": 0.2,
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
                "created_by": "test",
            },
        )

    command.upgrade(config, "20260424_0082")

    with engine.connect() as connection:
        prompt_columns = {
            column["name"] for column in inspect(connection).get_columns("llm_prompt_versions")
        }
        archive_row = (
            connection.execute(
                text(
                    """
                    SELECT
                        prompt_version_id,
                        model,
                        temperature,
                        max_output_tokens
                    FROM llm_prompt_version_legacy_archives
                    WHERE prompt_version_id = :prompt_version_id
                    """
                ),
                {"prompt_version_id": "11111111-1111-1111-1111-111111111111"},
            )
            .mappings()
            .one()
        )

    assert "model" not in prompt_columns
    assert "temperature" not in prompt_columns
    assert "max_output_tokens" not in prompt_columns
    assert archive_row["prompt_version_id"] == "11111111-1111-1111-1111-111111111111"
    assert archive_row["model"] == "gpt-4o-mini"
    assert archive_row["temperature"] == 0.7
    assert archive_row["max_output_tokens"] == 256

    command.downgrade(config, "20260423_0081")

    with engine.connect() as connection:
        restored_prompt = (
            connection.execute(
                text(
                    """
                    SELECT model, temperature, max_output_tokens
                    FROM llm_prompt_versions
                    WHERE id = :prompt_version_id
                    """
                ),
                {"prompt_version_id": "11111111-1111-1111-1111-111111111111"},
            )
            .mappings()
            .one()
        )
        remaining_tables = set(inspect(connection).get_table_names())

    assert restored_prompt["model"] == "gpt-4o-mini"
    assert restored_prompt["temperature"] == 0.7
    assert restored_prompt["max_output_tokens"] == 256
    assert "llm_prompt_version_legacy_archives" not in remaining_tables

    engine.dispose()


def test_migration_0082_allows_seeded_empty_allowed_persona_ids(
    monkeypatch: object, tmp_path: Path
) -> None:
    """L upgrade archive les champs legacy de use case au lieu de les effacer silencieusement."""
    db_path = tmp_path / "migration-20260424-0082-empty-allowed-persona-ids.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.upgrade(config, "20260423_0081")

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
                    fallback_use_case_key,
                    eval_failure_threshold
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
                    NULL,
                    :eval_failure_threshold
                )
                """
            ),
            {
                "key": "guidance_daily",
                "display_name": "Guidance Daily",
                "description": "Test",
                "eval_failure_threshold": 0.2,
            },
        )

    command.upgrade(config, "20260424_0082")

    with engine.connect() as connection:
        use_case_columns = {
            column["name"] for column in inspect(connection).get_columns("llm_use_case_configs")
        }
        archive_columns = {
            column["name"]
            for column in inspect(connection).get_columns("llm_use_case_config_legacy_archives")
        }
        archive_row = (
            connection.execute(
                text(
                    """
                    SELECT
                        use_case_key,
                        allowed_persona_ids,
                        interaction_mode,
                        user_question_policy,
                        persona_strategy,
                        safety_profile
                    FROM llm_use_case_config_legacy_archives
                    WHERE use_case_key = :use_case_key
                    """
                ),
                {"use_case_key": "guidance_daily"},
            )
            .mappings()
            .one()
        )

    assert "allowed_persona_ids" not in use_case_columns
    assert "allowed_persona_ids" in archive_columns
    assert archive_row["use_case_key"] == "guidance_daily"
    _assert_json_empty_array(archive_row["allowed_persona_ids"])
    assert archive_row["interaction_mode"] == "structured"
    assert archive_row["user_question_policy"] == "none"
    assert archive_row["persona_strategy"] == "optional"
    assert archive_row["safety_profile"] == "astrology"

    engine.dispose()


def test_migration_0082_backfills_provider_compat_into_operational_metadata(
    monkeypatch: object, tmp_path: Path
) -> None:
    """L upgrade doit recopier `provider_compat` dans les metadonnees canoniques."""
    db_path = tmp_path / "migration-20260424-0082-provider-compat.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.upgrade(config, "20260423_0081")

    engine = create_engine(database_url, future=True)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO llm_call_logs (
                    id,
                    use_case,
                    provider_compat,
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
                    :provider_compat,
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
                "provider_compat": "openai",
                "model": "gpt-4o-mini",
                "latency_ms": 100,
                "tokens_in": 10,
                "tokens_out": 20,
                "cost_usd_estimated": 0.001,
                "validation_status": "VALID",
                "repair_attempted": 0,
                "fallback_triggered": 0,
                "request_id": "req-provider-compat",
                "trace_id": "trace-provider-compat",
                "input_hash": "hash-provider-compat",
                "environment": "test",
                "evidence_warnings_count": 0,
            },
        )

    command.upgrade(config, "20260424_0082")

    with engine.connect() as connection:
        call_log_columns = {
            column["name"] for column in inspect(connection).get_columns("llm_call_logs")
        }
        metadata_row = (
            connection.execute(
                text(
                    """
                    SELECT executed_provider
                    FROM llm_call_log_operational_metadata
                    WHERE call_log_id = :call_log_id
                    """
                ),
                {"call_log_id": "22222222-2222-2222-2222-222222222222"},
            )
            .mappings()
            .one()
        )

    assert "provider_compat" not in call_log_columns
    assert metadata_row["executed_provider"] == "openai"

    engine.dispose()


def test_migration_0082_restores_dropped_checks_and_provider_on_downgrade(
    monkeypatch: object, tmp_path: Path
) -> None:
    """Le downgrade doit reconstruire le schema et recopier `provider_compat`."""
    db_path = tmp_path / "migration-20260424-0082-downgrade-provider-restore.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    engine = create_engine(database_url, future=True)
    command.upgrade(config, "20260423_0081")

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
                    fallback_use_case_key,
                    eval_failure_threshold
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
                    NULL,
                    :eval_failure_threshold
                )
                """
            ),
            {
                "key": "guidance_daily",
                "display_name": "Guidance Daily",
                "description": "Test",
                "eval_failure_threshold": 0.2,
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO llm_call_logs (
                    id,
                    use_case,
                    provider_compat,
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
                    :provider_compat,
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
                "id": "33333333-3333-3333-3333-333333333333",
                "use_case": "guidance_daily",
                "provider_compat": "openai",
                "model": "gpt-4o-mini",
                "latency_ms": 100,
                "tokens_in": 10,
                "tokens_out": 20,
                "cost_usd_estimated": 0.001,
                "validation_status": "VALID",
                "repair_attempted": 0,
                "fallback_triggered": 0,
                "request_id": "req-provider-restore",
                "trace_id": "trace-provider-restore",
                "input_hash": "hash-provider-restore",
                "environment": "test",
                "evidence_warnings_count": 0,
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO llm_call_log_operational_metadata (
                    id,
                    call_log_id,
                    executed_provider
                ) VALUES (
                    :id,
                    :call_log_id,
                    :executed_provider
                )
                """
            ),
            {
                "id": "44444444-4444-4444-4444-444444444444",
                "call_log_id": "33333333-3333-3333-3333-333333333333",
                "executed_provider": "openai",
            },
        )

    command.upgrade(config, "20260424_0082")

    with engine.connect() as connection:
        assembly_columns = {
            column["name"] for column in inspect(connection).get_columns("llm_assembly_configs")
        }
        call_log_columns = {
            column["name"] for column in inspect(connection).get_columns("llm_call_logs")
        }

    assert "interaction_mode" not in assembly_columns
    assert "user_question_policy" not in assembly_columns
    assert "provider_compat" not in call_log_columns

    command.downgrade(config, "20260423_0081")

    with engine.connect() as connection:
        assembly_columns_after = {
            column["name"] for column in inspect(connection).get_columns("llm_assembly_configs")
        }
        call_log_columns_after = {
            column["name"] for column in inspect(connection).get_columns("llm_call_logs")
        }
        assembly_checks_after = {
            check["name"]
            for check in inspect(connection).get_check_constraints("llm_assembly_configs")
            if check.get("name")
        }
        call_log_checks_after = {
            check["name"]
            for check in inspect(connection).get_check_constraints("llm_call_logs")
            if check.get("name")
        }
        restored_provider = connection.execute(
            text(
                """
                SELECT provider_compat
                FROM llm_call_logs
                WHERE id = :id
                """
            ),
            {"id": "33333333-3333-3333-3333-333333333333"},
        ).scalar_one()
        restored_use_case = (
            connection.execute(
                text(
                    """
                    SELECT
                        allowed_persona_ids,
                        interaction_mode,
                        user_question_policy,
                        persona_strategy,
                        safety_profile
                    FROM llm_use_case_configs
                    WHERE key = :key
                    """
                ),
                {"key": "guidance_daily"},
            )
            .mappings()
            .one_or_none()
        )
        remaining_tables = set(inspect(connection).get_table_names())

    assert "interaction_mode" in assembly_columns_after
    assert "user_question_policy" in assembly_columns_after
    assert "provider_compat" in call_log_columns_after
    assert "ck_llm_assembly_configs_interaction_mode" in assembly_checks_after
    assert "ck_llm_assembly_configs_user_question_policy" in assembly_checks_after
    assert "ck_llm_call_logs_provider" in call_log_checks_after
    assert restored_provider == "openai"
    assert restored_use_case is not None
    _assert_json_empty_array(restored_use_case["allowed_persona_ids"])
    assert restored_use_case["interaction_mode"] == "structured"
    assert restored_use_case["user_question_policy"] == "none"
    assert restored_use_case["persona_strategy"] == "optional"
    assert restored_use_case["safety_profile"] == "astrology"
    assert "llm_use_case_config_legacy_archives" not in remaining_tables

    engine.dispose()

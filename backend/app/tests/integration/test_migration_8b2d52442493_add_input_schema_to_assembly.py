import json
import uuid
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


def test_migration_8b2d_backfills_existing_assembly_metadata(
    monkeypatch: object, tmp_path: Path
) -> None:
    db_path = tmp_path / "migration-8b2d-assembly-input-schema.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.upgrade(config, "8a839be9fea4")

    engine = create_engine(database_url, future=True)
    use_case_key = "chat_astrologer"
    prompt_version_id = str(uuid.uuid4())
    assembly_id = str(uuid.uuid4())
    input_schema = {
        "type": "object",
        "required": ["message"],
        "properties": {"message": {"type": "string", "maxLength": 1000}},
    }

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
                    safety_profile
                ) VALUES (
                    :key,
                    :display_name,
                    :description,
                    :output_schema_id,
                    :allowed_persona_ids,
                    :input_schema,
                    :required_prompt_placeholders,
                    :interaction_mode,
                    :user_question_policy,
                    :persona_strategy,
                    :safety_profile
                )
                """
            ),
            {
                "key": use_case_key,
                "display_name": "Chat Astrologer",
                "description": "Conversation astrologique canonique.",
                "output_schema_id": "ChatResponse_v1",
                "allowed_persona_ids": json.dumps([]),
                "input_schema": json.dumps(input_schema),
                "required_prompt_placeholders": json.dumps([]),
                "interaction_mode": "chat",
                "user_question_policy": "required",
                "persona_strategy": "optional",
                "safety_profile": "astrology",
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
                "id": prompt_version_id,
                "use_case_key": use_case_key,
                "status": "published",
                "developer_prompt": "Réponds à {{last_user_msg}}.",
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_output_tokens": 800,
                "fallback_use_case_key": None,
                "created_by": "test",
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO llm_assembly_configs (
                    id,
                    feature,
                    subfeature,
                    plan,
                    locale,
                    feature_template_ref,
                    subfeature_template_ref,
                    persona_ref,
                    execution_profile_ref,
                    plan_rules_ref,
                    execution_config,
                    output_contract_ref,
                    length_budget,
                    interaction_mode,
                    user_question_policy,
                    fallback_use_case,
                    feature_enabled,
                    subfeature_enabled,
                    persona_enabled,
                    plan_rules_enabled,
                    status,
                    created_by,
                    created_at,
                    published_at
                ) VALUES (
                    :id,
                    :feature,
                    :subfeature,
                    :plan,
                    :locale,
                    :feature_template_ref,
                    NULL,
                    NULL,
                    NULL,
                    NULL,
                    :execution_config,
                    NULL,
                    NULL,
                    :interaction_mode,
                    :user_question_policy,
                    NULL,
                    1,
                    1,
                    1,
                    1,
                    :status,
                    :created_by,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                """
            ),
            {
                "id": assembly_id,
                "feature": "chat",
                "subfeature": "astrologer",
                "plan": "free",
                "locale": "fr-FR",
                "feature_template_ref": prompt_version_id,
                "execution_config": json.dumps(
                    {
                        "model": "gpt-4o",
                        "temperature": 0.7,
                        "max_output_tokens": 800,
                        "timeout_seconds": 60,
                    }
                ),
                "interaction_mode": "structured",
                "user_question_policy": "none",
                "status": "published",
                "created_by": "test",
            },
        )

    command.upgrade(config, "head")

    with engine.connect() as connection:
        columns = {
            column["name"] for column in inspect(connection).get_columns("llm_assembly_configs")
        }
        row = (
            connection.execute(
                text(
                    """
                SELECT input_schema, output_contract_ref, interaction_mode, user_question_policy
                FROM llm_assembly_configs
                WHERE id = :assembly_id
                """
                ),
                {"assembly_id": assembly_id},
            )
            .mappings()
            .one()
        )

    assert "input_schema" in columns
    assert json.loads(row["input_schema"]) == input_schema
    assert row["output_contract_ref"] == "ChatResponse_v1"
    assert row["interaction_mode"] == "chat"
    assert row["user_question_policy"] == "required"

    engine.dispose()

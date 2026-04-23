from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.llm.configuration.canonical_use_case_registry import (
    ASTRO_RESPONSE_V3_JSON_SCHEMA,
    CANONICAL_OUTPUT_SCHEMAS,
    CANONICAL_USE_CASE_CONTRACTS,
    CHAT_RESPONSE_V1,
)
from app.infra.db.models import LlmOutputSchemaModel, LlmPersonaModel, LlmUseCaseConfigModel
from app.infra.db.session import SessionLocal

# Legacy test imports remain temporarily supported here while the seed module
# delegates canonical contracts to the shared registry.
__all__ = [
    "ASTRO_RESPONSE_V3_JSON_SCHEMA",
    "CHAT_RESPONSE_V1",
    "seed_canonical_contracts",
    "seed_output_schemas",
    "seed_use_cases",
]


class SeedValidationError(Exception):
    """Raised when seed configuration is invalid."""

    pass


def seed_output_schemas(db: Session) -> dict[str, LlmOutputSchemaModel]:
    schema_map: dict[str, LlmOutputSchemaModel] = {}
    for schema_def in CANONICAL_OUTPUT_SCHEMAS:
        stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == schema_def.name)
        schema = db.execute(stmt).scalar_one_or_none()
        if not schema:
            schema = LlmOutputSchemaModel(
                name=schema_def.name,
                json_schema=schema_def.json_schema,
                version=schema_def.version,
            )
            db.add(schema)
            db.flush()
        else:
            schema.json_schema = schema_def.json_schema
            schema.version = schema_def.version
        schema_map[schema_def.name] = schema
    return schema_map


def seed_use_cases(db: Session) -> None:
    stmt_persona = select(LlmPersonaModel).where(LlmPersonaModel.name == "Astrologue Standard")
    default_persona = db.execute(stmt_persona).scalars().first()

    if not default_persona:
        default_persona = LlmPersonaModel(
            name="Astrologue Standard",
            description="Persona par défaut pour les services d'astrologie.",
            tone="Bienveillant et professionnel",
            verbosity="medium",
            style_markers=["précis", "empathique"],
            boundaries="Ne donne pas de conseils médicaux ou financiers fermes.",
            enabled=True,
        )
        db.add(default_persona)
        db.flush()

    default_persona_id = str(default_persona.id)
    enabled_personas = (
        db.execute(
            select(LlmPersonaModel)
            .where(LlmPersonaModel.enabled == True)  # noqa: E712
            .order_by(LlmPersonaModel.name)
        )
        .scalars()
        .all()
    )
    enabled_persona_ids = [str(persona.id) for persona in enabled_personas] or [default_persona_id]

    schema_map = seed_output_schemas(db)

    for contract in CANONICAL_USE_CASE_CONTRACTS:
        stmt = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == contract.key)
        use_case = db.execute(stmt).scalar_one_or_none()
        eval_failure_threshold = (
            contract.eval_failure_threshold if contract.eval_failure_threshold is not None else 0.20
        )

        schema_id = None
        if contract.output_schema_name and contract.output_schema_name in schema_map:
            schema_id = str(schema_map[contract.output_schema_name].id)

        if not use_case:
            use_case = LlmUseCaseConfigModel(
                key=contract.key,
                display_name=contract.display_name,
                description=contract.description,
                input_schema=contract.input_schema,
                output_schema_id=schema_id,
                persona_strategy=contract.persona_strategy,
                safety_profile=contract.safety_profile,
                required_prompt_placeholders=contract.required_prompt_placeholders,
                fallback_use_case_key=contract.fallback_use_case_key,
                interaction_mode=contract.interaction_mode,
                user_question_policy=contract.user_question_policy,
                allowed_persona_ids=[],
                eval_fixtures_path=contract.eval_fixtures_path,
                eval_failure_threshold=eval_failure_threshold,
                golden_set_path=contract.golden_set_path,
            )
            db.add(use_case)
        else:
            use_case.display_name = contract.display_name
            use_case.description = contract.description
            use_case.input_schema = contract.input_schema
            use_case.output_schema_id = schema_id
            use_case.persona_strategy = contract.persona_strategy
            use_case.safety_profile = contract.safety_profile
            use_case.required_prompt_placeholders = contract.required_prompt_placeholders
            use_case.fallback_use_case_key = contract.fallback_use_case_key
            use_case.interaction_mode = contract.interaction_mode
            use_case.user_question_policy = contract.user_question_policy
            use_case.eval_fixtures_path = contract.eval_fixtures_path
            use_case.eval_failure_threshold = eval_failure_threshold
            use_case.golden_set_path = contract.golden_set_path

        if use_case.persona_strategy == "required":
            use_case.allowed_persona_ids = enabled_persona_ids

    db.commit()


def seed_canonical_contracts(db: Session) -> None:
    """Neutral alias used by startup bootstrap without reviving legacy naming in main.py."""
    seed_use_cases(db)


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_use_cases(session)
        print("Use cases seed completed.")

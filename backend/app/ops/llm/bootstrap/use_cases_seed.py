"""Seeds canoniques LLM utilises par le bootstrap local et les scripts de convergence."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.llm.configuration.canonical_use_case_registry import (
    ASTRO_RESPONSE_V3_JSON_SCHEMA,
    CANONICAL_OUTPUT_SCHEMAS,
    CANONICAL_USE_CASE_CONTRACTS,
    CHAT_RESPONSE_V1,
    CanonicalUseCaseContract,
)
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import LlmUseCaseConfigModel
from app.infra.db.session import SessionLocal

# Legacy test imports remain temporarily supported here while the seed module
# delegates canonical contracts to the shared registry.
__all__ = [
    "ASTRO_RESPONSE_V3_JSON_SCHEMA",
    "CHAT_RESPONSE_V1",
    "SeedValidationError",
    "seed_bootstrap_contracts",
    "seed_canonical_contracts",
    "seed_output_schemas",
    "seed_use_cases",
    "validate_use_case_seed_contracts",
]


class SeedValidationError(Exception):
    """Signale une configuration de seed incompatible avec le contrat canonique."""


def validate_use_case_seed_contracts(
    contracts: Iterable[CanonicalUseCaseContract],
) -> None:
    """Valide les invariants metier des contrats de use cases avant le seed."""
    for contract in contracts:
        required_placeholders = [
            placeholder.strip()
            for placeholder in contract.required_prompt_placeholders
            if placeholder.strip()
        ]
        if not contract.key.strip():
            raise SeedValidationError("Un contrat de use case seed doit avoir une cle.")
        if contract.persona_strategy not in {"optional", "required", "forbidden"}:
            raise SeedValidationError(
                f"Use case '{contract.key}' declare une strategie persona invalide: "
                f"{contract.persona_strategy!r}."
            )
        if contract.persona_strategy == "required" and not required_placeholders:
            raise SeedValidationError(
                f"Use case '{contract.key}' exige une persona mais ne declare aucun "
                "placeholder requis non vide pour porter ce contrat."
            )


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
    validate_use_case_seed_contracts(CANONICAL_USE_CASE_CONTRACTS)

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

    seed_output_schemas(db)

    for contract in CANONICAL_USE_CASE_CONTRACTS:
        stmt = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == contract.key)
        use_case = db.execute(stmt).scalar_one_or_none()
        eval_failure_threshold = (
            contract.eval_failure_threshold if contract.eval_failure_threshold is not None else 0.20
        )

        if not use_case:
            use_case = LlmUseCaseConfigModel(
                key=contract.key,
                display_name=contract.display_name,
                description=contract.description,
                required_prompt_placeholders=contract.required_prompt_placeholders,
                eval_fixtures_path=contract.eval_fixtures_path,
                eval_failure_threshold=eval_failure_threshold,
                golden_set_path=contract.golden_set_path,
            )
            db.add(use_case)
        else:
            use_case.display_name = contract.display_name
            use_case.description = contract.description
            use_case.required_prompt_placeholders = contract.required_prompt_placeholders
            use_case.eval_fixtures_path = contract.eval_fixtures_path
            use_case.eval_failure_threshold = eval_failure_threshold
            use_case.golden_set_path = contract.golden_set_path

    db.commit()


def seed_canonical_contracts(db: Session) -> None:
    """Neutral alias used by startup bootstrap without reviving legacy naming in main.py."""
    seed_use_cases(db)


def seed_bootstrap_contracts(db: Session) -> None:
    """Expose un point d'entree canonique pour le bootstrap local sans contrat legacy."""
    seed_use_cases(db)


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_use_cases(session)
        print("Use cases seed completed.")

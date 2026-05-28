"""Tests de coherence schema ORM pour le contrat prompt theme astral."""

from __future__ import annotations

from sqlalchemy import inspect

from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import LlmPromptVersionModel, LlmUseCaseConfigModel
from tests.integration.app_db import open_app_db_session


def test_theme_astral_contract_reuses_existing_llm_tables_at_head() -> None:
    """Prouve qu'aucune table parallele n'est necessaire pour CS-364."""
    db = open_app_db_session()
    try:
        inspector = inspect(db.get_bind())
        tables = set(inspector.get_table_names())
    finally:
        db.close()

    expected_tables = {
        LlmUseCaseConfigModel.__tablename__,
        LlmPromptVersionModel.__tablename__,
        LlmOutputSchemaModel.__tablename__,
        LlmPersonaModel.__tablename__,
        LlmExecutionProfileModel.__tablename__,
        PromptAssemblyConfigModel.__tablename__,
    }
    assert expected_tables.issubset(tables)
    assert "theme_astral_prompt_contracts" not in tables
    assert "llm_theme_astral_contracts" not in tables

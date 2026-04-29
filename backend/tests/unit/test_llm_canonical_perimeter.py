# Garde-fou structurel AC33-AC50 pour le perimetre canonique LLM.
"""Verifie la separation compatibilite/canonique, la doc generee et les helpers autorises."""

from __future__ import annotations

from pathlib import Path

from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_canonical_perimeter import (
    ALLOWED_HELPER_MODULES,
    ALLOWED_MODEL_TABLES,
    AUTHORITATIVE_EXECUTION_FIELDS,
    MODEL_STRUCTURE,
    render_structure_markdown,
)
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_observability import LlmCallLogModel
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_release import LlmReleaseSnapshotModel

BACKEND_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = BACKEND_ROOT / "app" / "infra" / "db" / "models" / "llm"
GENERATED_DOC = BACKEND_ROOT / "docs" / "llm-model-structure.md"


def test_generated_llm_structure_doc_matches_code() -> None:
    """Garantit que la documentation structurelle reste synchronisee avec le code."""
    assert GENERATED_DOC.read_text(encoding="utf-8") == render_structure_markdown()


def test_canonical_perimeter_lists_authorized_tables_and_helpers() -> None:
    """Verifie que le perimetre formalise reste borne a la structure attendue."""
    assert "llm_assembly_configs" in ALLOWED_MODEL_TABLES
    assert "llm_call_log_operational_metadata" in ALLOWED_MODEL_TABLES
    assert "llm_canonical_perimeter" in ALLOWED_HELPER_MODULES
    assert {"execution_profile_ref", "output_schema_id"}.issubset(AUTHORITATIVE_EXECUTION_FIELDS)


def test_assembly_uses_fk_output_schema_and_keeps_historical_alias_outside_columns() -> None:
    """Verifie la FK canonique de schema et l isolement de l alias textuel legacy."""
    columns = PromptAssemblyConfigModel.__table__.columns.keys()
    relationships = set(PromptAssemblyConfigModel.__mapper__.relationships.keys())

    assert "output_schema_id" in columns
    assert "output_contract_ref" not in columns
    assert "output_schema" in relationships
    assert "feature_enabled" not in PromptAssemblyConfigModel.__dict__
    assert "persona_enabled" not in PromptAssemblyConfigModel.__dict__


def test_call_log_core_table_no_longer_redeclares_operational_columns() -> None:
    """Interdit le retour des colonnes operationnelles dans la table coeur des logs."""
    columns = set(LlmCallLogModel.__table__.columns.keys())
    assert "provider_compat" not in columns
    assert "manifest_entry_id" not in columns
    assert "executed_provider" not in columns
    assert "pipeline_kind" not in columns


def test_llm_models_reuse_canonical_helpers_without_local_redeclaration() -> None:
    """Interdit les duplications locales des helpers canonique dans les modeles LLM."""
    offenders: list[str] = []
    forbidden_tokens = (
        "def allowed_values_check(",
        "def published_unique_index(",
        "def validate_string_list_field(",
        "def validate_persona_formatting(",
        "default=lambda: datetime_provider.utcnow(",
    )
    for path in MODEL_ROOT.glob("llm_*.py"):
        if path.stem in ALLOWED_HELPER_MODULES:
            continue
        content = path.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            if token in content:
                offenders.append(f"{path.name} contient {token}")

    assert offenders == []


def test_audit_mixins_cover_models_that_share_audit_columns() -> None:
    """Verifie l alignement des modeles cibles avec les mixins d audit communs."""
    assert "created_at" in PromptAssemblyConfigModel.__table__.columns.keys()
    assert "created_at" in LlmExecutionProfileModel.__table__.columns.keys()
    assert "created_at" in LlmOutputSchemaModel.__table__.columns.keys()
    assert "created_at" in LlmReleaseSnapshotModel.__table__.columns.keys()


def test_model_structure_entries_cover_runtime_canonical_tables() -> None:
    """Garantit que la documentation executable couvre les agregats nominaux critiques."""
    indexed = {entry.table_name for entry in MODEL_STRUCTURE}
    assert "llm_assembly_configs" in indexed
    assert "llm_call_logs" in indexed
    assert "llm_call_log_operational_metadata" in indexed

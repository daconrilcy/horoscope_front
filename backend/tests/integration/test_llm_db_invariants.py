# Tests d'invariants DB LLM pour la story 70-18.
"""Valide les contraintes de release, schema de sortie et payload QA canonique."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

import pytest
from sqlalchemy import delete, inspect
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.exc import IntegrityError

from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_audit import (
    CreatedAtMixin,
    CreatedByMixin,
    CreatedUpdatedAtMixin,
    PublishedAtMixin,
)
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_observability import LlmCallLogModel
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_prompt import LlmPromptVersionModel
from app.infra.db.models.llm.llm_release import (
    LlmActiveReleaseModel,
    LlmReleaseSnapshotModel,
    ReleaseStatus,
)
from app.infra.db.models.llm.llm_sample_payload import LlmSamplePayloadModel
from tests.integration.app_db import open_app_db_session


def _index_columns(inspector: Inspector, table_name: str) -> dict[str, list[str]]:
    """Retourne les colonnes indexees pour une table inspectee."""
    return {
        str(index["name"]): list(index["column_names"])
        for index in inspector.get_indexes(table_name)
    }


def _column_lengths(inspector: Inspector, table_name: str) -> dict[str, int | None]:
    """Retourne les tailles SQL declarees pour les colonnes texte d'une table."""
    return {
        str(column["name"]): getattr(column["type"], "length", None)
        for column in inspector.get_columns(table_name)
    }


def _check_constraint_names(inspector: Inspector, table_name: str) -> set[str]:
    """Retourne les noms des contraintes CHECK presentes sur une table."""
    names = {
        str(check["name"])
        for check in inspector.get_check_constraints(table_name)
        if check.get("name")
    }
    if names or inspector.bind.dialect.name != "sqlite":
        return names

    with inspector.bind.connect() as connection:
        create_table_sql = connection.exec_driver_sql(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).scalar_one_or_none()
    if not create_table_sql:
        return names

    return {
        match.group("name")
        for match in re.finditer(
            r"CONSTRAINT\s+(?P<name>ck_[A-Za-z0-9_]+)\s+CHECK",
            create_table_sql,
            flags=re.IGNORECASE,
        )
    }


def test_output_schema_name_is_versioned_by_database_constraint() -> None:
    """Autorise plusieurs versions d'un schema mais interdit le doublon exact."""
    db = open_app_db_session()
    schema_name = f"story-70-18-schema-{uuid.uuid4().hex}"
    try:
        db.add_all(
            [
                LlmOutputSchemaModel(name=schema_name, version=1, json_schema={"type": "object"}),
                LlmOutputSchemaModel(name=schema_name, version=2, json_schema={"type": "object"}),
            ]
        )
        db.commit()

        db.add(LlmOutputSchemaModel(name=schema_name, version=2, json_schema={"type": "object"}))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    finally:
        db.execute(delete(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == schema_name))
        db.commit()
        db.close()


def test_release_snapshot_version_is_unique() -> None:
    """Empêche deux snapshots de release de partager la meme version."""
    db = open_app_db_session()
    version = f"story-70-18-release-{uuid.uuid4().hex}"
    try:
        db.add_all(
            [
                LlmReleaseSnapshotModel(
                    version=version,
                    manifest={"targets": {}},
                    status=ReleaseStatus.DRAFT,
                    created_by="test",
                ),
                LlmReleaseSnapshotModel(
                    version=version,
                    manifest={"targets": {}},
                    status=ReleaseStatus.DRAFT,
                    created_by="test",
                ),
            ]
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    finally:
        db.execute(
            delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.version == version)
        )
        db.commit()
        db.close()


def test_active_release_table_is_singleton() -> None:
    """Garantit que la table de pointeur actif ne peut contenir qu'une ligne logique."""
    db = open_app_db_session()
    snapshot_id = uuid.uuid4()
    try:
        db.execute(delete(LlmActiveReleaseModel))
        db.add(
            LlmReleaseSnapshotModel(
                id=snapshot_id,
                version=f"story-70-18-active-{uuid.uuid4().hex}",
                manifest={"targets": {}},
                status=ReleaseStatus.ACTIVE,
                created_by="test",
            )
        )
        db.flush()
        db.add(
            LlmActiveReleaseModel(
                id=1,
                release_snapshot_id=snapshot_id,
                activated_by="test",
            )
        )
        db.flush()
        db.add(
            LlmActiveReleaseModel(
                id=2,
                release_snapshot_id=snapshot_id,
                activated_by="test",
            )
        )
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()
    finally:
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.commit()
        db.close()


def test_llm_call_logs_operational_indexes_cover_story_queries() -> None:
    """Verifie les index utiles aux recherches d exploitation sur les logs LLM."""
    db = open_app_db_session()
    try:
        inspector = inspect(db.get_bind())
        indexes = _index_columns(inspector, "llm_call_logs")
        metadata_indexes = _index_columns(inspector, "llm_call_log_operational_metadata")
    finally:
        db.close()

    assert indexes["ix_llm_call_logs_timestamp"] == ["timestamp"]
    assert indexes["ix_llm_call_logs_trace_id"] == ["trace_id"]
    assert indexes["ix_llm_call_logs_scope_timestamp"] == [
        "feature",
        "subfeature",
        "plan",
        "timestamp",
    ]
    assert metadata_indexes["ix_llm_call_log_operational_metadata_snapshot"] == [
        "active_snapshot_version"
    ]
    assert metadata_indexes["ix_llm_call_log_operational_metadata_provider"] == [
        "executed_provider",
        "pipeline_kind",
    ]


def test_canonical_consumption_aggregate_uses_single_scope_and_observability_terms() -> None:
    """Verifie que l agregat garde un seul scope et les noms de tokens des logs."""
    db = open_app_db_session()
    try:
        columns = {
            column["name"]
            for column in inspect(db.get_bind()).get_columns("llm_canonical_consumption_aggregates")
        }
    finally:
        db.close()

    assert "is_legacy_residual" in columns
    assert "taxonomy_scope" not in columns
    assert {"tokens_in", "tokens_out", "cost_usd_estimated_microusd"}.issubset(columns)
    assert "input_tokens" not in columns
    assert "output_tokens" not in columns
    assert "estimated_cost_microusd" not in columns


def test_llm_finite_domains_are_database_constrained() -> None:
    """Verifie que les domaines LLM stables ne restent pas de simples String libres."""
    db = open_app_db_session()
    try:
        inspector = inspect(db.get_bind())
        execution_checks = _check_constraint_names(inspector, "llm_execution_profiles")
        assembly_checks = _check_constraint_names(inspector, "llm_assembly_configs")
        consumption_checks = _check_constraint_names(
            inspector, "llm_canonical_consumption_aggregates"
        )
        call_log_checks = _check_constraint_names(inspector, "llm_call_logs")
        call_log_metadata_checks = _check_constraint_names(
            inspector, "llm_call_log_operational_metadata"
        )
    finally:
        db.close()

    assert {
        "ck_llm_execution_profiles_reasoning_profile",
        "ck_llm_execution_profiles_verbosity_profile",
        "ck_llm_execution_profiles_output_mode",
        "ck_llm_execution_profiles_tool_mode",
    }.issubset(execution_checks)
    assert {
        "ck_llm_assembly_configs_feature_template_state",
        "ck_llm_assembly_configs_subfeature_template_state",
        "ck_llm_assembly_configs_persona_state",
        "ck_llm_assembly_configs_plan_rules_state",
    }.issubset(assembly_checks)
    assert "ck_llm_canonical_consumption_granularity" in consumption_checks
    assert {
        "ck_llm_execution_profiles_provider",
        "ck_llm_call_logs_environment",
    }.issubset(call_log_checks | execution_checks)
    assert {
        "ck_llm_call_log_operational_metadata_pipeline_kind",
        "ck_llm_call_log_operational_metadata_breaker_state",
    }.issubset(call_log_metadata_checks)


def test_llm_shared_text_fields_use_homogeneous_lengths() -> None:
    """Verifie les tailles communes des champs provider, modele, locale et scopes."""
    db = open_app_db_session()
    try:
        inspector = inspect(db.get_bind())
        execution_columns = _column_lengths(inspector, "llm_execution_profiles")
        assembly_columns = _column_lengths(inspector, "llm_assembly_configs")
        sample_payload_columns = _column_lengths(inspector, "llm_sample_payloads")
        call_log_columns = _column_lengths(inspector, "llm_call_logs")
    finally:
        db.close()

    assert execution_columns["provider"] == 32
    assert execution_columns["model"] == 100
    assert call_log_columns["model"] == 100

    assert execution_columns["feature"] == 64
    assert execution_columns["subfeature"] == 64
    assert execution_columns["plan"] == 64
    assert assembly_columns["feature"] == 64
    assert assembly_columns["subfeature"] == 64
    assert assembly_columns["plan"] == 64

    assert assembly_columns["locale"] == 32
    assert sample_payload_columns["locale"] == 32


def test_call_log_operational_metadata_is_split_from_base_log() -> None:
    """Verifie que les metadonnees operationnelles ont leur couche one-to-one."""
    db = open_app_db_session()
    try:
        inspector = inspect(db.get_bind())
        columns = {
            column["name"] for column in inspector.get_columns("llm_call_log_operational_metadata")
        }
        indexes = _index_columns(inspector, "llm_call_log_operational_metadata")
        unique_constraints = {
            constraint["name"]
            for constraint in inspector.get_unique_constraints("llm_call_log_operational_metadata")
        }
    finally:
        db.close()

    assert {
        "call_log_id",
        "pipeline_kind",
        "requested_provider",
        "resolved_provider",
        "executed_provider",
        "active_snapshot_version",
    }.issubset(columns)
    assert "uq_llm_call_log_operational_metadata_call_log" in unique_constraints
    assert indexes["ix_llm_call_log_operational_metadata_provider"] == [
        "executed_provider",
        "pipeline_kind",
    ]
    assert "ix_llm_call_log_operational_metadata_snapshot" in indexes


def test_call_log_no_longer_persists_legacy_provider_columns() -> None:
    """Verifie que le log coeur ne persiste plus aucun provider ambigu ou legacy."""
    db = open_app_db_session()
    try:
        columns = {column["name"] for column in inspect(db.get_bind()).get_columns("llm_call_logs")}
    finally:
        db.close()

    assert "provider_compat" not in columns
    assert "provider" not in columns
    assert "executed_provider" not in columns
    assert "manifest_entry_id" not in columns


def test_call_log_operational_compatibility_fields_do_not_repollute_core_table() -> None:
    """Verifie que les champs operationnels restent hors de `llm_call_logs`."""
    db = open_app_db_session()
    try:
        columns = {column["name"] for column in inspect(db.get_bind()).get_columns("llm_call_logs")}
    finally:
        db.close()

    assert {
        "pipeline_kind",
        "requested_provider",
        "resolved_provider",
        "executed_provider",
        "breaker_state",
        "breaker_scope",
        "active_snapshot_version",
        "manifest_entry_id",
    }.isdisjoint(columns)


def test_call_log_requires_canonical_provider_metadata_only() -> None:
    """Verifie que le log refuse l alias `provider=` et ecrit via les metadata canoniques."""
    with pytest.raises(TypeError, match="provider"):
        LlmCallLogModel(
            use_case="story-70-18",
            provider="openai",
            model="gpt-4o",
            latency_ms=120,
            tokens_in=10,
            tokens_out=20,
            cost_usd_estimated=0.01,
            validation_status="valid",
            request_id="req-story-70-18",
            trace_id="trace-story-70-18",
            input_hash="a" * 64,
            environment="test",
        )

    call_log = LlmCallLogModel(
        use_case="story-70-18",
        model="gpt-4o",
        latency_ms=120,
        tokens_in=10,
        tokens_out=20,
        cost_usd_estimated=0.01,
        validation_status="valid",
        request_id="req-story-70-18",
        trace_id="trace-story-70-18",
        input_hash="a" * 64,
        environment="test",
        pipeline_kind="nominal_canonical",
        requested_provider="openai",
        executed_provider="openai",
        breaker_state="closed",
        active_snapshot_version="snapshot-v1",
    )

    assert call_log.operational_metadata is not None
    assert call_log.pipeline_kind == "nominal_canonical"
    assert call_log.requested_provider == "openai"
    assert call_log.executed_provider == "openai"
    assert call_log.breaker_state == "closed"
    assert call_log.active_snapshot_version == "snapshot-v1"
    assert "pipeline_kind" not in call_log.__dict__
    assert "requested_provider" not in call_log.__dict__
    assert "executed_provider" not in call_log.__dict__
    assert "breaker_state" not in call_log.__dict__
    assert "active_snapshot_version" not in call_log.__dict__


def test_assembly_output_schema_is_backed_by_real_foreign_key() -> None:
    """Verifie que l assembly reference le schema de sortie via une vraie FK canonique."""
    db = open_app_db_session()
    try:
        inspector = inspect(db.get_bind())
        columns = {column["name"] for column in inspector.get_columns("llm_assembly_configs")}
        foreign_keys = inspector.get_foreign_keys("llm_assembly_configs")
    finally:
        db.close()

    assert "output_schema_id" in columns
    assert "output_contract_ref" not in columns
    assert any(
        fk.get("referred_table") == "llm_output_schemas"
        and fk.get("constrained_columns") == ["output_schema_id"]
        for fk in foreign_keys
    )


def test_persona_domains_are_database_constrained() -> None:
    """Verifie que tone et verbosity sont fermes aussi cote base."""
    db = open_app_db_session()
    try:
        checks = _check_constraint_names(inspect(db.get_bind()), "llm_personas")
    finally:
        db.close()

    assert {"ck_llm_personas_tone", "ck_llm_personas_verbosity"}.issubset(checks)


def test_assembly_schema_uses_explicit_component_states_instead_of_boolean_flags() -> None:
    """Verifie que le schema assembly ne porte plus les anciens booléens `*_enabled`."""
    db = open_app_db_session()
    try:
        columns = {
            column["name"] for column in inspect(db.get_bind()).get_columns("llm_assembly_configs")
        }
    finally:
        db.close()

    assert {
        "feature_template_state",
        "subfeature_template_state",
        "persona_state",
        "plan_rules_state",
    }.issubset(columns)
    assert {
        "feature_enabled",
        "subfeature_enabled",
        "persona_enabled",
        "plan_rules_enabled",
    }.isdisjoint(columns)


def test_sample_payload_model_uses_created_updated_at_mixin() -> None:
    """Verifie que les payloads QA reutilisent le mixin canonique de timestamps."""
    assert issubclass(LlmSamplePayloadModel, CreatedUpdatedAtMixin)


def test_llm_models_with_audit_columns_use_shared_mixins() -> None:
    """Verifie que les modeles LLM attendus heritent bien des mixins d audit communs."""
    assert issubclass(LlmSamplePayloadModel, CreatedUpdatedAtMixin)
    assert issubclass(PromptAssemblyConfigModel, CreatedAtMixin)
    assert issubclass(PromptAssemblyConfigModel, CreatedByMixin)
    assert issubclass(PromptAssemblyConfigModel, PublishedAtMixin)
    assert issubclass(LlmExecutionProfileModel, CreatedAtMixin)
    assert issubclass(LlmExecutionProfileModel, CreatedByMixin)
    assert issubclass(LlmExecutionProfileModel, PublishedAtMixin)
    assert issubclass(LlmPromptVersionModel, CreatedAtMixin)
    assert issubclass(LlmPromptVersionModel, CreatedByMixin)
    assert issubclass(LlmPromptVersionModel, PublishedAtMixin)
    assert issubclass(LlmReleaseSnapshotModel, CreatedAtMixin)
    assert issubclass(LlmReleaseSnapshotModel, CreatedByMixin)


def test_llm_models_do_not_redeclare_local_audit_columns_or_time_defaults() -> None:
    """Bloque la reintroduction de colonnes d audit locales dans `models.llm`."""
    llm_models_root = (
        Path(__file__).resolve().parents[2] / "app" / "infra" / "db" / "models" / "llm"
    )
    forbidden_fragments = (
        "created_at: Mapped",
        "updated_at: Mapped",
        "created_by: Mapped",
        "published_at: Mapped",
    )

    offenders: list[str] = []
    for path in llm_models_root.glob("*.py"):
        if path.name == "llm_audit.py":
            continue
        content = path.read_text(encoding="utf-8")
        for fragment in forbidden_fragments:
            if fragment in content:
                offenders.append(f"{path.name}:{fragment}")

    assert offenders == []

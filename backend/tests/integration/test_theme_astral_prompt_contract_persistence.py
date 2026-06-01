"""Tests d'integration de persistance du contrat prompt theme astral."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.domain.llm.configuration.theme_astral_contracts import (
    THEME_ASTRAL_DELIVERY_PROFILES,
    THEME_ASTRAL_FEATURE,
    THEME_ASTRAL_INPUT_CONTRACT_ID,
    THEME_ASTRAL_INPUT_SCHEMA,
    THEME_ASTRAL_OUTPUT_SCHEMA_NAME,
    THEME_ASTRAL_PERSONA_CODE,
    THEME_ASTRAL_PROMPT_CONTRACT_ID,
    THEME_ASTRAL_RESPONSE_CONTRACT_ID,
    THEME_ASTRAL_SUBFEATURE,
    THEME_ASTRAL_USE_CASE_KEY,
    resolve_active_theme_astral_prompt_contract,
)
from app.infra.db.models.llm.llm_assembly import (
    AssemblyComponentResolutionState,
    PromptAssemblyConfigModel,
)
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.ops.llm.bootstrap.seed_theme_astral_prompt_contract import (
    seed_theme_astral_prompt_contract,
)
from tests.integration.app_db import open_app_db_session


def _published_count(db, model, *criteria) -> int:
    """Compte les lignes publiees qui matchent un scope de contrat."""
    return len(
        db.execute(select(model).where(model.status == PromptStatus.PUBLISHED, *criteria))
        .scalars()
        .all()
    )


def test_theme_astral_seed_persists_stable_contract_family() -> None:
    """Le seed persiste les identifiants stables dans les owners LLM existants."""
    db = open_app_db_session()
    try:
        seed_theme_astral_prompt_contract(db)

        use_case = db.get(LlmUseCaseConfigModel, THEME_ASTRAL_USE_CASE_KEY)
        schema = db.execute(
            select(LlmOutputSchemaModel).where(
                LlmOutputSchemaModel.name == THEME_ASTRAL_OUTPUT_SCHEMA_NAME,
                LlmOutputSchemaModel.version == 1,
            )
        ).scalar_one()
        prompt = db.execute(
            select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.use_case_key == THEME_ASTRAL_USE_CASE_KEY,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
        ).scalar_one()
        persona = db.execute(
            select(LlmPersonaModel).where(LlmPersonaModel.code == THEME_ASTRAL_PERSONA_CODE)
        ).scalar_one()

        assert use_case is not None
        assert THEME_ASTRAL_INPUT_CONTRACT_ID in use_case.required_prompt_placeholders
        assert schema.json_schema["$id"] == THEME_ASTRAL_RESPONSE_CONTRACT_ID
        assert THEME_ASTRAL_PROMPT_CONTRACT_ID in prompt.developer_prompt
        assert THEME_ASTRAL_INPUT_CONTRACT_ID in prompt.developer_prompt
        assert "free" not in prompt.developer_prompt.lower()
        assert "premium" not in prompt.developer_prompt.lower()
        assert "basic_natal_prompt_payload" in prompt.developer_prompt
        assert "verite astrologique" in persona.disallowed_topics
    finally:
        db.close()


def test_theme_astral_input_schema_declares_birth_context_shape() -> None:
    """Le schema versionne expose les champs de naissance visibles provider."""
    input_properties = THEME_ASTRAL_INPUT_SCHEMA["properties"][THEME_ASTRAL_INPUT_CONTRACT_ID][
        "properties"
    ]
    birth_context = input_properties["input_data"]["properties"]["birth_context"]

    assert birth_context["required"] == [
        "chart_id",
        "birth_date",
        "birth_time_local",
        "birth_place",
        "precision",
        "locale",
        "chart_type",
    ]
    assert set(birth_context["properties"]["birth_place"]["properties"]) == {
        "city",
        "country",
        "timezone",
        "latitude",
        "longitude",
    }
    assert set(birth_context["properties"]["precision"]["properties"]) == {
        "birth_time_known",
        "coordinates_known",
    }


def test_active_read_returns_canonical_family_without_plan_leakage() -> None:
    """La lecture active retourne le contrat canonique par profondeur non commerciale."""
    db = open_app_db_session()
    try:
        seed_theme_astral_prompt_contract(db)

        for depth in ("essential", "expanded", "complete"):
            family = resolve_active_theme_astral_prompt_contract(db, depth=depth)
            dumped = family.model_dump()

            assert family.prompt_contract_id == THEME_ASTRAL_PROMPT_CONTRACT_ID
            assert family.input_contract_id == THEME_ASTRAL_INPUT_CONTRACT_ID
            assert family.response_contract_id == THEME_ASTRAL_RESPONSE_CONTRACT_ID
            assert family.delivery_profile["depth"] == depth
            assert family.output_schema_ref.id == THEME_ASTRAL_RESPONSE_CONTRACT_ID
            assert family.astrologer_voice["code"] == THEME_ASTRAL_PERSONA_CODE
            assert "free" not in repr(dumped).lower()
            assert "basic" not in repr(dumped).lower()
            assert "premium" not in repr(dumped).lower()
    finally:
        db.close()


def test_theme_astral_seed_is_idempotent_for_active_rows() -> None:
    """Deux executions du seed ne créent pas de doublons actifs."""
    db = open_app_db_session()
    try:
        seed_theme_astral_prompt_contract(db)
        first_counts = {
            "prompts": _published_count(
                db,
                LlmPromptVersionModel,
                LlmPromptVersionModel.use_case_key == THEME_ASTRAL_USE_CASE_KEY,
            ),
            "profiles": _published_count(
                db,
                LlmExecutionProfileModel,
                LlmExecutionProfileModel.feature == THEME_ASTRAL_FEATURE,
                LlmExecutionProfileModel.subfeature == THEME_ASTRAL_SUBFEATURE,
            ),
            "assemblies": _published_count(
                db,
                PromptAssemblyConfigModel,
                PromptAssemblyConfigModel.feature == THEME_ASTRAL_FEATURE,
                PromptAssemblyConfigModel.subfeature == THEME_ASTRAL_SUBFEATURE,
            ),
        }

        seed_theme_astral_prompt_contract(db)
        second_counts = {
            "prompts": _published_count(
                db,
                LlmPromptVersionModel,
                LlmPromptVersionModel.use_case_key == THEME_ASTRAL_USE_CASE_KEY,
            ),
            "profiles": _published_count(
                db,
                LlmExecutionProfileModel,
                LlmExecutionProfileModel.feature == THEME_ASTRAL_FEATURE,
                LlmExecutionProfileModel.subfeature == THEME_ASTRAL_SUBFEATURE,
            ),
            "assemblies": _published_count(
                db,
                PromptAssemblyConfigModel,
                PromptAssemblyConfigModel.feature == THEME_ASTRAL_FEATURE,
                PromptAssemblyConfigModel.subfeature == THEME_ASTRAL_SUBFEATURE,
            ),
        }

        assert first_counts == second_counts == {"prompts": 1, "profiles": 1, "assemblies": 3}
        assert set(THEME_ASTRAL_DELIVERY_PROFILES) == {"essential", "expanded", "complete"}
    finally:
        db.close()


def test_theme_astral_seed_archives_stale_deep_assembly() -> None:
    """Le seed retire `deep` des assemblies actives sans mapping de compatibilite."""
    db = open_app_db_session()
    try:
        seed_theme_astral_prompt_contract(db)
        canonical = db.execute(
            select(PromptAssemblyConfigModel).where(
                PromptAssemblyConfigModel.feature == THEME_ASTRAL_FEATURE,
                PromptAssemblyConfigModel.subfeature == THEME_ASTRAL_SUBFEATURE,
                PromptAssemblyConfigModel.plan == "essential",
                PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
            )
        ).scalar_one()
        stale = PromptAssemblyConfigModel(
            feature=THEME_ASTRAL_FEATURE,
            subfeature=THEME_ASTRAL_SUBFEATURE,
            plan="deep",
            locale="fr-FR",
            feature_template_ref=canonical.feature_template_ref,
            persona_ref=canonical.persona_ref,
            execution_profile_ref=canonical.execution_profile_ref,
            output_schema_id=canonical.output_schema_id,
            plan_rules_ref="theme_astral_delivery_profile_v1",
            length_budget={"target": "legacy", "max_output_tokens": 3200},
            plan_rules_state=AssemblyComponentResolutionState.ENABLED.value,
            persona_state=AssemblyComponentResolutionState.ENABLED.value,
            status=PromptStatus.PUBLISHED,
            created_by="test",
        )
        db.add(stale)
        db.commit()

        seed_theme_astral_prompt_contract(db)

        active_plans = {
            assembly.plan
            for assembly in db.execute(
                select(PromptAssemblyConfigModel).where(
                    PromptAssemblyConfigModel.feature == THEME_ASTRAL_FEATURE,
                    PromptAssemblyConfigModel.subfeature == THEME_ASTRAL_SUBFEATURE,
                    PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
                )
            )
            .scalars()
            .all()
        }
        db.refresh(stale)
        assert active_plans == {"essential", "expanded", "complete"}
        assert stale.status == PromptStatus.ARCHIVED
    finally:
        db.close()


def test_invalid_theme_astral_version_combinations_fail_deterministically() -> None:
    """Les profondeurs ou schemas incompatibles échouent explicitement."""
    db = open_app_db_session()
    try:
        seed_theme_astral_prompt_contract(db)

        with pytest.raises(ValueError, match="Unknown theme_astral delivery depth"):
            resolve_active_theme_astral_prompt_contract(db, depth="deep")
        with pytest.raises(ValueError, match="Unknown theme_astral delivery depth"):
            resolve_active_theme_astral_prompt_contract(db, depth="premium")

        assembly = db.execute(
            select(PromptAssemblyConfigModel).where(
                PromptAssemblyConfigModel.feature == THEME_ASTRAL_FEATURE,
                PromptAssemblyConfigModel.subfeature == THEME_ASTRAL_SUBFEATURE,
                PromptAssemblyConfigModel.plan == "essential",
                PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
            )
        ).scalar_one()
        original_schema_id = assembly.output_schema_id
        bad_schema = LlmOutputSchemaModel(
            name="theme_astral_response_contract_v2",
            version=2,
            json_schema={"type": "object"},
        )
        db.add(bad_schema)
        db.flush()
        assembly.output_schema_id = bad_schema.id
        db.flush()

        with pytest.raises(ValueError, match="incompatible output schema"):
            resolve_active_theme_astral_prompt_contract(db, depth="essential")

        assembly.output_schema_id = original_schema_id
        db.delete(bad_schema)
        db.commit()
    finally:
        db.close()

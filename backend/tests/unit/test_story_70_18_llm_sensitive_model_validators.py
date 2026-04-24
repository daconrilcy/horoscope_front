# Tests des validateurs metier LLM ajoutes par la story 70-18.
"""Verifie les garde-fous locaux sur les colonnes sensibles des modeles LLM."""

from __future__ import annotations

import pytest

from app.infra.db.models.llm.llm_assembly import (
    AssemblyComponentResolutionState,
    PromptAssemblyConfigModel,
)
from app.infra.db.models.llm.llm_audit import CreatedAtMixin, CreatedByMixin, PublishedAtMixin
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm.llm_release import LlmActiveReleaseModel, LlmReleaseSnapshotModel


def test_published_unique_index_helper_keeps_known_index_names() -> None:
    """Verifie la convention commune des index partiels published par scope."""
    prompt_indexes = {index.name for index in LlmPromptVersionModel.__table__.indexes}
    assembly_indexes = {index.name for index in PromptAssemblyConfigModel.__table__.indexes}
    profile_indexes = {index.name for index in LlmExecutionProfileModel.__table__.indexes}

    assert "ix_llm_prompt_version_active_unique" in prompt_indexes
    assert "ix_llm_assembly_config_active_unique" in assembly_indexes
    assert "ix_llm_execution_profile_active_unique" in profile_indexes


def test_assembly_exposes_execution_profile_relationship() -> None:
    """Documente la navigation ORM directe depuis une assembly vers son profil."""
    relationship_names = set(PromptAssemblyConfigModel.__mapper__.relationships.keys())

    assert "execution_profile" in relationship_names
    assert "output_schema" in relationship_names


def test_llm_orm_relationships_cover_canonical_graph() -> None:
    """Documente les relations ORM ajoutees pour eviter les lookups manuels."""
    assembly_relationships = set(PromptAssemblyConfigModel.__mapper__.relationships.keys())
    release_relationships = set(LlmReleaseSnapshotModel.__mapper__.relationships.keys())
    active_relationships = set(LlmActiveReleaseModel.__mapper__.relationships.keys())
    prompt_relationships = set(LlmPromptVersionModel.__mapper__.relationships.keys())

    assert {"execution_profile", "output_schema"}.issubset(assembly_relationships)
    assert "active_release" in release_relationships
    assert "release_snapshot" in active_relationships
    assert "use_case" in prompt_relationships


def test_llm_models_reuse_audit_mixins() -> None:
    """Verifie la factorisation des colonnes d audit communes."""
    assert issubclass(PromptAssemblyConfigModel, CreatedByMixin)
    assert issubclass(PromptAssemblyConfigModel, CreatedAtMixin)
    assert issubclass(PromptAssemblyConfigModel, PublishedAtMixin)


def test_assembly_marks_legacy_runtime_compatibility_fields() -> None:
    """Verifie que les anciens champs runtime assembly n existent plus sur le modele."""
    for legacy_name in (
        "execution_config",
        "interaction_mode",
        "user_question_policy",
        "input_schema",
        "output_contract_ref",
        "fallback_use_case",
    ):
        assert not hasattr(PromptAssemblyConfigModel, legacy_name)


def test_prompt_models_mark_legacy_and_canonical_boundaries() -> None:
    """Documente la frontiere entre use_case legacy et scope canonique."""
    assert LlmUseCaseConfigModel.legacy_identity_field == "key"
    assert LlmUseCaseConfigModel.canonical_scope_fields == {
        "feature",
        "subfeature",
        "plan",
        "locale",
    }
    assert LlmUseCaseConfigModel.runtime_surface == "historical_admin_only"
    assert LlmPromptVersionModel.legacy_use_case_link_field == "use_case_key"
    assert LlmPromptVersionModel.canonical_text_fields == {"developer_prompt"}


def test_assembly_component_states_make_optional_resolution_explicit() -> None:
    """Distingue absence, heritage, activation et desactivation volontaire."""
    assembly = PromptAssemblyConfigModel(
        created_by="test",
        feature_template_ref=None,
        subfeature="interpretation",
        subfeature_template_ref=None,
        persona_ref=None,
        plan="premium",
        plan_rules_ref="premium-rules",
        persona_state=AssemblyComponentResolutionState.DISABLED.value,
    )

    states = assembly.component_resolution_states()

    assert states["feature_template"] == AssemblyComponentResolutionState.ABSENT
    assert states["subfeature_template"] == AssemblyComponentResolutionState.INHERITED
    assert states["persona"] == AssemblyComponentResolutionState.DISABLED
    assert states["plan_rules"] == AssemblyComponentResolutionState.ENABLED


def test_execution_profile_rejects_empty_model() -> None:
    """Empêche un profil d execution sans identifiant de modele."""
    with pytest.raises(ValueError, match="model must not be empty"):
        LlmExecutionProfileModel(model=" ", created_by="test")


def test_execution_profile_rejects_non_positive_timeout() -> None:
    """Empêche un timeout nul ou negatif dans les profils runtime."""
    with pytest.raises(ValueError, match="timeout_seconds must be positive"):
        LlmExecutionProfileModel(model="gpt-5", timeout_seconds=0, created_by="test")


def test_execution_profile_rejects_non_positive_max_output_tokens() -> None:
    """Empêche une limite de sortie optionnelle non exploitable."""
    with pytest.raises(ValueError, match="max_output_tokens must be positive"):
        LlmExecutionProfileModel(model="gpt-5", max_output_tokens=-1, created_by="test")


def test_assembly_rejects_empty_optional_references() -> None:
    """Empêche les references optionnelles vides sur les assemblies."""
    with pytest.raises(ValueError, match="plan_rules_ref must not be empty"):
        PromptAssemblyConfigModel(plan_rules_ref="", created_by="test")


def test_persona_rejects_invalid_json_string_lists() -> None:
    """Empêche les listes JSON persona de contenir autre chose que du texte."""
    with pytest.raises(ValueError, match="style_markers must be a list of strings"):
        LlmPersonaModel(name="test", style_markers="warm")

    with pytest.raises(ValueError, match="boundaries must contain only non-empty strings"):
        LlmPersonaModel(name="test", boundaries=["clair", " "])


def test_persona_rejects_invalid_formatting_contract() -> None:
    """Empêche les options formatting de sortir du contrat booléen attendu."""
    with pytest.raises(ValueError, match="formatting must be an object"):
        LlmPersonaModel(name="test", formatting=["sections"])

    with pytest.raises(ValueError, match="formatting.emojis must be a boolean"):
        LlmPersonaModel(name="test", formatting={"emojis": "no"})

    persona = LlmPersonaModel(name="test", formatting={"sections": False})
    assert persona.formatting == {"sections": False, "bullets": False, "emojis": False}

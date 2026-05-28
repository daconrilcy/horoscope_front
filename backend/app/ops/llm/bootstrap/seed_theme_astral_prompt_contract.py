"""Seed idempotent des contrats LLM versionnes pour le prompt theme astral."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.llm.configuration.theme_astral_contracts import (
    THEME_ASTRAL_DELIVERY_PROFILES,
    THEME_ASTRAL_EXECUTION_PROFILE_NAME,
    THEME_ASTRAL_FEATURE,
    THEME_ASTRAL_OUTPUT_SCHEMA_NAME,
    THEME_ASTRAL_PERSONA_CODE,
    THEME_ASTRAL_PROMPT_CONTRACT_ID,
    THEME_ASTRAL_RESPONSE_SCHEMA,
    THEME_ASTRAL_SUBFEATURE,
    THEME_ASTRAL_USE_CASE_KEY,
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

logger = logging.getLogger(__name__)

THEME_ASTRAL_PROMPT_TEMPLATE = """
Contrat de prompt: theme_astral_prompt_v1.
Langue: {{locale}}. Persona: {{persona_name}}.
Entree contractuelle: {{theme_astral_llm_input_v1}}.
Respecte runtime_contract, safety_contract, astrologer_voice, feature_context,
delivery_profile, input_data et output_contract. N'expose jamais le nom du plan
commercial; utilise uniquement les valeurs non commerciales de delivery_profile.
""".strip()


def _published_now(db: Session):
    """Retourne l'horodatage SQL de publication pour les seeds systeme."""
    from sqlalchemy import func

    return db.execute(select(func.now())).scalar()


def _ensure_use_case(db: Session) -> LlmUseCaseConfigModel:
    """Crée ou met a jour le use case canonique theme_astral."""
    use_case = db.get(LlmUseCaseConfigModel, THEME_ASTRAL_USE_CASE_KEY)
    required = ["theme_astral_llm_input_v1", "persona_name"]
    if use_case is None:
        use_case = LlmUseCaseConfigModel(
            key=THEME_ASTRAL_USE_CASE_KEY,
            display_name="Contrat Prompt Theme Astral",
            description="Contrat versionne de construction du prompt theme astral.",
            required_prompt_placeholders=required,
            eval_failure_threshold=0.20,
        )
        db.add(use_case)
    else:
        use_case.display_name = "Contrat Prompt Theme Astral"
        use_case.description = "Contrat versionne de construction du prompt theme astral."
        use_case.required_prompt_placeholders = required
    db.flush()
    return use_case


def _ensure_output_schema(db: Session) -> LlmOutputSchemaModel:
    """Persiste le contrat de sortie theme_astral_response_contract_v1."""
    schema = db.execute(
        select(LlmOutputSchemaModel).where(
            LlmOutputSchemaModel.name == THEME_ASTRAL_OUTPUT_SCHEMA_NAME,
            LlmOutputSchemaModel.version == 1,
        )
    ).scalar_one_or_none()
    if schema is None:
        schema = LlmOutputSchemaModel(
            name=THEME_ASTRAL_OUTPUT_SCHEMA_NAME,
            version=1,
            json_schema=THEME_ASTRAL_RESPONSE_SCHEMA,
        )
        db.add(schema)
    else:
        schema.json_schema = THEME_ASTRAL_RESPONSE_SCHEMA
    db.flush()
    return schema


def _ensure_prompt_version(db: Session) -> LlmPromptVersionModel:
    """Publie le prompt versionne sans créer de doublon actif."""
    prompts = list(
        db.execute(
            select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.use_case_key == THEME_ASTRAL_USE_CASE_KEY,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
        )
        .scalars()
        .all()
    )
    prompt = prompts[0] if prompts else None
    for duplicate in prompts[1:]:
        duplicate.status = PromptStatus.ARCHIVED
    if prompt is None:
        prompt = LlmPromptVersionModel(
            use_case_key=THEME_ASTRAL_USE_CASE_KEY,
            status=PromptStatus.PUBLISHED,
            developer_prompt=THEME_ASTRAL_PROMPT_TEMPLATE,
            created_by="system",
            published_at=_published_now(db),
        )
        db.add(prompt)
    else:
        prompt.developer_prompt = THEME_ASTRAL_PROMPT_TEMPLATE
    db.flush()
    return prompt


def _ensure_persona(db: Session) -> LlmPersonaModel:
    """Lie la voix astrologue a un persona de style, sans verite astrologique."""
    persona = db.execute(
        select(LlmPersonaModel).where(LlmPersonaModel.code == THEME_ASTRAL_PERSONA_CODE)
    ).scalar_one_or_none()
    if persona is None:
        persona = LlmPersonaModel(
            code=THEME_ASTRAL_PERSONA_CODE,
            name="Astrologue Theme Astral",
            description="Voix de style pour les prompts theme astral, sans faits astrologiques.",
            tone="warm",
            verbosity="medium",
            style_markers=["clair", "symbolique", "non fataliste"],
            boundaries=[
                "Ne modifie jamais les faits astrologiques.",
                "Ne deduit aucun plan commercial depuis le profil de livraison.",
            ],
            allowed_topics=["style", "ton", "vocabulaire", "emphases"],
            disallowed_topics=["verite astrologique", "calculs", "plan commercial"],
            formatting={"sections": True, "bullets": False, "emojis": False},
            enabled=True,
        )
        db.add(persona)
    else:
        persona.enabled = True
        persona.description = (
            "Voix de style pour les prompts theme astral, sans faits astrologiques."
        )
        persona.boundaries = [
            "Ne modifie jamais les faits astrologiques.",
            "Ne deduit aucun plan commercial depuis le profil de livraison.",
        ]
        persona.disallowed_topics = ["verite astrologique", "calculs", "plan commercial"]
    db.flush()
    return persona


def _ensure_execution_profile(db: Session) -> LlmExecutionProfileModel:
    """Publie un profil d'execution backend-only pour theme_astral."""
    profiles = list(
        db.execute(
            select(LlmExecutionProfileModel).where(
                LlmExecutionProfileModel.feature == THEME_ASTRAL_FEATURE,
                LlmExecutionProfileModel.subfeature == THEME_ASTRAL_SUBFEATURE,
                LlmExecutionProfileModel.status == PromptStatus.PUBLISHED,
            )
        )
        .scalars()
        .all()
    )
    profile = profiles[0] if profiles else None
    for duplicate in profiles[1:]:
        duplicate.status = PromptStatus.ARCHIVED
    if profile is None:
        profile = LlmExecutionProfileModel(
            name=THEME_ASTRAL_EXECUTION_PROFILE_NAME,
            feature=THEME_ASTRAL_FEATURE,
            subfeature=THEME_ASTRAL_SUBFEATURE,
            provider="openai",
            model="gpt-4o",
            reasoning_profile="medium",
            verbosity_profile="balanced",
            output_mode="structured_json",
            max_output_tokens=3200,
            status=PromptStatus.PUBLISHED,
            created_by="system",
            published_at=_published_now(db),
        )
        db.add(profile)
    else:
        profile.name = THEME_ASTRAL_EXECUTION_PROFILE_NAME
        profile.provider = "openai"
        profile.model = "gpt-4o"
        profile.output_mode = "structured_json"
        profile.max_output_tokens = 3200
    db.flush()
    return profile


def seed_theme_astral_prompt_contract(db: Session) -> None:
    """Seed les contrats theme_astral via les tables LLM existantes."""
    _ensure_use_case(db)
    output_schema = _ensure_output_schema(db)
    prompt = _ensure_prompt_version(db)
    persona = _ensure_persona(db)
    profile = _ensure_execution_profile(db)

    for depth, delivery_profile in THEME_ASTRAL_DELIVERY_PROFILES.items():
        assemblies = list(
            db.execute(
                select(PromptAssemblyConfigModel).where(
                    PromptAssemblyConfigModel.feature == THEME_ASTRAL_FEATURE,
                    PromptAssemblyConfigModel.subfeature == THEME_ASTRAL_SUBFEATURE,
                    PromptAssemblyConfigModel.plan == depth,
                    PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
                )
            )
            .scalars()
            .all()
        )
        assembly = assemblies[0] if assemblies else None
        for duplicate in assemblies[1:]:
            duplicate.status = PromptStatus.ARCHIVED
        if assembly is None:
            assembly = PromptAssemblyConfigModel(
                feature=THEME_ASTRAL_FEATURE,
                subfeature=THEME_ASTRAL_SUBFEATURE,
                plan=depth,
                locale="fr-FR",
                feature_template_ref=prompt.id,
                persona_ref=persona.id,
                execution_profile_ref=profile.id,
                output_schema_id=output_schema.id,
                plan_rules_ref=delivery_profile["delivery_profile_id"],
                length_budget=delivery_profile["output_length_policy"],
                plan_rules_state=AssemblyComponentResolutionState.ENABLED.value,
                persona_state=AssemblyComponentResolutionState.ENABLED.value,
                status=PromptStatus.PUBLISHED,
                created_by="system",
                published_at=_published_now(db),
            )
            db.add(assembly)
        else:
            assembly.feature_template_ref = prompt.id
            assembly.persona_ref = persona.id
            assembly.execution_profile_ref = profile.id
            assembly.output_schema_id = output_schema.id
            assembly.plan_rules_ref = delivery_profile["delivery_profile_id"]
            assembly.length_budget = delivery_profile["output_length_policy"]
            assembly.plan_rules_state = AssemblyComponentResolutionState.ENABLED.value
            assembly.persona_state = AssemblyComponentResolutionState.ENABLED.value
    db.commit()
    logger.info("seed_theme_astral_prompt_contract: seeded %s", THEME_ASTRAL_PROMPT_CONTRACT_ID)


__all__ = ["seed_theme_astral_prompt_contract"]

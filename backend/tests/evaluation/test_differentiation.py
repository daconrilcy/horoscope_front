import uuid

import pytest

from app.domain.llm.configuration.assembly_registry import AssemblyRegistry
from app.domain.llm.runtime.contracts import ExecutionUserInput, LLMExecutionRequest
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.models.llm.llm_assembly import (
    AssemblyComponentResolutionState,
    PromptAssemblyConfigModel,
)
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)


@pytest.mark.evaluation
@pytest.mark.asyncio
async def test_plan_differentiation(db):
    """Checks that premium plan produces a different (longer/richer) prompt than free."""
    # 1. Setup
    feat = "natal"
    uc_key = "natal_test"
    uc = LlmUseCaseConfigModel(
        key=uc_key, display_name=uc_key, description="test", safety_profile="astrology"
    )
    db.add(uc)
    v = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key=uc_key,
        developer_prompt="BASE",
        model="gpt-4o",
        status=PromptStatus.PUBLISHED,
        created_by="eval",
    )
    db.add(v)
    db.commit()

    # Create assemblies for free and premium
    for plan in ["free", "premium"]:
        profile = LlmExecutionProfileModel(
            id=uuid.uuid4(),
            name=f"profile-{plan}",
            provider="openai",
            model="gpt-4o",
            reasoning_profile="off",
            verbosity_profile="balanced",
            output_mode="structured_json",
            tool_mode="none",
            feature=feat,
            subfeature="interpretation",
            plan=plan,
            status=PromptStatus.PUBLISHED,
            created_by="eval",
        )
        db.add(profile)
        db.flush()
        config = PromptAssemblyConfigModel(
            id=uuid.uuid4(),
            feature=feat,
            subfeature="interpretation",
            plan=plan,
            locale="fr-FR",
            feature_template_ref=v.id,
            execution_profile_ref=profile.id,
            plan_rules_ref="plan_free_concise" if plan == "free" else "plan_premium_full",
            plan_rules_state=AssemblyComponentResolutionState.ENABLED,
            execution_config={"model": "gpt-4o", "max_output_tokens": 2000},
            status=PromptStatus.PUBLISHED,
            created_by="eval",
        )
        db.add(config)
    db.commit()

    gateway = LLMGateway()

    # 2. Resolve both
    req_free = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case=uc_key, feature=feat, subfeature="interpretation", plan="free"
        ),
        request_id="r1",
        trace_id="t1",
    )
    plan_free, _ = await gateway._resolve_plan(req_free, db)

    req_prem = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case=uc_key, feature=feat, subfeature="interpretation", plan="premium"
        ),
        request_id="r2",
        trace_id="t2",
    )
    plan_prem, _ = await gateway._resolve_plan(req_prem, db)

    # 3. Assertions
    assert plan_free.rendered_developer_prompt != plan_prem.rendered_developer_prompt
    assert "CONSIGNE ABONNEMENT PREMIUM" in plan_prem.rendered_developer_prompt
    assert "CONSIGNE ABONNEMENT FREE" in plan_free.rendered_developer_prompt


@pytest.mark.evaluation
@pytest.mark.asyncio
async def test_persona_differentiation(db, mock_personas):
    """Checks persona differentiation through the assembly path, not only via runtime override."""
    feat = "chat_persona_eval"
    uc_key = "chat_test"
    uc = LlmUseCaseConfigModel(
        key=uc_key, display_name=uc_key, description="test", safety_profile="astrology"
    )
    db.add(uc)
    v = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key=uc_key,
        developer_prompt="BASE",
        model="gpt-4o",
        status=PromptStatus.PUBLISHED,
        created_by="eval",
    )
    db.add(v)
    db.commit()

    # Create personas
    p_ids = {}
    for p_type, p_data in mock_personas.items():
        persona = LlmPersonaModel(
            id=uuid.uuid4(),
            name=p_data["name"],
            description="test",
            tone="direct" if p_type == "synthetique" else "mystical",
            verbosity="short" if p_type == "synthetique" else "long",
            style_markers=p_data["style_markers"],
            boundaries=p_data["boundaries"],
            allowed_topics=[],
            disallowed_topics=[],
            formatting={"sections": True, "bullets": False, "emojis": False},
            enabled=True,
        )
        db.add(persona)
        p_ids[p_type] = persona.id
    db.commit()

    assembly = PromptAssemblyConfigModel(
        id=uuid.uuid4(),
        feature=feat,
        plan="free",
        locale="fr-FR",
        feature_template_ref=v.id,
        persona_ref=p_ids["synthetique"],
        persona_state=AssemblyComponentResolutionState.ENABLED,
        execution_config={"model": "gpt-4o", "max_output_tokens": 1200},
        status=PromptStatus.PUBLISHED,
        created_by="eval",
    )
    db.add(assembly)
    db.commit()

    gateway = LLMGateway()
    registry = AssemblyRegistry(db)
    registry.invalidate_cache()

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case=uc_key, feature=feat, plan="free"),
        request_id="r-synthetique",
        trace_id="t",
    )
    plan_synth, _ = await gateway._resolve_plan(request, db)

    assembly.persona_ref = p_ids["ample"]
    db.commit()
    registry.invalidate_cache()

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case=uc_key, feature=feat, plan="free"),
        request_id="r-ample",
        trace_id="t",
    )
    plan_ample, _ = await gateway._resolve_plan(request, db)

    results = [plan_synth.persona_block, plan_ample.persona_block]

    assert results[0] != results[1]
    assert mock_personas["synthetique"]["name"] in results[0]
    assert mock_personas["ample"]["name"] in results[1]

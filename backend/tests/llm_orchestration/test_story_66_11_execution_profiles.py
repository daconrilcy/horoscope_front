import uuid

import pytest

from app.domain.llm.configuration.execution_profile_registry import ExecutionProfileRegistry
from app.domain.llm.runtime.contracts import ExecutionUserInput, LLMExecutionRequest
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_prompt import PromptStatus


@pytest.mark.asyncio
async def test_execution_profile_waterfall_resolution(db):
    """Test Story 66.11: Waterfall resolution of execution profiles."""
    # 1. Setup profiles
    # Generic feature profile
    p_feat = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="Feature Profile",
        feature="test_feat",
        model="gpt-4o-feat",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    # Specific feature+plan profile
    p_plan = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="Plan Profile",
        feature="test_feat",
        plan="premium",
        model="gpt-4o-premium",
        reasoning_profile="medium",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db.add_all([p_feat, p_plan])
    db.commit()

    ExecutionProfileRegistry.invalidate_cache()

    gateway = LLMGateway()

    # Test match premium plan
    req_prem = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat", feature="test_feat", plan="premium"),
        request_id="req1",
        trace_id="tr1",
    )
    plan_prem, _ = await gateway._resolve_plan(req_prem, db)
    assert plan_prem.execution_profile_id == str(p_plan.id)
    assert plan_prem.model_id == "gpt-4o-premium"
    assert plan_prem.execution_profile_source == "waterfall"
    assert plan_prem.translated_provider_params.get("reasoning_effort") == "medium"

    # Test fallback to feature (plan free not defined)
    req_free = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat", feature="test_feat", plan="free"),
        request_id="req2",
        trace_id="tr2",
    )
    plan_free, _ = await gateway._resolve_plan(req_free, db)
    assert plan_free.execution_profile_id == str(p_feat.id)
    assert plan_free.model_id == "gpt-4o-feat"


@pytest.mark.asyncio
async def test_execution_profile_assembly_ref(db):
    """Test Story 66.11: Assembly explicit reference to execution profile."""
    from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
    from app.infra.db.models.llm.llm_prompt import LlmPromptVersionModel, LlmUseCaseConfigModel

    # 1. Setup Profile
    profile = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="Explicit Profile",
        feature="none",  # Won't match waterfall
        model="o1-preview",
        reasoning_profile="deep",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db.add(profile)

    # 2. Setup Assembly with ref
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="feat_uc",
        developer_prompt="PROMPT",
        status=PromptStatus.PUBLISHED,
        model="gpt-4o",
        created_by="test",
    )
    db.add(fv)
    uc = LlmUseCaseConfigModel(
        key="feat_uc", display_name="UC", description="test", safety_profile="astrology"
    )
    db.add(uc)

    assembly = PromptAssemblyConfigModel(
        feature="feat_ref",
        plan="free",
        locale="fr-FR",
        feature_template_ref=fv.id,
        execution_profile_ref=profile.id,  # Explicit ref
        execution_config={"model": "gpt-4o-ignored", "max_output_tokens": 1000},
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db.add(assembly)
    db.commit()

    ExecutionProfileRegistry.invalidate_cache()

    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="test_ref", feature="feat_ref", plan="free"),
        request_id="req3",
        trace_id="tr3",
    )

    plan, _ = await gateway._resolve_plan(request, db)

    # Explicit profile ref wins
    assert plan.execution_profile_id == str(profile.id)
    assert plan.model_id == "o1-preview"
    assert plan.execution_profile_source == "assembly_ref"
    assert plan.translated_provider_params.get("reasoning_effort") == "high"  # deep -> high

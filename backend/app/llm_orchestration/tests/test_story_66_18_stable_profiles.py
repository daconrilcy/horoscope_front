import uuid

import pytest

from app.infra.db.models import LlmUseCaseConfigModel
from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import ExecutionUserInput, LLMExecutionRequest
from app.llm_orchestration.services.execution_profile_registry import ExecutionProfileRegistry


@pytest.mark.asyncio
async def test_verbosity_profile_injection(db):
    """Test Story 66.18: Verbosity instruction injection and default tokens."""
    # 1. Setup profile with verbosity 'concise'
    profile = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="Concise Profile",
        feature="test_verb",
        model="gpt-4o",
        verbosity_profile="concise",
        status=PromptStatus.PUBLISHED,
        created_by="test"
    )
    db.add(profile)
    db.commit()
    
    ExecutionProfileRegistry.invalidate_cache()

    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat", feature="test_verb"),
        request_id="req-v", trace_id="tr-v"
    )
    
    plan, _ = await gateway._resolve_plan(request, db)
    
    # 2. Assertions
    assert "[CONSIGNE DE VERBOSITÉ]" in plan.rendered_developer_prompt
    assert "concise" in plan.rendered_developer_prompt
    # Default tokens for concise is 800
    assert plan.max_output_tokens == 800
    assert plan.max_output_tokens_source == "verbosity_default"

@pytest.mark.asyncio
async def test_reasoning_profile_openai_mapping(db):
    """Test Story 66.18: Reasoning profile mapping for OpenAI."""
    profile = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="Deep Profile",
        feature="test_reason",
        model="o1-preview",
        reasoning_profile="deep",
        status=PromptStatus.PUBLISHED,
        created_by="test"
    )
    db.add(profile)
    db.commit()
    
    ExecutionProfileRegistry.invalidate_cache()

    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat", feature="test_reason"),
        request_id="req-r", trace_id="tr-r"
    )
    
    plan, _ = await gateway._resolve_plan(request, db)
    
    # 2. Assertions
    assert plan.translated_provider_params.get("reasoning_effort") == "high"

@pytest.mark.asyncio
async def test_max_tokens_priority(db):
    """Test Story 66.18: max_output_tokens priority resolution."""
    from app.infra.db.models.llm_prompt import LlmPromptVersionModel

    # 1. Setup Profile with max_tokens=1000
    profile = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="P1000",
        feature="test_prio",
        model="gpt-4o",
        max_output_tokens=1000,
        status=PromptStatus.PUBLISHED,
        created_by="test"
    )
    db.add(profile)
    
    # 2. Setup Assembly with LengthBudget=500
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(), use_case_key="chat", developer_prompt="P",
        status=PromptStatus.PUBLISHED, model="gpt-4o", created_by="test"
    )
    db.add(fv)
    
    assembly = PromptAssemblyConfigModel(
        feature="test_prio",
        plan="premium",
        locale="fr-FR",
        feature_template_ref=fv.id,
        length_budget={"global_max_tokens": 500},
        execution_config={"model": "gpt-4o", "max_output_tokens": 2000},
        status=PromptStatus.PUBLISHED,
        created_by="test"
    )
    db.add(assembly)
    db.commit()
    
    ExecutionProfileRegistry.invalidate_cache()

    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat", feature="test_prio", plan="premium"),
        request_id="req-p", trace_id="tr-p"
    )
    
    plan, _ = await gateway._resolve_plan(request, db)
    
    # LengthBudget wins over Profile
    assert plan.max_output_tokens == 500
    assert plan.max_output_tokens_source == "length_budget"

@pytest.mark.asyncio
async def test_structured_output_mode_populates_plan_response_format(db):
    """Execution profiles with structured_json output_mode should populate the resolved plan."""
    uc = LlmUseCaseConfigModel(key="json_uc", display_name="json_uc", description="test", safety_profile="astrology")
    db.add(uc)
    prompt = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="json_uc",
        developer_prompt="Return a compact structured response.",
        model="gpt-4o",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db.add(prompt)
    profile = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="JSON Profile",
        feature="json_feature",
        provider="openai",
        model="gpt-4o",
        output_mode="structured_json",
        status=PromptStatus.PUBLISHED,
        created_by="test"
    )
    db.add(profile)
    db.commit()

    ExecutionProfileRegistry.invalidate_cache()

    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="json_uc", feature="json_feature"),
        request_id="req-json", trace_id="tr-json"
    )

    plan, _ = await gateway._resolve_plan(request, db)

    assert plan.response_format is not None
    assert plan.response_format.type == "json_object"

@pytest.mark.asyncio
async def test_unsupported_profile_provider_falls_back_to_openai(db):
    """Unsupported providers should degrade to the stable OpenAI fallback path."""
    uc = LlmUseCaseConfigModel(key="chat", display_name="chat", description="test", safety_profile="astrology")
    db.add(uc)
    profile = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="Anthropic Profile",
        feature="anthropic_feature",
        provider="anthropic",
        model="claude-sonnet-4-5",
        reasoning_profile="deep",
        status=PromptStatus.PUBLISHED,
        created_by="test"
    )
    db.add(profile)
    db.commit()

    ExecutionProfileRegistry.invalidate_cache()

    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat", feature="anthropic_feature"),
        request_id="req-anthropic", trace_id="tr-anthropic"
    )

    plan, _ = await gateway._resolve_plan(request, db)

    assert plan.provider == "openai"
    assert plan.execution_profile_source == "fallback_resolve_model"
    assert plan.translated_provider_params == {}

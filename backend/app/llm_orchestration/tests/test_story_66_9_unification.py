import pytest
import uuid
import logging
from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import LLMExecutionRequest, ExecutionUserInput
from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2
from app.infra.db.models import LlmUseCaseConfigModel

@pytest.mark.asyncio
async def test_deprecated_use_case_redirection(db):
    """Test Story 66.9: Deprecated use case is redirected to assembly feature/plan."""
    # 1. Setup Assembly for the target feature/plan
    # We use 'horoscope_daily' as feature and 'free' as plan
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="horoscope_daily_feature",
        developer_prompt="DAILY HOROSCOPE FEATURE",
        status=PromptStatus.PUBLISHED,
        model="gpt-4o",
        created_by="test"
    )
    db.add(fv)
    
    # Need UseCaseConfig for safety_profile resolution
    uc_config = LlmUseCaseConfigModel(
        key="horoscope_daily_feature",
        display_name="Horoscope Daily",
        description="test description",
        safety_profile="astrology"
    )
    db.add(uc_config)
    
    config = PromptAssemblyConfigModel(
        feature="horoscope_daily",
        subfeature="narration",
        plan="free",
        locale="fr-FR",
        feature_template_ref=fv.id,
        plan_rules_ref="plan_free_concise",
        plan_rules_enabled=True,
        execution_config={"model": "gpt-4o", "max_output_tokens": 2000},
        status=PromptStatus.PUBLISHED,
        created_by="test"
    )

    db.add(config)
    db.commit()

    # 2. Call Gateway with deprecated use_case
    gateway = LLMGateway()
    # 'horoscope_daily_free' is in DEPRECATED_USE_CASE_MAPPING
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="horoscope_daily_free"),
        request_id="req-dep",
        trace_id="trace-dep"
    )
    
    # Stage 1 resolution
    plan, _ = await gateway._resolve_plan(request, db)
    
    # 3. Assertions
    # Redirection happened
    assert request.user_input.feature == "horoscope_daily"
    assert request.user_input.plan == "free"
    
    # Plan resolution used assembly
    assert plan.model_source == "assembly"
    assert plan.feature == "horoscope_daily"
    assert plan.plan == "free"
    assert plan.assembly_id == str(config.id)
    
    # Plan rules applied
    assert "CONSIGNE ABONNEMENT FREE" in plan.rendered_developer_prompt
    # max_output_tokens constrained by plan_free_concise (1000) vs config (2000)
    assert plan.max_output_tokens == 1000

@pytest.mark.asyncio
async def test_naming_validation_on_publish(db, caplog):
    """Test Story 66.9: Naming warning on publish if suffix _free/_full is used."""
    # 1. Setup draft version with _free suffix
    version = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="test_naming_free",
        developer_prompt="PROMPT",
        status=PromptStatus.DRAFT,
        model="gpt-4o",
        created_by="test"
    )
    db.add(version)
    db.commit()
    
    # 2. Publish
    with caplog.at_level(logging.WARNING):
        PromptRegistryV2.publish_prompt(db, version.id)
        
    # 3. Verify warning in logs
    assert "prompt_registry_v2_naming_warning" in caplog.text
    assert "use_case suffix '_free'/'_full' detected for 'test_naming_free'" in caplog.text

@pytest.mark.asyncio
async def test_deprecated_full_redirection(db):
    """Test Story 66.9: Deprecated 'horoscope_daily_full' redirection."""
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="h_full",
        developer_prompt="FULL HOROSCOPE",
        status=PromptStatus.PUBLISHED,
        model="gpt-4o",
        created_by="test"
    )
    db.add(fv)
    uc_config = LlmUseCaseConfigModel(
        key="h_full", 
        display_name="Horoscope Full",
        description="test description",
        safety_profile="astrology"
    )
    db.add(uc_config)
    
    config = PromptAssemblyConfigModel(
        feature="horoscope_daily",
        subfeature="narration",
        plan="premium",
        locale="fr-FR",
        feature_template_ref=fv.id,
        plan_rules_ref="plan_premium_full",
        plan_rules_enabled=True,
        execution_config={"model": "gpt-4o-premium"},
        status=PromptStatus.PUBLISHED,
        created_by="test"
    )
    db.add(config)
    db.commit()

    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="horoscope_daily_full"),
        request_id="req-full",
        trace_id="trace-full"
    )
    
    plan, _ = await gateway._resolve_plan(request, db)
    
    assert request.user_input.feature == "horoscope_daily"
    assert request.user_input.plan == "premium"
    assert plan.model_id == "gpt-4o-premium"
    assert "CONSIGNE ABONNEMENT PREMIUM" in plan.rendered_developer_prompt

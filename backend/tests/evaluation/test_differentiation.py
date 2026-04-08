import pytest
import uuid
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import LLMExecutionRequest, ExecutionUserInput
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus, LlmUseCaseConfigModel
from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel

@pytest.mark.evaluation
@pytest.mark.asyncio
async def test_plan_differentiation(db):
    """Checks that premium plan produces a different (longer/richer) prompt than free."""
    # 1. Setup
    feat = "natal"
    uc_key = "natal_test"
    uc = LlmUseCaseConfigModel(key=uc_key, display_name=uc_key, description="test", safety_profile="astrology")
    db.add(uc)
    v = LlmPromptVersionModel(
        id=uuid.uuid4(), use_case_key=uc_key, developer_prompt="BASE", 
        model="gpt-4o", status=PromptStatus.PUBLISHED, created_by="eval"
    )
    db.add(v)
    db.commit()
    
    from app.llm_orchestration.services.assembly_resolver import PLAN_RULES_REGISTRY
    
    # Create assemblies for free and premium
    for plan in ["free", "premium"]:
        config = PromptAssemblyConfigModel(
            id=uuid.uuid4(), feature=feat, plan=plan, locale="fr-FR",
            feature_template_ref=v.id,
            plan_rules_ref="plan_free_concise" if plan == "free" else "plan_premium_full",
            plan_rules_enabled=True,
            execution_config={"model": "gpt-4o", "max_output_tokens": 2000},
            status=PromptStatus.PUBLISHED, created_by="eval"
        )
        db.add(config)
    db.commit()

    gateway = LLMGateway()
    
    # 2. Resolve both
    req_free = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case=uc_key, feature=feat, plan="free"),
        request_id="r1", trace_id="t1"
    )
    plan_free, _ = await gateway._resolve_plan(req_free, db)
    
    req_prem = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case=uc_key, feature=feat, plan="premium"),
        request_id="r2", trace_id="t2"
    )
    plan_prem, _ = await gateway._resolve_plan(req_prem, db)
    
    # 3. Assertions
    assert plan_free.rendered_developer_prompt != plan_prem.rendered_developer_prompt
    assert "CONSIGNE ABONNEMENT PREMIUM" in plan_prem.rendered_developer_prompt
    assert "CONSIGNE ABONNEMENT FREE" in plan_free.rendered_developer_prompt

@pytest.mark.evaluation
@pytest.mark.asyncio
async def test_persona_differentiation(db, mock_personas):
    """Checks that different astrologer profiles produce different persona blocks."""
    feat = "chat"
    uc_key = "chat_test"
    uc = LlmUseCaseConfigModel(key=uc_key, display_name=uc_key, description="test", safety_profile="astrology")
    db.add(uc)
    v = LlmPromptVersionModel(
        id=uuid.uuid4(), use_case_key=uc_key, developer_prompt="BASE", 
        model="gpt-4o", status=PromptStatus.PUBLISHED, created_by="eval"
    )
    db.add(v)
    db.commit()
    
    # Create personas
    p_ids = {}
    for p_type, p_data in mock_personas.items():
        persona = LlmPersonaModel(
            id=uuid.uuid4(), name=p_data["name"], description="test",
            style_markers=p_data["style_markers"], boundaries=p_data["boundaries"],
            enabled=True
        )
        db.add(persona)
        p_ids[p_type] = persona.id
    db.commit()
    
    # Update UC with allowed personas
    uc.allowed_persona_ids = [str(pid) for pid in p_ids.values()]
    db.commit()

    gateway = LLMGateway()
    
    # 2. Resolve both with the same feature/plan but different persona_ref in assembly
    # We simulate this by overriding persona_id in the request
    # but the story says we should compare blocks.
    
    results = []
    for p_type in ["synthetique", "ample"]:
        request = LLMExecutionRequest(
            user_input=ExecutionUserInput(
                use_case=uc_key, feature=feat, plan="free", persona_id_override=str(p_ids[p_type])
            ),
            request_id=f"r-{p_type}", trace_id="t"
        )
        plan_res, _ = await gateway._resolve_plan(request, db)
        results.append(plan_res.persona_block)
        
    # 3. Assertions
    assert results[0] != results[1]
    assert mock_personas["synthetique"]["name"] in results[0]
    assert mock_personas["ample"]["name"] in results[1]

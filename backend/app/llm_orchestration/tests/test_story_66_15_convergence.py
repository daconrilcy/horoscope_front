import pytest
import uuid
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import LLMExecutionRequest, ExecutionUserInput
from app.services.ai_engine_adapter import AIEngineAdapter
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus, LlmUseCaseConfigModel
from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models import LlmOutputSchemaModel

def setup_convergence_data(db):
    # 1. Create Execution Profile
    prof = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="Standard",
        provider="openai",
        model="gpt-4o",
        status=PromptStatus.PUBLISHED,
        created_by="test"
    )
    db.add(prof)

    # 2. Create Output Schema for paid use cases
    schema = LlmOutputSchemaModel(
        id=uuid.uuid4(),
        name="Natal Interpretation V3",
        version=3,
        json_schema={"type": "object"}
    )
    db.add(schema)
    db.commit()

    # 3. Create UseCaseConfigs and PromptVersions
    ucs = ["chat_astrologer", "guidance_daily", "natal_interpretation"]
    for uc_key in ucs:
        uc = LlmUseCaseConfigModel(
            key=uc_key, 
            display_name=uc_key, 
            description="test", 
            safety_profile="astrology",
            output_schema_id=str(schema.id) if uc_key == "natal_interpretation" else None
        )
        db.add(uc)
        
        v = LlmPromptVersionModel(
            id=uuid.uuid4(),
            use_case_key=uc_key,
            developer_prompt=f"PROMPT FOR {uc_key}",
            model="gpt-4o",
            status=PromptStatus.PUBLISHED,
            created_by="test"
        )
        db.add(v)
        
        # 4. Create Assembly
        feat = uc_key.split("_")[0]
        # Align subfeature name with the one used in tests
        if uc_key == "chat_astrologer":
            subfeat = "astrologer"
        elif uc_key == "guidance_daily":
            subfeat = "daily"
        elif uc_key == "natal_interpretation":
            subfeat = "natal_interpretation"
        else:
            subfeat = uc_key
            
        plan = "premium" if "chat" in uc_key or "natal" in uc_key else "free"
        
        config = PromptAssemblyConfigModel(
            id=uuid.uuid4(),
            feature=feat,
            subfeature=subfeat if subfeat != feat else None,
            plan=plan,
            locale="fr-FR",
            feature_template_ref=v.id,
            execution_profile_ref=prof.id,
            execution_config={"model": "gpt-4o", "max_output_tokens": 1000},
            output_contract_ref=str(schema.id) if uc_key == "natal_interpretation" else None,
            status=PromptStatus.PUBLISHED,
            created_by="test"
        )
        db.add(config)
    
    db.commit()

@pytest.mark.asyncio
async def test_chat_convergence_to_assembly(db):
    """Test Story 66.15: Chat family uses assembly."""
    setup_convergence_data(db)
    gateway = LLMGateway()
    
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="chat_astrologer",
            feature="chat",
            subfeature="astrologer",
            plan="premium"
        ),
        request_id="req-chat", trace_id="tr-chat"
    )
    
    plan, _ = await gateway._resolve_plan(request, db)
    
    assert plan.model_source == "assembly"
    assert plan.feature == "chat"
    assert plan.subfeature == "astrologer"
    assert plan.plan == "premium"

@pytest.mark.asyncio
async def test_guidance_convergence_to_assembly(db):
    """Test Story 66.15: Guidance family uses assembly."""
    setup_convergence_data(db)
    gateway = LLMGateway()
    
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="guidance_daily",
            feature="guidance",
            subfeature="daily",
            plan="free"
        ),
        request_id="req-gui", trace_id="tr-gui"
    )
    
    plan, _ = await gateway._resolve_plan(request, db)
    
    assert plan.model_source == "assembly"
    assert plan.feature == "guidance"
    assert plan.subfeature == "daily"

@pytest.mark.asyncio
async def test_natal_convergence_to_assembly(db):
    """Test Story 66.15: Natal family uses assembly."""
    setup_convergence_data(db)
    gateway = LLMGateway()
    
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal_interpretation",
            feature="natal",
            subfeature="natal_interpretation",
            plan="premium"
        ),
        request_id="req-nat", trace_id="tr-nat"
    )
    
    plan, _ = await gateway._resolve_plan(request, db)
    
    assert plan.model_source == "assembly"
    assert plan.feature == "natal"
    assert plan.subfeature == "natal_interpretation"
    assert plan.output_schema is not None

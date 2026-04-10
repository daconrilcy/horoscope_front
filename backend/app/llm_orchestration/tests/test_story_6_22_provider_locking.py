import uuid
import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel, LlmPromptVersionModel
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import LLMExecutionRequest, ExecutionUserInput
from app.llm_orchestration.services.assembly_admin_service import AssemblyAdminService
from app.infra.observability.metrics import get_metrics_snapshot, reset_metrics

@pytest.fixture
def gateway():
    return LLMGateway()

@pytest.mark.asyncio
async def test_ac4_runtime_rejected_nominal_unsupported_provider(db: Session, gateway):
    """
    Finding 1: Ensure nominal path fails BEFORE fallback for any unsupported provider.
    """
    # 1. Create a version for assembly
    version = LlmPromptVersionModel(
        use_case_key="chat",
        developer_prompt="test {{last_user_msg}}",
        status=PromptStatus.PUBLISHED,
        created_by="test",
        model="gpt-4o"
    )
    db.add(version)
    db.flush()

    # 2. Bypass validator via direct SQL to have a published unsupported profile
    profile_id = str(uuid.uuid4())
    db.execute(
        text("INSERT INTO llm_execution_profiles (id, name, provider, model, feature, status, created_by, reasoning_profile, verbosity_profile, output_mode, tool_mode, timeout_seconds, created_at) "
             "VALUES (:id, :name, :provider, :model, :feature, :status, :created_by, :rp, :vp, :om, :tm, :timeout, datetime('now'))"),
        {
            "id": profile_id,
            "name": "Mistral Nominal",
            "provider": "mistral",
            "model": "mistral-large",
            "feature": "chat",
            "status": "published",
            "created_by": "test",
            "rp": "off", "vp": "balanced", "om": "free_text", "tm": "none", "timeout": 30
        }
    )
    
    # 3. Create a published assembly referencing it
    assembly = PromptAssemblyConfigModel(
        feature="chat",
        feature_template_ref=version.id,
        execution_profile_ref=uuid.UUID(profile_id),
        status=PromptStatus.PUBLISHED,
        created_by="test",
        locale="fr-FR",
        plan="free",
        execution_config={"provider": "mistral", "model": "mistral-large"} 
    )
    db.add(assembly)
    db.commit()

    request = LLMExecutionRequest(
        request_id=str(uuid.uuid4()),
        trace_id=str(uuid.uuid4()),
        user_input=ExecutionUserInput(
            use_case="chat",
            feature="chat",
            message="hello"
        )
    )

    reset_metrics()
    with pytest.raises(ValueError, match="Provider 'mistral' is not nominally supported"):
        await gateway.execute_request(request, db=db)
    
    metrics = get_metrics_snapshot()
    found = False
    for name in metrics["counters"]:
        if "llm_governance_event_total" in name and "event_type=runtime_rejected" in name and "provider=mistral" in name:
            found = True
            break
    assert found

@pytest.mark.asyncio
async def test_ac5_non_nominal_tolerated(db: Session, gateway):
    """
    AC5: Unsupported provider on NON-NOMINAL path should fallback to OpenAI.
    """
    # Use a non-mapped use case to keep feature=None
    from app.llm_orchestration.gateway import USE_CASE_STUBS, UseCaseConfig
    USE_CASE_STUBS["legacy_test_lock"] = UseCaseConfig(
        model="gpt-4o",
        developer_prompt="test {{last_user_msg}}",
        required_prompt_placeholders=["last_user_msg"]
    )

    # Bypass validator
    profile_id = str(uuid.uuid4())
    db.execute(
        text("INSERT INTO llm_execution_profiles (id, name, provider, model, feature, status, created_by, reasoning_profile, verbosity_profile, output_mode, tool_mode, timeout_seconds, created_at) "
             "VALUES (:id, :name, :provider, :model, :feature, :status, :created_by, :rp, :vp, :om, :tm, :timeout, datetime('now'))"),
        {
            "id": profile_id,
            "name": "Anthropic Legacy",
            "provider": "anthropic",
            "model": "claude-3",
            "feature": None, # Non-nominal
            "status": "published",
            "created_by": "test",
            "rp": "off", "vp": "balanced", "om": "free_text", "tm": "none", "timeout": 30
        }
    )
    
    version = LlmPromptVersionModel(
        use_case_key="chat", 
        developer_prompt="test {{last_user_msg}}",
        status=PromptStatus.PUBLISHED,
        created_by="test",
        model="gpt-4o"
    )
    db.add(version)
    db.flush()
    
    assembly = PromptAssemblyConfigModel(
        feature="legacy_test_lock",
        feature_template_ref=version.id,
        execution_profile_ref=uuid.UUID(profile_id),
        status=PromptStatus.PUBLISHED,
        created_by="test",
        locale="fr-FR",
        plan="free",
        execution_config={"provider": "anthropic", "model": "claude-3"} 
    )
    db.add(assembly)
    db.commit()

    request = LLMExecutionRequest(
        request_id=str(uuid.uuid4()),
        trace_id=str(uuid.uuid4()),
        user_input=ExecutionUserInput(
            use_case="legacy_test_lock",
            feature="legacy_test_lock", 
            message="hello"
        )
    )

    reset_metrics()
    try:
        await gateway.execute_request(request, db=db)
    except Exception:
        pass # We only care about the metric being emitted before any execution errors

    metrics = get_metrics_snapshot()
    found = False
    for name in metrics["counters"]:
        if "llm_governance_event_total" in name and "event_type=non_nominal_tolerated" in name and "provider=anthropic" in name:
            found = True
            break
    assert found

@pytest.mark.asyncio
async def test_finding_2_rollback_validation(db: Session):
    """
    Finding 2: Rollback must re-validate provider.
    """
    service = AssemblyAdminService(db)
    
    version = LlmPromptVersionModel(
        use_case_key="chat",
        developer_prompt="test",
        status=PromptStatus.PUBLISHED,
        created_by="test",
        model="gpt-4o"
    )
    db.add(version)
    db.flush()

    config = PromptAssemblyConfigModel(
        feature="chat",
        feature_template_ref=version.id,
        execution_config={"provider": "mistral", "model": "m"},
        status=PromptStatus.ARCHIVED, 
        created_by="test",
        locale="fr-FR"
    )
    db.add(config)
    db.commit()

    with pytest.raises(ValueError, match="not nominally supported"):
        await service.rollback_config("chat", None, "free", "fr-FR", config.id)

@pytest.mark.asyncio
async def test_ac3_publish_validation(db: Session):
    """
    AC3: Publication must validate provider.
    """
    service = AssemblyAdminService(db)
    
    version = LlmPromptVersionModel(
        use_case_key="chat",
        developer_prompt="test",
        status=PromptStatus.PUBLISHED,
        created_by="test",
        model="gpt-4o"
    )
    db.add(version)
    db.flush()

    config = PromptAssemblyConfigModel(
        feature="chat",
        feature_template_ref=version.id,
        execution_config={"provider": "mistral", "model": "m"},
        status=PromptStatus.DRAFT,
        created_by="test",
        locale="fr-FR"
    )
    db.add(config)
    db.commit()

    with pytest.raises(ValueError, match="not nominally supported"):
        await service.publish_config(config.id)

def test_finding_3_model_level_validation(db: Session):
    """
    Finding 3: LlmExecutionProfileModel should reject status=PUBLISHED if provider is unsupported.
    """
    profile = LlmExecutionProfileModel(
        name="Mistral",
        provider="mistral",
        model="m",
        status=PromptStatus.DRAFT,
        created_by="test"
    )
    db.add(profile)
    db.commit()

    with pytest.raises(ValueError, match="not nominally supported"):
        profile.status = PromptStatus.PUBLISHED

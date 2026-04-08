import pytest
import uuid
from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import LLMExecutionRequest, ExecutionUserInput
from app.llm_orchestration.services.assembly_registry import AssemblyRegistry
from app.llm_orchestration.services.assembly_resolver import resolve_assembly, assemble_developer_prompt

from app.infra.db.models import LlmUseCaseConfigModel
from app.llm_orchestration.services.assembly_resolver import validate_placeholders

@pytest.mark.asyncio
async def test_assembly_resolution_basic(db):
    # 1. Setup data
    feature_v = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="feature_test",
        developer_prompt="FEATURE PROMPT {{locale}}",
        status=PromptStatus.PUBLISHED,
        model="gpt-4o",
        created_by="test"
    )
    db.add(feature_v)
    
    # M2 Fix: Need UseCaseConfig to resolve safety_profile
    uc_config = LlmUseCaseConfigModel(
        key="feature_test",
        display_name="Feature Test",
        description="test",
        safety_profile="astrology"
    )
    db.add(uc_config)
    
    persona = LlmPersonaModel(
        id=uuid.uuid4(),
        name="Test Persona",
        description="A test persona",
        tone="direct",
        verbosity="medium",
        enabled=True
    )
    db.add(persona)
    db.commit()

    config = PromptAssemblyConfigModel(
        feature="feature_test",
        locale="fr-FR",
        feature_template_ref=feature_v.id,
        persona_ref=persona.id,
        execution_config={"model": "gpt-4o", "temperature": 0.5, "max_output_tokens": 100},
        status=PromptStatus.PUBLISHED,
        created_by="test"
    )
    db.add(config)
    db.commit()

    # 2. Test Registry
    registry = AssemblyRegistry(db)
    resolved_db = await registry.get_active_config("feature_test", None, None, "fr-FR")
    assert resolved_db is not None
    assert resolved_db.feature == "feature_test"

    # 3. Test Resolver
    resolved = resolve_assembly(resolved_db)
    assert resolved.feature_template_prompt == "FEATURE PROMPT {{locale}}"
    assert "Adopte un ton direct" in resolved.persona_block
    assert resolved.execution_config.temperature == 0.5
    assert "interprétation astrologique" in resolved.policy_layer_content
    # 4. Test Assembly concatenation
    full_prompt = assemble_developer_prompt(resolved, resolved_db)
    assert full_prompt == "FEATURE PROMPT {{locale}}"

def test_validate_placeholders_logic():
    # Valid placeholders for guidance
    assert validate_placeholders("Hello {{last_user_msg}}", "guidance") == []
    assert validate_placeholders("Hello {{locale}}", "guidance") == []
    
    # Invalid placeholder
    assert validate_placeholders("Hello {{forbidden_var}}", "guidance") == ["forbidden_var"]
    
    # Valid for natal
    assert validate_placeholders("Theme {{chart_json}}", "natal") == []
    # Invalid for natal
    assert validate_placeholders("Theme {{situation}}", "natal") == ["situation"]

@pytest.mark.asyncio
async def test_assembly_waterfall_fallback(db):
    # Setup: 1 generic config, 1 specific config
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(), use_case_key="f", developer_prompt="GENERIC",
        status=PromptStatus.PUBLISHED, model="m", created_by="t"
    )
    db.add(fv)
    db.commit()

    c_gen = PromptAssemblyConfigModel(
        feature="feat", subfeature=None, plan=None, locale="fr-FR",
        feature_template_ref=fv.id, execution_config={"model":"m"},
        status=PromptStatus.PUBLISHED, created_by="t"
    )
    c_spec = PromptAssemblyConfigModel(
        feature="feat", subfeature="sub", plan=None, locale="fr-FR",
        feature_template_ref=fv.id, execution_config={"model":"m-spec"},
        status=PromptStatus.PUBLISHED, created_by="t"
    )
    db.add_all([c_gen, c_spec])
    db.commit()

    registry = AssemblyRegistry(db)
    
    # Precise match
    res1 = await registry.get_active_config("feat", "sub", "anyplan", "fr-FR")
    assert res1.execution_config["model"] == "m-spec"
    
    # Fallback to generic
    res2 = await registry.get_active_config("feat", "other", None, "fr-FR")
    assert res2.execution_config["model"] == "m"

@pytest.mark.asyncio
async def test_gateway_uses_assembly(db):
    # 1. Setup Assembly
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(), use_case_key="feat_gw", developer_prompt="FROM ASSEMBLY",
        status=PromptStatus.PUBLISHED, model="gpt-4o", created_by="t"
    )
    db.add(fv)
    db.commit()

    config = PromptAssemblyConfigModel(
        feature="feat_gw", locale="fr-FR",
        feature_template_ref=fv.id,
        execution_config={"model": "gpt-4o-assembly", "max_output_tokens": 500},
        status=PromptStatus.PUBLISHED, created_by="t"
    )
    db.add(config)
    db.commit()

    # 2. Call Gateway
    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="feat_gw", feature="feat_gw"),
        request_id="req-1",
        trace_id="trace-1"
    )
    
    plan, qctx = await gateway._resolve_plan(request, db)
    
    assert plan.model_id == "gpt-4o-assembly"
    assert plan.model_source == "assembly"
    assert plan.rendered_developer_prompt == "FROM ASSEMBLY"
    assert plan.assembly_id == str(config.id)

@pytest.mark.asyncio
async def test_gateway_assembly_priority_id(db):
    # Setup two assemblies
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(), use_case_key="priority", developer_prompt="PROMPT",
        status=PromptStatus.PUBLISHED, model="m", created_by="t"
    )
    db.add(fv)
    db.commit()

    c1 = PromptAssemblyConfigModel(
        id=uuid.uuid4(), feature="priority", status=PromptStatus.PUBLISHED,
        feature_template_ref=fv.id, execution_config={"model":"m1"}, created_by="t"
    )
    c2 = PromptAssemblyConfigModel(
        id=uuid.uuid4(), feature="priority", status=PromptStatus.DRAFT, # Even draft works with ID
        feature_template_ref=fv.id, execution_config={"model":"m2"}, created_by="t"
    )
    db.add_all([c1, c2])
    db.commit()

    gateway = LLMGateway()
    
    # Normal resolution uses PUBLISHED c1
    req1 = LLMExecutionRequest(user_input=ExecutionUserInput(use_case="priority", feature="priority"), request_id="r1", trace_id="t1")
    plan1, _ = await gateway._resolve_plan(req1, db)
    assert plan1.model_id == "m1"

    # ID resolution uses c2 (even if draft)
    req2 = LLMExecutionRequest(user_input=ExecutionUserInput(use_case="priority", assembly_config_id=c2.id), request_id="r2", trace_id="t2")
    plan2, _ = await gateway._resolve_plan(req2, db)
    assert plan2.model_id == "m2"
    assert plan2.assembly_id == str(c2.id)

@pytest.mark.asyncio
async def test_assembly_template_source_traceability(db):
    # Setup assembly with subfeature
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(), use_case_key="ts", developer_prompt="F",
        status=PromptStatus.PUBLISHED, model="m", created_by="t"
    )
    sv = LlmPromptVersionModel(
        id=uuid.uuid4(), use_case_key="ts_sub", developer_prompt="S",
        status=PromptStatus.PUBLISHED, model="m", created_by="t"
    )
    db.add_all([fv, sv])
    db.commit()

    c1 = PromptAssemblyConfigModel(
        id=uuid.uuid4(), feature="ts", subfeature="sub", locale="fr-FR",
        feature_template_ref=fv.id, subfeature_template_ref=sv.id,
        execution_config={"model":"m"}, status=PromptStatus.PUBLISHED, created_by="t"
    )
    c2 = PromptAssemblyConfigModel(
        id=uuid.uuid4(), feature="ts", subfeature="other", locale="fr-FR",
        feature_template_ref=fv.id, subfeature_template_ref=None,
        execution_config={"model":"m"}, status=PromptStatus.PUBLISHED, created_by="t"
    )
    db.add_all([c1, c2])
    db.commit()

    gateway = LLMGateway()
    
    # Case 1: explicit_subfeature
    req1 = LLMExecutionRequest(user_input=ExecutionUserInput(use_case="ts", feature="ts", subfeature="sub"), request_id="r1", trace_id="t1")
    plan1, _ = await gateway._resolve_plan(req1, db)
    assert plan1.template_source == "explicit_subfeature"

    # Case 2: fallback_default (no subfeature template defined in assembly)
    req2 = LLMExecutionRequest(user_input=ExecutionUserInput(use_case="ts", feature="ts", subfeature="other"), request_id="r2", trace_id="t2")
    plan2, _ = await gateway._resolve_plan(req2, db)
    assert plan2.template_source == "fallback_default"

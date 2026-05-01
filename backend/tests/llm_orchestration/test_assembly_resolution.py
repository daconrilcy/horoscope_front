import uuid

import pytest

from app.domain.llm.configuration.admin_models import PromptAssemblyConfig
from app.domain.llm.configuration.assembly_admin_service import AssemblyAdminService
from app.domain.llm.configuration.assembly_registry import AssemblyRegistry
from app.domain.llm.configuration.assembly_resolver import (
    assemble_developer_prompt,
    resolve_assembly,
    validate_placeholders,
)
from app.domain.llm.prompting.catalog import PROMPT_FALLBACK_CONFIGS
from app.domain.llm.runtime import gateway as gateway_module
from app.domain.llm.runtime.contracts import (
    ExecutionContext,
    ExecutionMessage,
    ExecutionUserInput,
    GatewayConfigError,
    InputValidationError,
    LLMExecutionRequest,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)


def _create_execution_profile(
    db,
    *,
    feature: str | None,
    subfeature: str | None = None,
    plan: str | None = None,
    model: str = "gpt-4o",
    provider: str = "openai",
    created_by: str = "test",
    status: PromptStatus = PromptStatus.PUBLISHED,
) -> LlmExecutionProfileModel:
    """Crée un profil d'exécution canonique pour les tests d'orchestration."""

    profile = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name=f"profile-{feature or 'generic'}-{subfeature or 'none'}-{plan or 'none'}",
        feature=feature,
        subfeature=subfeature,
        plan=plan,
        provider=provider,
        model=model,
        status=status,
        created_by=created_by,
    )
    db.add(profile)
    db.flush()
    return profile


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("feature", "subfeature", "plan", "use_case", "payload"),
    [
        ("chat", "astrologer", "free", "chat_astrologer", {"message": "Bonjour"}),
        ("guidance", "contextual", "free", "guidance_contextual", {"message": "Que faire ?"}),
        ("natal", "interpretation", "premium", "natal_interpretation", {"chart_json": {}}),
        ("horoscope_daily", None, "free", "horoscope_daily", {"question": "Ma journee ?"}),
    ],
)
async def test_production_rejects_missing_assembly_for_supported_families(
    db,
    monkeypatch: pytest.MonkeyPatch,
    feature: str,
    subfeature: str | None,
    plan: str,
    use_case: str,
    payload: dict,
) -> None:
    """La production refuse toute famille supportee sans assembly canonique."""

    monkeypatch.setattr(gateway_module.settings, "app_env", "production")
    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case=use_case,
            feature=feature,
            subfeature=subfeature,
            plan=plan,
            locale="fr-FR",
            **payload,
        ),
        context=ExecutionContext(),
        request_id=f"req-missing-{feature}",
        trace_id=f"trace-missing-{feature}",
    )

    with pytest.raises(GatewayConfigError) as exc:
        await gateway._resolve_plan(request, db=db)

    assert exc.value.error_code == "missing_assembly"
    assert exc.value.details["feature"] == feature


@pytest.mark.asyncio
async def test_db_prompt_resolution_does_not_require_supported_fallback_prompt(
    db,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Un prompt DB publie reste resoluble sans prompt fallback supporte."""

    monkeypatch.setattr(gateway_module.settings, "app_env", "development")
    assert "guidance_contextual" not in PROMPT_FALLBACK_CONFIGS

    prompt = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="guidance_contextual",
        developer_prompt="DB guidance prompt {{situation}}",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    use_case = LlmUseCaseConfigModel(
        key="guidance_contextual",
        display_name="Guidance Contextual",
        description="test",
    )
    db.add_all([prompt, use_case])
    db.commit()

    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="guidance_contextual",
            feature="guidance",
            subfeature="contextual",
            plan="free",
            message="Que faire ?",
        ),
        context=ExecutionContext(),
        request_id="req-db-guidance",
        trace_id="trace-db-guidance",
    )

    plan, _ = await gateway._resolve_plan(request, db=db)

    assert plan.rendered_developer_prompt.startswith("DB guidance prompt")
    assert plan.prompt_version_id == str(prompt.id)


@pytest.mark.asyncio
async def test_assembly_resolution_basic(db):
    # 1. Setup data
    feature_v = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="feature_test",
        developer_prompt="FEATURE PROMPT {{locale}}",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db.add(feature_v)

    uc_config = LlmUseCaseConfigModel(
        key="feature_test",
        display_name="Feature Test",
        description="test",
    )
    db.add(uc_config)

    persona = LlmPersonaModel(
        id=uuid.uuid4(),
        name="Test Persona",
        description="A test persona",
        tone="direct",
        verbosity="medium",
        enabled=True,
    )
    db.add(persona)
    profile = _create_execution_profile(db, feature="feature_test", model="gpt-4o")
    db.commit()

    config = PromptAssemblyConfigModel(
        feature="feature_test",
        locale="fr-FR",
        feature_template_ref=feature_v.id,
        persona_ref=persona.id,
        execution_profile_ref=profile.id,
        status=PromptStatus.PUBLISHED,
        created_by="test",
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
    assert resolved.execution_profile_ref == profile.id
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
async def test_resolve_assembly_keeps_execution_profile_ref_for_reasoning_model(db):
    feature_v = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="reasoning_feature",
        developer_prompt="FEATURE PROMPT {{locale}}",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db.add(feature_v)

    uc_config = LlmUseCaseConfigModel(
        key="reasoning_feature",
        display_name="Reasoning Feature",
        description="test",
    )
    db.add(uc_config)
    profile = _create_execution_profile(db, feature="reasoning_feature", model="gpt-5")
    db.commit()

    config = PromptAssemblyConfigModel(
        feature="reasoning_feature",
        locale="fr-FR",
        feature_template_ref=feature_v.id,
        execution_profile_ref=profile.id,
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db.add(config)
    db.commit()

    resolved_db = db.get(PromptAssemblyConfigModel, config.id)
    assert resolved_db is not None

    resolved = resolve_assembly(resolved_db)

    assert resolved.execution_profile_ref == profile.id


@pytest.mark.asyncio
async def test_assembly_waterfall_fallback(db):
    # Setup: 1 generic config, 1 specific config
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="f",
        developer_prompt="GENERIC",
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    db.add(fv)
    generic_profile = _create_execution_profile(db, feature="feat", model="m")
    specific_profile = _create_execution_profile(
        db,
        feature="feat",
        subfeature="sub",
        model="m-spec",
    )
    db.commit()

    c_gen = PromptAssemblyConfigModel(
        feature="feat",
        subfeature=None,
        plan=None,
        locale="fr-FR",
        feature_template_ref=fv.id,
        execution_profile_ref=generic_profile.id,
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    c_spec = PromptAssemblyConfigModel(
        feature="feat",
        subfeature="sub",
        plan=None,
        locale="fr-FR",
        feature_template_ref=fv.id,
        execution_profile_ref=specific_profile.id,
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    db.add_all([c_gen, c_spec])
    db.commit()

    registry = AssemblyRegistry(db)

    # Precise match
    res1 = await registry.get_active_config("feat", "sub", "anyplan", "fr-FR")
    assert res1.execution_profile.model == "m-spec"

    # Fallback to generic
    res2 = await registry.get_active_config("feat", "other", None, "fr-FR")
    assert res2.execution_profile.model == "m"


@pytest.mark.asyncio
async def test_gateway_uses_assembly(db):
    # 1. Setup Assembly
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="feat_gw",
        developer_prompt="FROM ASSEMBLY",
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    db.add(fv)
    profile = _create_execution_profile(db, feature="feat_gw", model="gpt-4o-assembly")
    db.commit()

    config = PromptAssemblyConfigModel(
        feature="feat_gw",
        locale="fr-FR",
        feature_template_ref=fv.id,
        execution_profile_ref=profile.id,
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    db.add(config)
    db.commit()

    # 2. Call Gateway
    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="feat_gw", feature="feat_gw"),
        request_id="req-1",
        trace_id="trace-1",
    )

    plan, qctx = await gateway._resolve_plan(request, db)

    assert plan.model_id == "gpt-4o-assembly"
    assert plan.model_source == "assembly"
    assert plan.rendered_developer_prompt == "FROM ASSEMBLY"
    assert plan.assembly_id == str(config.id)


@pytest.mark.asyncio
async def test_gateway_assembly_sets_default_persona_name_when_missing(db):
    feature_v = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="feat_persona",
        developer_prompt="Persona {{persona_name}}",
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    db.add(feature_v)

    uc_config = LlmUseCaseConfigModel(
        key="feat_persona",
        display_name="Feature Persona",
        description="test",
    )
    db.add(uc_config)
    profile = _create_execution_profile(db, feature="feat_persona", model="gpt-4o")
    db.commit()

    config = PromptAssemblyConfigModel(
        feature="feat_persona",
        locale="fr-FR",
        feature_template_ref=feature_v.id,
        execution_profile_ref=profile.id,
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    db.add(config)
    db.commit()

    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="feat_persona",
            feature="feat_persona",
            locale="fr-FR",
        ),
        request_id="req-persona",
        trace_id="trace-persona",
    )

    plan, _ = await gateway._resolve_plan(request, db)

    assert "Persona Standard" in plan.rendered_developer_prompt


@pytest.mark.asyncio
async def test_gateway_assembly_priority_id(db):
    # Setup two assemblies
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="priority",
        developer_prompt="PROMPT",
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    db.add(fv)
    profile_1 = _create_execution_profile(db, feature="priority", model="m1")
    profile_2 = _create_execution_profile(
        db,
        feature="priority",
        model="m2",
        status=PromptStatus.DRAFT,
    )
    db.commit()

    c1 = PromptAssemblyConfigModel(
        id=uuid.uuid4(),
        feature="priority",
        status=PromptStatus.PUBLISHED,
        feature_template_ref=fv.id,
        execution_profile_ref=profile_1.id,
        created_by="t",
    )
    c2 = PromptAssemblyConfigModel(
        id=uuid.uuid4(),
        feature="priority",
        status=PromptStatus.DRAFT,  # Even draft works with ID
        feature_template_ref=fv.id,
        execution_profile_ref=profile_2.id,
        created_by="t",
    )
    db.add_all([c1, c2])
    db.commit()

    gateway = LLMGateway()

    # Normal resolution uses PUBLISHED c1
    req1 = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="priority", feature="priority"),
        request_id="r1",
        trace_id="t1",
    )
    plan1, _ = await gateway._resolve_plan(req1, db)
    assert plan1.model_id == "m1"

    # ID resolution uses c2 (even if draft)
    req2 = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="priority", assembly_config_id=c2.id),
        request_id="r2",
        trace_id="t2",
    )
    plan2, _ = await gateway._resolve_plan(req2, db)
    assert plan2.model_id == "m2"
    assert plan2.assembly_id == str(c2.id)


@pytest.mark.asyncio
async def test_assembly_rollback_with_hot_cache(db):
    # 1. Setup two published versions for same target
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="rb",
        developer_prompt="P",
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    db.add(fv)
    profile_1 = _create_execution_profile(
        db,
        feature="rb",
        model="m1",
        status=PromptStatus.ARCHIVED,
    )
    profile_2 = _create_execution_profile(db, feature="rb", model="m2")
    db.commit()

    c1 = PromptAssemblyConfigModel(
        id=uuid.uuid4(),
        feature="rb",
        locale="fr-FR",
        feature_template_ref=fv.id,
        execution_profile_ref=profile_1.id,
        status=PromptStatus.ARCHIVED,
        created_by="t",
    )
    c2 = PromptAssemblyConfigModel(
        id=uuid.uuid4(),
        feature="rb",
        locale="fr-FR",
        feature_template_ref=fv.id,
        execution_profile_ref=profile_2.id,
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    db.add_all([c1, c2])
    db.commit()

    registry = AssemblyRegistry(db)

    # 2. Heat cache
    res_heat = await registry.get_active_config("rb", None, None, "fr-FR")
    assert res_heat.execution_profile.model == "m2"

    # 3. Rollback to c1
    await registry.rollback_config("rb", None, None, "fr-FR", c1.id)

    # 4. Verify DB and Cache (cache should be invalidated)
    res_final = await registry.get_active_config("rb", None, None, "fr-FR")
    assert res_final.execution_profile.model == "m1"
    assert res_final.id == c1.id


@pytest.mark.asyncio
async def test_assembly_admin_validate_all_templates(db):
    fv_valid = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="val_feat",
        developer_prompt="Valid {{locale}}",
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    sv_invalid = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="val_sub",
        developer_prompt="Invalid {{forbidden}}",
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    db.add_all([fv_valid, sv_invalid])
    db.commit()

    admin_service = AssemblyAdminService(db)
    config_in = PromptAssemblyConfig(
        feature="guidance",
        feature_template_ref=fv_valid.id,
        subfeature_template_ref=sv_invalid.id,
    )

    # Should raise error because of subfeature_template_ref
    with pytest.raises(ValueError, match="Invalid placeholders in subfeature template"):
        await admin_service.create_draft(config_in, "test@test.com")


@pytest.mark.asyncio
async def test_gateway_assembly_chat_mode(db):
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="chat_astrologer",
        developer_prompt="CHAT PROMPT {{last_user_msg}}",
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    db.add(fv)
    profile = _create_execution_profile(
        db,
        feature="chat",
        subfeature="astrologer",
        plan="free",
        model="gpt-4o",
        created_by="t",
    )
    config = PromptAssemblyConfigModel(
        feature="chat",
        subfeature="astrologer",
        plan="free",
        locale="fr-FR",
        feature_template_ref=fv.id,
        execution_profile_ref=profile.id,
        status=PromptStatus.PUBLISHED,
        created_by="t",
    )
    db.add(config)
    db.commit()

    gateway = LLMGateway()

    # 1. Test missing question triggers InputValidationError (policy=required)
    req_fail = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="chat_astrologer",
            feature="chat",
            subfeature="astrologer",
            plan="free",
        ),
        request_id="r1",
        trace_id="t1",
    )
    with pytest.raises(InputValidationError):
        await gateway.execute_request(req_fail, db=db)

    # 2. Test successful plan resolution with chat mode
    req_ok = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="chat_astrologer",
            feature="chat",
            subfeature="astrologer",
            plan="free",
            message="Hello",
        ),
        context=ExecutionContext(history=[ExecutionMessage(role="user", content="Hi")]),
        request_id="r2",
        trace_id="t2",
    )
    plan, _ = await gateway._resolve_plan(req_ok, db)
    assert plan.interaction_mode == "chat"
    assert plan.user_question_policy == "required"

    # 3. Test message composition (Stage 2)
    messages = gateway._build_messages(req_ok, plan, None)
    # system + developer + history(1) + user = 4 messages
    assert len(messages) == 4
    assert messages[2]["content"] == "Hi"
    assert messages[3]["content"] == "Hello"

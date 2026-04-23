import uuid

import pytest

from app.domain.llm.runtime.contracts import ExecutionUserInput, LLMExecutionRequest
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)


def setup_convergence_data(db):
    # 1. Create Execution Profile
    prof = LlmExecutionProfileModel(
        id=uuid.uuid4(),
        name="Standard",
        provider="openai",
        model="gpt-4o",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db.add(prof)

    # 2. Create Output Schema for paid use cases
    schema = LlmOutputSchemaModel(
        id=uuid.uuid4(), name="Natal Interpretation V3", version=3, json_schema={"type": "object"}
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
            output_schema_id=str(schema.id) if uc_key == "natal_interpretation" else None,
        )
        db.add(uc)

        v = LlmPromptVersionModel(
            id=uuid.uuid4(),
            use_case_key=uc_key,
            developer_prompt=f"PROMPT FOR {uc_key}",
            model="gpt-4o",
            status=PromptStatus.PUBLISHED,
            created_by="test",
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
            subfeat = "interpretation"
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
            created_by="test",
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
            use_case="chat_astrologer", feature="chat", subfeature="astrologer", plan="premium"
        ),
        request_id="req-chat",
        trace_id="tr-chat",
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
            use_case="guidance_daily", feature="guidance", subfeature="daily", plan="free"
        ),
        request_id="req-gui",
        trace_id="tr-gui",
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

    # We use the seeded assembly natal/natal_interpretation/premium
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal_interpretation",
            feature="natal",
            subfeature="natal_interpretation",
            plan="premium",
        ),
        request_id="req-nat",
        trace_id="tr-nat",
    )

    plan, _ = await gateway._resolve_plan(request, db)

    assert plan.model_source == "assembly"
    assert plan.feature == "natal"
    assert plan.subfeature == "interpretation"
    assert plan.output_schema is not None


@pytest.mark.asyncio
async def test_assembly_fallback_to_use_case(db, caplog):
    """Test Story 66.15 AC4: Fallback to use_case when no assembly is found (L2 fix)."""
    setup_convergence_data(db)
    gateway = LLMGateway()

    # Combination that DOES NOT exist in seeded assemblies
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="chat_astrologer", feature="non_existent_feature", plan="free"
        ),
        request_id="req-fallback",
        trace_id="tr-fallback",
    )

    import logging

    with caplog.at_level(logging.INFO, logger="app.domain.llm.runtime.gateway"):
        plan, _ = await gateway._resolve_plan(request, db)

    # Assertions
    # model_source should NOT be 'assembly'
    assert plan.model_source != "assembly"
    # It should fallback to resolve_model (legacy behavior)
    assert plan.model_source in ["os_granular", "os_legacy", "config", "stub"]

    # Story 66.11 D3/AC2 logic in gateway confirms the source
    assert plan.execution_profile_source == "fallback_resolve_model"

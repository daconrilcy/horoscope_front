import logging
import uuid

import pytest

from app.domain.llm.runtime.contracts import ExecutionUserInput, LLMExecutionRequest
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.ops.llm.prompt_registry_v2 import PromptRegistryV2


@pytest.mark.asyncio
async def test_deprecated_use_case_redirection(db):
    """Test Story 66.9: Deprecated use case is redirected to assembly feature/plan."""
    # 1. Setup Assembly for the target feature/plan
    # We use 'horoscope_daily' as feature and 'free' as plan
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="horoscope_daily",
        developer_prompt="DAILY HOROSCOPE FEATURE",
        status=PromptStatus.PUBLISHED,
        model="gpt-4o",
        created_by="test",
    )
    db.add(fv)

    # Need UseCaseConfig for safety_profile resolution
    uc_config = LlmUseCaseConfigModel(
        key="horoscope_daily",
        display_name="Horoscope Daily",
        description="test description",
        safety_profile="astrology",
    )
    db.add(uc_config)

    from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel

    prof = LlmExecutionProfileModel(
        name="test",
        feature="horoscope_daily",
        model="gpt-4o",
        provider="openai",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db.add(prof)

    config = PromptAssemblyConfigModel(
        feature="horoscope_daily",
        subfeature="narration",
        plan="free",
        locale="fr-FR",
        feature_template_ref=fv.id,
        execution_profile_ref=prof.id,
        plan_rules_ref="plan_free_concise",
        plan_rules_enabled=True,
        execution_config={"model": "gpt-4o", "max_output_tokens": 2000},
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )

    db.add(config)
    db.commit()

    # 2. Call Gateway with deprecated use_case
    gateway = LLMGateway()
    # 'horoscope_daily_free' is in DEPRECATED_USE_CASE_MAPPING
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="horoscope_daily_free"),
        request_id="req-dep",
        trace_id="trace-dep",
    )

    from unittest.mock import AsyncMock, patch

    # Mock the actual provider call to avoid OpenAI usage
    with patch.object(gateway, "_call_provider", new_callable=AsyncMock) as mock_call:
        from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo

        mock_call.return_value = GatewayResult(
            use_case="horoscope_daily_free",
            request_id="req-dep",
            trace_id="trace-dep",
            raw_output='{"message": "ok"}',
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=0, model="test"),
        )
        with patch.object(gateway, "_validate_and_normalize") as mock_val:
            from app.domain.llm.runtime.output_validator import ValidationResult

            mock_val.return_value = ValidationResult(
                valid=True, parsed={}, errors=[], normalizations_applied=[]
            )

            # Execute full request to trigger mapping in execute_request
            result = await gateway.execute_request(request, db)

    # 3. Assertions
    # Redirection happened
    assert request.user_input.feature == "horoscope_daily"
    assert request.user_input.plan == "free"

    # Plan resolution used assembly (verified via meta)
    assert result.meta.feature == "horoscope_daily"
    assert result.meta.plan == "free"
    assert result.meta.assembly_id == str(config.id)


@pytest.mark.asyncio
async def test_naming_validation_on_publish(db, caplog):
    """Test Story 66.9: Naming warning on publish if suffix _free/_full is used."""
    # 1. Setup draft version with _free suffix
    version = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="horoscope_daily_free",  # Use a key that is actually in catalog
        # but marked deprecated
        developer_prompt="PROMPT",
        status=PromptStatus.DRAFT,
        model="gpt-4o",
        created_by="test",
    )
    db.add(version)
    db.commit()

    # 2. Publish
    with caplog.at_level(logging.WARNING):
        PromptRegistryV2.publish_prompt(db, version.id)

    # 3. Verify warning in logs
    assert "prompt_registry_v2_naming_warning" in caplog.text
    assert "use_case suffix '_free'/'_full' detected for 'horoscope_daily_free'" in caplog.text


@pytest.mark.asyncio
async def test_deprecated_full_redirection(db):
    """Test Story 66.9: Deprecated 'horoscope_daily_full' redirection."""
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(),
        use_case_key="horoscope_daily",
        developer_prompt="FULL HOROSCOPE",
        status=PromptStatus.PUBLISHED,
        model="gpt-4o",
        created_by="test",
    )
    db.add(fv)
    uc_config = LlmUseCaseConfigModel(
        key="horoscope_daily",
        display_name="Horoscope Full",
        description="test description",
        safety_profile="astrology",
    )
    # Check if uc already exists
    existing_uc = db.query(LlmUseCaseConfigModel).filter_by(key="horoscope_daily").first()
    if not existing_uc:
        db.add(uc_config)

    from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel

    prof = LlmExecutionProfileModel(
        name="test full",
        feature="horoscope_daily",
        model="gpt-4o-premium",
        provider="openai",
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db.add(prof)

    config = PromptAssemblyConfigModel(
        feature="horoscope_daily",
        subfeature="narration",
        plan="premium",
        locale="fr-FR",
        feature_template_ref=fv.id,
        execution_profile_ref=prof.id,
        plan_rules_ref="plan_premium_full",
        plan_rules_enabled=True,
        execution_config={"model": "gpt-4o-premium"},
        status=PromptStatus.PUBLISHED,
        created_by="test",
    )
    db.add(config)
    db.commit()

    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="horoscope_daily_full"),
        request_id="req-full",
        trace_id="trace-full",
    )

    from unittest.mock import AsyncMock, patch

    with patch.object(gateway, "_call_provider", new_callable=AsyncMock) as mock_call:
        from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo

        mock_call.return_value = GatewayResult(
            use_case="horoscope_daily_full",
            request_id="req-full",
            trace_id="trace-full",
            raw_output='{"message": "ok"}',
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=0, model="test"),
        )
        with patch.object(gateway, "_validate_and_normalize") as mock_val:
            from app.domain.llm.runtime.output_validator import ValidationResult

            mock_val.return_value = ValidationResult(
                valid=True, parsed={}, errors=[], normalizations_applied=[]
            )

            result = await gateway.execute_request(request, db)

    assert request.user_input.feature == "horoscope_daily"
    assert request.user_input.plan == "premium"
    # To check the plan details, we could mock _call_provider and inspect the args,
    # or just trust that the assembly resolution was successful and populated metadata
    assert result.meta.model == "gpt-4o-premium"
    assert result.meta.plan == "premium"

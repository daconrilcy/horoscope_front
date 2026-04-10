from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionContext,
    ExecutionFlags,
    ExecutionUserInput,
    GatewayConfigError,
    LLMExecutionRequest,
    UseCaseConfig,
)


@pytest.mark.asyncio
async def test_enforce_mandatory_assembly_chat_nominal():
    """Test Story 66.20: mandatory assembly for nominal chat family."""
    gateway = LLMGateway()

    # Request without assembly_config_id but with feature="chat"
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="chat_astrologer",
            feature="chat",
            subfeature="astrologer",
            plan="free",
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        flags=ExecutionFlags(),
        user_id=1,
        request_id="req-1",
        trace_id="tr-1",
    )

    db = MagicMock(spec=Session)

    with patch(
        "app.llm_orchestration.services.assembly_registry.AssemblyRegistry.get_active_config_sync"
    ) as mock_get:
        mock_get.return_value = None

        with pytest.raises(GatewayConfigError) as exc:
            await gateway._resolve_plan(request, db=db)

        assert "Mandatory assembly missing for nominal chat family" in str(exc.value)


@pytest.mark.asyncio
async def test_allow_legacy_fallback_for_deprecated_use_case():
    """Test Story 66.20: deprecated use cases still allow fallback (legacy compatibility)."""
    gateway = LLMGateway()

    # "chat" is in DEPRECATED_USE_CASE_MAPPING
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="chat",  # deprecated key
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        flags=ExecutionFlags(skip_common_context=True),
        user_id=1,
        request_id="req-2",
        trace_id="tr-2",
    )

    db = MagicMock(spec=Session)

    # Mock DEPRECATED_USE_CASE_MAPPING lookup sets feature="chat"
    with patch(
        "app.llm_orchestration.services.assembly_registry.AssemblyRegistry.get_active_config_sync"
    ) as mock_get:
        mock_get.return_value = None

        # Mock _resolve_config to return a valid UseCaseConfig
        mock_config = UseCaseConfig(
            model="gpt-4o",
            temperature=0.7,
            max_output_tokens=1000,
            system_core_key="default_v1",
            developer_prompt="Legacy prompt",
            prompt_version_id="legacy-v1",
        )

        with (
            patch.object(gateway, "_resolve_config", new_callable=AsyncMock) as mock_resolve_cfg,
            patch.object(
                gateway, "_resolve_persona", new_callable=AsyncMock
            ) as mock_resolve_persona,
            patch("app.llm_orchestration.gateway.get_hard_policy") as mock_hard_policy,
            patch(
                "app.llm_orchestration.services.execution_profile_registry.ExecutionProfileRegistry.get_active_profile"
            ) as mock_get_profile,
        ):
            mock_resolve_cfg.return_value = mock_config
            mock_resolve_persona.return_value = (None, None, None)
            mock_hard_policy.return_value = "System policy"
            mock_get_profile.return_value = None

            # This should NOT raise GatewayConfigError
            plan, _ = await gateway._resolve_plan(request, db=db)

            assert plan is not None
            assert plan.prompt_version_id == "legacy-v1"
            assert plan.feature == "chat"
            assert plan.plan == "free"


@pytest.mark.asyncio
async def test_natal_convergence_nominal():
    """Test Story 66.20: natal family also enforces assembly."""
    gateway = LLMGateway()

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal_interpretation",
            feature="natal",
            subfeature="natal_interpretation",
            plan="premium",
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        flags=ExecutionFlags(),
        user_id=1,
        request_id="req-3",
        trace_id="tr-3",
    )

    db = MagicMock(spec=Session)

    with patch(
        "app.llm_orchestration.services.assembly_registry.AssemblyRegistry.get_active_config_sync"
    ) as mock_get:
        mock_get.return_value = None

        with pytest.raises(GatewayConfigError) as exc:
            await gateway._resolve_plan(request, db=db)

        assert "Mandatory assembly missing for nominal natal family" in str(exc.value)

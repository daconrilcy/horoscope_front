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

        # Message changed in Story 66.29
        assert "Mandatory assembly missing for supported chat family" in str(exc.value)


@pytest.mark.asyncio
async def test_allow_legacy_fallback_for_deprecated_use_case():
    """
    Test Story 66.20: legacy fallback is now BLOCKED for supported features (Story 66.29).
    We test that it raises GatewayConfigError instead of allowing it.
    """
    gateway = LLMGateway()

    # "chat" is in DEPRECATED_USE_CASE_MAPPING and is a supported feature
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="chat",  # deprecated key
            feature="chat",   # Explicitly set feature to trigger perimeter check
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        flags=ExecutionFlags(skip_common_context=True),
        user_id=1,
        request_id="req-2",
        trace_id="tr-2",
    )

    db = MagicMock(spec=Session)

    with patch(
        "app.llm_orchestration.services.assembly_registry.AssemblyRegistry.get_active_config_sync"
    ) as mock_get:
        mock_get.return_value = None

        # This should now RAISE GatewayConfigError because chat is a supported feature
        with pytest.raises(GatewayConfigError) as exc:
            await gateway._resolve_plan(request, db=db)
        
        assert "Mandatory assembly missing for supported chat family" in str(exc.value)


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

        # Message changed in Story 66.29
        assert "Mandatory assembly missing for supported natal family" in str(exc.value)

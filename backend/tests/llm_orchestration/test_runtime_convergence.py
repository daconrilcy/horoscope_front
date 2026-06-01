# Commentaire global: tests de convergence runtime LLM sans reactivation des chemins natals legacy.

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.domain.llm.runtime.contracts import (
    ExecutionContext,
    ExecutionFlags,
    ExecutionUserInput,
    GatewayConfigError,
    LLMExecutionRequest,
    UnknownUseCaseError,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import LlmPromptVersionModel, PromptStatus


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
        "app.domain.llm.configuration.assembly_registry.AssemblyRegistry.get_active_config_sync"
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
            feature="chat",  # Explicitly set feature to trigger perimeter check
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
        "app.domain.llm.configuration.assembly_registry.AssemblyRegistry.get_active_config_sync"
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
        "app.domain.llm.configuration.assembly_registry.AssemblyRegistry.get_active_config_sync"
    ) as mock_get:
        mock_get.return_value = None

        with pytest.raises(GatewayConfigError) as exc:
            await gateway._resolve_plan(request, db=db)

        # Message changed in Story 66.29
        assert "Mandatory assembly missing for supported natal family" in str(exc.value)


@pytest.mark.asyncio
async def test_natal_bootstrap_fallback_rejects_deleted_short_generation(db):
    """Le bootstrap local ne doit plus rendre executable la generation short legacy."""
    gateway = LLMGateway()

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="natal_interpretation_short",
            feature="natal",
            subfeature="interpretation",
            plan="free",
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        flags=ExecutionFlags(skip_common_context=True),
        user_id=1,
        request_id="req-bootstrap",
        trace_id="tr-bootstrap",
    )

    with pytest.raises(UnknownUseCaseError, match="natal_interpretation_short"):
        await gateway._resolve_plan(request, db=db)


def test_natal_basic_interpretation_seed_is_not_published_on_legacy_contract(db) -> None:
    """Le bootstrap ne publie plus Basic sur l'ancien contrat natal_interpretation."""
    from app.ops.llm.bootstrap.seed_66_20_taxonomy import seed_66_20_taxonomy

    db.add(
        LlmPersonaModel(
            name="Persona test",
            description="Persona de test",
            tone="direct",
            verbosity="medium",
            enabled=True,
        )
    )
    db.add_all(
        [
            LlmPromptVersionModel(
                use_case_key="natal_interpretation",
                developer_prompt="Theme complet {{llm_astrology_input_v1}}",
                status=PromptStatus.PUBLISHED,
                created_by="test",
            ),
            LlmOutputSchemaModel(
                name="AstroResponse_v1",
                json_schema={"type": "object"},
                version=1,
            ),
            LlmOutputSchemaModel(
                name="AstroResponse_v3",
                json_schema={"type": "object"},
                version=3,
            ),
        ]
    )
    db.commit()

    seed_66_20_taxonomy(db)

    basic = (
        db.query(PromptAssemblyConfigModel)
        .filter(
            PromptAssemblyConfigModel.feature == "natal",
            PromptAssemblyConfigModel.subfeature == "interpretation",
            PromptAssemblyConfigModel.plan == "basic",
            PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
        )
        .one_or_none()
    )

    premium = (
        db.query(PromptAssemblyConfigModel)
        .filter(
            PromptAssemblyConfigModel.feature == "natal",
            PromptAssemblyConfigModel.subfeature == "interpretation",
            PromptAssemblyConfigModel.plan == "premium",
            PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
        )
        .one()
    )

    assert basic is None
    assert premium.feature_template.use_case_key == "natal_interpretation"
    assert premium.output_schema is not None
    assert premium.output_schema.name == "AstroResponse_v3"
    assert premium.output_schema.version == 3

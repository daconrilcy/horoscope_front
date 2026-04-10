from unittest.mock import MagicMock, patch

import pytest

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionContext,
    ExecutionUserInput,
    FallbackType,
    GatewayError,
    LLMExecutionRequest,
    UseCaseConfig,
)
from app.llm_orchestration.services.fallback_governance import FallbackGovernanceRegistry


@pytest.fixture
def gateway():
    return LLMGateway()


@pytest.mark.asyncio
async def test_governance_blocks_use_case_first_on_closed_family(gateway):
    """
    AC3: Sur les familles nominales fermées (ex: chat), le fallback use_case-first est interdit.
    """
    with pytest.raises(GatewayError) as exc:
        FallbackGovernanceRegistry.track_fallback(
            FallbackType.USE_CASE_FIRST,
            call_site="resolve_config:chat_astrologer",
            feature="chat",
            is_nominal=True,
        )

    assert "Usage du fallback 'use_case_first' interdit pour la famille 'chat'" in str(exc.value)


@pytest.mark.asyncio
async def test_governance_blocks_narrator_legacy_for_horoscope_daily():
    """
    AC8: Le narrator legacy est interdit pour horoscope_daily.
    """
    from app.prediction.llm_narrator import LLMNarrator

    narrator = LLMNarrator()

    with pytest.raises(GatewayError) as exc:
        await narrator.narrate(
            time_windows=[],
            common_context=MagicMock(),
        )

    # Message exact : "Usage du fallback 'narrator_legacy' interdit
    # pour la famille 'horoscope_daily'"
    expected = "Usage du fallback 'narrator_legacy' interdit pour la famille 'horoscope_daily'"
    assert expected in str(exc.value)


@pytest.mark.asyncio
async def test_governance_telemetry_emission():
    """
    Vérifie que l'usage d'un fallback autorisé émet bien la télémétrie.
    """
    with patch(
        "app.llm_orchestration.services.fallback_governance.increment_counter"
    ) as mock_increment:
        # On utilise un feature autorisé pour ne pas lever d'exception
        FallbackGovernanceRegistry.track_fallback(
            FallbackType.LEGACY_WRAPPER,
            call_site="test_site",
            feature="other_allowed",
            is_nominal=False,
        )

        mock_increment.assert_called_once()
        args, kwargs = mock_increment.call_args
        assert args[0] == "llm_gateway_fallback_usage_total"
        assert kwargs["labels"]["fallback_type"] == "legacy_wrapper"
        assert kwargs["labels"]["status"] == "transitoire"


@pytest.mark.asyncio
async def test_governance_allows_transitory_fallback_on_permitted_perimeter(gateway):
    """
    Vérifie qu'un fallback transitoire est autorisé s'il n'est pas sur une famille interdite.
    """
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="any_case",
            feature="other_family",  # NOT in closed families -> TRANSITORY
            locale="fr-FR",
        ),
        context=ExecutionContext(),
        request_id="test-gov-2",
        trace_id="trace-gov-2",
    )

    # Mock config correct pour éviter les erreurs Pydantic et de policy
    mock_config = UseCaseConfig(
        model="gpt-4o",
        temperature=0.7,
        max_output_tokens=1000,
        system_core_key="default_v1",
        developer_prompt="test prompt",
        prompt_version_id="stub-v1",
        safety_profile="astrology",
    )

    with patch(
        "app.llm_orchestration.services.assembly_registry.AssemblyRegistry.get_active_config_sync",
        return_value=None,
    ):
        with patch.object(gateway, "_resolve_config", return_value=mock_config):
            # No mock on track_fallback here: we want to check it doesn't raise
            # because 'other_family' makes use_case_first TRANSITORY
            try:
                await gateway._resolve_plan(request, db=MagicMock())
            except GatewayError as e:
                pytest.fail(f"GatewayError raised unexpectedly for non-forbidden family: {e}")
            except Exception:
                pass


@pytest.mark.asyncio
async def test_governance_blocks_to_remove_on_nominal_path():
    """
    AC6: Les fallbacks à retirer sont interdits sur les parcours nominaux.
    """
    # En développement, cela doit bloquer
    with patch("app.core.config.settings.app_env", "development"):
        with pytest.raises(GatewayError) as exc:
            FallbackGovernanceRegistry.track_fallback(
                FallbackType.EXECUTION_CONFIG_ADMIN,
                call_site="test_nominal",
                feature="any",
                is_nominal=True,
            )
        msg = "Dépendance nominale au fallback 'execution_config_admin' interdite"
        assert msg in str(exc.value)

    # En production, cela doit AUSSI bloquer (AC6 strict)
    with patch("app.core.config.settings.app_env", "production"):
        with pytest.raises(GatewayError) as exc:
            FallbackGovernanceRegistry.track_fallback(
                FallbackType.EXECUTION_CONFIG_ADMIN,
                call_site="test_prod_nominal",
                feature="any",
                is_nominal=True,
            )
        msg = "Dépendance nominale au fallback 'execution_config_admin' interdite"
        assert msg in str(exc.value)


@pytest.mark.asyncio
async def test_governance_blocks_test_local_in_prod():
    """
    AC9: Le fallback de test local est interdit en production.
    """
    with patch("app.core.config.settings.app_env", "production"):
        with pytest.raises(GatewayError) as exc:
            FallbackGovernanceRegistry.track_fallback(
                FallbackType.TEST_LOCAL,
                call_site="test_prod",
                feature="any",
                is_nominal=False,
            )
        assert "Usage du fallback 'test_local' strictement interdit en production" in str(exc.value)


@pytest.mark.asyncio
async def test_governance_critical_log_on_db_error_in_prod():
    """
    AC9: Une erreur DB masquée en production doit déclencher un log critique.
    """
    with patch("app.core.config.settings.app_env", "production"):
        # Import logger from the module to patch it correctly
        from app.llm_orchestration.services.fallback_governance import logger as gov_logger

        with patch.object(gov_logger, "critical") as mock_log:
            FallbackGovernanceRegistry.track_fallback(
                FallbackType.NATAL_NO_DB,
                call_site="test_db_crash",
                feature="natal",
                is_nominal=False,  # False means it's an error, not intentional stub
            )
            mock_log.assert_called_once()
            args, _ = mock_log.call_args
            assert "governance_critical_prod_database_error_masked" in args[0]


@pytest.mark.asyncio
async def test_governance_infers_family_from_call_site():
    """
    AC3: La famille doit être inférée si feature est None (évite contournement).
    """
    with patch("app.core.config.settings.app_env", "development"):
        with pytest.raises(GatewayError) as exc:
            # feature=None, but call_site has 'horoscope_daily'
            FallbackGovernanceRegistry.track_fallback(
                FallbackType.USE_CASE_FIRST,
                call_site="resolve_config:horoscope_daily",
                feature=None,
                is_nominal=True,
            )
        expected = "Usage du fallback 'use_case_first' interdit pour la famille 'horoscope_daily'"
        assert expected in str(exc.value)


@pytest.mark.asyncio
async def test_governance_telemetry_emitted_even_on_block():
    """
    Medium: La télémétrie doit être émise même si l'appel est bloqué par une exception.
    """
    with patch(
        "app.llm_orchestration.services.fallback_governance.increment_counter"
    ) as mock_increment:
        # On force un blocage via TO_REMOVE + is_nominal
        with pytest.raises(GatewayError):
            FallbackGovernanceRegistry.track_fallback(
                FallbackType.EXECUTION_CONFIG_ADMIN,
                call_site="test_telemetry_block",
                feature="any",
                is_nominal=True,
            )
        # increment_counter doit avoir été appelé AVANT de lever GatewayError
        mock_increment.assert_called_once()
        args, kwargs = mock_increment.call_args
        assert args[0] == "llm_gateway_fallback_usage_total"
        assert kwargs["labels"]["fallback_type"] == "execution_config_admin"

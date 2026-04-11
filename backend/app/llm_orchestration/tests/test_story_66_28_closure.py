import pytest
from sqlalchemy.orm import Session
from unittest.mock import AsyncMock, patch

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionUserInput, 
    LLMExecutionRequest, 
    GatewayResult, 
    GatewayMeta, 
    UsageInfo
)

@pytest.mark.asyncio
async def test_daily_path_is_nominal_canonical(db: Session):
    """
    Story 66.28 AC5: Verify that the default daily path is now nominal_canonical.
    This proves that absorption of daily_prediction into horoscope_daily is complete.
    """
    # Seed required data
    from app.infra.db.models.llm_persona import LlmPersonaModel
    from app.llm_orchestration.seeds.seed_horoscope_narrator_assembly import (
        seed_horoscope_narrator_assembly,
    )

    # Need at least one persona for the assembly to seed correctly
    if not db.query(LlmPersonaModel).first():
        p = LlmPersonaModel(
            name="Luna", description="...", tone="...", verbosity="...", enabled=True
        )
        db.add(p)
        db.commit()

    seed_horoscope_narrator_assembly(db)

    gateway = LLMGateway()

    # Request without explicit feature/subfeature/plan (mimicking old daily_prediction default)
    # But after 66.28, the adapter sends horoscope_daily/narration/free.
    # We test the gateway's ability to handle 'daily_prediction' as a nominal alias
    # if it ever arrives.

    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(
            use_case="daily_prediction",  # Old use case
            feature=None,                 # No feature passed (legacy style)
            plan=None,                    # Old plan (implicit)
        ),
        request_id="req-66-28",
        trace_id="tr-66-28",
    )

    # Mock the actual provider call to avoid OpenAI usage
    with patch.object(gateway, "_call_provider", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = GatewayResult(
            use_case="daily_prediction",
            request_id="req-66-28",
            trace_id="tr-66-28",
            raw_output='{"daily_synthesis": "..."}',
            structured_output={},
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=0, model="test"),
        )

        result = await gateway.execute_request(request, db=db)

        # 1. Verify Taxonomy redirection
        assert result.meta.feature == "horoscope_daily"
        assert result.meta.plan == "free"

        # 2. Verify Governance (The real closure proof)
        assert result.meta.obs_snapshot.pipeline_kind == "nominal_canonical"
        assert result.meta.obs_snapshot.fallback_kind.value == "deprecated_use_case"

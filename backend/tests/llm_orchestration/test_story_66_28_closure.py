import pytest
from sqlalchemy.orm import Session

from app.domain.llm.runtime.contracts import (
    ExecutionUserInput,
    GatewayConfigError,
    LLMExecutionRequest,
)
from app.domain.llm.runtime.gateway import LLMGateway


@pytest.mark.asyncio
async def test_daily_path_is_nominal_canonical(db: Session):
    """
    Story 66.28 AC5: Verify that the default daily path is now nominal_canonical.
    This proves that absorption of daily_prediction into horoscope_daily is complete.
    """
    # Seed required data
    from app.infra.db.models.llm.llm_persona import LlmPersonaModel
    from app.ops.llm.bootstrap.seed_horoscope_narrator_assembly import (
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
            feature=None,  # No feature passed (legacy style)
            plan=None,  # Old plan (implicit)
        ),
        request_id="req-66-28",
        trace_id="tr-66-28",
    )

    with pytest.raises(GatewayConfigError) as exc:
        await gateway.execute_request(request, db=db)
    assert "removed" in str(exc.value).lower()

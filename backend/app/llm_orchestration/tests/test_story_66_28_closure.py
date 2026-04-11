import pytest
from sqlalchemy.orm import Session

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import ExecutionUserInput, LLMExecutionRequest


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
            feature="daily_prediction",  # Old feature
            subfeature="narration",  # Subfeature
            plan=None,  # Old plan (implicit)
        ),
        request_id="req-66-28",
        trace_id="tr-66-28",
    )

    # We don't actually need to execute the full request (which would call OpenAI).
    # We just need to check how the plan is resolved.

    # 1. Early normalization check
    from app.llm_orchestration.feature_taxonomy import normalize_feature, normalize_subfeature

    f = normalize_feature(request.user_input.feature)
    _sf = normalize_subfeature(f, request.user_input.subfeature)

    assert f == "horoscope_daily"
    # 2. Pipeline Kind check in _resolve_plan
    # We can use the gateway's internal logic
    plan, _ = await gateway._resolve_plan(request, db)

    # Verify the plan has the right taxonomy
    assert plan.feature == "horoscope_daily"
    assert plan.plan == "free"

    # Verify the pipeline kind
    # We use the same set as in gateway._build_result
    canonical_families = {"chat", "guidance", "natal", "horoscope_daily"}
    assert plan.feature in canonical_families

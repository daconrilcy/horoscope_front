import uuid

import pytest
from sqlalchemy import select

from app.infra.db.models.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo
from app.llm_orchestration.services.observability_service import (
    compute_input_hash,
    count_evidence_warnings,
    log_call,
)


@pytest.mark.asyncio
async def test_compute_input_hash_is_reproducible():
    input1 = {"b": 2, "a": 1}
    input2 = {"a": 1, "b": 2}

    hash1 = compute_input_hash(input1)
    hash2 = compute_input_hash(input2)

    assert hash1 == hash2
    assert len(hash1) == 64


def test_count_evidence_warnings():
    # Valid evidence
    out1 = {"evidence": ["SUN_IN_ARIES", "MOON_IN_TAURUS"]}
    assert count_evidence_warnings(out1) == 0

    # Invalid evidence (free text)
    out2 = {"evidence": ["Sun is in Aries", "MOON_IN_TAURUS"]}
    assert count_evidence_warnings(out2) == 1

    # Non-list evidence
    assert count_evidence_warnings({"evidence": "not a list"}) == 0

    # Missing evidence
    assert count_evidence_warnings({}) == 0


@pytest.mark.asyncio
async def test_log_call_persists_to_db(db):
    use_case = "test_case"
    request_id = f"req-{uuid.uuid4()}"
    trace_id = "trace-123"
    user_input = {"message": "hello"}

    result = GatewayResult(
        use_case=use_case,
        request_id=request_id,
        trace_id=trace_id,
        raw_output="raw",
        structured_output={"message": "hi"},
        usage=UsageInfo(
            input_tokens=10, output_tokens=5, total_tokens=15, estimated_cost_usd=0.001
        ),
        meta=GatewayMeta(latency_ms=100, model="gpt-test", validation_status="valid"),
    )

    await log_call(db, use_case, request_id, trace_id, user_input, result=result)

    # Verify in DB
    stmt = select(LlmCallLogModel).where(LlmCallLogModel.request_id == request_id)
    log = db.execute(stmt).scalar_one()

    assert log.use_case == use_case
    assert log.latency_ms == 100
    assert log.validation_status == "valid"
    assert log.input_hash == compute_input_hash(user_input)
    assert log.cost_usd_estimated == 0.001


@pytest.mark.asyncio
async def test_log_call_on_error(db):
    request_id = f"req-err-{uuid.uuid4()}"
    user_input = {"message": "fail"}

    await log_call(db, "fail_case", request_id, "trace-err", user_input, error=ValueError("boom"))

    stmt = select(LlmCallLogModel).where(LlmCallLogModel.request_id == request_id)
    log = db.execute(stmt).scalar_one()

    assert log.validation_status == LlmValidationStatus.ERROR

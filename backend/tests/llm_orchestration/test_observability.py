import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.ai_engine.exceptions import UpstreamCircuitOpenError
from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.domain.llm.runtime.observability_service import (
    compute_input_hash,
    count_evidence_warnings,
    log_call,
)
from app.infra.db.models.llm.llm_observability import (
    LlmCallLogModel,
    LlmCallLogOperationalMetadataModel,
    LlmValidationStatus,
)
from app.infra.db.models.user import UserModel


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

    metadata = db.execute(
        select(LlmCallLogOperationalMetadataModel).where(
            LlmCallLogOperationalMetadataModel.call_log_id == log.id
        )
    ).scalar_one()
    assert metadata.call_log_id == log.id
    assert metadata.executed_provider == log.executed_provider


@pytest.mark.asyncio
async def test_log_call_on_error(db):
    request_id = f"req-err-{uuid.uuid4()}"
    user_input = {"message": "fail"}

    await log_call(db, "fail_case", request_id, "trace-err", user_input, error=ValueError("boom"))

    stmt = select(LlmCallLogModel).where(LlmCallLogModel.request_id == request_id)
    log = db.execute(stmt).scalar_one()

    assert log.validation_status == LlmValidationStatus.ERROR


@pytest.mark.asyncio
async def test_log_call_on_error_persists_provider_runtime_metadata(db):
    request_id = f"req-runtime-err-{uuid.uuid4()}"
    error = UpstreamCircuitOpenError(provider="openai", family="chat")
    error._executed_provider_mode = "circuit_open"  # type: ignore[attr-defined]
    error._attempt_count = 0  # type: ignore[attr-defined]
    error._provider_error_code = error.error_type  # type: ignore[attr-defined]
    error._breaker_state = "open"  # type: ignore[attr-defined]
    error._breaker_scope = "openai:chat"  # type: ignore[attr-defined]

    await log_call(
        db,
        "chat_astrologer",
        request_id,
        "trace-runtime-err",
        {"message": "bonjour"},
        error=error,
    )

    stmt = select(LlmCallLogModel).where(LlmCallLogModel.request_id == request_id)
    log = db.execute(stmt).scalar_one()

    assert log.validation_status == LlmValidationStatus.ERROR
    assert log.executed_provider_mode == "circuit_open"
    assert log.attempt_count == 0
    assert log.provider_error_code == "UPSTREAM_CIRCUIT_OPEN"
    assert log.breaker_state == "open"
    assert log.breaker_scope == "openai:chat"

    metadata = db.execute(
        select(LlmCallLogOperationalMetadataModel).where(
            LlmCallLogOperationalMetadataModel.call_log_id == log.id
        )
    ).scalar_one()
    assert metadata.executed_provider_mode == "circuit_open"
    assert metadata.provider_error_code == "UPSTREAM_CIRCUIT_OPEN"
    assert metadata.breaker_state == "open"


@pytest.mark.asyncio
async def test_log_call_failure_does_not_rollback_outer_transaction(db):
    request_id = f"req-fk-{uuid.uuid4()}"
    user = UserModel(
        email=f"observability-{uuid.uuid4()}@example.com",
        password_hash="test-hash",
        role="user",
    )
    db.add(user)
    db.flush()

    result = GatewayResult(
        use_case="chat_astrologer",
        request_id=request_id,
        trace_id="trace-fk",
        raw_output="raw",
        structured_output={"message": "hi"},
        usage=UsageInfo(
            input_tokens=10, output_tokens=5, total_tokens=15, estimated_cost_usd=0.001
        ),
        meta=GatewayMeta(
            latency_ms=100,
            model="gpt-test",
            validation_status="valid",
            prompt_version_id=str(uuid.uuid4()),
        ),
    )

    original_flush = db.flush

    def failing_flush(*args, **kwargs):
        raise IntegrityError("insert into llm_call_logs", {}, Exception("fk failure"))

    db.flush = failing_flush  # type: ignore[method-assign]
    try:
        await log_call(
            db,
            "chat_astrologer",
            request_id,
            "trace-fk",
            {"message": "hello"},
            result=result,
        )
    finally:
        db.flush = original_flush  # type: ignore[method-assign]

    persisted_user = db.execute(
        select(UserModel).where(UserModel.id == user.id)
    ).scalar_one_or_none()
    persisted_log = db.execute(
        select(LlmCallLogModel).where(LlmCallLogModel.request_id == request_id)
    ).scalar_one_or_none()

    assert persisted_user is not None
    assert persisted_log is None

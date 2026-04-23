from __future__ import annotations

import json
import os
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import APITimeoutError, InternalServerError, RateLimitError

from app.ai_engine.config import ai_engine_settings
from app.ai_engine.exceptions import RetryBudgetExhaustedError, UpstreamCircuitOpenError
from app.domain.llm.runtime.contracts import (
    ContextCompensationStatus,
    ExecutionObservabilitySnapshot,
    ExecutionPathKind,
    GatewayMeta,
    GatewayResult,
    MaxTokensSource,
    UsageInfo,
)
from app.domain.llm.runtime.provider_runtime_manager import ProviderRuntimeManager
from app.infra.providers.llm.circuit_breaker import (
    get_circuit_breaker,
    reset_circuit_breakers,
)


@dataclass(frozen=True)
class ChaosOutcome:
    scenario: str
    failure_type: str
    invariant: str
    passed: bool
    observed: dict[str, Any]


_RUN_UNIQUE_REPORT_PATH: Path | None = None
_RUN_EFFECTIVE_REPORT_PATH: Path | None = None


def _build_obs_snapshot(
    *,
    attempt_count: int,
    provider_error_code: str | None = None,
    breaker_state: str | None = None,
    breaker_scope: str | None = None,
    active_snapshot_id: uuid.UUID | None = None,
    active_snapshot_version: str | None = None,
    manifest_entry_id: str | None = None,
) -> ExecutionObservabilitySnapshot:
    return ExecutionObservabilitySnapshot(
        pipeline_kind="nominal_canonical",
        execution_path_kind=ExecutionPathKind.CANONICAL_ASSEMBLY,
        fallback_kind=None,
        requested_provider="openai",
        resolved_provider="openai",
        executed_provider="openai",
        context_quality="full",
        context_compensation_status=ContextCompensationStatus.NOT_NEEDED,
        max_output_tokens_source=MaxTokensSource.EXECUTION_PROFILE,
        max_output_tokens_final=900,
        executed_provider_mode="nominal",
        attempt_count=attempt_count,
        provider_error_code=provider_error_code,
        breaker_state=breaker_state,
        breaker_scope=breaker_scope,
        active_snapshot_id=active_snapshot_id,
        active_snapshot_version=active_snapshot_version,
        manifest_entry_id=manifest_entry_id,
    )


def _result(
    raw_output: str = "ok",
    *,
    obs_snapshot: ExecutionObservabilitySnapshot | None = None,
) -> GatewayResult:
    return GatewayResult(
        use_case="chaos_test",
        request_id="req-chaos",
        trace_id="trace-chaos",
        raw_output=raw_output,
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="gpt-4o-mini", obs_snapshot=obs_snapshot),
    )


def _build_report(outcomes: list[ChaosOutcome]) -> list[dict[str, Any]]:
    return [
        {
            "scenario": outcome.scenario,
            "failure_type": outcome.failure_type,
            "invariant": outcome.invariant,
            "passed": outcome.passed,
            "observed": outcome.observed,
        }
        for outcome in outcomes
    ]


def _observed_from_error(err: Exception) -> dict[str, Any]:
    return {
        "attempt_count": getattr(err, "_attempt_count", None),
        "provider_error_code": getattr(err, "_provider_error_code", None),
        "breaker_state": getattr(err, "_breaker_state", None),
        "breaker_scope": getattr(err, "_breaker_scope", None),
        "active_snapshot_id": None,
        "active_snapshot_version": None,
        "manifest_entry_id": None,
    }


def _observed_from_result(result: GatewayResult) -> dict[str, Any]:
    snapshot = result.meta.obs_snapshot
    return {
        "attempt_count": result.meta.attempt_count,
        "provider_error_code": result.meta.provider_error_code,
        "breaker_state": result.meta.breaker_state,
        "breaker_scope": result.meta.breaker_scope,
        "active_snapshot_id": str(snapshot.active_snapshot_id) if snapshot else None,
        "active_snapshot_version": snapshot.active_snapshot_version if snapshot else None,
        "manifest_entry_id": snapshot.manifest_entry_id if snapshot else None,
    }


def _resolve_report_path() -> Path:
    if os.getenv("CHAOS_REPORT_PATH"):
        return Path(os.environ["CHAOS_REPORT_PATH"])
    global _RUN_UNIQUE_REPORT_PATH
    if _RUN_UNIQUE_REPORT_PATH is not None:
        return _RUN_UNIQUE_REPORT_PATH
    run_id = f"pid-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    backend_root = Path(__file__).resolve().parents[2]
    _RUN_UNIQUE_REPORT_PATH = (
        backend_root / ".pytest_cache" / "chaos" / f"story-66-43-chaos-report-{run_id}.json"
    )
    return _RUN_UNIQUE_REPORT_PATH


def _candidate_report_paths() -> list[Path]:
    primary_path = _resolve_report_path()
    fallback_path = Path(tempfile.gettempdir()) / "horoscope_front" / "chaos" / primary_path.name
    return [primary_path, fallback_path]


def _emit_report(report: list[dict[str, Any]]) -> Path:
    global _RUN_EFFECTIVE_REPORT_PATH
    payload = json.dumps(
        {
            "story": "66.43",
            "report_kind": "provider_runtime_chaos_invariants",
            "scenario_count": len(report),
            "all_passed": all(item["passed"] for item in report),
            "scenarios": report,
        },
        ensure_ascii=True,
        indent=2,
    )
    candidate_paths = [_RUN_EFFECTIVE_REPORT_PATH] if _RUN_EFFECTIVE_REPORT_PATH else []
    candidate_paths.extend(
        path for path in _candidate_report_paths() if path not in candidate_paths
    )
    last_error: OSError | None = None
    for output_path in candidate_paths:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(payload, encoding="utf-8")
            _RUN_EFFECTIVE_REPORT_PATH = output_path
            return output_path
        except OSError as exc:
            last_error = exc
            continue
    if last_error is not None:
        raise last_error
    return _resolve_report_path()


def _load_existing_report() -> dict[str, Any]:
    candidate_paths = [_RUN_EFFECTIVE_REPORT_PATH] if _RUN_EFFECTIVE_REPORT_PATH else []
    candidate_paths.extend(
        path for path in _candidate_report_paths() if path not in candidate_paths
    )
    for report_path in candidate_paths:
        if report_path.exists():
            return json.loads(report_path.read_text(encoding="utf-8"))
    return {
        "story": "66.43",
        "report_kind": "provider_runtime_chaos_invariants",
        "scenario_count": 0,
        "all_passed": True,
        "scenarios": [],
    }


def _record_outcomes(outcomes: list[ChaosOutcome]) -> Path:
    existing = _load_existing_report()
    by_scenario: dict[str, dict[str, Any]] = {
        item["scenario"]: item for item in existing.get("scenarios", [])
    }
    for item in _build_report(outcomes):
        by_scenario[item["scenario"]] = item
    merged = sorted(by_scenario.values(), key=lambda item: item["scenario"])
    return _emit_report(merged)


@pytest.fixture(autouse=True)
def _reset_runtime_state() -> None:
    reset_circuit_breakers()


@pytest.fixture
def _deterministic_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai_engine_settings, "max_retries", 2)
    monkeypatch.setattr(ai_engine_settings, "retry_base_delay_ms", 1)
    monkeypatch.setattr(ai_engine_settings, "retry_max_delay_ms", 1)


@pytest.mark.asyncio
async def test_story_66_43_chaos_matrix_minimum_coverage(
    _deterministic_runtime: None,
) -> None:
    outcomes: list[ChaosOutcome] = []
    manager = ProviderRuntimeManager()

    with patch("asyncio.sleep", new_callable=AsyncMock):
        # rate_limit -> retry budget exhausted
        rate_limit = RateLimitError(message="rate limited", response=MagicMock(), body={})
        manager.client.execute = AsyncMock(side_effect=rate_limit)  # type: ignore[method-assign]
        with pytest.raises(RetryBudgetExhaustedError) as rl_exc:
            await manager.execute_with_resilience(messages=[], model="m", family="chat")
        outcome = ChaosOutcome(
            scenario="rate_limit_budget_exhausted",
            failure_type="rate_limit",
            invariant="retry budget exhausted sans provider externe",
            passed=getattr(rl_exc.value, "_attempt_count", 0) == 3,
            observed=_observed_from_error(rl_exc.value),
        )
        outcomes.append(outcome)

        # timeout -> retry budget exhausted
        manager.client.execute = AsyncMock(  # type: ignore[method-assign]
            side_effect=APITimeoutError(request=MagicMock())
        )
        with pytest.raises(RetryBudgetExhaustedError) as timeout_exc:
            await manager.execute_with_resilience(messages=[], model="m", family="guidance")
        outcome = ChaosOutcome(
            scenario="timeout_budget_exhausted",
            failure_type="timeout",
            invariant="classification timeout + retries bornes",
            passed=getattr(timeout_exc.value, "_attempt_count", 0) == 3,
            observed=_observed_from_error(timeout_exc.value),
        )
        outcomes.append(outcome)
        outcome = ChaosOutcome(
            scenario="retry_budget_exhausted_explicit",
            failure_type="retry_budget_exhausted",
            invariant="le budget de retries borne strictement les tentatives",
            passed=getattr(timeout_exc.value, "_attempt_count", 0)
            == ai_engine_settings.max_retries + 1,
            observed=_observed_from_error(timeout_exc.value),
        )
        outcomes.append(outcome)

        # 5xx -> retry budget exhausted
        manager.client.execute = AsyncMock(  # type: ignore[method-assign]
            side_effect=InternalServerError(
                message="upstream 5xx", response=MagicMock(), body={"error": {"message": "boom"}}
            )
        )
        with pytest.raises(RetryBudgetExhaustedError) as server_exc:
            await manager.execute_with_resilience(messages=[], model="m", family="natal")
        outcome = ChaosOutcome(
            scenario="server_error_budget_exhausted",
            failure_type="5xx",
            invariant="classification provider 5xx retryable puis budget exhausted",
            passed=getattr(server_exc.value, "_attempt_count", 0) == 3,
            observed=_observed_from_error(server_exc.value),
        )
        outcomes.append(outcome)

    # breaker open après échecs répétés sur une même famille
    failing_manager = ProviderRuntimeManager()
    failing_manager.client.execute = AsyncMock(  # type: ignore[method-assign]
        side_effect=APITimeoutError(request=MagicMock())
    )
    with patch("asyncio.sleep", new_callable=AsyncMock):
        for _ in range(ai_engine_settings.circuit_breaker_failure_threshold):
            with pytest.raises(RetryBudgetExhaustedError):
                await failing_manager.execute_with_resilience(
                    messages=[],
                    model="m",
                    family="horoscope_daily",
                )

    with pytest.raises(UpstreamCircuitOpenError) as open_exc:
        await failing_manager.execute_with_resilience(
            messages=[], model="m", family="horoscope_daily"
        )
    outcome = ChaosOutcome(
        scenario="breaker_open_after_repeated_failures",
        failure_type="breaker_open",
        invariant="fermeture stricte du nominal quand breaker ouvert",
        passed=getattr(open_exc.value, "_attempt_count", None) == 0
        and getattr(open_exc.value, "_breaker_state", None) == "open",
        observed=_observed_from_error(open_exc.value),
    )
    outcomes.append(outcome)

    report = _build_report(outcomes)
    report_path = _record_outcomes(outcomes)
    persisted_report = json.loads(report_path.read_text(encoding="utf-8"))

    assert len(report) >= 5
    assert all(item["passed"] for item in report)
    assert {item["failure_type"] for item in report} >= {
        "rate_limit",
        "timeout",
        "5xx",
        "breaker_open",
    }
    assert persisted_report["report_kind"] == "provider_runtime_chaos_invariants"
    assert persisted_report["scenario_count"] >= 5
    assert persisted_report["all_passed"] is True
    assert {item["scenario"] for item in persisted_report["scenarios"]} >= {
        item["scenario"] for item in report
    }


@pytest.mark.asyncio
async def test_story_66_43_partial_failure_then_recovery_keeps_consistent_metadata(
    _deterministic_runtime: None,
) -> None:
    snapshot_id = uuid.UUID("f8ab2498-7f2c-48e9-90d2-4da65f4f1f88")
    obs_snapshot = _build_obs_snapshot(
        attempt_count=2,
        active_snapshot_id=snapshot_id,
        active_snapshot_version="snapshot-v66-43",
        manifest_entry_id="chat:astrologer:premium",
    )
    manager = ProviderRuntimeManager()
    manager.client.execute = AsyncMock(  # type: ignore[method-assign]
        side_effect=[
            APITimeoutError(request=MagicMock()),
            (_result("recovered", obs_snapshot=obs_snapshot), {"x-request-id": "r-ok"}),
        ]
    )

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await manager.execute_with_resilience(
            messages=[{"role": "user", "content": "bonjour"}],
            model="m",
            family="chat",
        )

    assert result.raw_output == "recovered"
    assert result.meta.attempt_count == 2
    assert result.meta.breaker_state == "closed"
    assert result.meta.breaker_scope == "openai:chat"
    assert result.meta.executed_provider_mode == "nominal"
    observed = _observed_from_result(result)
    assert observed["active_snapshot_id"] == str(snapshot_id)
    assert observed["active_snapshot_version"] == "snapshot-v66-43"
    assert observed["manifest_entry_id"] == "chat:astrologer:premium"
    outcome = ChaosOutcome(
        scenario="partial_failure_then_recovery_with_snapshot_correlation",
        failure_type="recovery_with_snapshot",
        invariant="corrélation snapshot préservée en rétablissement nominal",
        passed=observed["active_snapshot_id"] == str(snapshot_id)
        and observed["active_snapshot_version"] == "snapshot-v66-43"
        and observed["manifest_entry_id"] == "chat:astrologer:premium",
        observed=observed,
    )
    _record_outcomes([outcome])


@pytest.mark.asyncio
async def test_story_66_43_configuration_error_is_not_reclassified_as_provider_incident(
    _deterministic_runtime: None,
) -> None:
    manager = ProviderRuntimeManager()
    manager.client.execute = AsyncMock(  # type: ignore[method-assign]
        side_effect=ValueError("invalid runtime configuration")
    )

    with pytest.raises(ValueError) as exc:
        await manager.execute_with_resilience(messages=[], model="m", family="chat")

    assert "invalid runtime configuration" in str(exc.value)
    # La classification ne doit pas transformer l'erreur de config en erreur provider.
    assert type(exc.value) is ValueError
    assert getattr(exc.value, "_provider_error_code", None) is None
    outcome = ChaosOutcome(
        scenario="configuration_error_not_reclassified",
        failure_type="configuration_error",
        invariant="erreur configuration non transformée en incident provider",
        passed=type(exc.value) is ValueError
        and getattr(exc.value, "_provider_error_code", None) is None,
        observed=_observed_from_error(exc.value),
    )
    _record_outcomes([outcome])


@pytest.mark.asyncio
async def test_story_66_43_retry_idempotence_and_nominal_closure(
    _deterministic_runtime: None,
) -> None:
    manager = ProviderRuntimeManager()
    manager.client.execute = AsyncMock(  # type: ignore[method-assign]
        side_effect=APITimeoutError(request=MagicMock())
    )

    with patch("asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(RetryBudgetExhaustedError) as exc:
            await manager.execute_with_resilience(messages=[], model="m", family="chat")

    # Idempotence logique: 3 tentatives = max_retries(2) + 1, pas de surcomptage.
    assert manager.client.execute.call_count == 3
    assert getattr(exc.value, "_attempt_count", None) == 3

    breaker = get_circuit_breaker(
        provider="openai",
        family="chat",
        failure_threshold=ai_engine_settings.circuit_breaker_failure_threshold,
        recovery_timeout_sec=ai_engine_settings.circuit_breaker_recovery_timeout_sec,
    )
    # Une seule failure breaker pour une exécution épuisée.
    assert len(breaker.failure_timestamps) == 1
    assert getattr(exc.value, "_breaker_scope", None) == "openai:chat"
    # Pas de réouverture fallback: mode reste nominal et provider verrouillé.
    assert getattr(exc.value, "_executed_provider_mode", None) == "nominal"
    outcome = ChaosOutcome(
        scenario="retry_idempotence_and_nominal_closure",
        failure_type="retry_idempotence",
        invariant="pas de surcomptage retries/breaker et fermeture nominale stricte",
        passed=manager.client.execute.call_count == 3
        and getattr(exc.value, "_attempt_count", None) == 3
        and len(breaker.failure_timestamps) == 1
        and getattr(exc.value, "_executed_provider_mode", None) == "nominal",
        observed=_observed_from_error(exc.value),
    )
    report_path = _record_outcomes([outcome])
    persisted_report = json.loads(report_path.read_text(encoding="utf-8"))
    expected_scenarios = {
        "rate_limit_budget_exhausted",
        "timeout_budget_exhausted",
        "retry_budget_exhausted_explicit",
        "server_error_budget_exhausted",
        "breaker_open_after_repeated_failures",
        "partial_failure_then_recovery_with_snapshot_correlation",
        "configuration_error_not_reclassified",
        "retry_idempotence_and_nominal_closure",
    }
    assert {item["scenario"] for item in persisted_report["scenarios"]} >= expected_scenarios

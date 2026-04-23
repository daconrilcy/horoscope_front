from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.infra.db.models.llm.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.services.auth_service import AuthService
from app.services.llm_canonical_consumption_service import (
    CanonicalConsumptionFilters,
    LlmCanonicalConsumptionService,
)


def _seed_user_id(db, email: str) -> int:
    auth = AuthService.register(db, email=email, password="admin123", role="user")
    db.commit()
    return auth.user.id


def _build_call_log(
    *,
    feature: str | None,
    subfeature: str | None,
    plan: str,
    timestamp: datetime,
    request_id: str,
    manifest_entry_id: str,
    use_case: str | None = None,
    executed_provider: str = "openai",
    active_snapshot_version: str = "release-2026-04",
    validation_status: LlmValidationStatus = LlmValidationStatus.VALID,
    tokens_in: int = 100,
    tokens_out: int = 50,
    cost_usd_estimated: float = 0.01,
    latency_ms: int = 400,
) -> LlmCallLogModel:
    resolved_use_case = use_case if use_case is not None else (feature or "unspecified")
    return LlmCallLogModel(
        id=uuid.uuid4(),
        use_case=resolved_use_case,
        feature=feature,
        subfeature=subfeature,
        plan=plan,
        provider="openai",
        model="gpt-4.1-mini",
        latency_ms=latency_ms,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd_estimated=cost_usd_estimated,
        validation_status=validation_status,
        repair_attempted=False,
        fallback_triggered=False,
        request_id=request_id,
        trace_id=f"trace-{request_id}",
        input_hash=f"hash-{request_id}",
        environment="test",
        requested_provider=executed_provider,
        resolved_provider=executed_provider,
        executed_provider=executed_provider,
        active_snapshot_version=active_snapshot_version,
        manifest_entry_id=manifest_entry_id,
        timestamp=timestamp,
    )


def test_governed_feature_alias_is_nominal_when_subfeature_maps(db_session) -> None:
    _seed_user_id(db_session, "consumption-alias-nominal@example.com")
    ts = datetime(2026, 4, 15, 10, 12, tzinfo=timezone.utc)
    db_session.add(
        _build_call_log(
            feature="natal_interpretation",
            subfeature="full",
            plan="premium",
            timestamp=ts,
            request_id="req-alias-nominal",
            manifest_entry_id="natal_interpretation:full:premium:fr-FR",
        )
    )
    db_session.commit()

    nominal = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(granularity="day", scope="nominal"),
        refresh=True,
    )
    assert len(nominal) == 1
    assert nominal[0].feature == "natal"
    assert nominal[0].subfeature == "full"
    assert nominal[0].is_legacy_residual is False


def test_null_feature_reclassifies_from_use_case_compat(db_session) -> None:
    _seed_user_id(db_session, "consumption-null-feature@example.com")
    ts = datetime(2026, 4, 15, 10, 12, tzinfo=timezone.utc)
    db_session.add(
        _build_call_log(
            feature=None,
            use_case="natal_interpretation",
            subfeature="full",
            plan="premium",
            timestamp=ts,
            request_id="req-null-feature",
            manifest_entry_id="natal:full:premium:fr-FR",
        )
    )
    db_session.commit()

    nominal = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(granularity="day", scope="nominal"),
        refresh=True,
    )
    assert len(nominal) == 1
    assert nominal[0].feature == "natal"
    assert nominal[0].is_legacy_residual is False


def test_nominal_scope_excludes_legacy_residual_and_keeps_user_dimension(db_session) -> None:
    user_id = _seed_user_id(db_session, "consumption-a@example.com")
    ts = datetime(2026, 4, 15, 10, 12, tzinfo=timezone.utc)
    nominal = _build_call_log(
        feature="natal",
        subfeature="full",
        plan="premium",
        timestamp=ts,
        request_id="req-nominal",
        manifest_entry_id="natal:full:premium:fr-FR",
    )
    legacy = _build_call_log(
        feature="natal_interpretation",
        subfeature="legacy_unknown",
        plan="free",
        timestamp=ts + timedelta(minutes=2),
        request_id="req-legacy",
        manifest_entry_id="natal_interpretation:None:free:en-US",
    )
    db_session.add(nominal)
    db_session.add(legacy)
    db_session.flush()
    db_session.add(
        UserTokenUsageLogModel(
            user_id=user_id,
            feature_code="natal",
            provider_model="gpt-4.1-mini",
            tokens_in=100,
            tokens_out=50,
            tokens_total=150,
            request_id="req-nominal",
            llm_call_log_id=nominal.id,
            created_at=ts,
        )
    )
    db_session.commit()

    result = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(granularity="day", scope="nominal"),
        refresh=True,
    )
    assert len(result) == 1
    assert result[0].feature == "natal"
    assert result[0].subfeature == "full"
    assert result[0].user_id == user_id


def test_monthly_aggregation_uses_utc_boundaries(db_session) -> None:
    _seed_user_id(db_session, "consumption-b@example.com")
    april = _build_call_log(
        feature="horoscope_daily",
        subfeature=None,
        plan="basic",
        timestamp=datetime(2026, 4, 30, 23, 59, tzinfo=timezone.utc),
        request_id="req-april",
        manifest_entry_id="horoscope_daily:None:basic:fr-FR",
    )
    may = _build_call_log(
        feature="horoscope_daily",
        subfeature=None,
        plan="basic",
        timestamp=datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc),
        request_id="req-may",
        manifest_entry_id="horoscope_daily:None:basic:fr-FR",
    )
    db_session.add(april)
    db_session.add(may)
    db_session.commit()

    result = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(granularity="month", scope="all"),
        refresh=True,
    )
    assert len(result) == 2
    assert result[0].period_start_utc == datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc)
    assert result[1].period_start_utc == datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)


def test_plan_cost_provider_snapshot_are_frozen_from_call_log(db_session) -> None:
    _seed_user_id(db_session, "consumption-c@example.com")
    db_session.add(
        _build_call_log(
            feature="chat",
            subfeature=None,
            plan="premium",
            timestamp=datetime(2026, 4, 15, 8, 0, tzinfo=timezone.utc),
            request_id="req-frozen",
            manifest_entry_id="chat:None:premium:en-US",
            executed_provider="anthropic",
            active_snapshot_version="release-locked",
            tokens_in=90,
            tokens_out=60,
            cost_usd_estimated=0.0123,
            latency_ms=240,
        )
    )
    db_session.commit()

    result = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(granularity="day", scope="all"),
        refresh=True,
    )
    assert len(result) == 1
    aggregate = result[0]
    assert aggregate.subscription_plan == "premium"
    assert aggregate.cost_usd_estimated == 0.0123
    assert aggregate.executed_provider == "anthropic"
    assert aggregate.active_snapshot_version == "release-locked"
    assert aggregate.locale == "en-US"


def test_unknown_feature_is_marked_legacy_residual(db_session) -> None:
    _seed_user_id(db_session, "consumption-d@example.com")
    db_session.add(
        _build_call_log(
            feature="foo_bar",
            subfeature=None,
            plan="free",
            timestamp=datetime(2026, 4, 15, 8, 30, tzinfo=timezone.utc),
            request_id="req-unknown-feature",
            manifest_entry_id="foo_bar:None:free:fr-FR",
        )
    )
    db_session.commit()

    nominal = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(granularity="day", scope="nominal"),
        refresh=True,
    )
    all_rows = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(granularity="day", scope="all"),
    )

    assert nominal == []
    assert len(all_rows) == 1
    assert all_rows[0].is_legacy_residual is True


def test_duplicate_usage_rows_do_not_duplicate_llm_calls(db_session) -> None:
    user_a = _seed_user_id(db_session, "consumption-e1@example.com")
    user_b = _seed_user_id(db_session, "consumption-e2@example.com")
    ts = datetime(2026, 4, 15, 11, 0, tzinfo=timezone.utc)
    call = _build_call_log(
        feature="natal",
        subfeature="full",
        plan="premium",
        timestamp=ts,
        request_id="req-duplicate-usage",
        manifest_entry_id="natal:full:premium:fr-FR",
        tokens_in=80,
        tokens_out=20,
        cost_usd_estimated=0.02,
    )
    db_session.add(call)
    db_session.flush()
    db_session.add_all(
        [
            UserTokenUsageLogModel(
                user_id=user_a,
                feature_code="natal",
                provider_model="gpt-4.1-mini",
                tokens_in=80,
                tokens_out=20,
                tokens_total=100,
                request_id="req-duplicate-usage-a",
                llm_call_log_id=call.id,
                created_at=ts,
            ),
            UserTokenUsageLogModel(
                user_id=user_b,
                feature_code="natal",
                provider_model="gpt-4.1-mini",
                tokens_in=80,
                tokens_out=20,
                tokens_total=100,
                request_id="req-duplicate-usage-b",
                llm_call_log_id=call.id,
                created_at=ts,
            ),
        ]
    )
    db_session.commit()

    rows = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(granularity="day", scope="all"),
        refresh=True,
    )
    assert len(rows) == 1
    assert rows[0].call_count == 1
    assert rows[0].tokens_in == 80
    assert rows[0].tokens_out == 20
    assert rows[0].total_tokens == 100
    assert rows[0].user_id is None


def test_partial_refresh_keeps_history_outside_requested_window(db_session) -> None:
    _seed_user_id(db_session, "consumption-f@example.com")
    april_call = _build_call_log(
        feature="chat",
        subfeature=None,
        plan="premium",
        timestamp=datetime(2026, 4, 15, 9, 0, tzinfo=timezone.utc),
        request_id="req-april-history",
        manifest_entry_id="chat:None:premium:fr-FR",
        tokens_in=40,
        tokens_out=10,
    )
    may_call = _build_call_log(
        feature="chat",
        subfeature=None,
        plan="premium",
        timestamp=datetime(2026, 5, 15, 9, 0, tzinfo=timezone.utc),
        request_id="req-may-history",
        manifest_entry_id="chat:None:premium:fr-FR",
        tokens_in=60,
        tokens_out=20,
    )
    db_session.add(april_call)
    db_session.add(may_call)
    db_session.commit()

    full = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(granularity="month", scope="all"),
        refresh=True,
    )
    assert len(full) == 2

    may_only = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(
            granularity="month",
            scope="all",
            from_utc=datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc),
            to_utc=datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc),
        ),
        refresh=True,
    )
    assert len(may_only) == 1

    after_partial = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(granularity="month", scope="all"),
    )
    assert len(after_partial) == 2


def test_partial_refresh_mid_day_rebuilds_full_day_bucket(db_session) -> None:
    _seed_user_id(db_session, "consumption-g@example.com")
    first = _build_call_log(
        feature="chat",
        subfeature=None,
        plan="premium",
        timestamp=datetime(2026, 5, 15, 8, 0, tzinfo=timezone.utc),
        request_id="req-day-first",
        manifest_entry_id="chat:None:premium:fr-FR",
        tokens_in=10,
        tokens_out=5,
    )
    second = _build_call_log(
        feature="chat",
        subfeature=None,
        plan="premium",
        timestamp=datetime(2026, 5, 15, 20, 0, tzinfo=timezone.utc),
        request_id="req-day-second",
        manifest_entry_id="chat:None:premium:fr-FR",
        tokens_in=30,
        tokens_out=15,
    )
    db_session.add(first)
    db_session.add(second)
    db_session.commit()

    LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(granularity="day", scope="all"),
        refresh=True,
    )
    partial = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(
            granularity="day",
            scope="all",
            from_utc=datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc),
            to_utc=datetime(2026, 5, 15, 23, 0, tzinfo=timezone.utc),
        ),
        refresh=True,
    )
    assert len(partial) == 1
    assert partial[0].total_tokens == 60
    assert partial[0].call_count == 2


def test_month_query_with_mid_month_from_keeps_containing_bucket(db_session) -> None:
    _seed_user_id(db_session, "consumption-h@example.com")
    db_session.add(
        _build_call_log(
            feature="natal",
            subfeature="full",
            plan="premium",
            timestamp=datetime(2026, 5, 10, 10, 0, tzinfo=timezone.utc),
            request_id="req-mid-month",
            manifest_entry_id="natal:full:premium:fr-FR",
        )
    )
    db_session.commit()

    LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(granularity="month", scope="all"),
        refresh=True,
    )
    may_only = LlmCanonicalConsumptionService.get_aggregates(
        db_session,
        filters=CanonicalConsumptionFilters(
            granularity="month",
            scope="all",
            from_utc=datetime(2026, 5, 15, 0, 0, tzinfo=timezone.utc),
            to_utc=datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc),
        ),
    )
    assert len(may_only) == 1
    assert may_only[0].period_start_utc == datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)

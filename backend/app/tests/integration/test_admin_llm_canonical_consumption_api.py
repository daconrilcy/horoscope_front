from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.infra.db.models.llm.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.infra.db.session import SessionLocal
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _build_call_log(
    *,
    feature: str,
    subfeature: str | None,
    plan: str,
    timestamp: datetime,
    request_id: str,
    manifest_entry_id: str,
    validation_status: LlmValidationStatus = LlmValidationStatus.VALID,
    latency_ms: int = 400,
) -> LlmCallLogModel:
    import uuid

    return LlmCallLogModel(
        id=uuid.uuid4(),
        use_case=feature,
        feature=feature,
        subfeature=subfeature,
        plan=plan,
        provider="openai",
        model="gpt-4.1-mini",
        latency_ms=latency_ms,
        tokens_in=100,
        tokens_out=50,
        cost_usd_estimated=0.01,
        validation_status=validation_status,
        repair_attempted=False,
        fallback_triggered=False,
        request_id=request_id,
        trace_id=f"trace-{request_id}",
        input_hash=f"hash-{request_id}",
        environment="test",
        requested_provider="openai",
        resolved_provider="openai",
        executed_provider="openai",
        active_snapshot_version="release-2026-04",
        manifest_entry_id=manifest_entry_id,
        timestamp=timestamp,
    )


def _admin_token(email: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="admin123", role="admin")
        db.commit()
        return auth.tokens.access_token


def test_admin_consumption_endpoint_returns_canonical_aggregates() -> None:
    token = _admin_token("admin-consumption@example.com")
    with SessionLocal() as db:
        db.add(
            _build_call_log(
                feature="natal",
                subfeature="full",
                plan="premium",
                timestamp=datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc),
                request_id="req-admin-consumption",
                manifest_entry_id="natal:full:premium:fr-FR",
                validation_status=LlmValidationStatus.ERROR,
                latency_ms=650,
            )
        )
        db.commit()

    response = client.get(
        "/v1/admin/llm/consumption/canonical",
        params={"view": "feature", "granularity": "day", "scope": "all", "refresh": "true"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["timezone"] == "UTC"
    assert payload["meta"]["refresh"] is True
    assert payload["meta"]["count"] >= 1
    first = payload["data"][0]
    assert first["feature"] == "natal"
    assert first["subfeature"] == "full"
    assert first["avg_latency_ms"] == 650.0
    assert "use_case" not in first


def test_admin_consumption_endpoint_supports_view_pagination_and_csv_export() -> None:
    token = _admin_token("admin-consumption-pagination@example.com")
    with SessionLocal() as db:
        first_log = _build_call_log(
            feature="chat",
            subfeature="chat_default",
            plan="basic",
            timestamp=datetime(2026, 4, 16, 10, 0, tzinfo=timezone.utc),
            request_id="req-pagination-1",
            manifest_entry_id="chat:chat_default:basic:fr-FR",
        )
        second_log = _build_call_log(
            feature="chat",
            subfeature="chat_default",
            plan="premium",
            timestamp=datetime(2026, 4, 16, 11, 0, tzinfo=timezone.utc),
            request_id="req-pagination-2",
            manifest_entry_id="chat:chat_default:premium:fr-FR",
        )
        db.add(first_log)
        db.add(second_log)
        db.commit()

    list_response = client.get(
        "/v1/admin/llm/consumption/canonical",
        params={
            "view": "subscription",
            "granularity": "day",
            "scope": "all",
            "refresh": "true",
            "page": 1,
            "page_size": 1,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload["meta"]["view"] == "subscription"
    assert list_payload["meta"]["page_size"] == 1
    assert list_payload["meta"]["count"] >= 2
    assert len(list_payload["data"]) == 1

    export_response = client.get(
        "/v1/admin/llm/consumption/canonical",
        params={
            "view": "subscription",
            "granularity": "day",
            "scope": "all",
            "export": "csv",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert export_response.status_code == 200
    assert export_response.headers["content-type"].startswith("text/csv")
    assert "subscription_plan" in export_response.text


def test_admin_consumption_drilldown_is_limited_to_50_and_safe_fields_only() -> None:
    token = _admin_token("admin-consumption-drilldown@example.com")
    base_ts = datetime(2026, 4, 17, 8, 0, tzinfo=timezone.utc)
    with SessionLocal() as db:
        for index in range(60):
            db.add(
                _build_call_log(
                    feature="natal",
                    subfeature="full",
                    plan="premium",
                    timestamp=base_ts + timedelta(minutes=index),
                    request_id=f"req-drill-{index}",
                    manifest_entry_id="natal:full:premium:fr-FR",
                )
            )
        db.commit()

    # Build canonical aggregates first.
    client.get(
        "/v1/admin/llm/consumption/canonical",
        params={"view": "feature", "granularity": "day", "scope": "all", "refresh": "true"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/v1/admin/llm/consumption/canonical/drilldown",
        params={
            "view": "feature",
            "granularity": "day",
            "period_start_utc": "2026-04-17T00:00:00Z",
            "feature": "natal",
            "subfeature": "full",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["count"] == 50
    assert payload["meta"]["order"] == "timestamp_desc"
    assert len(payload["data"]) == 50
    first = payload["data"][0]
    assert first["request_id"] == "req-drill-59"
    assert "raw_output" not in first
    assert "structured_output" not in first


def test_admin_consumption_user_sort_handles_rows_without_user_id() -> None:
    token = _admin_token("admin-consumption-sort@example.com")
    with SessionLocal() as db:
        user_auth = AuthService.register(
            db, email="consumption-sort-user@example.com", password="admin123", role="user"
        )
        db.commit()
        with_user = _build_call_log(
            feature="chat",
            subfeature=None,
            plan="premium",
            timestamp=datetime(2026, 4, 18, 10, 0, tzinfo=timezone.utc),
            request_id="req-sort-user",
            manifest_entry_id="chat:None:premium:fr-FR",
        )
        no_user = _build_call_log(
            feature="chat",
            subfeature=None,
            plan="premium",
            timestamp=datetime(2026, 4, 18, 11, 0, tzinfo=timezone.utc),
            request_id="req-sort-none",
            manifest_entry_id="chat:None:premium:fr-FR",
        )
        db.add(with_user)
        db.add(no_user)
        db.flush()
        db.add(
            UserTokenUsageLogModel(
                user_id=user_auth.user.id,
                feature_code="chat",
                provider_model="gpt-4.1-mini",
                tokens_in=100,
                tokens_out=50,
                tokens_total=150,
                request_id="usage-sort-user",
                llm_call_log_id=with_user.id,
                created_at=with_user.timestamp,
            )
        )
        db.commit()

    response = client.get(
        "/v1/admin/llm/consumption/canonical",
        params={
            "view": "user",
            "granularity": "day",
            "scope": "all",
            "refresh": "true",
            "sort_by": "user_id",
            "sort_order": "asc",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["sort_by"] == "user_id"
    assert payload["meta"]["count"] >= 2


def test_admin_consumption_user_drilldown_deduplicates_same_call_log() -> None:
    token = _admin_token("admin-consumption-dedup@example.com")
    with SessionLocal() as db:
        user_auth = AuthService.register(
            db, email="consumption-dedup-user@example.com", password="admin123", role="user"
        )
        db.commit()
        call_log = _build_call_log(
            feature="natal",
            subfeature="full",
            plan="premium",
            timestamp=datetime(2026, 4, 19, 9, 0, tzinfo=timezone.utc),
            request_id="req-dedup",
            manifest_entry_id="natal:full:premium:fr-FR",
        )
        db.add(call_log)
        db.flush()
        db.add_all(
            [
                UserTokenUsageLogModel(
                    user_id=user_auth.user.id,
                    feature_code="natal",
                    provider_model="gpt-4.1-mini",
                    tokens_in=100,
                    tokens_out=50,
                    tokens_total=150,
                    request_id="usage-dedup-1",
                    llm_call_log_id=call_log.id,
                    created_at=call_log.timestamp,
                ),
                UserTokenUsageLogModel(
                    user_id=user_auth.user.id,
                    feature_code="natal",
                    provider_model="gpt-4.1-mini",
                    tokens_in=100,
                    tokens_out=50,
                    tokens_total=150,
                    request_id="usage-dedup-2",
                    llm_call_log_id=call_log.id,
                    created_at=call_log.timestamp,
                ),
            ]
        )
        db.commit()

    response = client.get(
        "/v1/admin/llm/consumption/canonical/drilldown",
        params={
            "view": "user",
            "granularity": "day",
            "period_start_utc": "2026-04-19T00:00:00Z",
            "user_id": user_auth.user.id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    request_ids = [row["request_id"] for row in payload["data"]]
    assert request_ids == ["req-dedup"]


def test_admin_consumption_user_drilldown_none_user_only_returns_ambiguous_calls() -> None:
    token = _admin_token("admin-consumption-ambiguous@example.com")
    with SessionLocal() as db:
        user_a = AuthService.register(
            db, email="ambiguous-a@example.com", password="admin123", role="user"
        )
        user_b = AuthService.register(
            db, email="ambiguous-b@example.com", password="admin123", role="user"
        )
        db.commit()
        ambiguous = _build_call_log(
            feature="chat",
            subfeature=None,
            plan="premium",
            timestamp=datetime(2026, 4, 20, 8, 0, tzinfo=timezone.utc),
            request_id="req-ambiguous",
            manifest_entry_id="chat:None:premium:fr-FR",
        )
        unrelated = _build_call_log(
            feature="chat",
            subfeature=None,
            plan="premium",
            timestamp=datetime(2026, 4, 20, 9, 0, tzinfo=timezone.utc),
            request_id="req-unrelated",
            manifest_entry_id="chat:None:premium:fr-FR",
        )
        db.add_all([ambiguous, unrelated])
        db.flush()
        db.add_all(
            [
                UserTokenUsageLogModel(
                    user_id=user_a.user.id,
                    feature_code="chat",
                    provider_model="gpt-4.1-mini",
                    tokens_in=100,
                    tokens_out=50,
                    tokens_total=150,
                    request_id="usage-ambiguous-a",
                    llm_call_log_id=ambiguous.id,
                    created_at=ambiguous.timestamp,
                ),
                UserTokenUsageLogModel(
                    user_id=user_b.user.id,
                    feature_code="chat",
                    provider_model="gpt-4.1-mini",
                    tokens_in=100,
                    tokens_out=50,
                    tokens_total=150,
                    request_id="usage-ambiguous-b",
                    llm_call_log_id=ambiguous.id,
                    created_at=ambiguous.timestamp,
                ),
                UserTokenUsageLogModel(
                    user_id=user_a.user.id,
                    feature_code="chat",
                    provider_model="gpt-4.1-mini",
                    tokens_in=100,
                    tokens_out=50,
                    tokens_total=150,
                    request_id="usage-unrelated",
                    llm_call_log_id=unrelated.id,
                    created_at=unrelated.timestamp,
                ),
            ]
        )
        db.commit()

    response = client.get(
        "/v1/admin/llm/consumption/canonical/drilldown",
        params={
            "view": "user",
            "granularity": "day",
            "period_start_utc": "2026-04-20T00:00:00Z",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert [row["request_id"] for row in payload["data"]] == ["req-ambiguous"]


def test_admin_consumption_avg_latency_respects_locale_provider_and_snapshot_filters() -> None:
    token = _admin_token("admin-consumption-filtered-latency@example.com")
    with SessionLocal() as db:
        target = _build_call_log(
            feature="natal",
            subfeature="full",
            plan="premium",
            timestamp=datetime(2026, 4, 21, 10, 0, tzinfo=timezone.utc),
            request_id="req-fr-openai-snap-a",
            manifest_entry_id="natal:full:premium:fr-FR",
            latency_ms=120,
        )
        wrong_locale = _build_call_log(
            feature="natal",
            subfeature="full",
            plan="premium",
            timestamp=datetime(2026, 4, 21, 11, 0, tzinfo=timezone.utc),
            request_id="req-en-openai-snap-a",
            manifest_entry_id="natal:full:premium:en-US",
            latency_ms=900,
        )
        wrong_provider = _build_call_log(
            feature="natal",
            subfeature="full",
            plan="premium",
            timestamp=datetime(2026, 4, 21, 12, 0, tzinfo=timezone.utc),
            request_id="req-fr-anthropic-snap-a",
            manifest_entry_id="natal:full:premium:fr-FR",
            latency_ms=800,
        )
        wrong_provider.executed_provider = "anthropic"
        wrong_snapshot = _build_call_log(
            feature="natal",
            subfeature="full",
            plan="premium",
            timestamp=datetime(2026, 4, 21, 13, 0, tzinfo=timezone.utc),
            request_id="req-fr-openai-snap-b",
            manifest_entry_id="natal:full:premium:fr-FR",
            latency_ms=700,
        )
        wrong_snapshot.active_snapshot_version = "release-other"
        db.add_all([target, wrong_locale, wrong_provider, wrong_snapshot])
        db.commit()

    response = client.get(
        "/v1/admin/llm/consumption/canonical",
        params={
            "view": "feature",
            "granularity": "day",
            "scope": "all",
            "refresh": "true",
            "locale": "fr-FR",
            "executed_provider": "openai",
            "active_snapshot_version": "release-2026-04",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]
    assert payload["data"][0]["avg_latency_ms"] == 120.0


def test_admin_consumption_feature_drilldown_with_null_subfeature_stays_scoped() -> None:
    token = _admin_token("admin-consumption-feature-null-subfeature@example.com")
    with SessionLocal() as db:
        null_subfeature_call = _build_call_log(
            feature="chat",
            subfeature=None,
            plan="premium",
            timestamp=datetime(2026, 4, 22, 10, 0, tzinfo=timezone.utc),
            request_id="req-chat-none",
            manifest_entry_id="chat:None:premium:fr-FR",
        )
        specific_subfeature_call = _build_call_log(
            feature="chat",
            subfeature="chat_default",
            plan="premium",
            timestamp=datetime(2026, 4, 22, 11, 0, tzinfo=timezone.utc),
            request_id="req-chat-default",
            manifest_entry_id="chat:chat_default:premium:fr-FR",
        )
        db.add_all([null_subfeature_call, specific_subfeature_call])
        db.commit()

    response = client.get(
        "/v1/admin/llm/consumption/canonical/drilldown",
        params={
            "view": "feature",
            "granularity": "day",
            "period_start_utc": "2026-04-22T00:00:00Z",
            "feature": "chat",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    request_ids = [row["request_id"] for row in payload["data"]]
    assert request_ids == ["req-chat-none"]

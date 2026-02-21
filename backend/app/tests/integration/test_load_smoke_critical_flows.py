from __future__ import annotations

import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.billing import (
    BillingPlanModel,
    PaymentAttemptModel,
    SubscriptionPlanChangeModel,
    UserDailyQuotaUsageModel,
    UserSubscriptionModel,
)
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_editorial_config import EnterpriseEditorialConfigModel
from app.infra.db.models.enterprise_usage import EnterpriseDailyUsageModel
from app.infra.db.models.privacy import UserPrivacyRequestModel
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.enterprise_credentials_service import EnterpriseCredentialsService
from app.services.reference_data_service import ReferenceDataService


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            UserPrivacyRequestModel,
            ChatMessageModel,
            ChatConversationModel,
            ChartResultModel,
            UserDailyQuotaUsageModel,
            PaymentAttemptModel,
            SubscriptionPlanChangeModel,
            UserSubscriptionModel,
            BillingPlanModel,
            EnterpriseEditorialConfigModel,
            EnterpriseDailyUsageModel,
            EnterpriseApiCredentialModel,
            EnterpriseAccountModel,
            UserBirthProfileModel,
            AuditEventModel,
            AstroCharacteristicModel,
            AspectModel,
            HouseModel,
            SignModel,
            PlanetModel,
            ReferenceVersionModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()


def _create_enterprise_api_key(email: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email=email,
            password="strong-pass-123",
            role="enterprise_admin",
        )
        account = EnterpriseAccountModel(
            admin_user_id=auth.user.id,
            company_name="Load Test Enterprise",
            status="active",
        )
        db.add(account)
        db.flush()
        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()
        return created.api_key


def _create_access_token(*, email: str, password: str, role: str) -> str:
    with SessionLocal() as db:
        AuthService.register(db, email=email, password=password, role=role)
        auth = AuthService.login(db, email=email, password=password)
        db.commit()
        return auth.tokens.access_token


def _run_concurrent_requests(
    request_fn: Callable[[], tuple[int, float]],
    *,
    total_requests: int,
    max_workers: int,
    allowed_statuses: set[int] | None = None,
) -> dict[str, float | int]:
    latencies_ms: list[float] = []
    statuses: list[int] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(request_fn) for _ in range(total_requests)]
        for future in as_completed(futures):
            status_code, duration_ms = future.result()
            statuses.append(status_code)
            latencies_ms.append(duration_ms)

    sorted_latencies = sorted(latencies_ms)
    p95_index = min(len(sorted_latencies) - 1, int(0.95 * len(sorted_latencies)))
    p95_ms = sorted_latencies[p95_index]
    success_count = sum(1 for status in statuses if 200 <= status < 300)
    expected_protection_count = sum(1 for status in statuses if status == 429)
    allowed_statuses = allowed_statuses or set()
    expected_allowed_count = sum(
        1 for status in statuses if status in allowed_statuses and status != 429
    )
    error_5xx_count = sum(1 for status in statuses if status >= 500)
    unexpected_count = sum(
        1
        for status in statuses
        if not (200 <= status < 300) and status != 429 and status not in allowed_statuses
    )

    return {
        "count": len(statuses),
        "success_count": success_count,
        "expected_protection_count": expected_protection_count,
        "expected_allowed_count": expected_allowed_count,
        "error_5xx_count": error_5xx_count,
        "unexpected_count": unexpected_count,
        "p95_ms": p95_ms,
    }


def test_load_smoke_critical_flows() -> None:
    """Short non-destructive load smoke over critical flows.

    This test is intentionally small and stable: it validates basic
    concurrency handling and captures p95/error signals.
    """
    _cleanup_tables()
    client = TestClient(app)

    register = client.post(
        "/v1/auth/register",
        json={"email": "load-smoke-user@example.com", "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    access_token = register.json()["data"]["tokens"]["access_token"]
    bearer_headers = {"Authorization": f"Bearer {access_token}"}

    checkout = client.post(
        "/v1/billing/checkout",
        headers=bearer_headers,
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "load-smoke-checkout-1",
        },
    )
    assert checkout.status_code == 200

    privacy_export = client.post("/v1/privacy/export", headers=bearer_headers)
    assert privacy_export.status_code == 200
    first_message = client.post(
        "/v1/chat/messages",
        headers=bearer_headers,
        json={"message": "Bonjour, message initial pour creer une conversation."},
    )
    assert first_message.status_code == 200

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db)
        db.commit()

    api_key = _create_enterprise_api_key("load-smoke-b2b@example.com")
    b2b_headers = {"X-API-Key": api_key}
    ops_token = _create_access_token(
        email="load-smoke-ops@example.com",
        password="strong-pass-123",
        role="ops",
    )
    ops_headers = {"Authorization": f"Bearer {ops_token}"}
    ops_pre = client.get("/v1/ops/monitoring/operational-summary", headers=ops_headers)
    assert ops_pre.status_code == 200

    total_requests = 16
    max_workers = 4

    def _timed_get(path: str, headers: dict[str, str]) -> tuple[int, float]:
        start = time.perf_counter()
        # Avoid sharing a single TestClient across worker threads.
        with TestClient(app) as threaded_client:
            response = threaded_client.get(path, headers=headers)
        duration_ms = (time.perf_counter() - start) * 1000
        return response.status_code, duration_ms

    billing_metrics = _run_concurrent_requests(
        lambda: _timed_get("/v1/billing/quota", bearer_headers),
        total_requests=total_requests,
        max_workers=max_workers,
    )
    privacy_metrics = _run_concurrent_requests(
        lambda: _timed_get("/v1/privacy/export", bearer_headers),
        total_requests=total_requests,
        max_workers=max_workers,
    )
    privacy_delete_metrics = _run_concurrent_requests(
        lambda: _timed_get("/v1/privacy/delete", bearer_headers),
        total_requests=total_requests,
        max_workers=max_workers,
    )
    chat_metrics = _run_concurrent_requests(
        lambda: _timed_get("/v1/chat/conversations?limit=20&offset=0", bearer_headers),
        total_requests=total_requests,
        max_workers=max_workers,
    )
    b2b_metrics = _run_concurrent_requests(
        lambda: _timed_get("/v1/b2b/astrology/weekly-by-sign", b2b_headers),
        total_requests=total_requests,
        max_workers=max_workers,
    )

    def _timed_post_delete(path: str, headers: dict[str, str]) -> tuple[int, float]:
        start = time.perf_counter()
        with TestClient(app) as threaded_client:
            response = threaded_client.post(path, headers=headers, json={"confirmation": "DELETE"})
        duration_ms = (time.perf_counter() - start) * 1000
        return response.status_code, duration_ms

    privacy_delete_metrics = _run_concurrent_requests(
        lambda: _timed_post_delete("/v1/privacy/delete", bearer_headers),
        total_requests=total_requests,
        max_workers=max_workers,
        allowed_statuses={409},
    )

    all_metrics = {
        "billing": billing_metrics,
        "privacy": privacy_metrics,
        "chat": chat_metrics,
        "b2b": b2b_metrics,
        "privacy_delete": privacy_delete_metrics,
    }

    for name, metric in all_metrics.items():
        assert metric["count"] == total_requests, f"{name} count mismatch"
        assert metric["error_5xx_count"] == 0, f"{name} has 5xx responses"
        assert metric["unexpected_count"] == 0, f"{name} has unexpected responses"
        assert (
            metric["success_count"]
            + metric["expected_protection_count"]
            + metric["expected_allowed_count"]
        ) == total_requests, f"{name} response accounting mismatch"
        assert metric["success_count"] >= 1, f"{name} has no successful response under load"
        assert metric["p95_ms"] < 1500, f"{name} p95 too high in smoke test"

    p95_values = [float(metric["p95_ms"]) for metric in all_metrics.values()]
    assert statistics.mean(p95_values) < 1200
    ops_post = client.get("/v1/ops/monitoring/operational-summary", headers=ops_headers)
    assert ops_post.status_code == 200

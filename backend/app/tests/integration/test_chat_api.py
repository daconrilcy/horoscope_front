from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.core.config import settings
from app.core.llm_settings import ai_engine_settings
from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.infra.db.base import Base
from app.infra.db.models.billing import (
    BillingPlanModel,
    PaymentAttemptModel,
    UserDailyQuotaUsageModel,
    UserSubscriptionModel,
)
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel
from app.infra.db.models.feature_flag import FeatureFlagModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    FeatureUsageCounterModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
)
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.repositories.chat_repository import ChatRepository
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.billing.service import BillingService
from app.services.llm_generation.chat.chat_guidance_service import ChatGuidanceServiceError
from app.services.llm_generation.llm_token_usage_service import LlmTokenUsageService
from app.tests.helpers.llm_adapter_stub import reset_test_generators, set_test_chat_generator

client = TestClient(app)


def _cleanup_tables() -> None:
    # Ensure no API key is present for these tests to use stubs
    ai_engine_settings.openai_api_key = ""

    BillingService.reset_subscription_status_cache()
    reset_test_generators()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    from scripts.seed_66_20_convergence import seed_66_20_convergence

    seed_66_20_convergence()
    with SessionLocal() as db:
        for model in (
            ChatMessageModel,
            ChatConversationModel,
            FeatureFlagModel,
            ChartResultModel,
            UserDailyQuotaUsageModel,
            PaymentAttemptModel,
            UserSubscriptionModel,
            BillingPlanModel,
            UserBirthProfileModel,
            UserModel,
            AstroCharacteristicModel,
            AspectModel,
            HouseModel,
            SignModel,
            PlanetModel,
            ReferenceVersionModel,
        ):
            db.execute(delete(model))

        # Seed canonical features
        feature = FeatureCatalogModel(
            feature_code="astrologer_chat",
            feature_name="Astrologer chat",
            is_metered=True,
        )
        db.add(feature)
        db.flush()

        # Seed basic plan
        p_basic = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
        db.add(p_basic)
        db.flush()

        b_basic = PlanFeatureBindingModel(
            plan_id=p_basic.id,
            feature_id=feature.id,
            access_mode=AccessMode.QUOTA,
            is_enabled=True,
        )
        db.add(b_basic)
        db.flush()

        db.add(
            PlanFeatureQuotaModel(
                plan_feature_binding_id=b_basic.id,
                quota_key="tokens",
                quota_limit=10000,
                period_unit=PeriodUnit.DAY,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
            )
        )
        db.add(
            PlanFeatureQuotaModel(
                plan_feature_binding_id=b_basic.id,
                quota_key="tokens",
                quota_limit=50000,
                period_unit=PeriodUnit.WEEK,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
            )
        )
        db.add(
            PlanFeatureQuotaModel(
                plan_feature_binding_id=b_basic.id,
                quota_key="tokens",
                quota_limit=200000,
                period_unit=PeriodUnit.MONTH,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
            )
        )

        # Seed premium plan
        p_premium = PlanCatalogModel(
            plan_code="premium", plan_name="Premium", audience=Audience.B2C
        )
        db.add(p_premium)
        db.flush()

        b_premium = PlanFeatureBindingModel(
            plan_id=p_premium.id,
            feature_id=feature.id,
            access_mode=AccessMode.QUOTA,
            is_enabled=True,
        )
        db.add(b_premium)
        db.flush()

        db.add(
            PlanFeatureQuotaModel(
                plan_feature_binding_id=b_premium.id,
                quota_key="tokens",
                quota_limit=50000,
                period_unit=PeriodUnit.DAY,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
            )
        )
        db.add(
            PlanFeatureQuotaModel(
                plan_feature_binding_id=b_premium.id,
                quota_key="tokens",
                quota_limit=375000,
                period_unit=PeriodUnit.WEEK,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
            )
        )
        db.add(
            PlanFeatureQuotaModel(
                plan_feature_binding_id=b_premium.id,
                quota_key="tokens",
                quota_limit=1000000,
                period_unit=PeriodUnit.MONTH,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
            )
        )

        # Seed default persona
        default_persona = LlmPersonaModel(
            name="Astrologue Standard",
            enabled=True,
            tone="direct",
            verbosity="medium",
            style_markers=[],
            boundaries=[],
            allowed_topics=[],
            disallowed_topics=[],
            formatting={},
        )
        db.add(default_persona)
        db.commit()


def _register_and_get_access_token() -> str:
    register = client.post(
        "/v1/auth/register",
        json={"email": "chat-api-user@example.com", "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    return register.json()["data"]["tokens"]["access_token"]


def _set_active_subscription(user_id: int, plan_code: str) -> None:
    with SessionLocal() as db:
        period_start = datetime(2026, 4, 17, 10, 0, tzinfo=timezone.utc)
        period_end = datetime(2026, 5, 17, 10, 0, tzinfo=timezone.utc)

        # 0. Ensure plans exist
        BillingService.ensure_default_plans(db)

        # 1. Ensure StripeBillingProfileModel exists and is active
        profile = db.query(StripeBillingProfileModel).filter_by(user_id=user_id).first()
        if not profile:
            profile = StripeBillingProfileModel(
                user_id=user_id,
                stripe_customer_id=f"cus_{user_id}",
                stripe_subscription_id=f"sub_{user_id}",
                subscription_status="active",
                entitlement_plan=plan_code,
                current_period_start=period_start,
                current_period_end=period_end,
            )
            db.add(profile)
        else:
            profile.entitlement_plan = plan_code
            profile.subscription_status = "active"
            profile.current_period_start = period_start
            profile.current_period_end = period_end

        # 2. Also ensure UserSubscriptionModel exists
        plan = db.scalar(select(BillingPlanModel).where(BillingPlanModel.code == plan_code))
        if plan:
            sub = db.query(UserSubscriptionModel).filter_by(user_id=user_id).first()
            if not sub:
                sub = UserSubscriptionModel(
                    user_id=user_id,
                    plan_id=plan.id,
                    status="active",
                    started_at=datetime.now(timezone.utc),
                )
                db.add(sub)
            else:
                sub.plan_id = plan.id
                sub.status = "active"
        db.commit()


def _activate_entry_plan(access_token: str, idempotency_key: str) -> None:
    user_id = _get_chat_api_user_id()
    _set_active_subscription(user_id, "basic")

    # Seed canonical binding so ChatEntitlementGate works
    _seed_canonical_chat_binding(
        plan_code="basic",
        access_mode=AccessMode.QUOTA,
        is_enabled=True,
        quotas=[("tokens", 5000)],
    )


def _activate_free_plan() -> None:
    user_id = _get_chat_api_user_id()
    _set_active_subscription(user_id, "free")
    _seed_canonical_chat_binding(
        plan_code="free",
        access_mode=AccessMode.QUOTA,
        is_enabled=True,
        quotas=[("messages", 1, PeriodUnit.WEEK)],
    )


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def _enable_module_for_user(
    *,
    module: str,
    ops_token: str,
    user_id: int,
    enabled: bool = True,
) -> None:
    flag_key = f"{module}_enabled"
    response = client.put(
        f"/v1/ops/feature-flags/{flag_key}",
        headers={"Authorization": f"Bearer {ops_token}"},
        json={
            "enabled": enabled,
            "target_roles": ["user"],
            "target_user_ids": [user_id],
        },
    )
    assert response.status_code == 200


def _get_chat_api_user_id() -> int:
    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        return user.id


def _seed_canonical_chat_binding(
    *,
    plan_code: str,
    access_mode: AccessMode,
    is_enabled: bool = True,
    quotas: list[tuple[str, int] | tuple[str, int, PeriodUnit]] | None = None,
) -> None:
    with SessionLocal() as db:
        plan = db.scalar(select(PlanCatalogModel).where(PlanCatalogModel.plan_code == plan_code))
        if plan is None:
            plan = PlanCatalogModel(plan_code=plan_code, plan_name=plan_code, audience=Audience.B2C)
            db.add(plan)
            db.flush()

        feature = db.scalar(
            select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == "astrologer_chat")
        )
        if feature is None:
            feature = FeatureCatalogModel(
                feature_code="astrologer_chat",
                feature_name="Astrologer chat",
                is_metered=True,
            )
            db.add(feature)
            db.flush()

        binding = db.scalar(
            select(PlanFeatureBindingModel).where(
                PlanFeatureBindingModel.plan_id == plan.id,
                PlanFeatureBindingModel.feature_id == feature.id,
            )
        )
        if binding is None:
            binding = PlanFeatureBindingModel(
                plan_id=plan.id,
                feature_id=feature.id,
                access_mode=access_mode,
                is_enabled=is_enabled,
            )
            db.add(binding)
            db.flush()
        else:
            binding.access_mode = access_mode
            binding.is_enabled = is_enabled
            db.flush()

        if quotas is not None:
            db.query(PlanFeatureQuotaModel).filter(
                PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
            ).delete()
            for quota_item in quotas:
                if len(quota_item) == 2:
                    quota_key, quota_limit = quota_item
                    period_unit = PeriodUnit.MONTH
                else:
                    quota_key, quota_limit, period_unit = quota_item
                db.add(
                    PlanFeatureQuotaModel(
                        plan_feature_binding_id=binding.id,
                        quota_key=quota_key,
                        quota_limit=quota_limit,
                        period_unit=period_unit,
                        period_value=1,
                        reset_mode=ResetMode.CALENDAR,
                    )
                )
        db.commit()


def test_send_chat_message_requires_token() -> None:
    _cleanup_tables()
    response = client.post("/v1/chat/messages", json={"message": "Bonjour"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_send_chat_message_success() -> None:
    _cleanup_tables()
    # Story 66.20: Seed mandatory assemblies after table cleanup
    from scripts.seed_66_20_convergence import seed_66_20_convergence

    seed_66_20_convergence()

    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-success-1")
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Quelle est mon energie du jour ?"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["conversation_id"] > 0
    assert payload["user_message"]["role"] == "user"
    assert payload["assistant_message"]["role"] == "assistant"
    assert payload["fallback_used"] is False
    assert payload["recovery"]["recovery_strategy"] == "none"
    assert "context" in payload


def test_send_chat_message_returns_429_when_token_quota_is_reached() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-quota-1")

    # Set a low token quota (enough for one call, not two)
    _seed_canonical_chat_binding(
        plan_code="basic",
        access_mode=AccessMode.QUOTA,
        is_enabled=True,
        quotas=[("tokens", 100, PeriodUnit.DAY)],
    )

    headers = {"Authorization": f"Bearer {access_token}"}

    # First message should consume some tokens
    response = client.post(
        "/v1/chat/messages",
        headers=headers,
        json={"message": "Question contextuelle"},
    )
    assert response.status_code == 200

    # Exhaust remaining quota
    with SessionLocal() as db:
        user_id = _get_chat_api_user_id()
        counter = db.scalar(
            select(FeatureUsageCounterModel).where(
                FeatureUsageCounterModel.user_id == user_id,
                FeatureUsageCounterModel.feature_code == "astrologer_chat",
                FeatureUsageCounterModel.quota_key == "tokens",
            )
        )
        if counter:
            counter.used_count = 100
            db.commit()

    # Second message should be blocked
    blocked = client.post(
        "/v1/chat/messages",
        headers=headers,
        json={"message": "Question depassement quota"},
    )
    assert blocked.status_code == 429
    payload = blocked.json()["error"]
    assert payload["code"] == "chat_quota_exceeded"
    assert payload["details"]["quota_key"] == "tokens"


def test_first_chat_message_can_saturate_token_quota_without_rollback() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-token-cap-1")
    _seed_canonical_chat_binding(
        plan_code="basic",
        access_mode=AccessMode.QUOTA,
        is_enabled=True,
        quotas=[("tokens", 100, PeriodUnit.DAY)],
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    async def _large_usage_reply(*args: object, **kwargs: object) -> GatewayResult:
        return GatewayResult(
            use_case="chat_astrologer",
            request_id=str(args[3]),
            trace_id=str(args[4]),
            raw_output="Réponse longue mais autorisée.",
            structured_output=None,
            usage=UsageInfo(input_tokens=80, output_tokens=50, total_tokens=130),
            meta=GatewayMeta(latency_ms=0, model="test-model"),
        )

    set_test_chat_generator(_large_usage_reply)

    first = client.post(
        "/v1/chat/messages",
        headers=headers,
        json={"message": "Premier message quota"},
    )
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["quota_info"]["remaining"] == 0
    assert first_payload["quota_info"]["limit"] == 100

    entitlements = client.get("/v1/entitlements/me", headers=headers)
    assert entitlements.status_code == 200
    chat_ent = next(
        f for f in entitlements.json()["data"]["features"] if f["feature_code"] == "astrologer_chat"
    )
    day_state = next(state for state in chat_ent["usage_states"] if state["period_unit"] == "day")
    assert day_state["used"] == 100
    assert day_state["remaining"] == 0
    assert day_state["exhausted"] is True

    second = client.post(
        "/v1/chat/messages",
        headers=headers,
        json={"message": "Second message quota"},
    )
    assert second.status_code == 429
    assert second.json()["error"]["code"] == "chat_quota_exceeded"


def test_chat_message_consumption_is_reflected_in_entitlements_status() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-quota-progress-1")
    headers = {"Authorization": f"Bearer {access_token}"}

    first_message = client.post(
        "/v1/chat/messages",
        headers=headers,
        json={"message": "Question progression 1"},
    )
    assert first_message.status_code == 200
    first_ent = client.get("/v1/entitlements/me", headers=headers)
    assert first_ent.status_code == 200
    chat_ent = next(
        f for f in first_ent.json()["data"]["features"] if f["feature_code"] == "astrologer_chat"
    )
    # used should be > 0 tokens
    assert chat_ent["usage_states"][0]["used"] > 0
    assert chat_ent["usage_states"][0]["quota_key"] == "tokens"


def test_free_chat_message_limit_consumes_single_message_quota() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_free_plan()
    headers = {"Authorization": f"Bearer {access_token}"}

    first = client.post(
        "/v1/chat/messages",
        headers=headers,
        json={"message": "Premier message free"},
    )
    assert first.status_code == 200

    entitlements = client.get("/v1/entitlements/me", headers=headers)
    assert entitlements.status_code == 200
    chat_ent = next(
        f for f in entitlements.json()["data"]["features"] if f["feature_code"] == "astrologer_chat"
    )
    week_state = next(
        state
        for state in chat_ent["usage_states"]
        if state["quota_key"] == "messages" and state["period_unit"] == "week"
    )
    assert week_state["used"] == 1
    assert week_state["remaining"] == 0
    assert week_state["exhausted"] is True

    second = client.post(
        "/v1/chat/messages",
        headers=headers,
        json={"message": "Second message free"},
    )
    assert second.status_code == 429
    payload = second.json()["error"]
    assert payload["code"] == "chat_quota_exceeded"
    assert payload["details"]["quota_key"] == "messages"


def test_chat_enforcement_uses_updated_limit_after_plan_change() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    _activate_entry_plan(access_token, "chat-checkout-plan-change-1")

    user_id = _get_chat_api_user_id()
    _set_active_subscription(user_id, "premium")

    for attempt in range(2):
        response = client.post(
            "/v1/chat/messages",
            headers=headers,
            json={"message": f"Question premium {attempt}"},
        )
        assert response.status_code == 200

    ent = client.get("/v1/entitlements/me", headers=headers)
    assert ent.status_code == 200
    chat_ent = next(
        f for f in ent.json()["data"]["features"] if f["feature_code"] == "astrologer_chat"
    )
    month_state = next(
        state for state in chat_ent["usage_states"] if state["period_unit"] == "month"
    )
    assert month_state["quota_limit"] == 1000000
    assert month_state["used"] > 0


def test_send_chat_message_second_turn_uses_first_turn_context() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-context-1")

    first = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Premiere question contexte"},
    )
    assert first.status_code == 200
    conversation_id = first.json()["data"]["conversation_id"]

    second = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Deuxieme question contexte"},
    )
    assert second.status_code == 200
    payload = second.json()["data"]
    assert payload["conversation_id"] == conversation_id
    # The stub returns a fixed response, we check context metadata instead
    assert payload["context"]["message_count"] >= 3


def test_send_chat_message_forbidden_for_non_user_role() -> None:
    _cleanup_tables()
    support_access_token = _register_user_with_role_and_token("chat-support@example.com", "support")
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {support_access_token}"},
        json={"message": "Question support"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_send_chat_message_invalid_input_returns_422() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-invalid-input-1")
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "   "},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_chat_input"


def test_send_chat_message_invalid_payload_uses_standard_error_envelope() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-invalid-payload-1")
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json=["not-an-object"],
    )
    assert response.status_code == 422
    payload = response.json()
    assert "error" in payload
    assert payload["error"]["code"] == "invalid_chat_request"


def test_send_chat_message_timeout_returns_503(monkeypatch: object) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-timeout-1")

    def _raise_timeout(*args: object, **kwargs: object) -> object:
        raise ChatGuidanceServiceError(
            code="llm_timeout",
            message="llm provider timeout",
            details={"retryable": "true", "action": "retry_message"},
        )

    monkeypatch.setattr("app.api.v1.routers.chat.ChatGuidanceService.send_message", _raise_timeout)
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question"},
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_timeout"


def test_send_chat_message_unavailable_returns_503(monkeypatch: object) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-unavailable-1")

    def _raise_unavailable(*args: object, **kwargs: object) -> object:
        raise ChatGuidanceServiceError(
            code="llm_unavailable",
            message="llm provider is unavailable",
            details={"retryable": "true", "action": "retry_message"},
        )

    monkeypatch.setattr(
        "app.api.v1.routers.chat.ChatGuidanceService.send_message",
        _raise_unavailable,
    )
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question"},
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_unavailable"
    assert (
        response.json()["error"]["message"]
        == "Je suis desole, je ne peux pas vous repondre pour l'instant. Revenez un peu plus tard."
    )


def test_send_chat_message_invalid_context_config_returns_422(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-invalid-context-1")
    monkeypatch.setattr(settings, "chat_context_window_messages", 0)

    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question"},
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "invalid_chat_context_config"


def test_list_chat_conversations_returns_user_history_sorted() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-list-history-1")
    first = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Conversation one"},
    )
    assert first.status_code == 200
    first_id = first.json()["data"]["conversation_id"]

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        # Deactivate previous active conversation created by API
        prev_active = db.scalar(
            select(ChatConversationModel)
            .where(ChatConversationModel.user_id == user.id)
            .where(ChatConversationModel.status == "active")
        )
        if prev_active:
            prev_active.status = "archived"
            db.flush()

        persona_id = db.scalar(select(LlmPersonaModel.id))
        second_conversation = ChatRepository(db).create_conversation(user.id, persona_id=persona_id)
        ChatRepository(db).create_message(
            conversation_id=second_conversation.id,
            role="user",
            content="Conversation two",
        )
        db.commit()
        second_id = second_conversation.id

    response = client.get(
        "/v1/chat/conversations?limit=10&offset=0",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total"] >= 2
    ids = [item["conversation_id"] for item in payload["conversations"]]
    assert ids[0] == second_id
    assert first_id in ids
    assert payload["limit"] == 10
    assert payload["offset"] == 0


def test_list_chat_conversations_paginates_with_limit_and_offset() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-list-pagination-1")

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        persona_id = db.scalar(select(LlmPersonaModel.id))
        repo = ChatRepository(db)
        conversation_ids: list[int] = []
        for index in range(5):
            conversation = repo.create_conversation(user.id, persona_id=persona_id)
            repo.create_message(
                conversation_id=conversation.id,
                role="user",
                content=f"Conversation {index}",
            )
            conversation_ids.append(conversation.id)
            # Deactivate to allow creating next one for same persona
            conversation.status = "archived"
            db.flush()
        db.commit()

    response = client.get(
        "/v1/chat/conversations?limit=2&offset=1",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total"] == 5
    assert payload["limit"] == 2
    assert payload["offset"] == 1
    returned_ids = [item["conversation_id"] for item in payload["conversations"]]
    expected_order = sorted(conversation_ids, reverse=True)
    assert returned_ids == expected_order[1:3]


def test_list_chat_conversations_uses_id_tiebreak_when_updated_at_is_equal() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-list-tiebreak-1")

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        persona_id = db.scalar(select(LlmPersonaModel.id))
        repo = ChatRepository(db)
        conversation_a = repo.create_conversation(user.id, persona_id=persona_id)
        repo.create_message(
            conversation_id=conversation_a.id,
            role="user",
            content="Conversation A",
        )
        # Deactivate A to allow creating B for same persona
        conversation_a.status = "archived"
        db.flush()

        conversation_b = repo.create_conversation(user.id, persona_id=persona_id)
        repo.create_message(
            conversation_id=conversation_b.id,
            role="user",
            content="Conversation B",
        )
        same_timestamp = datetime(2026, 2, 20, 10, 0, 0, tzinfo=timezone.utc)
        conversation_a.updated_at = same_timestamp
        conversation_b.updated_at = same_timestamp
        conversation_a_id = conversation_a.id
        conversation_b_id = conversation_b.id
        db.commit()

    response = client.get(
        "/v1/chat/conversations?limit=10&offset=0",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    ids = [item["conversation_id"] for item in response.json()["data"]["conversations"]]
    assert ids.index(conversation_b_id) < ids.index(conversation_a_id)


def test_list_chat_conversations_pagination_pages_do_not_overlap() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-list-pages-1")

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        persona_id = db.scalar(select(LlmPersonaModel.id))
        repo = ChatRepository(db)
        for index in range(6):
            conversation = repo.create_conversation(user.id, persona_id=persona_id)
            repo.create_message(
                conversation_id=conversation.id,
                role="user",
                content=f"Conversation page {index}",
            )
            # Deactivate to allow creating next one for same persona
            conversation.status = "archived"
            db.flush()
        db.commit()

    first_page = client.get(
        "/v1/chat/conversations?limit=3&offset=0",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    second_page = client.get(
        "/v1/chat/conversations?limit=3&offset=3",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert first_page.status_code == 200
    assert second_page.status_code == 200
    first_ids = {item["conversation_id"] for item in first_page.json()["data"]["conversations"]}
    second_ids = {item["conversation_id"] for item in second_page.json()["data"]["conversations"]}
    assert len(first_ids) == 3
    assert len(second_ids) == 3
    assert first_ids.isdisjoint(second_ids)


def test_list_chat_conversations_propagates_request_id() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.get(
        "/v1/chat/conversations?limit=10&offset=0",
        headers={"Authorization": f"Bearer {access_token}", "X-Request-Id": "rid-chat-list-1"},
    )
    assert response.status_code == 200
    assert response.json()["meta"]["request_id"] == "rid-chat-list-1"


def test_get_chat_conversation_history_returns_messages() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-history-1")
    send = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Historique test"},
    )
    assert send.status_code == 200
    conversation_id = send.json()["data"]["conversation_id"]

    response = client.get(
        f"/v1/chat/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["conversation_id"] == conversation_id
    assert len(payload["messages"]) >= 2
    assert payload["messages"][0]["role"] == "user"


def test_get_chat_conversation_history_propagates_request_id() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-history-rid-1")
    send = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Historique rid"},
    )
    assert send.status_code == 200
    conversation_id = send.json()["data"]["conversation_id"]

    response = client.get(
        f"/v1/chat/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {access_token}", "X-Request-Id": "rid-chat-history-1"},
    )
    assert response.status_code == 200
    assert response.json()["meta"]["request_id"] == "rid-chat-history-1"


def test_get_chat_conversation_history_forbidden_for_other_user() -> None:
    _cleanup_tables()
    first_token = _register_and_get_access_token()
    _activate_entry_plan(first_token, "chat-checkout-forbidden-history-1")
    send = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {first_token}"},
        json={"message": "Private thread"},
    )
    assert send.status_code == 200
    conversation_id = send.json()["data"]["conversation_id"]

    second_token = _register_user_with_role_and_token("chat-second-user@example.com", "user")
    response = client.get(
        f"/v1/chat/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "conversation_forbidden"


def test_get_chat_conversation_history_not_found() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.get(
        "/v1/chat/conversations/999999",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "conversation_not_found"


def test_send_chat_message_with_conversation_id_targets_selected_thread() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-conversation-target-1")

    first = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Thread A"},
    )
    assert first.status_code == 200
    conversation_a = first.json()["data"]["conversation_id"]

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == "chat-api-user@example.com"))
        assert user is not None
        # We need a different persona or just deactivate the previous conversation (Thread A)
        # Thread A was created via API, so it's active.
        prev_active = db.scalar(
            select(ChatConversationModel)
            .where(ChatConversationModel.user_id == user.id)
            .where(ChatConversationModel.status == "active")
        )
        if prev_active:
            prev_active.status = "archived"
            db.flush()

        persona_id = db.scalar(select(LlmPersonaModel.id))
        conversation_b = ChatRepository(db).create_conversation(user.id, persona_id=persona_id)
        ChatRepository(db).create_message(
            conversation_id=conversation_b.id,
            role="user",
            content="Thread B",
        )
        db.commit()

    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Follow-up A", "conversation_id": conversation_a},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["conversation_id"] == conversation_a

    history = client.get(
        f"/v1/chat/conversations/{conversation_a}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert history.status_code == 200
    # In integration test with stub, we can only verify the messages were recorded in DB
    contents = [message["content"] for message in history.json()["data"]["messages"]]
    assert "Thread A" in contents
    assert "Follow-up A" in contents


def test_send_chat_message_off_scope_recovery_reformulates_response() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-offscope-reformulate-1")
    calls = {"count": 0}

    async def _off_scope_then_recover(*args: object, **kwargs: object) -> str:
        calls["count"] += 1
        if calls["count"] == 1:
            return "[off_scope] incoherent"
        return "Reponse reformulee pertinente"

    set_test_chat_generator(_off_scope_then_recover)
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["recovery"]["off_scope_detected"] is True
    assert payload["recovery"]["recovery_applied"] is True
    assert payload["recovery"]["recovery_strategy"] == "reformulate"
    assert payload["fallback_used"] is False


def test_send_chat_message_off_scope_recovery_uses_safe_fallback() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-offscope-fallback-1")

    async def _always_off_scope(*args: object, **kwargs: object) -> str:
        return "[off_scope] incoherent"

    set_test_chat_generator(_always_off_scope)
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["recovery"]["off_scope_detected"] is True
    assert payload["recovery"]["recovery_strategy"] == "safe_fallback"
    assert payload["fallback_used"] is True


def test_send_chat_message_requires_active_subscription() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question sans abonnement"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "chat_access_denied"


def test_send_chat_message_disabled_canonical_binding_returns_disabled_by_plan() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-disabled-binding-1")
    _seed_canonical_chat_binding(
        plan_code="basic",
        access_mode=AccessMode.DISABLED,
        is_enabled=True,
    )

    response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "Question binding desactive"},
    )

    assert response.status_code == 403
    payload = response.json()["error"]
    assert payload["code"] == "chat_access_denied"
    assert payload["details"]["reason"] == "disabled_by_plan"


def test_send_chat_message_rolls_back_partial_canonical_consumption() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    _activate_entry_plan(access_token, "chat-checkout-rollback-1")
    _seed_canonical_chat_binding(
        plan_code="basic",
        access_mode=AccessMode.QUOTA,
        is_enabled=True,
        quotas=[("tokens", 5000), ("burst", 2)],
    )

    # We mock LlmTokenUsageService.record_usage to fail
    monkeypatch = pytest.MonkeyPatch()

    original_record_usage = LlmTokenUsageService.record_usage

    def _record_then_fail(*args: object, **kwargs: object) -> object:
        feature_code = kwargs.get("feature_code")
        if feature_code == "astrologer_chat":
            # Force failure to trigger rollback
            raise Exception("Simulated DB error during token recording")
        return original_record_usage(*args, **kwargs)

    monkeypatch.setattr(
        "app.services.llm_generation.chat.chat_guidance_service.LlmTokenUsageService.record_usage",
        _record_then_fail,
    )

    try:
        response = client.post(
            "/v1/chat/messages",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"message": "Question rollback"},
        )
        assert response.status_code == 500
    finally:
        monkeypatch.undo()

    # Verify that the message was NOT saved due to transaction rollback
    with SessionLocal() as db:
        msg = db.scalar(
            select(ChatMessageModel).where(ChatMessageModel.content == "Question rollback")
        )
        assert msg is None

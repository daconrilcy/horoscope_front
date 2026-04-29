from datetime import UTC, date, datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.base import Base
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    FeatureUsageCounterModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
)
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.main import app
from app.prediction.llm_narrator import NarratorResult
from app.prediction.persisted_snapshot import PersistedPredictionSnapshot
from app.services.billing.service import BillingService
from app.services.prediction import ServiceResult
from app.tests.helpers.db_session import app_test_engine


@pytest.fixture
def setup_catalog(db_session: Session):
    # Clear and reset
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    BillingService.reset_subscription_status_cache()

    # Feature
    feature = FeatureCatalogModel(
        feature_code="horoscope_daily", feature_name="Horoscope Quotidien", is_metered=False
    )
    db_session.add(feature)

    # Plans
    plans_data = [
        ("free", "summary_only"),
        ("basic", "full"),
    ]

    for code, variant in plans_data:
        bp = BillingPlanModel(
            code=code,
            display_name=code,
            monthly_price_cents=0 if code == "free" else 900,
            currency="EUR",
            daily_message_limit=10,
            is_active=True,
        )
        db_session.add(bp)
        db_session.flush()

        cp = PlanCatalogModel(
            plan_code=code,
            plan_name=code,
            audience=Audience.B2C,
            is_active=True,
        )
        db_session.add(cp)
        db_session.flush()

        db_session.add(
            PlanFeatureBindingModel(
                plan_id=cp.id,
                feature_id=feature.id,
                is_enabled=True,
                access_mode=AccessMode.UNLIMITED,
                variant_code=variant,
            )
        )
    db_session.commit()


def test_get_daily_prediction_passes_correct_variant_to_narrator(
    db_session: Session, setup_catalog
):
    from app.infra.db.session import get_db_session

    app.dependency_overrides[get_db_session] = lambda: db_session

    client = TestClient(app)

    # 1. Free User
    user_free = UserModel(email="free@example.com", password_hash="...", role="user")
    db_session.add(user_free)
    db_session.flush()

    db_session.add(
        UserBirthProfileModel(
            user_id=user_free.id,
            birth_date=datetime(1990, 1, 1).date(),
            birth_time="12:00:00",
            birth_lat=48.8566,
            birth_lon=2.3522,
            birth_place="Paris, France",
            birth_timezone="Europe/Paris",
        )
    )

    free_plan_id = db_session.query(BillingPlanModel).filter_by(code="free").one().id
    db_session.add(
        UserSubscriptionModel(user_id=user_free.id, plan_id=free_plan_id, status="active")
    )
    db_session.commit()

    auth_user_free = AuthenticatedUser(
        id=user_free.id,
        email=user_free.email,
        role=user_free.role,
        created_at=datetime.now(UTC),
    )
    app.dependency_overrides[require_authenticated_user] = lambda: auth_user_free

    # Mock settings to enable LLM narration
    with (
        patch("app.api.v1.routers.public.predictions.settings") as mock_settings_router,
        patch("app.prediction.public_projection.settings") as mock_settings_proj,
    ):
        mock_settings_router.llm_narrator_enabled = True
        mock_settings_router.ruleset_version = "2.0.0"
        mock_settings_router.active_reference_version = "2.0.0"
        mock_settings_proj.llm_narrator_enabled = True

        # Mock CommonContextBuilder.build
        with patch("app.domain.llm.prompting.context.CommonContextBuilder.build") as mock_ctx_build:
            mock_ctx = MagicMock()
            mock_ctx.context_quality = "nominal"
            mock_ctx.missing_fields = []
            mock_ctx.payload.model_dump.return_value = {}
            mock_ctx_build.return_value = mock_ctx
            # Mock DailyPredictionService to return a dummy run
            dummy_run = PersistedPredictionSnapshot(
                run_id=1,
                user_id=1,
                local_date=date(2026, 4, 4),
                timezone="Europe/Paris",
                computed_at=datetime(2026, 4, 4, 10, 0),
                input_hash="test-hash",
                reference_version_id=1,
                ruleset_id=1,
                house_system_effective="placidus",
                is_provisional_calibration=False,
                calibration_label="test",
                overall_tone="positive",
                overall_summary="Test summary",
                category_scores=[],
                turning_points=[],
                time_blocks=[],
                llm_narrative=None,
            )

            mock_result = ServiceResult(run=dummy_run, bundle=None, was_reused=True)

            with patch(
                "app.api.v1.routers.public.predictions.DailyPredictionService"
            ) as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_service.get_or_compute.return_value = mock_result

                # AC9: Ensure canonical path is used
                with patch(
                    "app.domain.llm.runtime.adapter.AIEngineAdapter.generate_horoscope_narration"
                ) as mock_adapter:
                    mock_adapter.return_value = NarratorResult(
                        daily_synthesis="Synthèse du jour canonique.",
                        astro_events_intro="Intro canonique.",
                        time_window_narratives={},
                        turning_point_narratives=[],
                    )

                    response = client.get("/v1/predictions/daily")
                    assert response.status_code == 200
                    _, kwargs = mock_adapter.call_args
                    assert kwargs["variant_code"] == "summary_only"

    # 2. Basic User
    user_basic = UserModel(email="basic@example.com", password_hash="...", role="user")
    db_session.add(user_basic)
    db_session.flush()

    db_session.add(
        UserBirthProfileModel(
            user_id=user_basic.id,
            birth_date=datetime(1990, 1, 1).date(),
            birth_time="12:00:00",
            birth_lat=48.8566,
            birth_lon=2.3522,
            birth_place="Paris, France",
            birth_timezone="Europe/Paris",
        )
    )

    basic_plan_id = db_session.query(BillingPlanModel).filter_by(code="basic").one().id
    db_session.add(
        UserSubscriptionModel(user_id=user_basic.id, plan_id=basic_plan_id, status="active")
    )
    db_session.commit()

    auth_user_basic = AuthenticatedUser(
        id=user_basic.id,
        email=user_basic.email,
        role=user_basic.role,
        created_at=datetime.now(UTC),
    )
    app.dependency_overrides[require_authenticated_user] = lambda: auth_user_basic

    with (
        patch("app.api.v1.routers.public.predictions.settings") as mock_settings_router,
        patch("app.prediction.public_projection.settings") as mock_settings_proj,
    ):
        mock_settings_router.llm_narrator_enabled = True
        mock_settings_router.ruleset_version = "2.0.0"
        mock_settings_router.active_reference_version = "2.0.0"
        mock_settings_proj.llm_narrator_enabled = True

        with patch("app.domain.llm.prompting.context.CommonContextBuilder.build") as mock_ctx_build:
            mock_ctx = MagicMock()
            mock_ctx.context_quality = "nominal"
            mock_ctx.missing_fields = []
            mock_ctx.payload.model_dump.return_value = {}
            mock_ctx_build.return_value = mock_ctx

            with patch(
                "app.api.v1.routers.public.predictions.DailyPredictionService"
            ) as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_service.get_or_compute.return_value = mock_result

                with (
                    patch(
                        "app.domain.llm.runtime.adapter.AIEngineAdapter.generate_horoscope_narration"
                    ) as mock_adapter,
                    patch("app.prediction.llm_narrator.LLMNarrator.narrate") as mock_narrate,
                ):
                    mock_adapter.return_value = NarratorResult(
                        daily_synthesis="Synthèse du jour canonique.",
                        astro_events_intro="Intro canonique.",
                        time_window_narratives={},
                        turning_point_narratives=[],
                    )
                    mock_narrate.return_value = None

                    response = client.get("/v1/predictions/daily")
                    assert response.status_code == 200
                    _, kwargs = mock_adapter.call_args
                    assert kwargs["variant_code"] == "full"

    app.dependency_overrides.clear()


def test_daily_prediction_llm_does_not_consume_astrologer_chat_quota(
    db_session: Session, setup_catalog
):
    from datetime import UTC, date, datetime

    from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
    from app.infra.db.models.user_birth_profile import UserBirthProfileModel
    from app.infra.db.session import get_db_session
    from app.prediction.persisted_snapshot import PersistedPredictionSnapshot
    from app.services.prediction import ServiceResult

    app.dependency_overrides[get_db_session] = lambda: db_session
    client = TestClient(app)

    user = UserModel(email="daily-quota@example.com", password_hash="...", role="user")
    db_session.add(user)
    db_session.flush()
    db_session.add(
        UserBirthProfileModel(
            user_id=user.id,
            birth_date=datetime(1990, 1, 1).date(),
            birth_time="12:00:00",
            birth_lat=48.8566,
            birth_lon=2.3522,
            birth_place="Paris, France",
            birth_timezone="Europe/Paris",
        )
    )
    basic_plan_id = db_session.query(BillingPlanModel).filter_by(code="basic").one().id
    db_session.add(UserSubscriptionModel(user_id=user.id, plan_id=basic_plan_id, status="active"))
    db_session.commit()

    auth_user = AuthenticatedUser(
        id=user.id,
        email=user.email,
        role=user.role,
        created_at=datetime.now(UTC),
    )
    app.dependency_overrides[require_authenticated_user] = lambda: auth_user

    dummy_run = PersistedPredictionSnapshot(
        run_id=1,
        user_id=user.id,
        local_date=date(2026, 4, 4),
        timezone="Europe/Paris",
        computed_at=datetime(2026, 4, 4, 10, 0),
        input_hash="test-hash",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        is_provisional_calibration=False,
        calibration_label="test",
        overall_tone="positive",
        overall_summary="Test summary",
        category_scores=[],
        turning_points=[],
        time_blocks=[],
        llm_narrative=None,
    )
    mock_result = ServiceResult(run=dummy_run, bundle=None, was_reused=True)

    with (
        patch("app.api.v1.routers.public.predictions.settings") as mock_settings_router,
        patch("app.prediction.public_projection.settings") as mock_settings_proj,
        patch("app.domain.llm.prompting.context.CommonContextBuilder.build") as mock_ctx_build,
        patch("app.api.v1.routers.public.predictions.DailyPredictionService") as mock_service_cls,
        patch(
            "app.domain.llm.runtime.adapter.AIEngineAdapter.generate_horoscope_narration"
        ) as mock_adapter,
    ):
        mock_settings_router.llm_narrator_enabled = True
        mock_settings_router.ruleset_version = "2.0.0"
        mock_settings_router.active_reference_version = "2.0.0"
        mock_settings_proj.llm_narrator_enabled = True

        mock_ctx = MagicMock()
        mock_ctx.context_quality = "nominal"
        mock_ctx.missing_fields = []
        mock_ctx.payload.model_dump.return_value = {}
        mock_ctx_build.return_value = mock_ctx

        mock_service = mock_service_cls.return_value
        mock_service.get_or_compute.return_value = mock_result

        mock_adapter.return_value = NarratorResult(
            daily_synthesis="Synthèse du jour en plusieurs phrases.",
            astro_events_intro="Introduction narrative.",
            time_window_narratives={},
            turning_point_narratives=[],
        )

        response = client.get("/v1/predictions/daily")
        assert response.status_code == 200
    astrologer_chat_counter = (
        db_session.query(FeatureUsageCounterModel)
        .filter(FeatureUsageCounterModel.feature_code == "astrologer_chat")
        .first()
    )
    astrologer_chat_logs = (
        db_session.query(UserTokenUsageLogModel)
        .filter(UserTokenUsageLogModel.feature_code == "astrologer_chat")
        .all()
    )

    assert astrologer_chat_counter is None
    assert astrologer_chat_logs == []

    app.dependency_overrides.clear()

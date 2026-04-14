from datetime import UTC, date, datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.domain.astrology.natal_calculation import NatalResult
from app.infra.db.base import Base
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import get_db_session
from app.llm_orchestration.gateway import GatewayResult
from app.llm_orchestration.models import GatewayMeta, UsageInfo
from app.main import app
from app.services.billing_service import BillingService
from app.services.user_birth_profile_service import UserBirthProfileData
from app.services.user_natal_chart_service import UserNatalChartMetadata, UserNatalChartReadData


@pytest.fixture
def setup_natal_catalog(db_session: Session):
    bind = db_session.get_bind()
    Base.metadata.create_all(bind=bind)
    BillingService.reset_subscription_status_cache()

    f_short = FeatureCatalogModel(
        feature_code="natal_chart_short",
        feature_name="Short",
        is_metered=False,
    )
    f_long = FeatureCatalogModel(
        feature_code="natal_chart_long",
        feature_name="Long",
        is_metered=False,
    )
    db_session.add_all([f_short, f_long])

    cp_free = PlanCatalogModel(
        plan_code="free",
        plan_name="Free",
        audience=Audience.B2C,
        is_active=True,
    )
    db_session.add(cp_free)
    db_session.flush()

    bp_free = BillingPlanModel(
        code="free",
        display_name="Free",
        monthly_price_cents=0,
        currency="EUR",
        daily_message_limit=10,
        is_active=True,
    )
    db_session.add(bp_free)
    db_session.flush()

    db_session.add(
        PlanFeatureBindingModel(
            plan_id=cp_free.id,
            feature_id=f_short.id,
            is_enabled=True,
            access_mode=AccessMode.UNLIMITED,
        )
    )
    db_session.add(
        PlanFeatureBindingModel(
            plan_id=cp_free.id,
            feature_id=f_long.id,
            is_enabled=True,
            access_mode=AccessMode.UNLIMITED,
            variant_code="free_short",
        )
    )

    db_session.commit()


def test_interpret_natal_chart_free_user_gets_free_short_variant(
    db_session: Session,
    setup_natal_catalog,
):
    user = UserModel(email="free@example.com", password_hash="...", role="user")
    db_session.add(user)
    db_session.flush()

    db_session.add(
        UserBirthProfileModel(
            user_id=user.id,
            birth_date=date(1990, 1, 1),
            birth_time="12:00:00",
            birth_lat=48.8566,
            birth_lon=2.3522,
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
    )

    free_plan_id = db_session.query(BillingPlanModel).filter_by(code="free").one().id
    db_session.add(UserSubscriptionModel(user_id=user.id, plan_id=free_plan_id, status="active"))
    db_session.commit()

    auth_user = AuthenticatedUser(
        id=user.id,
        email=user.email,
        role=user.role,
        created_at=datetime.now(UTC),
    )
    app.dependency_overrides[require_authenticated_user] = lambda: auth_user
    app.dependency_overrides[get_db_session] = lambda: db_session

    client = TestClient(app)

    mock_natal_result = MagicMock(spec=NatalResult)
    mock_natal_result.reference_version = "2.0.0"
    mock_natal_result.ruleset_version = "2.0.0"
    mock_natal_result.zodiac = "tropical"
    mock_natal_result.house_system = "placidus"
    mock_natal_result.engine = "simplified"
    mock_natal_result.frame = "geocentric"
    mock_natal_result.ayanamsa = None
    mock_natal_result.aspect_school = "modern"
    mock_natal_result.altitude_m = 0.0
    mock_natal_result.prepared_input = MagicMock()
    mock_natal_result.sun = MagicMock()
    mock_natal_result.moon = MagicMock()
    mock_natal_result.mercury = MagicMock()
    mock_natal_result.venus = MagicMock()
    mock_natal_result.mars = MagicMock()
    mock_natal_result.jupiter = MagicMock()
    mock_natal_result.saturn = MagicMock()
    mock_natal_result.uranus = MagicMock()
    mock_natal_result.neptune = MagicMock()
    mock_natal_result.pluto = MagicMock()
    mock_natal_result.chiron = MagicMock()
    mock_natal_result.lilith = MagicMock()
    mock_natal_result.node = MagicMock()
    mock_natal_result.planet_positions = []
    mock_natal_result.houses = []
    mock_natal_result.aspects = []
    mock_natal_result.ephemeris_path_version = None
    mock_natal_result.ephemeris_path_hash = None
    mock_natal_result.model_dump.return_value = {}

    mock_chart_data = UserNatalChartReadData(
        chart_id="chart-123",
        result=mock_natal_result,
        metadata=MagicMock(spec=UserNatalChartMetadata),
        created_at=datetime.now(UTC),
    )
    mock_profile_data = UserBirthProfileData(
        user_id=user.id,
        birth_date="1990-01-01",
        birth_time="12:00:00",
        birth_lat=48.8566,
        birth_lon=2.3522,
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )

    with (
        patch(
            "app.api.v1.routers.natal_interpretation.UserNatalChartService.get_latest_for_user"
        ) as mock_get_chart,
        patch(
            "app.api.v1.routers.natal_interpretation.UserBirthProfileService.get_for_user"
        ) as mock_get_profile,
        patch("app.services.natal_interpretation_service_v2.build_chart_json") as mock_build_json,
    ):
        mock_get_chart.return_value = mock_chart_data
        mock_get_profile.return_value = mock_profile_data
        mock_build_json.return_value = {"dummy": "chart"}

        mock_meta = GatewayMeta(
            latency_ms=100,
            cached=False,
            prompt_version_id="00000000-0000-0000-0000-000000000000",
            persona_id=None,
            model="gpt-4o-mini",
            model_override_active=False,
            output_schema_id=None,
            schema_version="v1",
            validation_status="valid",
            repair_attempted=False,
            fallback_triggered=False,
        )
        mock_usage = UsageInfo(input_tokens=10, output_tokens=10, total_tokens=20)
        mock_output = {
            "title": "Votre thème révèle une intensité intuitive qui cherche l'équilibre.",
            "summary": "Resume free short",
            "accordion_titles": ["Section 1", "Section 2"],
        }
        mock_res = GatewayResult(
            use_case="natal_long_free",
            structured_output=mock_output,
            meta=mock_meta,
            request_id="req-123",
            trace_id="trace-123",
            raw_output="{}",
            usage=mock_usage,
        )

        with patch("app.llm_orchestration.gateway.LLMGateway.execute_request") as mock_execute:
            mock_execute.return_value = mock_res

            response = client.post(
                "/v1/natal/interpretation",
                json={
                    "use_case_level": "complete",
                    "locale": "fr-FR",
                    "force_refresh": True,
                },
            )

            assert response.status_code == 200
            data = response.json()["data"]
            assert data["use_case"] == "natal_long_free"
            assert (
                data["interpretation"]["title"]
                == "Votre thème révèle une intensité intuitive qui cherche l'équilibre."
            )
            assert data["interpretation"]["summary"] == "Resume free short"

            sections = data["interpretation"]["sections"]
            assert len(sections) == 2
            assert sections[0]["heading"] == "Section 1"
            assert sections[1]["heading"] == "Section 2"
            assert sections[0]["content"] == ""
            assert data["meta"]["level"] == "complete"

            _, kwargs = mock_execute.call_args
            assert kwargs["request"].user_input.use_case == "natal_long_free"
            assert kwargs["request"].user_input.feature == "natal"
            assert kwargs["request"].user_input.subfeature == "interpretation"

    app.dependency_overrides.clear()

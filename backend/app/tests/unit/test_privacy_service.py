from sqlalchemy import delete, func, select

from app.infra.db.base import Base
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
from app.infra.db.models.dignity_reference import AstralChartPlanetDignityResultModel
from app.infra.db.models.privacy import UserPrivacyRequestModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.repositories.dignity_reference_repository import (
    ChartPlanetDignityResultInput,
    DignityReferenceRepository,
)
from app.services.auth_service import AuthService
from app.services.privacy_service import PrivacyService, PrivacyServiceError
from app.services.reference_data_service import ReferenceDataService
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
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
            UserBirthProfileModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()


def _create_user_id() -> int:
    with open_app_test_db_session() as db:
        auth = AuthService.register(
            db,
            email="privacy-user@example.com",
            password="strong-pass-123",
            role="user",
        )
        db.commit()
        return auth.user.id


def test_request_export_returns_completed_request_with_counts() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with open_app_test_db_session() as db:
        result = PrivacyService.request_export(db, user_id=user_id, request_id="privacy-export-1")
        db.commit()

    assert result.request_kind == "export"
    assert result.status == "completed"
    assert result.result_data["user"]["email"] == "privacy-user@example.com"
    assert result.result_data["messages_count"] == 0


def test_get_latest_export_status_raises_when_absent() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with open_app_test_db_session() as db:
        try:
            PrivacyService.get_latest_export_status(db, user_id=user_id)
        except PrivacyServiceError as error:
            assert error.code == "privacy_not_found"
        else:
            raise AssertionError("Expected PrivacyServiceError")


def test_request_delete_anonymizes_account() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with open_app_test_db_session() as db:
        result = PrivacyService.request_delete(db, user_id=user_id, request_id="privacy-delete-1")
        db.commit()
        user = db.get(UserModel, user_id)
        assert user is not None
        assert user.email.startswith(f"deleted-user-{user_id}-")
        assert user.email.endswith("@deleted.local")
        profile = db.scalar(
            select(UserBirthProfileModel).where(UserBirthProfileModel.user_id == user_id)
        )
        assert profile is None

    assert result.request_kind == "delete"
    assert result.status == "completed"
    assert result.result_data["account_anonymized"] is True


def test_request_export_is_idempotent_after_completion() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with open_app_test_db_session() as db:
        first = PrivacyService.request_export(db, user_id=user_id, request_id="privacy-export-1")
        second = PrivacyService.request_export(db, user_id=user_id, request_id="privacy-export-2")
        db.commit()
        count = db.scalar(
            select(func.count(UserPrivacyRequestModel.id)).where(
                UserPrivacyRequestModel.user_id == user_id,
                UserPrivacyRequestModel.request_kind == "export",
            )
        )
    assert second.request_id == first.request_id
    assert count == 1


def test_request_delete_is_idempotent_after_completion() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with open_app_test_db_session() as db:
        first = PrivacyService.request_delete(db, user_id=user_id, request_id="privacy-delete-1")
        second = PrivacyService.request_delete(db, user_id=user_id, request_id="privacy-delete-2")
        db.commit()
        count = db.scalar(
            select(func.count(UserPrivacyRequestModel.id)).where(
                UserPrivacyRequestModel.user_id == user_id,
                UserPrivacyRequestModel.request_kind == "delete",
            )
        )
    assert second.request_id == first.request_id
    assert count == 1


def test_request_export_marks_request_failed_on_processing_error(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    user_id = _create_user_id()

    with open_app_test_db_session() as db:
        original_get = db.get

        def _failing_get(model: object, identity: object) -> object:
            if model == UserModel and identity == user_id:
                raise RuntimeError("storage failure")
            return original_get(model, identity)

        monkeypatch.setattr(db, "get", _failing_get)
        try:
            PrivacyService.request_export(db, user_id=user_id, request_id="privacy-export-fail-1")
        except PrivacyServiceError as error:
            assert error.code == "privacy_request_failed"
        else:
            raise AssertionError("Expected PrivacyServiceError")

        failed = db.scalar(
            select(UserPrivacyRequestModel)
            .where(UserPrivacyRequestModel.user_id == user_id)
            .where(UserPrivacyRequestModel.request_kind == "export")
            .order_by(UserPrivacyRequestModel.id.desc())
            .limit(1)
        )
        assert failed is not None
        assert failed.status == "failed"
        assert failed.error_reason == "privacy_request_failed"


def test_request_delete_removes_chart_with_dignity_audit_rows() -> None:
    """La suppression doit retirer les audits de dignité avant les thèmes astraux."""
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())

    user_id = _create_user_id()
    chart_result_id: int
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        chart_result = ChartResultModel(
            user_id=user_id,
            chart_id="privacy-delete-dignity-chart",
            reference_version="1.0.0",
            ruleset_version="test",
            input_hash="hash",
            result_payload={},
        )
        db.add(chart_result)
        db.flush()
        chart_result_id = chart_result.id
        DignityReferenceRepository(db).upsert_chart_planet_dignity_result(
            ChartPlanetDignityResultInput(
                chart_result_id=chart_result.id,
                planet_code="mars",
                score_profile_code="traditional_standard",
                astral_system_code="traditional",
                reference_version="1.0.0",
                essential_score=5,
                accidental_score=3,
                total_score=8,
                functional_strength_score=1.2,
                expression_quality_score=0.8,
                intensity_score=0.7,
                essential_breakdown_json=[{"type": "domicile"}],
                accidental_breakdown_json=[{"type": "angular_house"}],
                condition_summary_json={"detected": 2},
                calculation_context_json={"engine": "unit"},
            )
        )
        db.commit()

    with open_app_test_db_session() as db:
        result = PrivacyService.request_delete(
            db, user_id=user_id, request_id="privacy-delete-dignity"
        )
        db.commit()
        dignity_count = db.scalar(
            select(func.count(AstralChartPlanetDignityResultModel.id)).where(
                AstralChartPlanetDignityResultModel.chart_result_id == chart_result_id
            )
        )
        chart_count = db.scalar(
            select(func.count(ChartResultModel.id)).where(ChartResultModel.user_id == user_id)
        )

    assert result.status == "completed"
    assert dignity_count == 0
    assert chart_count == 0
    assert "astral_chart_planet_dignity_results" in result.result_data["deleted_entities"]

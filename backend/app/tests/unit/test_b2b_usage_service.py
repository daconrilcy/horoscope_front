from sqlalchemy import delete

from app.core.config import settings
from app.infra.db.base import Base
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_usage import EnterpriseDailyUsageModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.b2b_usage_service import B2BUsageService, B2BUsageServiceError
from app.services.enterprise_credentials_service import EnterpriseCredentialsService


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(EnterpriseDailyUsageModel))
        db.execute(delete(EnterpriseApiCredentialModel))
        db.execute(delete(EnterpriseAccountModel))
        db.execute(delete(UserModel))
        db.commit()


def _create_enterprise_credential() -> tuple[int, int]:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email="b2b-usage-service@example.com",
            password="strong-pass-123",
            role="enterprise_admin",
        )
        account = EnterpriseAccountModel(
            admin_user_id=auth.user.id,
            company_name="Acme Media",
            status="active",
        )
        db.add(account)
        db.flush()
        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()
        return account.id, created.credential_id


def test_b2b_usage_consume_and_summary_in_limit(monkeypatch: object) -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_credential()
    monkeypatch.setattr(settings, "b2b_daily_usage_limit", 3)
    monkeypatch.setattr(settings, "b2b_monthly_usage_limit", 10)
    monkeypatch.setattr(settings, "b2b_usage_limit_mode", "block")

    with SessionLocal() as db:
        first = B2BUsageService.consume_or_raise(
            db,
            account_id=account_id,
            credential_id=credential_id,
            request_id="rid-b2b-usage-1",
        )
        db.commit()
        assert first.daily_consumed == 1
        assert first.daily_remaining == 2
        assert first.blocked is False

        summary = B2BUsageService.get_usage_summary(
            db,
            account_id=account_id,
            credential_id=credential_id,
        )
        assert summary.daily_consumed == 1
        assert summary.monthly_consumed == 1


def test_b2b_usage_blocks_when_limit_exceeded_in_block_mode(monkeypatch: object) -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_credential()
    monkeypatch.setattr(settings, "b2b_daily_usage_limit", 1)
    monkeypatch.setattr(settings, "b2b_monthly_usage_limit", 2)
    monkeypatch.setattr(settings, "b2b_usage_limit_mode", "block")

    with SessionLocal() as db:
        B2BUsageService.consume_or_raise(
            db,
            account_id=account_id,
            credential_id=credential_id,
            request_id="rid-b2b-usage-2",
        )
        db.commit()
    with SessionLocal() as db:
        try:
            B2BUsageService.consume_or_raise(
                db,
                account_id=account_id,
                credential_id=credential_id,
                request_id="rid-b2b-usage-3",
            )
        except B2BUsageServiceError as error:
            assert error.code == "b2b_quota_exceeded"
            assert error.details["limit_mode"] == "block"
        else:
            raise AssertionError("expected B2BUsageServiceError")


def test_b2b_usage_allows_overage_when_mode_is_overage(monkeypatch: object) -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_credential()
    monkeypatch.setattr(settings, "b2b_daily_usage_limit", 1)
    monkeypatch.setattr(settings, "b2b_monthly_usage_limit", 2)
    monkeypatch.setattr(settings, "b2b_usage_limit_mode", "overage")

    with SessionLocal() as db:
        first = B2BUsageService.consume_or_raise(
            db,
            account_id=account_id,
            credential_id=credential_id,
            request_id="rid-b2b-usage-4",
        )
        second = B2BUsageService.consume_or_raise(
            db,
            account_id=account_id,
            credential_id=credential_id,
            request_id="rid-b2b-usage-5",
        )
        db.commit()

    assert first.overage_applied is False
    assert second.overage_applied is True
    assert second.daily_consumed == 2
    assert second.daily_remaining == 0
    assert second.blocked is False

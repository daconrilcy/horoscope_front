from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.enterprise_credentials_service import (
    EnterpriseCredentialsService,
    EnterpriseCredentialsServiceError,
)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(EnterpriseApiCredentialModel))
        db.execute(delete(EnterpriseAccountModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_enterprise_admin_with_account(
    email: str, *, status: str = "active"
) -> tuple[int, str]:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email=email,
            password="strong-pass-123",
            role="enterprise_admin",
        )
        account = EnterpriseAccountModel(
            admin_user_id=auth.user.id,
            company_name="Acme Media",
            status=status,
        )
        db.add(account)
        db.commit()
        return auth.user.id, auth.tokens.access_token


def test_authenticate_api_key_accepts_active_key() -> None:
    _cleanup_tables()
    admin_user_id, _ = _register_enterprise_admin_with_account("b2b-auth-active@example.com")
    with SessionLocal() as db:
        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=admin_user_id)
        db.commit()

    with SessionLocal() as db:
        authenticated = EnterpriseCredentialsService.authenticate_api_key(
            db, api_key=created.api_key
        )
        assert authenticated.credential_status == "active"
        assert authenticated.account_status == "active"
        assert authenticated.credential_id == created.credential_id


def test_authenticate_api_key_rejects_revoked_key() -> None:
    _cleanup_tables()
    admin_user_id, _ = _register_enterprise_admin_with_account("b2b-auth-revoked@example.com")
    with SessionLocal() as db:
        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=admin_user_id)
        db.commit()
    with SessionLocal() as db:
        EnterpriseCredentialsService.rotate_credential(db, admin_user_id=admin_user_id)
        db.commit()
    with SessionLocal() as db:
        try:
            EnterpriseCredentialsService.authenticate_api_key(db, api_key=created.api_key)
        except EnterpriseCredentialsServiceError as error:
            assert error.code == "revoked_api_key"
        else:
            raise AssertionError("expected EnterpriseCredentialsServiceError")


def test_authenticate_api_key_rejects_invalid_key() -> None:
    _cleanup_tables()
    admin_user_id, _ = _register_enterprise_admin_with_account("b2b-auth-invalid@example.com")
    with SessionLocal() as db:
        EnterpriseCredentialsService.create_credential(db, admin_user_id=admin_user_id)
        db.commit()
    with SessionLocal() as db:
        try:
            EnterpriseCredentialsService.authenticate_api_key(
                db, api_key="b2b_invalid_unknown_secret"
            )
        except EnterpriseCredentialsServiceError as error:
            assert error.code == "invalid_api_key"
        else:
            raise AssertionError("expected EnterpriseCredentialsServiceError")

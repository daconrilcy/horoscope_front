from sqlalchemy import delete, select

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


def _register_enterprise_admin_with_account(email: str) -> int:
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
            status="active",
        )
        db.add(account)
        db.commit()
        return auth.user.id


def test_create_credential_persists_hashed_secret_only() -> None:
    _cleanup_tables()
    admin_user_id = _register_enterprise_admin_with_account("b2b-admin-create@example.com")

    with SessionLocal() as db:
        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=admin_user_id)
        db.commit()
        credential = db.scalar(
            select(EnterpriseApiCredentialModel).where(
                EnterpriseApiCredentialModel.id == created.credential_id
            )
        )
        assert credential is not None
        assert credential.status == "active"
        assert credential.secret_hash != created.api_key
        assert created.api_key.startswith("b2b_")


def test_rotate_credential_revokes_previous_and_activates_new() -> None:
    _cleanup_tables()
    admin_user_id = _register_enterprise_admin_with_account("b2b-admin-rotate@example.com")

    with SessionLocal() as db:
        first = EnterpriseCredentialsService.create_credential(db, admin_user_id=admin_user_id)
        db.commit()

    with SessionLocal() as db:
        rotated = EnterpriseCredentialsService.rotate_credential(db, admin_user_id=admin_user_id)
        db.commit()
        credentials = db.scalars(
            select(EnterpriseApiCredentialModel)
            .where(EnterpriseApiCredentialModel.created_by_user_id == admin_user_id)
            .order_by(EnterpriseApiCredentialModel.id.asc())
        ).all()
        assert len(credentials) == 2
        assert credentials[0].id == first.credential_id
        assert credentials[0].status == "revoked"
        assert credentials[0].revoked_at is not None
        assert credentials[1].id == rotated.credential_id
        assert credentials[1].status == "active"


def test_create_credential_fails_when_active_exists() -> None:
    _cleanup_tables()
    admin_user_id = _register_enterprise_admin_with_account("b2b-admin-existing@example.com")
    with SessionLocal() as db:
        EnterpriseCredentialsService.create_credential(db, admin_user_id=admin_user_id)
        db.commit()

    with SessionLocal() as db:
        try:
            EnterpriseCredentialsService.create_credential(db, admin_user_id=admin_user_id)
        except EnterpriseCredentialsServiceError as error:
            assert error.code == "credential_already_exists"
        else:
            raise AssertionError("expected EnterpriseCredentialsServiceError")


def test_rotate_credential_fails_without_active_credential() -> None:
    _cleanup_tables()
    admin_user_id = _register_enterprise_admin_with_account("b2b-admin-missing@example.com")
    with SessionLocal() as db:
        try:
            EnterpriseCredentialsService.rotate_credential(db, admin_user_id=admin_user_id)
        except EnterpriseCredentialsServiceError as error:
            assert error.code == "credential_not_found"
        else:
            raise AssertionError("expected EnterpriseCredentialsServiceError")


def test_authenticate_api_key_accepts_previous_rotation_secret(monkeypatch: object) -> None:
    _cleanup_tables()
    admin_user_id = _register_enterprise_admin_with_account("b2b-admin-rotation-auth@example.com")

    with SessionLocal() as db:
        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=admin_user_id)
        db.commit()

    from app.core import config as config_module

    old_secret = config_module.settings.api_credentials_secret_key
    monkeypatch.setattr(config_module.settings, "api_credentials_secret_key", "new-api-secret-key")
    monkeypatch.setattr(
        config_module.settings,
        "api_credentials_previous_secret_keys",
        [old_secret],
    )

    with SessionLocal() as db:
        auth_data = EnterpriseCredentialsService.authenticate_api_key(db, api_key=created.api_key)
        assert auth_data.credential_status == "active"

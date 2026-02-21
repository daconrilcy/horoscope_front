from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_editorial_config import EnterpriseEditorialConfigModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.b2b_editorial_service import (
    B2BEditorialConfigUpdatePayload,
    B2BEditorialService,
)
from app.services.enterprise_credentials_service import EnterpriseCredentialsService


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(EnterpriseEditorialConfigModel))
        db.execute(delete(EnterpriseApiCredentialModel))
        db.execute(delete(EnterpriseAccountModel))
        db.execute(delete(UserModel))
        db.commit()


def _create_enterprise_context() -> tuple[int, int]:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email="b2b-editorial-service@example.com",
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


def test_editorial_default_config_is_returned_when_missing() -> None:
    _cleanup_tables()
    account_id, _ = _create_enterprise_context()

    with SessionLocal() as db:
        config = B2BEditorialService.get_active_config(db, account_id=account_id)
    assert config.version_number == 0
    assert config.output_format == "paragraph"
    assert config.preferred_terms == []


def test_editorial_upsert_creates_new_version() -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context()

    with SessionLocal() as db:
        first = B2BEditorialService.upsert_config(
            db,
            account_id=account_id,
            credential_id=credential_id,
            payload=B2BEditorialConfigUpdatePayload(
                tone="friendly",
                length_style="short",
                output_format="bullet",
                preferred_terms=["focus"],
                avoided_terms=["drama"],
            ),
        )
        second = B2BEditorialService.upsert_config(
            db,
            account_id=account_id,
            credential_id=credential_id,
            payload=B2BEditorialConfigUpdatePayload(
                tone="premium",
                length_style="long",
                output_format="paragraph",
                preferred_terms=["clarte"],
                avoided_terms=["confusion"],
            ),
        )
        db.commit()

    assert first.version_number == 1
    assert second.version_number == 2
    assert second.tone == "premium"


def test_editorial_render_applies_format_terms_and_filters() -> None:
    config = B2BEditorialConfigUpdatePayload(
        tone="friendly",
        length_style="short",
        output_format="bullet",
        preferred_terms=["focus", "ancrage"],
        avoided_terms=["ancrage"],
    )
    rendered = B2BEditorialService.render_weekly_summary(
        sign_name="Aries",
        config=B2BEditorialService.default_config(account_id=1).model_copy(
            update=config.model_dump()
        ),
    )
    assert rendered.startswith("- Conseil Aries:")
    assert "focus" in rendered
    assert "ancrage" not in rendered.lower()

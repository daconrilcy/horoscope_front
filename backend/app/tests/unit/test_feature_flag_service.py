from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.feature_flag import FeatureFlagModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.feature_flag_service import FeatureFlagService, FeatureFlagUpdatePayload


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(FeatureFlagModel))
        db.execute(delete(UserModel))
        db.commit()


def _create_user_id(email: str = "flag-user@example.com") -> int:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role="user")
        db.commit()
        return auth.user.id


def test_feature_flags_seed_and_update() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        initial = FeatureFlagService.list_flags(db)
        assert initial.total == 2
        assert {flag.key for flag in initial.flags} == {"runes_enabled", "tarot_enabled"}

        updated = FeatureFlagService.update_flag(
            db,
            key="tarot_enabled",
            payload=FeatureFlagUpdatePayload(
                enabled=True,
                target_roles=["user"],
                target_user_ids=[user_id],
            ),
            updated_by_user_id=user_id,
        )
        db.commit()

    assert updated.enabled is True
    assert updated.target_roles == ["user"]
    assert updated.target_user_ids == [user_id]


def test_module_availability_respects_segments() -> None:
    _cleanup_tables()
    allowed_user_id = _create_user_id("flag-allowed@example.com")
    blocked_user_id = _create_user_id("flag-blocked@example.com")
    with SessionLocal() as db:
        FeatureFlagService.update_flag(
            db,
            key="runes_enabled",
            payload=FeatureFlagUpdatePayload(
                enabled=True,
                target_roles=["user"],
                target_user_ids=[allowed_user_id],
            ),
            updated_by_user_id=allowed_user_id,
        )
        db.commit()

        allowed = FeatureFlagService.get_module_availability(
            db,
            module="runes",
            user_id=allowed_user_id,
            user_role="user",
        )
        blocked = FeatureFlagService.get_module_availability(
            db,
            module="runes",
            user_id=blocked_user_id,
            user_role="user",
        )

    assert allowed.available is True
    assert allowed.status == "module-ready"
    assert blocked.available is False
    assert blocked.reason == "segment_mismatch"

import pytest
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.persona_config import PersonaConfigModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.persona_config_service import (
    PersonaConfigService,
    PersonaConfigServiceError,
    PersonaConfigUpdatePayload,
    PersonaProfileCreatePayload,
)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(PersonaConfigModel))
        db.execute(delete(UserModel))
        db.commit()


def _create_ops_user_id() -> int:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email="persona-ops@example.com",
            password="strong-pass-123",
            role="ops",
        )
        db.commit()
        return auth.user.id


def test_get_active_returns_default_config_when_none_exists() -> None:
    _cleanup_tables()
    with SessionLocal() as db:
        active = PersonaConfigService.get_active(db)
    assert active.is_default is True
    assert active.version == 0
    assert active.tone == "calm"
    assert active.profile_code == "legacy-default"
    assert active.fallback_policy == "safe_fallback"


def test_update_active_creates_new_active_version() -> None:
    _cleanup_tables()
    user_id = _create_ops_user_id()
    with SessionLocal() as db:
        updated = PersonaConfigService.update_active(
            db,
            user_id=user_id,
            payload=PersonaConfigUpdatePayload(
                tone="direct",
                prudence_level="high",
                scope_policy="balanced",
                response_style="detailed",
            ),
        )
        db.commit()
    assert updated.is_default is False
    assert updated.version == 1
    assert updated.status == "active"
    assert updated.tone == "direct"
    assert updated.profile_code == "legacy-default"


def test_update_active_is_idempotent_for_identical_payload() -> None:
    _cleanup_tables()
    user_id = _create_ops_user_id()
    with SessionLocal() as db:
        first = PersonaConfigService.update_active(
            db,
            user_id=user_id,
            payload=PersonaConfigUpdatePayload(
                tone="direct",
                prudence_level="high",
                scope_policy="balanced",
                response_style="detailed",
            ),
        )
        second = PersonaConfigService.update_active(
            db,
            user_id=user_id,
            payload=PersonaConfigUpdatePayload(
                tone="direct",
                prudence_level="high",
                scope_policy="balanced",
                response_style="detailed",
            ),
        )
        total_rows = len(list(db.scalars(select(PersonaConfigModel))))
        db.commit()

    assert first.id == second.id
    assert first.version == second.version
    assert total_rows == 1


def test_update_active_rejects_invalid_payload() -> None:
    _cleanup_tables()
    user_id = _create_ops_user_id()
    with SessionLocal() as db:
        with pytest.raises(PersonaConfigServiceError) as error:
            PersonaConfigService.update_active(
                db,
                user_id=user_id,
                payload=PersonaConfigUpdatePayload(
                    tone="invalid",
                    prudence_level="high",
                    scope_policy="balanced",
                    response_style="detailed",
                ),
            )
    assert error.value.code == "invalid_persona_config"


def test_rollback_active_reactivates_previous_version() -> None:
    _cleanup_tables()
    user_id = _create_ops_user_id()
    with SessionLocal() as db:
        first = PersonaConfigService.update_active(
            db,
            user_id=user_id,
            payload=PersonaConfigUpdatePayload(
                tone="calm",
                prudence_level="high",
                scope_policy="strict",
                response_style="concise",
            ),
        )
        second = PersonaConfigService.update_active(
            db,
            user_id=user_id,
            payload=PersonaConfigUpdatePayload(
                tone="direct",
                prudence_level="standard",
                scope_policy="balanced",
                response_style="detailed",
            ),
        )
        rolled_back = PersonaConfigService.rollback_active(db, user_id=user_id)
        db.commit()

    assert first.version == 1
    assert second.version == 2
    assert rolled_back.rolled_back_version == 2
    assert rolled_back.active.version == 1
    assert rolled_back.active.status == "active"
    assert rolled_back.active.created_by_user_id == first.created_by_user_id


def test_rollback_ignores_rolled_back_versions() -> None:
    _cleanup_tables()
    user_id = _create_ops_user_id()
    with SessionLocal() as db:
        PersonaConfigService.update_active(
            db,
            user_id=user_id,
            payload=PersonaConfigUpdatePayload(
                tone="calm",
                prudence_level="high",
                scope_policy="strict",
                response_style="concise",
            ),
        )
        PersonaConfigService.update_active(
            db,
            user_id=user_id,
            payload=PersonaConfigUpdatePayload(
                tone="direct",
                prudence_level="standard",
                scope_policy="balanced",
                response_style="detailed",
            ),
        )
        PersonaConfigService.rollback_active(db, user_id=user_id)
        third = PersonaConfigService.update_active(
            db,
            user_id=user_id,
            payload=PersonaConfigUpdatePayload(
                tone="empathetic",
                prudence_level="high",
                scope_policy="strict",
                response_style="detailed",
            ),
        )
        rolled_back = PersonaConfigService.rollback_active(db, user_id=user_id)
        db.commit()

    assert third.version == 3
    assert rolled_back.rolled_back_version == 3
    assert rolled_back.active.version == 1


def test_create_profile_activate_archive_restore_and_list() -> None:
    _cleanup_tables()
    user_id = _create_ops_user_id()
    with SessionLocal() as db:
        created = PersonaConfigService.create_profile(
            db,
            user_id=user_id,
            payload=PersonaProfileCreatePayload(
                profile_code="sage-astro",
                display_name="Sage Astrologue",
                tone="empathetic",
                prudence_level="high",
                scope_policy="strict",
                response_style="detailed",
                fallback_policy="safe_fallback",
                activate=False,
            ),
        )
        assert created.status == "inactive"
        activated = PersonaConfigService.activate_profile(
            db,
            user_id=user_id,
            profile_id=created.id or -1,
        )
        assert activated.status == "active"
        with pytest.raises(PersonaConfigServiceError) as archive_active_error:
            PersonaConfigService.archive_profile(
                db,
                user_id=user_id,
                profile_id=activated.id or -1,
            )
        assert archive_active_error.value.code == "persona_profile_archive_forbidden"

        updated_default = PersonaConfigService.update_active(
            db,
            user_id=user_id,
            payload=PersonaConfigUpdatePayload(
                tone="direct",
                prudence_level="high",
                scope_policy="balanced",
                response_style="detailed",
            ),
        )
        assert updated_default.status == "active"
        archived = PersonaConfigService.archive_profile(
            db,
            user_id=user_id,
            profile_id=created.id or -1,
        )
        assert archived.status == "archived"
        restored = PersonaConfigService.restore_profile(
            db,
            user_id=user_id,
            profile_id=created.id or -1,
        )
        assert restored.status == "inactive"
        profiles = PersonaConfigService.list_profiles(db)
        db.commit()

    assert profiles.total >= 2
    assert any(item.profile_code == "sage-astro" for item in profiles.items)

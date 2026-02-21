from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.repositories.reference_repository import ReferenceRepository


class ReferenceDataServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ReferenceDataService:
    @staticmethod
    def seed_reference_version(db: Session, version: str | None = None) -> str:
        target_version = version or settings.active_reference_version
        repo = ReferenceRepository(db)
        model = repo.get_version(target_version)
        if model is None:
            model = repo.create_version(target_version, description="Initial seeded version")
            repo.seed_version_defaults(model.id)
        elif not repo.has_version_data(model.id):
            repo.seed_version_defaults(model.id)

        db.commit()
        return target_version

    @staticmethod
    def get_active_reference_data(db: Session, version: str | None = None) -> dict[str, object]:
        target_version = version or settings.active_reference_version
        return ReferenceRepository(db).get_reference_data(target_version)

    @staticmethod
    def clone_reference_version(db: Session, source_version: str, new_version: str) -> str:
        repo = ReferenceRepository(db)
        source_model = repo.get_version(source_version)
        if source_model is None:
            raise ReferenceDataServiceError(
                code="reference_source_not_found",
                message="source reference version was not found",
                details={"source_version": source_version},
            )

        if repo.get_version(new_version) is not None:
            raise ReferenceDataServiceError(
                code="reference_target_exists",
                message="target reference version already exists",
                details={"new_version": new_version},
            )

        try:
            target = repo.create_version(new_version, description=f"Cloned from {source_version}")
            repo.clone_version_data(source_model.id, target.id)
            db.commit()
        except IntegrityError as error:
            db.rollback()
            raise ReferenceDataServiceError(
                code="reference_clone_conflict",
                message="reference clone could not be persisted",
                details={"new_version": new_version},
            ) from error
        except ValueError as error:
            db.rollback()
            raise ReferenceDataServiceError(
                code="reference_version_immutable",
                message="reference version is immutable",
                details={"new_version": new_version},
            ) from error
        return new_version

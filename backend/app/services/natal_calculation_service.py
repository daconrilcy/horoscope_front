from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.astrology.natal_calculation import (
    NatalCalculationError,
    NatalResult,
    build_natal_result,
)
from app.domain.astrology.natal_preparation import BirthInput
from app.services.reference_data_service import ReferenceDataService


class NatalCalculationService:
    @staticmethod
    def calculate(
        db: Session,
        birth_input: BirthInput,
        reference_version: str | None = None,
        timeout_check: Callable[[], None] | None = None,
    ) -> NatalResult:
        reference_data = ReferenceDataService.get_active_reference_data(
            db,
            version=reference_version,
        )
        if not reference_data:
            raise NatalCalculationError(
                code="reference_version_not_found",
                message="reference version not found",
                details={"version": reference_version or settings.active_reference_version},
            )

        return build_natal_result(
            birth_input=birth_input,
            reference_data=reference_data,
            ruleset_version=settings.ruleset_version,
            timeout_check=timeout_check,
        )

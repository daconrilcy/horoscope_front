from __future__ import annotations

import json
from datetime import date
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.infra.db.models.prediction_ruleset import (
    CategoryCalibrationModel,
    PredictionRulesetModel,
    RulesetEventTypeModel,
    RulesetParameterModel,
)
from app.infra.db.repositories.prediction_schemas import (
    CalibrationData,
    EventTypeData,
    RulesetContext,
    RulesetData,
)


class PredictionRulesetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_ruleset(self, version: str) -> RulesetData | None:
        row = self.db.execute(
            select(PredictionRulesetModel).where(PredictionRulesetModel.version == version)
        ).scalar_one_or_none()

        if not row:
            return None

        return RulesetData(
            id=row.id,
            version=row.version,
            reference_version_id=row.reference_version_id,
            zodiac_type=row.zodiac_type,
            coordinate_mode=row.coordinate_mode,
            house_system=row.house_system,
            time_step_minutes=row.time_step_minutes,
            is_locked=row.is_locked,
        )

    def get_parameters(self, ruleset_id: int) -> dict[str, Any]:
        rows = (
            self.db.execute(
                select(RulesetParameterModel).where(RulesetParameterModel.ruleset_id == ruleset_id)
            )
            .scalars()
            .all()
        )

        return {row.param_key: self._convert_param(row.param_value, row.data_type) for row in rows}

    def get_event_types(self, ruleset_id: int) -> dict[str, EventTypeData]:
        rows = (
            self.db.execute(
                select(RulesetEventTypeModel).where(RulesetEventTypeModel.ruleset_id == ruleset_id)
            )
            .scalars()
            .all()
        )

        return {
            row.code: EventTypeData(
                id=row.id,
                code=row.code,
                name=row.name,
                event_group=row.event_group,
                priority=row.priority,
                base_weight=row.base_weight,
            )
            for row in rows
        }

    def get_calibrations(
        self, ruleset_id: int, category_id: int, reference_date: date
    ) -> CalibrationData | None:
        row = self.db.execute(
            select(CategoryCalibrationModel)
            .where(
                CategoryCalibrationModel.ruleset_id == ruleset_id,
                CategoryCalibrationModel.category_id == category_id,
                CategoryCalibrationModel.valid_from <= reference_date,
                or_(
                    CategoryCalibrationModel.valid_to >= reference_date,
                    CategoryCalibrationModel.valid_to.is_(None),
                ),
            )
            .order_by(CategoryCalibrationModel.valid_from.desc())
            .limit(1)
        ).scalar_one_or_none()

        if not row:
            return None

        return CalibrationData(
            p05=row.p05,
            p25=row.p25,
            p50=row.p50,
            p75=row.p75,
            p95=row.p95,
            sample_size=row.sample_size,
        )

    def get_active_ruleset_context(self, version: str, reference_date: date | None = None) -> RulesetContext | None:
        del reference_date  # reserved for future calibration filtering
        ruleset = self.get_ruleset(version)
        if not ruleset:
            return None

        return RulesetContext(
            ruleset=ruleset,
            parameters=self.get_parameters(ruleset.id),
            event_types=self.get_event_types(ruleset.id),
        )

    def _convert_param(self, value: str, data_type: str) -> Any:
        match data_type:
            case "float":
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0
            case "int":
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return 0
            case "bool":
                return str(value).lower() in ("true", "1", "yes") if value is not None else False
            case "json":
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return {}
            case _:
                return value

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infra.db.models.calibration import CalibrationRawDayModel


class CalibrationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_existing_category_codes(
        self,
        profile_label: str,
        local_date: date,
        reference_version: str,
        ruleset_version: str,
    ) -> frozenset[str]:
        rows = self.db.execute(
            select(CalibrationRawDayModel.category_code).where(
                CalibrationRawDayModel.profile_label == profile_label,
                CalibrationRawDayModel.local_date == local_date,
                CalibrationRawDayModel.reference_version == reference_version,
                CalibrationRawDayModel.ruleset_version == ruleset_version,
            )
        ).scalars()
        return frozenset(rows)

    def exists(
        self,
        profile_label: str,
        local_date: date,
        category_code: str,
        reference_version: str,
        ruleset_version: str,
    ) -> bool:
        return self.db.scalar(
            select(CalibrationRawDayModel).where(
                CalibrationRawDayModel.profile_label == profile_label,
                CalibrationRawDayModel.local_date == local_date,
                CalibrationRawDayModel.category_code == category_code,
                CalibrationRawDayModel.reference_version == reference_version,
                CalibrationRawDayModel.ruleset_version == ruleset_version,
            )
        ) is not None

    def save(self, raw_day: CalibrationRawDayModel) -> None:
        self.db.add(raw_day)
        self.db.flush()

    def count(self, reference_version: str, ruleset_version: str) -> int:
        return self.db.scalar(
            select(func.count(CalibrationRawDayModel.id)).where(
                CalibrationRawDayModel.reference_version == reference_version,
                CalibrationRawDayModel.ruleset_version == ruleset_version,
            )
        ) or 0

    def get_raw_scores_by_category(
        self, reference_version: str, ruleset_version: str
    ) -> dict[str, list[float]]:
        results = self.db.execute(
            select(CalibrationRawDayModel.category_code, CalibrationRawDayModel.raw_score).where(
                CalibrationRawDayModel.reference_version == reference_version,
                CalibrationRawDayModel.ruleset_version == ruleset_version,
            )
        ).all()

        scores_by_cat: dict[str, list[float]] = {}
        for cat_code, score in results:
            if cat_code not in scores_by_cat:
                scores_by_cat[cat_code] = []
            scores_by_cat[cat_code].append(score)
        return scores_by_cat

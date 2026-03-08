from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.infra.db.models.daily_prediction import (
    DailyPredictionCategoryScoreModel,
    DailyPredictionRunModel,
    DailyPredictionTimeBlockModel,
    DailyPredictionTurningPointModel,
)


class DailyPredictionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_run_by_hash(self, user_id: int, input_hash: str) -> DailyPredictionRunModel | None:
        return self.db.scalar(
            select(DailyPredictionRunModel).where(
                DailyPredictionRunModel.user_id == user_id,
                DailyPredictionRunModel.input_hash == input_hash,
            )
        )

    def create_run(
        self,
        user_id: int,
        local_date: date,
        timezone: str,
        reference_version_id: int,
        ruleset_id: int,
        input_hash: str | None = None,
        house_system_effective: str | None = None,
        is_provisional_calibration: bool | None = None,
        calibration_label: str | None = None,
        overall_summary: str | None = None,
        overall_tone: str | None = None,
        main_turning_point_at: datetime | None = None,
    ) -> DailyPredictionRunModel:
        run = DailyPredictionRunModel(
            user_id=user_id,
            local_date=local_date,
            timezone=timezone,
            reference_version_id=reference_version_id,
            ruleset_id=ruleset_id,
            input_hash=input_hash,
            house_system_effective=house_system_effective,
            is_provisional_calibration=is_provisional_calibration,
            calibration_label=calibration_label,
            overall_summary=overall_summary,
            overall_tone=overall_tone,
            main_turning_point_at=main_turning_point_at,
            computed_at=datetime.now(UTC),
        )
        self.db.add(run)
        self.db.flush()
        return run

    def get_run(
        self,
        user_id: int,
        local_date: date,
        reference_version_id: int,
        ruleset_id: int,
    ) -> DailyPredictionRunModel | None:
        return self.db.scalar(
            select(DailyPredictionRunModel).where(
                DailyPredictionRunModel.user_id == user_id,
                DailyPredictionRunModel.local_date == local_date,
                DailyPredictionRunModel.reference_version_id == reference_version_id,
                DailyPredictionRunModel.ruleset_id == ruleset_id,
            )
        )

    def get_or_create_run(
        self,
        user_id: int,
        local_date: date,
        timezone: str,
        reference_version_id: int,
        ruleset_id: int,
        input_hash: str | None = None,
    ) -> tuple[DailyPredictionRunModel, bool]:
        run = self.get_run(user_id, local_date, reference_version_id, ruleset_id)
        if run is None:
            created_run = self.create_run(
                user_id=user_id,
                local_date=local_date,
                timezone=timezone,
                reference_version_id=reference_version_id,
                ruleset_id=ruleset_id,
                input_hash=input_hash,
            )
            created_run.needs_recompute = False
            return (created_run, True)

        # Policy: if input_hash is provided and different, invalidate children
        if input_hash is not None and run.input_hash != input_hash:
            self.db.execute(
                delete(DailyPredictionCategoryScoreModel).where(
                    DailyPredictionCategoryScoreModel.run_id == run.id
                )
            )
            self.db.execute(
                delete(DailyPredictionTurningPointModel).where(
                    DailyPredictionTurningPointModel.run_id == run.id
                )
            )
            self.db.execute(
                delete(DailyPredictionTimeBlockModel).where(
                    DailyPredictionTimeBlockModel.run_id == run.id
                )
            )

            run.input_hash = input_hash
            run.computed_at = datetime.now(UTC)
            run.needs_recompute = True
            self.db.flush()
            self.db.expire(run, ["category_scores", "turning_points", "time_blocks"])
        else:
            run.needs_recompute = False

        return (run, False)

    def upsert_category_scores(self, run_id: int, scores: list[dict[str, Any]]) -> None:
        # Simple DELETE + INSERT pattern
        self.db.execute(
            delete(DailyPredictionCategoryScoreModel).where(
                DailyPredictionCategoryScoreModel.run_id == run_id
            )
        )
        for score_data in scores:
            score = DailyPredictionCategoryScoreModel(run_id=run_id, **score_data)
            self.db.add(score)
        self.db.flush()
        self.db.expire_all()

    def upsert_turning_points(self, run_id: int, turning_points: list[dict[str, Any]]) -> None:
        self.db.execute(
            delete(DailyPredictionTurningPointModel).where(
                DailyPredictionTurningPointModel.run_id == run_id
            )
        )
        for tp_data in turning_points:
            tp = DailyPredictionTurningPointModel(run_id=run_id, **tp_data)
            self.db.add(tp)
        self.db.flush()
        self.db.expire_all()

    def upsert_time_blocks(self, run_id: int, blocks: list[dict[str, Any]]) -> None:
        self.db.execute(
            delete(DailyPredictionTimeBlockModel).where(
                DailyPredictionTimeBlockModel.run_id == run_id
            )
        )
        for block_data in blocks:
            block = DailyPredictionTimeBlockModel(run_id=run_id, **block_data)
            self.db.add(block)
        self.db.flush()
        self.db.expire_all()

    def get_full_run(self, run_id: int) -> dict[str, Any] | None:
        run = self.db.scalar(
            select(DailyPredictionRunModel)
            .execution_options(populate_existing=True)
            .options(
                selectinload(DailyPredictionRunModel.category_scores),
                selectinload(DailyPredictionRunModel.turning_points),
                selectinload(DailyPredictionRunModel.time_blocks),
            )
            .where(DailyPredictionRunModel.id == run_id)
        )
        if run is None:
            return None

        return {
            "id": run.id,
            "user_id": run.user_id,
            "local_date": run.local_date.isoformat(),
            "timezone": run.timezone,
            "reference_version_id": run.reference_version_id,
            "ruleset_id": run.ruleset_id,
            "input_hash": run.input_hash,
            "computed_at": run.computed_at.isoformat(),
            "house_system_effective": run.house_system_effective,
            "is_provisional_calibration": run.is_provisional_calibration,
            "calibration_label": run.calibration_label,
            "overall_summary": run.overall_summary,
            "overall_tone": run.overall_tone,
            "main_turning_point_at": (
                run.main_turning_point_at.isoformat() if run.main_turning_point_at else None
            ),
            "category_scores": [
                {
                    "category_id": s.category_id,
                    "raw_score": s.raw_score,
                    "normalized_score": s.normalized_score,
                    "note_20": s.note_20,
                    "power": s.power,
                    "volatility": s.volatility,
                    "rank": s.rank,
                    "summary": s.summary,
                    "contributors_json": s.contributors_json,
                }
                for s in run.category_scores
            ],
            "turning_points": [
                {
                    "occurred_at_local": tp.occurred_at_local.isoformat()
                    if tp.occurred_at_local
                    else None,
                    "event_type_id": tp.event_type_id,
                    "severity": tp.severity,
                    "driver_json": tp.driver_json,
                    "summary": tp.summary,
                }
                for tp in run.turning_points
            ],
            "time_blocks": [
                {
                    "block_index": b.block_index,
                    "start_at_local": b.start_at_local.isoformat() if b.start_at_local else None,
                    "end_at_local": b.end_at_local.isoformat() if b.end_at_local else None,
                    "tone_code": b.tone_code,
                    "dominant_categories_json": b.dominant_categories_json,
                    "summary": b.summary,
                }
                for b in sorted(run.time_blocks, key=lambda x: x.block_index)
            ],
        }

    def get_user_history(
        self, user_id: int, from_date: date, to_date: date
    ) -> list[DailyPredictionRunModel]:
        return list(
            self.db.scalars(
                select(DailyPredictionRunModel)
                .options(
                    selectinload(DailyPredictionRunModel.category_scores),
                    selectinload(DailyPredictionRunModel.turning_points),
                )
                .where(
                    DailyPredictionRunModel.user_id == user_id,
                    DailyPredictionRunModel.local_date >= from_date,
                    DailyPredictionRunModel.local_date <= to_date,
                )
                .order_by(DailyPredictionRunModel.local_date.desc())
            ).all()
        )

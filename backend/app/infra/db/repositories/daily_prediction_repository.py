from __future__ import annotations

import json
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
from app.prediction.persisted_snapshot import (
    PersistedCategoryScore,
    PersistedPredictionSnapshot,
    PersistedTimeBlock,
    PersistedTurningPoint,
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

    def get_run_for_reuse(
        self, user_id: int, input_hash: str
    ) -> PersistedPredictionSnapshot | None:
        """
        Retrieves a run by hash and returns a typed snapshot for reuse decision.
        AC2 Compliance: Explicit naming for technical reuse.
        """
        run = self.db.scalar(
            select(DailyPredictionRunModel)
            .options(
                selectinload(DailyPredictionRunModel.category_scores).selectinload(
                    DailyPredictionCategoryScoreModel.category
                ),
                selectinload(DailyPredictionRunModel.time_blocks),
                selectinload(DailyPredictionRunModel.turning_points),
            )
            .where(
                DailyPredictionRunModel.user_id == user_id,
                DailyPredictionRunModel.input_hash == input_hash,
            )
        )
        return self.get_snapshot(run) if run else None

    def get_run_for_fallback(
        self, user_id: int, date_local: date
    ) -> PersistedPredictionSnapshot | None:
        """
        Retrieves the most recent run before a specific date for fallback.
        AC2 Compliance: Explicit naming for business fallback.
        """
        run = self.db.scalar(
            select(DailyPredictionRunModel)
            .options(
                selectinload(DailyPredictionRunModel.category_scores).selectinload(
                    DailyPredictionCategoryScoreModel.category
                ),
                selectinload(DailyPredictionRunModel.time_blocks),
                selectinload(DailyPredictionRunModel.turning_points),
            )
            .where(
                DailyPredictionRunModel.user_id == user_id,
                DailyPredictionRunModel.local_date < date_local,
            )
            .order_by(DailyPredictionRunModel.local_date.desc())
            .limit(1)
        )
        return self.get_snapshot(run) if run else None

    def get_run_by_hash_with_details(
        self, user_id: int, input_hash: str
    ) -> DailyPredictionRunModel | None:
        return self.db.scalar(
            select(DailyPredictionRunModel)
            .options(
                selectinload(DailyPredictionRunModel.category_scores),
                selectinload(DailyPredictionRunModel.time_blocks),
                selectinload(DailyPredictionRunModel.turning_points),
            )
            .where(
                DailyPredictionRunModel.user_id == user_id,
                DailyPredictionRunModel.input_hash == input_hash,
            )
        )

    def get_latest_run_before(
        self,
        user_id: int,
        date_local: date,
    ) -> DailyPredictionRunModel | None:
        """
        Retrieves the most recent run for a user before a specific date.
        Useful for fallback logic.
        """
        return self.db.scalar(
            select(DailyPredictionRunModel)
            .where(
                DailyPredictionRunModel.user_id == user_id,
                DailyPredictionRunModel.local_date < date_local,
            )
            .order_by(DailyPredictionRunModel.local_date.desc())
            .limit(1)
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

    def get_snapshot(
        self, run: DailyPredictionRunModel | None
    ) -> PersistedPredictionSnapshot | None:
        """
        Converts a run model to a typed snapshot.
        AC1 Compliance: Robust, typed read model.
        """
        if run is None:
            return None

        # AC3 Compliance: Explicit contributors and drivers parsing
        category_scores = [
            PersistedCategoryScore(
                category_id=s.category_id,
                category_code=(
                    s.category.code if getattr(s, "category", None) is not None else "unknown"
                ),
                note_20=s.note_20 or 0,
                raw_score=s.raw_score or 0.0,
                power=s.power or 0.0,
                volatility=s.volatility or 0.0,
                rank=s.rank or 0,
                is_provisional=bool(s.is_provisional),
                summary=s.summary,
                contributors=self._load_json_list(s.contributors_json),
            )
            for s in run.category_scores
        ]

        turning_points = [
            PersistedTurningPoint(
                occurred_at_local=tp.occurred_at_local,
                severity=tp.severity or 0.0,
                summary=tp.summary,
                drivers=self._load_json_list(tp.driver_json),
            )
            for tp in run.turning_points
        ]

        time_blocks = [
            PersistedTimeBlock(
                block_index=b.block_index,
                start_at_local=b.start_at_local,
                end_at_local=b.end_at_local,
                tone_code=b.tone_code or "neutral",
                dominant_categories=self._load_json_list(b.dominant_categories_json),
                summary=b.summary,
            )
            for b in sorted(run.time_blocks, key=lambda x: x.block_index)
        ]

        return PersistedPredictionSnapshot(
            run_id=run.id,
            user_id=run.user_id,
            local_date=run.local_date,
            timezone=run.timezone,
            computed_at=run.computed_at,
            input_hash=run.input_hash,
            reference_version_id=run.reference_version_id,
            ruleset_id=run.ruleset_id,
            house_system_effective=run.house_system_effective,
            is_provisional_calibration=bool(run.is_provisional_calibration),
            calibration_label=run.calibration_label,
            overall_summary=run.overall_summary,
            overall_tone=run.overall_tone,
            category_scores=category_scores,
            turning_points=turning_points,
            time_blocks=time_blocks,
        )

    def _load_json_list(self, raw: str | None) -> list[Any]:
        if not raw:
            return []
        try:
            val = json.loads(raw)
            return val if isinstance(val, list) else []
        except (json.JSONDecodeError, TypeError):
            return []

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

    def get_full_run(self, run_id: int) -> PersistedPredictionSnapshot | None:
        """
        Retrieves a full run and returns a typed snapshot.
        AC1 Compliance: Replaces dict[str, Any] output.
        """
        run = self.db.scalar(
            select(DailyPredictionRunModel)
            .execution_options(populate_existing=True)
            .options(
                selectinload(DailyPredictionRunModel.category_scores).selectinload(
                    DailyPredictionCategoryScoreModel.category
                ),
                selectinload(DailyPredictionRunModel.turning_points),
                selectinload(DailyPredictionRunModel.time_blocks),
            )
            .where(DailyPredictionRunModel.id == run_id)
        )
        return self.get_snapshot(run)

    def get_user_history(
        self, user_id: int, from_date: date, to_date: date
    ) -> list[DailyPredictionRunModel]:
        return list(
            self.db.scalars(
                select(DailyPredictionRunModel)
                .options(
                    selectinload(DailyPredictionRunModel.category_scores).selectinload(
                        DailyPredictionCategoryScoreModel.category
                    ),
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

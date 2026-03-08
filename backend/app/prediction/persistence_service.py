from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.infra.db.models.daily_prediction import (
    DailyPredictionCategoryScoreModel,
    DailyPredictionRunModel,
    DailyPredictionTimeBlockModel,
    DailyPredictionTurningPointModel,
)
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
from app.infra.db.repositories.prediction_reference_repository import PredictionReferenceRepository

if TYPE_CHECKING:
    from .explainability import ExplainabilityReport
from .schemas import EngineOutput


@dataclass(frozen=True)
class SaveResult:
    """Result of a persistence operation."""

    run: DailyPredictionRunModel
    was_reused: bool


class PredictionPersistenceService:
    """Service to persist engine outputs to the database."""

    def save(
        self,
        engine_output: EngineOutput,
        user_id: int,
        local_date: date,
        reference_version_id: int,
        ruleset_id: int,
        db: Session,
    ) -> SaveResult:
        """
        Persists an engine output to the database.
        Uses a single transaction (session flush).
        """
        input_hash = engine_output.effective_context.input_hash
        repo = DailyPredictionRepository(db)

        # AC1 - Reuse if hash matches
        existing = repo.get_run_by_hash(user_id, input_hash)
        if existing:
            return SaveResult(run=existing, was_reused=True)

        # AC2 - Create new run
        run = repo.create_run(
            user_id=user_id,
            local_date=local_date,
            timezone=engine_output.effective_context.timezone,
            reference_version_id=reference_version_id,
            ruleset_id=ruleset_id,
            input_hash=input_hash,
            house_system_effective=engine_output.effective_context.house_system_effective,
            is_provisional_calibration=engine_output.run_metadata.get("is_provisional_calibration"),
            overall_summary=engine_output.run_metadata.get("overall_summary"),
            overall_tone=engine_output.run_metadata.get("overall_tone"),
        )

        # AC3, AC4, AC5 - Persist child entities
        self._save_scores(
            run,
            engine_output,
            reference_version_id,
            db,
            engine_output.explainability,
        )
        self._save_turning_points(run, engine_output, db)
        self._save_time_blocks(run, engine_output, db)

        # AC6 - Single transaction (flush)
        db.flush()

        return SaveResult(run=run, was_reused=False)

    def _save_scores(
        self,
        run: DailyPredictionRunModel,
        engine_output: EngineOutput,
        reference_version_id: int,
        db: Session,
        explainability: ExplainabilityReport | None = None,
    ) -> None:
        """Saves category scores with computed ranks and top contributors."""
        ref_repo = PredictionReferenceRepository(db)
        categories = {cat.code: cat for cat in ref_repo.get_categories(reference_version_id)}

        # Filter scores to only include enabled categories found in DB
        active_scores = []
        for code, score_data in engine_output.category_scores.items():
            if code in categories:
                active_scores.append((categories[code], score_data))

        # AC3 - Sort for rank calculation: note DESC, then sort_order ASC
        active_scores.sort(key=lambda x: (-x[1].get("note_20", 0), x[0].sort_order))

        for rank, (category, score_data) in enumerate(active_scores, start=1):
            contributors_json = None
            if explainability and category.code in explainability.categories:
                expl = explainability.categories[category.code]
                contributors_json = json.dumps(
                    [
                        {
                            k: v.isoformat() if hasattr(v, "isoformat") else v
                            for k, v in asdict(c).items()
                        }
                        for c in expl.top_contributors
                    ]
                )

            model = DailyPredictionCategoryScoreModel(
                run_id=run.id,
                category_id=category.id,
                raw_score=score_data.get("raw_score"),
                normalized_score=score_data.get("normalized_score"),
                note_20=score_data.get("note_20"),
                power=score_data.get("power"),
                volatility=score_data.get("volatility"),
                rank=rank,
                summary=score_data.get("summary"),
                contributors_json=contributors_json,
            )
            db.add(model)

    def _save_turning_points(
        self,
        run: DailyPredictionRunModel,
        engine_output: EngineOutput,
        db: Session,
    ) -> None:
        """Saves turning points with serialized drivers.

        Handles both dict format (tests/external) and real TurningPoint objects
        from TurningPointDetector.
        """
        for tp in engine_output.turning_points:
            if isinstance(tp, dict):
                occurred_at = tp.get("occurred_at_local")
                severity = tp.get("severity")
                summary = tp.get("summary")
                drivers = tp.get("driver_events") or tp.get("drivers")
                driver_json = self._dumps_optional_list(drivers)
            else:
                # Real TurningPoint from TurningPointDetector
                occurred_at = tp.local_time
                severity = tp.severity
                summary = tp.reason

                # AC3 - Use driver_events if present, otherwise fallback to trigger_event
                drivers = getattr(tp, "driver_events", None)
                if drivers is not None:
                    driver_json = self._dumps_optional_list(drivers)
                else:
                    trigger = tp.trigger_event
                    driver_data = (
                        [
                            {
                                "event_type": trigger.event_type,
                                "body": trigger.body,
                                "target": trigger.target,
                                "contribution": None,
                                "local_time": trigger.local_time.isoformat(),
                            }
                        ]
                        if trigger is not None
                        else None
                    )
                    driver_json = self._dumps_optional_list(driver_data)

            model = DailyPredictionTurningPointModel(
                run_id=run.id,
                occurred_at_local=occurred_at,
                severity=severity,
                driver_json=driver_json,
                summary=summary,
            )
            db.add(model)

    def _save_time_blocks(
        self,
        run: DailyPredictionRunModel,
        engine_output: EngineOutput,
        db: Session,
    ) -> None:
        """Saves time blocks with serialized dominant categories.

        Handles both dict format (tests/external) and real TimeBlock objects
        from BlockGenerator (start_local, end_local, dominant_categories).
        """
        for block in engine_output.time_blocks:
            if isinstance(block, dict):
                block_index = block.get("block_index")
                start_at = block.get("start_at_local")
                end_at = block.get("end_at_local")
                tone_code = block.get("tone_code")
                summary = block.get("summary")
                dominant = block.get("dominant_categories")
            else:
                # Real TimeBlock from BlockGenerator
                block_index = block.block_index
                start_at = block.start_local
                end_at = block.end_local
                tone_code = block.tone_code
                summary = None  # TimeBlock has no summary field
                dominant = block.dominant_categories

            dominant_json = self._dumps_optional_list(dominant)

            model = DailyPredictionTimeBlockModel(
                run_id=run.id,
                block_index=block_index,
                start_at_local=start_at,
                end_at_local=end_at,
                tone_code=tone_code,
                dominant_categories_json=dominant_json,
                summary=summary,
            )
            db.add(model)

    def _dumps_optional_list(self, value: object) -> str | None:
        if value is None:
            return None
        return json.dumps(self._json_ready(value))

    def _json_ready(self, value: object) -> object:
        if hasattr(value, "isoformat"):
            return value.isoformat()
        if hasattr(value, "__dataclass_fields__"):
            return {key: self._json_ready(item) for key, item in asdict(value).items()}
        if isinstance(value, dict):
            return {key: self._json_ready(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._json_ready(item) for item in value]
        return value

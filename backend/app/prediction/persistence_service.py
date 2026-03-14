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

from .schemas import (
    CoreEngineOutput,
    EditorialOutputBundle,
    EngineOutput,
    PersistablePredictionBundle,
)

if TYPE_CHECKING:
    from .explainability import ExplainabilityReport
    from .persisted_snapshot import PersistedPredictionSnapshot


@dataclass(frozen=True)
class SaveResult:
    """Result of a persistence operation."""

    run: PersistedPredictionSnapshot
    was_reused: bool


class PredictionPersistenceService:
    """Service to persist engine outputs to the database."""

    def save(
        self,
        bundle: PersistablePredictionBundle | EngineOutput | None = None,
        user_id: int | None = None,
        local_date: date | None = None,
        reference_version_id: int | None = None,
        ruleset_id: int | None = None,
        db: Session | None = None,
        **legacy_kwargs: object,
    ) -> SaveResult:
        """
        Persists a prediction bundle to the database.
        Uses a single transaction (session flush).
        """
        if bundle is None:
            bundle = legacy_kwargs.pop("engine_output", None)
        if legacy_kwargs:
            unexpected = ", ".join(sorted(legacy_kwargs))
            raise TypeError(f"Unexpected keyword argument(s): {unexpected}")
        if bundle is None:
            raise TypeError("save() missing required argument: 'bundle'")
        missing_required_arg = (
            user_id is None
            or local_date is None
            or reference_version_id is None
            or ruleset_id is None
            or db is None
        )
        if missing_required_arg:
            raise TypeError("save() missing required persistence arguments")

        core, editorial = self._coerce_bundle_parts(bundle)
        v3_core = getattr(bundle, "v3_core", None)
        editorial_text = self._get_editorial_text(bundle, editorial)
        input_hash = core.effective_context.input_hash
        engine_mode = str(core.run_metadata.get("engine_mode", "v2"))

        if v3_core:
            engine_version = v3_core.engine_version
            snapshot_version = v3_core.snapshot_version
            evidence_pack_version = v3_core.evidence_pack_version
        else:
            engine_version = core.run_metadata.get("engine_version")
            snapshot_version = core.run_metadata.get("snapshot_version")
            evidence_pack_version = core.run_metadata.get("evidence_pack_version")

        repo = DailyPredictionRepository(db)

        # AC1 - Reuse if hash matches
        existing = repo.get_run_for_reuse(
            user_id,
            input_hash,
            engine_mode=engine_mode,
            engine_version=engine_version,
            snapshot_version=snapshot_version,
            evidence_pack_version=evidence_pack_version,
        )
        if existing:
            return SaveResult(run=existing, was_reused=True)

        # AC2 - Create new run
        run_model = repo.create_run(
            user_id=user_id,
            local_date=local_date,
            timezone=core.effective_context.timezone,
            reference_version_id=reference_version_id,
            ruleset_id=ruleset_id,
            input_hash=input_hash,
            engine_mode=engine_mode,
            engine_version=engine_version,
            snapshot_version=snapshot_version,
            evidence_pack_version=evidence_pack_version,
            v3_metrics_json=json.dumps(self._json_ready(v3_core)) if v3_core else None,
            house_system_effective=core.effective_context.house_system_effective,
            is_provisional_calibration=core.run_metadata.get("is_provisional_calibration"),
            calibration_label=core.run_metadata.get("calibration_label"),
            overall_summary=(
                editorial_text.intro
                if editorial_text is not None
                else core.run_metadata.get("overall_summary")
            ),
            overall_tone=(
                editorial.data.overall_tone
                if editorial is not None
                else core.run_metadata.get("overall_tone")
            ),
        )

        # AC3, AC4, AC5 - Persist child entities
        self._save_scores(
            run_model,
            bundle,
            reference_version_id,
            db,
            core.explainability,
        )
        self._save_turning_points(run_model, bundle, db)
        self._save_time_blocks(run_model, bundle, db)

        # AC6 - Single transaction (flush)
        db.flush()

        # Reload full run to get typed snapshot
        snapshot = repo.get_full_run(run_model.id)
        if snapshot is None:
            raise RuntimeError("Failed to reload persisted run snapshot")

        return SaveResult(run=snapshot, was_reused=False)

    def _save_scores(
        self,
        run: DailyPredictionRunModel,
        bundle: PersistablePredictionBundle | EngineOutput,
        reference_version_id: int,
        db: Session,
        explainability: ExplainabilityReport | None = None,
    ) -> None:
        """Saves category scores with computed ranks and top contributors."""
        ref_repo = PredictionReferenceRepository(db)
        categories = {cat.code: cat for cat in ref_repo.get_categories(reference_version_id)}
        core, editorial = self._coerce_bundle_parts(bundle)
        v3_core = getattr(bundle, "v3_core", None)
        editorial_text = self._get_editorial_text(bundle, editorial)

        # Filter scores to only include enabled categories found in DB
        active_scores = []
        for code, score_data in core.category_scores.items():
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

            editorial_summary = None
            if editorial_text is not None:
                editorial_summary = editorial_text.category_summaries.get(category.code)

            v3_metrics = None
            if v3_core and category.code in v3_core.daily_metrics:
                v3_metrics = v3_core.daily_metrics[category.code]

            model = DailyPredictionCategoryScoreModel(
                run_id=run.id,
                category_id=category.id,
                raw_score=score_data.get("raw_score"),
                normalized_score=score_data.get("normalized_score"),
                note_20=score_data.get("note_20"),
                power=score_data.get("power"),
                volatility=v3_metrics.volatility if v3_metrics else score_data.get("volatility"),
                score_20=v3_metrics.score_20 if v3_metrics else score_data.get("score_20"),
                intensity_20=score_data.get("intensity_20"),
                confidence_20=score_data.get("confidence_20"),
                rarity_percentile=v3_metrics.rarity_percentile
                if v3_metrics
                else score_data.get("rarity_percentile"),
                level_day=v3_metrics.level_day if v3_metrics else None,
                dominance_day=v3_metrics.dominance_day if v3_metrics else None,
                stability_day=v3_metrics.stability_day if v3_metrics else None,
                intensity_day=v3_metrics.intensity_day if v3_metrics else None,
                avg_score=v3_metrics.avg_score if v3_metrics else score_data.get("avg_score"),
                max_score=v3_metrics.max_score if v3_metrics else score_data.get("max_score"),
                min_score=v3_metrics.min_score if v3_metrics else score_data.get("min_score"),
                rank=rank,
                is_provisional=score_data.get("is_provisional"),
                summary=editorial_summary or score_data.get("summary"),
                contributors_json=contributors_json,
            )
            db.add(model)

    def _save_turning_points(
        self,
        run: DailyPredictionRunModel,
        bundle: PersistablePredictionBundle | EngineOutput,
        db: Session,
    ) -> None:
        """Saves turning points with serialized drivers."""
        core, editorial = self._coerce_bundle_parts(bundle)
        editorial_text = self._get_editorial_text(bundle, editorial)

        for i, tp in enumerate(core.turning_points):
            summary = None
            if editorial_text is not None and i < len(editorial_text.turning_point_summaries):
                summary = editorial_text.turning_point_summaries[i]

            if isinstance(tp, dict):
                occurred_at = tp.get("occurred_at_local")
                severity = tp.get("severity")
                summary = summary or tp.get("summary")
                drivers = tp.get("driver_events") or tp.get("drivers")
                driver_json = self._dumps_optional_list(drivers)
            else:
                # Real TurningPoint from TurningPointDetector
                occurred_at = tp.local_time
                severity = tp.severity
                summary = summary or tp.summary or tp.reason

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
        bundle: PersistablePredictionBundle | EngineOutput,
        db: Session,
    ) -> None:
        """Saves time blocks with serialized dominant categories."""
        core, editorial = self._coerce_bundle_parts(bundle)
        editorial_text = self._get_editorial_text(bundle, editorial)

        for i, block in enumerate(core.time_blocks):
            summary = None
            if editorial_text is not None and i < len(editorial_text.time_block_summaries):
                summary = editorial_text.time_block_summaries[i]

            if isinstance(block, dict):
                block_index = block.get("block_index")
                start_at = block.get("start_at_local")
                end_at = block.get("end_at_local")
                tone_code = block.get("tone_code")
                summary = summary or block.get("summary")
                dominant = block.get("dominant_categories")
            else:
                # Real TimeBlock from BlockGenerator
                block_index = block.block_index
                start_at = block.start_local
                end_at = block.end_local
                tone_code = block.tone_code
                summary = summary or block.summary or None
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

    def _coerce_bundle_parts(
        self,
        bundle: PersistablePredictionBundle | EngineOutput,
    ) -> tuple[CoreEngineOutput, EditorialOutputBundle | None]:
        if isinstance(bundle, PersistablePredictionBundle):
            return bundle.core, bundle.editorial

        core = CoreEngineOutput(
            effective_context=bundle.effective_context,
            run_metadata=dict(bundle.run_metadata),
            category_scores=dict(bundle.category_scores),
            time_blocks=list(bundle.time_blocks),
            turning_points=list(bundle.turning_points),
            decision_windows=list(bundle.decision_windows),
            detected_events=list(bundle.detected_events),
            sampling_timeline=list(bundle.sampling_timeline),
            explainability=bundle.explainability,
        )
        editorial = None
        if bundle.editorial is not None and bundle.editorial_text is not None:
            editorial = EditorialOutputBundle(
                data=bundle.editorial,
                text=bundle.editorial_text,
            )
        return core, editorial

    def _get_editorial_text(
        self,
        bundle: PersistablePredictionBundle | EngineOutput,
        editorial: EditorialOutputBundle | None,
    ):
        if editorial is not None:
            return editorial.text
        if isinstance(bundle, PersistablePredictionBundle):
            return None
        return bundle.editorial_text

    def _dumps_optional_list(self, value: object) -> str | None:
        if value is None:
            return None
        return json.dumps(self._json_ready(value))

    def _json_ready(self, value: object) -> object:
        if hasattr(value, "isoformat"):
            return value.isoformat()
        if hasattr(value, "__dataclass_fields__"):
            return {
                str(key) if hasattr(key, "isoformat") else key: self._json_ready(item)
                for key, item in asdict(value).items()
            }
        if isinstance(value, dict):
            return {
                str(key) if hasattr(key, "isoformat") else key: self._json_ready(item)
                for key, item in value.items()
            }
        if isinstance(value, (list, tuple)):
            return [self._json_ready(item) for item in value]
        return value

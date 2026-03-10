import json
import logging
import time
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.infra.db.models.calibration import CalibrationRawDayModel
from app.infra.db.repositories.calibration_repository import CalibrationRepository
from app.infra.db.session import SessionLocal
from app.jobs.calibration.natal_profiles import (
    CALIBRATION_DATE_RANGE,
    CALIBRATION_PROFILES,
    CALIBRATION_VERSIONS,
)
from app.jobs.calibration.runtime import resolve_calibration_runtime
from app.prediction.context_loader import PredictionContextLoader
from app.prediction.engine_orchestrator import EngineOrchestrator
from app.prediction.schemas import EngineInput

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_date_range(start_iso: str, end_iso: str) -> list[date]:
    start = date.fromisoformat(start_iso)
    end = date.fromisoformat(end_iso)
    delta = end - start
    return [start + timedelta(days=i) for i in range(delta.days + 1)]


def _resolve_active_category_codes(
    db: Session,
    *,
    reference_version: str,
    ruleset_version: str,
    reference_date: date,
) -> tuple[str, ...]:
    loaded_context = PredictionContextLoader().load(
        db,
        reference_version,
        ruleset_version,
        reference_date,
    )
    return tuple(
        category.code
        for category in loaded_context.prediction_context.categories
        if category.is_enabled
    )


def _log_profile_result(
    *,
    profile_label: str,
    local_date: date,
    status: str,
    duration_seconds: float,
    category_codes: tuple[str, ...],
) -> None:
    logger.info(
        "calibration_raw_day_run %s",
        json.dumps(
            {
                "profile_label": profile_label,
                "local_date": local_date.isoformat(),
                "status": status,
                "duration_seconds": round(duration_seconds, 6),
                "category_codes": list(category_codes),
            },
            sort_keys=True,
        ),
    )


def run_job() -> None:
    dates = get_date_range(CALIBRATION_DATE_RANGE["start"], CALIBRATION_DATE_RANGE["end"])
    if not dates:
        logger.info("Calibration job skipped: empty date range.")
        return

    with SessionLocal() as db:
        repo = CalibrationRepository(db)

        runtime = resolve_calibration_runtime(
            db,
            requested_reference_version=CALIBRATION_VERSIONS["reference_version"],
            requested_ruleset_version=CALIBRATION_VERSIONS["ruleset_version"],
        )
        ref_version = runtime.reference_version
        ruleset_version = runtime.ruleset_version

        def ctx_loader(
            reference_version_value: str,
            ruleset_version_value: str,
            local_date: date,
        ):
            return PredictionContextLoader().load(
                db,
                reference_version_value,
                ruleset_version_value,
                local_date,
            )

        orchestrator = EngineOrchestrator(prediction_context_loader=ctx_loader)
        active_category_codes = _resolve_active_category_codes(
            db,
            reference_version=ref_version,
            ruleset_version=ruleset_version,
            reference_date=dates[0],
        )

        total_profiles = len(CALIBRATION_PROFILES)
        total_dates = len(dates)
        total_iterations = total_profiles * total_dates

        computed_count = 0
        skipped_count = 0
        start_time_global = time.time()

        logger.info("Starting calibration job: %s profiles, %s days.", total_profiles, total_dates)
        logger.info("Versions: ref=%s, ruleset=%s", ref_version, ruleset_version)

        try:
            for p_idx, profile in enumerate(CALIBRATION_PROFILES, 1):
                for d_idx, local_date in enumerate(dates, 1):
                    profile_label = profile["label"]
                    iteration_started_at = time.time()
                    existing_codes = repo.get_existing_category_codes(
                        profile_label, local_date, ref_version, ruleset_version
                    )
                    missing_category_codes = tuple(
                        code for code in active_category_codes if code not in existing_codes
                    )

                    if not missing_category_codes:
                        skipped_count += 1
                        _log_profile_result(
                            profile_label=profile_label,
                            local_date=local_date,
                            status="skipped",
                            duration_seconds=time.time() - iteration_started_at,
                            category_codes=active_category_codes,
                        )
                        continue

                    start_time_calc = time.time()
                    engine_input = EngineInput(
                        natal_chart=profile["natal_chart"],
                        local_date=local_date,
                        timezone=profile["timezone"],
                        latitude=profile["latitude"],
                        longitude=profile["longitude"],
                        reference_version=ref_version,
                        ruleset_version=ruleset_version,
                        debug_mode=False,
                    )

                    bundle = orchestrator.run(
                        engine_input,
                        category_codes=missing_category_codes,
                        include_editorial=False,
                    )
                    core_output = bundle.core
                    duration_calc = time.time() - start_time_calc
                    pivot_count = (
                        len(core_output.turning_points) if core_output.turning_points else 0
                    )

                    for category_code in missing_category_codes:
                        score = core_output.category_scores.get(category_code)
                        if score is None:
                            raise RuntimeError(
                                "Engine output is missing a requested category score for "
                                f"{category_code!r}"
                            )

                        raw_day = CalibrationRawDayModel(
                            profile_label=profile_label,
                            local_date=local_date,
                            category_code=category_code,
                            raw_score=score["raw_score"],
                            power=score.get("power"),
                            volatility=score.get("volatility"),
                            pivot_count=pivot_count,
                            reference_version=ref_version,
                            ruleset_version=ruleset_version,
                        )
                        repo.save(raw_day)

                    db.commit()
                    computed_count += 1
                    _log_profile_result(
                        profile_label=profile_label,
                        local_date=local_date,
                        status="computed",
                        duration_seconds=duration_calc,
                        category_codes=missing_category_codes,
                    )

                    if computed_count % 10 == 0:
                        logger.info(
                            (
                                "Progress: %s/%s profiles, %s/%s days. "
                                "Computed: %s, Skipped: %s, Total: %s"
                            ),
                            p_idx,
                            total_profiles,
                            d_idx,
                            total_dates,
                            computed_count,
                            skipped_count,
                            total_iterations,
                        )

        except Exception as e:
            logger.error("Job failed: %s", e)
            db.rollback()
            raise

        duration_global = time.time() - start_time_global
        logger.info("Job completed.")
        logger.info(
            "Summary: Computed=%s, Skipped=%s, Duration=%.2fs",
            computed_count, skipped_count, duration_global,
        )


if __name__ == "__main__":
    run_job()

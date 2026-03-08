# backend/app/jobs/qa/generate_qa_cases.py
import hashlib
import json
import logging
import secrets
import uuid
from datetime import date
from pathlib import Path

from app.core.config import settings
from app.core.security import hash_password
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import SessionLocal
from app.jobs.calibration.natal_profiles import CALIBRATION_PROFILES
from app.prediction.context_loader import PredictionContextLoader
from app.prediction.engine_orchestrator import EngineOrchestrator
from app.prediction.persistence_service import PredictionPersistenceService
from app.services.daily_prediction_service import ComputeMode, DailyPredictionService

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent.parent.parent.parent / "docs" / "qa" / "cases"

QA_DATES = [
    date(2026, 3, 8),
    date(2026, 3, 9),
    date(2026, 3, 10),
    date(2026, 3, 11),
    date(2026, 3, 12),
]


def get_or_create_qa_user(db, profile):
    email = f"qa_{profile['label']}@horoscope.app"
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        user = UserModel(
            email=email,
            password_hash=hash_password(secrets.token_urlsafe(16)),
            role="user",
        )
        db.add(user)
        db.flush()

        # Create birth profile
        birth_profile = UserBirthProfileModel(
            user_id=user.id,
            birth_date=date(1990, 1, 1),
            birth_place="Test City",
            birth_timezone=profile["timezone"],
            birth_lat=profile["latitude"],
            birth_lon=profile["longitude"],
            current_lat=profile["latitude"],
            current_lon=profile["longitude"],
            current_timezone=profile["timezone"],
        )
        db.add(birth_profile)

        # Create chart result
        chart_result = ChartResultModel(
            user_id=user.id,
            chart_id=str(uuid.uuid4()),
            reference_version=settings.active_reference_version,
            ruleset_version=settings.active_ruleset_version,
            input_hash=hashlib.sha256(f"qa_{profile['label']}".encode()).hexdigest()[:32],
            result_payload=profile["natal_chart"],
        )
        db.add(chart_result)
        db.commit()
        logger.info(f"Created QA user {email}")
    return user


def generate() -> int:
    """
    Generate QA cases for all calibration profiles.

    Returns the number of cases successfully generated.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    generated_count = 0

    # Setup service
    context_loader = PredictionContextLoader()
    persistence_service = PredictionPersistenceService()
    orchestrator = EngineOrchestrator()
    service = DailyPredictionService(context_loader, persistence_service, orchestrator=orchestrator)

    try:
        for i, profile in enumerate(CALIBRATION_PROFILES):
            user = get_or_create_qa_user(db, profile)
            qa_date = QA_DATES[i % len(QA_DATES)]

            logger.info(f"Generating QA case for {profile['label']} on {qa_date}")

            result = service.get_or_compute(
                user_id=user.id,
                db=db,
                date_local=qa_date,
                mode=ComputeMode.force_recompute,
                ruleset_version=settings.active_ruleset_version,
            )

            if result and result.engine_output:
                metadata = result.engine_output.run_metadata
                case_data = {
                    "case_id": f"QA-{i+1:02d}",
                    "profile": profile["label"],
                    "date": qa_date.isoformat(),
                    "overall_tone": metadata.get("overall_tone"),
                    "is_provisional": metadata.get("is_provisional_calibration"),
                    "calibration_label": metadata.get("calibration_label"),
                    "category_scores": result.engine_output.category_scores,
                    "turning_points_count": len(result.engine_output.turning_points),
                    "timeline_blocks_count": len(result.engine_output.time_blocks),
                }

                output_file = OUTPUT_DIR / f"case_{profile['label']}_{qa_date}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(case_data, f, indent=2, ensure_ascii=False, default=str)

                scores_summary = {
                    k: v["note_20"] for k, v in case_data["category_scores"].items()
                }
                logger.info(f"  Result: Tone={case_data['overall_tone']}, Scores={scores_summary}")
                generated_count += 1
            else:
                logger.warning(f"  Failed to generate output for {profile['label']}")

    finally:
        db.close()

    logger.info(
        "Generation complete: %s/%s cases produced",
        generated_count,
        len(CALIBRATION_PROFILES),
    )
    return generated_count


if __name__ == "__main__":
    import sys

    generated = generate()
    if generated < 5:
        logger.error(f"AC1 VIOLATION: only {generated} case(s) generated, minimum 5 required")
        sys.exit(1)

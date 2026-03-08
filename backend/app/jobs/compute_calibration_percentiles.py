import logging
from datetime import date
from pathlib import Path

from app.infra.db.repositories.calibration_repository import CalibrationRepository
from app.infra.db.session import SessionLocal
from app.jobs.calibration.natal_profiles import CALIBRATION_VERSIONS
from app.jobs.calibration.percentile_calculator import PercentileCalculatorService
from app.jobs.calibration.runtime import resolve_calibration_runtime, resolve_project_root

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run() -> None:
    db = SessionLocal()
    calibration_repo = CalibrationRepository(db)
    service = PercentileCalculatorService(db, calibration_repo)

    runtime = resolve_calibration_runtime(
        db,
        requested_reference_version=CALIBRATION_VERSIONS["reference_version"],
        requested_ruleset_version=CALIBRATION_VERSIONS["ruleset_version"],
    )
    ref_version = runtime.reference_version
    ruleset_version = runtime.ruleset_version

    # Plage de validité pour la calibration
    valid_from = date(2024, 1, 1)
    valid_to = date(2024, 12, 31)

    logger.info("Démarrage du calcul des percentiles pour %s/%s", ref_version, ruleset_version)

    try:
        results = service.run(
            reference_version=ref_version,
            ruleset_version=ruleset_version,
            valid_from=valid_from,
            valid_to=valid_to,
        )

        if not results:
            logger.warning("Aucun résultat généré.")
            return

        report_path = resolve_project_root() / Path("docs/calibration/percentile_report.json")
        metadata = {
            "reference_version": ref_version,
            "ruleset_version": ruleset_version,
            "valid_from": valid_from.isoformat(),
            "valid_to": valid_to.isoformat(),
        }
        service.generate_report(results, report_path, metadata)

        total_cats = len(results)
        avg_sample = sum(r.sample_size for r in results) / total_cats

        logger.info("Calcul terminé avec succès pour %s catégories.", total_cats)
        logger.info("Taille d'échantillon moyenne: %.1f", avg_sample)
        logger.info("Rapport disponible dans: %s", report_path)

    except Exception as exc:
        logger.error("Échec du calcul des percentiles: %s", exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()

# backend/app/jobs/compute_calibration_percentiles.py
import logging
from datetime import date
from pathlib import Path

from app.infra.db.session import SessionLocal
from app.infra.db.repositories.calibration_repository import CalibrationRepository
from app.jobs.calibration.percentile_calculator import PercentileCalculatorService
from app.jobs.calibration.natal_profiles import CALIBRATION_VERSIONS

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run():
    db = SessionLocal()
    calibration_repo = CalibrationRepository(db)
    service = PercentileCalculatorService(db, calibration_repo)
    
    ref_version = CALIBRATION_VERSIONS["reference_version"]
    ruleset_version = CALIBRATION_VERSIONS["ruleset_version"]
    
    # Plage de validité pour la calibration
    valid_from = date(2024, 1, 1)
    valid_to = date(2024, 12, 31)
    
    logger.info(f"Démarrage du calcul des percentiles pour {ref_version}/{ruleset_version}")
    
    try:
        results = service.run(
            reference_version=ref_version,
            ruleset_version=ruleset_version,
            valid_from=valid_from,
            valid_to=valid_to
        )
        
        if not results:
            logger.warning("Aucun résultat généré.")
            return

        report_path = Path("docs/calibration/percentile_report.json")
        metadata = {
            "reference_version": ref_version,
            "ruleset_version": ruleset_version,
            "valid_from": valid_from.isoformat(),
            "valid_to": valid_to.isoformat(),
        }
        service.generate_report(results, report_path, metadata)
        
        total_cats = len(results)
        avg_sample = sum(r.sample_size for r in results) / total_cats
        
        logger.info(f"Calcul terminé avec succès pour {total_cats} catégories.")
        logger.info(f"Taille d'échantillon moyenne: {avg_sample:.1f}")
        logger.info(f"Rapport disponible dans: {report_path}")

    except Exception as e:
        logger.error(f"Échec du calcul des percentiles: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run()

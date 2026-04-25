"""Expose le seed de prediction historique via le composant applicatif canonique."""

import sys

from app.infra.db.session import SessionLocal
from app.services.prediction.reference_seed_service import (
    PredictionReferenceSeedAbortError,
    run_prediction_reference_seed,
)

SeedAbortError = PredictionReferenceSeedAbortError
run_seed = run_prediction_reference_seed


def main() -> None:
    """Execute le seed historique depuis le module applicatif canonique."""
    with SessionLocal() as db:
        try:
            with db.begin():
                run_prediction_reference_seed(db)
        except PredictionReferenceSeedAbortError as error:
            print(error)
            sys.exit(1)
        except Exception as error:
            import traceback

            traceback.print_exc()
            print(f"Seed failed: {error}")
            sys.exit(1)


if __name__ == "__main__":
    main()

# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Table editoriale avec colonnes demandees et JSON texte. | Migration Alembic + modele SQLAlchemy. | `pytest -q app/tests/integration/test_reference_data_migrations.py`. | PASS |
| AC2 | Versioning, FK maison stable, unicite version/maison/langue/tradition. | Contraintes migration + modele. | `pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_reference_data_migrations.py`. | PASS |
| AC3 | Aucune modification runtime/scoring produit. | Aucun changement `domain/astrology`, aucune consommation prediction. | Scan `rg` zero-hit sous `app/domain/astrology` + tests existants. | PASS |

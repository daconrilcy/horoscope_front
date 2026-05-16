# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `flagged_contents` est charge par `Base.metadata`. | `backend/app/infra/db/models/__init__.py` exporte `FlaggedContentModel`; `backend/app/infra/db/base.py` charge les registres ORM. | `pytest -q app/tests/unit/test_db_model_registry_guard.py` - PASS | PASS |
| AC2 | Les tables sans modele applicatif sont classifiees exactement. | `db-table-exception-register.md` liste quatre exceptions exactes et la garde refuse les motifs generiques. | `pytest -q app/tests/unit/test_db_model_registry_guard.py` - PASS | PASS |
| AC3 | Zero table applicative non classifiee hors metadata. | `Base.metadata` charge 125 tables de modeles pour 125 modeles declares; audit apres sans manque metadata. | `pytest -q app/tests/unit/test_db_model_registry_guard.py` + `db-model-registry-after.md` - PASS | PASS |
| AC4 | Les usages de `FlaggedContentModel` restent fonctionnels. | Le routeur support reste inchange; le modele est disponible dans les bases de test via `Base.metadata.create_all`. | `pytest -q --long app/tests/integration/test_admin_support_api.py` - PASS | PASS |
| AC5 | Aucun nettoyage destructif n'est introduit. | Aucun fichier de migration ni DB locale modifie; scan cible des fichiers modifies sans `drop_table`/`DROP TABLE`. | Scan destructif cible - PASS; scan large classe des downgrades historiques existants | PASS |

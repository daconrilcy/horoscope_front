# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | L'inventaire avant/après classe chaque constante auditée. | Artefacts before/after et registre d'exceptions. | `test_astrology_runtime_reference_guard.py`; scans avant/après. | Pending |
| AC2 | Les fallbacks legacy de `_legacy_payload_for_mock_db` sont supprimés. | Suppression du helper et de ses imports dans `calculation_service.py`. | `test_natal_calculation_service.py`; scan natal zéro. | Pending |
| AC3 | Les mappings d'aspects daily ne sont plus dupliqués localement. | Résolution des aspects via profils runtime (`angle`, `family_code`) et helper partagé. | `test_enriched_astro_events_builder.py`; scans `ASPECTS_V1`/`ASPECTS`. | Pending |
| AC4 | Les constantes conservées sont classées sans wildcard ni exception de dossier. | `astrology-constant-exceptions.md` exact. | `test_astrology_reference_catalog_guard.py`; revue du registre. | Pending |
| AC5 | Le domaine astrology reste séparé de prediction. | Aucun import prediction depuis `domain/astrology`. | `test_astrology_prediction_boundary.py`; scan imports interdits. | Pending |
| AC6 | Les guards échouent si les mappings DB-backed reviennent. | Guard AST dédié dans `test_astrology_reference_catalog_guard.py`. | `test_astrology_runtime_reference_guard.py` et `test_astrology_reference_catalog_guard.py`. | Pending |
| AC7 | La validation standard backend passe dans le venv. | Aucun changement de dépendance. | `ruff format .`, `ruff check .`, commandes pytest ciblées. | Pending |

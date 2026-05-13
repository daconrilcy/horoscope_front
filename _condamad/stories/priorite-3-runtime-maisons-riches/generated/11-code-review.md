# Code Review

Verdict: CLEAN_WITH_VALIDATION_LIMITATION

## Independent Review Findings

1. `sign` absent de `chart_results.result_payload.houses[]`.
   - Status: FIXED.
   - Correction: `HouseRuntimeData.sign` est un champ serialisable synchronise avec
     `cusp_sign`; `test_persist_and_get_audit_record` verifie la persistance.

2. Garde Whole Sign non prouvee avec enum runtime.
   - Status: FIXED.
   - Correction: `house_runtime_builder._normalize_house_system` utilise `.value`
     quand disponible; test enum ajoute.

3. Evidence CONDAMAD incomplete.
   - Status: FIXED.
   - Correction: `03-acceptance-traceability.md` et `10-final-evidence.md`
     renseignes.

## Fresh Review

- Runtime uniquement: aucun ajout SQL ou migration.
- Rulers: resolution unique via `HouseRulerResolver(sign_rulerships)`, puis
  injection structurelle dans les maisons.
- JSON: projection depuis le runtime, `sign` legacy expose.
- Tests: 101 tests cibles PASS; lint complet PASS.

Residual validation limitation: `pytest -q` complet a expire apres 304 secondes.

## Follow-up Review For House Ruler Projection

Context: demande utilisateur du 2026-05-13 sur le risque de divergence entre
`houses[*].ruler` et `house_rulers[]`.

### Independent Findings

1. `chart_results.result_payload.house_rulers[]` persistait encore
   `NatalResult.house_rulers` via `model_dump()`.
   - Status: FIXED.
   - Correction: `ChartResultService.persist_trace` remplace le champ persiste
     par la projection de `result_payload["houses"][*]["ruler"]`.
   - Guard: `test_persist_trace_projects_legacy_house_rulers_from_runtime_houses`.

2. Le test de coherence payload ne prouvait pas l'absence de fallback vers une
   entree stale quand `houses[*].ruler` manque.
   - Status: FIXED.
   - Correction: test negatif ajoutant une entree stale pour la maison 2 et
     verifiant qu'elle n'est pas emise sans ruler runtime.

3. Le contrat canonique/legacy creait un invariant durable non inscrit dans les
   guardrails.
   - Status: FIXED.
   - Correction: ajout de `RG-094` avec tests et scans cibles.

### Fresh Review

- Public JSON: `house_rulers[]` est projete depuis `houses[*].ruler`.
- Persistance: `chart_results.result_payload.house_rulers[]` est reprojete depuis
  `result_payload.houses[]`.
- Serializer/persister chart: aucun hit `natal_result.house_rulers`,
  `HouseRulerResolver`, `sign_rulerships` ou `get_sign_rulerships`.
- Revue independante finale: CLEAN.

Residual validation limitation: `pytest -q` complet non relance; les tests
cibles de projection/persistance passent et le lint complet passe.

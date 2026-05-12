# Final Evidence

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: `supprimer-astro-characteristics`
- Source story: `_condamad/stories/supprimer-astro-characteristics/00-story.md`
- Capsule path: `_condamad/stories/supprimer-astro-characteristics/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `?? output/`
- Pre-existing dirty files: `output/`
- AGENTS.md files considered: `AGENTS.md`
- Regression guardrails read: yes
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | |
| `generated/01-execution-brief.md` | yes | yes | PASS | |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | |
| `generated/04-target-files.md` | yes | yes | PASS | |
| `generated/06-validation-plan.md` | yes | yes | PASS | |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | |
| `generated/10-final-evidence.md` | yes | yes | PASS | |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/infra/db/models/reference.py` supprime le modele et la relation; `reference_repository.py` supprime seed/clone/clear/read. | Tests cibles PASS; scan actif sans `AstroCharacteristicModel`. | PASS | |
| AC2 | `get_reference_data` retourne uniquement version, planets, signs, houses, aspects. | `test_reference_data_contract_does_not_expose_characteristics` PASS; tests d'aspects PASS. | PASS | Overrides directs des definitions d'aspects inchanges. |
| AC3 | Migration `backend/migrations/versions/20260512_0085_drop_astro_characteristics.py`. | `test_reference_migrations_upgrade_and_downgrade` PASS, verifie presence en `20260218_0001` puis absence en `head`. | PASS | |
| AC4 | Tests importeurs nettoyes; `RG-091` ajoute au registre. | Scans No Legacy: seuls hits dans tests de garde. | PASS | |
| AC5 | Validation locale executee avec venv active. | Ruff PASS, tests cibles PASS, app `/health` PASS, suite complete FAIL hors scope. | PASS_WITH_LIMITATIONS | Echec existant sur dette SQL `public/astrologers.py`. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/infra/db/models/reference.py` | modified | Retirer le modele `AstroCharacteristicModel` et sa relation. | AC1 |
| `backend/app/infra/db/repositories/reference_repository.py` | modified | Retirer seed, clone, delete, completeness et payload `characteristics`. | AC1, AC2 |
| `backend/migrations/versions/20260512_0085_drop_astro_characteristics.py` | added | Supprimer la table pour les bases existantes. | AC3 |
| `backend/app/tests/unit/test_reference_data_service.py` | modified | Verifier le contrat sans `characteristics`. | AC2, AC4 |
| `backend/app/tests/integration/test_reference_data_migrations.py` | modified | Verifier absence de table au head. | AC3, AC4 |
| `backend/app/tests/**` importeurs reference | modified | Retirer le modele supprime des cleanups DB. | AC1, AC4 |
| `_condamad/stories/regression-guardrails.md` | modified | Ajouter RG-091 anti-reintroduction. | AC4 |
| `_condamad/stories/story-status.md` | modified | Ajouter la story en `ready-to-review`. | AC5 |

## Files deleted

- None.

## Tests added or updated

- `backend/app/tests/unit/test_reference_data_service.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff format .` | repo root | PASS | 0 | 5 fichiers formates. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest app/tests/unit/test_reference_data_service.py app/tests/integration/test_reference_data_migrations.py -q` | repo root | PASS | 0 | 10 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_aspects_calculator.py -q` | repo root | PASS | 0 | 20 passed. |
| `rg -n 'AstroCharacteristicModel\|astro_characteristics\|"characteristics"\|\\[''characteristics''\\]' backend/app backend/tests` | repo root | PASS | 0 | Seuls hits dans assertions de garde. |
| `rg -n "legacy\|compat\|shim\|fallback\|deprecated\|alias" backend/app/infra/db backend/app/tests/unit/test_reference_data_service.py backend/app/tests/integration/test_reference_data_migrations.py` | repo root | PASS | 0 | Hits preexistants hors scope DB/LLM/prediction, aucun lie a `astro_characteristics`. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check .` | repo root | PASS | 0 | All checks passed. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q` | repo root | FAIL | 1 | 3614 passed, 12 skipped, 1 failed: `test_api_sql_boundary_debt_matches_exact_allowlist`, dette SQL `public/astrologers.py` hors scope. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; python -m uvicorn app.main:app --host 127.0.0.1 --port 8011` + `GET /health` | repo root | PASS | 0 | `/health` HTTP 200, status healthy; job arrete apres verification. |
| `git diff --check` | repo root | PASS | 0 | Aucun conflit/whitespace; avertissements CRLF seulement. |
| `git diff --stat` | repo root | PASS | 0 | Diff limite au scope story plus artefacts CONDAMAD. |
| `git status --short` | repo root | PASS | 0 | Statut final enregistre. |

## Commands skipped or blocked

- None.

## DRY / No Legacy evidence

- Aucun shim, alias, fallback ou re-export conserve pour `AstroCharacteristicModel`.
- Scan `AstroCharacteristicModel|astro_characteristics|"characteristics"` dans `backend/app backend/tests`: seuls hits attendus dans tests de garde.
- `RG-091` ajoute pour bloquer la reintroduction runtime de la table/modele/payload.
- Le scan generique No Legacy retourne des hits preexistants hors scope (`llm`, `prediction`, `billing`, `chart_result_repository`), non modifies par cette story.

## Diff review

- `git diff --stat` revu: changements limites au backend reference data, tests associes, migration, capsule et registres.
- `git diff --check`: PASS avec avertissements CRLF Git uniquement.
- Bruit de formatage Ruff hors scope restaure.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/story-status.md
 M backend/app/infra/db/models/reference.py
 M backend/app/infra/db/repositories/reference_repository.py
 M backend/app/tests/integration/test_b2b_astrology_api.py
 M backend/app/tests/integration/test_b2b_editorial_api.py
 M backend/app/tests/integration/test_chat_api.py
 M backend/app/tests/integration/test_daily_prediction_qa.py
 M backend/app/tests/integration/test_guidance_api.py
 M backend/app/tests/integration/test_load_smoke_critical_flows.py
 M backend/app/tests/integration/test_natal_chart_accurate_api.py
 M backend/app/tests/integration/test_reference_data_api.py
 M backend/app/tests/integration/test_reference_data_migrations.py
 M backend/app/tests/integration/test_user_natal_chart_api.py
 M backend/app/tests/unit/test_chat_guidance_service.py
 M backend/app/tests/unit/test_natal_calculation_service.py
 M backend/app/tests/unit/test_natal_golden_swisseph.py
 M backend/app/tests/unit/test_reference_data_service.py
 M backend/app/tests/unit/test_user_astro_profile_service.py
 M backend/app/tests/unit/test_user_natal_chart_service.py
?? _condamad/stories/supprimer-astro-characteristics/
?? backend/migrations/versions/20260512_0085_drop_astro_characteristics.py
?? output/
```

Pre-existing dirty file/directory: `output/`.

## Remaining risks

- La suite backend complete echoue sur un guard SQL API preexistant/hors scope: `app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist` detecte six appels SQL dans `app/api/v1/routers/public/astrologers.py`.

## Suggested reviewer focus

- Verifier que la suppression de `characteristics` du payload public est acceptable pour les consommateurs.
- Verifier la migration Alembic `20260512_0085` et le downgrade recreant la table historique.
- Verifier que les hits de scan restants sont uniquement des tests de garde.

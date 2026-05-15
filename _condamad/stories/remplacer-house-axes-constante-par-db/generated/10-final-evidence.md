# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `remplacer-house-axes-constante-par-db`
- Source story: `_condamad/stories/remplacer-house-axes-constante-par-db/00-story.md`
- Capsule path: `_condamad/stories/remplacer-house-axes-constante-par-db/`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: clean lors du premier passage; la reprise de review affichait les fichiers de cette story deja modifies
- Pre-existing dirty files: aucun fichier hors scope observe
- AGENTS.md files considered: `AGENTS.md`
- Regression guardrails: `RG-095`, `RG-106`

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
| AC1 | `house_runtime_builder.py` prend `house_axes`; `house_axes.py` supprime | `pytest tests/unit/domain/astrology/test_house_runtime_builder.py -q` PASS; scan anciens symboles zero hit | PASS | |
| AC2 | `reference_repository.py` expose `house_axes` depuis `astral_house_axis_members` et `astral_house_axis_definitions`; `astral_house_axis_definitions` n'est plus versionnee | `pytest app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py -q` PASS; `pytest app/tests/integration/test_reference_data_migrations.py -q` PASS | PASS | |
| AC3 | `natal_calculation.py` valide `house_axes`, refuse les valeurs non entieres strictes et leve `NatalCalculationError` si incomplet | `test_reference_house_axes_extraction_rejects_incomplete_payload` PASS; `test_reference_house_axes_extraction_rejects_coerced_numbers` PASS | PASS | |
| AC4 | Tests cibles ajoutes/adaptes sur repository, seed, migration et builder | Pytest cible, Ruff cible, format check cible | PASS | Pas de suite globale par demande utilisateur |
| AC5 | Ancienne constante supprimee; documentation remplacee par tables DB | `rg -n "resolve_house_axis|HOUSE_AXES|constants/house_axes\.py|constants\\house_axes\.py" backend docs` zero hit | PASS | Hits restants uniquement dans la capsule CONDAMAD |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/astrology/builders/house_runtime_builder.py` | modified | Consommer un mapping d'axes fourni par le referentiel | AC1 |
| `backend/app/domain/astrology/natal_calculation.py` | modified | Valider et transmettre les axes de maisons au builder | AC1, AC3 |
| `backend/app/infra/db/models/interpretation_reference.py` | modified | Supprimer `reference_version_id` du modele `AstralHouseAxisDefinitionModel` | AC2 |
| `backend/app/infra/db/repositories/astrology_reference_sources.py` | modified | Charger les sources JSON des axes et langues pour le seed structurel | AC2 |
| `backend/app/infra/db/repositories/reference_repository.py` | modified | Charger les axes depuis les tables DB canoniques | AC2 |
| `backend/migrations/versions/20260515_0109_create_astral_house_axis_definitions.py` | modified | Creer les definitions d'axes sans colonne de version | AC2 |
| `backend/migrations/versions/20260515_0111_deversion_astral_house_axis_definitions.py` | added | Migrer les bases deja appliquees pour retirer la colonne de version | AC2 |
| `backend/app/tests/integration/test_reference_data_migrations.py` | modified | Verifier le schema non versionne et le nouveau head Alembic | AC2, AC4 |
| `backend/app/tests/unit/test_prediction_reference_repository.py` | modified | Tester l'exposition DB des axes dans le payload | AC2 |
| `backend/app/tests/unit/test_reference_data_service.py` | modified | Tester le seed des axes pour une version active type `2.0.0` | AC2 |
| `backend/tests/unit/domain/astrology/test_house_runtime_builder.py` | modified | Tester le mapping d'axes et l'erreur explicite | AC1, AC3 |
| `docs/recherches astro/astral_house_axis_definitions.json` | modified | Retirer `reference_version_id` de la source canonique | AC2 |
| `docs/recherches astro/tables-maisons-et-roles.md` | modified | Remplacer la reference obsolete a la constante par les tables | AC5 |
| `_condamad/stories/story-status.md` | modified | Enregistrer la story en ready-to-review | AC4 |
| `_condamad/stories/remplacer-house-axes-constante-par-db/**` | generated | Capsule et preuves CONDAMAD | AC4 |

## Files deleted

| File | Purpose | Related AC |
|---|---|---|
| `backend/app/domain/astrology/constants/house_axes.py` | Supprimer l'ancien chemin constant hard-code | AC1, AC5 |

## Tests added or updated

- `test_get_reference_data_exposes_house_axes_from_canonical_tables`
- `test_house_axis_definition_is_structural_not_versioned`
- `test_structural_astrology_models_are_not_versioned`
- `test_seed_reference_version_repairs_partial_existing_version`
- `test_runtime_builder_golden_placidus_with_interception_and_three_signs` mis a jour pour verifier `axis.theme`
- `test_runtime_builder_rejects_missing_house_axis`
- `test_reference_house_axes_extraction_rejects_incomplete_payload`
- `test_reference_house_axes_extraction_rejects_coerced_numbers`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest tests/unit/domain/astrology/test_house_runtime_builder.py -q` | `backend/` | PASS | 0 | 7 tests passed |
| `pytest app/tests/unit/test_prediction_reference_repository.py -q` | `backend/` | FAIL | 1 | Premier run: ambiguite SQLAlchemy sur les alias `HouseModel`; corrige par `select_from(AstralHouseAxisMemberModel)` |
| `pytest app/tests/unit/test_prediction_reference_repository.py -q` | `backend/` | PASS | 0 | 20 tests passed |
| `ruff check --fix app/infra/db/repositories/reference_repository.py` | `backend/` | PASS | 0 | Import ordering fixed |
| `ruff check app/domain/astrology/builders/house_runtime_builder.py app/domain/astrology/natal_calculation.py app/infra/db/repositories/reference_repository.py app/infra/db/repositories/prediction_schemas.py tests/unit/domain/astrology/test_house_runtime_builder.py app/tests/unit/test_prediction_reference_repository.py` | `backend/` | PASS | 0 | All checks passed |
| `ruff format --check app/domain/astrology/builders/house_runtime_builder.py app/domain/astrology/natal_calculation.py app/infra/db/repositories/reference_repository.py app/infra/db/repositories/prediction_schemas.py tests/unit/domain/astrology/test_house_runtime_builder.py app/tests/unit/test_prediction_reference_repository.py` | `backend/` | PASS | 0 | 6 files already formatted |
| `pytest tests/unit/domain/astrology/test_house_runtime_builder.py -q` | `backend/` | PASS | 0 | Rerun: 7 tests passed |
| `rg -n "resolve_house_axis\|HOUSE_AXES\|constants/house_axes\.py\|constants\\house_axes\.py" backend docs` | repo root | PASS | 1 | Zero hit, `rg` exit 1 attendu sans match |
| `rg -n "app\\.domain\\.prediction\|app\\.services\\.prediction\|prediction_categories\|house_category_weights\|visibility_weight\|base_priority\|routing_role\|DomainRouter\|PublicAstroFoundationProjector" app/domain/astrology -g "*.py"` | `backend/` | PASS | 1 | Zero hit, `rg` exit 1 attendu sans match |
| `python -c "from app.main import app; print(app.title)"` | `backend/` | PASS | 0 | Import FastAPI OK, titre `horoscope-backend` |
| `pytest tests/unit/domain/astrology/test_house_runtime_builder.py app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py -q` | `backend/` | PASS | 0 | 39 tests passed |
| `pytest app/tests/integration/test_reference_data_migrations.py -q` | `backend/` | FAIL | 1 | Premier run: expectation de head Alembic encore sur `20260515_0110`; corrigee vers `20260515_0111` |
| `pytest app/tests/integration/test_reference_data_migrations.py -q` | `backend/` | PASS | 0 | 3 tests passed |
| `ruff check app/domain/astrology/builders/house_runtime_builder.py app/domain/astrology/natal_calculation.py app/infra/db/repositories/reference_repository.py app/infra/db/repositories/astrology_reference_sources.py app/infra/db/models/interpretation_reference.py migrations/versions/20260515_0109_create_astral_house_axis_definitions.py migrations/versions/20260515_0111_deversion_astral_house_axis_definitions.py tests/unit/domain/astrology/test_house_runtime_builder.py app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py app/tests/integration/test_reference_data_migrations.py` | `backend/` | PASS | 0 | All checks passed |
| `ruff format --check app/domain/astrology/builders/house_runtime_builder.py app/domain/astrology/natal_calculation.py app/infra/db/repositories/reference_repository.py app/infra/db/repositories/astrology_reference_sources.py app/infra/db/models/interpretation_reference.py migrations/versions/20260515_0109_create_astral_house_axis_definitions.py migrations/versions/20260515_0111_deversion_astral_house_axis_definitions.py tests/unit/domain/astrology/test_house_runtime_builder.py app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py app/tests/integration/test_reference_data_migrations.py` | `backend/` | PASS | 0 | 11 files already formatted |
| `rg -n "AstralHouseAxisDefinitionModel\.reference_version_id\|astral_house_axis_definitions_reference_version_id\|reference_version_id.*AstralHouseAxisDefinitionModel\|astral_house_axis_definitions.*reference_version_id" backend/app backend/migrations docs` | repo root | PASS | 0 | Hits uniquement dans la migration de downgrade technique `20260515_0111` |
| `git diff --check` | repo root | PASS | 0 | Aucun whitespace/conflict; avertissements CRLF Git seulement |
| `git diff --stat` | repo root | PASS | 0 | Diff limite au scope + capsule/status |
| `git status --short` | repo root | PASS | 0 | Statut final enregistre ci-dessous |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `pytest -q` | no | L'utilisateur a demande pas de tests globaux | Regression hors surface non executee | Tests cibles + lint + scans |
| Demarrage serveur persistant `uvicorn` | no | Le changement est backend/reference; un import applicatif court suffit sans lancer de session longue | Risque faible sur bootstrap runtime complet | `from app.main import app` PASS |

## DRY / No Legacy evidence

| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
| `resolve_house_axis`, `HOUSE_AXES`, ancien chemin `constants/house_axes.py` | `backend docs` | active_legacy_removed | Fichier constant supprime, imports retires, doc mise a jour | PASS |
| `reference_version_id` sur `AstralHouseAxisDefinitionModel` | code actif | active_legacy_removed | Modele, seed, source JSON et migration initiale retires de la dimension version | PASS |
| `house_axes` | code actif | canonical_new_contract | Nom du payload reference canonique, pas une constante legacy | PASS |
| `app.domain.prediction` / symboles prediction interdits dans astrology | `backend/app/domain/astrology` | zero_hit_guard | Scan RG-095 execute | PASS |

## Diff review

- `git diff --stat`: fichiers applicatifs, migrations, tests, docs + capsule CONDAMAD + statut story.
- Ancien fichier constant supprime intentionnellement.
- Aucun changement frontend ou dependance.
- `git diff --check`: PASS, seulement avertissements Git CRLF informatifs.

## Final worktree status

```text
 M _condamad/stories/story-status.md
 M backend/app/domain/astrology/builders/house_runtime_builder.py
 D backend/app/domain/astrology/constants/house_axes.py
 M backend/app/domain/astrology/natal_calculation.py
 M backend/app/infra/db/models/interpretation_reference.py
 M backend/app/infra/db/repositories/astrology_reference_sources.py
 M backend/app/infra/db/repositories/reference_repository.py
 M backend/app/tests/integration/test_reference_data_migrations.py
 M backend/app/tests/unit/test_prediction_reference_repository.py
 M backend/app/tests/unit/test_reference_data_service.py
 M backend/migrations/versions/20260515_0109_create_astral_house_axis_definitions.py
 M backend/tests/unit/domain/astrology/test_house_runtime_builder.py
 M "docs/recherches astro/astral_house_axis_definitions.json"
 M "docs/recherches astro/tables-maisons-et-roles.md"
?? _condamad/stories/remplacer-house-axes-constante-par-db/
?? backend/migrations/versions/20260515_0111_deversion_astral_house_axis_definitions.py
```

## Remaining risks

- Les suites globales n'ont pas ete lancees par instruction utilisateur.
- Les donnees runtime exigent maintenant 12 entrees `house_axes`; une base non migree ou non seedee echouera explicitement en `invalid_reference_data`.

## Suggested reviewer focus

- Verifier que le filtrage repository `language=en` et `astral_system=modern` correspond bien au perimetre attendu du payload de reference actuel.
- Verifier que l'erreur explicite sur axes absents est acceptable pour les environnements dont la DB n'a pas encore applique les migrations du 2026-05-15.

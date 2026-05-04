# Story CS-019 clarifier-frontiere-jobs-scripts-backend: Clarifier la frontiere entre jobs applicatifs et scripts backend

Status: done

## 1. Objective

Clarifier et appliquer une frontiere canonique stricte entre les traitements
applicatifs planifiables, les services reutilisables et les scripts backend.
`backend/app/scheduled_tasks` devient l'unique owner des traitements
applicatifs planifiables; l'ancien namespace `app.jobs` doit disparaitre. Les
outils manuels de seed, migration, debug, QA et revue doivent vivre sous
`backend/scripts` ou sous un owner applicatif reutilisable appele par un wrapper
CLI.

## 2. Trigger / Source

- Source type: refactor
- Source reference: demande utilisateur du 2026-05-04 apres analyse de `backend/app/jobs` et `backend/scripts`.
- Reason for change: le role de `backend/app/jobs` est aujourd'hui ambigu avec
  `backend/scripts`; des outils QA/revue et de la logique reutilisable vivent
  sous `app.jobs`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/scheduled_tasks`
- In scope:
  - Definir une classification deterministe des responsabilites actuellement presentes sous `backend/app/jobs`.
  - Deplacer sous `backend/app/scheduled_tasks` les entrypoints batch applicatifs recurrents ou planifiables.
  - Sortir de `backend/app/jobs` la logique de service reutilisable et les outils QA/revue manuels.
  - Supprimer `backend/app/jobs` sans shim ni re-export.
  - Ajouter ou mettre a jour une garde d'architecture qui refuse le retour de `app.jobs` et de logique non planifiable sous `app.scheduled_tasks`.
  - Mettre a jour les imports et tests directement affectes par les deplacements.
- Out of scope:
  - Reorganiser tout `backend/scripts`.
  - Modifier le comportement metier des predictions, calibrations ou baselines.
  - Changer le schema DB, les migrations Alembic ou les contrats API.
  - Ajouter une nouvelle dependance ou un nouveau runner de jobs.
- Explicit non-goals:
  - Ne pas affaiblir `RG-010`, `RG-011`, `RG-013`, `RG-015` ni les invariants prediction `RG-035` a `RG-038`.
  - Ne pas creer de wrappers de compatibilite pour conserver les anciens imports
    `app.jobs.calibration.percentile_calculator`,
    `app.jobs.qa.generate_qa_cases` ou
    `app.jobs.calibration.generate_review_grid`.
  - Ne pas deplacer les traitements applicatifs planifiables vers `backend/scripts` pour masquer la frontiere.

## 4. Operation Contract

- Operation type: move
- Primary archetype: service-boundary-refactor
- Archetype reason: la story corrige une frontiere de responsabilite entre entrypoints batch, services applicatifs reutilisables et outillage CLI.
- Behavior change allowed: no
- Behavior change constraints:
  - Les commandes existantes doivent produire le meme effet fonctionnel apres migration.
  - Les chemins d'import et les wrappers CLI peuvent changer uniquement vers les owners canoniques documentes.
  - Les tests doivent etre adaptes aux nouveaux owners sans encoder l'ancien chemin comme comportement nominal.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un fichier de `backend/app/jobs` est identifie
  comme interface externe documentee ou planifiee hors repo et ne peut pas etre
  deplace sans rupture operationnelle.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La source executable est une garde d'architecture/AST sur le contenu autorise de `app.jobs`. |
| Baseline Snapshot | yes | L'inventaire des fichiers, imports et entrypoints jobs doit etre capture avant/apres. |
| Ownership Routing | yes | Chaque responsabilite doit etre routee vers `jobs`, `services`, `ops` ou `scripts`. |
| Allowlist Exception | no | Aucune exception durable n'est autorisee pour laisser de l'outillage manuel dans `app.jobs`. |
| Contract Shape | no | Aucun contrat API, DTO, OpenAPI ou type frontend n'est touche. |
| Batch Migration | no | Le scope est borne a un seul package et ses consommateurs directs. |
| Reintroduction Guard | yes | Une garde doit echouer si `app.jobs` redevient proprietaire d'outillage manuel ou de logique de service. |
| Persistent Evidence | yes | La classification et les inventaires avant/apres doivent rester auditable dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard dans `backend/app/tests/unit/test_backend_jobs_boundary.py` inspectant `backend/app/scheduled_tasks`, l'absence de `backend/app/jobs` et les imports consommateurs.
  - Commande cible: `pytest -q app/tests/unit/test_backend_jobs_boundary.py`.
- Secondary evidence:
  - `rg --files app/jobs`
  - `rg -n "from app\.jobs|import app\.jobs" app tests scripts -g "*.py"`
  - `rg -n "app\.jobs|from app\.jobs|import app\.jobs" app tests`
- Static scans alone are not sufficient for this story because:
  - La classification explicite decide si un fichier est acceptable; la garde
    doit verifier cette classification et les patterns interdits.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/jobs-boundary-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/jobs-boundary-after.md`
- Expected invariant:
  - Les traitements planifiables restent disponibles sous `app.scheduled_tasks`, et `app.jobs` est absent.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Job applicatif planifiable | `backend/app/scheduled_tasks` | `backend/scripts` seul sans owner applicatif ou `backend/app/jobs` |
| Logique de service reutilisable | `backend/app/services/**` | `backend/app/jobs/**` |
| Donnees/configuration de calibration reutilisees | `backend/app/services/**` ou `backend/app/domain/**` apres classification | `backend/app/jobs/**` si consomme hors job |
| Outil QA manuel | `backend/scripts` wrapper, avec logique sous `backend/app/ops/**` ou service existant si reutilisable | `backend/app/jobs/**` |
| Outil de revue/documentation manuel | `backend/scripts` wrapper, avec logique sous `backend/app/ops/**` si testee | `backend/app/jobs/**` |
| Seed, migration, backfill ou debug ponctuel | `backend/scripts` | `backend/app/jobs/**` |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Classification jobs | `jobs-boundary-classification.md` | Decider le owner canonique de chaque fichier actuellement sous `backend/app/jobs`. |
| Inventaire avant | `_condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/jobs-boundary-before.md` | Capturer fichiers, imports et entrypoints avant migration. |
| Inventaire apres | `_condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/jobs-boundary-after.md` | Prouver la frontiere finale et les imports canoniques. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route, field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- importable Python modules
- forbidden symbols or states

Required forbidden examples:

- namespace `backend/app/jobs` recree
- executable logic in `backend/app/scheduled_tasks/__init__.py`
- reusable service class owned by `backend/app/jobs/**`
- QA/review CLI owner under `backend/app/jobs/qa/**` or `backend/app/jobs/calibration/generate_review_grid.py`
- tests importing moved non-job helpers from `app.jobs.*`

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_jobs_boundary.py` checks the canonical boundary.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/jobs/__init__.py` - contient le meme hash que
  `backend/app/jobs/qa/generate_qa_cases.py`; `import app.jobs` pointe donc
  vers un script QA au lieu d'un package neutre.
- Evidence 2: `backend/app/jobs/calibration/percentile_calculator.py` -
  definit `PercentileCalculatorService`, une logique reutilisable qui ressemble
  a un service applicatif plutot qu'a un entrypoint job.
- Evidence 3: `backend/app/jobs/calibration/generate_review_grid.py` - expose
  une CLI de generation de grille de revue vers `docs/calibration`, plus proche
  d'un outil manuel que d'un job planifiable.
- Evidence 4: `backend/app/jobs/refresh_user_baselines.py` - expose
  `run_job()` pour un traitement applicatif recurrent qui doit migrer sous
  l'owner plus explicite `app.scheduled_tasks`.
- Evidence 5: `backend/scripts/seed_31_prediction_reference_v2.py` - montre le pattern acceptable d'un wrapper CLI mince qui appelle un service applicatif canonique.
- Evidence 6: `backend/scripts/run_ops_review_queue_alerts.py` - montre un
  script CLI qui parse les options puis appelle un service applicatif, sans
  placer la logique metier sous `scripts`.
- Evidence 7: `backend/app/tests/unit/test_calibration_dataset.py`,
  `backend/app/tests/unit/test_generate_review_grid.py` et
  `backend/app/tests/unit/test_percentile_calculator.py` importent encore des
  helpers non-job depuis `app.jobs`.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage, notamment `RG-010`, `RG-011`, `RG-013`, `RG-015`, `RG-035`, `RG-038`.

## 6. Target State

After implementation:

- `backend/app/jobs` est supprime physiquement, sans shim ni package marker.
- `backend/app/scheduled_tasks` contient uniquement des entrypoints batch applicatifs planifiables et leurs helpers strictement prives.
- La logique reusable de percentile/calibration sort de `app.jobs` vers l'owner
  canonique documente dans `jobs-boundary-classification.md`.
- Les outils QA/revue manuels disposent d'un wrapper CLI sous `backend/scripts` et d'un owner applicatif non-job si une logique testee doit rester reutilisable.
- Les tests importent les owners canoniques et une garde d'architecture bloque la reintroduction de `app.jobs` ou de surfaces non planifiables sous `app.scheduled_tasks`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-010` - les tests ajoutes ou deplaces doivent rester sous les racines collectees par `backend/pyproject.toml`.
  - `RG-011` - les nouveaux tests backend ne doivent pas importer directement `SessionLocal` ou `engine`.
  - `RG-013` - les helpers partages de tests ne doivent pas etre importes depuis des modules `test_*.py`.
  - `RG-015` - les tests de qualite/ops lies aux scripts doivent rester inventories si un test script/ops est ajoute.
  - `RG-035` - la logique pure prediction ne doit pas migrer vers une couche dependante de services/infra par opportunisme.
  - `RG-038` - aucun import ou fichier `app.prediction` ne doit etre recree pendant le reclassement calibration/prediction.
  - `RG-039` - invariant cree par cette story pour la frontiere `backend/app/scheduled_tasks` et l'extinction de `app.jobs`.
- Non-applicable invariants:
  - `RG-001` - aucune route historique ou facade HTTP n'est touchee.
  - `RG-025` - la politique reseau Stripe n'est pas touchee.
  - `RG-037` - les routeurs API prediction ne sont pas modifies.
- Required regression evidence:
  - Classification persistante, inventaires avant/apres, garde `test_backend_jobs_boundary.py`, scans imports, tests calibration/baseline cibles.
- Allowed differences:
  - Changements de chemins d'import vers les owners canoniques; aucun changement de comportement batch attendu.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Classification persistante des fichiers initiaux. | `test_backend_jobs_boundary.py` + artefacts before/after. |
| AC2 | `backend/app/jobs` est supprime sans marker ni shim. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_jobs_boundary.py`. |
| AC3 | Les services calibration/percentile ne sont plus sous `app.jobs`. | Evidence profile: `python_import_absence`; `pytest -q app/tests/unit/test_percentile_calculator.py`. |
| AC4 | Les outils QA/revue manuels ne sont plus owners sous `app.jobs`. | Evidence profile: `ownership_routing`; `pytest -q app/tests/unit/test_generate_review_grid.py`. |
| AC5 | Traitements planifiables observables sous `app.scheduled_tasks`. | `pytest -q app/tests/unit/test_calibration_job.py`. |
| AC6 | Une garde bloque le retour de `app.jobs`. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_jobs_boundary.py`. |
| AC7 | Les invariants transverses restent respectes. | Evidence profile: `regression_guardrails`; `pytest -q app/tests/unit/test_backend_test_topology.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer et classer l'etat initial de `app.jobs` (AC: AC1)
  - [ ] Subtask 1.1 - Generer `jobs-boundary-before.md` avec `rg --files app/jobs` et les imports consommateurs.
  - [ ] Subtask 1.2 - Ecrire `jobs-boundary-classification.md` avec une decision par fichier.

- [ ] Task 2 - Neutraliser le package `app.jobs` et definir la garde (AC: AC2, AC6)
  - [ ] Subtask 2.1 - Supprimer `backend/app/jobs/__init__.py` et creer `backend/app/scheduled_tasks/__init__.py` sans side effect.
  - [ ] Subtask 2.2 - Ajouter `backend/app/tests/unit/test_backend_jobs_boundary.py`.

- [ ] Task 3 - Reclasser la logique reusable hors `app.jobs` (AC: AC3, AC5)
  - [ ] Subtask 3.1 - Deplacer `PercentileCalculatorService` et helpers associes vers l'owner canonique choisi.
  - [ ] Subtask 3.2 - Mettre a jour les imports de jobs et tests sans shim ni re-export.

- [ ] Task 4 - Reclasser les outils QA/revue hors `app.jobs` (AC: AC4)
  - [ ] Subtask 4.1 - Deplacer ou wrapper `generate_qa_cases`, `validate_dataset` et `generate_review_grid` selon `jobs-boundary-classification.md`.
  - [ ] Subtask 4.2 - Mettre a jour les tests pour cibler les nouveaux owners.

- [ ] Task 5 - Prouver la preservation comportementale et les non-regressions (AC: AC5, AC7)
  - [ ] Subtask 5.1 - Generer `jobs-boundary-after.md`.
  - [ ] Subtask 5.2 - Executer lint, tests cibles, scans negatifs et validateurs CONDAMAD.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/scripts/seed_31_prediction_reference_v2.py` comme exemple de wrapper CLI mince vers un service canonique.
  - `backend/scripts/run_ops_review_queue_alerts.py` comme exemple de parsing CLI hors logique metier.
  - Les services prediction/calibration existants avant de creer un nouveau package.
- Do not recreate:
  - Deux implementations actives du calcul de percentiles.
  - Deux definitions actives des profils de calibration.
  - Un second registre d'ownership concurrent pour `backend/scripts`.
- Shared abstraction allowed only if:
  - Elle devient l'unique owner d'une responsabilite identifiee dans `jobs-boundary-classification.md`.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- namespace `backend/app/jobs`
- logique executable dans `backend/app/scheduled_tasks/__init__.py`
- `from app.jobs.calibration.percentile_calculator import`
- `from app.jobs.calibration import generate_review_grid`
- `from app.jobs.calibration import validate_dataset`
- `from app.jobs.qa.generate_qa_cases import`
- re-export depuis `app.jobs.calibration.__init__` pour masquer un deplacement

## 11. Removal Classification Rules

Use this section only when `Operation type: remove` or the archetype is a removal archetype. Otherwise write:

- Removal classification: not applicable

## 12. Removal Audit Format

Use this section only when `Operation type: remove` or the archetype is a removal archetype. Otherwise write:

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Refresh baseline utilisateur recurrent | `backend/app/scheduled_tasks/refresh_user_baselines.py` | `backend/scripts` contenant la logique metier ou `backend/app/jobs` |
| Generation dataset calibration recurrente | `backend/app/scheduled_tasks/generate_daily_calibration_dataset.py` | outil manuel sous `scripts` ou `backend/app/jobs` |
| Calcul percentile reusable | `backend/app/services/**` owner a confirmer par classification | `backend/app/jobs/calibration/percentile_calculator.py` |
| Profils et runtime calibration reutilises | Owner documente dans `jobs-boundary-classification.md` | `backend/app/jobs/calibration/**` consomme hors job |
| Generation cas QA | `backend/scripts` wrapper + owner documente dans la classification | `backend/app/jobs/qa/**` |
| Grille de revue calibration | `backend/scripts` wrapper + owner `app.ops` si logique testee | `backend/app/jobs/calibration/generate_review_grid.py` |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/jobs/__init__.py`
- `backend/app/jobs/refresh_user_baselines.py`
- `backend/app/jobs/generate_daily_calibration_dataset.py`
- `backend/app/jobs/compute_calibration_percentiles.py`
- `backend/app/scheduled_tasks/__init__.py`
- `backend/app/scheduled_tasks/refresh_user_baselines.py`
- `backend/app/scheduled_tasks/generate_daily_calibration_dataset.py`
- `backend/app/scheduled_tasks/compute_calibration_percentiles.py`
- `backend/app/jobs/calibration/percentile_calculator.py`
- `backend/app/jobs/calibration/natal_profiles.py`
- `backend/app/jobs/calibration/runtime.py`
- `backend/app/jobs/calibration/validate_dataset.py`
- `backend/app/jobs/calibration/generate_review_grid.py`
- `backend/app/jobs/qa/generate_qa_cases.py`
- `backend/app/tests/unit/test_calibration_job.py`
- `backend/app/tests/unit/test_calibration_dataset.py`
- `backend/app/tests/unit/test_generate_review_grid.py`
- `backend/app/tests/unit/test_percentile_calculator.py`
- `backend/app/tests/integration/test_user_baseline_refresh_job.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/jobs/__init__.py` - supprimer le package marker.
- `backend/app/scheduled_tasks/__init__.py` - marker neutre des traitements planifiables.
- `backend/app/scheduled_tasks/compute_calibration_percentiles.py` - importer le service depuis son owner canonique.
- `backend/app/scheduled_tasks/generate_daily_calibration_dataset.py` - importer profils/runtime depuis leur owner canonique si deplaces.
- `backend/app/scheduled_tasks/refresh_user_baselines.py` - conserver le comportement du job baseline sous owner explicite.
- `backend/app/jobs/calibration/percentile_calculator.py` - deplacer ou supprimer apres migration vers owner canonique.
- `backend/app/jobs/calibration/natal_profiles.py` - deplacer si classification `config-calibration` reutilisable.
- `backend/app/jobs/calibration/runtime.py` - deplacer si consomme hors entrypoint job.
- `backend/app/jobs/calibration/validate_dataset.py` - deplacer vers wrapper/outillage canonique.
- `backend/app/jobs/calibration/generate_review_grid.py` - deplacer vers wrapper/outillage canonique.
- `backend/app/jobs/qa/generate_qa_cases.py` - deplacer vers wrapper/outillage canonique.
- `backend/scripts/*.py` - ajouter les wrappers CLI minces decides dans la classification.
- `_condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/jobs-boundary-classification.md` - decisions de routing.
- `_condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/jobs-boundary-before.md` - snapshot initial.
- `_condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/jobs-boundary-after.md` - snapshot final.

Likely tests:

- `backend/app/tests/unit/test_backend_jobs_boundary.py` - nouvelle garde de frontiere.
- `backend/app/tests/unit/test_calibration_job.py` - imports job calibration.
- `backend/app/tests/unit/test_calibration_dataset.py` - validation dataset.
- `backend/app/tests/unit/test_generate_review_grid.py` - nouvel owner de grille.
- `backend/app/tests/unit/test_percentile_calculator.py` - nouvel owner du service percentile.
- `backend/app/tests/integration/test_user_baseline_refresh_job.py` - preservation job baseline.

Files not expected to change:

- `backend/alembic` - aucun changement schema ou migration DB.
- `frontend/src` - aucun impact frontend.
- `backend/app/api` - aucun contrat HTTP ou routeur ne change.
- `backend/pyproject.toml` - aucune dependance nouvelle.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_backend_jobs_boundary.py
pytest -q app/tests/unit/test_calibration_job.py app/tests/unit/test_calibration_dataset.py
pytest -q app/tests/unit/test_generate_review_grid.py app/tests/unit/test_percentile_calculator.py
pytest -q app/tests/unit/test_calibration_runtime.py
pytest -q app/tests/integration/test_user_baseline_refresh_job.py
pytest -q app/tests/unit/test_backend_test_topology.py app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_backend_test_helper_imports.py
rg -n "from app\.jobs\.calibration\.(percentile_calculator|natal_profiles|runtime)" app tests
rg -n "from app\.jobs\.qa\.generate_qa_cases" app tests
rg -n "from app\.jobs\.calibration import (generate_review_grid|validate_dataset)" app tests
rg --files app/prediction
rg -n "from app\.prediction|import app\.prediction" app tests -g "*.py"
Pop-Location
```

Then from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/00-story.md
```

## 22. Regression Risks

- Risk: un outil QA manuel reste sous `app.jobs` parce qu'il est teste comme job nominal.
  - Guardrail: classification persistante + `test_backend_jobs_boundary.py`.
- Risk: le deplacement du service percentile casse la calibration par import, pas par comportement.
  - Guardrail: tests unitaires percentile/calibration et scans imports interdits.
- Risk: un wrapper de compatibilite conserve l'ancien chemin `app.jobs.*`.
  - Guardrail: No Legacy scans et interdiction de re-export.
- Risk: un nouveau test viole le harnais DB ou la topologie backend.
  - Guardrail: `RG-010`, `RG-011`, `RG-013` dans le plan de validation.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Keep new or significantly modified Python files documented with a French file-level comment and French docstrings for public or non-trivial functions/classes.

## 24. References

- `backend/app/jobs` - package a clarifier.
- `backend/scripts` - repertoire des wrappers CLI, seeds, migrations, checks et debug.
- `backend/app/tests/unit/test_calibration_job.py` - tests du job calibration.
- `backend/app/tests/unit/test_percentile_calculator.py` - tests du service aujourd'hui sous `app.jobs`.
- `backend/app/tests/unit/test_scripts_ownership.py` - exemple de garde d'ownership durable.
- `_condamad/stories/regression-guardrails.md` - registre des invariants consultes et enrichi par `RG-039`.

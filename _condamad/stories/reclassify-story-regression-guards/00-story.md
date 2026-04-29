# Story reclassify-story-regression-guards: Rename and map story tests to durable backend invariants

Status: ready-for-review

## 1. Objective

Reclassifier les tests story-numbered backend en guards nommes par invariants durables.
La story conserve les protections utiles et bloque tout ecartement non approuve.
Elle produit un mapping entre tests conserves et surfaces protegees, notamment RG-001 a RG-009.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-tests/2026-04-28-1600`
- Reason for change: F-004 indique que 44 fichiers et 262 tests story-numbered masquent la responsabilite durable de leurs guards.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend regression and No Legacy test guard catalog
- In scope:
  - Inventorier chaque fichier `test_story_*.py`.
  - Classifier chaque test en keep, merge, rewrite, remove-candidate ou needs-user-decision.
  - Mapper les tests conserves vers un invariant durable ou un RG existant.
  - Renommer ou deplacer un premier lot coherent de guards sans changer leurs assertions.
  - Ajouter une garde qui interdit de nouveaux tests story-numbered sans justification.
- Out of scope:
  - Ecarter un guard legacy sans remplacement ou decision utilisateur.
  - Modifier les routes/API protegees par les guards.
  - Corriger la topologie complete des racines de tests.
- Explicit non-goals:
  - Ne pas Ecarter en bloc les tests legacy-heavy.
  - Ne pas rendre RG-001..RG-009 moins stricts.
  - Ne pas ajouter de dossier racine sous `backend/`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: registry-catalog-refactor
- Archetype reason: la story transforme un catalogue implicite de guards historiques en registre durable d'invariants.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les assertions des guards conserves doivent rester equivalentes.
  - Toute ecartement doit etre bloquee sauf preuve `dead` et decision explicite si surface historique active.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un test story-numbered protege une surface encore active mais sans invariant cible clair.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | Cette story classe des fichiers de tests, pas des routes runtime. |
| Baseline Snapshot | yes | Le nombre de fichiers/tests story-numbered doit etre mesure avant/apres. |
| Ownership Routing | yes | Chaque guard doit avoir un invariant proprietaire. |
| Allowlist Exception | yes | Les noms `test_story_*.py` restants doivent etre exceptionnels et justifies. |
| Contract Shape | no | Aucun contrat API n'est modifie. |
| Batch Migration | yes | La migration doit se faire par lots pour limiter le risque. |
| Reintroduction Guard | yes | Les nouveaux tests story-numbered doivent etre bloques. |
| Persistent Evidence | yes | Le mapping guards -> invariants est un artefact durable. |

## 4b. Runtime Source of Truth

- Runtime source of truth: not applicable
- Reason: no runtime API, DB schema, generated manifest, or production registration is changed.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/reclassify-story-regression-guards/story-test-inventory-before.md`
- Comparison after implementation:
  - `_condamad/stories/reclassify-story-regression-guards/story-test-inventory-after.md`
  - `_condamad/stories/reclassify-story-regression-guards/story-guard-mapping.md`
- Expected invariant:
  - Aucun fichier `test_story_*.py` non classifie ne reste.
- Allowed differences:
  - Renommage/deplacement avec assertions preservees; baisse du nombre de fichiers story-numbered uniquement apres mapping.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Historical API facade guard | RG-001 mapped regression suite | Unnamed `test_story_*.py` |
| API router architecture guard | RG-002/RG-003 mapped architecture suite | Story-number-only file |
| API error guard | RG-004 mapped API error suite | Hidden legacy keyword test |
| API/services boundary guard | RG-005/RG-006/RG-008 mapped architecture suite | Duplicate guard with unclear owner |
| Removed schema package guard | RG-009 mapped No Legacy suite | Unclassified legacy prune test |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `story-guard-mapping.md` | `story-numbered inventory` | Audit baseline F-004. | Exit: every listed file is classified. |
| `_condamad/stories/reclassify-story-regression-guards/story-guard-mapping.md` | `needs-user-decision` | Protected surface unclear. | Exit condition: user decision recorded. |
## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API payload, DTO, status code, generated client type, or frontend type changes.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 - Inventory | `test_story_*.py` | Mapping register | None | Collect-only | All classified | Unknown invariant |
| 2 - RG mapped guards | Story-number names | Durable guard suite names | Pytest paths/imports | Targeted tests | Old filename absent for migrated lot | Assertion drift |
| 3 - Reintroduction guard | Unguarded naming | Naming guard | Future tests | Guard test | New story-number file fails | User-approved exception missing |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Inventory before | `_condamad/stories/reclassify-story-regression-guards/story-test-inventory-before.md` | Lister les 44 fichiers initiaux. |
| Mapping | `_condamad/stories/reclassify-story-regression-guards/story-guard-mapping.md` | Classifier chaque guard. |
| Inventory after | `_condamad/stories/reclassify-story-regression-guards/story-test-inventory-after.md` | Prouver zero non-classifie. |

## 4i. Reintroduction Guard

The implementation must add or update deterministic guards that fail if:

- un nouveau fichier `test_story_*.py` apparait sans exception documentee;
- un guard RG-001..RG-009 est supprime sans test de remplacement;
- un fichier story-numbered conserve n'a pas de ligne dans `story-guard-mapping.md`.

Required architecture guard: pytest -q app/tests/unit/test_backend_architecture_guard.py with AST guard evidence.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md` - E-005 trouve 44 fichiers `test_story_*.py` et 262 fonctions `test_story_*`.
- Evidence 2: `_condamad/audits/backend-tests/2026-04-28-1600/05-executive-summary.md` - recommande de ne pas Ecarter en bloc ces tests.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - RG-001..RG-009 consultes avant cadrage.

## 6. Target State

- Chaque test story-numbered est mappe a un invariant durable, migre, ou bloque par decision utilisateur.
- Les tests conserves portent des noms de suites lisibles par surface protegee.
- Une garde empeche la reintroduction de fichiers story-numbered non justifies.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - beaucoup de tests legacy peuvent proteger les facades supprimees.
  - `RG-002` - les guards routeurs doivent rester proprietaires de l'architecture API.
  - `RG-003` - les guards montage runtime/OpenAPI ne doivent pas disparaitre.
  - `RG-004` - les guards erreurs API doivent garder leur enveloppe.
  - `RG-005` - les guards frontiere API/services doivent rester actifs.
  - `RG-006` - les guards adaptateur API doivent rester actifs.
  - `RG-007` - les guards observability LLM doivent rester actifs.
  - `RG-008` - les guards exceptions API/SQL doivent rester actifs.
  - `RG-009` - le guard anti-retour schemas legacy doit rester actif.
- Non-applicable invariants:
  - none for story-numbered regression guards.
- Required regression evidence:
  - Mapping complet, tests cibles des suites migrees, collecte pytest.
- Allowed differences:
  - Renommage et regroupement de tests; aucune baisse de protection sans decision.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Tous les fichiers story-numbered sont classes. | Evidence profile: `baseline_before_after_diff`; `rg -n "test_story_|RG-" story-guard-mapping.md`. |
| AC2 | Les guards conserves ont un invariant. | Evidence profile: `baseline_before_after_diff`; `rg -n "RG-00[1-9]|invariant" story-guard-mapping.md`. |
| AC3 | Un premier lot garde ses assertions. | Evidence profile: `runtime_openapi_contract`; `pytest -q app/tests/unit/test_backend_story_guard_names.py`. |
| AC4 | Aucun fichier story-numbered non classifie ne reste. | Evidence profile: `repo_wide_negative_scan`; `rg --files backend -g test_story_*.py` compare au mapping. |
| AC5 | Une garde bloque les nouveaux noms non approuves. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_story_guard_names.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer l'inventaire story-numbered (AC: AC1)
- [x] Task 2 - Classifier chaque fichier et invariant cible (AC: AC1, AC2)
- [x] Task 3 - Migrer un lot coherent de guards (AC: AC3)
- [x] Task 4 - Ajouter la garde anti-reintroduction (AC: AC4, AC5)
- [x] Task 5 - Executer collecte, tests cibles et lint (AC: AC3, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `_condamad/stories/regression-guardrails.md` comme registre des invariants transverses.
  - Les assertions existantes des tests conserves.
- Do not recreate:
  - Des doublons de guards pour la meme surface.
  - Un second registre RG concurrent.
- Shared abstraction allowed only if:
  - Elle supprime une duplication de helper de guard existante.

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

- Nouveau fichier `test_story_*.py` sans exception.
- ecartement d'un guard RG-001..RG-009 sans remplacement.
- Mapping incomplet marque comme termine.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Regression guard invariant | `_condamad/stories/regression-guardrails.md` or story-local durable mapping | Filename story number only |
| Story guard mapping | `_condamad/stories/reclassify-story-regression-guards/story-guard-mapping.md` | Ad hoc comments in test files only |

## 14. Delete-Only Rule

- Delete-Only Rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 17. Files to Inspect First

- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/05-executive-summary.md`
- `_condamad/stories/regression-guardrails.md`
- All files from `rg --files backend -g test_story_*.py`

## 18. Expected Files to Modify

Likely files:

- Story-numbered test files selected for first migration lot.
- Durable target guard files under existing backend test roots.
- `backend/app/tests/unit/test_backend_story_guard_names.py` or `backend/tests/unit/test_backend_story_guard_names.py`.
- `_condamad/stories/reclassify-story-regression-guards/story-guard-mapping.md`.

Likely tests:

- `backend/app/tests/unit/test_backend_story_guard_names.py` - garde de nommage story-numbered.

Files not expected to change:

- `backend/app/api` - no production route change.
- `frontend/src` - no frontend change.
- `requirements.txt` - must not be created.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_backend_story_guard_names.py
pytest --collect-only -q --ignore=.tmp-pytest
pytest -q
rg --files . -g test_story_*.py
rg -n "legacy|deprecated|decommission|removed_legacy" app/tests tests app/domain -g test_*.py
```

Story validation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/reclassify-story-regression-guards/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/reclassify-story-regression-guards/00-story.md
```

## 21. Regression Risks

- Risk: un guard legacy utile est supprime.
  - Guardrail: classification obligatoire et RG mapping.
- Risk: le renommage change la collecte.
  - Guardrail: collect-only avant/apres et tests cibles.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Respecter l'activation du venv avant toute commande Python.
- Ne pas creer de `requirements.txt`.

## 23. References

- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md` - preuve E-005 et E-010.
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md` - finding F-004.
- `_condamad/audits/backend-tests/2026-04-28-1600/03-story-candidates.md` - candidat SC-004.
- `_condamad/stories/regression-guardrails.md` - registre RG-001..RG-009.

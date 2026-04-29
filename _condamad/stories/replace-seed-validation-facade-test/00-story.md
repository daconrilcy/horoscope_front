# Story replace-seed-validation-facade-test: Replace the seed validation facade test with executable behavior

Status: ready-for-review

## 1. Objective

Remplacer le test facade ackend/app/tests/unit/test_seed_validation.py par une assertion executable.
Si la regle produit n'existe plus, le test doit etre traite avec une decision explicite.
La story corrige le faux signal donne par un test qui passe avec pass.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-tests/2026-04-28-1600`
- Reason for change: F-006 identifie un test collecte qui ne verifie aucun comportement.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: seed validation unit test coverage
- In scope:
  - Identifier le comportement attendu pour une persona requise vide.
  - Remplacer `pass` par une assertion ou un `pytest.raises` executable.
  - Supprimer le test facade si la regle est obsolete, avec preuve de decision.
  - Ajouter un scan/garde contre `assert True` et tests a corps `pass` dans les tests backend.
- Out of scope:
  - Revoir tout le systeme de seed.
  - Modifier les donnees produit au-dela de la validation cible.
  - Changer la topologie globale des tests.
- Explicit non-goals:
  - Ne pas garder un test qui passe sans assertion.
  - Ne pas introduire une compatibilite qui avale silencieusement l'erreur attendue.
  - Ne pas ajouter de dossier racine sous `backend/`.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: le test actuel est une facade historique sans comportement executable; il doit etre remplace ou supprime.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Si la regle persona vide est active, le comportement de validation doit etre implemente et teste.
  - Si la regle est obsolete, le test facade doit etre supprime avec evidence de decision.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: la regle produit "required persona empty values are invalid" n'est pas confirmable depuis le code ou la documentation.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La preuve doit executer la validation seed ou le test supprime. |
| Baseline Snapshot | yes | Le test facade actuel et les no-op tests doivent etre captures avant/apres. |
| Ownership Routing | yes | La regle doit appartenir au module de validation seed, pas au commentaire du test. |
| Allowlist Exception | no | Aucun test no-op n'est autorise. |
| Contract Shape | no | Aucun contrat API n'est modifie. |
| Batch Migration | no | La surface est un seul test/fonction de validation. |
| Reintroduction Guard | yes | Une garde doit bloquer `pass`/`assert True` dans les tests sauf exception explicite. |
| Persistent Evidence | yes | La decision implement-or-delete doit etre persistante. |

## 4b. Runtime Source of Truth

- Primary source of truth:`n  - AST guard and loaded config evidence for this story.`n  - Execution de `pytest -q app/tests/unit/test_seed_validation.py`.
  - Module de validation seed inspecte par le dev agent apres recherche.
- Secondary evidence:
  - Scan `rg -n "assert True|pass$" app/tests tests -g test_*.py`.
- Static scans alone are not sufficient for this story because:
  - la correction doit prouver un comportement executable ou l'absence approuvee de la regle.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/replace-seed-validation-facade-test/noop-test-scan-before.md`
  - `_condamad/stories/replace-seed-validation-facade-test/seed-validation-current-behavior.md`
- Comparison after implementation:
  - `_condamad/stories/replace-seed-validation-facade-test/noop-test-scan-after.md`
  - `_condamad/stories/replace-seed-validation-facade-test/seed-validation-decision.md`
- Expected invariant:
  - Aucun test collecte ne passe uniquement via `pass` ou `assert True` sans skip explicite et raison trackee.
- Allowed differences:
  - Remplacement du test par une assertion; ou suppression du fichier si la regle est obsolete.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Seed validation behavior | Existing seed validation module or focused validation service | Comment in a no-op test |
| Unit coverage | `backend/app/tests/unit/test_seed_validation.py` or approved replacement | `pass` body |
| No-op test guard | Dedicated test-quality guard | Manual review only |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no no-op test exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API payload, DTO, status code, generated client type, or frontend type changes.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: the story is scoped to one facade test and its direct validation behavior.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| No-op scan before | `_condamad/stories/replace-seed-validation-facade-test/noop-test-scan-before.md` | Capturer le facade test. |
| Current behavior | `_condamad/stories/replace-seed-validation-facade-test/seed-validation-current-behavior.md` | Montrer si la validation existe deja. |
| Decision | `_condamad/stories/replace-seed-validation-facade-test/seed-validation-decision.md` | Documenter implement or delete. |
| No-op scan after | `_condamad/stories/replace-seed-validation-facade-test/noop-test-scan-after.md` | Prouver absence de facade. |

## 4i. Reintroduction Guard

The implementation must add or update deterministic guards that fail if:

- `backend/app/tests/unit/test_seed_validation.py` contient un corps `pass` sans skip explicite;
- un test backend contient `assert True` comme seule assertion;
- un nouveau test no-op est ajoute sans `pytest.skip` avec raison trackee.

Required architecture guard against reintroduction:
- pytest -q app/tests/unit/test_backend_noop_tests.py with AST guard evidence.
- Forbidden symbols pass and ssert True must not be reintroduced.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md` - E-006 identifie le test facade.
- Evidence 2: `backend/app/tests/unit/test_seed_validation.py` - le test seed validation actuel se termine par `pass`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Le test seed validation verifie un comportement executable ou est supprime comme obsolete.
- La decision de comportement est documentee dans le dossier de story.
- Une garde empeche les tests backend no-op collectes.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-004` - si la validation seed influence des erreurs applicatives, elle ne doit pas reconstruire localement un contrat d'erreur API.
- Non-applicable invariants:
  - `RG-001`, `RG-002`, `RG-003`, `RG-005`, `RG-006`, `RG-007`, `RG-008`, `RG-009` - la story ne touche pas les routes API, schemas legacy ou proprietes router.
- Required regression evidence:
  - Test seed cible, scan no-op, collecte pytest.
- Allowed differences:
  - Ajout d'une assertion de validation ou suppression approuvee du test facade.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le comportement persona vide est decide. | Evidence profile: `baseline_before_after_diff`; `rg -n "SeedValidationError|persona" app tests`. |
| AC2 | Le test facade ne contient plus `pass`. | Evidence profile: `repo_wide_negative_scan`; `rg -n "assert True|pass$" app/tests tests -g test_*.py`. |
| AC3 | La validation est executable ou la decision est tracee. | Evidence profile: `runtime_openapi_contract`; `pytest -q app/tests/unit/test_seed_validation.py`. |
| AC4 | Une garde bloque les tests no-op futurs. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_noop_tests.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le comportement et le scan no-op avant changement (AC: AC1, AC2)
- [x] Task 2 - Decider implement-or-delete pour la regle seed (AC: AC1)
- [x] Task 3 - Remplacer le facade test par une assertion ou supprimer le test obsolete (AC: AC2, AC3)
- [x] Task 4 - Ajouter la garde anti no-op tests (AC: AC4)
- [x] Task 5 - Executer validations dans le venv (AC: AC3, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Module ou fonction de validation seed existante apres inspection.
  - Pytest `raises` ou assertions directes.
- Do not recreate:
  - Une validation seed parallele uniquement pour le test.
  - Une exception silencieuse qui preserve le faux positif.
- Shared abstraction allowed only if:
  - La meme validation est utilisee par plusieurs chemins seed.

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

- `pass` comme corps du test seed validation.
- `assert True` comme assertion de facade.
- `pytest.mark.skip` sans raison explicite et ticket/decision.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: test verifies active seed validation behavior.
- `historical-facade`: test exists only to document future work and passes with no assertion.
- `dead`: product rule is obsolete and no code path should validate it.
- 
eeds-user-decision: product rule cannot be confirmed from code/docs.
- `external-active`: external seed contract or operator workflow depends on current behavior.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must contain executable assertion. |
| `historical-facade` | `delete`, `replace` | Must not remain as no-op. |
| `dead` | `delete` | Must be deleted with decision evidence. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `test_seed_validation.py::persona_empty` | test | `historical-facade` | pytest | assertion | decision-set | E-006 | false positive |

Allowed decisions for this audit: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path when applicable:

- `_condamad/stories/replace-seed-validation-facade-test/seed-validation-decision.md`
## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Seed validation rule | Existing seed validation implementation after inspection | Comment inside no-op test |
| No-op test policy | Dedicated test-quality guard | Manual review only |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving a wrapper
- adding a compatibility alias
- preserving the old path through re-export
- replacing deletion with soft-disable behavior
- leaving `pass` plus comment

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted.
If the rule is product-active but ambiguous, the dev agent must stop and record a user decision.
## 16. Generated Contract Check

Required generated-contract evidence:

- OpenAPI path absence: no API route path is created or removed by this story.
- generated client/schema absence: `rg -n "seed_validation|required persona|SeedValidationError" ../frontend app` records no generated client/schema impact.
- route manifest absence: no FastAPI route manifest entry is expected for this unit-only validation story.
## 17. Files to Inspect First

- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/unit/test_seed_validation.py`
- Seed validation implementation files found by `rg -n "SeedValidationError|seed validation|required persona|persona" backend/app backend/scripts backend/tests`

## 18. Expected Files to Modify

Likely files:

- `backend/app/tests/unit/test_seed_validation.py` - replace facade with executable assertion or delete obsolete test.
- Existing seed validation module if the rule is active but unimplemented.
- `backend/app/tests/unit/test_backend_noop_tests.py` or `backend/tests/unit/test_backend_noop_tests.py` - no-op guard.
- `_condamad/stories/replace-seed-validation-facade-test/*.md` - evidence and decision.

Likely tests:

- `backend/app/tests/unit/test_seed_validation.py`
- No-op guard test.

Files not expected to change:

- `frontend/src` - no frontend change.
- `backend/alembic` - no DB schema change.
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
pytest -q app/tests/unit/test_seed_validation.py
pytest -q app/tests/unit/test_backend_noop_tests.py
pytest --collect-only -q --ignore=.tmp-pytest
pytest -q
rg -n "assert True|pass$" app/tests tests -g test_*.py
```

Story validation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/replace-seed-validation-facade-test/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/replace-seed-validation-facade-test/00-story.md
```

## 21. Regression Risks

- Risk: la regle produit est supprimee par erreur.
  - Guardrail: decision obligatoire avant deletion.
- Risk: la garde no-op signale des `pass` legitimes dans helpers.
  - Guardrail: scope limite aux fonctions de tests collectees et skip explicite autorise avec raison.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respecter l'activation du venv avant toute commande Python.
- Ne pas creer de `requirements.txt`.

## 23. References

- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md` - preuve E-006.
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md` - finding F-006.
- `_condamad/audits/backend-tests/2026-04-28-1600/03-story-candidates.md` - candidat SC-006.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
- `backend/app/tests/unit/test_seed_validation.py` - test facade actuel.















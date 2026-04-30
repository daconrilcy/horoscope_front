# Story guard-backend-pytest-test-roots: Document and enforce backend pytest test roots

Status: ready-for-dev

## 1. Objective

Rendre explicite la topologie canonique des tests backend.
La configuration `backend/pyproject.toml`, le registre de topologie et la garde doivent decrire le meme ensemble de racines.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- Reason for change: F-102 signale que la topologie reste partagee entre `app/tests` et `tests/*` sans registre canonique explicite.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend tests topology
- In scope:
  - Documenter les racines pytest backend configurees.
  - Comparer les fichiers `test_*.py` et `*_test.py` aux racines autorisees.
  - Ajouter une garde qui echoue si une nouvelle racine de tests apparait hors registre.
  - Conserver la collecte standard depuis `backend`.
- Out of scope:
  - Migrer les tests DB.
  - Classifier les tests ops qualite.
  - Modifier les assertions metier des tests.
- Explicit non-goals:
  - Ne pas ajouter de dossier racine sous `backend/`.
  - Ne pas retirer `backend/tests/*` sans decision utilisateur.
  - Ne pas affaiblir `RG-010`.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: test-guard-hardening
- Archetype reason: la story durcit une garde d'architecture sur les racines de tests backend.
- Behavior change allowed: no
- Behavior change constraints:
  - La collecte pytest existante doit rester stable.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une racine detectee est intentionnelle mais absente du registre canonique.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La source observable est la configuration pytest chargee depuis `backend/pyproject.toml`. |
| Baseline Snapshot | yes | L'inventaire des racines et fichiers de tests doit etre capture avant/apres. |
| Ownership Routing | yes | Chaque racine doit avoir un owner canonique documente. |
| Allowlist Exception | yes | Toute racine speciale doit etre exacte et justifiee. |
| Contract Shape | no | Aucun contrat API ou DTO n'est modifie. |
| Batch Migration | no | La story durcit une garde unique sans migration multi-surface. |
| Reintroduction Guard | yes | Une garde doit echouer si une racine cachee reapparait. |
| Persistent Evidence | yes | Le registre de topologie doit etre persiste. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - loaded config from `backend/pyproject.toml` and AST guard coverage in `backend/app/tests/unit/test_backend_test_topology.py`.
- Secondary evidence:
  - Inventaire de fichiers via `rg --files backend -g "test_*.py" -g "*_test.py"`.
- Static scans alone are not sufficient for this story because:
  - la regle doit comparer les fichiers reels aux `testpaths` effectifs de pytest.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-before.md`
- Comparison after implementation:
  - `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-after.md`
- Expected invariant:
  - Tous les tests backend restent sous les racines documentees et collectees.
- Allowed differences:
  - Ajout du registre de topologie ou correction de garde sans deplacement de test.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| App backend tests | `backend/app/tests` | `backend/app/**/tests` hors exception documentee |
| Shared backend suites | `backend/tests/evaluation`, `backend/tests/integration`, `backend/tests/llm_orchestration`, `backend/tests/unit` | Racine cachee non collectee |
| Topology registry | `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md` | Commentaire implicite dans audit |
| Topology guard | `backend/app/tests/unit/test_backend_test_topology.py` | Scan manuel uniquement |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/domain/llm/prompting/tests` | Package local tests | Racine non standard existante. | Permanent while exact path is guarded. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Topology registry | `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md` | Documenter les racines pytest standard et leurs owners. |
| Baseline inventory | `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-before.md` | Capturer les fichiers de tests avant garde. |
| After inventory | `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-after.md` | Prouver que la garde couvre tous les fichiers. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- pytest `testpaths` loaded from `backend/pyproject.toml`
- filesystem inventory of backend test files
- topology registry markdown

Required forbidden examples:

- `backend/app/**/tests/test_*.py` outside `backend/app/tests`
- any `backend/**/test_*.py` outside documented roots
- a pytest root present in `pyproject.toml` but absent from topology registry

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_test_topology.py` checks hidden test roots.

## 5. Current State Evidence

- Evidence 1: `backend/pyproject.toml` - `testpaths` liste `app/tests`, `tests/evaluation`, `tests/integration`, `tests/llm_orchestration` et `tests/unit`.
- Evidence 2: `backend/app/tests/unit/test_backend_test_topology.py` - une garde compare deja une documentation de topologie a `pyproject.toml`.
- Evidence 3: `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md` - F-102 qualifie l'ownership de topologie comme partiel.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Le registre de topologie liste toutes les racines pytest standard.
- La garde compare registre, configuration pytest et inventaire fichier.
- Toute nouvelle racine non collectee echoue en test.

## 6b. Post-implementation Follow-up

- La limitation de validation signalee pendant cette story concernait un faux negatif
  wall-clock dans `backend/app/tests/unit/test_transit_performance.py`, hors domaine
  de la topologie pytest.
- Cette limitation a ete traitee par la story
  `_condamad/stories/stabilize-transit-performance-benchmark/00-story.md`.
- Preuve de resolution:
  `_condamad/stories/stabilize-transit-performance-benchmark/generated/10-final-evidence.md`
  indique que `pytest -q` passe avec `3479 passed, 12 skipped`.
- Le statut de cette story de topologie ne depend donc plus de la fluctuation
  `test_v3_layers_performance_benchmark` observee initialement.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-010` - la story touche directement la topologie des tests backend.
  - `RG-013` - les racines scannees par la garde d'import croise dependent de cette topologie.
- Non-applicable invariants:
  - `RG-011` - aucun changement du harnais DB n'est requis.
  - `RG-014` - aucun changement du contenu des tests no-op n'est requis.
- Required regression evidence:
  - `pytest -q app/tests/unit/test_backend_test_topology.py`
  - `pytest --collect-only -q --ignore=.tmp-pytest`
- Allowed differences:
  - Ajout d'un artefact de topologie et durcissement de garde.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Pytest roots are documented. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_backend_test_topology.py`. |
| AC2 | Hidden backend test roots fail the guard. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_backend_test_topology.py`. |
| AC3 | Standard collection remains stable. | Evidence profile: `runtime_openapi_contract`; `pytest --collect-only -q --ignore=.tmp-pytest`. |
| AC4 | Topology evidence is persisted. | Evidence profile: `baseline_before_after_diff`; `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-after.md`. |

## 8. Implementation Tasks

- [x] Task 1 - Persist the topology registry (AC: AC1)
- [x] Task 2 - Capture the backend test file baseline (AC: AC4)
- [x] Task 3 - Harden the topology guard against hidden roots (AC: AC2)
- [x] Task 4 - Prove pytest collection still uses the intended roots (AC: AC3)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/pyproject.toml` as the source of configured pytest roots.
  - `backend/app/tests/unit/test_backend_test_topology.py` as the guard owner.
- Do not recreate:
  - A second topology parser in another test file.
  - A duplicate topology markdown under another story folder.
- Shared abstraction allowed only if:
  - Multiple topology guards reuse the same parser.

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

- `backend/app/**/tests/test_*.py` outside `backend/app/tests`
- `backend/tests` subroot absent from `backend/pyproject.toml`
- topology documentation that diverges from pytest `testpaths`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Pytest configured roots | `backend/pyproject.toml` | Untracked CLI-only root |
| Backend test topology registry | `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md` | Audit prose only |
| Topology guard | `backend/app/tests/unit/test_backend_test_topology.py` | Manual checklist |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/pyproject.toml`
- `backend/app/tests/unit/test_backend_test_topology.py`

## 19. Expected Files to Modify

Likely files:

- `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md` - canonical topology registry.
- `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-before.md` - baseline inventory.
- `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-after.md` - after inventory.

Likely tests:

- `backend/app/tests/unit/test_backend_test_topology.py` - guard comparing registry, pyproject and files.

Files not expected to change:

- `backend/app/tests/conftest.py` - DB harness belongs to SC-101.
- `frontend/src` - no frontend change.
- `requirements.txt` - must not be created.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_backend_test_topology.py
pytest --collect-only -q --ignore=.tmp-pytest
rg --files . -g "test_*.py" -g "*_test.py"
```

## 22. Regression Risks

- Risk: une racine legitime est bloquee faute de registre.
  - Guardrail: stop condition avec decision utilisateur.
- Risk: la garde scanne un dossier cache temporaire.
  - Guardrail: ignorer explicitement `.tmp-pytest`, `.pytest_cache` et `__pycache__`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respecter l'activation du venv avant toute commande Python.
- Ne pas creer de `requirements.txt`.

## 24. References

- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md` - finding F-102.
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md` - candidat SC-102.
- `_condamad/stories/regression-guardrails.md` - invariant RG-010.
- `backend/app/tests/unit/test_backend_test_topology.py` - garde existante.
- `_condamad/stories/stabilize-transit-performance-benchmark/generated/10-final-evidence.md`
  - levee de la limitation full-suite wall-clock observee pendant la validation de cette story.

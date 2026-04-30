# Story classify-backend-ops-quality-tests: Classify backend ops and quality checks

Status: ready-for-dev

## 1. Objective

Classer les tests backend docs, scripts, secrets, securite et operations dans une ownership persistante.
La story doit produire une decision explicite: pytest backend, suite qualite, ou job separe.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- Reason for change: F-104 signale que les tests docs/scripts/ops restent dans pytest backend sans decision d'ownership.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend quality and ops test ownership
- In scope:
  - Inventorier les tests docs, scripts, secrets, securite et ops collectes par pytest backend.
  - Mesurer le cout d'execution cible et les dependances OS.
  - Persister une decision d'ownership par groupe.
  - Adapter les commandes de validation documentees si la decision change le perimetre.
- Out of scope:
  - Modifier la logique des scripts ops.
  - Reparer les tests fonctionnels des endpoints ops.
  - Refondre la CI complete sans decision documentee.
- Explicit non-goals:
  - Ne pas basculer silencieusement des tests hors de la suite backend.
  - Ne pas creer de marqueur pytest sans documentation de commande.
  - Ne pas affaiblir `RG-010`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: registry-catalog-refactor
- Archetype reason: la story cree un registre d'ownership pour classifier des suites existantes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les tests restent collectables ou une commande de suite qualite prend explicitement la couverture.
  - Toute separation CI doit etre documentee avant modification de configuration.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: l'ownership choisi change la commande backend standard.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La collecte pytest et les marqueurs effectifs doivent prouver la decision. |
| Baseline Snapshot | yes | L'inventaire des tests ops qualite doit etre capture avant/apres. |
| Ownership Routing | yes | Chaque groupe doit etre route vers un owner de suite. |
| Allowlist Exception | yes | Les exceptions OS ou CI doivent etre exactes. |
| Contract Shape | no | Aucun contrat API ou DTO n'est modifie. |
| Batch Migration | yes | La classification se fait par groupes docs, scripts, secrets, securite et ops. |
| Reintroduction Guard | yes | Une garde doit empecher les nouveaux tests qualite sans owner. |
| Persistent Evidence | yes | Le registre d'ownership et les mesures doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - loaded config pytest avec marqueurs effectifs et commandes ciblees par groupe.
- Secondary evidence:
  - Inventaire `rg --files backend -g "test_*.py"` filtre par `docs`, `scripts`, `secret`, `security` et `ops`.
- Static scans alone are not sufficient for this story because:
  - la decision doit rester executable par pytest ou par une commande qualite documentee.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-tests-before.md`
- Comparison after implementation:
  - `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-tests-after.md`
- Expected invariant:
  - Aucun test qualite ou ops n'existe sans owner et commande de validation.
- Allowed differences:
  - Ajout de marqueurs pytest, registre d'ownership ou documentation de commande.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Docs validation test | Backend quality suite registry | Pytest backend implicite sans owner |
| Script validation test | Backend quality suite registry or ops job | Test cache non documente |
| Secret or security check | Security quality suite registry | Skip silencieux |
| Ops endpoint test | Backend integration suite | Job qualite sans preuve API |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md` | OS or subprocess | PowerShell. | Permanent with exact command. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Docs | `test_natal_pro_docs.py` | Ownership row | Docs tests | `pytest -q app/tests/unit/test_natal_pro_docs.py` | Command named | Owner unknown. |
| Scripts | `test_*_scripts.py` | Quality or ops row | Script tests | `pytest -q app/tests/integration/test_pipeline_scripts.py` | Command named | CI job missing. |
| Secrets | `test_secret*`, `test_security*` | Security row | Secret tests | `pytest -q app/tests/integration/test_secrets_scan_script.py` | OS row | External secret needed. |
| Ops | `test_ops_*` | Integration or ops row | Ops tests | `pytest -q app/tests/integration/test_ops_monitoring_api.py` | Owner explicit | User decision needed. |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline inventory | `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-tests-before.md` | Capturer les tests concernes. |
| Ownership registry | `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md` | Persister owner, commande et dependances. |
| After inventory | `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-tests-after.md` | Prouver qu'aucun test concerne n'est sans owner. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- filesystem inventory of backend tests
- ownership registry rows
- pytest markers or commands

Required forbidden examples:

- `test_*scripts*.py` without ownership row
- `test_secret*.py` without ownership row
- `test_security*.py` without ownership row
- `test_ops_*.py` without ownership row or backend integration decision

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` checks registry coverage.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md` - F-104 decrit l'absence de decision d'ownership.
- Evidence 2: `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md` - SC-104 liste docs, scripts, secrets, securite et ops.
- Evidence 3: `backend/pyproject.toml` - les racines pytest collectent actuellement ces tests avec la suite backend.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Chaque test docs, scripts, secrets, securite ou ops possede un owner documente.
- Les commandes backend et qualite sont explicites.
- Les dependances OS ou subprocess sont visibles.
- Un guard empeche les nouveaux tests qualite sans classification.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-010` - la story peut modifier la topologie ou la collecte effective.
  - `RG-014` - les tests reclasses ne doivent pas devenir des no-op.
- Non-applicable invariants:
  - `RG-011` - aucun harnais DB n'est migre.
  - `RG-013` - aucun helper cross-test n'est deplace.
- Required regression evidence:
  - `pytest --collect-only -q --ignore=.tmp-pytest`
  - garde d'ownership qualite.
- Allowed differences:
  - Marqueurs, registre et documentation de commandes.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Classified test inventory is persisted. | Evidence profile: `baseline_before_after_diff`; `pytest --collect-only -q --ignore=.tmp-pytest`. |
| AC2 | Every classified test has one owner. | Evidence profile: `allowlist_register_validated`; `pytest -q app/tests/unit/test_backend_quality_test_ownership.py`. |
| AC3 | Pytest collection impact is explicit. | Evidence profile: `runtime_openapi_contract`; `pytest --collect-only -q --ignore=.tmp-pytest`. |
| AC4 | User decision blocks backend scope change. | Evidence profile: `external_usage_blocker`; `pytest --collect-only -q --ignore=.tmp-pytest`. |

## 8. Implementation Tasks

- [ ] Task 1 - Persist the current inventory (AC: AC1)
- [ ] Task 2 - Create the ownership registry (AC: AC2)
- [ ] Task 3 - Add or update the ownership guard (AC: AC2)
- [ ] Task 4 - Validate collection and record any user decision (AC: AC3, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/pyproject.toml` for current pytest roots.
  - Existing pytest markers when they already match a suite role.
- Do not recreate:
  - A second registry for the same tests.
  - A hidden CI command not documented in the ownership registry.
- Shared abstraction allowed only if:
  - Multiple guards need the same registry parser.

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

- unowned `test_*scripts*.py`
- unowned `test_secret*.py`
- unowned `test_security*.py`
- unowned `test_ops_*.py`
- pytest marker without documented command

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Quality test ownership | `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md` | Implicit pytest collection |
| Quality ownership guard | `backend/app/tests/unit/test_backend_quality_test_ownership.py` | Manual inventory |
| Pytest backend roots | `backend/pyproject.toml` | CI-only hidden root |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

If a decision changes the standard backend pytest command, the dev agent must stop.
Approval must be recorded in `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/pyproject.toml`
- `backend/app/tests/integration/test_pipeline_scripts.py`
- `backend/app/tests/integration/test_secrets_scan_script.py`
- `backend/app/tests/integration/test_security_verification_script.py`

## 19. Expected Files to Modify

Likely files:

- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md` - owner registry.
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-tests-before.md` - baseline.
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-tests-after.md` - after evidence.
- `backend/pyproject.toml` - only if markers are added with documented commands.

Likely tests:

- `backend/app/tests/unit/test_backend_quality_test_ownership.py` - registry coverage guard.

Files not expected to change:

- `backend/app/api` - no API behavior change.
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
pytest -q app/tests/unit/test_backend_quality_test_ownership.py
pytest --collect-only -q --ignore=.tmp-pytest
pytest -q app/tests/integration/test_pipeline_scripts.py app/tests/integration/test_secrets_scan_script.py app/tests/integration/test_security_verification_script.py
rg --files . -g "test_*.py" | rg "(docs|scripts|ops|secret|security)"
```

## 22. Regression Risks

- Risk: un test critique bascule hors de la suite backend sans commande equivalente.
  - Guardrail: decision utilisateur obligatoire avant retrait.
- Risk: un marqueur pytest cree une deuxieme commande non documentee.
  - Guardrail: registre d'ownership avec commande exacte.

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

- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md` - finding F-104.
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md` - candidat SC-104.
- `_condamad/stories/regression-guardrails.md` - invariants RG-010 et RG-014.
- `backend/pyproject.toml` - racines pytest actuelles.

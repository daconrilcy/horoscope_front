# Story CS-091 centraliser-contrats-hooks-api-admin-pages: Centraliser les contrats et hooks API admin consommes par les pages

Status: ready-to-dev

## 1. Objective

Creer un owner canonique pour les contrats, hooks, query keys, builders d'URL et parsing d'erreur des API admin.
Migrer un cluster coherent `dashboard/logs/users`.
Les pages ne doivent plus posseder directement `apiFetch` pour ce cluster.
Aucun legacy ne doit rester et aucune AC ne peut passer avec limitation.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md#SC-002`
- Reason for change: `F-002` montre 20 appels directs `apiFetch` et des contrats admin dupliques dans les pages.

## 3. Domain Boundary

- Domain: `frontend-react-pages/admin-api`
- In scope:
  - Choisir l'owner canonique `frontend/src/api/admin*.ts` pour ce lot.
  - Migrer `AdminDashboardPage`, `AdminLogsPage`, `AdminUsersPage` et `AdminUserDetailPage` si leurs appels appartiennent au cluster choisi.
  - Centraliser parsing de reponse, erreurs et query keys du cluster.
- Out of scope:
  - Migration des pages admin hors cluster.
  - Changement backend ou schema HTTP.
  - Refonte UI des pages admin.
- Explicit non-goals:
  - Ne pas creer d'API feature concurrente pour le meme cluster.
  - Ne pas garder `apiFetch` page-local pour les endpoints migres.
  - Ne pas accepter de `PASS with limitation`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: service-boundary-refactor
- Archetype reason: la story deplace la responsabilite API depuis les pages vers un service/client frontend canonique.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les endpoints, payloads et messages utilisateur existants restent equivalentes.
  - Les erreurs deviennent uniformes seulement pour le cluster migre.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le cluster ne peut pas migrer sans double implementation active ou fallback.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests API/page frontend prouvent le comportement runtime du cluster. |
| Baseline Snapshot | yes | Inventaire before/after des `apiFetch` directs requis. |
| Ownership Routing | yes | Les pages doivent router vers un owner API unique. |
| Allowlist Exception | no | Aucune exception `apiFetch` n'est autorisee dans le cluster migre. |
| Contract Shape | no | Le contrat HTTP ne change pas, il est seulement centralise. |
| Batch Migration | no | Un seul cluster coherent est migre. |
| Reintroduction Guard | yes | Les appels directs ne doivent pas revenir dans les pages migrees. |
| Persistent Evidence | yes | L'audit before/after et l'evidence finale doivent rester consultables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard or Vitest guard for direct page API ownership when implemented.
  - `frontend/src/tests/AdminDashboardPage.test.tsx`
  - `frontend/src/tests/AdminLogsPage.test.tsx`
  - `frontend/src/tests/AdminUserDetailPage.test.tsx`
- Secondary evidence:
  - scans cibles `apiFetch(` sur les pages migrees.
- Static scans alone are not sufficient because:
  - les pages admin migrees doivent rester couvertes par Vitest.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-091-centraliser-contrats-hooks-api-admin-pages/admin-api-before.md`.
- Comparison after implementation: `_condamad/stories/CS-091-centraliser-contrats-hooks-api-admin-pages/admin-api-after.md`.
- Expected invariant: zero `apiFetch(` direct dans les pages migrees du cluster.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin API cluster dashboard/logs/users | `frontend/src/api/admin*.ts` modules exacts | pages React |
| Query keys admin migrees | meme module API ou hook canonique | constantes page-locales dupliquees |
| Parsing erreur admin | helper API canonique existant ou module admin API | `catch` page-local divergent |

## 4e. Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: aucune exception n'est autorisee pour les pages du cluster migre.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is changed semantically.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: la migration est bornee a un cluster admin unique.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before admin API audit | `_condamad/stories/CS-091-centraliser-contrats-hooks-api-admin-pages/admin-api-before.md` | Capturer appels directs et contrats locaux. |
| After admin API audit | `admin-api-after.md` | Prouver owner API canonique et absence d'appels directs migres. |
| Final validation | `_condamad/stories/CS-091-centraliser-contrats-hooks-api-admin-pages/generated/10-final-evidence.md` | Persister commandes sans limitation. |

## 4i. Reintroduction Guard

- The implementation must add or update an architecture guard that fails if the forbidden surface is reintroduced.
- Architecture guard against reintroduction: un guard exact doit empecher `apiFetch(` dans les pages admin migrees.
- Deterministic source: scan `rg -n "apiFetch\\(" src/pages/admin`.
- Required forbidden examples: `apiFetch(` dans les fichiers migres, query key dupliquee, builder URL page-local pour endpoint migre.
- Guard evidence: `npm run test -- AdminDashboardPage AdminLogsPage AdminUserDetailPage AdminUsersPage admin`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md#F-002` - ownership API admin duplique dans les pages.
- Evidence 2: `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md#E-007` - 20 appels directs `apiFetch` dans les pages admin.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants frontend consultes avant cadrage.

## 6. Target State

- Le cluster migre consomme uniquement des modules API admin canoniques.
- Les pages ne reconstruisent plus endpoints, query keys ou erreurs pour ce cluster.
- Les tests prouvent comportement page et absence de legacy.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-049` - aucun alias ou surface legacy frontend ne doit etre cree.
  - `RG-050` - les guards frontend restent executables.
  - `RG-054` - aucune route admin legacy ne doit revenir.
- Non-applicable invariants:
  - `RG-044` - aucun token CSS n'est modifie.
  - `RG-047` - aucun style inline attendu.
- Required regression evidence:
  - `npm run test -- AdminDashboardPage AdminLogsPage AdminUserDetailPage AdminUsersPage admin`
  - `npm run lint`
  - scan `apiFetch(`.
- Allowed differences:
  - centralisation interne des appels API uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le cluster est inventorie. | Evidence profile: `baseline_before_after_diff`; artifact `admin-api-before.md`; command `rg -n "apiFetch\\(" src/pages/admin`. |
| AC2 | Le cluster utilise un owner API canonique. | Evidence profile: `ownership_routing`; test `npm run test -- frontend/src/tests/AdminDashboardPage.test.tsx`. |
| AC3 | `apiFetch(` quitte les pages migrees. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "apiFetch\\(" src/pages/admin`; test `npm run test -- AdminLogsPage`. |
| AC4 | Le runtime page du cluster reste couvert. | Evidence profile: `runtime_behavior`; `npm run test -- frontend/src/tests/AdminUserDetailPage.test.tsx`. |
| AC5 | Aucun legacy ne reste. | Evidence profile: `persistent_evidence`; `rg -n "PASS with limitation|legacy|fallback" generated/10-final-evidence.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'inventaire before des appels admin API du cluster. (AC: AC1)
- [ ] Task 2 - Creer ou completer les modules API admin canoniques. (AC: AC2)
- [ ] Task 3 - Migrer les pages du cluster vers les hooks/clients canoniques. (AC: AC2, AC3)
- [ ] Task 4 - Adapter les tests API/page sans encoder de legacy. (AC: AC4)
- [ ] Task 5 - Capturer l'after et les scans no-legacy. (AC: AC3, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/api/apiClient.ts` et helpers API existants.
- Reuse les tests admin existants au lieu de creer une suite parallele.
- Do not recreate un second client HTTP ou un parseur d'erreur concurrent.

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
- `apiFetch(` dans les pages migrees.
- builders URL dupliques pour endpoints migres.
- `PASS with limitation` dans les preuves.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Admin API calls | `frontend/src/api/admin*.ts` | direct `apiFetch` page-local |
| Admin page rendering | `frontend/src/pages/admin/*.tsx` | contrat HTTP local |
| Admin API tests | `frontend/src/tests/*admin*Api.test.ts` or page tests | manual-only verification |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md`
- `frontend/src/api/apiClient.ts`
- `frontend/src/pages/admin/AdminDashboardPage.tsx`
- `frontend/src/pages/admin/AdminLogsPage.tsx`
- `frontend/src/pages/admin/AdminUsersPage.tsx`
- `frontend/src/pages/admin/AdminUserDetailPage.tsx`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/api/adminDashboard.ts` - canonicaliser appels dashboard si absent.
- `frontend/src/api/adminLogs.ts` - canonicaliser logs si absent.
- `frontend/src/api/adminUsers.ts` - canonicaliser users si absent.
- `frontend/src/pages/admin/AdminDashboardPage.tsx` - consommer owner API.
- `frontend/src/pages/admin/AdminLogsPage.tsx` - consommer owner API.
- `frontend/src/pages/admin/AdminUsersPage.tsx` - consommer owner API.
- `frontend/src/pages/admin/AdminUserDetailPage.tsx` - consommer owner API.

Likely tests:
- `frontend/src/tests/AdminDashboardPage.test.tsx`
- `frontend/src/tests/AdminLogsPage.test.tsx`
- `frontend/src/tests/AdminUserDetailPage.test.tsx`
- `frontend/src/tests/adminPromptsApi.test.ts` or a focused admin API test for the migrated cluster.

Files not expected to change:
- `frontend/package.json` - aucune dependance.
- `backend/app/main.py` - aucun backend.
- `frontend/src/app/routes.tsx` - aucune route.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- AdminDashboardPage AdminLogsPage AdminUserDetailPage AdminUsersPage admin
npm run lint
rg -n "apiFetch\\(" src/pages/admin/AdminDashboardPage.tsx src/pages/admin/AdminLogsPage.tsx src/pages/admin/AdminUsersPage.tsx src/pages/admin/AdminUserDetailPage.tsx
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-091-centraliser-contrats-hooks-api-admin-pages/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: centralisation modifie silencieusement les erreurs admin.
  - Guardrail: tests pages et API du cluster.
- Risk: un appel direct reste en page.
  - Guardrail: AC3 scan exact.
- Risk: deux clients API admin coexistent.
  - Guardrail: ownership routing.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not create compatibility shims, aliases, fallbacks, wrappers or re-exports.
- No legacy may remain in the implemented cluster.
- No AC may be accepted as `PASS with limitation`.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md#SC-002`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md#F-002`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/stories/regression-guardrails.md`

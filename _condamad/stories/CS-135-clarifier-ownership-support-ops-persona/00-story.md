# Story CS-135 clarifier-ownership-support-ops-persona: Clarifier ownership support et ops persona

Status: ready-to-dev

## 1. Objective

Faire de `frontend/src/api/opsPersona.ts` l'owner unique des hooks ops persona et eviter que `frontend/src/api/support.ts` expose une composition transversale.
La story doit aussi classer le contrat frontend du endpoint `/v1/support/users/context?email={email}` avant toute modification de commentaire ou d'appel.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md#SC-005`
- Reason for change: l'audit `frontend-api` signale `F-005`, `support.ts` melange ownership support et ops persona.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/api`
- In scope:
  - Classer le role frontend de `/v1/support/users/context?email={email}`.
  - Faire importer le panneau support depuis l'owner ops persona canonique ou une composition feature explicite.
  - Eliminer l'exposition ops persona depuis `support.ts` si la classification confirme la duplication.
- Out of scope:
  - Verifier le contrat runtime backend du endpoint support, differe par l'audit.
  - Changer les autorisations ou routes backend.
  - Reorganiser toute la facade `@api`, couvert par `CS-136`.
- Explicit non-goals:
  - Ne pas modifier les invariants `RG-053`, `RG-057`, `RG-064` et `RG-069`.
  - Ne pas creer un wrapper support autour de `opsPersona.ts`.
  - Ne pas supprimer un export public sans classification et consommateurs remplaces.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: l'exposition ops persona via support est une facade de domaine non canonique a classer puis fermer.
- Behavior change allowed: no
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: le endpoint support search-by-email est produit comme owner canonique par evidence backend ou produit.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | le guard `api-architecture` devient source executable de l'ownership frontend. |
| Baseline Snapshot | yes | consommateurs et exports doivent etre inventories avant/apres. |
| Ownership Routing | yes | support et ops persona doivent avoir des owners separes. |
| Allowlist Exception | no | aucune exception support-vers-ops ne doit rester sans decision utilisateur. |
| Contract Shape | no | les payloads ne changent pas. |
| Batch Migration | no | la story porte sur une facade exacte. |
| Reintroduction Guard | yes | la facade ops persona depuis support ne doit pas revenir. |
| Persistent Evidence | yes | classification endpoint/export doit persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard `api-architecture` sous `frontend/src/tests`.
- Secondary evidence:
  - tests `SupportOpsPanel` et `opsPersona`.
- Static scans alone are not sufficient:
  - la classification frontend doit etre verifiee par architecture guard, pas seulement par `rg`.
  - AST guard evidence: `npm run test -- api-architecture`.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-135-clarifier-ownership-support-ops-persona/support-ops-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-135-clarifier-ownership-support-ops-persona/support-ops-after.md`
- Expected invariant:
  - aucun consommateur runtime ne passe par `support.ts` pour une responsabilite ops persona.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| API support utilisateur | `frontend/src/api/support.ts` | `opsPersona.ts` |
| API ops persona | `frontend/src/api/opsPersona.ts` | `support.ts` |
| Composition panneau support | feature support ou import direct owner canonique | facade API croisee |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: aucune exception cross-domain n'est attendue apres classification.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: aucun champ ou statut API n'est modifie.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: une facade cross-domain exacte est ciblee.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| baseline | `_condamad/stories/CS-135-clarifier-ownership-support-ops-persona/support-ops-before.md` | capturer exports et consommateurs initiaux. |
| endpoint classification | `support-endpoint-classification.md` | classer `/v1/support/users/context?email={email}`. |
| after | `_condamad/stories/CS-135-clarifier-ownership-support-ops-persona/support-ops-after.md` | prouver la convergence finale. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard against reintroduced ops persona ownership from `support.ts`.

Deterministic source: forbidden symbols in `frontend/src/api/support.ts`.

Required guard evidence:

```powershell
cd frontend
npm run test -- api-architecture SupportOpsPanel opsPersona
rg -n "useOpsRollbackPersona|opsPersona" src/api/support.ts src/features/support -g "*.ts" -g "*.tsx"
```

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md` - `F-005` signale le melange support et ops persona.
- Evidence 2: `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md` - `SC-005` liste `support.ts`, `SupportOpsPanel.tsx` et tests associes.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- `support.ts` expose uniquement des responsabilites support classees.
- `opsPersona.ts` reste l'owner canonique des hooks ops persona.
- `SupportOpsPanel.tsx` importe depuis l'owner correct ou une composition feature documentee.
- Le endpoint support search-by-email est classe dans un artefact persistant.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - les pages et panneaux ne doivent pas recevoir de logique API directe non classee.
  - `RG-069` - les composants partages ne deviennent pas owners support ou ops.
- Required regression evidence:
  - `npm run test -- api-architecture SupportOpsPanel opsPersona component-architecture page-architecture`
- Allowed differences:
  - chemins d'import internes uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les consommateurs support/ops sont inventories. | Evidence profile: `baseline_before_after_diff`; `npm run test -- api-architecture`. |
| AC2 | Le endpoint support search-by-email est classe. | Evidence profile: `allowlist_register_validated`; AST guard via `npm run test -- api-architecture`. |
| AC3 | `support.ts` ne re-exporte plus la responsabilite ops persona. | Evidence profile: `python_module_removed`; `npm run test -- api-architecture SupportOpsPanel`. |
| AC4 | Le panneau support importe depuis l'owner canonique. | Evidence profile: `ast_architecture_guard`; `npm run test -- SupportOpsPanel component-architecture`. |
| AC5 | La facade cross-domain ne peut pas revenir. | Evidence profile: `reintroduction_guard`; `rg -n "useOpsRollbackPersona|opsPersona" src/api/support.ts`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer baseline et classification (AC: AC1, AC2)
  - [ ] Ecrire `support-ops-before.md`.
  - [ ] Ecrire `support-endpoint-classification.md`.
- [ ] Task 2 - Corriger l'ownership support/ops (AC: AC3, AC4)
  - [ ] Adapter `SupportOpsPanel.tsx`.
  - [ ] Fermer l'exposition ops persona depuis `support.ts` si non canonique.
- [ ] Task 3 - Ajouter garde et preuve finale (AC: AC5)
  - [ ] Ajouter ou etendre `api-architecture`.
  - [ ] Ecrire `support-ops-after.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/api/opsPersona.ts` pour ops persona.
  - `frontend/src/api/support.ts` pour support uniquement.
  - tests existants support et ops.
- Do not recreate:
  - wrapper support pour hook ops.
  - hook ops persona duplique.
  - facade cross-domain cachee dans `@api`.
- Shared abstraction allowed only if:
  - elle vit dans une composition feature et ne devient pas un owner API concurrent.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- legacy imports
- fallback ownership routing
- duplicate active implementations
- silent fallback behavior

Specific forbidden symbols / paths:

- `useOpsRollbackPersona` exporte depuis `frontend/src/api/support.ts`
- import de `opsPersona` dans `support.ts`
- commentaire placeholder pour `/v1/support/users/context?email={email}` sans classification

## 11. Removal Classification Rules

Removal classification must use exactly these classes:

- `canonical-active`
- `external-active`
- `historical-facade`
- `dead`
- `needs-user-decision`

`support.ts` exposing ops persona must be classified before it is changed.

## 12. Removal Audit Format

Required audit table in `_condamad/stories/CS-135-clarifier-ownership-support-ops-persona/support-ops-before.md`:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Support API context | `frontend/src/api/support.ts` after endpoint classification | ops persona module |
| Ops persona API hooks | `frontend/src/api/opsPersona.ts` | support re-export |
| Support panel composition | `frontend/src/features/support/SupportOpsPanel.tsx` | API module cross-domain composition |

## 14. Delete-Only Rule

- Delete-only rule: active for items classified `historical-facade` or `dead`.
- Rule: closed items are deleted, not repointed.
- Forbidden routes: wrapper, alias, fallback, or re-export.

## 15. External Usage Blocker

- If a consumer outside `frontend/src` or an explicit public facade contract depends on `support.ts` exporting ops persona, stop and record `external-active`.
- An `external-active` surface must not be deleted without user decision.

## 16. Generated Contract Check

- Generated contract check: applicable as absence proof.
- Required generated evidence:
  - no generated client or OpenAPI artifact is changed by this frontend ownership cleanup.
  - `git diff --stat` must show no generated OpenAPI path changes.

## 17. Files to Inspect First

- `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md`
- `frontend/src/api/support.ts`
- `frontend/src/api/opsPersona.ts`
- `frontend/src/features/support/SupportOpsPanel.tsx`
- `frontend/package.json`

## 18. Expected Files to Modify

Likely files:

- `frontend/src/api/support.ts` - ownership cleanup.
- `frontend/src/features/support/SupportOpsPanel.tsx` - import owner correction.
- `frontend/src/tests/api-architecture-guards.test.ts` - guard support/ops.
- `_condamad/stories/CS-135-clarifier-ownership-support-ops-persona/support-ops-before.md` - baseline.
- `_condamad/stories/CS-135-clarifier-ownership-support-ops-persona/support-endpoint-classification.md` - classification.
- `_condamad/stories/CS-135-clarifier-ownership-support-ops-persona/support-ops-after.md` - preuve finale.

Likely tests:

- tests existants `SupportOpsPanel` et `opsPersona`.
- `frontend/src/tests/api-architecture-guards.test.ts`.

Files not expected to change:

- `backend/app/**` - verification backend differee.
- `frontend/src/components/**` - aucun composant partage.
- `frontend/src/pages/**` - aucun routage page.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- SupportOpsPanel opsPersona api-architecture component-architecture page-architecture
npm run lint
npm run typecheck
rg -n "useOpsRollbackPersona|opsPersona" src/api/support.ts src/features/support -g "*.ts" -g "*.tsx"
```

## 21. Regression Risks

- Risk: import support panel casse.
  - Guardrail: test `SupportOpsPanel`.
- Risk: endpoint support mal classe sans backend.
  - Guardrail: artefact `support-endpoint-classification.md` et blocker explicite.
- Risk: facade cross-domain recreee.
  - Guardrail: scan et guard `api-architecture`.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not invent backend contract evidence.
- Keep all Python commands behind `.\\.venv\\Scripts\\Activate.ps1`.

## 23. References

- `_condamad/audits/frontend-api/2026-05-10-1850/00-audit-report.md`
- `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md#F-005`
- `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md#SC-005`
- `_condamad/stories/regression-guardrails.md`

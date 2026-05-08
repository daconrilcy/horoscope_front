# Story CS-093 converger-barrels-pages-exports-stale: Converger les barrels de pages et les exports stale

Status: ready-to-dev

## 1. Objective

Supprimer les exports stale ou dupliques des barrels de pages React.
Les barrels doivent converger vers des exports canoniques exacts.
`PricingAdmin`, `MonitoringAdmin` et tout export duplique ne doivent pas rester disponibles comme legacy.
Aucune AC ne peut etre acceptee avec limitation.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md#SC-004`
- Reason for change: `F-004` montre que `frontend/src/pages/admin/index.ts` conserve des exports stale et dupliques.

## 3. Domain Boundary

- Domain: `frontend-react-pages/barrels`
- In scope:
  - Auditer les barrels `frontend/src/pages/admin/index.ts` et `frontend/src/pages/index.ts`.
  - Supprimer les exports stale, dupliques et facades historiques.
  - Migrer les imports internes qui consomment un export supprime vers les chemins canoniques.
- Out of scope:
  - Suppression de routes publiques.
  - Refonte UI admin.
  - Migration generale des features admin.
- Explicit non-goals:
  - Ne pas preserver un ancien import via re-export.
  - Ne pas ajouter un barrel concurrent.
  - Ne pas accepter de `PASS with limitation`.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story retire des facades d'import stale exposees par barrels.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les imports internes doivent utiliser les owners canoniques.
  - Les surfaces stale ne restent pas importables.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un import externe prouve dependance active a un export stale; la decision actuelle interdit tout legacy interne.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | TypeScript/lint prouvent les imports resolus. |
| Baseline Snapshot | yes | Inventaire before/after des exports requis. |
| Ownership Routing | yes | Chaque page exportee doit avoir un owner canonique. |
| Allowlist Exception | no | Aucune exception stale/duplicate n'est autorisee. |
| Contract Shape | no | Aucun contrat API n'est modifie. |
| Batch Migration | no | Suppression exacte de barrels stale. |
| Reintroduction Guard | yes | Les exports stale ne doivent pas revenir. |
| Persistent Evidence | yes | L'audit barrel doit rester consultable. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard or frontend route table guard for barrels when implemented.
  - TypeScript lint via `npm run lint`
  - tests router/admin utilisant les imports canoniques
- Secondary evidence:
  - scans des exports barrels.
- Static scans alone are not sufficient because:
  - TypeScript doit prouver que les consommateurs internes ont migre.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-093-converger-barrels-pages-exports-stale/page-barrels-before.md`.
- Comparison after implementation: `_condamad/stories/CS-093-converger-barrels-pages-exports-stale/page-barrels-after.md`.
- Expected invariant: aucun export stale ou duplique ne reste dans les barrels audites.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin page module | fichier page canonique exact | barrel stale ou duplicate |
| Public page export | import direct ou barrel exact documente | broad barrel ambigu |
| Tests de navigation | tests router/admin existants | tests encodant l'ancien barrel |

## 4e. Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: aucune exception d'export stale ou duplicate n'est autorisee.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, DTO, OpenAPI contract, generated client, or frontend type contract is affected.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: les surfaces sont supprimees par inventaire exact, pas par batch.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before barrel audit | `_condamad/stories/CS-093-converger-barrels-pages-exports-stale/page-barrels-before.md` | Lister exports stale/dupliques. |
| After barrel audit | `_condamad/stories/CS-093-converger-barrels-pages-exports-stale/page-barrels-after.md` | Prouver suppression et consumers migres. |
| Final validation | `_condamad/stories/CS-093-converger-barrels-pages-exports-stale/generated/10-final-evidence.md` | Persister commandes sans limitation. |

## 4i. Reintroduction Guard

- The implementation must add or update an architecture guard that fails if the forbidden surface is reintroduced.
- Architecture guard against reintroduction: test ou scan qui echoue si `PricingAdmin`, `MonitoringAdmin` ou un export duplicate est reintroduced par barrel.
- Deterministic source: forbidden symbols in `frontend/src/tests/ui-barrel.test.ts` and targeted `rg` scans.
- Required forbidden examples: `PricingAdmin`, `MonitoringAdmin`, duplicate `export`.
- Guard evidence: `npm run test -- router AdminPage AdminPromptsRouting ui-nav BottomNavPremium`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md#F-004` - barrels pages gardent anciens chemins.
- Evidence 2: `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md#E-008` - `pages/admin/index.ts` duplique et expose `PricingAdmin`/`MonitoringAdmin`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants frontend consultes avant cadrage.

## 6. Target State

- Les barrels audites n'exposent que les surfaces canoniques utiles.
- Les exports stale sont supprimes, pas repointes.
- Les validations prouvent absence de legacy et imports internes valides.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-049` - les surfaces legacy frontend doivent etre retirees.
  - `RG-050` - les guards frontend restent executables.
  - `RG-054` - les anciennes surfaces admin ne doivent pas revenir indirectement.
- Non-applicable invariants:
  - `RG-044` - pas de tokens CSS.
  - `RG-047` - pas de styles inline.
- Required regression evidence:
  - `npm run test -- router AdminPage AdminPromptsRouting ui-nav BottomNavPremium`
  - `npm run lint`
  - scans des exports interdits.
- Allowed differences:
  - les anciens imports stale ne sont plus supportes.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | L'audit before classe chaque export barrel. | Evidence profile: `baseline_before_after_diff`; artifact `page-barrels-before.md`; command `rg -n "export" src/pages`. |
| AC2 | Les exports stale internes sont supprimes. | Evidence profile: `removal_audit`; command `rg -n "PricingAdmin|MonitoringAdmin" src/pages`. |
| AC3 | Les consommateurs internes utilisent les imports canoniques. | Evidence profile: `ownership_routing`; `npm run lint`. |
| AC4 | Le runtime navigation reste couvert. | Evidence profile: `runtime_behavior`; `npm run test -- frontend/src/tests/router.test.tsx`. |
| AC5 | Aucun re-export legacy ne reste. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "PASS with limitation|legacy|fallback" generated/10-final-evidence.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'audit before des barrels. (AC: AC1)
- [ ] Task 2 - Supprimer exports stale/dupliques et migrer consumers internes. (AC: AC2, AC3)
- [ ] Task 3 - Ajouter ou renforcer le guard anti-retour. (AC: AC5)
- [ ] Task 4 - Executer tests navigation/router/admin et lint. (AC: AC3, AC4)
- [ ] Task 5 - Capturer l'after sans limitation. (AC: AC1, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse les chemins de pages canoniques existants.
- Do not create a second barrel to preserve old imports.
- Shared abstraction allowed only if elle remplace un barrel ambigu par un export exact documente.

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
- `PricingAdmin` exporte par barrel.
- `MonitoringAdmin` exporte par barrel.
- exports dupliques dans `frontend/src/pages/admin/index.ts`.
- `PASS with limitation`.

## 11. Removal Classification Rules

- `canonical-active`: export utilise par code interne canonique.
- `external-active`: export prouve consomme hors repo; bloque suppression sans decision.
- `historical-facade`: export qui preserve un ancien nom ou module.
- `dead`: export sans consommateur.
- `needs-user-decision`: ambiguite externe apres scans.

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete` | Must be deleted under the no-legacy decision. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:
- `_condamad/stories/CS-093-converger-barrels-pages-exports-stale/page-barrels-after.md`

Allowed decisions: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Admin page imports | exact page module path | stale admin barrel exports |
| Public page imports | exact page module or intentionally exact barrel | broad stale barrel |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.
Forbidden: wrapper, compatibility alias, deprecated export, soft-disable behavior, re-export.

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted without a user decision.
Implementation must stop and record exact external evidence and required user decision.
Without proof, the no-legacy decision requires deletion for internal stale surfaces.

## 17. Generated Contract Check

- OpenAPI path absence: no backend OpenAPI path may change for this frontend-only removal.
- Generated artifact absence: if a route manifest, schema, public contract or generated client exists, prove stale exports are absent.
- Required evidence: `npm run lint` and targeted scans for removed barrel exports.

## 18. Files to Inspect First

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md`
- `frontend/src/pages/admin/index.ts`
- `frontend/src/pages/index.ts`
- `frontend/src/app/routes.tsx`
- `frontend/src/tests/ui-barrel.test.ts`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/pages/admin/index.ts` - supprimer stale/duplicates.
- `frontend/src/pages/index.ts` - reduire ou classifier les broad exports detectes par audit.
- `frontend/src/tests/ui-barrel.test.ts` or `frontend/src/tests/page-architecture-guards.test.ts` - guard anti-retour.

Likely tests:
- `frontend/src/tests/router.test.tsx`
- `frontend/src/tests/AdminPage.test.tsx`
- `frontend/src/tests/AdminPromptsRouting.test.tsx`
- `frontend/src/tests/ui-nav.test.ts`
- `frontend/src/tests/BottomNavPremium.test.tsx`

Files not expected to change:
- `frontend/package.json` - aucune dependance.
- `backend/app/main.py` - aucun backend.
- `frontend/src/styles/design-tokens.css` - aucun style.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- router AdminPage AdminPromptsRouting ui-nav BottomNavPremium
npm run lint
rg -n "PricingAdmin|MonitoringAdmin" src/pages src/tests
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-093-converger-barrels-pages-exports-stale/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: import interne casse apres suppression de barrel.
  - Guardrail: `npm run lint`.
- Risk: ancienne surface conservee par re-export.
  - Guardrail: Delete-only rule et scans.
- Risk: dependance externe inconnue.
  - Guardrail: External Usage Blocker.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- No legacy may remain in the implemented cluster.
- No AC may be accepted as `PASS with limitation`.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md#SC-004`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md#F-004`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/stories/regression-guardrails.md`

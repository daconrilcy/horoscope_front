# Story CS-110 corriger-garder-validite-css-primitives-layout: Corriger et garder la validite CSS des primitives layout

Status: done

## 1. Objective

Corriger la declaration CSS invalide de `PageLayout.css` et ajouter une garde
deterministe pour que les CSS actives de `frontend/src/layouts/**` ne puissent
plus contenir une erreur de syntaxe comparable sans faire echouer la suite
frontend.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-layouts/2026-05-08-2026/03-story-candidates.md#SC-301`
- Reason for change: l'audit prouve que `PageLayout.css` contient
  `padding: var(--layout-page-padding));` alors que `npm run lint` et les tests
  existants restent verts.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-layouts`
- In scope:
  - Corriger `frontend/src/layouts/PageLayout.css`.
  - Ajouter ou etendre un test qui valide la syntaxe des CSS layout actives.
  - Conserver les variables CSS layout existantes.
  - Produire une preuve avant/apres pour le motif invalide.
- Out of scope:
  - Modifier la hierarchie des routes ou les owners de pages.
  - Migrer des tokens design-system hors layout.
  - Refactorer `PageLayout.tsx`, `TwoColumnLayout.tsx` ou les pages.
  - Changer les commandes npm ou ajouter une dependance.
- Explicit non-goals:
  - Ne pas affaiblir `RG-050` ou `RG-068`.
  - Ne pas creer de token de spacing duplique.
  - Ne pas ajouter de wildcard, de broad allowlist, de compatibility wrapper,
    de legacy path ou de fallback silencieux.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: test-guard-hardening
- Archetype reason: la correction est minime, mais le resultat attendu est une
  garde executable qui detecte les CSS layout invalides.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: restaurer le padding attendu de `PageLayout`.
  - Interdit: changer la structure de layout, les routes, ou les tokens
    semantiques existants.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: la correction exige un nouveau token global ou une
  nouvelle dependance de parsing CSS.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le guard de test doit analyser les CSS actives, pas seulement chercher un texte. |
| Baseline Snapshot | no | Le scan avant/apres suffit pour une declaration unique et ciblee. |
| Ownership Routing | no | Aucun transfert de responsabilite layout n'est prevu. |
| Allowlist Exception | yes | Les guards design-system existants reposent sur des registres exacts a ne pas elargir. |
| Contract Shape | no | Aucun contrat API, type public ou DTO n'est touche. |
| Batch Migration | no | Il n'y a pas de migration par lots. |
| Reintroduction Guard | yes | La garde doit echouer si une CSS layout active redevient invalide. |
| Persistent Evidence | yes | La preuve avant/apres du scan et du guard doit etre conservee dans le dossier CS-110. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard ou parser-based guard dans `frontend/src/tests/design-system-guards.test.ts`
    ou un nouveau fichier sous `frontend/src/tests/`.
- Secondary evidence:
  - Scan cible du motif invalide dans `frontend/src/layouts`.
- Static scans alone are not sufficient because:
  - Le motif actuel est connu, mais une autre declaration CSS invalide pourrait
    apparaitre sans contenir exactement la meme chaine.
- Command:
  - `npm run test -- design-system`

## 4c. Baseline / Before-After Rule

- Baseline / before-after rule: not applicable
- Reason: la story ne revendique pas une preservation large de comportement;
  elle corrige une declaration unique et ajoute une garde executable.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: les fichiers layout conservent leurs proprietaires actuels.

## 4e. Allowlist / Exception Register

Use existing frontend guard registries only; do not create a new broad register.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | layout CSS parse failures | Layout parse failures are not accepted. | Permanent rule: no layout CSS parse failure is allowed. |
| `frontend/src/tests/design-system-guards.test.ts` | layout CSS under `frontend/src/layouts` | Layout CSS must be validated. | Permanent guard for active layout CSS. |

Rules:

- no wildcard parse failure allowlist;
- no folder-wide bypass;
- no accepted parse failure for `PageLayout.css`.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, HTTP response, payload, generated client, export contract, DTO
  or frontend public type is changed.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: one CSS declaration and one guard surface are in scope.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Closure evidence | `_condamad/stories/CS-110-corriger-garder-validite-css-primitives-layout/layout-css-validity-after.md` | Record scans, guard command, and lint outcome. |

## 4i. Reintroduction Guard

The implementation must add or preserve a deterministic guard against invalid
layout CSS.

Deterministic guard sources:

- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/**/*.css`
- `frontend/src/tests/design-system-guards.test.ts` or a focused CSS syntax guard

Required forbidden examples:

- `padding: var(--layout-page-padding));`
- any active layout CSS declaration rejected by the selected parser or validator

Guard evidence:

- `npm run test -- design-system`
- `npm run test -- page-architecture layout`

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-layouts/2026-05-08-2026/02-finding-register.md#F-301`
- Closure proof required: before scan showing the malformed declaration, after
  scan showing absence, guard test proving layout CSS syntax validation, lint.
- Known residual in-domain work: none
- Deferred non-domain concerns: broader CSS quality tooling outside layout primitives.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/frontend-layouts/2026-05-08-2026/01-evidence-log.md` - E-005 and E-006 record the malformed `PageLayout.css` declaration.
- Evidence 2: `_condamad/audits/frontend-layouts/2026-05-08-2026/02-finding-register.md` - F-301 says lint and tests stay green despite invalid layout CSS.
- Evidence 3: `_condamad/audits/frontend-layouts/2026-05-08-2026/03-story-candidates.md` - SC-301 requires correction plus deterministic guard coverage.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - `RG-050` and `RG-068` were consulted before scope was finalized.

## 6. Target State

After implementation:

- `PageLayout.css` uses `padding: var(--layout-page-padding);`.
- Layout CSS files are covered by a deterministic syntax guard.
- Existing layout tokens are reused without duplication.
- Route hierarchy and page ownership remain unchanged.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-050` - design-system guards and allowlists must remain exact.
  - `RG-068` - layout hierarchy tests must keep protecting route-level owners.
- Non-applicable invariants:
  - `RG-047` - this story does not touch TSX inline styles.
  - `RG-064` - page architecture classifications are not modified.
- Required regression evidence:
  - `npm run test -- design-system`
  - `npm run test -- page-architecture layout`
  - targeted scan for the malformed padding pattern
- Allowed differences:
  - only the corrected CSS declaration and the added or extended guard.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `PageLayout.css` no longer contains malformed padding. | Evidence profile: `targeted_forbidden_symbol_scan`; command `rg -n "layout-page-padding" frontend/src/layouts`. |
| AC2 | Layout CSS syntax has a frontend guard. | Evidence profile: `ast_architecture_guard`; command `npm run test -- design-system`. |
| AC3 | Existing layout ownership tests still pass. | Evidence profile: `reintroduction_guard`; command `npm run test -- page-architecture layout`. |
| AC4 | Frontend lint remains green. | Evidence profile: `frontend_typecheck_no_orphan`; command `npm run lint`. |

## 8. Implementation Tasks

- [x] Task 1 - Capture the current CSS failure. (AC: AC1)
  - [x] Run the targeted `rg` scan and record the current hit in implementation evidence.

- [x] Task 2 - Correct the layout CSS declaration. (AC: AC1)
  - [x] Update only `frontend/src/layouts/PageLayout.css`.
  - [x] Reuse `--layout-page-padding`; do not introduce a duplicate spacing token.

- [x] Task 3 - Add deterministic layout CSS syntax coverage. (AC: AC2, AC3)
  - [x] Extend `design-system-guards.test.ts` or add a focused test under `frontend/src/tests/`.
  - [x] Ensure the guard covers `frontend/src/layouts/**/*.css`.

- [x] Task 4 - Validate and record closure. (AC: AC1, AC2, AC3, AC4)
  - [x] Run lint, targeted tests, and the negative scan.
  - [x] Record command outcomes in the implementation evidence.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css` and existing layout variables for spacing.
  - Existing design-system guard patterns in `frontend/src/tests/design-system-guards.test.ts`.
- Do not recreate:
  - a second layout token namespace;
  - a parallel design-system guard runner;
  - local fallback values for `--layout-page-padding`.
- Shared abstraction allowed only when:
  - the existing guard file cannot parse CSS cleanly without a small local helper.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `padding: var(--layout-page-padding));`
- layout CSS parse-failure bypass under `frontend/src/layouts`
- new fallback value for `--layout-page-padding`
- broad CSS syntax allowlist

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

- Canonical ownership: not applicable

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/audits/frontend-layouts/2026-05-08-2026/01-evidence-log.md`
- `_condamad/audits/frontend-layouts/2026-05-08-2026/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-2026/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/layouts/PageLayout.css` - correct the malformed padding declaration.
- `frontend/src/tests/design-system-guards.test.ts` - add or extend layout CSS syntax validation.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - proves invalid layout CSS fails.
- `frontend/src/tests/page-architecture-guards.test.ts` - remains passing for layout hierarchy.

Files not expected to change:

- `frontend/src/layouts/PageLayout.tsx` - no component behavior change.
- `frontend/src/app/routes.tsx` - no route hierarchy change.
- `frontend/package.json` - no dependency or script change.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- design-system
npm run test -- page-architecture layout
Pop-Location
rg -n "padding: var\\(--layout-page-padding\\)\\);" frontend/src/layouts
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-110-corriger-garder-validite-css-primitives-layout/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-110-corriger-garder-validite-css-primitives-layout/00-story.md
```

## 22. Regression Risks

- Risk: the fix removes the visible padding instead of correcting the token call.
  - Guardrail: AC1 requires the corrected token declaration, not deletion.
- Risk: the new guard only catches the exact old string.
  - Guardrail: AC2 requires parser-based or deterministic CSS syntax validation.
- Risk: design-system allowlists become broader.
  - Guardrail: `RG-050` and the allowlist rules forbid broad bypasses.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not change route ownership, page classifications, or layout component APIs.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-layouts/2026-05-08-2026/03-story-candidates.md#SC-301` - source story candidate.
- `_condamad/audits/frontend-layouts/2026-05-08-2026/02-finding-register.md#F-301` - source finding.
- `_condamad/audits/frontend-layouts/2026-05-08-2026/01-evidence-log.md#E-006` - malformed declaration evidence.
- `_condamad/stories/regression-guardrails.md` - shared guardrail registry.

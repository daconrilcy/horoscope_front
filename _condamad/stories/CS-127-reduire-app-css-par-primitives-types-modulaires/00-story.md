# Story CS-127 reduire-app-css-par-primitives-types-modulaires: Reduire App.css par primitives de type modulaires

Status: ready-to-dev

## 1. Objective

Reduire drastiquement `frontend/src/App.css` en refactorisant les classes et
tokens redondants vers des primitives CSS reutilisables classees par type.

`App.css` doit devenir un point d'import leger. Les styles extraits doivent
vivre dans des fichiers modulaires sous `frontend/src/styles/app/`.

## 2. Scope

In scope:

- `frontend/src/App.css`
- nouveaux fichiers modulaires CSS sous `frontend/src/styles/app/`
- consommateurs TSX exacts des classes App migrees, supprimees ou renommees
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- artefacts before/after dans ce dossier de story

Out of scope:

- backend, API, DB, auth, billing
- refonte visuelle produit
- migration des CSS page-scoped existants hors extraction directe depuis `App.css`
- decomposition React non necessaire au remplacement de `className`

## 2a. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-09, apres les audits App CSS de `2026-05-09-1145` et `2026-05-09-1753`
- Reason for change: `frontend/src/App.css` reste volumineux avec variables mecaniques, selecteurs dupliques et patterns identiques sous plusieurs noms.

## 2b. Domain Boundary

- Domain: frontend-app-css-standardization

In scope:

- `frontend/src/App.css`
- `frontend/src/styles/app/**`
- consommateurs TSX exacts des classes App migrees ou composees
- tests design-system, theme-token, fallback, inline-style, legacy-style et visual-smoke
- artefacts before/after dans ce dossier de story

Out of scope:

- backend, API, DB, auth, billing
- nouvelle dependance frontend
- refonte visuelle produit
- migration de CSS page-scoped non extrait depuis `App.css`

Explicit non-goals:

- ne pas ajouter de dossier backend
- ne pas creer de classe globale single-use hors primitive fondationnelle documentee
- ne pas affaiblir `RG-044` a `RG-050`, `RG-059`, `RG-061`, `RG-075`, `RG-076`, `RG-077`, `RG-078`
- ne pas conserver d'ancien selecteur comme alias de compatibilite

## 2c. Operation Contract

- Operation type: split
- Primary archetype: large-file-split
- Archetype reason: split a monolithic CSS file into approved type modules while preserving existing behavior.
- Behavior change allowed: constrained
- Behavior change constraints:
  - differences visuelles limitees aux approximations standardisees de radius, font-size, couleurs, borders, shadows, spacing et etats
  - aucun changement de route, donnees, texte metier ou interaction React
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une difference visuelle page-specific doit rester permanente ou si une classe CSS single-use doit rester globale.

## 2d. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Visual-smoke and build prove CSS still renders. |
| Baseline Snapshot | yes | The size and duplicate-body reduction must be measured before/after. |
| Ownership Routing | yes | Each style type routes to an approved module. |
| Allowlist Exception | yes | Exact single-use or variable exceptions only. |
| Contract Shape | no | Aucun contrat API, DTO, schema, route ou client genere n'est touche. |
| Batch Migration | yes | CSS is extracted by style-type batches. |
| Reintroduction Guard | yes | Guards must prevent App.css monolith regrowth. |
| Persistent Evidence | yes | Metrics, mapping, consumers and validation must be persisted. |

## 2e. Runtime Source of Truth

- Primary source of truth: AST guard `frontend/src/tests/design-system-guards.test.ts`, loaded CSS manifest via Vite build, and visual-smoke tests.
- Secondary evidence: `npm run lint`, `npm run build`, and targeted `rg` scans.
- Static scans alone are not sufficient because CSS selector movement can pass text scans while breaking runtime cascade, loading states or route fallback rendering.

## 2f. Baseline / Before-After Rule

- Baseline artifact before implementation: `app-css-size-and-duplication-before.md`.
- Comparison after implementation: `app-css-size-and-duplication-after.md`.
- Expected invariant: `App.css` must be under `2600` lines and the final import order must be documented.

## 2g. Ownership Routing Rule

Responsibility routing table:

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Tokens App generiques | `frontend/src/styles/app/tokens.css` | variables mecaniques page/element/propriete |
| Typographie App | `frontend/src/styles/app/typography.css` | variables de font-size par composant single-use |
| Base et reset App | `frontend/src/styles/app/base.css` | base rules enfouies dans un theme feature |
| Layout/flex/grid | `frontend/src/styles/app/layout.css` | repetitions locales de `display:flex` |
| Boutons/actions | `frontend/src/styles/app/buttons.css` | variantes bouton page-specific |
| Cartes/panels/selectables | `frontend/src/styles/app/cards.css` | cartes cliquables dupliquees par theme |
| Formulaires/inputs | `frontend/src/styles/app/forms.css` | input/modal form style single-use global |
| Notices/error/warning | `frontend/src/styles/app/notices.css` | notices nommees par page |
| Etats loading/error/empty | `frontend/src/styles/app/states.css` | etats centres nommes par page |
| Media/avatars/images | `frontend/src/styles/app/media.css` | avatars identiques repartis par feature |
| Skeletons | `frontend/src/styles/app/skeletons.css` | definitions `.skeleton-line` concurrentes |

## 2j. Contract Shape

- Contract shape: not applicable.
- Reason: no API, route manifest, DTO, OpenAPI schema, generated client or payload contract is modified.

## 2k. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| mechanical split | `App.css` monolith | approved `styles/app/*.css` modules | none | build and visual-smoke | `App.css` imports only | invalid cascade |
| primitives | repeated state/card/form/layout classes | shared primitives | exact TSX className composition | design-system and scans | no alias | visual regression |
| guards | App-only guard assumptions | App CSS surface guard | none | named design-system tests | mapping guard reads evidence | guard cannot access evidence |
| evidence | missing before/after artifacts | story evidence markdown files | none | story validation scripts | final evidence records scans | missing validation |

## 2h. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | CSS fallback exact `--usage-progress` | valeur runtime injectee | permanent tant que la progression reste runtime |
| `app-css-variable-usage.md` | App custom properties retained | shared/themeable/variant-driven token evidence | reviewed by this story |

## 2i. Reintroduction Guard

Required guard test names:

- `blocks stale TSX consumers from App CSS mapping`
- `blocks single-use App custom properties without retained decision`
- `blocks non-type App CSS module filenames`
- `blocks App CSS duplicate selectors and size regression`

Executable evidence: `npm run test -- design-system` runs these tests in `frontend/src/tests/design-system-guards.test.ts`.

## 3. Required Modules

Allowed `frontend/src/styles/app/` files:

- `tokens.css`
- `base.css`
- `typography.css`
- `layout.css`
- `buttons.css`
- `cards.css`
- `forms.css`
- `notices.css`
- `states.css`
- `media.css`
- `skeletons.css`

Any other file under `frontend/src/styles/app/` is forbidden unless the user approves a new type owner in this story.

## 4. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Baseline records current App CSS metrics. | Evidence: `app-css-size-and-duplication-before.md`; `rg -n "^" src/App.css`. |
| AC2 | `App.css` is below `2600` lines or reduced by at least `35%`. | Evidence: command `rg -n "^" src/App.css`; `app-css-size-and-duplication-after.md`. |
| AC3 | Modules are grouped by type under `frontend/src/styles/app/`. | Evidence: exact filename guard; `npm run test -- design-system`. |
| AC4 | Repeated UI patterns use primitives. | Evidence: `app-css-type-primitive-mapping.md`; command `rg -n "\.(notice|state-centered|select-card|skeleton-line)" src`. |
| AC5 | Token scales use generic names where migrated. | Evidence: `npm run test -- theme-tokens design-system`; mechanical-token scan. |
| AC6 | No migrated selector remains as an alias. | Evidence: command `rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css src/styles/app`. |
| AC7 | App CSS guard prevents listed regressions. | Evidence: named tests in `design-system-guards.test.ts`; command `npm run test -- design-system`. |
| AC8 | Frontend validates after className migration. | Evidence: `npm run lint`, `npm run build`, and targeted Vitest command. |
| AC9 | Single-use custom properties are removed or justified. | Evidence: `app-css-variable-usage.md`; `npm run test -- design-system`. |
| AC10 | JSX uses primitive class composition. | Evidence: command `rg -n "\b(notice|select-card|form-control|state-centered|stack|cluster)\b" src -g "*.tsx" -g "*.css"`. |
| AC11 | TSX consumers are migrated for every changed CSS class. | Evidence: `app-css-tsx-consumers.md`; `npm run test -- design-system`. |
| AC12 | Total App CSS surface reduces duplicate bodies by 30%. | Evidence: before/after metrics and `npm run test -- design-system`. |

## 5. Implementation Tasks

- [ ] Task 1 - Capture baseline and consumers. (AC: AC1)
- [ ] Task 2 - Create type-based App CSS modules. (AC: AC2, AC3)
- [ ] Task 3 - Run mechanical selector merge. (AC: AC4, AC12)
- [ ] Task 4 - Consolidate reusable primitives. (AC: AC4, AC10, AC11)
- [ ] Task 5 - Normalize token scales where safe. (AC: AC5, AC9)
- [ ] Task 6 - Harden guards and evidence. (AC: AC7, AC9, AC11, AC12)
- [ ] Task 7 - Validate runtime and static quality. (AC: AC8)

## 6. Regression Guardrails

Applicable invariants:

- `RG-044` to `RG-050`
- `RG-059`
- `RG-061`
- `RG-075`
- `RG-076`
- `RG-077`
- `RG-078`

## 6a. Current State Evidence

- Evidence 1: `frontend/src/App.css` - baseline before implementation is 4094 lines.
- Evidence 2: `frontend/src/App.css` - duplicate declaration bodies and duplicated skeleton/header selectors were present before extraction.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consulted before implementation.

## 6b. Target State

- `frontend/src/App.css` contains only typed imports and a short file-level comment.
- `frontend/src/styles/app/` contains only approved type modules.
- App primitives `.notice`, `.state-centered`, `.select-card`, `.form-control`, `.stack` and `.cluster` exist and are consumed by TSX.
- Design-system guards read the whole App CSS surface after modular extraction.

## 7. Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke
npm run lint
npm run build
rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css src/styles/app
rg -n "skeleton-line|people-page-header h1|people-page-header p" src/App.css src/styles/app
rg -n -- "--app-.*-(font-size|border-radius|background|color)-[0-9]+" src/App.css src/styles/app
rg -n "\b(notice|select-card|form-control|state-centered|stack|cluster)\b" src -g "*.tsx" -g "*.css"
rg --files src/styles/app
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/00-story.md
```

## 8. Mandatory Reuse / DRY Constraints

- Reuse existing global tokens from `frontend/src/styles/design-tokens.css`, `theme.css`, `premium-theme.css`, `glass.css`, `backgrounds.css` and `utilities.css`.
- Reuse existing App primitives when they already satisfy a type responsibility.
- Shared abstractions must group by style type, not by page, feature or product wording.
- Prefer class composition in JSX over duplicated CSS bodies.

## 8a. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- duplicate active implementations
- legacy class aliases
- silent fallback behavior
- broad allowlists
- unapproved files under `frontend/src/styles/app/`
- old CSS classes retained only to avoid TSX migration
- duplicate `.skeleton-line` base definitions
- repeated `.people-page-header h1` or `.people-page-header p` base definitions outside responsive overrides
- single-use custom properties that are not shared, themeable or variant-driven

## 8b. Files to Inspect First

- `_condamad/stories/regression-guardrails.md`
- `frontend/src/App.css`
- `frontend/src/App.tsx`
- `frontend/src/main.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`

## 8c. Expected Files to Modify

Likely files:

- `frontend/src/App.css`
- `frontend/src/styles/app/tokens.css`
- `frontend/src/styles/app/base.css`
- `frontend/src/styles/app/typography.css`
- `frontend/src/styles/app/layout.css`
- `frontend/src/styles/app/buttons.css`
- `frontend/src/styles/app/cards.css`
- `frontend/src/styles/app/forms.css`
- `frontend/src/styles/app/notices.css`
- `frontend/src/styles/app/states.css`
- `frontend/src/styles/app/media.css`
- `frontend/src/styles/app/skeletons.css`
- exact TSX consumers returned by className scans
- evidence artifacts in this story folder

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`

Files not expected to change:

- `backend/**`
- `frontend/package.json`
- dependency lockfiles

## 8d. Dependency Policy

- New dependencies: none.
- Dependency changes allowed only with explicit user approval.
- Justification: the CSS split, guards and evidence use existing React, Vite, Vitest and CSS tooling only.

## 8e. Regression Risks

- Risk: visual drift from changed cascade order after module extraction.
- Risk: CSS is split but duplicated bodies remain in modules.
- Risk: guards miss App CSS because they read only `App.css`.

## 8f. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through alias, shim, wrapper or fallback.

## 8g. References

- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/03-story-candidates.md`
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/03-story-candidates.md`
- `_condamad/stories/CS-121-definir-primitives-css-generiques-app/00-story.md`
- `_condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 9. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before metrics | `app-css-size-and-duplication-before.md` | line count, selector count, duplicate body baseline |
| after metrics | `_condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/app-css-size-and-duplication-after.md` | size target and import/module ownership |
| migration mapping | `_condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/app-css-type-primitive-mapping.md` | map App classes to canonical primitives |
| TSX consumers | `_condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/app-css-tsx-consumers.md` | before/after className consumers |
| variable usage | `_condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/app-css-variable-usage.md` | custom-property usage counts and decisions |
| final evidence | `_condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/generated/10-final-evidence.md` | test, lint, build and scan results |

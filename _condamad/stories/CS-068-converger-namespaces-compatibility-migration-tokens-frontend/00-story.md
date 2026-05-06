# Story CS-068 converger-namespaces-compatibility-migration-tokens-frontend: Converger les namespaces compatibility et migration-only de tokens frontend

Status: done

## Objective

Retirer tous les namespaces de tokens frontend classes compatibility ou migration-only par l'audit `F-002`.
Les consommateurs doivent utiliser les tokens canoniques ou une extension semantique documentee non legacy.
Aucun alias transitoire et aucune AC livree avec limitation ne sont acceptables.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0806/03-story-candidates.md#SC-001`
- Reason for change: des namespaces compatibility/migration restent declares ou consommes dans `frontend/src`.

## Domain Boundary

- Domain: `frontend/src/styles`
- In scope:
  - Inventorier puis retirer les declarations et consommateurs des namespaces listes par `SC-001`.
  - Migrer les fichiers sources/tests listes par `SC-001` vers les tokens canoniques ou vers une extension semantique durable sans vocabulaire compatibility.
  - Mettre a jour `frontend/src/styles/token-namespace-registry.md` et les guards associes.
- Out of scope:
  - Refonte visuelle ou changement produit volontaire.
  - Migration des valeurs hardcodees non liees a ces namespaces.
  - Renommage du concept admin prompts `legacy`, couvert par `CS-070`.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-048`, `RG-049` ou `RG-050`.
  - Ne pas conserver `--badge-*`, `--nav-*` ou les namespaces produit comme compatibility active.
  - Ne pas remplacer un alias legacy par un autre alias, fallback, wrapper CSS ou re-export.

## Regression Guardrails

- Applicable invariants:
  - `RG-044` - token namespaces classified and `design-tokens.css` remains source.
  - `RG-045` - migrated visual values must not return as local literals.
  - `RG-048` - no CSS fallback preserving retired tokens.
  - `RG-049` - legacy style aliases must not remain unclassified.
  - `RG-050` - design-system guards remain executable.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story deletes compatibility and migration-only token facades while routing consumers to canonical token ownership.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Visual output may change only by documented canonical token equivalence.
  - Runtime CSS consumers must keep equivalent states, spacing and interaction semantics.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: a token namespace is classified as `external-active` or no canonical owner can be proven.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest design-system prouvent les namespaces actifs. |
| Baseline Snapshot | yes | Les scans before/after prouvent la convergence. |
| Ownership Routing | yes | Chaque namespace retire doit etre route vers un owner canonique. |
| Allowlist Exception | no | Aucune exception large ou temporaire n'est autorisee. |
| Contract Shape | no | Aucun contrat API, DTO ou serialization n'est modifie. |
| Batch Migration | no | La suppression est bornee par namespaces, pas par plan batch multi-surface. |
| Reintroduction Guard | yes | Les namespaces retires ne doivent pas revenir. |
| Persistent Evidence | yes | Les artefacts de story persistent les decisions. |

## Runtime Source of Truth

- Primary source of truth: AST guard and CSS token guards in:
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/tests/legacy-style-policy.test.ts`
- Secondary evidence: targeted `rg` scans over `frontend/src` for forbidden declarations and consumers.
- Static scans alone are not sufficient: runtime-equivalent guard execution is required through `npm run test -- theme-tokens design-system legacy-style css-fallback`.

## Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-068-converger-namespaces-compatibility-migration-tokens-frontend/token-namespaces-before.md`.
- Comparison after implementation: `_condamad/stories/CS-068-converger-namespaces-compatibility-migration-tokens-frontend/token-namespaces-after.md`.
- Expected invariant: every forbidden namespace from the before artifact is either deleted or mapped to a canonical non-legacy owner with no compatibility fallback.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Frontend token namespace | `frontend/src/styles/design-tokens.css` or a documented semantic local namespace | compatibility namespace, migration-only namespace, fallback alias |
| Component visual consumer | canonical CSS variable or registered semantic extension | retired `--badge-*`, `--nav-*`, `--bg-*`, `--cta-*` facade |

## Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: no exception or allowlist is allowed for compatibility/migration-only namespaces.

## Contract Shape

- Contract Shape: not applicable
- Reason: no generated API, DTO, HTTP status, serialization name, or frontend data contract is changed.

## Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: the active archetype is legacy facade removal and each namespace is audited through the removal audit instead of a batch migration table.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before namespace baseline | `token-namespaces-before.md` | Inventory forbidden namespace declarations and consumers before deletion. |
| After namespace evidence | `token-namespaces-after.md` | Prove zero active forbidden namespace consumers after migration. |
| Final validation evidence | `generated/10-final-evidence.md` | Persist commands, results and residual risks. |

## Reintroduction Guard

- Architecture guard: forbidden namespace symbols must fail if reintroduced.
- Deterministic source: forbidden symbols `--bg-`, `--cta-`, `--badge-`, `--nav-`,
  `--background-`, `--ni-`, `--result-`, `--timeline-`, `--page-`,
  `--inner-light`, `--accent-purple`.
- Evidence profile: `reintroduction_guard`; command `npm run test -- theme-tokens design-system legacy-style css-fallback`.
- Additional executable evidence: targeted `rg` scans in the Validation Plan must remain clean.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0806/03-story-candidates.md#SC-001` - audit source for forbidden token namespaces.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - shared guardrails protecting token namespace convergence.

## Target State

- Aucun consommateur actif des namespaces retires ne reste sous `frontend/src`.
- Les nouveaux namespaces locaux sont semantiques et declares dans `token-namespace-registry.md`.
- Les guards Vitest et scans ciblant les namespaces retires passent sans limitation.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The before artifact inventories every forbidden namespace. | Evidence profile: `baseline_snapshot`; `rg -n "TODO" token-namespaces-before.md` returns zero hits. |
| AC2 | All forbidden namespace declarations are removed. | Evidence profile: `removal`; run the AC2 `rg` declaration scan in the Validation Plan. |
| AC3 | All consumers use canonical tokens or non-legacy extensions. | Evidence profile: `ownership_routing`; run the AC3 `rg` consumer scan in the Validation Plan. |
| AC4 | Registries are synchronized. | Evidence profile: `registry_guard`; `npm run test -- theme-tokens design-system legacy-style css-fallback`. |
| AC5 | Focused visual smoke passes. | Evidence profile: `runtime_guard`; `npm run test -- visual-smoke` and `npm run lint`. |
| AC6 | Reintroduction of retired namespaces is guarded. | Evidence profile: `reintroduction_guard`; `npm run test -- theme-tokens design-system`. |

## Implementation Tasks

- [ ] Task 1 - Capture complete namespace baseline and canonical owners. (AC: AC1)
- [ ] Task 2 - Migrate consumers to canonical tokens or durable non-legacy semantic extensions. (AC: AC3, AC5)
- [ ] Task 3 - Delete obsolete declarations without alias, fallback, or wrapper. (AC: AC2, AC6)
- [ ] Task 4 - Update token/legacy/fallback registries and tests that asserted alias names. (AC: AC4, AC6)
- [ ] Task 5 - Capture after evidence and run all validation commands. (AC: AC2, AC3, AC4, AC5, AC6)

## Mandatory Reuse / DRY Constraints

- Reuse `design-tokens.css`, `theme.css`, `token-namespace-registry.md` and existing Vitest guards.
- Do not recreate compatibility aliases.
- Shared semantic extensions are allowed only when they are reusable, documented and non-legacy.

## No Legacy / Forbidden Paths

- Forbidden: compatibility wrappers, legacy transitional aliases, duplicate active token paths, silent fallback behavior.
- Forbidden: preserving a retired path through wrapper CSS, fallback variables, or re-export.
- Forbidden symbols: active declarations or consumers for retired namespaces listed in SC-001.

## Removal Classification Rules

- `canonical-active`: item is the canonical source and must be kept.
- `external-active`: item is referenced by public docs, generated links, clients, or audit evidence and must block deletion.
- `historical-facade`: compatibility or migration namespace delegating to canonical tokens.
- `dead`: item has zero active consumers and can be deleted.
- `needs-user-decision`: ambiguity remains after scans and must block implementation.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions: `delete`, `keep`, `replace-consumer`, `needs-user-decision`.
Persisted audit artifact: `_condamad/stories/CS-068-converger-namespaces-compatibility-migration-tokens-frontend/token-namespaces-after.md`.

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Token namespaces | `design-tokens.css` and semantic local namespaces | compatibility/migration namespaces |
| Registry classification | `frontend/src/styles/token-namespace-registry.md` | ad hoc comments or unregistered local variables |

## Delete-Only Rule

Items classified as removable must be deleted, not repointed.
Forbidden replacements include preserving a wrapper, adding a compatibility alias, preserving a retired path through re-export, or replacing deletion with fallback behavior.

## External Usage Blocker

If an item is classified as `external-active`, it must not be deleted.
The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## Generated Contract Check

- OpenAPI path absence: no backend OpenAPI path is added, removed or renamed by this frontend token story.
- Generated client/schema absence: no generated client, generated schema or generated manifest is affected.
- Required evidence: `git diff -- frontend` remains limited to CSS/tests/registry surfaces and no generated API artifact is changed.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-0806/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-06-0806/03-story-candidates.md`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`

## Expected Files to Modify

Likely files:
- `frontend/src/**/*.css`
- `frontend/src/**/*.tsx`
- `frontend/src/**/*.ts`
- `frontend/src/styles/token-namespace-registry.md`

Likely tests:
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`

Files not expected to change:
- `backend/app/main.py`
- `frontend/package.json`

## Dependency Policy

- New dependencies: none.
- Justification: no dependency change is required.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- theme-tokens design-system legacy-style css-fallback
npm run test -- AppBgStyles BottomNavPremium MiniInsightCard ShortcutCard predictionBands visual-smoke
npm run lint
rg -n "var\(--bg-" src -g "*.css" -g "*.tsx" -g "*.ts"
rg -n "var\(--cta-" src -g "*.css" -g "*.tsx" -g "*.ts"
rg -n "var\(--badge-" src -g "*.css" -g "*.tsx" -g "*.ts"
rg -n "--(bg-|cta-|badge-|nav-|background-|ni-|result-|timeline-|page-|inner-light|accent-purple)|--(line|success|danger|btn-text|purple_base):" src -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-068-converger-namespaces-compatibility-migration-tokens-frontend/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- No PASS with limitation is accepted.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Visual drift from near-equivalent tokens.
- Legacy alias reintroduction through tests or CSS.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0806/03-story-candidates.md#SC-001`
- `_condamad/stories/regression-guardrails.md`

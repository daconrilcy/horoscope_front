# Story CS-060 reduire-derniers-fallbacks-css-tokens-premium: Reduire les derniers fallbacks CSS et statuer les tokens premium manquants

Status: ready-to-dev

## Objective

Reduire les fallbacks CSS `var(--token, literal)` restants lorsque le token canonique est garanti.
Les tokens premium `--premium-text-muted` et `--premium-glass-border-soft` doivent etre declares dans une source canonique ou bloques comme decision explicite.

## Source

- Audit: `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-001`
- Finding: F-002

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-001`
- Reason for change: réduire les fallbacks CSS restants et trancher les tokens premium manquants.

## Domain Boundary

- Domain: `frontend/src/styles`

In scope:
- Migrer les fallbacks CSS classés dans le lot CS-060.
- Synchroniser les registres markdown et executables.

Out of scope:
- Migration des styles inline.
- Migration des selectors legacy.

Explicit non-goals:
- Ne pas affaiblir `RG-048` ou `RG-050`.
- Ne pas ajouter de fallback literal local.

## Operation Contract

- Operation type: migrate
- Primary archetype: legacy-facade-removal
- Behavior change allowed: constrained
- Deletion allowed: yes
- Replacement allowed: no

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les tests design-system prouvent les tokens et fallbacks |
| Baseline Snapshot | yes | before/after requis |
| Ownership Routing | yes | tokens premium dans `premium-theme.css` |
| Allowlist Exception | yes | registres fallback synchronisés |

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-001`.
- Evidence 2: `frontend/src/styles/css-fallback-allowlist.md`.
- Evidence 3: `_condamad/stories/regression-guardrails.md`.

## Target State

- Les fallbacks garantis sont retirés.
- Les exceptions restantes sont classées.

## Scope

In scope:
- Capturer les compteurs before/after des fallbacks CSS restants.
- Supprimer les fallbacks garantis.
- Conserver les entrees dynamiques `--usage-progress` si le pont runtime reste requis.
- Decider `--premium-text-muted` et `--premium-glass-border-soft`.
- Synchroniser `frontend/src/styles/css-fallback-allowlist.md` et `frontend/src/tests/design-system-allowlist.ts`.

Out of scope:
- Refactor global des themes premium.
- Conversion des styles inline.
- Suppression de selectors legacy admin.

## Regression Guardrails

- `RG-048`: les fallbacks CSS doivent rester exacts et classes.
- `RG-050`: les guards anti-drift design-system restent executables.

## Runtime Source of Truth

- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `npm run test -- css-fallback design-system theme-tokens`

## Allowlist / Exception Register

- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline couvre les fallbacks actuels. | `npm run test -- css-fallback` et inventaire before. |
| AC2 | Chaque fallback supprime a une preuve de token garanti. | `npm run test -- theme-tokens`. |
| AC3 | Les registres fallback restent synchronises. | `npm run test -- css-fallback design-system`. |
| AC4 | Les tokens premium manquants sont tranches. | `rg -n "premium-text-muted|premium-glass-border-soft" src`. |
| AC5 | Aucun nouveau fallback non classe n'est introduit. | `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"`. |

## Validation Plan

```powershell
Push-Location frontend
npm run test -- css-fallback design-system theme-tokens
npm run lint
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-060-reduire-derniers-fallbacks-css-tokens-premium/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-060-reduire-derniers-fallbacks-css-tokens-premium/00-story.md
```

## Implementation Tasks

- [ ] Task 1 - Capturer le baseline.
- [ ] Task 2 - Supprimer les fallbacks garantis.
- [ ] Task 3 - Synchroniser les registres.
- [ ] Task 4 - Valider.

## Mandatory Reuse / DRY Constraints

- Réutiliser `premium-theme.css`, `css-fallback-allowlist.md` et `design-system-allowlist.ts`.
- Ne pas créer de registre parallèle.

## No Legacy / Forbidden Paths

- Aucun nouveau `var(--token, literal)` non classé.
- Aucun alias premium implicite.

## Files to Inspect First

- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`

## Expected Files to Modify

Likely files:
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`

Likely tests:
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`

Files not expected to change:
- `backend/`

## Dependency Policy

- New dependencies: none.

## Regression Risks

- Risque: suppression d'un fallback encore requis.
- Garde: tests fallback et inventaire after.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, record the blocker.
- Do not preserve legacy behavior for convenience.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-001`
- `_condamad/stories/regression-guardrails.md`

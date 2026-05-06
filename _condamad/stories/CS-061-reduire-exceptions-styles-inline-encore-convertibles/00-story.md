# Story CS-061 reduire-exceptions-styles-inline-encore-convertibles: Reduire les exceptions de styles inline encore convertibles

Status: ready-to-dev

## Objective

Convertir les styles inline restants qui peuvent devenir des classes CSS, variantes de composant ou ponts par custom properties sans perdre les valeurs runtime.
Le pass-through public `Skeleton.style` reste preserve sauf decision explicite de changement d'API.

## Source

- Audit: `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-002`
- Finding: F-003

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-002`
- Reason for change: réduire les exceptions inline convertibles.

## Domain Boundary

- Domain: `frontend/src/components`

In scope:
- Classer et réduire les styles inline convertibles.
- Synchroniser les allowlists inline.

Out of scope:
- Refonte de l'API `Skeleton`.
- Migration des fallbacks CSS.

Explicit non-goals:
- Ne pas affaiblir `RG-047` ou `RG-050`.
- Ne pas supprimer `Skeleton.style`.

## Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Behavior change allowed: constrained
- Deletion allowed: yes
- Replacement allowed: no

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | guards inline-style et design-system |
| Baseline Snapshot | yes | before/after requis |
| Ownership Routing | yes | styles visuels vers CSS |
| Allowlist Exception | yes | exceptions restantes exactes |
| Contract Shape | yes | `Skeleton.style` préservé |

## Runtime Source of Truth

- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `npm run test -- inline-style design-system`

## Allowlist / Exception Register

- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-allowlist.ts`

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-002`.
- Evidence 2: `frontend/src/tests/inline-style-allowlist.ts`.
- Evidence 3: `_condamad/stories/regression-guardrails.md`.

## Target State

- Les styles inline convertibles sont déplacés en CSS.
- Les exceptions restantes sont classées.

## Scope

In scope:
- Classer chaque style inline restant.
- Preferer classes, variantes ou custom properties typees pour `Badge` et la geometrie timeline lorsque possible.
- Preserver `Skeleton.style`.
- Synchroniser `frontend/src/tests/inline-style-allowlist.ts` et `frontend/src/tests/design-system-allowlist.ts`.

Out of scope:
- Refonte d'API publique des composants UI.
- Migration des fallbacks CSS, aliases token ou selectors legacy.

## Regression Guardrails

- `RG-047`: les styles inline statiques sont interdits hors exceptions exactes.
- `RG-050`: les guards design-system restent executables.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline classe chaque style inline restant. | `rg -n "style=\\{" src -g "*.tsx"` et inventaire before. |
| AC2 | Les declarations visuelles convertibles passent en CSS. | `npm run test -- inline-style design-system`. |
| AC3 | Le contrat runtime `Skeleton.style` reste preserve. | `npm run test -- inline-style design-system`. |
| AC4 | Les allowlists design-system restent synchronisees. | `npm run test -- inline-style design-system`. |
| AC5 | Aucun nouveau style inline non classe n'est introduit. | scan final `rg -n "style=\\{" src -g "*.tsx"`. |

## Validation Plan

```powershell
Push-Location frontend
npm run test -- inline-style design-system
npm run lint
rg -n "style=\{" src -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-061-reduire-exceptions-styles-inline-encore-convertibles/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-061-reduire-exceptions-styles-inline-encore-convertibles/00-story.md
```

## Implementation Tasks

- [ ] Task 1 - Capturer le baseline.
- [ ] Task 2 - Migrer les styles convertibles.
- [ ] Task 3 - Synchroniser les allowlists.
- [ ] Task 4 - Valider.

## Mandatory Reuse / DRY Constraints

- Réutiliser les CSS composants existants.
- Ne pas créer de registre parallèle.

## No Legacy / Forbidden Paths

- Aucun nouveau style inline statique non classé.
- Pas de suppression silencieuse du prop `style` de `Skeleton`.

## Files to Inspect First

- `frontend/src/components/prediction/TimelineRail.tsx`
- `frontend/src/components/prediction/TimelineRail.css`
- `frontend/src/tests/inline-style-allowlist.ts`

## Expected Files to Modify

Likely files:
- `frontend/src/components/prediction/TimelineRail.tsx`
- `frontend/src/components/prediction/TimelineRail.css`
- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-allowlist.ts`

Likely tests:
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`

Files not expected to change:
- `backend/`

## Dependency Policy

- New dependencies: none.

## Regression Risks

- Risque: perte de géométrie du rail temporel.
- Garde: tests inline-style et visual-smoke.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, record the blocker.
- Do not preserve legacy behavior for convenience.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-002`
- `_condamad/stories/regression-guardrails.md`

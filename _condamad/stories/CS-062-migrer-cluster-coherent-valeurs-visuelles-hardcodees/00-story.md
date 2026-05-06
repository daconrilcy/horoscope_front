# Story CS-062 migrer-cluster-coherent-valeurs-visuelles-hardcodees: Migrer un cluster coherent de valeurs visuelles hardcodees

Status: ready-to-dev

## Objective

Migrer un seul cluster produit coherent de valeurs visuelles ou typographiques hardcodees parmi les fichiers signales.
Le cluster doit converger vers les tokens, roles typographiques ou utilitaires existants sans refactor global.

## Source

- Audit: `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-003`
- Finding: F-004

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-003`
- Reason for change: migrer un cluster visuel borné.

## Domain Boundary

- Domain: `frontend/src/components`

In scope:
- Cluster unique `frontend/src/components/prediction/PeriodCard.css`.
- Migration vers tokens existants.

Out of scope:
- Migration globale des 110 fichiers.
- Migration des styles inline et selectors legacy.

Explicit non-goals:
- Ne pas affaiblir `RG-044`, `RG-045`, `RG-046` ou `RG-050`.
- Ne pas créer de token synonyme.

## Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Behavior change allowed: constrained
- Deletion allowed: yes
- Replacement allowed: no

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | tests design-system/theme/visual |
| Baseline Snapshot | yes | before/after requis |
| Ownership Routing | yes | tokens et roles existants |

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-003`.
- Evidence 2: `frontend/src/styles/typography-roles.md`.
- Evidence 3: `_condamad/stories/regression-guardrails.md`.

## Target State

- Le cluster choisi utilise davantage de tokens existants.

## Scope

In scope:
- Choisir un cluster borne avant edition.
- Utiliser les tokens, roles typographiques et utilitaires existants avant toute creation.
- Capturer les compteurs before/after du cluster choisi.
- Mettre a jour les registres seulement si un token ou role durable est introduit.

Out of scope:
- Migration de tous les fichiers signales.
- Refonte visuelle produit.
- Migration des fallbacks CSS, styles inline ou selectors legacy hors cluster choisi.

## Regression Guardrails

- `RG-044`: les namespaces de tokens restent classes.
- `RG-045`: les valeurs migrees ne doivent pas revenir non classees.
- `RG-046`: les roles typographiques restent canoniques.
- `RG-050`: les guards design-system restent executables.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le cluster choisi est borne avant edition. | inventaire before et scan cible. |
| AC2 | Les valeurs remplacees reutilisent les tokens existants. | `npm run test -- design-system theme-tokens`. |
| AC3 | Tout token ou role durable est registre ou bloque. | registre verifie ou mention non applicable. |
| AC4 | Le compteur du cluster diminue ou reste justifie. | inventaire after et scan cible. |
| AC5 | Les validations frontend ciblees passent. | `npm run test -- design-system theme-tokens visual-smoke` et `npm run lint`. |

## Validation Plan

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens visual-smoke
npm run lint
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-062-migrer-cluster-coherent-valeurs-visuelles-hardcodees/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-062-migrer-cluster-coherent-valeurs-visuelles-hardcodees/00-story.md
```

## Implementation Tasks

- [ ] Task 1 - Choisir le cluster.
- [ ] Task 2 - Capturer le before.
- [ ] Task 3 - Migrer les valeurs éligibles.
- [ ] Task 4 - Capturer l'after et valider.

## Mandatory Reuse / DRY Constraints

- Réutiliser `design-tokens.css`, `theme.css`, `utilities.css` et `typography-roles.md`.
- Ne pas créer de nouveau token.

## No Legacy / Forbidden Paths

- Aucun nouveau token non classé.
- Pas de migration opportuniste hors cluster.

## Files to Inspect First

- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/typography-roles.md`

## Expected Files to Modify

Likely files:
- `frontend/src/components/prediction/PeriodCard.css`

Likely tests:
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`

Files not expected to change:
- `backend/`

## Dependency Policy

- New dependencies: none.

## Regression Risks

- Risque: différence visuelle du cluster.
- Garde: visual-smoke et inventaire after.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, record the blocker.
- Do not preserve legacy behavior for convenience.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0108/03-story-candidates.md#SC-003`
- `_condamad/stories/regression-guardrails.md`

# Story CS-393 refondre-page-natal-autour-lecture-narrative: Recentrer La Page Natale
Status: done

## Trigger / Source
- Source type: frontend-refactor
- Source reference: `_story_briefs/cs-393-refondre-page-natal-autour-lecture-narrative.md`
- Reason for change: la page publique doit présenter une lecture continue et accessible.

## Objective
Composer `/natal` autour du profil, du fil narratif et du mode astrologue replié.

## Target State
- La page publique présente trois couches lisibles.
- Le fil narratif reste la surface principale.
- Les détails experts restent dans le mode astrologue.

## Current State Evidence
- Evidence 1: `frontend/src/pages/NatalChartPage.tsx` - composition publique inspectée.
- Evidence 2: `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` - fil narratif inspecté.

## Domain Boundary
- Domain: natal-public-reading-ui
- In scope:
  - Composition React publique, états et styles associés.
- Out of scope:
  - Génération backend et calcul astrologique.
- Explicit non-goals:
  - Aucun changement d'entitlement.

## Operation Contract
- Operation type: update
- Primary archetype: custom
- Archetype reason: la convergence visuelle publique est ciblée sur `/natal`.
- Behavior change allowed: yes
- Behavior change constraints:
  - Conserver le profil et le mode astrologue existants.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une carte publique secondaire reste nécessaire.

Additional validation rules:
- Garder le mode astrologue replié et centraliser les styles dans les feuilles CSS.

## Required Contracts
| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | Le frontend consomme le contrat backend. |
| Baseline Snapshot | no | La QA responsive est portée par CS-395. |
| Ownership Routing | no | Aucun routage modifié. |
| Allowlist Exception | no | Aucun allowlist requis. |
| Contract Shape | no | Les types frontend portent la forme attendue. |
| Batch Migration | no | Aucune migration de lot. |
| Reintroduction Guard | no | Les gardes arrivent dans CS-395. |
| Persistent Evidence | no | Les tests versionnés suffisent. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La page publique conserve le profil. | `pnpm --dir frontend test -- NatalChartPage`. |
| AC2 | Le fil narratif devient la surface principale. | `pnpm --dir frontend test -- natalNarrativeReading`. |
| AC3 | Le mode astrologue reste replié. | `pnpm --dir frontend test -- NatalAstrologerMode`. |
| AC4 | Les composants historiques ne sont plus rendus. | `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC5 | Aucun style inline n'est ajouté. | `pnpm --dir frontend lint`. |

## Implementation Tasks
- [x] Task 1: Recomposer `NatalChartPage`. (AC: AC1, AC2, AC3)
- [x] Task 2: Ajouter le composant narratif et sa feuille CSS. (AC: AC2, AC5)
- [x] Task 3: Écarter les cartes publiques historiques. (AC: AC4)
- [x] Task 4: Couvrir les états de rendu. (AC: AC1, AC2, AC3, AC4)

## Mandatory Reuse / DRY Constraints
- Réutiliser `NatalInterpretation` et `NatalAstrologerMode`.
- Réutiliser les variables CSS existantes.

## No Legacy / Forbidden Paths
- Aucun wrapper legacy.
- Aucun chemin compatibility.
- Aucun fallback vers les cartes historiques.

## Regression Guardrails
- Applicable invariants: `RG-047`, `RG-052`, `RG-071`, `RG-073`, `RG-153`.
- Required regression evidence: `pnpm --dir frontend test -- NatalChartPage natalNarrativeReading`.
- Allowed differences: composition publique recentrée.

## Files to Inspect First
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`

## Expected Files to Modify
Likely files:
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.css`

Likely tests:
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/natalNarrativeReading.test.tsx`

Files not expected to change:
- `backend/app/**`

## Dependency Policy
- New dependencies: none.
- Justification: React et les styles existants suffisent.

## Validation Plan
- VC1: `pnpm --dir frontend test -- NatalChartPage natalNarrativeReading`
- VC2: `pnpm --dir frontend test -- NatalAstrologerMode natalPublicDomGuard`
- VC3: `pnpm --dir frontend lint`

## Regression Risks
- Une carte historique pourrait réapparaître ; RG-153 et le test DOM bornent ce risque.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.

## References
- `_story_briefs/cs-393-refondre-page-natal-autour-lecture-narrative.md`
- `_condamad/stories/regression-guardrails.md`

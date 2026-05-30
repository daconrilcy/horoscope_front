# Story CS-394 ajouter-ce-que-nous-avons-utilise-fin-lecture-natale: Ajouter Les Sources Lisibles
Status: done

## Trigger / Source
- Source type: frontend-feature
- Source reference: `_story_briefs/cs-394-ajouter-ce-que-nous-avons-utilise-fin-lecture-natale.md`
- Reason for change: la lecture publique doit expliquer ses sources sans exposer la plomberie interne.

## Objective
Afficher en fin de lecture une liste compacte de sources formulées pour le lecteur.

## Target State
- Les sources humaines apparaissent après la synthèse.
- Aucun identifiant technique n'est visible.

## Current State Evidence
- Evidence 1: `frontend/src/features/natal-chart/NatalReadingSources.tsx` - rendu public inspecté.
- Evidence 2: `frontend/src/tests/natalNarrativeReading.test.tsx` - tests de rendu inspectés.

## Domain Boundary
- Domain: natal-public-reading-sources
- In scope:
  - Rendu React et styles de la liste des sources.
- Out of scope:
  - Mode astrologue, fournisseur LLM et calcul astrologique.
- Explicit non-goals:
  - Aucun affichage de payload brut.

## Operation Contract
- Operation type: update
- Primary archetype: custom
- Archetype reason: la liste de sources complète le composant narratif public.
- Behavior change allowed: yes
- Behavior change constraints:
  - Afficher uniquement les libellés humains validés.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: une source technique devient nécessaire au public.

Additional validation rules:
- Les identifiants internes restent absents du DOM public.

## Required Contracts
| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | Le frontend consomme le contrat backend. |
| Baseline Snapshot | no | Aucun snapshot comparatif requis. |
| Ownership Routing | no | Aucun routage modifié. |
| Allowlist Exception | no | Aucun allowlist requis. |
| Contract Shape | no | Les types frontend portent la forme attendue. |
| Batch Migration | no | Aucune migration de lot. |
| Reintroduction Guard | no | Les gardes arrivent dans CS-395. |
| Persistent Evidence | no | Les tests versionnés suffisent. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La liste apparaît après la synthèse. | `pnpm --dir frontend test -- natalNarrativeReading`. |
| AC2 | Les libellés humains sont rendus. | `pnpm --dir frontend test -- natalNarrativeReading`. |
| AC3 | Les identifiants internes restent absents du DOM. | `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC4 | Les styles restent dans une feuille CSS dédiée. | `pnpm --dir frontend lint`. |

## Implementation Tasks
- [x] Task 1: Ajouter `NatalReadingSources`. (AC: AC1, AC2)
- [x] Task 2: Ajouter la feuille CSS dédiée. (AC: AC4)
- [x] Task 3: Couvrir l'absence d'identifiants internes. (AC: AC3)

## Mandatory Reuse / DRY Constraints
- Réutiliser le tableau `sources` du contrat public.
- Réutiliser les variables CSS existantes.

## No Legacy / Forbidden Paths
- Aucun wrapper legacy.
- Aucun chemin compatibility.
- Aucun fallback vers un identifiant interne.

## Regression Guardrails
- Applicable invariants: `RG-071`, `RG-073`, `RG-154`.
- Required regression evidence: `pnpm --dir frontend test -- natalNarrativeReading natalPublicDomGuard`.
- Allowed differences: ajout de la liste publique de sources.

## Files to Inspect First
- `frontend/src/features/natal-chart/NatalReadingSources.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`

## Expected Files to Modify
Likely files:
- `frontend/src/features/natal-chart/NatalReadingSources.tsx`
- `frontend/src/features/natal-chart/NatalReadingSources.css`

Likely tests:
- `frontend/src/tests/natalNarrativeReading.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`

Files not expected to change:
- `backend/app/**`

## Dependency Policy
- New dependencies: none.
- Justification: React et CSS suffisent.

## Validation Plan
- VC1: `pnpm --dir frontend test -- natalNarrativeReading natalPublicDomGuard`
- VC2: `pnpm --dir frontend lint`

## Regression Risks
- Un identifiant interne pourrait fuiter ; RG-154 et le test DOM bornent ce risque.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.

## References
- `_story_briefs/cs-394-ajouter-ce-que-nous-avons-utilise-fin-lecture-natale.md`
- `_condamad/stories/regression-guardrails.md`

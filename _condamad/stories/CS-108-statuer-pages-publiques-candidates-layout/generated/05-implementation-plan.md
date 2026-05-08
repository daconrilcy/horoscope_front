# Implementation Plan - CS-108

## Current architecture finding

CS-103 a CS-107 ont ferme la hierarchie runtime des layouts. CS-108 ne doit pas modifier cette hierarchie; elle doit transformer les cinq residus en decisions persistantes et testables.

## Selected approach

Conserver les trois pages publiques potentielles non routees sous decision bloquee avec owners explicites et echeance. Conserver les deux candidats morts avec decision de retrait dediee future, sans suppression physique dans cette story.

## Files to modify

- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts` si necessaire pour verifier les decisions non anonymes.
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-before.md`
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-after.md`
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md`
- generated evidence files.

## Tests to add or update

- Reutiliser `page-architecture-guards.test.ts`.
- Ajouter une verification ciblee uniquement si le registre accepte encore owner `A definir` ou sortie vague.

## Frontend subagent assignment

`condamad-frontend-dev` owns frontend changes under `frontend/**`. Main session owns evidence and final review.

## No Legacy stance

No route alias, redirect, fallback, compatibility wrapper, wildcard exception, or physical deletion is introduced.

## Rollback strategy

Revert only CS-108 frontend registry/guard edits and evidence files if validation fails; do not touch unrelated CS-103 a CS-107 dirty files.

# Execution Brief - CS-100

## Objective

Extraire les surfaces actives catalogue, consommation et release de `frontend/src/pages/admin/AdminPromptsPage.tsx` vers des owners canoniques sous `frontend/src/features/admin-prompts/**`, sans changement de comportement ni contrat API.

## Boundaries

- Modifier uniquement les fichiers frontend autorises, les guards page-architecture et les preuves CS-100.
- Ne pas toucher `backend/**`.
- Reutiliser `frontend/src/api/adminPrompts.ts`.
- Ne pas introduire de wildcard, seuil augmente ou dette temporaire dans `PAGE_SIZE_EXCEPTIONS`.

## Guardrails

- Applicables: `RG-064`, `RG-047`, `RG-049`, `RG-065`.
- Interdits: `apiFetch(` hors owner API, `@ts-nocheck`, `@ts-ignore`, duplicate active section locale, facade de compatibilite.

## Completion

- Inventaires before/after presents.
- Tests cibles AdminPrompts et `page-architecture` passes.
- `npm run lint` passe.
- Evidence finale complete et statut story synchronise.

<!-- Brief d'execution genere pour CS-083. -->

# Execution Brief

Story: CS-083 fermer-garde-no-legacy-vocabulaire-css-actif.

Objectif: supprimer le vocabulaire interdit dans les commentaires CSS actifs et
ajouter une garde Vitest deterministe.

In scope:

- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/components/astro/AstroMoodBackground.css`
- `frontend/src/tests/design-system-policy.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- artefacts CONDAMAD CS-083

Non-goals:

- pas de changement selectors ou comportements Admin Prompts;
- pas de migration des valeurs visuelles Admin Prompts;
- pas de dependance nouvelle.


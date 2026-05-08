<!-- Baseline CS-090 capture avant extraction admin-prompts. -->

# CS-090 Before

Date: 2026-05-08

| Surface | Etat initial |
|---|---|
| `frontend/src/pages/admin/AdminPromptsPage.tsx` | 3035 lignes, `// @ts-nocheck` en tete, hook responsive local. |
| Owner feature | `frontend/src/features/admin-prompts/**` absent pour la slice extraite. |
| Tests existants | `AdminPromptsPage`, `AdminPromptsRouting`, `AdminPromptsCatalogFlow`. |

Commande baseline: `rg -n "@ts-nocheck" frontend/src/pages/admin/AdminPromptsPage.tsx`.
Resultat initial: hit ligne 1.

# CS-146 - Dev log

## Preflight

- Skill utilise: `condamad-frontend-dev`, avec `condamad-dev-story` et `condamad-regression-guardrails`.
- Worktree initial: `_condamad/stories/story-status.md` modifie avant intervention; `.codex-artifacts/*.png` non suivis; dossier CS-146 non suivi.
- Registre anti-regression lu: `_condamad/stories/regression-guardrails.md`.
- Guardrails applicables: `RG-083`, `RG-084`, `RG-085`, `RG-086`, `RG-087`, `RG-088`.

## Implementation

- Baseline runtime before capture sur Vite local.
- Navbar desktop masquee jusqu'a `1024px`.
- Menu mobile rendu modal au clavier: focus initial, wrapping Tab, Escape, scroll lock, restauration focus.
- H1 unique avec nom accessible separe.
- Hero mobile/tablette compactifie par contraintes CSS existantes.


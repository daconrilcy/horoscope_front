<!-- Journal de developpement CONDAMAD pour CS-087. -->

# CS-087 Dev Log

## 2026-05-07

- Lu `AGENTS.md`, le registre `regression-guardrails.md`, la story CS-087 et les references du skill `condamad-frontend-dev`.
- Constate un worktree deja sale avec les stories/audits CS-087 a CS-089 non suivis et `story-status.md` modifie; changements preserves.
- Cree `hardcoded-values-before.md`.
- Migre les declarations actives de `frontend/src/App.css` vers des variables `--app-*` ou tokens existants, sans toucher `App.tsx`.
- Documente l'extension `--app-*` et le role typographique `app-scoped`.
- Ajoute la garde CS-087 dans `design-system-guards.test.ts` et `RG-061`.
- Execute les validations frontend, les scans cibles et les validations story Python apres activation du venv.

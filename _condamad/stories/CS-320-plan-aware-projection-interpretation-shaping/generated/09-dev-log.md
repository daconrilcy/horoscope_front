<!-- Commentaire global: ce journal conserve les decisions d'execution CONDAMAD pour la story CS-320. -->

# Dev Log CS-320

## 2026-05-26

- Logs de reprise lus dans `_condamad/codex-runs/`; l'execution precedente avait
  aligne la story et laisse le statut `ready-to-dev`.
- Capsule `generated/` manquante preparee puis validee avec
  `condamad_prepare.py` et `condamad_validate.py`.
- Changement applicatif volontairement limite a la documentation contractuelle:
  `docs/architecture/client-interpretation-projection-v1-contract.md`.
- Aucun code runtime backend, frontend, Stripe, DB, migration, prompt provider ou
  route publique n'a ete modifie.
- Worktree initial deja sale sur des briefs, docs et artefacts CONDAMAD non lies;
  aucun de ces changements n'a ete revert.
- Reprise finale: tracker, story et preuves realignes sur `ready-to-review`
  pour respecter la consigne d'implementation sans clore en statut review.
- Validations relancees: capsule CONDAMAD, backend pytest projection, backend
  `ruff check`, frontend lint, Vitest cible, JSON samples, OpenAPI neutrality et
  scan negatif des owners React applicatifs.

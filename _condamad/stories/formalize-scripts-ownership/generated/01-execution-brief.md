# Execution Brief

## Story key

`formalize-scripts-ownership`

## Primary objective

Formaliser `scripts/ownership-index.md` comme registre canonique de ownership
pour chaque fichier actuellement liste par `rg --files scripts`, sans deplacer
ni modifier le comportement des scripts.

## Boundaries

- Couvrir exactement les fichiers presents sous `scripts/`.
- Reutiliser `backend/app/tests/unit/test_scripts_ownership.py` comme garde
  d'architecture existant.
- Persister les snapshots baseline et after dans la capsule.
- Renforcer le registre de guardrails si un invariant durable est cree.

## Non-goals

- Ne pas deplacer les scripts dans des sous-dossiers.
- Ne pas supprimer `stripe-listen-webhook.sh`.
- Ne pas modifier les routes API, le frontend, ni les contrats OpenAPI.
- Ne pas creer de registre concurrent sous `_condamad/`.

## Preflight checks

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Executer `git status --short`.
- Inventorier `scripts/` avec `rg --files scripts`.

## Write rules

- Modifier uniquement le registre, le garde de test, les preuves capsule et le
  registre de guardrails.
- Ne pas introduire de dependency.
- Toute commande Python doit etre lancee apres activation de `.venv`.

## Done conditions

- Chaque script inventorie a une ligne unique dans `scripts/ownership-index.md`.
- Le test d'ownership detecte les scripts absents ou dupliques.
- Les snapshots baseline et after sont identiques.
- Les validations ciblees et lint passent ou sont documentees.

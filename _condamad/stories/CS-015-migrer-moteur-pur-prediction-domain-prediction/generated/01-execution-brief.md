# Execution Brief

## Story key

`CS-015-migrer-moteur-pur-prediction-domain-prediction`

## Objectif primaire

Valider et finaliser la migration du moteur pur de prediction sous `backend/app/domain/prediction`, avec des consommateurs service pointant vers `app.domain.prediction` et sans dependance inverse API, infra, settings, services ou runtime LLM dans le domaine.

## Bornes

- Modifier uniquement les fichiers necessaires a CS-015.
- Ne pas recreer `backend/app/prediction`.
- Ne pas ajouter de facade, alias, wrapper ou re-export depuis `app.prediction`.
- Ne pas changer le comportement de calcul.
- Ne pas ajouter de dependance.

## Preflight requis

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Capturer `git status --short`.
- Capturer l'etat actuel des fichiers prediction avant toute modification.

## Regles d'ecriture

- Garder un seul owner canonique: `backend/app/domain/prediction`.
- Les services peuvent orchestrer et importer le domaine, mais le domaine ne doit pas importer les services.
- Les imports interdits sous `app/domain/prediction` sont bloquants: `fastapi`, `sqlalchemy`, `Session`, `settings`, `AIEngineAdapter`, `app.infra`, `app.api`, `app.services`.

## Definition de termine

- Les AC1 a AC5 sont traces avec preuves code et validation.
- Les tests moteur cibles passent.
- Les scans d'import legacy et de dependances interdites sont zero-hit hors gardes attendues.
- Les inventaires avant/apres sont persistants.
- `_condamad/stories/story-status.md` passe CS-015 a `ready-to-review`.

## Conditions d'arret

- Une dependance API, infra ou service est necessaire dans le domaine pour conserver le comportement.
- Une validation requise echoue sans correction sure dans le scope.
- Une modification destructive hors scope serait necessaire.

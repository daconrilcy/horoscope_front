# Execution Brief

## Story key

`align-prompt-generation-story-validation-paths`

## Primary objective

Aligner les chemins de validation actifs des stories prompt-generation avec les fichiers pytest reellement collectes sous `backend/app/tests/unit`.

## Boundaries

- Modifier uniquement les artefacts `_condamad/stories` necessaires.
- Ne pas modifier le code applicatif backend ou frontend.
- Ne pas deplacer ni dupliquer les tests existants.
- Conserver les preuves historiques si elles sont explicitement classees comme historiques.

## Preflight checks

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Capturer `git status --short`.
- Scanner les trois chemins obsoletes listes par la story.

## Write rules

- Remplacer les commandes actives obsoletes par les chemins `app/tests/unit`.
- Ne pas creer de fichiers sous `backend/tests/unit`.
- Ajouter un audit persistant avant/apres.
- Completer la preuve finale avant de marquer la story prete pour review.

## Done conditions

- AC1 a AC4 ont une preuve documentaire et une validation.
- Les tests cibles passent depuis `backend/` apres activation du venv.
- Les scans des anciens chemins sont classes.
- `generated/10-final-evidence.md` est complet.

## Halt conditions

- Un chemin obsolete reste actif sans classification.
- Un test cible n'est pas collectable depuis `backend/`.
- Une correction demande de modifier du code applicatif, de creer une dependance ou de dupliquer un test.

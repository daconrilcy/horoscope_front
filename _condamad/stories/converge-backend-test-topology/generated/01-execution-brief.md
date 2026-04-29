# Execution Brief

## Story key

`converge-backend-test-topology`

## Objective

Converger la topologie des tests backend vers des racines documentees, collectees par pytest et protegees par une garde deterministe.

## Boundaries

- Modifier uniquement la topologie et les guards de tests backend.
- Conserver les assertions metier des tests deplaces.
- Ne pas traiter la convergence des fixtures DB.
- Ne pas creer de nouvelle dependance ni de `requirements.txt`.

## Preflight

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Capturer `git status --short`.
- Capturer l'inventaire des racines avant/apres.

## Write rules

- Utiliser `backend/pyproject.toml` comme source de configuration pytest.
- Utiliser `_condamad/stories/converge-backend-test-topology/backend-test-topology.md` comme registre de topologie.
- Interdire les nouveaux tests embarques sous `backend/app/**/tests` hors `backend/app/tests`.

## Done conditions

- Les racines autorisees sont documentees.
- Aucun fichier de test backend n'est hors racine approuvee.
- La collecte pytest couvre les racines configurees.
- Une garde echoue si la documentation, la config pytest ou l'inventaire divergent.

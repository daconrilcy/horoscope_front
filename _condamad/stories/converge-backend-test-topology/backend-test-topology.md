# Backend Test Topology

Ce document est l'evidence historique de la story
`converge-backend-test-topology`. Il n'est plus le registre canonique actif.

Le registre canonique actif est:
`_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md`.

Toute modification de topologie doit etre portee dans ce registre canonique,
dans `backend/pyproject.toml`, puis validee par
`backend/app/tests/unit/test_backend_test_topology.py`.

## Racines pytest standard

| Racine | Responsabilite | Statut |
|---|---|---|
| `app/tests` | Tests applicatifs backend collectes par defaut, incluant les sous-racines unit, integration et regression. | Historique - voir registre canonique actif |
| `tests/evaluation` | Suite d'evaluation des prompts et sorties LLM. | Historique - voir registre canonique actif |
| `tests/integration` | Suite d'integration backend transverse hors package applicatif. | Historique - voir registre canonique actif |
| `tests/llm_orchestration` | Suite LLM orchestration et guards historiques associes. | Historique - voir registre canonique actif |
| `tests/unit` | Suite unitaire backend transverse hors package applicatif. | Historique - voir registre canonique actif |

## Regles

- Tout fichier `test_*.py` ou `*_test.py` sous `backend/` doit etre sous l'une des racines pytest standard ci-dessus.
- Aucun nouveau dossier `tests` ne doit etre ajoute sous `backend/app/**` hors `backend/app/tests` et exceptions documentees.
- Toute suite opt-in doit etre ajoutee explicitement ici avec une justification et une condition de permanence ou d'expiration.
- Les racines documentees doivent etre identiques a `tool.pytest.ini_options.testpaths` dans `backend/pyproject.toml`.

## Suites opt-in

Aucune suite opt-in active.

## Hors scope connu

`backend/app/domain/llm/prompting/tests/__init__.py` reste un module non-test historique contenant du code de registre. Il n'est pas une racine de tests approuvee, et aucun fichier de test ne doit etre ajoute dans ce dossier.

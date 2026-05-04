# Pourquoi `backend/docs` existe

Ce dossier n'est pas un espace de documentation generale. Il sert a gouverner
les artefacts documentaires qui participent aux gardes backend.

Les artefacts lus ou compares par les tests et validateurs sont regroupes dans
`guarded-artifacts/`. Si un document est une note humaine, une decision
historique ou une explication produit, il doit vivre dans `docs/` a la racine
du projet.

## En une phrase

| Fichier | A quoi il sert vraiment | Pourquoi il reste ici |
|---|---|---|
| `ownership-index.md` | Empêcher que `backend/docs/` redevienne un fourre-tout. | Le test `app/tests/unit/test_backend_docs_ownership.py` le lit pour verifier que chaque fichier du dossier est classe. |
| `guarded-artifacts/llm-model-structure.md` | Montrer la structure canonique actuelle des modeles LLM. | Le test `tests/unit/test_llm_canonical_perimeter.py` compare ce document avec les modeles backend LLM. |
| `guarded-artifacts/llm-db-cleanup-registry.json` | Lister les objets DB LLM et les compatibilites encore tolerees. | Le validateur `app.ops.llm.db_cleanup_validator.LlmDbCleanupValidator` charge ce JSON depuis ce chemin. |

## Ce que chaque fichier protege

### `ownership-index.md`

Ce fichier est le registre de controle du dossier. Il indique, pour chaque
fichier encore present ici:

- qui en est responsable;
- s'il est genere, executable ou seulement documentaire;
- quel test doit echouer si le fichier devient incoherent.

Sa presence evite qu'un nouveau fichier soit ajoute sous `backend/docs/` sans
decision explicite. Le test d'ownership compare l'inventaire reel du dossier aux
lignes de ce registre.

### `guarded-artifacts/llm-model-structure.md`

Ce fichier n'est pas une note de conception. C'est un rendu de la structure LLM
attendue: tables, relations, contraintes, champs autoritaires et compatibilites
tolerees.

Il reste sous `backend/docs/guarded-artifacts/` parce qu'il est lie au code
backend qui definit le perimetre LLM canonique. Quand les modeles LLM changent,
la garde `tests/unit/test_llm_canonical_perimeter.py` permet de detecter si ce
document est devenu obsolete.

### `guarded-artifacts/llm-db-cleanup-registry.json`

Ce fichier est un registre de validation, pas une documentation narrative. Il
decrit les objets DB LLM, les migrations relues, et les acces legacy encore
autorises de facon bornee.

Il reste ici parce que `LlmDbCleanupValidator` le charge directement depuis
`backend/docs/guarded-artifacts/llm-db-cleanup-registry.json`. Le deplacer sans
changer le validateur casserait la garde d'integration
`tests/integration/test_llm_db_cleanup_registry.py`.

## Pourquoi les autres documents ont ete deplaces

Les notes humaines LLM et la note historique entitlement ne sont plus dans ce
dossier parce qu'elles ne sont pas des sources de verite executables:

- les notes LLM humaines sont sous `docs/llm/`;
- la note historique entitlement est sous `docs/architecture/`.

Cette separation evite de donner un statut canonique a de la prose qui ne doit
pas piloter le runtime.

## Regle simple pour l'avenir

Avant d'ajouter un fichier ici, il faut pouvoir repondre oui a au moins une de
ces questions:

- Un test backend lit-il ce fichier a un chemin precis?
- Un validateur backend le charge-t-il directement?
- Le fichier est-il genere ou compare depuis une source backend executable?

Si la reponse est oui et que le fichier est un artefact lu ou compare, il doit
aller dans `backend/docs/guarded-artifacts/`. Si la reponse est non, le fichier
doit aller dans `docs/`, pas dans `backend/docs/`.

## Gardes associees

Depuis `backend/`, apres activation du venv:

```powershell
pytest -q app/tests/unit/test_backend_docs_ownership.py
pytest -q tests/unit/test_llm_canonical_perimeter.py
pytest -q tests/integration/test_llm_db_cleanup_registry.py
```

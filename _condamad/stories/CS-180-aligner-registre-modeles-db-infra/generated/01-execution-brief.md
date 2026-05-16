# Execution Brief

## Story

- Key: `CS-180-aligner-registre-modeles-db-infra`
- Source: `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/00-story.md`
- Objective: aligner les tables applicatives SQLite, les fichiers de modeles SQLAlchemy et `Base.metadata`.

## Boundaries

- In scope: registre `backend/app/infra/db/models`, chargement global `Base.metadata`, garde pytest DB/model registry, preuves avant/apres, classification exacte des exceptions.
- Out of scope: suppression de tables SQLite, migration destructive, changement API/OpenAPI, modification du scheduler APScheduler, refonte des modeles LLM.

## Write Rules

- Corriger uniquement le chargement des modeles necessaire a `Base.metadata`.
- Garder le registre LLM separe; ne pas dupliquer ses exports dans le registre racine non-LLM.
- Ne pas ajouter d'allowlist large ou de wildcard.
- Ne pas creer de dependance ni de `requirements.txt`.

## Completion Definition

- `flagged_contents` est present dans `Base.metadata.tables`.
- Toute table SQLite sans modele est classifiee exactement.
- Toute table avec modele est chargee dans `Base.metadata`.
- Les tests cibles, lint et scans de non-destruction sont executes et documentes.

## Halt Conditions

- Une correction necessite une migration destructive.
- Une table applicative non classifiee reste hors modele ou hors metadata.
- Une validation obligatoire echoue sans correctif sur.

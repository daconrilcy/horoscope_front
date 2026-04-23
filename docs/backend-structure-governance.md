# Gouvernance de structure backend

Ce document fixe les dossiers fondationnels autorises pour le backend et la
convention de nommage a conserver apres la convergence de la story 70-18.

## Regles

- Le namespace canonique pour l infrastructure technique est `backend/app/infra/`.
- Le namespace `backend/app/infrastructure/` est deprecie et interdit.
- Aucun nouveau dossier de base sous `backend/` ou `backend/app/` ne doit etre ajoute
  sans accord explicite de l utilisateur.
- Toute nouvelle couche technique doit d abord etre rattachee a un dossier existant
  quand sa responsabilite correspond deja a une couche autorisee.
- Les imports applicatifs doivent viser le namespace canonique reel, sans shim durable
  ni alias de compatibilite pour masquer un ancien chemin.

## Dossiers racines backend

| Dossier | Statut | Responsabilite |
| --- | --- | --- |
| `backend/app/` | canonique | Code applicatif FastAPI. |
| `backend/migrations/` | canonique | Migrations Alembic. |
| `backend/scripts/` | canonique | Scripts operatoires et seeds backend. |
| `backend/tests/` | canonique | Tests backend hors package applicatif. |
| `backend/tools/` | tolere | Outillage local de developpement. |
| `backend/docs/` | tolere | Documentation technique locale au backend. |
| `backend/artifacts/` | tolere | Artefacts generes ou rapports techniques. |
| `backend/logs/` | tolere | Journaux locaux non applicatifs. |

## Dossiers autorises sous `backend/app/`

| Dossier | Statut | Responsabilite |
| --- | --- | --- |
| `api/` | canonique | Routeurs, schemas de surface et dependances HTTP. |
| `core/` | canonique | Configuration, securite, horloge, RBAC et concerns transverses. |
| `domain/` | canonique | Entites, politiques et logique metier pure. |
| `services/` | canonique | Cas d usage applicatifs. |
| `infra/` | canonique | DB, repositories, clients externes et integration technique. |
| `application/` | tolere | Adaptateurs applicatifs existants a conserver tant qu ils ne dupliquent pas `services/`. |
| `integrations/` | tolere | Integrations metier existantes lorsque `infra/` ne porte pas le meme role. |
| `jobs/` | tolere | Jobs applicatifs planifies. |
| `ops/` | tolere | Surfaces et helpers operationnels. |
| `prediction/` | tolere | Sous-domaine historique de prediction. |
| `resources/` | tolere | Ressources embarquees. |
| `schemas/` | tolere | Schemas transverses existants. |
| `startup/` | tolere | Initialisation applicative explicite. |
| `templates/` | tolere | Templates backend. |
| `tests/` | tolere | Tests historiques embarques dans le package applicatif. |
| `ai_engine/` | a converger | Ancien sous-systeme technique a ne pas etendre si une couche canonique existe. |
| `infrastructure/` | interdit | Doublon de `infra/`. |

## Garde-fous

Le test `backend/tests/unit/test_story_70_18_backend_structure_guard.py` controle :

- la liste des dossiers directs autorises sous `backend/` ;
- la liste des dossiers directs classes sous `backend/app/` ;
- l absence du dossier et des imports `app.infrastructure`.

Pour approuver un nouveau dossier racine, mettre a jour ce document et le garde-fou
dans la meme evolution, avec la justification d architecture associee.

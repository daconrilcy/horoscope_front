# Story 70.18b: Continuer le cleanup de la génération de prompts LLM

Status: done

## Story

As a Platform Architect,  
I want finir de reclasser et simplifier les briques backend qui participent à la génération LLM,  
so that le runtime de prompting reste canonique, DRY, lisible et sans reliquat legacy.

## Contexte

La story 70.18 a refermé une large partie de la gouvernance structurelle backend, mais un sous-périmètre reste ambigu côté génération LLM :

- `backend/app/ai_engine/` mélange encore des responsabilités `api`, `core`, `infra`, `domain` et du legacy de migration ;
- `backend/app/infra/llm/client.py` est explicitement déprécié et doit disparaître ;
- `backend/app/infra/llm/anonymizer.py` porte à la fois des motifs techniques réutilisables et une logique applicative d’anonymisation ;
- `backend/app/schemas/audit_details.py` est hors de sa couche naturelle ;
- plusieurs services applicatifs liés à la génération LLM vivent encore à plat sous `backend/app/services/`.

Cette story vise un nettoyage strictement DRY, sans refactor cosmétique gratuit et sans réintroduire de wrappers ambiguës.

## Acceptance Criteria

1. `backend/app/ai_engine/` n’est plus une zone fourre-tout : chaque brique utile est relocalisée selon sa responsabilité canonique.
2. `backend/app/infra/llm/client.py` est supprimé sans consommateur nominal restant.
3. Les motifs regex de détection sensible réutilisables sont centralisés en `core`.
4. L’anonymisation LLM vit dans une couche applicative cohérente avec ses consommateurs métier.
5. `backend/app/schemas/audit_details.py` est relocalisé dans un namespace audit canonique.
6. Les services applicatifs de génération LLM sont regroupés sous un sous-dossier dédié dans `backend/app/services/`.
7. Aucun nouveau doublon ou shim durable n’est introduit.
8. Les imports du code nominal pointent vers les nouveaux chemins canoniques.
9. Les tests ciblés des fichiers touchés sont mis à jour et exécutés dans le venv.

## Tasks / Subtasks

- [x] Reclasser les briques utiles de `ai_engine` vers `api`, `core`, `domain` et `infra`.
- [x] Préparer la suppression de `infra/llm/client.py`.
- [x] Extraire les motifs sensibles partagés dans `core`.
- [x] Déplacer l’anonymisation vers `services/llm_generation`.
- [x] Relocaliser les détails d’audit vers `domain/audit`.
- [x] Regrouper les services de génération LLM sous `services/llm_generation`.
- [x] Mettre à jour et exécuter les tests ciblés du périmètre touché.

## References

- [Source: AGENTS.md]
- [Source: _bmad-output/implementation-artifacts/70-18-cleaner-la-structure-backend-et-converger-les-namespaces-techniques.md]
- [Source: docs/2026-04-21-audit-prompts-backend-post-story-70-15-v2.md]

# Source checklist CS-264

## Builder reel selectionne

- Builder: `AINarrativeInputBuilder.from_interpretation_input`.
- Projection persistee: `ai_narrative_input` / `ai_narrative_input.v1`.
- Raison: aucun builder `structured_facts_v1`, `beginner_summary_v1` ou `client_interpretation_projection_v1` n'est present dans ce snapshot.

## Reutilisation obligatoire

- Hash canonique: `backend/app/domain/astrology/projections/projection_hash.py`.
- Persistance: `backend/app/infra/db/models/projection_persistence.py`.
- Repository: `backend/app/infra/db/repositories/projection_repository.py`.
- Service: `backend/app/services/projection_persistence_service.py`.
- Versions source: `AINarrativeSourceVersions`, converti par la normalisation JSON canonique partagee.

## Frontieres confirmees

- Aucun builder fictif ou payload synthetique n'est ajoute.
- Aucune route publique, exposition OpenAPI, modification frontend ou client genere n'est ajoutee.
- Les lectures repository exigent `projection_type`, `projection_version` et `ProjectionAccessScope`.

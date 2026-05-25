# CS-296 source checklist

- Story cible lue: `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/00-story.md`.
- Brief source verifie: `_story_briefs/cs-296-implement-replay-snapshot-v1-service-retention-purge.md`.
- Registre verifie: ligne `CS-296`, path cible et brief source correspondent.
- CS-295 pris en compte: stockage `LlmReplaySnapshotModel`, retention 30 jours et purge existante.
- Owners inspectes: `observability_service.py`, `replay_service.py`, `audit_service.py`, `safe_details.py`, modele `llm_observability.py`.
- Politique retenue: service canonique interne; purge automatique physique des expires; purge manuelle par tombstone de payload sans migration.

# DB Table Exception Register

Chaque ligne ci-dessous est une exception exacte. La garde pytest refuse les motifs
generiques et exige que les tables conservees soient nommees individuellement.

| Table | Classification | Reason | Status |
|---|---|---|---|
| `_alembic_tmp_astrologer_profiles` | historique locale | Table temporaire Alembic locale detectee dans `backend/horoscope.db`; suppression hors scope car destructive et decision migration separee requise. | Exception exacte bloquee hors CS-180. |
| `alembic_version` | technique | Table de version Alembic, non applicative. | Exception technique permanente. |
| `apscheduler_jobs` | technique | Table geree par `SQLAlchemyJobStore(url=settings.database_url)` dans `backend/app/core/scheduler.py`. | Exception technique permanente tant que le scheduler utilise APScheduler. |
| `llm_prompt_version_fallback_archives` | historique LLM | Table d'archive de migration LLM vide, sans modele applicatif voulu dans cette story. | A revalider par une story dediee aux archives LLM. |

# SQL public email before

```text
686:| `app/api/v1/routers/public/email.py` | 10 | `import_from` | `sqlalchemy:update` | `<module>` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
687:| `app/api/v1/routers/public/email.py` | 11 | `import_from` | `sqlalchemy.orm:Session` | `<module>` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
688:| `app/api/v1/routers/public/email.py` | 16 | `import_from` | `app.infra.db.models.user:UserModel` | `<module>` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
689:| `app/api/v1/routers/public/email.py` | 17 | `import_from` | `app.infra.db.session:get_db_session` | `<module>` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
690:| `app/api/v1/routers/public/email.py` | 32 | `dependency` | `Depends(get_db_session)` | `unsubscribe` | Dette F-002 existante d injection de session DB dans les routeurs API. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
691:| `app/api/v1/routers/public/email.py` | 56 | `session_call` | `db.execute` | `unsubscribe` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
692:| `app/api/v1/routers/public/email.py` | 59 | `session_call` | `db.commit` | `unsubscribe` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
```

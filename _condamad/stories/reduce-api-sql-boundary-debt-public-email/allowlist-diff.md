# Allowlist diff

```diff
diff --git a/_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md b/_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md
index c49cb9d2..791351bc 100644
--- a/_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md
+++ b/_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md
@@ -683,13 +683,6 @@
 | `app/api/v1/routers/public/consultations.py` | 98 | `session_call` | `db.rollback` | `generate_consultation` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
 | `app/api/v1/routers/public/consultations.py` | 113 | `session_call` | `db.rollback` | `generate_consultation` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
 | `app/api/v1/routers/public/consultations.py` | 131 | `session_call` | `db.commit` | `generate_consultation` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
-| `app/api/v1/routers/public/email.py` | 10 | `import_from` | `sqlalchemy:update` | `<module>` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
-| `app/api/v1/routers/public/email.py` | 11 | `import_from` | `sqlalchemy.orm:Session` | `<module>` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
-| `app/api/v1/routers/public/email.py` | 16 | `import_from` | `app.infra.db.models.user:UserModel` | `<module>` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
-| `app/api/v1/routers/public/email.py` | 17 | `import_from` | `app.infra.db.session:get_db_session` | `<module>` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
-| `app/api/v1/routers/public/email.py` | 32 | `dependency` | `Depends(get_db_session)` | `unsubscribe` | Dette F-002 existante d injection de session DB dans les routeurs API. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
-| `app/api/v1/routers/public/email.py` | 56 | `session_call` | `db.execute` | `unsubscribe` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
-| `app/api/v1/routers/public/email.py` | 59 | `session_call` | `db.commit` | `unsubscribe` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
 | `app/api/v1/routers/public/entitlements.py` | 6 | `import_from` | `sqlalchemy:select` | `<module>` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
 | `app/api/v1/routers/public/entitlements.py` | 7 | `import_from` | `sqlalchemy.orm:Session,selectinload` | `<module>` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
 | `app/api/v1/routers/public/entitlements.py` | 12 | `import_from` | `app.infra.db.models.billing:BillingPlanModel` | `<module>` | Dette F-002 existante capturee avant la garde SQL routeur. | Temporaire; aucune croissance autorisee, reduction progressive par stories dediees. |
```

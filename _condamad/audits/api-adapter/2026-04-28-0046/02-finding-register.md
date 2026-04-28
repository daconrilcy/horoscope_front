# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | boundary-violation | backend/app/api | E-009, E-010 | La frontière API reste propriétaire de 848 usages directs SQL/session ou dépendances DB, même si leur croissance est désormais bloquée par allowlist exacte. | Découper une série de stories de réduction par routeur ou flux métier, en retirant chaque entrée extraite de `router-sql-allowlist.md`. | yes |
| F-002 | Medium | High | legacy-surface | backend/app/api | E-008, E-012 | L'URL publique historique `/api/email/unsubscribe` reste active hors `/v1`; elle est gouvernée mais pas convergée vers un contrat canonique. Le caractère public est normal pour un désabonnement email, mais le token en query string impose des durcissements HTTP/logging. | Décider si l'URL doit rester une exception permanente ou créer une migration vers une route canonique avec compatibilité bornée. Dans tous les cas, durcir la route: réponse générique non énumérante, `Cache-Control: no-store`, interdiction de journaliser le token/query string, et décision explicite sur `GET` direct vs confirmation `GET` + action `POST`. | yes |
| F-003 | Info | High | duplicate-responsibility | backend/app/api | E-005, E-006, E-010 | Le risque précédent de double propriétaire admin LLM observability est corrigé et protégé par tests d'architecture. | Conserver `RG-007` et les tests de propriétaire runtime lors des évolutions admin LLM. | no |
| F-004 | Info | High | route-architecture-convergence | backend/app/api | E-007, E-008, E-010 | Les montages hors registre v1 sont maintenant structurés dans `API_ROUTE_MOUNT_EXCEPTIONS` et vérifiés contre le runtime. | Conserver le registre d'exceptions comme unique point d'entrée pour toute route hors registre API v1. | no |
| F-005 | Info | High | dependency-direction-violation | backend/app/api | E-003, E-004, E-010 | Aucun import inverse vers `app.api` ni fuite de types FastAPI dans les couches non-API auditées n'a été détecté. | Maintenir les scans et gardes existants dans le flux CI. | no |

## F-001 API Persistence Debt Remains Active But Guarded

- Severity: High
- Confidence: High
- Category: boundary-violation
- Domain: backend/app/api
- Evidence: E-009, E-010
- Expected rule: La couche API doit rester un adaptateur HTTP strict et ne pas posséder directement la persistance, les sessions DB ou les modèles infra.
- Actual state: `router-sql-allowlist.md` inventorie 848 entrées SQL/session/dépendance DB encore actives dans `backend/app/api`, et le test `test_api_sql_boundary_debt_matches_exact_allowlist` impose une correspondance exacte.
- Impact: La frontière API reste propriétaire de 848 usages directs SQL/session ou dépendances DB, même si leur croissance est désormais bloquée par allowlist exacte.
- Recommended action: Découper une série de stories de réduction par routeur ou flux métier, en retirant chaque entrée extraite de `router-sql-allowlist.md`.
- Story candidate: yes
- Suggested archetype: api-adapter-boundary-convergence

## F-002 Public Email Unsubscribe Historical URL Remains Active

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: backend/app/api
- Evidence: E-008, E-012
- Expected rule: Les surfaces historiques doivent être supprimées ou gouvernées par une décision explicite, un propriétaire canonique et une stratégie de migration.
- Actual state: `API_ROUTE_MOUNT_EXCEPTIONS` conserve `/api/email/unsubscribe` avec la décision "Suppression uniquement via une story dediee de migration d URL".
- Impact: L'URL publique historique `/api/email/unsubscribe` reste active hors `/v1`; elle est gouvernée mais pas convergée vers un contrat canonique. Le risque principal n'est pas son accessibilité publique, qui est attendue pour un lien email non authentifié, mais l'exposition du token dans l'URL et l'action d'état déclenchée par `GET`.
- Recommended action: Décider si l'URL doit rester une exception permanente ou créer une migration vers une route canonique avec compatibilité bornée. Ajouter au périmètre de la décision les durcissements suivants:
  - retourner une réponse générique si le token est valide mais l'utilisateur absent, afin de limiter l'énumération;
  - ajouter `Cache-Control: no-store` aux réponses de désabonnement;
  - vérifier que les logs applicatifs, reverse-proxy et analytics ne conservent pas le token ni la query string;
  - décider explicitement si le désabonnement reste une action `GET` directe ou passe par une confirmation `GET` suivie d'une action `POST`;
  - conserver l'expiration courte et la signature forte du token, et ne jamais accepter de désabonnement sans token signé.
- Follow-up implementation note: `backend/app/api/v1/routers/public/email.py` conserve le `GET` public pour compatibilité des emails déjà envoyés, ajoute `Cache-Control: no-store`, rend le cas utilisateur absent non énumérant pour un token signé valide, et évite de journaliser le détail d'exception susceptible de contenir des informations de requête.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal

## F-003 Admin LLM Observability Ownership Is Corrected

- Severity: Info
- Confidence: High
- Category: duplicate-responsibility
- Domain: backend/app/api
- Evidence: E-005, E-006, E-010
- Expected rule: Les routes admin LLM observability doivent être servies par un unique routeur canonique.
- Actual state: Les routes `/v1/admin/llm/call-logs`, `/dashboard`, `/replay` et `/call-logs/purge` sont servies par `app.api.v1.routers.admin.llm.observability`; le scan ciblé ne trouve plus de redéfinition dans `prompts.py`.
- Impact: Le risque précédent de double propriétaire admin LLM observability est corrigé et protégé par tests d'architecture.
- Recommended action: Conserver `RG-007` et les tests de propriétaire runtime lors des évolutions admin LLM.
- Story candidate: no
- Suggested archetype: no-story

## F-004 Route Registration Exceptions Are Now Structured

- Severity: Info
- Confidence: High
- Category: route-architecture-convergence
- Domain: backend/app/api
- Evidence: E-007, E-008, E-010
- Expected rule: Toute route hors registre API v1 doit être inventoriée dans un registre explicite, avec raison, condition et décision.
- Actual state: `route_exceptions.py` déclare les exceptions de montage; les tests vérifient les clés attendues, le runtime et les routes QA internes.
- Impact: Les montages hors registre v1 sont maintenant structurés dans `API_ROUTE_MOUNT_EXCEPTIONS` et vérifiés contre le runtime.
- Recommended action: Conserver le registre d'exceptions comme unique point d'entrée pour toute route hors registre API v1.
- Story candidate: no
- Suggested archetype: no-story

## F-005 Downstream Dependency Direction Remains Clean

- Severity: Info
- Confidence: High
- Category: dependency-direction-violation
- Domain: backend/app/api
- Evidence: E-003, E-004, E-010
- Expected rule: Les couches `services`, `domain`, `infra` et `core` ne doivent pas dépendre de `app.api`, et `services/domain` ne doivent pas importer FastAPI.
- Actual state: Les scans ciblés ne trouvent aucun import interdit.
- Impact: Aucun import inverse vers `app.api` ni fuite de types FastAPI dans les couches non-API auditées n'a été détecté.
- Recommended action: Maintenir les scans et gardes existants dans le flux CI.
- Story candidate: no
- Suggested archetype: no-story

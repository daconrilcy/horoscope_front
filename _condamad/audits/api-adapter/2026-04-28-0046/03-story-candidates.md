# Story Candidates

## SC-001 Reduce API SQL Boundary Debt By Bounded Router Batch

- Source finding: F-001
- Suggested story title: Réduire la dette SQL directe des routeurs API par lot borné
- Suggested archetype: api-adapter-boundary-convergence
- Primary domain: backend/app/api
- Required contracts: api-adapter-audit-contract.md, no-legacy-dry-audit-contract.md
- Draft objective: Extraire un premier lot d'usages SQL/session depuis les routeurs vers les services applicatifs ou repositories existants, sans changer les contrats HTTP.
- Must include: Choix d'un lot explicite, suppression des entrées correspondantes dans `router-sql-allowlist.md`, tests unitaires services, tests d'intégration routes, preuve que `test_api_sql_boundary_debt_matches_exact_allowlist` passe après réduction.
- Validation hints: `pytest -q app/tests/unit/test_api_router_architecture.py`; tests d'intégration des routes touchées; diff de `router-sql-allowlist.md`.
- Blockers: Décision de lot initial. Les meilleurs candidats restent les routeurs les plus denses: `admin/llm/prompts.py`, `admin/users.py`, `ops/entitlement_mutation_audits.py`, `public/billing.py`.

## SC-002 Decide Public Email Unsubscribe Route Canonicalization

- Source finding: F-002
- Suggested story title: Décider et cadrer la migration de `/api/email/unsubscribe`
- Suggested archetype: legacy-facade-removal
- Primary domain: backend/app/api
- Required contracts: api-adapter-audit-contract.md, no-legacy-dry-audit-contract.md
- Draft objective: Déterminer si l'URL historique de désabonnement doit rester une exception permanente, rester en attente de décision explicite, ou migrer vers une route canonique documentée.
- Must include: Décision produit/architecture, inventaire des liens email existants, compatibilité temporaire si migration, test OpenAPI/runtime et mise à jour de `API_ROUTE_MOUNT_EXCEPTIONS`. Inclure aussi les durcissements sécurité propres à une route publique à token: réponse non énumérante, `Cache-Control: no-store`, politique de logs sans token/query string, et décision `GET` direct vs confirmation `GET` + action `POST`.
- Validation hints: Test runtime des paths email; scan des templates/liens email; test d'absence de route historique si suppression décidée; tests d'erreurs qui ne révèlent pas inutilement l'existence utilisateur; test ou inspection des headers de cache.
- Blockers: La conservation ou suppression de l'URL peut impacter des emails déjà envoyés; décision utilisateur requise avant retrait.

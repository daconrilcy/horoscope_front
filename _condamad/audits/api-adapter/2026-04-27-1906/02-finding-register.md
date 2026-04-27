# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | duplicate-responsibility | backend/app/api | E-004, E-005, E-006, E-012 | Les endpoints d'observabilité LLM ont deux propriétaires de code actifs, mais seul l'ancien bloc dans `prompts.py` est exposé runtime. | Monter le routeur `admin.llm.observability` via le registre canonique, retirer les endpoints du routeur `prompts.py`, puis couvrir l'OpenAPI runtime. | yes |
| F-002 | High | High | boundary-violation | backend/app/api | E-007, E-008 | La couche API orchestre directement requêtes SQL, mutations et commits dans de nombreux routeurs au lieu de rester adaptateur HTTP vers services. | Extraire progressivement les use cases DB vers `services` ou repositories existants, en commençant par les routeurs les plus denses et les mutations. | yes |
| F-003 | Medium | High | route-architecture-convergence | backend/app/api | E-004, E-005, E-009 | Le registre v1 n'est pas la source unique réelle de montage: `email_router` et le routeur interne QA sont montés depuis `main.py`, avec exceptions codées dans le test. | Formaliser ces exceptions ou les converger vers un registre explicite par catégorie, avec garde runtime des routes conditionnelles. | yes |
| F-004 | Medium | Medium | missing-guard | backend/app/api | E-007, E-008, E-011 | Les gardes empêchent certains retours legacy et erreurs HTTP, mais pas la réintroduction d'orchestration SQL dans les routers. | Ajouter une garde AST ciblée qui interdit modèles DB, SQLAlchemy et commits dans les routeurs sauf allowlist temporaire documentée. | yes |
| F-005 | Info | High | dependency-direction-violation | backend/app/api | E-002, E-003 | Aucun import inverse `services/domain -> app.api` ni fuite FastAPI dans `services/domain` n'a été détecté. | Conserver les gardes existantes et les exécuter dans le flux CI standard. | no |

## F-001 Duplicate LLM Observability Route Owners

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: backend/app/api
- Evidence: E-004, E-005, E-006, E-012
- Expected rule: Un endpoint HTTP doit avoir un propriétaire routeur canonique unique, monté par le registre ou par une exception explicitement justifiée.
- Actual state: `backend/app/api/v1/routers/admin/llm/observability.py` déclare les endpoints `/call-logs`, `/dashboard`, `/replay` et `/call-logs/purge`, mais il n'est référencé ni par `registry.py` ni par `main.py`. Les mêmes paths existent encore dans `backend/app/api/v1/routers/admin/llm/prompts.py` et ce sont eux qui apparaissent dans l'OpenAPI runtime.
- Impact: Les endpoints d'observabilité LLM ont deux propriétaires de code actifs, mais seul l'ancien bloc dans `prompts.py` est exposé runtime.
- Recommended action: Monter le routeur `admin.llm.observability` via le registre canonique, retirer les endpoints du routeur `prompts.py`, puis couvrir l'OpenAPI runtime.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal

## F-002 API Routers Own Persistence Orchestration

- Severity: High
- Confidence: High
- Category: boundary-violation
- Domain: backend/app/api
- Evidence: E-007, E-008
- Expected rule: La couche API parse les requêtes HTTP, appelle des services applicatifs, puis mappe les réponses et erreurs. Elle ne doit pas posséder de requêtes SQL, transactions, commits ou règles de mutation.
- Actual state: Le scan AST détecte des opérations DB directes dans 39 routeurs. Exemples: `admin/llm/prompts.py` contient 40 opérations DB directes, `admin/content.py` 25 et `ops/entitlement_mutation_audits.py` 20. Le scan d'import confirme la dépendance directe aux modèles DB, `get_db_session` et SQLAlchemy.
- Impact: La couche API orchestre directement requêtes SQL, mutations et commits dans de nombreux routeurs au lieu de rester adaptateur HTTP vers services.
- Recommended action: Extraire progressivement les use cases DB vers `services` ou repositories existants, en commençant par les routeurs les plus denses et les mutations.
- Story candidate: yes
- Suggested archetype: api-adapter-boundary-convergence

## F-003 API v1 Registration Has Hard-Coded Main Exceptions

- Severity: Medium
- Confidence: High
- Category: route-architecture-convergence
- Domain: backend/app/api
- Evidence: E-004, E-005, E-009
- Expected rule: Les routeurs API v1 doivent être inventoriés par un propriétaire clair afin que la table de routes runtime corresponde au registre source.
- Actual state: `include_api_v1_routers(app)` est le montage principal, mais `main.py` monte aussi `email_router` hors registre et un routeur interne QA conditionnel. Le test d'architecture autorise ces exceptions au lieu de vérifier un registre secondaire ou une raison structurée.
- Impact: Le registre v1 n'est pas la source unique réelle de montage: `email_router` et le routeur interne QA sont montés depuis `main.py`, avec exceptions codées dans le test.
- Recommended action: Formaliser ces exceptions ou les converger vers un registre explicite par catégorie, avec garde runtime des routes conditionnelles.
- Story candidate: yes
- Suggested archetype: route-architecture-convergence

## F-004 Missing Guard Against Router-Level SQL

- Severity: Medium
- Confidence: Medium
- Category: missing-guard
- Domain: backend/app/api
- Evidence: E-007, E-008, E-011
- Expected rule: Les contraintes d'architecture importantes doivent être protégées par tests ou scripts pour éviter leur réintroduction.
- Actual state: Les tests d'architecture couvrent les imports de routeurs, les anciens modules d'erreurs et les fuites HTTP vers services, mais aucune garde ne bloque les requêtes SQL ou commits dans `backend/app/api/v1/routers`.
- Impact: Les gardes empêchent certains retours legacy et erreurs HTTP, mais pas la réintroduction d'orchestration SQL dans les routers.
- Recommended action: Ajouter une garde AST ciblée qui interdit modèles DB, SQLAlchemy et commits dans les routeurs sauf allowlist temporaire documentée.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening

## F-005 Downstream Dependency Direction Is Currently Clean

- Severity: Info
- Confidence: High
- Category: dependency-direction-violation
- Domain: backend/app/api
- Evidence: E-002, E-003
- Expected rule: `domain` et `services` ne doivent pas dépendre de `app.api` ni de types FastAPI.
- Actual state: Les scans ciblés ne trouvent aucun import `app.api` depuis `domain` ou `services`, ni usage de `fastapi`, `HTTPException` ou `JSONResponse` dans ces couches.
- Impact: Aucun import inverse `services/domain -> app.api` ni fuite FastAPI dans `services/domain` n'a été détecté.
- Recommended action: Conserver les gardes existantes et les exécuter dans le flux CI standard.
- Story candidate: no
- Suggested archetype: no-story

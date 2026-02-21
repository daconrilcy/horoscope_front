---
stepsCompleted:
  - 1
  - 2
  - 3
  - 4
  - 5
  - 6
  - 7
  - 8
inputDocuments:
  - 'C:\dev\horoscope_front\_bmad-output\planning-artifacts\prd.md'
  - 'C:\dev\horoscope_front\_bmad-output\planning-artifacts\prd-validation-report.md'
  - 'C:\dev\horoscope_front\docs\recherches astro\00_Orientation_et_reglages.md'
  - 'C:\dev\horoscope_front\docs\recherches astro\01_Langage_astro_signes_planetes_maisons.md'
  - 'C:\dev\horoscope_front\docs\recherches astro\02_Aspects_dignites_et_etat_des_planetes.md'
  - 'C:\dev\horoscope_front\docs\recherches astro\03_Methode_de_lecture_natal.md'
  - 'C:\dev\horoscope_front\docs\recherches astro\04_Transits_pratique.md'
  - 'C:\dev\horoscope_front\docs\recherches astro\05_Revolution_solaire_pratique.md'
  - 'C:\dev\horoscope_front\docs\recherches astro\06_Progressions_secondaires_option.md'
  - 'C:\dev\horoscope_front\docs\recherches astro\07_Synastrie_option.md'
  - 'C:\dev\horoscope_front\docs\recherches astro\08_Calculs_donnees_ephemerides.md'
  - 'C:\dev\horoscope_front\docs\recherches astro\09_Checklists_et_grilles_de_restitution.md'
  - 'C:\dev\horoscope_front\docs\recherches astro\README.md'
workflowType: 'architecture'
project_name: 'horoscope_front'
user_name: 'Cyril'
date: '2026-02-17T22:52:34+01:00'
lastStep: 8
status: 'complete'
completedAt: '2026-02-17T23:09:49+01:00'
---
# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._
## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
Le produit couvre 42 capacités structurées autour d’un noyau métier astrologique et d’une application web conversationnelle. Le moteur astrologique est explicitement positionné comme prérequis fondation (Phase 0), avant les capacités applicatives MVP. Le MVP simplifié cible un flux B2C centré sur onboarding natal -> génération du thème -> chat astrologue, avec monétisation initiale simple. Les capacités post-MVP étendent vers multi-profils, offres avancées et API B2B.

**Non-Functional Requirements:**
Les NFR qui orientent fortement l’architecture sont: confidentialité/sécurité des données personnelles, traçabilité des résultats astrologiques par version de règles/données, expérience conversationnelle fluide, disponibilité 24/7, accessibilité WCAG 2.1 AA, et capacité de montée en charge vers l’objectif business (~2000 payants). Le rapport de validation souligne un besoin de formalisation plus stricte de la mesurabilité de certains NFR.

**Scale & Complexity:**
Le projet combine un cœur de calcul symbolique spécialisé, une couche conversationnelle LLM, et une application produit monétisée. Cette combinaison crée une complexité élevée malgré un MVP fonctionnellement simplifié.

- Primary domain: full-stack web application with astrology computation core
- Complexity level: high
- Estimated architectural components: 10-14

### Technical Constraints & Dependencies

Le moteur astrologique dépend d’un référentiel métier explicite (tropical occidental, géocentrique, maisons Placidus avec contrôles Whole Sign/Equal, orbes conservateurs, nœud vrai). La fiabilité des sorties dépend de la qualité des données de naissance (heure/fuseau/DST/lieu), des conversions temporelles (UT/JD), et de la robustesse des calculs d’angles/aspects/maisons. Les dépendances externes incluent: éphémérides/bibliothèques de calcul astronomique, fournisseur(s) LLM, et composants de paiement/abonnement.

### Cross-Cutting Concerns Identified

- Security & privacy by design (chiffrement transit/repos, anonymisation LLM, droits RGPD)
- Traceability & versioning (règles de calcul + référentiels + audit des sorties)
- AI response governance (garde-fous hors-scope, fallback, monitoring qualité)
- Observability & operations (métriques produit, incidents, rollback config)
- Data quality controls (validation des entrées naissance, contrôles anti-erreur)
- Product consistency (alignement entre logique astrologique, restitution et conversation)
## Starter Template Evaluation

### Primary Technology Domain

Full-stack web application (backend API + frontend SPA) avec noyau métier de calcul astrologique.

### Starter Options Considered

1. **FastAPI Full-Stack Template (official)**
   - FastAPI + React + SQLModel + PostgreSQL + Docker + JWT + CI.
   - Très complet, mais plus lourd que le MVP simplifié et impose une stack large dès le départ.

2. **Split Starter (recommended for this project)**
   - Backend dédié (FastAPI) + Frontend dédié (React/Vite TS) dans monorepo.
   - Meilleur contrôle pour isoler le moteur astrologique en module fondation (Phase 0).
   - Plus aligné avec le MVP simplifié et la stratégie de montée progressive.

### Selected Starter: Split Starter (FastAPI backend + Vite React frontend)

**Rationale for Selection:**
- Respect strict des contraintes du projet (Python 3.13 + React).
- Permet de construire le moteur astrologique comme composant central indépendant.
- Évite le sur-embarquement (template full-stack trop chargé pour le scope MVP initial).
- Réduit le risque d’architecture couplée trop tôt.

**Initialization Commands:**

```bash
# Frontend (Vite + React + TypeScript)
npm create vite@latest frontend -- --template react-ts

# Backend (uv project + FastAPI)
uv init backend --app
cd backend
uv add "fastapi[standard]"
```

**Run command (backend dev):**

```bash
cd backend
uv run fastapi dev main.py
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
- Backend Python (uv-managed project), frontend TypeScript + React.

**Styling Solution:**
- UI kit custom leger base sur Tailwind CSS + shadcn/ui (primitives Radix), aligne avec la specification UX.

**Build Tooling:**
- Vite côté frontend; tooling Python moderne via uv côté backend.

**Testing Framework:**
- Non imposé automatiquement (sera fixé en décisions architecture: pytest, vitest, etc.).

**Code Organization:**
- Monorepo à deux apps (`backend/`, `frontend/`) + module métier astrologique clairement isolé côté backend.

**Development Experience:**
- Hot reload frontend (Vite), dev server FastAPI, séparation claire des responsabilités.

**Note:** Project initialization with these commands should be the first implementation story.
## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- PostgreSQL comme base principale.
- Redis active des le MVP pour cache/rate-limit support.
- Alembic pour migrations DB.
- Pydantic + SQLAlchemy comme socle modele/validation.
- Auth JWT access+refresh.
- RBAC minimal MVP: user, support, ops.
- API REST versionnee (/v1) avec rate limiting global + par user/plan.
- Front state: TanStack Query + Zustand.
- Forms: React Hook Form + Zod.
- Deploiement initial: Docker Compose single host.
- Observabilite MVP: logs structures + metriques + erreurs.

**Important Decisions (Shape Architecture):**
- UI kit custom leger (Tailwind CSS + shadcn/ui + primitives Radix) pour MVP.
- Chiffrement explicite des donnees sensibles en plus du transit/repos standard.
- Pas de GitHub Actions au demarrage (CI/CD manuel/alternatif initial).

**Deferred Decisions (Post-MVP):**
- Pipeline CI/CD industrialise.
- Orchestration multi-host.
- Optimisations de scalabilite avancee et separation de services.

### Data Architecture

- **Database:** PostgreSQL (major stable courante recommandee: 17/18 selon politique d upgrade).
- **ORM/Data Layer:** SQLAlchemy 2.x + Pydantic 2.x.
- **Migrations:** Alembic.
- **Cache & shared counters:** Redis (sessions techniques, quotas, rate-limits, cache calculs).
- **Data governance:** versioning explicite des referentiels astro et des regles de calcul.

### Authentication & Security

- **Authentication:** JWT access + refresh.
- **Authorization:** RBAC minimal (user, support, ops) des MVP.
- **Security controls:** chiffrement transit/repos + chiffrement applicatif des champs sensibles.
- **Privacy:** anonymisation des payloads envoyes aux LLM + audit des actions sensibles.
- **API protection:** rate limiting global et par user/plan.

### API & Communication Patterns

- **Style:** REST.
- **Versioning:** prefixe /v1.
- **Error model:** schema d erreurs unifie (codes + messages + correlation).
- **Contracts:** OpenAPI natif FastAPI comme source de verite.
- **Communication:** backend modulaire interne + cache Redis pour concerns transverses.

### Frontend Architecture

- **Server state:** TanStack Query v5.
- **Client state:** Zustand v5.
- **Forms/validation:** React Hook Form v7 + Zod v4.
- **UI strategy:** custom leger implemente avec Tailwind CSS + shadcn/ui (primitives Radix), composants orientes accessibilite (WCAG 2.1 AA cible).
- **Runtime:** React + Vite + TypeScript.

### Offline Strategy

- **MVP scope:** mode offline en lecture seule des derniers echanges deja synchronises.
- **Client approach (MVP):** service worker minimal + cache local des ressources statiques et des dernieres conversations consultees.
- **Write behavior (MVP):** envoi de message desactive hors ligne avec feedback explicite et reprise automatique a reconnexion initiee par l utilisateur.
- **Data integrity:** aucune ecriture metier definitive en mode offline au MVP pour eviter les conflits de synchronisation.
- **Post-MVP path:** file d attente locale (outbox) avec retry idempotent et resolution de conflits horodatage/version.

### Infrastructure & Deployment

- **Initial deployment:** Docker Compose single host.
- **CI/CD:** GitHub Actions non retenu a ce stade.
- **Observability baseline:** logs structures, metriques techniques, collecte d erreurs.
- **Environment strategy:** separation claire dev/staging/prod via variables d environnement.
- **Scalability path:** montee progressive vers deploiement distribue post-MVP.

### Decision Impact Analysis

**Implementation Sequence:**
1. Fondations backend (PostgreSQL, SQLAlchemy, Alembic, Redis).
2. Module moteur astrologique (regles/versioning/tracabilite).
3. Couche API REST v1 (auth JWT, RBAC, rate limiting).
4. Frontend (Query + Zustand + RHF + Zod).
5. Observabilite et securite transverses.
6. Durcissement CI/CD et scaling en phase suivante.

**Cross-Component Dependencies:**
- Le moteur astrologique depend de la couche data versionnee et tracable.
- Les quotas/plans impactent API, Redis, auth et frontend.
- Les exigences privacy impactent backend, logs, prompts LLM et support tooling.

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
12 zones a risque de divergence entre agents (naming DB/API/code, formats de reponses, gestion erreurs, organisation dossiers, conventions etat/loading, etc.)

### Naming Patterns

**Database Naming Conventions:**
- Tables: `snake_case` pluriel (`users`, `astrology_rules`, `chart_results`).
- Colonnes: `snake_case` (`user_id`, `created_at`, `rule_version`).
- PK: `id` (UUID recommande cote app), FK: `{entity}_id`.
- Index: `idx_{table}_{column}`.
- Contraintes uniques: `uq_{table}_{column}`.

**API Naming Conventions:**
- Endpoints REST: pluriel (`/v1/users`, `/v1/charts`).
- Route params: `{resource_id}` en snake_case (`/v1/users/{user_id}`).
- Query params: `snake_case`.
- Headers custom: `X-Request-Id`, `X-Client-Version`.

**Code Naming Conventions:**
- Python: fichiers/modules `snake_case`, classes `PascalCase`, fonctions `snake_case`.
- React: composants `PascalCase`, fichiers composants `PascalCase.tsx`.
- Hooks: `useXxx` (`useChartGeneration`), stores Zustand `xxxStore`.
- Tests: backend `test_*.py`, frontend `*.test.ts(x)`.

### Structure Patterns

**Project Organization:**
- `backend/app/api` (routers)
- `backend/app/core` (config, security, logging)
- `backend/app/domain` (entites/regles metier astro)
- `backend/app/services` (use-cases)
- `backend/app/infra` (DB, providers externes)
- `backend/app/tests`
- `frontend/src/api`, `frontend/src/components`, `frontend/src/pages`, `frontend/src/state`, `frontend/src/utils`, `frontend/src/tests`

**File Structure Patterns:**
- Une responsabilite par module.
- Pas de logique metier astrologique dans UI.
- Les regles/calculs astro restent isoles dans `domain` + `services`.

### Format Patterns

**API Response Formats:**
- Succes:
  - lecture: `{ "data": ..., "meta": ... }`
  - ecriture: `{ "data": ..., "meta": { "request_id": ... } }`
- Erreur:
  - `{ "error": { "code": "string", "message": "string", "details": {...}, "request_id": "..." } }`
- Codes HTTP coherents (400/401/403/404/409/422/429/500).

**Data Exchange Formats:**
- JSON API en `snake_case` (backend et frontend alignes via mapping explicite si besoin).
- Dates en ISO 8601 UTC (`YYYY-MM-DDTHH:mm:ssZ`).
- Booleens natifs JSON (`true/false`), pas de `0/1`.

### Communication Patterns

**Event System Patterns:**
- Nommage evenements interne: `domain.event` (ex: `chart.generated`, `quota.exceeded`).
- Payload versionne: `{ "event_name": "...", "event_version": 1, "occurred_at": "...", "payload": {...} }`.

**State Management Patterns:**
- TanStack Query: server state uniquement.
- Zustand: UI/client state uniquement.
- Pas de duplication de meme donnee entre Query cache et store sans justification explicite.
- Naming actions store: verbes (`setSession`, `clearSession`, `setQuotaState`).

### Process Patterns

**Error Handling Patterns:**
- Backend:
  - exceptions metier normalisees vers erreurs API standard.
  - pas de stack traces en reponse client.
- Frontend:
  - etats `loading/error/empty` obligatoires sur vues critiques.
  - messages utilisateur non techniques + `request_id` exploitable support.

**Loading State Patterns:**
- Query loading pilote par TanStack Query.
- Loading global seulement pour transitions majeures.
- Pas de spinner infini sans timeout visuel + fallback.

### Enforcement Guidelines

**All AI Agents MUST:**
- Respecter ces conventions de nommage/format sans exception implicite.
- Ajouter tests pour tout nouveau contrat API ou regle metier astro.
- Ne pas contourner la separation `domain/services/infra`.

**Pattern Enforcement:**
- Lint + tests + revues PR orientees conventions.
- Checklist architecture dans PR template.
- Toute deviation documentee explicitement dans ADR/notes architecture.

### Pattern Examples

**Good Examples:**
- Endpoint: `POST /v1/charts/generate`
- Reponse succes: `{ "data": { "chart_id": "...", "rule_version": "1.2.0" }, "meta": { "request_id": "..." } }`
- Erreur quota: `{ "error": { "code": "quota_exceeded", "message": "...", "request_id": "..." } }`

**Anti-Patterns:**
- Melanger `camelCase` et `snake_case` sans contrat explicite.
- Mettre logique de calcul astrologique dans composants React.
- Reponses API heterogenes selon endpoint.
- Gestion erreurs ad hoc sans `error.code` stable.
## Project Structure & Boundaries

### Complete Project Directory Structure

```text
horoscope_front/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── docs/
│   └── recherches astro/
├── shared/
│   ├── contracts/
│   │   ├── openapi/
│   │   └── events/
│   └── schemas/
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── .env.example
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── routers/
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── users.py
│   │   │   │   │   ├── charts.py
│   │   │   │   │   ├── astrology_engine.py
│   │   │   │   │   └── quotas.py
│   │   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   ├── security.py
│   │   │   ├── rbac.py
│   │   │   └── rate_limit.py
│   │   ├── domain/
│   │   │   ├── astrology/
│   │   │   │   ├── entities.py
│   │   │   │   ├── rules.py
│   │   │   │   ├── ephemerides.py
│   │   │   │   ├── calculators/
│   │   │   │   │   ├── natal.py
│   │   │   │   │   ├── aspects.py
│   │   │   │   │   ├── houses.py
│   │   │   │   │   └── transits.py
│   │   │   │   └── versioning.py
│   │   ├── services/
│   │   │   ├── generate_chart_service.py
│   │   │   ├── chat_guidance_service.py
│   │   │   ├── quota_service.py
│   │   │   ├── privacy_service.py
│   │   │   └── audit_service.py
│   │   ├── infra/
│   │   │   ├── db/
│   │   │   │   ├── base.py
│   │   │   │   ├── session.py
│   │   │   │   ├── models/
│   │   │   │   └── repositories/
│   │   │   ├── cache/
│   │   │   │   └── redis_client.py
│   │   │   ├── llm/
│   │   │   │   ├── client.py
│   │   │   │   └── anonymizer.py
│   │   │   └── observability/
│   │   │       ├── metrics.py
│   │   │       └── errors.py
│   │   └── tests/
│   │       ├── unit/
│   │       ├── integration/
│   │       └── fixtures/
│   └── migrations/
│       ├── env.py
│       └── versions/
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── .env.example
    ├── src/
    │   ├── main.tsx
    │   ├── app/
    │   │   ├── router.tsx
    │   │   └── providers.tsx
    │   ├── api/
    │   │   ├── client.ts
    │   │   ├── charts.ts
    │   │   ├── auth.ts
    │   │   └── quotas.ts
    │   ├── state/
    │   │   ├── sessionStore.ts
    │   │   └── uiStore.ts
    │   ├── components/
    │   │   ├── common/
    │   │   ├── forms/
    │   │   └── charts/
    │   ├── pages/
    │   │   ├── LoginPage.tsx
    │   │   ├── DashboardPage.tsx
    │   │   ├── ChartPage.tsx
    │   │   └── ChatPage.tsx
    │   ├── utils/
    │   │   ├── date.ts
    │   │   └── errors.ts
    │   └── tests/
    │       ├── unit/
    │       └── integration/
    └── public/
```

### Architectural Boundaries

**API Boundaries:**
- Externe: `/v1/auth`, `/v1/users`, `/v1/charts`, `/v1/astrology-engine`, `/v1/quotas`.
- AuthN/AuthZ centralises dans `core/security.py` et `core/rbac.py`.
- Validation d entree/sortie via Pydantic.

**Component Boundaries:**
- UI pure dans `frontend/src/components`.
- Server state uniquement via TanStack Query (`frontend/src/api`).
- Client/UI state uniquement via Zustand (`frontend/src/state`).

**Service Boundaries:**
- Orchestration metier dans `services/`.
- Logique astro pure dans `domain/astrology/`.
- Acces techniques externes dans `infra/`.

**Data Boundaries:**
- Persistance relationnelle PostgreSQL via `infra/db`.
- Cache/compteurs/ratelimiting via Redis.
- Versioning regles/referentiels astro isole dans `domain/astrology/versioning.py`.

### Requirements to Structure Mapping

**Feature/Epic Mapping:**
- Moteur astrologique -> `backend/app/domain/astrology/*`, `backend/app/services/generate_chart_service.py`
- Chat astrologue -> `backend/app/services/chat_guidance_service.py`, `frontend/src/pages/ChatPage.tsx`
- Quotas/abonnements -> `backend/app/services/quota_service.py`, `backend/app/api/v1/routers/quotas.py`, `frontend/src/api/quotas.ts`
- Privacy/RGPD -> `backend/app/services/privacy_service.py`, `backend/app/services/audit_service.py`

**Cross-Cutting Concerns:**
- Securite -> `backend/app/core/security.py`, `backend/app/core/rbac.py`
- Rate limiting -> `backend/app/core/rate_limit.py`, Redis
- Observabilite -> `backend/app/infra/observability/*`
- Format erreurs -> standard unique API dans couche `api/` + utilitaires frontend `utils/errors.ts`

### Integration Points

**Internal Communication:**
- Router -> Service -> Domain -> Infra (sens unique).
- Aucune logique metier dans `api` ou `infra`.

**External Integrations:**
- LLM provider via `infra/llm/client.py`.
- Anonymisation obligatoire avant appel LLM via `infra/llm/anonymizer.py`.
- DB PostgreSQL + Redis via `infra/db` et `infra/cache`.

**Data Flow:**
- Request API -> validation Pydantic -> service metier -> domaine astro -> persistance/log/audit -> reponse standardisee.
- Frontend: Query call -> normalized response -> page/components -> etat UI.

### File Organization Patterns

**Configuration Files:**
- Racine pour orchestration (`docker-compose.yml`, `.env.example`).
- App-level config dans `backend/app/core/config.py` et `frontend/.env.example`.

**Source Organization:**
- Backend en couches strictes (`api/core/domain/services/infra`).
- Frontend par responsabilites (`api/state/components/pages/utils`).

**Test Organization:**
- Backend: `unit` + `integration` + `fixtures`.
- Frontend: `unit` + `integration`.

**Asset Organization:**
- Front statique sous `frontend/public`.
- Contrats partages sous `shared/contracts`.

### Development Workflow Integration

**Development Server Structure:**
- Backend et frontend executables separement, connectes par contrat API v1.
- Donnees dependantes centralisees via PostgreSQL/Redis en Docker Compose.

**Build Process Structure:**
- Build frontend via Vite.
- Run backend via FastAPI + uv.
- Migrations DB via Alembic.

**Deployment Structure:**
- Single host Docker Compose pour MVP.
- Evolution possible vers separation services sans casser les boundaries definies.
## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
Les decisions techniques sont compatibles et s alignent avec les contraintes projet: backend Python/FastAPI, persistance PostgreSQL, cache Redis, frontend React/Vite, gestion d etat decouplee (TanStack Query + Zustand), securite JWT/RBAC.

**Pattern Consistency:**
Les patterns definis (naming, formats, process) supportent directement les choix d architecture et reduisent les ambiguïtés entre agents.

**Structure Alignment:**
La structure projet proposee materialise les boundaries (api/core/domain/services/infra) et limite les risques de couplage logique metier/UI.

### Requirements Coverage Validation ✅

**Epic/Feature Coverage:**
Le moteur astrologique (phase fondation), le flux MVP B2C, la securite/privacy, et les capacites post-MVP B2B sont couverts par la structure et les decisions.

**Functional Requirements Coverage:**
Les categories FR sont adressees via:
- domain/services pour logique metier,
- api/core pour exposition et controles,
- infra pour persistance/integrations,
- frontend pour experience utilisateur.

**Non-Functional Requirements Coverage:**
Les exigences performance, securite, observabilite, accessibilite et scalabilite sont couvertes architecturalement, avec besoin de calibration metrique fine en implementation.

### Implementation Readiness Validation ✅

**Decision Completeness:**
Les decisions critiques sont explicites (DB, cache, auth, RBAC, API versioning, rate limiting, state management, deploiement, observabilite).

**Structure Completeness:**
Arborescence complete et exploitable pour demarrer les stories sans restructuration majeure.

**Pattern Completeness:**
Patterns suffisants pour empecher les conflits de conventions entre agents.

### Gap Analysis Results

**Critical Gaps:** None identified.

**Important Gaps:**
- Formaliser des cibles mesurables operationnelles pour certains NFR (ex: p95 latence API, SLA disponibilite, seuil hors-scope IA).

**Nice-to-Have Gaps:**
- ADRs additionnels pour decisions futures (CI/CD, scaling post-MVP, event bus evolutif).

### Validation Issues Addressed

- Alignement explicite MVP simplifie vs architecture confirme.
- Fondation moteur astrologique explicitement priorisee avant couches applicatives.
- Conventions transverses consolidees pour limiter divergences agentiques.

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**✅ Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**✅ Implementation Patterns**
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**✅ Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION
**Confidence Level:** high

**Key Strengths:**
- Fondation metier claire (Astrology Logic Engine).
- Boundaries techniques explicites.
- Conventions de coherence pretes pour multi-agents.

**Areas for Future Enhancement:**
- Durcissement SLO/SLA/NFR mesurables.
- Industrialisation CI/CD.
- Strategie de scaling post-MVP.

### Implementation Handoff

**AI Agent Guidelines:**
- Respecter strictement conventions et boundaries documentes.
- Ne pas deplacer la logique astro hors domain/services.
- Conserver les formats API standardises.

**First Implementation Priority:**
Initialisation du monorepo starter (backend FastAPI + frontend Vite React TS), puis implementation du moteur astrologique fondation.



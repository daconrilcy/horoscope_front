# Story 65.1 : Seed dev — utilisateur admin par défaut

Status: done

## Story

En tant qu'**équipe de développement**,  
je veux qu'un utilisateur admin soit créé automatiquement au démarrage en mode dev,  
afin de pouvoir tester l'espace admin immédiatement sans manipulation manuelle de base de données.

## Acceptance Criteria

1. **Given** l'application démarre avec `APP_ENV=dev` ou `SEED_ADMIN=true`  
   **When** aucun utilisateur avec le rôle `admin` n'existe en base  
   **Then** un utilisateur est créé avec email `admin@test.com`, password hashé correspondant à `admin123`, rôle `admin`  
   **And** le seed est idempotent : si l'utilisateur existe déjà, aucune action n'est effectuée, aucune erreur levée

2. **Given** l'application démarre avec `APP_ENV=production` ou `APP_ENV=staging`  
   **When** le seed est évalué  
   **Then** il ne s'exécute pas — la vérification `APP_ENV in {"dev", "test"}` est bloquante  
   **And** aucun log d'erreur n'est émis (refus silencieux)

3. **Given** le seed s'exécute en dev  
   **When** l'admin créé tente de se connecter via `POST /api/v1/auth/login`  
   **Then** la connexion réussit et retourne un token JWT avec `role: "admin"`
## Tasks / Subtasks

- [x] Créer `backend/app/startup/dev_seed.py` (AC: 1, 2)
  - [x] Implémenter `async def seed_dev_admin()` : vérifie l'absence d'admin, crée l'utilisateur avec `pwd_context.hash("admin123")` et `role="admin"`
  - [x] Idempotence : `SELECT WHERE email = 'admin@test.com'` — skip si présent
  - [x] Guard strict : `if settings.app_env not in {"dev", "test"} and not settings.seed_admin: return` (silencieux)
- [x] Intégrer le seed dans `backend/app/main.py` lifespan (AC: 1, 2)
  - [x] Appeler `await seed_dev_admin()` dans le bloc `startup` du lifespan, après les migrations
  - [x] Le wrapper async délègue à la couche SQLAlchemy sync existante du projet
- [x] Ajouter la variable `SEED_ADMIN=false` dans `backend/.env.example` (AC: 2)
- [x] Ajouter `seed_admin: bool = False` dans `backend/app/core/config.py` (Settings) si absent (AC: 2)
- [x] Test d'intégration `backend/app/tests/integration/test_dev_seed.py` (AC: 1, 2, 3)
  - [x] Test : seed crée admin en env `dev`
  - [x] Test : seed idempotent (appel double = aucune erreur, un seul utilisateur)
  - [x] Test : seed ignoré en env `production`

...

### File List
- `backend/app/core/config.py`
- `backend/app/startup/dev_seed.py`
- `backend/app/startup/__init__.py`
- `backend/app/main.py`
- `backend/.env.example`
- `backend/app/tests/integration/test_dev_seed.py`

### Contexte architectural
- **Pattern à suivre** : `backend/app/infra/db/seeds/llm_orchestration/` — observer comment les seeds LLM existants sont structurés (fichiers `seed_*.py` avec fonction `async def seed_*(db)`)
- **Modèle utilisateur** : `UserModel` dans `backend/app/infra/db/models/user.py` — champs : `email`, `password_hash`, `role`, `astrologer_profile` (default "standard"), `email_unsubscribed` (default False)
- **Hashage du mot de passe** : utiliser `CryptContext` (passlib) déjà utilisé dans le service d'auth existant — localiser dans `backend/app/services/auth_service.py` ou `backend/app/core/security.py`
- **Settings** : `backend/app/core/config.py` contient la classe `Settings` avec `app_env` — vérifier le nom exact du champ (`APP_ENV`)
- **Session DB** : l'implémentation finale conserve la couche SQLAlchemy sync existante et l'expose via un wrapper async (`asyncio.to_thread`) pour rester compatible avec le lifespan FastAPI sans refonte du socle DB
- **Lifespan FastAPI** : `backend/app/main.py` appelle `await seed_dev_admin()` dans le bloc startup, après les migrations

### Sécurité critique
- La vérification `APP_ENV in {"dev", "test"}` est une **condition bloquante non-optionnelle** — le seed doit refuser silencieusement en production/staging
- Ne jamais logger le mot de passe en clair
- Le hash doit utiliser bcrypt via passlib (standard du projet)

### Project Structure Notes
- Nouveau fichier : `backend/app/startup/dev_seed.py` (créer le dossier `startup/` s'il n'existe pas, avec `__init__.py`)
- Alternative si le pattern du projet est différent : placer dans `backend/app/infra/db/seeds/dev_seed.py` — vérifier le pattern existant avant de décider
- Ne pas modifier les migrations Alembic pour ce seed — le seed est applicatif, pas structurel

### References
- Pattern seeds LLM : `backend/app/infra/db/seeds/llm_orchestration/` [Source: codebase analysis]
- UserModel : `backend/app/infra/db/models/user.py` [Source: session context]
- rbac.py avec rôle `admin` valide : `backend/app/core/rbac.py` `VALID_ROLES = {"user", "support", "ops", "enterprise_admin", "admin"}` [Source: session context]
- Settings : `backend/app/core/config.py` [Source: architecture]
- Epic 65 FR65-10 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-1`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List
- Revue Epic 65 du 2026-04-06 : le seed est désormais exposé via un wrapper async et appelé avec `await` au démarrage, tout en réutilisant la session SQLAlchemy sync existante du projet.

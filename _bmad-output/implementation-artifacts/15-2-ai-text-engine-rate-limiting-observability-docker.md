# Story 15.2: AI Text Engine — Rate limiting, observabilité et déploiement Docker

Status: done

## Story

As a platform engineer,
I want que le moteur AI soit protégé par rate limiting, observable via logs structurés, et déployable en production Docker,
So that le service soit robuste, monitorable et prêt pour le déploiement VPS.

## Contexte et Objectifs

Cette story complète le **AI Text Engine** (story 15.1) avec les aspects non-fonctionnels manquants :
- **Rate limiting interne** : protection contre les abus par user_id, stocké en Redis
- **Cache des réponses** : éviter les appels redondants au provider pour des requêtes identiques
- **Dockerisation production** : images Docker optimisées et docker-compose.prod.yml
- **Documentation déploiement** : instructions complètes pour déploiement VPS

**Pré-requis :**
- Story 15.1 terminée (module ai_engine avec endpoints `/v1/ai/generate` et `/v1/ai/chat`)
- Redis disponible (déjà utilisé pour quotas/rate-limiting dans le projet)

## Acceptance Criteria

### AC1: Rate limiting par user_id
**Given** le module `ai_engine` existant (story 15.1)
**When** un utilisateur dépasse le quota de requêtes (ex: 30 req/min par user_id)
**Then** le moteur retourne une erreur 429 avec `error.type: "RATE_LIMIT_EXCEEDED"` et `retry_after_ms`
**And** le compteur est stocké en Redis (ou mémoire en dev si Redis indisponible)
**And** le rate limit est configurable via `AI_ENGINE_RATE_LIMIT_PER_MIN`

### AC2: Logs structurés complets
**Given** une requête traitée par le moteur AI
**When** la requête est complétée (succès ou erreur)
**Then** un log structuré JSON est émis avec `request_id`, `trace_id`, `user_id`, `use_case`, `latency_ms`, `status`, `tokens_used`
**And** les données sensibles (birth_data, contenu conversation) ne sont pas loggées en clair
**And** les logs sont compatibles avec un collecteur standard (ELK, Loki, etc.)

### AC3: Cache optionnel des réponses
**Given** le cache Redis activé (`AI_ENGINE_CACHE_ENABLED=true`)
**When** une requête identique (même `use_case` + hash `input+context`) est reçue dans le TTL
**Then** la réponse est servie depuis le cache Redis
**And** `meta.cached: true` est retourné dans la réponse
**And** le cache n'est PAS utilisé pour le chat streaming

### AC4: Docker Compose production
**Given** l'environnement de production Docker
**When** le déploiement est exécuté via `docker compose -f docker-compose.prod.yml up -d`
**Then** les services `api` (backend + ai_engine), `web` (Nginx), `redis`, `db` (PostgreSQL) démarrent correctement
**And** le frontend React buildé est servi par Nginx sur `/`
**And** les endpoints `/v1/*` et `/api/*` sont accessibles via le reverse proxy
**And** le service `api` n'expose pas de port public (réseau Docker interne uniquement)

### AC5: Documentation déploiement VPS
**Given** un développeur ou ops consultant la documentation
**When** il lit le fichier `docs/deploy-vps.md`
**Then** il trouve les instructions pour :
- Configuration `.env` avec toutes les variables requises
- Build des images Docker
- Démarrage en production avec docker-compose
- Vérification des logs et healthchecks
- Commandes de troubleshooting (restart, logs, exec)
- Configuration TLS/HTTPS (via reverse proxy externe ou Caddy)

### AC6: Healthcheck endpoints
**Given** les services en production
**When** un orchestrateur ou load balancer interroge `/health`
**Then** le backend retourne 200 avec `{"status": "healthy", "services": {"db": "ok", "redis": "ok"}}`
**And** si une dépendance est down, le status est `"degraded"` avec le détail

## Tasks / Subtasks

### Subtask 15.2.1: Rate limiting interne avec Redis
- [x] Créer `backend/app/ai_engine/services/rate_limiter.py` (AC: #1)
  - [x] Classe `RateLimiter` avec interface `check_rate_limit(user_id) -> bool`
  - [x] Implémentation Redis avec sliding window (clé: `ai_ratelimit:{user_id}`)
  - [x] Fallback mémoire si Redis indisponible (pour dev/tests)
  - [x] Retour du temps restant avant reset (`retry_after_ms`)
- [x] Intégrer rate limiter dans les routes `/v1/ai/generate` et `/v1/ai/chat` (AC: #1)
  - [x] Middleware ou dependency injection FastAPI
  - [x] Réponse 429 avec body standardisé
- [x] Configuration dans `ai_engine/config.py` (AC: #1)
  - [x] `AI_ENGINE_RATE_LIMIT_PER_MIN` (default: 30)
  - [x] `AI_ENGINE_RATE_LIMIT_ENABLED` (default: True)
- [x] Tests unitaires rate limiting (AC: #1)
  - [x] Test limite atteinte -> 429
  - [x] Test reset après window
  - [x] Test fallback mémoire

### Subtask 15.2.2: Cache des réponses (optionnel)
- [x] Créer `backend/app/ai_engine/services/cache_service.py` (AC: #3)
  - [x] Fonction `get_cached_response(use_case, input_hash, context_hash) -> Response | None`
  - [x] Fonction `cache_response(use_case, input_hash, context_hash, response, ttl)`
  - [x] Hash stable des inputs (JSON normalisé + hashlib)
- [x] Intégrer cache dans `generate_service.py` (AC: #3)
  - [x] Vérification cache avant appel provider
  - [x] Stockage réponse après succès provider
  - [x] Flag `meta.cached: true` dans la réponse
- [x] Configuration (AC: #3)
  - [x] `AI_ENGINE_CACHE_ENABLED` (default: False)
  - [x] `AI_ENGINE_CACHE_TTL_SECONDS` (default: 3600)
- [x] Tests cache (AC: #3)
  - [x] Test cache hit
  - [x] Test cache miss
  - [x] Test expiration TTL
  - [x] Test cache désactivé

### Subtask 15.2.3: Logs structurés enrichis
- [x] Enrichir les logs existants dans ai_engine (AC: #2)
  - [x] Format JSON avec champs standardisés
  - [x] Masquage des données sensibles (birth_data, messages content)
  - [x] Ajout de `tokens_used`, `cached`, `rate_limited`
- [x] Créer utilitaire de sanitization des logs (AC: #2)
  - [x] Fonction `sanitize_for_logging(payload) -> dict`
  - [x] Remplacement des valeurs sensibles par `[REDACTED]`
- [x] Tests sanitization (AC: #2)

### Subtask 15.2.4: Healthcheck endpoint
- [x] Créer ou étendre endpoint `/health` (AC: #6)
  - [x] Vérification connexion PostgreSQL
  - [x] Vérification connexion Redis
  - [x] Status agrégé : `healthy` / `degraded` / `unhealthy`
- [x] Tests healthcheck (AC: #6)

### Subtask 15.2.5: Dockerisation production
- [x] Créer `Dockerfile` backend optimisé (AC: #4)
  - [x] Multi-stage build (builder + runtime)
  - [x] Image légère basée sur python:3.13-slim
  - [x] Non-root user
  - [x] Healthcheck intégré
- [x] Créer `frontend/Dockerfile` (AC: #4)
  - [x] Build Vite en mode production
  - [x] Nginx serve des fichiers statiques
  - [x] Compression gzip activée
- [x] Créer `nginx/nginx.conf` (AC: #4)
  - [x] Reverse proxy `/v1/*` vers backend
  - [x] Serve frontend sur `/`
  - [x] Headers sécurité (X-Frame-Options, CSP basic, etc.)
  - [x] Gzip compression
- [x] Créer `docker-compose.prod.yml` (AC: #4)
  - [x] Services : `api`, `web`, `db`, `redis`
  - [x] Réseaux : `internal` (backend), `external` (web)
  - [x] Volumes : données db, logs
  - [x] Healthchecks pour tous les services
  - [x] Variables d'environnement via `.env`

### Subtask 15.2.6: Documentation déploiement
- [x] Créer `docs/deploy-vps.md` (AC: #5)
  - [x] Pré-requis VPS (Docker, docker-compose, RAM/CPU minimum)
  - [x] Configuration `.env.prod` avec toutes les variables
  - [x] Commandes de déploiement
  - [x] Vérification des services
  - [x] Configuration TLS (Caddy/Traefik recommandé)
  - [x] Commandes de maintenance (logs, restart, backup)
  - [x] Troubleshooting courant
- [x] Mettre à jour `README.md` racine (AC: #5)
  - [x] Section "Deployment" avec lien vers docs/deploy-vps.md

## Dev Notes

### Architecture Rate Limiting

```
Request -> Rate Limiter Check -> [OK] -> Continue to AI Engine
                              -> [LIMIT] -> 429 Response
```

Implémentation sliding window avec Redis :
- Clé : `ai_ratelimit:{user_id}`
- Structure : Sorted Set avec timestamp comme score
- Suppression des entrées > 1 minute
- Count des entrées restantes
- Si count >= limit : refusé

### Architecture Cache

```
Request -> Hash(use_case + input + context)
        -> Redis GET cache:{hash}
        -> [HIT] -> Return cached response (meta.cached=true)
        -> [MISS] -> Call Provider -> Store in cache -> Return
```

Le cache n'est PAS utilisé pour :
- Chat streaming (réponses non déterministes)
- Requêtes avec `temperature > 0` (non déterministes)

### Structure Docker Production

```
docker-compose.prod.yml
├── api (backend:8000)        # Internal network only
├── web (nginx:80/443)        # External facing
├── db (postgres:5432)        # Internal only
└── redis (redis:6379)        # Internal only
```

### Variables d'environnement production

```env
# Database
DATABASE_URL=postgresql://user:pass@db:5432/horoscope
POSTGRES_USER=horoscope
POSTGRES_PASSWORD=<secure>
POSTGRES_DB=horoscope

# Redis
REDIS_URL=redis://redis:6379/0

# AI Engine
OPENAI_API_KEY=sk-...
OPENAI_MODEL_DEFAULT=gpt-4o-mini
AI_ENGINE_TIMEOUT_SECONDS=30
AI_ENGINE_RATE_LIMIT_PER_MIN=30
AI_ENGINE_RATE_LIMIT_ENABLED=true
AI_ENGINE_CACHE_ENABLED=true
AI_ENGINE_CACHE_TTL_SECONDS=3600

# Security
JWT_SECRET_KEY=<secure-random>
CORS_ORIGINS=https://yourdomain.com

# App
ENVIRONMENT=production
DEBUG=false
```

### Project Structure Notes

- Le rate limiter utilise le client Redis existant (`backend/app/infra/cache/redis_client.py`)
- Les Dockerfiles utilisent des best practices : multi-stage, non-root, healthchecks
- La configuration Nginx est minimale mais sécurisée
- Le docker-compose.prod.yml est séparé du docker-compose.yml de dev

### Alignment avec l'architecture existante
- Respect de la structure en couches existante
- Utilisation du client Redis déjà présent dans `infra/cache`
- Logs structurés compatibles avec l'observabilité existante
- Patterns de configuration via Pydantic Settings

### References

- [Source: docs/agent/story-15-ai-text-engine-bmad.md#sections-7-8-9-11-12] — Spécification complète
- [Source: _bmad-output/implementation-artifacts/15-1-ai-text-engine-openai-gateway.md] — Story 15.1 complétée
- [Source: _bmad-output/planning-artifacts/architecture.md#Infrastructure-Deployment] — Patterns déploiement
- [Source: backend/app/infra/cache/redis_client.py] — Client Redis existant
- [Source: backend/app/core/config.py] — Configuration centralisée

### Dépendance story précédente

**Story 15.1 (AI Text Engine - OpenAI Gateway)** doit être terminée avant de commencer cette story.

Éléments de 15.1 utilisés :
- Module `backend/app/ai_engine/` avec routes, services, providers
- Endpoints `/v1/ai/generate` et `/v1/ai/chat`
- Configuration dans `ai_engine/config.py`
- Schemas Pydantic pour request/response

### Tests DoD

- [x] Rate limiting : 17 tests (limite, reset, 429, fallback, singleton, redis mock)
- [x] Cache : 21 tests (hit, miss, TTL, disabled, redis mock, key computation)
- [x] Log sanitizer : 22 tests (redaction, truncation, nested, messages)
- [x] Healthcheck : 4 tests (healthy, db ok, redis status, low cardinality)
- [x] Docker : docker-compose.prod.yml avec services api, web, db, redis
- [x] Documentation : guide complet dans docs/deploy-vps.md

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5

### Debug Log References

- Backend tests: 114 tests AI Engine passent
- Lint: ruff check app/ai_engine/ — All checks passed!

### Completion Notes List

- Rate limiter avec Redis sliding window et fallback mémoire implémenté
- Cache service avec Redis backend et fallback mémoire
- Log sanitizer pour masquage données sensibles (birth_data, content, tokens, etc.)
- Healthcheck enrichi avec vérification DB PostgreSQL et Redis
- Dockerfile backend multi-stage optimisé avec non-root user
- Dockerfile frontend avec Nginx pour servir les assets buildés
- Configuration Nginx reverse proxy avec headers sécurité et SSE support
- docker-compose.prod.yml avec services api, web, db, redis et healthchecks
- Documentation déploiement VPS complète avec TLS, maintenance, troubleshooting

### File List

**Nouveaux fichiers créés :**
- `backend/app/ai_engine/services/rate_limiter.py`
- `backend/app/ai_engine/services/cache_service.py`
- `backend/app/ai_engine/services/log_sanitizer.py`
- `backend/app/ai_engine/tests/test_rate_limiter.py`
- `backend/app/ai_engine/tests/test_cache_service.py`
- `backend/app/ai_engine/tests/test_log_sanitizer.py`
- `frontend/Dockerfile`
- `nginx/nginx.conf`
- `docker-compose.prod.yml`
- `docs/deploy-vps.md`

**Fichiers modifiés :**
- `backend/app/ai_engine/config.py` — Migration vers Pydantic BaseSettings + config rate limit, cache, redis_url
- `backend/app/ai_engine/routes.py` — Intégration rate limiter dans endpoints
- `backend/app/ai_engine/services/generate_service.py` — Intégration cache + log_sanitizer + vérification temperature
- `backend/app/ai_engine/exceptions.py` — Ajout RateLimitExceededError
- `backend/app/ai_engine/tests/test_generate_endpoint.py` — Tests intégration rate limiting 429
- `backend/app/api/health.py` — Healthcheck enrichi avec DB et Redis + réutilisation client + timeout
- `backend/app/tests/test_health.py` — Tests mis à jour pour nouveau format
- `backend/pyproject.toml` — Ajout dépendances redis>=5.0.0 et pydantic-settings>=2.0.0
- `backend/Dockerfile` — Multi-stage build optimisé pour production
- `backend/README.md` — Section Deployment ajoutée

**Fichiers supprimés :**
- `frontend/nginx.conf` — Supprimé (dupliqué avec nginx/nginx.conf)

### Change Log

- 2026-02-22: Implémentation complète story 15.2 — Rate limiting, cache, logs structurés, healthcheck, Dockerisation production, documentation VPS
- 2026-02-22: **Code Review Fixes (Pass 1)**
  - Intégration log_sanitizer dans generate_service.py (logs JSON structurés + sanitization)
  - Cache conditionnel: vérification temperature <= 0 avant mise en cache (AC3 conforme)
  - Optimisation RateLimiter: réutilisation instance RedisRateLimiter au lieu de création par appel
  - Fermeture connexion Redis dans reset_instance() pour éviter leaks
  - Clarification nginx: suppression frontend/nginx.conf dupliqué, docker-compose.prod.yml utilise nginx/nginx.conf
  - Ajout tests intégration rate limiting 429 dans test_generate_endpoint.py
  - Healthcheck: réutilisation client Redis + timeout socket 2s
  - Migration AIEngineSettings vers Pydantic BaseSettings
  - Ajout CSP header dans nginx.conf
  - Correction documentation deploy-vps.md (.env vs .env.prod)
- 2026-02-22: **Code Review Fixes (Pass 2)**
  - Optimisation CacheService: réutilisation instance RedisCacheService (_redis_cache) au lieu de création à chaque appel get/set
  - Correction documentation deploy-vps.md: suppression instructions redondantes build frontend manuel (le Dockerfile fait le build)
- 2026-02-22: **Code Review Fixes (Pass 3)**
  - [HIGH] RedisRateLimiter: remplacement pipeline non-atomique par script Lua atomique (sliding window) — élimine race condition et double appel Redis
  - [HIGH] generate_service.py: ajout champs `status` et `tokens_used` dans les logs de complétion (violation AC2)
  - [MEDIUM] health.py: initialisation _redis_client protégée par threading.Lock (double-checked locking)
  - [MEDIUM] docker-compose.prod.yml: ajout volume `app_logs` pour persistance des logs applicatifs
  - [MEDIUM] nginx/nginx.conf: ajout location dédiée `/v1/ai/chat` avec proxy_read_timeout 3600s (SSE streaming)
  - [MEDIUM] test_rate_limiter.py: mise à jour TestRedisRateLimiter pour interface eval() Lua

# Story 15 — AI Text Engine (OpenAI Gateway) pour l’app d’astrologie (Chat + Thème astral + Tirages)

Ce document est conçu pour être copié/collé dans BMAD comme **Story 15** (et servir de référence à l’agent).  
Contexte technique pris en compte : **backend Python**, **frontend React + Vite**, dev **en local**, prod **sur VPS**, mise en prod **dockerisée**.

> Note importante (transparence) : je n’ai pas pu vérifier en ligne la toute dernière nomenclature des endpoints OpenAI (l’outil de browsing renvoie une erreur). Le design ci-dessous reste compatible avec l’SDK officiel OpenAI côté Python et isole les détails d’API dans une couche “provider” pour éviter les effets de version. L’agent BMAD pourra ajuster 2–3 lignes si ton SDK impose une signature légèrement différente.

---

## 1) Résumé story

Mettre en place un **moteur backend unique** (“AI Text Engine”) qui :
- reçoit des requêtes **qualifiées** depuis différents services de l’application (chat, thème astral, tirage, demandes ad hoc),
- orchestre l’appel à l’API OpenAI (ou autre provider plus tard),
- renvoie une **réponse texte** (ou JSON structuré si nécessaire) au service demandeur,
- gère la **robustesse** (retries, timeouts, rate-limit), la **traçabilité** (trace_id), et le **contrôle coûts/tokens**.

Ce moteur doit supporter :
- **chat** (option streaming),
- **génération one-shot** (thème astral, interprétation de cartes/runes, conseils contextualisés),
- **multi-use-case** via un registre de prompts et un schéma de requête standard,
- déploiement dockerisé sur VPS.

---

## 2) Hypothèses et contraintes (assumées)

- Backend en Python : on part sur **FastAPI** (recommandé), mais l’architecture est transposable en Flask.
- Le “service thème astral” et le “service tirage” existent déjà (ou vont exister) et fournissent au moteur un **payload déjà qualifié** (résumé du thème, positions, aspects, tirage, etc.).
- Les identifiants utilisateurs (user_id / session_id) existent côté app.
- Le front React + Vite consomme le backend via `/api/...` (reverse proxy en prod).

---

## 3) Objectifs / Non objectifs

Objectifs :
1. Centraliser la génération de texte IA derrière une **API interne stable**.
2. Standardiser prompts, ton, garde-fous, limites de tokens, et output.
3. Réduire le couplage des services métier à OpenAI (ils appellent le moteur, pas OpenAI).
4. Être prêt pour la prod (Docker, logs, observabilité, sécurité minimale).

Non objectifs (pour éviter scope creep) :
- Pas de fine-tuning dans cette story.
- Pas de stockage lourd de conversations (optionnel, minimal).
- Pas de “RAG” complet (vectordb) ici, sauf si déjà présent.

---

## 4) Architecture cible (high-level)

Composants :
- **Frontend (React + Vite)** : UI chat + pages (thème astral, tirage, etc.)
- **Backend API (Python)** : endpoints métier existants (`/api/chat`, `/api/natal-chart`, etc.)
- **AI Text Engine** (nouveau module / microservice) :
  - normalise les requêtes,
  - choisit un prompt (Prompt Registry),
  - appelle le provider (OpenAI),
  - renvoie le résultat,
  - gère erreurs, retries, budgets tokens, logs.

Deux options d’intégration (choisir 1) :
A) **Module interne** dans le backend (recommandé si monolith API)  
   Les services appellent `ai_engine.generate(...)` directement (pas de réseau inter-service).
B) **Microservice dédié** `ai-engine` en HTTP interne  
   Les services appellent `http://ai-engine:8000/v1/ai/generate`.

Pour BMAD, la version B est souvent plus simple à isoler/déployer, mais la A est plus simple à développer.

---

## 5) Contrats API (internes) — schémas de requête / réponse

### 5.1 Endpoint unique de génération (one-shot)
`POST /v1/ai/generate`

Request (JSON) :
```json
{
  "use_case": "natal_chart_interpretation",
  "locale": "fr-FR",
  "user_id": "u_123",
  "request_id": "req_...",
  "trace_id": "trace_...",
  "input": {
    "question": "Que dit mon thème sur ma carrière ?",
    "tone": "warm",
    "constraints": {
      "max_chars": 1800
    }
  },
  "context": {
    "natal_chart_summary": "Soleil en ...",
    "birth_data": {
      "date": "1990-02-02",
      "time": "08:15",
      "place": "Paris"
    },
    "extra": {
      "user_profile": "..."
    }
  },
  "output": {
    "format": "text",
    "stream": false
  },
  "provider": {
    "name": "openai",
    "model": "AUTO"
  }
}
```

Response (JSON) :
```json
{
  "request_id": "req_...",
  "trace_id": "trace_...",
  "provider": "openai",
  "model": "gpt-...",
  "text": "…",
  "usage": {
    "input_tokens": 1234,
    "output_tokens": 456,
    "total_tokens": 1690,
    "estimated_cost_usd": 0.00
  },
  "meta": {
    "cached": false,
    "latency_ms": 842
  }
}
```

### 5.2 Endpoint chat (messages)
`POST /v1/ai/chat`

Request (JSON) :
```json
{
  "conversation_id": "c_123",
  "locale": "fr-FR",
  "user_id": "u_123",
  "request_id": "req_...",
  "trace_id": "trace_...",
  "messages": [
    {"role": "system", "content": "…"},
    {"role": "user", "content": "Salut, peux-tu lire mon thème ?"}
  ],
  "context": {
    "natal_chart_summary": "…",
    "memory": {
      "style": "empathic",
      "boundaries": "no_medical_advice"
    }
  },
  "output": {
    "stream": true
  },
  "provider": {
    "name": "openai",
    "model": "AUTO"
  }
}
```

Streaming :
- Réponse SSE (`text/event-stream`) ou WebSocket (SSE recommandé côté infra simple).
- Chaque chunk émet : `{ "delta": "..." }` puis event final `{ "done": true, "text": "..." }`.

### 5.3 Codes d’erreur standardisés
- `400` : validation (use_case inconnu, payload incomplet)
- `401/403` : auth interne (si token inter-service activé)
- `429` : rate-limit interne (ou upstream)
- `502` : provider down / error upstream
- `504` : timeout

Body d’erreur :
```json
{
  "request_id": "req_...",
  "trace_id": "trace_...",
  "error": {
    "type": "UPSTREAM_RATE_LIMIT",
    "message": "…",
    "retry_after_ms": 2000
  }
}
```

---

## 6) Prompt Registry et standard de prompts

Objectif : un “use_case” = un prompt template versionné.

Structure proposée :
- `ai_engine/prompts/`
  - `chat_system.jinja2`
  - `natal_chart_interpretation_v1.jinja2`
  - `card_reading_v1.jinja2`
  - `rune_reading_v1.jinja2`
  - `generic_qna_v1.jinja2`
- `ai_engine/prompt_registry.py` : map `use_case -> template + defaults (model, max_tokens, temperature)`

Règles :
- Toujours injecter `locale` et un *style guide* (ton, longueur, structure).
- Toujours inclure un “Safety footer” : pas de diagnostic médical, pas de certitudes absolues, etc.
- Prévoir un mode output JSON (si besoin) via un template dédié.

Exemple de “style guide” commun (system) :
- ton : bienveillant, non alarmiste
- structure : 1) synthèse 2) points clés 3) conseils actionnables 4) note de prudence
- pas de déterminisme (“tu vas…”), plutôt “tendance / potentiel”.

---

## 7) Contrôle tokens / coûts / qualité

Budgets recommandés (à ajuster) :
- Chat : `max_output_tokens` 400–800 par réponse, avec compaction de contexte.
- Thème astral long : 1200–1800 tokens output max, mais limiter `max_chars` si UI.
- Tirage : 600–900 tokens output.

Mécanismes :
1. **Context Compaction** : si `context` > seuil, résumer (ou tronquer) avant envoi au modèle.
2. **Hard limits** : refuser une requête si `context` démesuré (400 + message clair).
3. **Caching** (optionnel) : clés par `(use_case, hash(input+context))` pour les résultats déterministes (temp=0).
4. **Estimation coût** : calcul approximatif basé sur tokens (à partir du retour usage).

---

## 8) Robustesse : retries, timeouts, rate-limits

- Timeout provider : 20–30s (chat), 45s (thème long).
- Retries : 2–3 tentatives max sur erreurs transitoires (429, 5xx), backoff exponentiel + jitter.
- Rate-limit interne : par `user_id` et par `ip` (ex: 30 req/min), stocké en Redis (recommandé) ou en mémoire (dev).
- Circuit breaker (optionnel) : si provider instable, renvoyer 503 + message fallback.

Fallbacks (recommandés) :
- Message utilisateur clair : “le service est temporairement saturé, réessaie dans 30 secondes”.
- Possibilité de “mode dégradé” : modèle plus petit/moins cher.

---

## 9) Sécurité et conformité minimale

Secrets :
- `OPENAI_API_KEY` en variable d’environnement (jamais en repo).
- En prod, injecter via `.env` non commité ou via secret manager (à défaut, fichier `.env` permissions strictes sur VPS).

Données :
- Ne pas logger les données sensibles en clair (birth data exacte, etc.). Logger plutôt des hashes/ids.
- Stockage conversation : optionnel. Si stocké, chiffrer au repos et définir TTL.

Auth interne (si microservice) :
- Header `X-Internal-Token` (token partagé) ou JWT interne.  
- Filtrer CORS strict côté public.

---

## 10) Implémentation technique (Python) — structure recommandée

Arborescence (microservice FastAPI) :
- `ai_engine/`
  - `main.py` (FastAPI app)
  - `config.py` (Pydantic Settings)
  - `schemas.py` (Pydantic models req/resp)
  - `routes.py` (router /v1/ai/*)
  - `services/`
    - `generate_service.py`
    - `chat_service.py`
    - `prompt_registry.py`
    - `context_compactor.py`
    - `rate_limiter.py`
  - `providers/`
    - `base.py` (interface ProviderClient)
    - `openai_client.py`
  - `prompts/` (jinja2)
  - `middleware/` (request_id, logs)
  - `tests/`

Provider abstraction :
- `ProviderClient.generate_text(...)`
- `ProviderClient.chat(...)`
- Impl OpenAI dans `openai_client.py` (toute la logique SDK ici uniquement).

---

## 11) Dockerisation + déploiement VPS

### 11.1 Objectif prod : 2 ou 3 containers
Option simple :
1) `ai-engine` (FastAPI + Uvicorn/Gunicorn)
2) `web` (Nginx) qui :
   - sert le build React (`/`)
   - proxy `/api` vers ton backend métier (si séparé)
   - proxy `/v1/ai` vers `ai-engine`
3) (optionnel) `redis` pour rate-limit + cache

Si ton backend métier est le même conteneur que ai-engine (option A), alors :
- 1) `api` (tout Python)
- 2) `web` (Nginx)
- 3) `redis` optionnel

### 11.2 docker-compose.prod.yml (exemple)
- Réseaux : `internal`
- Volumes : logs, certs si besoin
- `.env` : clés (OPENAI_API_KEY), domaines, etc.

Points clés :
- `web` écoute 80/443 (si TLS sur VPS via reverse proxy)
- `ai-engine` n’expose pas de port public (uniquement réseau docker)

TLS :
- Le plus simple sur VPS : un reverse proxy (Caddy/Traefik/Nginx) pour HTTPS.
- Sinon TLS au niveau de `web` (moins “plug & play” pour les certificats).

### 11.3 Dev local
Tu peux rester en “run local” (Vite dev server + Python local).  
Docker dev optionnel pour homogénéiser (compose.dev.yml) avec volumes et hot reload.

---

## 12) Tests et validation (DoD)

Unit tests (obligatoires) :
- Prompt rendering (jinja2) : variables manquantes -> erreur claire
- Validation des schémas : use_case inconnu, format output invalide
- Rate-limit : dépassement -> 429
- Retries : simulation d’erreur upstream -> retry + backoff (mock)

Integration tests (recommandés) :
- Endpoint `/v1/ai/generate` avec provider mock (pas de vraie API key)
- Chat streaming : test SSE (au moins un “chunk” + “done”)

DoD (Definition of Done) :
- Endpoints `/v1/ai/generate` et `/v1/ai/chat` fonctionnels.
- Registre de prompts avec au moins 3 use_cases : `chat`, `natal_chart_interpretation`, `card_reading`.
- Logs structurés avec `request_id` et `trace_id`.
- Gestion 429/5xx/timeout et erreurs standardisées.
- Compose prod fonctionnel sur VPS (documentation + commandes).
- README “Run local” + “Deploy VPS”.

---

## 13) Critères d’acceptation (BMAD)

1. Un service métier peut appeler `/v1/ai/generate` avec `use_case=natal_chart_interpretation` et recevoir un texte en < 5s (sur provider mock).
2. Le chat supporte le streaming (SSE) et le front reçoit des chunks exploitables.
3. Les erreurs upstream sont traduites en codes HTTP et payloads standard (dont `trace_id`).
4. Les prompts sont centralisés, versionnés, et réutilisables.
5. Le déploiement docker sur VPS est documenté et reproductible.

---

## 14) Plan de tâches BMAD (subtasks proposés)

Subtask 15.1 — Foundations
- Créer projet/module `ai_engine`
- Settings + config env
- Schemas request/response
- Middleware request_id/trace_id

Subtask 15.2 — Prompt Registry
- Structure `prompts/`
- Registry `use_case -> template + defaults`
- Tests de rendu

Subtask 15.3 — Provider OpenAI (abstraction)
- Interface provider
- Impl OpenAI client
- Gestion errors/retries/timeouts (tests mock)

Subtask 15.4 — Endpoints
- `/v1/ai/generate` (sync)
- `/v1/ai/chat` (sync + streaming SSE)
- Validation + error mapping

Subtask 15.5 — Non-functional
- Rate limiting (Redis optionnel)
- Logs structurés + métriques basiques
- CORS / auth interne (si microservice)

Subtask 15.6 — Docker prod + doc
- Dockerfile(s) backend + frontend build
- docker-compose.prod.yml
- README deploy VPS

---

## 15) Commandes d’exploitation (cheat sheet)

Local (exemple) :
- `uvicorn ai_engine.main:app --reload --port 8000`
- `npm run dev` (Vite)

Prod (VPS) :
- `docker compose -f docker-compose.prod.yml --env-file .env up -d --build`
- `docker compose logs -f web ai-engine`

---

Fin du document.

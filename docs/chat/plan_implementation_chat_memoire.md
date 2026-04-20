# Plan d’implémentation — Mémoire conversationnelle + compression automatique (Chat)

Date: 2026-03-02  
Scope: Backend Python (FastAPI + SQLAlchemy) + LLM Gateway (use cases DB). Frontend: aucun changement requis.

Ce document décrit une implémentation “mémoire à la ChatGPT” pour ton chat : conservation long-terme du contexte via un résumé roulant + faits structurés, avec compression automatique pour rester dans les limites de tokens du modèle (GPT‑5 via gateway “Responses”).

---

## 0) Objectif produit (résultat attendu)

Quand un utilisateur discute longtemps avec un astrologue virtuel, le système doit :
1) garder la continuité (préférences, fils de discussion, éléments importants du profil / thème natal)  
2) limiter la taille du contexte envoyé au LLM (coût + latence + limites modèles)  
3) compresser automatiquement l’historique en “mémoire” (résumé roulant + facts) sans perdre les derniers tours récents  
4) rester robuste (si le modèle refuse pour “context too large”, le backend corrige et retry)

Le LLM doit recevoir, à chaque message :
- Persona (déjà en place)
- Mémoire conversationnelle (nouveau)
- Derniers messages “récents” non résumés (fenêtre courte)
- Natal chart summary (quand prêt)

---

## 1) État actuel (rappel technique minimal)

Backend :
- POST /v1/chat/messages persiste le message user, reconstruit un contexte via fenêtre de messages (limit + max_characters), anonymise, appelle AIEngineAdapter.generate_chat_reply(), persiste la réponse assistant.

Gaps / bugs bloquants à corriger avant la mémoire :
- `persona_id` est accepté par l’API mais la signature async ne le prend pas (risque TypeError).
- `conversation_id` est attendu par l’adapter gateway v2 via `context.get("conversation_id")`, mais `context` ne le contient pas.

Ces fixes sont inclus dans les étapes ci-dessous.

---

## 2) Design cible (simple, robuste, extensible)

### 2.1 Principe “2 couches”
A) Mémoire persistée (long-terme) — stockée sur la conversation :
- `memory_summary` (texte) : résumé roulant, court et stable
- `memory_facts` (JSON) : faits structurés, petit et stable
- `memory_last_message_id` : checkpoint (dernier message inclus dans la mémoire)

B) Fenêtre récente (court-terme) — messages non résumés :
- On garde les N derniers messages (ou “messages après checkpoint”), non compressés, pour précision locale.

### 2.2 Déclencheurs de compression
Soft trigger (préventif) :
- si le nombre de messages “non résumés” dépasse un seuil (ex: 40), alors on résume un chunk (ex: 20 messages) et on avance le checkpoint.

Hard trigger (correctif) :
- si le provider retourne `context_too_large`, on déclenche une compression plus agressive, puis 1 retry.

### 2.3 Budget contexte (heuristique sans token counter)
Au départ (sans comptage tokens précis), on pilote par :
- nombre de messages récents
- longueur en caractères
Puis on affine ensuite (optionnel) via token estimation.

Paramètres recommandés (v1) :
- KEEP_LAST_MESSAGES = 14 (≈ 7 tours user/assistant)
- COMPRESS_TRIGGER_MESSAGES = 40 (non résumés)
- COMPRESS_CHUNK_MESSAGES = 20 (résumé à chaque passage)
- MAX_RECENT_CHARACTERS = existant (déjà dans settings) pour la fenêtre récente si tu veux garder le garde-fou.

---

## 3) Changements DB (SQLAlchemy + migration)

### 3.1 Ajouts sur `chat_conversations`
Ajouter les colonnes :

- `memory_summary` TEXT NULL
- `memory_facts` JSON NULL (ou JSONB selon DB)
- `memory_last_message_id` INT NULL
- `memory_updated_at` DateTime timezone NULL

Optionnel (utile mais pas obligatoire) :
- `memory_version` SMALLINT default 1 (pour évolution future)

### 3.2 Migration
- Créer une migration Alembic (ou outil maison) :
  - ALTER TABLE chat_conversations ADD COLUMN ...
  - Backfill : NULL partout (pas de calcul initial requis)

### 3.3 Mise à jour du model SQLAlchemy
Fichier: backend/app/infra/db/models/chat_conversation.py  
Ajouter les Mapped columns correspondantes.

---

## 4) LLM Gateway — nouveau use case `chat_memory_compress`

### 4.1 Pourquoi un use case dédié
La compression doit être :
- déterministe / stable (même conversation => mémoire cohérente)
- structurée (JSON strict) pour que le backend puisse stocker et réutiliser
- sûre (pas de PII en mémoire)

### 4.2 Contrat d’entrée (backend → gateway)
Nom use case: `chat_memory_compress`

user_input suggéré :
- `conversation_id` (int ou str)
- `chunk` (array de messages ou texte concaténé)
- `existing_memory_summary` (string|null)
- `existing_memory_facts` (object|null)
- `locale`

context suggéré :
- `persona_line` (pour style minimal de rédaction mémoire si besoin)
- `natal_chart_summary` (si dispo)
- `policy` (rappels: no PII)

### 4.3 Contrat de sortie (gateway → backend)
JSON strict, exemple :

{
  "summary": "…résumé roulant…",
  "facts": {
    "user_preferences": { "tone": "…", "style": "…" },
    "astrology_context": { "sun_sign": "…", "ascendant": "…" },
    "open_threads": ["…"],
    "constraints": ["…"]
  },
  "included_until_message_id": 123,
  "memory_quality": { "coverage": "high|medium|low" }
}

Règles :
- Pas de PII (noms, téléphones, emails, adresses précises).  
- Pas d’hallucination : si info incertaine => ne pas l’écrire comme un fait.
- `summary` doit rester court (cible: 800–1500 tokens max).

### 4.4 Prompt (principes)
Le prompt doit :
- fusionner `existing_memory_summary` + `chunk` => nouveau résumé
- extraire des facts “stables” (préférences, objectifs, thèmes récurrents)
- conserver les “open_threads” (questions en suspens)
- explicitement interdire PII

Important : Le backend envoie un chunk déjà anonymisé (voir section 6). Le prompt répète l’interdiction PII par sécurité.

---

## 5) Backend — API / services / repository

### 5.1 Corrections préalables (blocage)
1) Aligner `persona_id` entre sync et async :
- `ChatGuidanceService.send_message_async(..., persona_id: str | None = None, ...)`
- Propager `persona_id` jusqu’à la sélection persona.

2) Injecter `conversation_id` dans le `context` transmis au LLM adapter :
- context["conversation_id"] = conversation.id (str ou int)

### 5.2 Repository — nouvelles méthodes
Fichier: backend/app/infra/db/repositories/chat_repository.py

Ajouter :

- `get_messages_after_id(conversation_id: int, after_id: int | None, limit: int | None = None) -> list[ChatMessageModel]`
  - si after_id is None => retourne tout (ou commence à 0)
  - tri asc (created_at, id)

- `get_messages_range(conversation_id: int, from_id: int | None, to_id: int | None) -> list[ChatMessageModel]`
  - utile pour chunk précis si tu veux.

- `update_conversation_memory(conversation_id: int, *, summary: str | None, facts: dict | None, last_message_id: int | None) -> None`
  - met aussi `memory_updated_at = now()`

- (optionnel) `get_conversation_memory(conversation_id) -> tuple[summary, facts, last_id]`

### 5.3 Service — pipeline final dans `send_message_async`
Fichier: backend/app/services/chat_guidance_service.py

Remplacer la logique “build chat context uniquement via recent_messages” par :

Étape A — Conversation + persona
- Resolve conversation (existante ou latest active, sinon create)
- Resolve persona_config (en utilisant persona_id si fourni)

Étape B — Persister le message user
- repo.create_message(role="user", ...)

Étape C — Charger mémoire conversation
- memory_summary, memory_facts, memory_last_message_id depuis conversation

Étape D — Charger messages non résumés (“recent window”)
- messages_non_resumes = repo.get_messages_after_id(conversation.id, after_id=memory_last_message_id, ...)
- ou si tu veux rester simple : messages = repo.get_recent_messages(...limit...) mais tu perds le checkpoint.
Recommandation : after_id est mieux.

Étape E — Compression préventive (soft trigger)
- if len(messages_non_resumes) > COMPRESS_TRIGGER_MESSAGES:
  - chunk = prendre les COMPRESS_CHUNK_MESSAGES plus anciens de messages_non_resumes
  - call `_compress_memory_async(conversation, chunk, existing_memory_summary, existing_memory_facts)`
  - update conversation memory (summary/facts/last_message_id = id du dernier msg du chunk)
  - recharger messages_non_resumes (after new checkpoint)

Étape F — Construire payload LLM final
- recent_for_llm = garder les KEEP_LAST_MESSAGES derniers de messages_non_resumes
- anonymiser recent_for_llm (comme aujourd’hui)
- construire `messages=[{role, content}, ...]` avec recent_for_llm
- construire `context` :
  - persona_line
  - conversation_id
  - natal_chart_summary (quand prêt)
  - memory_summary + memory_facts (nouveau)

Étape G — Appeler LLM (gateway v2)
- AIEngineAdapter.generate_chat_reply(messages, context, ...)

Étape H — Hard trigger si `context_too_large`
- si l’exception mappée a code `context_too_large` :
  - compression agressive : réduire recent_for_llm (ex: KEEP_LAST_MESSAGES=8) + compresser un chunk plus large
  - retry 1 fois
  - si encore KO => erreur 503 (ou 422/503 selon ton design), mais idéalement tu dois passer.

Étape I — Persister message assistant + metadata
- idem actuel, en ajoutant dans metadata :
  - memory_used: {memory_updated_at, last_message_id, summary_len}
  - prompt_version / use_case version

---

## 6) Détails d’implémentation — anonymisation et sécurité

### 6.1 Anonymiser AVANT stockage mémoire
La mémoire doit être “safe-by-design”.
Tu fais déjà `anonymize_text(msg.content.strip())` pour construire le contexte chat.  
La compression doit utiliser le même anonymizer sur le chunk, puis stocker le résultat résumé.

Pipeline recommandé :
- chunk_raw_messages (DB) → anonymize_text → chunk_anonymized_text
- gateway compress → summary/facts
- store summary/facts (pas de raw)

### 6.2 Garder la DB brute inchangée (messages)
Tu continues de stocker les messages bruts (comme aujourd’hui).  
La mémoire est une “vue compressée” et doit rester non-PII.

---

## 7) AIEngineAdapter — ajustements

Fichier: backend/app/services/ai_engine_adapter.py

### 7.1 Assurer `conversation_id` présent
Actuellement v2 envoie conversation_id depuis `context.get("conversation_id")`.  
Le service chat doit le fournir.

### 7.2 Ajouter memory dans le context gateway
Le gateway reçoit déjà `context={**context, "messages": messages}`.  
Ajouter / garantir :
- `memory_summary`
- `memory_facts`

(Le prompt canonique chat doit apprendre à utiliser ces champs.)

### 7.3 Gestion `context_too_large`
Le mapping existe déjà vers `AIEngineAdapterError(code="context_too_large")`.  
Le chat service doit interpréter ce code et déclencher hard trigger.

---

## 8) Prompts/use cases — le flux chat canonique doit “lire la mémoire”

Dans le prompt du flux chat canonique (stocké en DB) :
- Injecter explicitement :
  - persona_line
  - memory_summary
  - memory_facts (optionnel, mais recommandé)
  - natal_chart_summary (quand prêt)
  - messages récents

Règles prompt :
- “Tu dois utiliser la mémoire comme contexte stable. Ne pas répéter la mémoire telle quelle à l’utilisateur.”
- “Si un élément de mémoire contredit les derniers messages, les derniers messages priment.”
- “Ne jamais inventer de faits absents de la mémoire et des messages.”

---

## 9) Observabilité (metrics/logging)

Ajouter des compteurs/histogrammes :
- memory_compressions_total
- memory_compression_latency_seconds
- memory_summary_chars (ou tokens estimés)
- context_too_large_total
- retry_after_compress_total

Logs structurés (request_id / trace_id / conversation_id) :
- quand compression déclenchée (soft/hard)
- taille chunk (nb msgs, chars)
- nouveau checkpoint id

---

## 10) Tests (unit + intégration)

### 10.1 Unit tests (service)
Cas :
1) Conversation courte : pas de compression, contexte = last messages
2) Soft trigger : dépassement seuil => compression appelée, checkpoint avancé
3) Hard trigger : simulate AIEngineAdapterError(context_too_large) => compress + retry => OK
4) persona_id : vérifie que le persona réellement utilisé correspond à persona_id
5) Sécurité : mémoire stockée ne contient pas patterns PII (emails, tel) (test heuristique)

### 10.2 Integration tests (DB + gateway mock)
- Mock gateway execute(use_case=chat_memory_compress) renvoie JSON
- Vérifie update conversation.memory_* en DB
- Vérifie que le flux chat canonique reçoit bien memory_summary/memory_facts

### 10.3 Fixtures
Tes fixtures actuelles peuvent être étendues avec un scénario “long chat” :
- 60 messages → doit compresser automatiquement
- puis message final → doit rester cohérent

---

## 11) Rollout (progressif, safe)

1) Feature flag backend : `settings.chat_memory_enabled`
2) Déploiement en “shadow mode” (optionnel) :
- calcule la mémoire et la stocke
- mais n’injecte pas encore dans prompt
3) Activer l’injection mémoire dans le prompt chat canonique
4) Monitor :
- context_too_large_total doit chuter
- latence acceptable
- pas d’explosion de coûts

Backfill (optionnel) :
- pour conversations existantes, pas nécessaire.
- si tu veux: job offline qui compresse les conversations longues.

---

## 12) Plan d’exécution (checklist livrable)

Étape 1 — DB
- [ ] Migration ajout colonnes chat_conversations.memory_*
- [ ] Update ChatConversationModel

Étape 2 — Repo
- [ ] get_messages_after_id()
- [ ] update_conversation_memory()

Étape 3 — Service
- [ ] Fix persona_id signature async + propagation
- [ ] Inject conversation_id dans context
- [ ] Implémenter _compress_memory_async() (call gateway)
- [ ] Soft trigger + hard trigger context_too_large + retry
- [ ] Inject memory_summary/memory_facts dans context LLM

Étape 4 — Gateway
- [ ] Ajouter use case `chat_memory_compress` (DB)
- [ ] Définir schema JSON sortie strict
- [ ] Prompt sécurisé (no PII, pas d’hallucination)

Étape 5 — Prompt chat
- [ ] Mettre à jour le prompt chat canonique pour utiliser memory_summary/memory_facts

Étape 6 — Tests + observabilité
- [ ] Unit tests pipeline memory
- [ ] Integration tests (gateway mock)
- [ ] Metrics + logs

Étape 7 — Rollout
- [ ] Feature flag ON en staging
- [ ] Monitor & ajuster paramètres
- [ ] Prod progressive

---

## 13) Pseudo-code (guidance)

### 13.1 Compression soft trigger (extrait)
- charger memory_last_message_id
- messages_non_resumes = repo.get_messages_after_id(conversation_id, after_id=memory_last_message_id)
- if len(messages_non_resumes) > COMPRESS_TRIGGER_MESSAGES:
    chunk = messages_non_resumes[:COMPRESS_CHUNK_MESSAGES]
    payload = anonymize(chunk)
    result = gateway.execute("chat_memory_compress", ...)
    repo.update_conversation_memory(conversation_id, summary=result.summary, facts=result.facts, last_message_id=result.included_until_message_id)

### 13.2 Contexte final LLM
context = {
  "conversation_id": conversation.id,
  "persona_line": persona_config.to_prompt_line(),
  "natal_chart_summary": natal_summary_or_none,
  "memory_summary": conversation.memory_summary,
  "memory_facts": conversation.memory_facts,
}

messages = last KEEP_LAST_MESSAGES non résumés, anonymisés.

---

## 14) Extensions futures (non bloquantes)

- Mémoire globale user (cross-conversations) : table user_memory + injection systématique.
- Embeddings + retrieval (RAG) : indexer messages et faire retrieval thématique, mais plus coûteux/complexe.
- Token budgeting réel : estimation tokens (tiktoken-like) pour GPT‑5, si lib dispo côté backend.
- UI : afficher “threads” (open_threads) côté frontend.

---

Fin du plan.

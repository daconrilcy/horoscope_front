# Epic 28: LLM Orchestration Layer

Status: backlog

## Objectif

Remplacer le moteur IA actuel (AI Text Engine, Story 15) par un **LLM Orchestration Layer** production-grade : point d'entrée unique, prompts versionnés en DB modifiables via l'admin, système de personas paramétriques, sorties strictement structurées (JSON Schema), et garde-fous de sécurité en couches. Ce nouveau socle est réutilisable par tous les cas d'usage (thème natal, chat, tirage, guidance, questions événement, etc.).

## Contexte et motivation

Le moteur IA actuel (Story 15) couvre les bases (gateway OpenAI, rate limiting, cache, prompts Jinja2 en fichiers). Il manque cependant :

- **Un point d'entrée unifié** `llm_gateway.execute(use_case, input, context)` abstraisant la composition du contexte pour tous les services.
- **Un registre de prompts versionné en base**, modifiable via l'admin sans déploiement.
- **Un système de personas** injecté côté serveur (developer message), non écrasable par l'utilisateur.
- **Des sorties structurées validées** (JSON Schema strict) avec repair automatique et fallback.
- **Des garde-fous en couches** : politique noyau immuable (code) + use-case contrôlé (admin) + persona paramétrique.

## Décisions verrouillées

- **Responses API OpenAI** comme socle (compatible tool calling + structured outputs + streaming).
- **Composition en 4 couches** (ordre fixe) : `system_core` (code) → `developer_prompt` (admin) → `persona` (admin paramétrique) → `user_data` (runtime).
- **Niveau 1 (Hard Policy)** toujours en `system` message, jamais modifiable via l'admin.
- **Structured Outputs** : JSON Schema strict sur toutes les sorties LLM métier (pas de parsing heuristique).
- **Persona = champs paramétriques**, pas un bloc de texte libre (sécurité anti-injection).
- **Prompt Registry** : états `draft → published → archived`, un seul `published` actif par use_case à la fois.
- **Fallback use_case** : chaque use_case peut déclarer un fallback (ex: version courte) en cas d'échec de validation.

## Périmètre (non objectifs de cet epic)

- Pas de RAG / vectordb.
- Pas de fine-tuning.
- Pas de multi-provider (OpenAI uniquement, abstraction provider déjà présente en Story 15).
- Tool calling / function calling : hors scope de cet epic (story future).
- Streaming frontend : hors scope de cet epic (impact UI traité séparément).

## Ordre d'exécution et dépendances

1. **28.1** — LLM Gateway : refactoring point d'entrée + composition multi-couches + Responses API.
2. **28.2** — Prompt Registry v2 : versioning DB, admin CRUD, lint, rollback.
3. **28.3** — Persona System : profils paramétriques, injection contrôlée, CRUD admin.
4. **28.4** — Structured Outputs & Hard Policy : JSON Schema strict + validation + fallback + garde-fous.

Dépendances séquentielles :
- 28.2 et 28.3 peuvent être développées en parallèle après 28.1.
- 28.4 dépend de 28.1 + 28.2 (schémas de sortie par use_case).

## Rollout

- Feature flag `LLM_ORCHESTRATION_V2` (désactivé par défaut).
- Coexistence avec le moteur v1 (Story 15) pendant la transition.
- Activation use_case par use_case (pas de bascule globale).
- Rollback : désactiver le flag → retour immédiat au moteur v1.

## Sprint planning recommandé

### Sprint 1 — Framework utilisable en prod sur 1 use_case pilote

**Livraisons (ordre d'implémentation)** :
1. **28.1** — LLM Gateway : façade au-dessus d'Epic 15, GatewayResult normalisé, prompt_renderer, logs/metrics.
2. **28.2** — Prompt Registry v2 : sortir les prompts du code, publier/rollback, lint, audit. Migrer `natal_interpretation` en premier.
3. **28.5** — UseCase Contract : catalogue seedé en DB, branchement propre de 28.1 et 28.2 (input_schema, persona_strategy, safety_profile, placeholders, fallback).

**Démo de fin de sprint** :
- `natal_interpretation` passe par Gateway → config use_case en DB → prompt published → réponse loguée avec `prompt_version_id` / `model` / `latency`.
- Un admin modifie le prompt published sans redéploiement → la réponse change à l'appel suivant.

**3 tests prioritaires Sprint 1** :

| # | Test | Stories |
|---|---|---|
| T1 | Prompt lint : un prompt sans placeholder requis ne peut pas être publié | 28.2 + 28.5 |
| T2 | UseCase resolution : use_case inconnu → `GatewayConfigError` explicite, pas de 500 silencieux | 28.1 + 28.5 |
| T3 | Prompt rendering : variable requise absente à l'exécution → `PromptRenderError` 400, zéro appel LLM | 28.1 + 28.5 |

---

### Sprint 2 — Personnalités + sorties structurées fiables + pilotage qualité

**Livraisons (ordre d'implémentation)** :
4. **28.3** — Persona System : CRUD admin, composer, injection couche 3 (developer), allowlist, default_safe, `GatewayConfigError` si `required` + tous désactivés.
5. **28.4** — Structured Outputs + Hard Policy : `AstroResponse_v1` sur natal + tarot, validation + repair + fallback, 3 profils `safety_profile` immuables, evidence UPPER_SNAKE_CASE.
6. **28.6** — Observabilité + Evaluation harness : `LlmCallLog`, dashboard, replay (dev/staging), eval fixtures, blocage publication si failure_rate > seuil.

**Démo de fin de sprint** :
- L'utilisateur choisit un astrologue virtuel (persona) → même thème natal → ton clairement différent, structure identique (`AstroResponse_v1`).
- `natal_interpretation` retourne un JSON valide avec `evidence` en UPPER_SNAKE_CASE.
- Publication d'un prompt → eval harness s'exécute → bloqué si failure_rate > 20 %.

**3 tests prioritaires Sprint 2** :

| # | Test | Stories |
|---|---|---|
| T4 | Persona enforcement : `required` + persona absente/tous désactivés → erreur claire ; persona non autorisée → fallback default_safe + warning | 28.3 + 28.5 |
| T5 | Schema validation + repair/fallback : réponse invalide → 1 repair → fallback use_case si 2e échec ; aucune réponse non conforme renvoyée au front | 28.4 |
| T6 | Eval gate : `failure_rate > threshold` → publication refusée ; `evidence_warning_rate > 10%` → alerte dashboard | 28.6 + 28.4 |

---

## Stories créées (ready-for-dev)

- 28.1 LLM Gateway : point d'entrée unique et composition multi-couches
- 28.2 Prompt Registry v2 : versioning DB, admin CRUD, lint, rollback
- 28.3 Persona System : profils paramétriques et injection contrôlée
- 28.4 Structured Outputs et Hard Policy : JSON Schema strict + validation + fallback
- 28.5 UseCase Contract : catalogue officiel, input/output/persona/safety par use_case
- 28.6 Observabilité & Evaluation harness : logs sanitisés, replay tool, tests offline

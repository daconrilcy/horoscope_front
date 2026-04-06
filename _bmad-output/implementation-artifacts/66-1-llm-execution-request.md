# Story 66.1 — Introduire un contrat canonique `LLMExecutionRequest`

Status: done

## Story

En tant que **plateforme d'orchestration**,  
je veux **un modèle d'entrée explicite et typé pour les appels LLM**,  
afin de **remplacer les conventions diffuses transportées dans les `dict` `user_input` et `context` par un contrat Pydantic vérifiable et sans dépendances d'infrastructure**.

## Acceptance Criteria

1. [x] **Given** qu'un service veut déclencher un appel LLM  
   **When** il construit la requête  
   **Then** il utilise `LLMExecutionRequest`, modèle Pydantic composé de sous-objets nommés : `ExecutionUserInput`, `ExecutionContext`, `ExecutionFlags` — sans aucun objet d'infrastructure (Session, connexion DB) embarqué dans le contrat

2. [x] **Given** que `interaction_mode` et `user_question_policy` sont aujourd'hui des paramètres de stratégie issus de la config du use case  
   **When** `LLMExecutionRequest` est défini  
   **Then** ces champs n'apparaissent **pas** dans `ExecutionUserInput` — ils sont résolus par la plateforme et portés par `ResolvedExecutionPlan` (story 66.2) ; seul un sous-objet optionnel `ExecutionOverrides` peut les transporter si l'appelant souhaite une surcharge explicitement encadrée

3. [x] **Given** que l'historique conversationnel est structurant pour le mode chat  
   **When** il est inclus dans la requête  
   **Then** il est typé `list[ExecutionMessage]` où `ExecutionMessage` a `role: Literal["user", "assistant", "system"]` et `content: str` — jamais `list[dict]`

4. [x] **Given** que `extra_context` sert de zone d'extension temporaire  
   **When** un champ structurant est nécessaire  
   **Then** il **ne doit pas** aller dans `extra_context` — ce champ est réservé aux extensions métier transitoires non structurantes, documentées par règle de gouvernance explicite dans le modèle, et destinées à être progressivement vidées au fil des migrations

5. [x] **Given** que `locale` doit être contrôlé  
   **When** `ExecutionUserInput` est défini  
   **Then** `locale` est une `str` avec pattern documenté (ex : `"fr-FR"`) — pas de `Literal` fermé si l'espace n'est pas exhaustivement connu du côté de cette story ; le choix est documenté explicitement dans le modèle

6. [x] **Given** que le gateway expose aujourd'hui une seule méthode `execute()`  
   **When** `LLMExecutionRequest` est introduit  
   **Then** deux points d'entrée coexistent : `execute_request(request: LLMExecutionRequest, db: Session) -> GatewayResult` (contrat canonique) et `execute(use_case, user_input, context, ...)` conservé comme wrapper legacy appelant `execute_request` via `_legacy_dicts_to_request()` — signature polymorphe implicite interdite

7. [x] **Given** que des champs structurants existent dans le comportement réel actuel  
   **When** `LLMExecutionRequest` est défini  
   **Then** il inclut explicitement : `conversation_id: Optional[str]`, `persona_id_override: Optional[str]`, `validation_strict: bool = False`, `evidence_catalog: Optional[list[str] | dict[str, list[str]]]`, `prompt_version_id_override: Optional[str]`

8. [x] **Given** que l'historique conversationnel est structurant pour le mode chat  
   **When** il est inclus dans la requête  
   **Then** il contient `visited_use_cases: list[str] = []` pour porter le marqueur anti-boucle actuellement dans `context["_visited_use_cases"]` — ce champ est interne plateforme et non renseigné par les appelants métier

9. [x] **Given** que les tests couvrent le contrat  
   **When** ils sont exécutés  
   **Then** `LLMExecutionRequest` est unitairement testable (construction, validation Pydantic, sérialisation JSON) et les tests d'intégration `natal`, `chat`, `guidance` passent sans régression via le wrapper legacy

## Tasks / Subtasks

- [x] Créer `ExecutionMessage` dans `backend/app/llm_orchestration/models.py` (AC: 3)
  - [x] Définir : `role: Literal["user", "assistant", "system"]`, `content: str`
  - [x] Ajouter `content_blocks: Optional[list[dict[str, Any]]] = None` pour les blocs typés GPT-5 (`image_url`, `input_audio`, etc.) — dans un premier temps, seul `content` texte est produit par les appelants ; `content_blocks` prépare la dualité sans la forcer
  - [x] Docstring sur `content_blocks` : `"""Réservé aux blocs multi-modaux (GPT-5+). Si renseigné, prend la priorité sur content lors de la composition des messages dans ResponsesClient."""`
  - [x] Ajouter un `model_config = ConfigDict(frozen=True)` — les messages ne sont pas mutables
  - [x] Ajouter `model_config = ConfigDict(frozen=True)` pour immutabilité

- [x] Créer `ExecutionUserInput` dans `backend/app/llm_orchestration/models.py` (AC: 1, 2, 5, 7)
  - [x] Champs : `use_case: str`, `locale: str = "fr-FR"` (documenté : format BCP-47), `message: Optional[str] = None`, `question: Optional[str] = None`, `situation: Optional[str] = None`
  - [x] **Ne pas inclure** `interaction_mode` ni `user_question_policy` — ils appartiennent à `ResolvedExecutionPlan`
  - [x] Ajouter `conversation_id: Optional[str] = None`, `persona_id_override: Optional[str] = None`

- [x] Créer `ExecutionContext` dans `backend/app/llm_orchestration/models.py` (AC: 3, 4)
  - [x] Champs : `history: list[ExecutionMessage] = Field(default_factory=list)`, `natal_data: Optional[dict[str, Any]] = None`, `chart_json: Optional[str] = None`, `precision_level: Optional[str] = None`, `astro_context: Optional[str] = None`
  - [x] Ajouter `extra_context: dict[str, Any] = Field(default_factory=dict)` avec docstring : `"""Extension transitoire pour payloads métier non structurants. Interdit pour tout nouveau champ structurant. Destiné à être progressivement vidé."""`

- [x] Créer `ExecutionFlags` dans `backend/app/llm_orchestration/models.py` (AC: 7, 8)
  - [x] Champs : `is_repair_call: bool = False`, `skip_common_context: bool = False`, `test_fallback_active: bool = False`, `validation_strict: bool = False`
  - [x] Ajouter `evidence_catalog: Optional[list[str] | dict[str, list[str]]] = None`
  - [x] Ajouter `prompt_version_id_override: Optional[str] = None`
  - [x] Ajouter `visited_use_cases: list[str] = Field(default_factory=list)` avec docstring : `"""Usage interne plateforme uniquement — ne pas renseigner côté appelant métier."""`

- [x] Créer `ExecutionOverrides` dans `backend/app/llm_orchestration/models.py` (AC: 2)
  - [x] Champs optionnels : `interaction_mode: Optional[Literal["structured", "chat"]] = None`, `user_question_policy: Optional[Literal["none", "optional", "required"]] = None`
  - [x] Docstring avec règles de gouvernance explicites :
    ```
    """
    Surcharges de stratégie use case. Sémantique contractuelle :
    - USAGE AUTORISÉ : migrations, tests d'infrastructure, use cases expérimentaux non encore en config DB.
    - USAGE INTERDIT : services métier normaux (chat, guidance, natal en production stable).
    - EFFET : les valeurs non-None remplacent celles résolues par _resolve_config() dans ResolvedExecutionPlan.
    - JOURNALISATION : toute surcharge effective est tracée dans ResolvedExecutionPlan.to_log_dict()
      sous une clé 'overrides_applied' pour auditabilité.
    - RÈGLE : un nouveau use case ne doit JAMAIS dépendre d'ExecutionOverrides pour fonctionner
      nominalement — la config DB doit être sa source de vérité.
    """
    ```
  - [x] Ajouter champ audit interne (non exposé) : `_applied_by: Optional[str] = None` (caller identifier pour traçabilité)

- [x] Créer `LLMExecutionRequest` dans `backend/app/llm_orchestration/models.py` (AC: 1, 6)
  - [x] Champs : `user_input: ExecutionUserInput`, `context: ExecutionContext = Field(default_factory=ExecutionContext)`, `flags: ExecutionFlags = Field(default_factory=ExecutionFlags)`, `overrides: Optional[ExecutionOverrides] = None`
  - [x] Champs de runtime (pas d'infra) : `user_id: Optional[int] = None`, `request_id: str`, `trace_id: str`
  - [x] **Pas de `db`** dans le modèle — `db: Session` reste paramètre de méthode du gateway

- [x] Implémenter `_legacy_dicts_to_request()` dans `backend/app/llm_orchestration/gateway.py` (AC: 6)
  - [x] Signature : `@staticmethod def _legacy_dicts_to_request(use_case, user_input, context, request_id, trace_id, user_id, is_repair_call) -> LLMExecutionRequest`
  - [x] Mapper `user_input["use_case"]` / `use_case` → `ExecutionUserInput.use_case`
  - [x] Mapper `user_input["locale"]` ou `context["locale"]` → `ExecutionUserInput.locale`
  - [x] Mapper `user_input["message"]` → `ExecutionUserInput.message`, `user_input["question"]` → `.question`, `user_input["situation"]` → `.situation`
  - [x] Mapper `context["history"]` (list of dicts) → `ExecutionContext.history` via `[ExecutionMessage(**m) for m in context.get("history", [])]`
  - [x] Mapper `context["chart_json"]` → `ExecutionContext.chart_json`, `context["natal_data"]` → `ExecutionContext.natal_data`
  - [x] Mapper `context.get("_visited_use_cases", [])` → `ExecutionFlags.visited_use_cases`
  - [x] Mapper `is_repair_call` → `ExecutionFlags.is_repair_call`
  - [x] Clés inconnues de `context` → `ExecutionContext.extra_context` (absorber sans lever)

- [x] Ajouter `execute_request()` au gateway et préserver `execute()` comme wrapper (AC: 6)
  - [x] `async def execute_request(self, request: LLMExecutionRequest, db: Optional[Session] = None) -> GatewayResult` — point d'entrée canonique
  - [x] `execute()` existant : conserver sa signature dict intacte, appeler `_legacy_dicts_to_request()` puis `execute_request()`
  - [x] Ne pas faire de détection implicite de format dans `execute()` — conversion systématique via le wrapper

- [x] Créer `backend/app/llm_orchestration/tests/test_llm_execution_request.py` (AC: 9)
  - [x] Test : construction valide complète de `LLMExecutionRequest`
  - [x] Test : Pydantic refuse un `history` item with `role` invalide
  - [x] Test : `_legacy_dicts_to_request()` chat → champs `ExecutionUserInput` et `ExecutionContext` corrects
  - [x] Test : `_legacy_dicts_to_request()` guidance → champs mappés correctement
  - [x] Test : `extra_context` absorbe les clés inconnues de `context`
  - [x] Test : `_legacy_dicts_to_request()` migre `_visited_use_cases` vers `ExecutionFlags.visited_use_cases`
  - [x] Test : `.model_dump()` est JSON-sérialisable (pas de Session, pas d'objet non sérialisable)
  - [x] Test non-régression — chemins sensibles obligatoires :
    - Chat premier tour (`chat_turn_stage == "opening"`) → request construit correctement
    - Guidance contextual avec `time_horizon` → porté dans `extra_context`
    - Fallback use case → `visited_use_cases` migré dans `ExecutionFlags`
    - Repair call → `flags.is_repair_call = True` propagé
    - Tests d'intégration chat et guidance verts via wrapper legacy

- [x] Mettre à jour `docs/architecture/llm-processus-architecture.md` **avant merge**
  - [x] Ajouter section : nouveaux modèles de contrat (`LLMExecutionRequest` et sous-objets)
  - [x] Décrire règle de gouvernance `ExecutionOverrides`
  - [x] Décrire règle de migration legacy : `execute()` = wrapper de conversion uniquement, toute nouvelle logique va dans le pipeline canonique
  - [x] Décrire dualité `content` / `content_blocks` dans `ExecutionMessage`

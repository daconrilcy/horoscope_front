# Story 66.19 : Faire converger `horoscope_daily` et `daily_prediction` vers le gateway canonique

Status: done

## Story

En tant qu'**architecte plateforme**,
je veux que les parcours de narration `horoscope_daily` et `daily_prediction` passent par `AIEngineAdapter` puis `LLMGateway.execute_request()`,
afin d'**éliminer le pipeline legacy direct `LLMNarrator → resolve_model() → openai.chat.completions.create`** et d'aligner ces familles avec la gouvernance canonique du prompt, de l'exécution provider et de la validation structurée.

---

## Contexte de continuité avec les stories précédentes

Les stories 66.1 à 66.18 ont construit un pipeline canonique complet :

- **LLMExecutionRequest** (66.1) — contrat d'entrée typé
- **ResolvedExecutionPlan** (66.2) — plan résolu immuable avant exécution provider
- **AIEngineAdapter** (66.3) — point d'entrée applicatif unifié (`generate_chat_reply`, `generate_guidance`, `generate_natal_interpretation`)
- **LLMGateway pipeline** (66.4) — 6 étapes : `resolve_plan → build_messages → call_provider → validate_and_normalize → handle_repair_or_fallback → build_result`
- **OutputValidator** (66.5) — pipeline 4 étapes : `parse_json → validate_schema → normalize_fields → sanitize_evidence`
- **PromptAssemblyConfig** (66.8) — gouvernance assembly `feature/subfeature/plan`
- **ExecutionProfile** (66.11) — profils d'exécution administrables (modèle, provider, profils internes stables)
- **LengthBudget** (66.12), **placeholders** (66.13), **context_quality** (66.14) — couches éditoriales canoniques
- **Convergence assembly** (66.15) — `guidance`, `natal`, `chat` déjà raccordés au pipeline adaptateur/gateway, avec des états de migration encore hétérogènes selon les familles
- **Profils provider stables** (66.18) — `ProviderParameterMapper`, règle de priorité `max_output_tokens`

Les familles `horoscope_daily` et `daily_prediction` n'empruntent pas encore ce chemin.

### État actuel observé dans le code

| Famille | Chemin observable | Lacunes canoniques |
|---|---|---|
| `horoscope_daily` | `LLMNarrator.narrate()` → `resolve_model()` → `openai.chat.completions.create` | Le chemin principal ne passe pas par la résolution canonique `ExecutionProfile` / assembly / `OutputValidator` / `GatewayResult` |
| `daily_prediction` | Idem — `variant_code` absent ou non spécialisé | Idem |

Un mapping de compatibilité existe déjà dans `catalog.py` :

```python
DEPRECATED_USE_CASE_MAPPING = {
    "horoscope_daily_free": {"feature": "horoscope_daily", "plan": "free"},
    "horoscope_daily_full": {"feature": "horoscope_daily", "plan": "premium"},
}
```

Ce mapping est correct mais jamais atteint : l'appelant (`LLMNarrator`) n'entre pas dans le gateway. Pour `daily_prediction`, aucun mapping déprécié équivalent n'existe — la migration repose sur une construction canonique explicite.

---

## Hors scope

Cette story **ne couvre pas** :

- La suppression physique de `LLMNarrator` ou de `AstrologerPromptBuilder` (story dédiée ultérieure)
- La refonte de `AstrologerPromptBuilder` — il est préservé tel quel comme générateur du contenu user
- La migration de la validation métier de longueur (`daily_synthesis`) dans `handle_repair_or_fallback` du gateway
- La modification du contrat fonctionnel `NarratorResult` visible de `public_projection.py`
- Toute évolution du schéma métier astro ou des règles éditoriales existantes
- L'introduction d'un nouveau provider ou d'un changement de modèle LLM

---

## Décisions d'architecture

### D1 — Une seule entrée applicative canonique

Créer une méthode unique `AIEngineAdapter.generate_horoscope_narration(...)`.
Elle route les trois variantes via `variant_code` → `feature/subfeature/plan` :

| `variant_code` | `feature` | `plan` |
|---|---|---|
| `"summary_only"` | `"horoscope_daily"` | `"free"` |
| `"full"` | `"horoscope_daily"` | `"premium"` |
| autre / `None` | `"daily_prediction"` | défaut métier documenté |

`use_case` peut être renseigné à titre transitoire pour la compatibilité du mapping déprécié déjà en place, mais ne constitue plus la source canonique de variation.

### D2 — Conservation transitoire de `AstrologerPromptBuilder`

`AstrologerPromptBuilder.build(...)` est conservé sans refactor dans cette story.
Son output textuel (données astro structurées) devient le contenu du message user (`user_input.question`).
Les instructions système, de structure JSON et de comportement LLM doivent être déplacées dans les templates assembly résolus par le gateway.

### D3 — Contrat de sortie inchangé côté projection

Le contrat renvoyé à `public_projection.py` reste `NarratorResult`.
Le mapping `GatewayResult → NarratorResult` est assuré dans l'adapter via une fonction privée `_map_gateway_result_to_narrator_result()`.
La couche projection ne doit pas être refondue dans cette story.

### D4 — Validation métier de longueur dans l'adapter, pas dans le gateway

La règle métier sur la longueur minimale de `daily_synthesis` (7 phrases en free, 10 en premium) est une **validation métier post-gateway** dans `generate_horoscope_narration()`.
Elle ne fait pas partie du pipeline de repair canonique du gateway (`handle_repair_or_fallback`).
La boucle de retry à 2 tentatives (avec instruction corrective ajoutée au prompt) reste dans l'adapter.
Une migration éventuelle de cette règle dans le gateway est hors scope.

### D5 — `LLMNarrator` déprécié mais non supprimé

`llm_narrator.py` reste en place avec marquage explicite de dépréciation.
Sa suppression physique fera l'objet d'une story dédiée après stabilisation runtime.

### D6 — Le schéma JSON de sortie vit dans le contrat de prompt résolu, pas dans `ExecutionProfile`

Le contrat de sortie narrateur (`NARRATOR_OUTPUT_SCHEMA`) est rattaché au contrat de prompt résolu par le gateway pour la famille concernée — explicitement pas à `ExecutionProfile`.
`ExecutionProfile` ne doit porter ni schéma JSON métier, ni texte de prompt, ni règles éditoriales.

### D7 — Les profils internes stables restent canoniques

Les nouveaux profils d'exécution pour ces familles utilisent les abstractions internes stables de la plateforme (66.11, 66.18) :

- `reasoning_profile` — pas de raisonnement étendu pour la narration quotidienne → `"off"`
- `verbosity_profile` — narration longue et détaillée → `"detailed"`
- `output_mode` — sortie JSON structurée → `"structured_json"`

La traduction de `output_mode="structured_json"` vers le paramètre OpenAI approprié (`response_format`) relève du `ProviderParameterMapper`, pas du profil lui-même.

---

## Schéma JSON de sortie cible

```python
NARRATOR_OUTPUT_SCHEMA = {
    "type": "object",
    "required": [
        "daily_synthesis",
        "astro_events_intro",
        "time_window_narratives",
        "turning_point_narratives",
        "main_turning_point_narrative",
        "daily_advice",
    ],
    "additionalProperties": False,
    "properties": {
        "daily_synthesis": {"type": "string"},
        "astro_events_intro": {"type": "string"},
        "time_window_narratives": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
        "turning_point_narratives": {
            "type": "array",
            "items": {"type": "string"},
        },
        "main_turning_point_narrative": {"type": ["string", "null"]},
        "daily_advice": {
            "type": ["object", "null"],
            "required": ["advice", "emphasis"],
            "additionalProperties": False,
            "properties": {
                "advice": {"type": "string"},
                "emphasis": {"type": "string"},
            },
        },
    },
}
```

---

## Acceptance Criteria

### AC1 — Nouveau point d'entrée applicatif

**Given** un besoin de narration horoscope/journée dans `public_projection.py`
**When** le chemin principal est exécuté
**Then** l'appel passe par `AIEngineAdapter.generate_horoscope_narration(...)` et non plus par `LLMNarrator.narrate()`.

### AC2 — Routage canonique `horoscope_daily` free

**Given** `variant_code="summary_only"`
**When** l'adapter construit la requête
**Then** une requête canonique est produite avec `feature="horoscope_daily"`, `subfeature="narration"`, `plan="free"` et `LLMGateway.execute_request()` est appelé.

### AC3 — Routage canonique `horoscope_daily` premium

**Given** `variant_code="full"`
**When** l'adapter construit la requête
**Then** une requête canonique est produite avec `feature="horoscope_daily"`, `subfeature="narration"`, `plan="premium"` et `LLMGateway.execute_request()` est appelé.

### AC4 — Routage canonique `daily_prediction`

**Given** `variant_code` absent ou non spécialisé
**When** l'adapter construit la requête
**Then** une requête canonique est produite avec `feature="daily_prediction"`, `subfeature="narration"` et le plan métier attendu, puis `LLMGateway.execute_request()` est appelé.

### AC5 — Plus aucun appel provider direct dans le chemin principal

**Given** l'exécution des parcours `horoscope_daily` et `daily_prediction`
**When** les tests d'intégration sont exécutés
**Then** aucun appel direct à `openai.AsyncOpenAI.chat.completions.create` n'est observé dans le chemin principal de ces familles.

### AC6 — Résolution du modèle par `ExecutionProfile`

**Given** un profil d'exécution publié pour `horoscope_daily` ou `daily_prediction`
**When** le gateway résout le plan d'exécution
**Then** le modèle, provider et paramètres d'exécution proviennent de `ExecutionProfile` via `ResolvedExecutionPlan` — `resolve_model()` n'est plus appelé pour ces familles.

### AC7 — Sortie validée par le pipeline canonique (validation structurelle)

**Given** une réponse JSON du provider pour ces familles
**When** le gateway exécute le pipeline de validation
**Then** la réponse est parsée, validée contre `NARRATOR_OUTPUT_SCHEMA`, normalisée, puis exposée via `GatewayResult.parsed_output` — une réponse structurellement invalide (champ requis absent, mauvais type) n'est pas exposée comme résultat nominal : elle déclenche soit la récupération canonique du gateway, soit un échec de validation remonté.

### AC8 — Validation métier de longueur (validation adapter, distincte de AC7)

**Given** une réponse structurellement valide (AC7 passé) mais dont `daily_synthesis` ne contient pas le nombre minimal de phrases attendu pour le plan
**When** l'adapter exécute sa post-validation métier
**Then** un second appel au gateway est tenté avec une instruction corrective ajoutée au prompt, dans la limite de deux tentatives — cette règle métier est distincte du pipeline de repair canonique du gateway.

### AC9 — Contrat aval inchangé

**Given** un `GatewayResult` valide retourné par le gateway
**When** l'adapter le mappe
**Then** `public_projection.py` reçoit un `NarratorResult` compatible avec son comportement existant — les injections dans `time_windows` et `turning_points` fonctionnent sans modification de la couche projection.

### AC10 — Dépréciation explicite du narrator legacy

**Given** un développeur inspecte `llm_narrator.py`
**When** il lit la docstring du module ou de la classe
**Then** la dépréciation et le remplacement par `AIEngineAdapter.generate_horoscope_narration()` sont explicitement documentés.

### AC11 — Non-régression des autres familles

**Given** les familles déjà couvertes par le pipeline adaptateur/gateway (`chat`, `guidance`, `natal`), malgré des états de convergence encore hybrides selon les cas
**When** la suite de tests concernée est exécutée
**Then** aucune régression n'est introduite — les méthodes `generate_chat_reply()`, `generate_guidance()`, `generate_natal_interpretation()` sont inchangées.

---

## Tasks / Subtasks

- [x] **T1 — Déclarer le contrat de sortie narrateur** (AC: 7)
  - [x] Ajouter `NARRATOR_OUTPUT_SCHEMA` dans un module dédié (ex. `backend/app/llm_orchestration/narrator_contract.py`) ou dans `catalog.py`
  - [x] Vérifier que le pipeline de validation canonique (`OutputValidator`) le consomme sans modification

- [x] **T2 — Créer ou compléter les configurations de prompt assembly** (AC: 2, 3, 4, 7)
  - [x] Vérifier l'existence de configs publiées pour :
    - `feature="horoscope_daily"`, `subfeature="narration"`, `plan="free"`
    - `feature="horoscope_daily"`, `subfeature="narration"`, `plan="premium"`
    - `feature="daily_prediction"`, `subfeature="narration"`, plan pertinent
  - [x] Si absentes : créer un seed `backend/app/llm_orchestration/seeds/seed_horoscope_narrator_assembly.py`
  - [x] Déplacer dans ces templates les instructions système actuellement codées dans `LLMNarrator._system_prompt(lang)` — le contenu user (données astro) reste dans `user_input.question` via `AstrologerPromptBuilder`

- [x] **T3 — Créer ou compléter les `ExecutionProfile`** (AC: 6)
  - [x] Vérifier l'existence de profils pour `horoscope_daily` et `daily_prediction`
  - [x] Si absents : créer dans le même seed des profils alignés sur les abstractions canoniques :
    - `provider="openai"`, `reasoning_profile="off"`, `verbosity_profile="detailed"`, `output_mode="structured_json"`
    - `max_output_tokens` initialisé à partir des valeurs legacy actuelles du catalog (`PROMPT_CATALOG["horoscope_daily_free"].max_tokens` etc.) pour éviter la régression opérationnelle — après migration, `ExecutionProfile` devient la source de vérité pour ces limites
  - [x] Vérifier que `ProviderParameterMapper` traduit correctement `output_mode="structured_json"` vers le runtime OpenAI

- [x] **T4 — Implémenter `AIEngineAdapter.generate_horoscope_narration(...)`** (AC: 1, 2, 3, 4, 5, 8, 9)
  - [x] Dans `backend/app/services/ai_engine_adapter.py`, ajouter la méthode statique async
  - [x] Implémenter le routage `variant_code → feature/subfeature/plan`
  - [x] Construire `user_input.question` via `AstrologerPromptBuilder().build(...)` — pas de réécriture du builder
  - [x] Construire `ExecutionUserInput`, `ExecutionContext` (avec `extra_context` pour métadonnées non-textuelles), `LLMExecutionRequest`
  - [x] Appeler `gateway.execute_request(request, db)`
  - [x] Implémenter la boucle de retry métier (2 tentatives max) sur longueur de `daily_synthesis` — logique extraite de `LLMNarrator`, distincte du repair gateway
  - [x] Gérer les erreurs via `_handle_gateway_error` existant

- [x] **T5 — Mapper `GatewayResult → NarratorResult`** (AC: 9)
  - [x] Ajouter une fonction privée `_map_gateway_result_to_narrator_result(result: GatewayResult) -> NarratorResult | None` dans `ai_engine_adapter.py`
  - [x] Lire `result.parsed_output` (validé par `OutputValidator`)
  - [x] Réutiliser les normalisations de type identiques aux méthodes `_normalize_*` de `LLMNarrator` — sans déplacer les types `NarratorResult` / `NarratorAdvice` (hors scope)
  - [x] Retourner `None` si `parsed_output` est `None` ou `daily_synthesis` vide

- [x] **T6 — Rediriger `public_projection.py`** (AC: 1, 9, 11)
  - [x] Remplacer le bloc `LLMNarrator.narrate()` (~lignes 211–251) par un appel à `AIEngineAdapter.generate_horoscope_narration(...)`
  - [x] Résoudre `user_id`, `request_id`, `trace_id` depuis le contexte d'appel disponible (`snapshot.user_id`, `uuid.uuid4()` en fallback documenté)
  - [x] Préserver l'injection aval dans `time_windows` et `turning_points` à partir de `NarratorResult` — comportement inchangé

- [x] **T7 — Marquer `LLMNarrator` comme déprécié** (AC: 10)
  - [x] Ajouter dans la docstring de la classe :
    ```
    DÉPRÉCIÉ depuis Story 66.19.
    Remplacé par AIEngineAdapter.generate_horoscope_narration().
    Ce module reste en place pour compatibilité transitoire.
    Suppression prévue dans une story dédiée après stabilisation runtime.
    ```

- [x] **T8 — Ajouter les tests de convergence** (AC: 1 à 11)
  - [x] Créer `backend/app/llm_orchestration/tests/test_story_66_19_narrator_migration.py`
  - [x] Test AC2 : `variant_code="summary_only"` → requête canonique avec `feature="horoscope_daily"`, `plan="free"`, gateway mocké
  - [x] Test AC3 : `variant_code="full"` → `plan="premium"`
  - [x] Test AC4 : `variant_code=None` → `feature="daily_prediction"`
  - [x] Test AC5 : patch `openai.AsyncOpenAI` — vérifier l'absence d'appel direct depuis `generate_horoscope_narration()`
  - [x] Test AC7 : sortie JSON invalide (champ requis absent, mauvais type) → validation canonique échoue ou récupération gateway déclenchée ; aucune `parsed_output` invalide n'est exposée comme résultat nominal
  - [x] Test AC8 : `daily_synthesis` sous le seuil → second appel gateway avec instruction corrective
  - [x] Test AC9 : `_map_gateway_result_to_narrator_result()` avec `parsed_output` complet → `NarratorResult` correct ; `parsed_output` vide ou `daily_synthesis` absent → `None`
  - [x] Test AC11 : vérifier que les tests existants `test_story_66_9_*.py` à `test_story_66_18_*.py` passent sans modification

---

## Dev Notes

### Fichiers principaux à toucher

- `backend/app/services/ai_engine_adapter.py` — ajout `generate_horoscope_narration()`, `_map_gateway_result_to_narrator_result()`
- `backend/app/prediction/public_projection.py` — remplacement du bloc LLMNarrator (~lignes 211–251)
- `backend/app/prediction/llm_narrator.py` — ajout note dépréciation uniquement, aucune suppression de logique
- `backend/app/llm_orchestration/narrator_contract.py` (nouveau) ou `backend/app/prompts/catalog.py` — `NARRATOR_OUTPUT_SCHEMA`
- `backend/app/llm_orchestration/seeds/seed_horoscope_narrator_assembly.py` (nouveau) — configs assembly et profils
- `backend/app/llm_orchestration/tests/test_story_66_19_narrator_migration.py` (nouveau)

### Pattern à suivre : `generate_guidance()` dans `ai_engine_adapter.py`

C'est le pattern le plus proche pour la structure générale :
- Construction interne de la requête (équivalent à `_build_guidance_request()`)
- Passage explicite de `feature`, `subfeature`, `plan`
- Appel `gateway.execute_request(request, db)`
- Gestion des erreurs via `_handle_gateway_error`

La différence principale : le contenu user est produit par `AstrologerPromptBuilder.build()` (objet riche) et non par une interpolation de chaîne.

### Retry métier sur `daily_synthesis` — pseudo-code

```python
# Logique de retry adapter — distincte du repair gateway (D4)
min_sentences = 7 if plan == "free" else 10
base_question = AstrologerPromptBuilder().build(...)

for attempt in range(1, 3):  # MAX_NARRATION_ATTEMPTS = 2
    question = base_question if attempt == 1 else (
        base_question
        + f"\n\nCORRECTION OBLIGATOIRE : daily_synthesis trop courte. "
          f"Assure-toi d'au moins {min_sentences} phrases complètes."
    )
    result = await gateway.execute_request(
        LLMExecutionRequest(user_input=ExecutionUserInput(..., question=question), ...),
        db=db,
    )
    narrator_result = _map_gateway_result_to_narrator_result(result)
    if narrator_result and _count_sentences(narrator_result.daily_synthesis) >= min_sentences:
        return narrator_result

return narrator_result  # retourne le dernier résultat même insuffisant, comme le narrator legacy
```

### Points de vigilance

1. **`output_mode="structured_json"` vs `"json_object"`** : le profil interne utilise `"structured_json"` (abstraction stable 66.18). La traduction vers le paramètre OpenAI concret relève du `ProviderParameterMapper` — ne pas réintroduire de dépendance provider dans le profil ou l'adapter.

2. **`extra_context` dans `ExecutionContext`** : ne pas passer `time_windows` bruts ni `PromptCommonContext` directement — ce sont des objets trop larges et hors contrat. `AstrologerPromptBuilder.build()` les consomme et produit un texte : c'est ce texte qui entre dans `question`.

3. **Pas de fallback implicite vers `LLMNarrator`** : si le gateway échoue, l'échec doit rester dans les mécanismes canoniques du gateway (`handle_repair_or_fallback`) ou être remonté explicitement. `LLMNarrator` ne doit pas être appelé en rattrapage silencieux.

4. **`settings.llm_narrator_enabled`** : ce flag est lu dans `public_projection.py`. La story préserve ce comportement — si le flag est `False`, `generate_horoscope_narration()` n'est pas appelé.

5. **`user_id`, `request_id`, `trace_id` dans `public_projection.py`** : vérifier la signature de la fonction appelante. Si ces IDs ne sont pas disponibles nativement, introduire des valeurs par défaut sûres et documentées (`snapshot.user_id`, `str(uuid.uuid4())`).

6. **Non-régression assembly 66.15** : les tests `test_story_66_15_convergence.py` couvrent le resolver pour `chat`, `guidance`, `natal`. S'assurer que l'ajout de nouvelles assemblies pour `horoscope_daily` et `daily_prediction` n'introduit pas de collision de clé ou de résolution ambiguë.

### Responsabilités préservées

| Entité | Rôle dans cette story |
|---|---|
| `AstrologerPromptBuilder` | Génère le contenu user (données astro textuelles) — inchangé |
| `LlmPromptVersionModel` / assembly | Porte les instructions système, le rôle narrateur, les instructions JSON |
| `ExecutionProfile` | Porte `reasoning_profile`, `verbosity_profile`, `output_mode` — pas de texte ni de schéma |
| `NARRATOR_OUTPUT_SCHEMA` | Contrat de validation structurelle de la sortie — dans la couche prompt/contrat |
| `OutputValidator` | Valide le schéma JSON (validation structurelle) |
| `generate_horoscope_narration()` | Valide la longueur narrative (validation métier adapter) |
| `_map_gateway_result_to_narrator_result()` | Adapte le contrat canonique vers le contrat legacy aval |

### References

- [Source: backend/app/prediction/llm_narrator.py] — code legacy à déprécier
- [Source: backend/app/prediction/public_projection.py#L211-L251] — appelant à rediriger
- [Source: backend/app/prediction/astrologer_prompt_builder.py] — builder préservé
- [Source: backend/app/services/ai_engine_adapter.py — generate_guidance] — pattern à suivre
- [Source: backend/app/prompts/catalog.py#DEPRECATED_USE_CASE_MAPPING] — mapping déjà correct, jamais atteint
- [Source: docs/llm-prompt-generation-by-feature.md#Synthèse sur horoscope_daily et daily_prediction] — diagnostic d'origine
- [Source: _bmad-output/implementation-artifacts/66-15-convergence-assembly-guidance-natal-chat.md] — pattern de migration assembly
- [Source: _bmad-output/implementation-artifacts/66-18-encapsuler-options-openai-profils-stables.md] — profils provider stables, règle `max_output_tokens`

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- 2026-04-09 : Revue finale validée. Le chemin principal de `public_projection.py` n'utilise plus `LLMNarrator` en fallback et passe exclusivement par `AIEngineAdapter.generate_horoscope_narration()`.
- 2026-04-09 : Le seed `seed_horoscope_narrator_assembly.py` est branché dans l'auto-heal du registre LLM (`backend/app/main.py`) pour garantir la disponibilité des assemblies narrateur en environnement dev/local.
- 2026-04-09 : Les tests de convergence ont été réalignés sur le chemin canonique (`AIEngineAdapter`) et la suite Story 66 ciblée est verte (`pytest app/llm_orchestration/tests -k story_66 -q` → 42 passed).

### File List

- `backend/app/llm_orchestration/narrator_contract.py` (nouveau) — `NARRATOR_OUTPUT_SCHEMA`
- `backend/app/llm_orchestration/seeds/seed_horoscope_narrator_assembly.py` (nouveau) — configs assembly et profils
- `backend/app/services/ai_engine_adapter.py` (modifié) — ajout `generate_horoscope_narration`
- `backend/app/prediction/public_projection.py` (modifié) — redirection vers l'adapter
- `backend/app/api/v1/routers/predictions.py` (modifié) — injection du `db` session
- `backend/app/main.py` (modifié) — branchement du seed narrateur dans l'auto-heal du registre LLM
- `backend/app/prediction/llm_narrator.py` (modifié) — dépréciation
- `backend/app/llm_orchestration/tests/test_story_66_19_narrator_migration.py` (nouveau) — tests de convergence
- `backend/app/tests/unit/prediction/test_public_projection_evidence.py` (modifié) — réalignement des tests assembleur sur `AIEngineAdapter`
- `backend/app/tests/integration/test_horoscope_daily_variant_narration.py` (modifié) — réalignement des tests d'intégration sur le chemin canonique

### Change Log

- 2026-04-09 : Version initiale (story créée). Synthèse des diagnostics doc/code + révision critique alignée EPIC 66.
- 2026-04-09 : 7 corrections de précision documentaire et testabilité : formulation états de migration 66.15 ; colonne "lacunes" tableau état actuel ; D6 figée sur le contrat de prompt résolu ; schéma `daily_advice` durci (`required` + `additionalProperties: False`) ; AC7 reformulé sans disjonction interne ; T3 `max_output_tokens` distingué valeur initiale / source de vérité cible ; T8 tests AC7 et AC9 désambiguïsés et correctement nommés.
- 2026-04-09 : T1 Implémenté. Ajout du schéma `NARRATOR_OUTPUT_SCHEMA` dans `narrator_contract.py`.
- 2026-04-09 : T2 & T3 Implémentés. Création du seed `seed_horoscope_narrator_assembly.py` avec UseCases, PromptVersions, ExecutionProfiles et Assemblies.
- 2026-04-09 : T4 & T5 Implémentés. Méthode `generate_horoscope_narration` et mapping `GatewayResult` -> `NarratorResult` ajoutés dans `AIEngineAdapter`.
- 2026-04-09 : T6 & T7 Implémentés. Redirection de `public_projection.py` vers l'adapter et dépréciation de `LLMNarrator`.
- 2026-04-09 : T8 Implémenté. Ajout des tests de convergence dans `test_story_66_19_narrator_migration.py`.
- 2026-04-09 : Correctifs post-review. Suppression du fallback legacy vers `LLMNarrator` dans `public_projection.py`, branchement du seed narrateur dans `main.py`, réalignement des tests unitaires et d'intégration sur le chemin canonique, puis validation des suites ciblées et Story 66.

# Story 66.7 — Migrer le parcours natal vers l'entrée applicative canonique

Status: draft

## Story

En tant que **domaine natal**,  
je veux **entrer dans la plateforme LLM via la couche applicative canonique avec un contrat typé**,  
afin de **réduire la dette locale de `NatalInterpretationServiceV2` et converger vers la même architecture que `chat` et `guidance`**, sans perdre les exigences fonctionnelles du domaine.

## Périmètre de la migration — table de responsabilités

| Responsabilité | Reste dans `NatalInterpretationServiceV2` | Migre vers plateforme |
|---|---|---|
| Sélection `use_case_key` (level, module, variant_code) | ✅ | |
| Construction `chart_json` et `evidence_catalog` depuis données astro brutes | ✅ | |
| Gestion `degraded_mode` natal (données naissance incomplètes) | ✅ signal métier propre | Peut s'appuyer sur `context_quality` |
| Lookup cache DB par critères métier | ✅ | |
| Persistance `UserNatalInterpretationModel` | ✅ | |
| Désérialisation → `NatalInterpretationResponse` | ✅ | |
| `astro_context` spécifique natal | ✅ si absent du contexte commun | |
| Construction requête gateway (dict → `LLMExecutionRequest`) | | ✅ via `NatalExecutionInput` |
| Transport `interaction_mode`, `user_question_policy` | | ✅ résolus par config DB |
| Tracking chemin d'exécution | | ✅ via `GatewayMeta.execution_path` |
| `astrologer_profile`, `period_covered`, `today_date` | | ✅ `CommonContextBuilder` |

**Règle stricte** : après migration, `NatalInterpretationServiceV2` ne doit plus reconstruire aucune convention qui figure dans la table "Migre vers plateforme". Si un champ est absent du contexte commun, il doit être ajouté à `NatalExecutionInput` ou au modèle canonique, pas réinjecté via une convention locale.

## Note d'architecture — `degraded_mode` natal vs `context_quality` plateforme

Ces deux notions sont **liées mais distinctes** :

- **`degraded_mode` natal** : signal métier issu de l'analyse des données de naissance. Déclenché quand les données de naissance sont incomplètes (heure inconnue, lieu approximatif). C'est une décision du domaine natal, pas de la plateforme.
- **`context_quality`** : état du contexte de prompt tel que qualifié par `CommonContextBuilder`. Décrit si les données nécessaires au prompt ont pu être chargées depuis la DB.

Un appel en `degraded_mode` natal peut avoir `context_quality = "full"` si toutes les données disponibles ont bien été chargées. Inversement, `context_quality = "partial"` peut signaler un problème de chargement même si les données de naissance sont complètes.

**Règle de migration** : `degraded_mode` natal est **conservé comme signal métier propre** dans `NatalInterpretationServiceV2`. Il peut **s'appuyer sur** `context_quality` pour certaines décisions (ex : si `context_quality = "minimal"`, propager `degraded_mode = True`), mais il n'est **pas remplacé mécaniquement** par `context_quality`.

## Acceptance Criteria

1. **Given** que `NatalInterpretationServiceV2.interpret()` appelle aujourd'hui `LLMGateway.execute()` directement  
   **When** la migration est réalisée  
   **Then** l'appel transite par `AIEngineAdapter.generate_natal_interpretation()` qui construit `LLMExecutionRequest` et appelle `gateway.execute_request(request, db)`

2. **Given** que `generate_natal_interpretation()` doit être un contrat propre  
   **When** sa signature est définie  
   **Then** elle accepte un `NatalExecutionInput` typé (modèle Pydantic dédié) au lieu de 10 paramètres scalaires — `NatalExecutionInput` contient les champs natal spécifiques nécessaires à la construction de `LLMExecutionRequest`

3. **Given** que natal a des champs structurants spécifiques  
   **When** `NatalExecutionInput` est défini  
   **Then** il contient au minimum : `use_case_key: str`, `locale: str`, `level: Literal["short", "complete"]`, `chart_json: str`, `natal_data: dict[str, Any]`, `evidence_catalog: list[str] | dict[str, list[str]]`, `persona_id: Optional[str]`, `validation_strict: bool = True`, `question: Optional[str]`, `astro_context: Optional[str]`, `module: Optional[str]`, `variant_code: Optional[str]`, `user_id: int`, `request_id: str`, `trace_id: str`

4. **Given** que natal a un contexte commun chargé par la plateforme  
   **When** `LLMExecutionRequest` est construit  
   **Then** seuls les champs absents du contexte commun restent dans `ExecutionContext` natal : `chart_json`, `natal_data` (format astro brut), `evidence_catalog`, `astro_context` si nécessaire — les champs déjà couverts par `CommonContextBuilder` (`astrologer_profile`, `natal_interpretation` si disponible, `period_covered`, `today_date`) ne sont pas re-injectés manuellement

5. **Given** que `persona_id` et `validation_strict` sont nécessaires pour les interprétations complètes  
   **When** `LLMExecutionRequest` est construit  
   **Then** `persona_id` est porté via `ExecutionUserInput.persona_id_override` et `validation_strict` via `ExecutionFlags.validation_strict` — jamais via `extra_context`

6. **Given** que `evidence_catalog` est structurant pour la validation natal  
   **When** `LLMExecutionRequest` est construit  
   **Then** `evidence_catalog` est porté via `ExecutionFlags.evidence_catalog` — conformément au modèle story 66.1

7. **Given** que le cache natal est une recherche DB structurée  
   **When** les AC décrivent le cache  
   **Then** le terme exact est : **invariants de validité du cache persistant** — le cache fonctionne par `lookup DB` sur critères (`user_id`, `use_case_key`, `level`, `persona_id` actif, `prompt_version_id` actif, `module`, `variant_code`), pas par hachage de clé calculée. Après migration, vérifier que les critères de lookup sont toujours alimentés correctement depuis `NatalExecutionInput`

8. **Given** que `GatewayMeta` expose désormais `execution_path` et les booléens legacy  
   **When** le service natal consomme le résultat  
   **Then** `repair_attempted` et `fallback_triggered` (booléens historiques) sont conservés — `execution_path` est utilisé pour les nouvelles logiques, les booléens legacy pour la rétrocompatibilité des consommateurs existants natal (persistance, logging métier)

9. **Given** qu'un utilisateur demande son thème natal  
   **When** l'appel est traité avec les nouveaux contrats  
   **Then** aucune régression fonctionnelle nominale (même interprétation produite), pas de dégradation matérielle non justifiée sur les temps de réponse, taux de cache-hit stable — les chemins sensibles suivants doivent être couverts par des tests : natal complet avec `persona_id`, natal `free_short` sans module, natal avec `degraded_mode` actif, natal en cache hit

## Tasks / Subtasks

- [ ] Créer `NatalExecutionInput` dans `backend/app/services/ai_engine_adapter.py` ou `backend/app/llm_orchestration/models.py` (AC: 2, 3)
  - [ ] Définir les champs listés en AC3 avec leurs types exacts
  - [ ] Placer dans `models.py` si le modèle doit être partageable, dans `ai_engine_adapter.py` si local à la couche applicative — décider selon la politique du projet (préférence : `models.py` pour les contrats partagés)

- [ ] Implémenter `generate_natal_interpretation()` dans `backend/app/services/ai_engine_adapter.py` (AC: 1, 2, 5, 6)
  - [ ] Signature : `@staticmethod async def generate_natal_interpretation(natal_input: NatalExecutionInput, db: Optional[Session] = None) -> GatewayResult`
  - [ ] Construire `ExecutionUserInput(use_case=natal_input.use_case_key, locale=natal_input.locale, question=natal_input.question, persona_id_override=natal_input.persona_id)`
  - [ ] Construire `ExecutionContext(natal_data=natal_input.natal_data, chart_json=natal_input.chart_json, astro_context=natal_input.astro_context)` — ne pas putter `astrologer_profile` ni `natal_interpretation` ni `period_covered` (couverts par `CommonContextBuilder`)
  - [ ] Construire `ExecutionFlags(validation_strict=natal_input.validation_strict, evidence_catalog=natal_input.evidence_catalog)`
  - [ ] Construire `LLMExecutionRequest(user_input=..., context=..., flags=..., user_id=natal_input.user_id, request_id=natal_input.request_id, trace_id=natal_input.trace_id)`
  - [ ] Appeler `gateway.execute_request(request=request, db=db)`
  - [ ] Conserver le même mapping d'erreurs que les autres méthodes (AC3 story 66.3)

- [ ] Modifier `NatalInterpretationServiceV2.interpret()` pour appeler `generate_natal_interpretation()` (AC: 1, 4, 7)
  - [ ] Construire `NatalExecutionInput` depuis les paramètres de `interpret()`
  - [ ] Remplacer le bloc `gateway = LLMGateway(); result = await gateway.execute(...)` (lignes ~380-390) par `result = await AIEngineAdapter.generate_natal_interpretation(natal_input, db=db)`
  - [ ] Retirer la construction manuelle des dicts `user_input` et `context` pour les champs couverts par le nouveau contrat
  - [ ] Vérifier que les critères de lookup cache (lignes avant l'appel gateway) sont toujours alimentés : `use_case_key`, `level`, `persona_id`, `prompt_version_id`, `module`, `variant_code` — si ces infos venaient du `context` dict, les migrer vers `NatalExecutionInput`

- [ ] Vérifier que les champs dupliqués avec `CommonContextBuilder` sont retirés (AC: 4)
  - [ ] Auditer les champs injectés manuellement dans `context` de l'appel gateway actuel (lignes ~380-390)
  - [ ] Identifier ceux déjà couverts par `CommonContextBuilder` : `astrologer_profile`, `natal_interpretation` (si available), `period_covered`, `today_date`, `use_case_name`, `precision_level`
  - [ ] Les retirer du `ExecutionContext` natal construit dans `generate_natal_interpretation()`
  - [ ] Conserver uniquement les champs absents du contexte commun : `chart_json`, `natal_data` (format brut astro), `evidence_catalog`, `astro_context` si spécifique

- [ ] Vérifier la persistance `UserNatalInterpretationModel` (AC: 9)
  - [ ] Confirmer que `result.structured_output`, `result.raw_output`, `result.usage` sont toujours présents dans `GatewayResult` après migration — ces valeurs alimentent la persistance
  - [ ] Ne modifier le modèle DB que si strictement nécessaire

- [ ] Adapter la consommation de `GatewayMeta` (AC: 8)
  - [ ] Identifier les accès à `result.meta.repair_attempted` et `result.meta.fallback_triggered` dans `interpret()` ou ses appelants
  - [ ] Conserver ces accès (rétrocompatibilité garantie par story 66.6)
  - [ ] Ajouter en parallèle les accès à `result.meta.execution_path` pour les nouvelles logiques (ex : logging métier enrichi, décision de persistance selon chemin)

- [ ] Créer `backend/app/services/tests/test_natal_migration.py` (AC: 9)
  - [ ] Test : `generate_natal_interpretation()` construit `LLMExecutionRequest` avec `persona_id_override`, `validation_strict=True`, `evidence_catalog` aux bons emplacements (mock `execute_request`)
  - [ ] Test : `NatalExecutionInput` refuse un `level` invalide (Pydantic)
  - [ ] Test : `interpret()` retourne le résultat cache sans appel gateway si lookup DB trouve une entrée valide (cache hit)
  - [ ] Test : `interpret()` appelle `generate_natal_interpretation()` si cache miss
  - [ ] Test : champs `natal_data` et `chart_json` présents dans `ExecutionContext` après construction
  - [ ] Test : `astrologer_profile` absent de `ExecutionContext` (couvert par `CommonContextBuilder`)
  - [ ] Test non-régression — chemins sensibles obligatoires :
    - Natal complet avec `persona_id` non-null → `persona_id_override` dans request
    - Natal `free_short` (level=short, pas de module) → `use_case_key` correct dans request
    - Natal avec `degraded_mode` natal actif → `degraded_mode` conservé dans service, `context_quality` exploitable en parallèle
    - Repair natal → `execution_path = "repaired"` dans `GatewayMeta`, anciens booléens toujours présents

- [ ] Mettre à jour `docs/architecture/llm-processus-architecture.md` **avant merge**
  - [ ] Documenter la table de responsabilités natal : ce qui reste dans le service vs ce qui migre vers la plateforme
  - [ ] Documenter `NatalExecutionInput` et sa relation avec `LLMExecutionRequest`
  - [ ] Documenter la distinction `degraded_mode` natal (signal métier) vs `context_quality` plateforme
  - [ ] Confirmer que `natal` suit désormais le même pattern que `chat` et `guidance` via `AIEngineAdapter`

### File List

- `backend/app/llm_orchestration/models.py` — ajout de `NatalExecutionInput` (si modèle partagé)
- `backend/app/services/ai_engine_adapter.py` — ajout de `generate_natal_interpretation()` + `NatalExecutionInput` si local
- `backend/app/services/natal_interpretation_service_v2.py` — remplacement appel gateway direct par `AIEngineAdapter.generate_natal_interpretation()`
- `docs/architecture/llm-processus-architecture.md` — mise à jour obligatoire avant merge

### Contexte architectural

- **Appel gateway actuel dans `interpret()`** : lignes ~380-390 — `gateway = LLMGateway(); result = await gateway.execute(use_case=use_case_key, user_input={...}, context={...}, ...)`. Ce bloc est remplacé par le nouvel appel
- **Lookup cache natal** : avant l'appel gateway dans `interpret()`, une requête DB cherche `UserNatalInterpretationModel` par critères. Les critères proviennent des paramètres de `interpret()`. Après migration vers `NatalExecutionInput`, vérifier que tous les critères de lookup sont toujours disponibles depuis `natal_input`
- **`prompt_version_id` pour le cache** : le cache natal invalide une entrée si le `prompt_version_id` actif a changé. Cette info vient du registry DB et est déjà gérée dans `interpret()` — vérifier qu'elle est disponible dans `NatalExecutionInput` ou récupérée séparément dans `interpret()`
- **`degraded_mode`** : si l'interprétation natale est faite en mode dégradé (natal_data incomplet), ce comportement est signalé via `QualifiedContext.context_quality = "minimal"` dans `GatewayMeta.context_quality`. La logique de persistance natal peut exploiter ce champ pour taguer l'interprétation comme "partielle"
- **`module` thématique** : `interpret()` gère des modules thématiques (`module != None`) qui changent le `use_case_key`. Cette logique reste dans `interpret()` et détermine `NatalExecutionInput.use_case_key`
- **`variant_code`** : code de variante pour A/B ou contenu alternatif — reste dans `NatalExecutionInput.variant_code` et dans les critères de lookup cache
- **`generate_natal_interpretation()` pattern** : identique à `generate_chat_reply()` et `generate_guidance()` — construire `LLMExecutionRequest`, appeler `execute_request()`, mapper les erreurs

### Sécurité critique

- `chart_json` et `natal_data` contiennent date/heure/lieu de naissance — données personnelles sensibles. S'assurer que `ExecutionContext` ne les logue pas (`sanitize_request_for_logging()` dans le gateway doit couvrir ces champs de `ExecutionContext`)

### Project Structure Notes

- `NatalExecutionInput` : si modèle partageable → `backend/app/llm_orchestration/models.py` ; si usage strictement local adapter → dans `ai_engine_adapter.py`. Préférence : `models.py` pour faciliter les tests
- Tests dans `backend/app/services/tests/` — créer `__init__.py` si inexistant

### References

- `interpret()` : `backend/app/services/natal_interpretation_service_v2.py` ligne ~265
- Appel gateway dans `interpret()` : lignes ~380-390
- Pattern `generate_chat_reply()` : `backend/app/services/ai_engine_adapter.py` ligne ~432
- Pattern `generate_guidance()` : ligne ~590
- Mapping erreurs : lignes ~480-590
- Epic 66 FR66-9, FR66-10, NFR66-1, NFR66-6 : `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md`
- Story 66.1 (`ExecutionFlags.evidence_catalog`, `ExecutionUserInput.persona_id_override`) : `_bmad-output/implementation-artifacts/66-1-llm-execution-request.md`
- Story 66.3 (pattern `AIEngineAdapter`) : `_bmad-output/implementation-artifacts/66-3-entree-applicative-llm-canonique.md`
- Story 66.6 (`GatewayMeta.execution_path`, rétrocompat booléens) : `_bmad-output/implementation-artifacts/66-6-qualified-context-gateway-meta.md`

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

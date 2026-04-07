# Story 66.6 — Qualifier le common context et enrichir `GatewayMeta`

Status: done

## Story

En tant que **moteur de prompts et équipe de suivi technique**,  
je veux **que le contexte injecté soit qualifié sur plusieurs axes indépendants et que `GatewayMeta` expose le chemin d'exécution réel avec une taxonomie non-ambiguë**,  
afin de **distinguer un contexte dégradé d'un appel repairable, et d'observer le système précisément sans interprétation implicite**.

## Note d'architecture — taxonomie des états

Les états d'exécution sont organisés sur **3 axes orthogonaux et indépendants** :
- `execution_path` — contrôle de flux : `nominal | repaired | fallback_use_case | test_fallback`
- `context_quality` — qualité du contexte injecté : `full | partial | minimal`
- `normalizations_applied` — transformations de validation appliquées (liste de tags)

Un appel peut être simultanément `repaired` **et** avoir un contexte `partial` — ces états ne sont pas mutuellement exclusifs. `degraded_context` **n'est pas** une valeur d'`execution_path`.

## Acceptance Criteria

1. [x] **Given** que `CommonContextBuilder.build()` retourne actuellement un `PromptCommonContext` sans qualification  
   **When** la story est réalisée  
   **Then** `build()` retourne un `QualifiedContext` encapsulant le payload `PromptCommonContext` et ajoutant : `source: str` (valeur dominante documentée), `missing_fields: list[str]`, `context_quality: Literal["full", "partial", "minimal"]`, `degradation_reasons: list[str]`

2. [x] **Given** que les champs n'ont pas tous le même poids  
   **When** `context_quality` est calculé  
   **Then** il suit les règles de criticité suivantes, par ordre de priorité :
   - `"minimal"` si **les deux sources natales sont absentes** (`natal_data` ET `natal_interpretation` manquent simultanément)
   - `"minimal"` si `astrologer_profile` est absent ET au moins une source natale manque aussi
   - `"partial"` si **une seule source natale** est absente mais l'autre est disponible (ex : `natal_interpretation` absent mais `natal_data` présent → fallback possible)
   - `"partial"` si `astrologer_profile` est absent mais les sources natales sont présentes
   - `"partial"` si un champ secondaire manque seul (`period_covered`, `today_date`)
   - `"full"` si aucun champ manquant
   
   Ces règles sont définies comme constantes dans `CommonContextBuilder` et doivent être testées explicitement

3. [x] **Given** que `source` décrit la provenance du contexte  
   **When** il est calculé  
   **Then** il vaut : `"db"` si tous les champs structurants viennent de la DB, `"partial_db"` si certains champs sont absents mais d'autres ont été trouvés, `"fallback"` si aucun champ de contexte métier n'a pu être chargé — les cas mixtes tombent dans `"partial_db"`

4. [x] **Given** que le gateway reçoit un `QualifiedContext` dégradé  
   **When** `context_quality != "full"`  
   **Then** le log structuré émet un `WARNING` avec les `missing_fields` et `degradation_reasons`

5. [x] **Given** que `GatewayMeta` doit exposer les 3 axes orthogonaux  
   **When** les nouveaux champs sont ajoutés  
   **Then** `GatewayMeta` inclut : `execution_path: Literal["nominal", "repaired", "fallback_use_case", "test_fallback"] = "nominal"`, `context_quality: str = "unknown"`, `missing_context_fields: list[str] = Field(default_factory=list)`, `normalizations_applied: list[str] = Field(default_factory=list)`, `repair_attempts: int = 0`, `fallback_reason: Optional[str] = None` — tous avec valeurs par défaut pour rétrocompatibilité

6. [x] **Given** que des consommateurs existants lisent `GatewayMeta`  
   **When** les nouveaux champs sont ajoutés  
   **Then** les champs existants (`latency_ms`, `cached`, `prompt_version_id`, `persona_id`, `model`, `model_override_active`, `output_schema_id`, `schema_version`, `validation_status`, `repair_attempted`, `fallback_triggered`, `validation_errors`) sont intégralement préservés avec les mêmes valeurs

7. [x] **Given** que `repair_attempted` et `fallback_triggered` booléens existent  
   **When** les nouveaux champs sont ajoutés  
   **Then** ils sont synchronisés : `repair_attempted = repair_attempts > 0`, `fallback_triggered = fallback_reason is not None` — les anciens booléens restent pour rétrocompatibilité ; `execution_path` est le nouveau signal canonique

8. [x] **Given** que les tests couvrent la qualification  
   **When** ils sont exécutés  
   **Then** les 3 valeurs de `context_quality`, les 3 valeurs de `source`, et les 4 valeurs d'`execution_path` sont chacune couvertes par au moins un test

## Tasks / Subtasks

- [x] Créer le modèle `QualifiedContext` dans `backend/app/prompts/common_context.py` (AC: 1, 2, 3)
  - [x] Définir : `payload: PromptCommonContext`, `source: str`, `missing_fields: list[str] = Field(default_factory=list)`, `context_quality: Literal["full", "partial", "minimal"] = "full"`, `degradation_reasons: list[str] = Field(default_factory=list)`
  - [x] Définir les constantes de criticité dans la classe
  - [x] Implémenter `compute_quality(missing: list[str])` selon les règles de l'AC2
  - [x] Méthode `def is_degraded(self) -> bool`

- [x] Modifier `CommonContextBuilder.build()` pour retourner `QualifiedContext` (AC: 1, 2, 3, 4)
  - [x] Initialiser `missing_fields`, `degradation_reasons`, `source`
  - [x] Remplir `missing_fields` et `degradation_reasons` lors de chaque étape du builder
  - [x] Calculer `context_quality` via `compute_quality()`
  - [x] Construire et retourner `QualifiedContext`

- [x] Mettre à jour les appelants du common context dans `backend/app/llm_orchestration/gateway.py` (AC: 1)
  - [x] Dans `_resolve_plan()` : `qualified_ctx = await CommonContextBuilder.build(...)`
  - [x] Injecter `qualified_ctx.payload` dans les variables de rendu et de contexte
  - [x] Propager `qualified_ctx.context_quality` dans `ResolvedExecutionPlan`

- [x] Étendre `GatewayMeta` dans `backend/app/llm_orchestration/models.py` (AC: 5, 6, 7)
  - [x] Ajouter les 6 nouveaux champs avec valeurs par défaut
  - [x] Assurer la rétrocompatibilité Pydantic

- [x] Mettre à jour `_build_result()` dans `gateway.py` (AC: 5, 7)
  - [x] Calculer `execution_path` sur les axes repair/fallback/test/nominal
  - [x] Remplir `context_quality` et `missing_context_fields`
  - [x] Remplir `normalizations_applied` (depuis validation_result)
  - [x] Synchroniser les anciens booléens `repair_attempted` / `fallback_triggered`

- [x] Créer `backend/app/prompts/tests/test_qualified_context.py` (AC: 8)
  - [x] Test des 3 niveaux de qualité via `compute_quality`
  - [x] Test de `build()` avec mocks pour vérifier les dégradations
  - [x] Test de `is_degraded()`

- [x] Créer `backend/app/llm_orchestration/tests/test_gateway_meta_enrichi.py` (AC: 8)
  - [x] Test des 4 chemins d'exécution dans `GatewayMeta`
  - [x] Test de la synchronisation des booléens legacy
  - [x] Test de la persistance des champs existants

- [x] Mettre à jour `docs/architecture/llm-processus-architecture.md` **avant merge**
  - [x] Documenter `QualifiedContext` et taxonomie des 3 axes
  - [x] Documenter les nouveaux champs de télémétrie dans `GatewayMeta`

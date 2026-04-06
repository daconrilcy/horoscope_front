# Story 66.6 — Qualifier le common context et enrichir `GatewayMeta`

Status: draft

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

1. **Given** que `CommonContextBuilder.build()` retourne actuellement un `PromptCommonContext` sans qualification  
   **When** la story est réalisée  
   **Then** `build()` retourne un `QualifiedContext` encapsulant le payload `PromptCommonContext` et ajoutant : `source: str` (valeur dominante documentée), `missing_fields: list[str]`, `context_quality: Literal["full", "partial", "minimal"]`, `degradation_reasons: list[str]`

2. **Given** que les champs n'ont pas tous le même poids  
   **When** `context_quality` est calculé  
   **Then** il suit les règles de criticité suivantes, par ordre de priorité :
   - `"minimal"` si **les deux sources natales sont absentes** (`natal_data` ET `natal_interpretation` manquent simultanément)
   - `"minimal"` si `astrologer_profile` est absent ET au moins une source natale manque aussi
   - `"partial"` si **une seule source natale** est absente mais l'autre est disponible (ex : `natal_interpretation` absent mais `natal_data` présent → fallback possible)
   - `"partial"` si `astrologer_profile` est absent mais les sources natales sont présentes
   - `"partial"` si un champ secondaire manque seul (`period_covered`, `today_date`)
   - `"full"` si aucun champ manquant
   
   Ces règles sont définies comme constantes dans `CommonContextBuilder` et doivent être testées explicitement

3. **Given** que `source` décrit la provenance du contexte  
   **When** il est calculé  
   **Then** il vaut : `"db"` si tous les champs structurants viennent de la DB, `"partial_db"` si certains champs sont absents mais d'autres ont été trouvés, `"fallback"` si aucun champ de contexte métier n'a pu être chargé — les cas mixtes tombent dans `"partial_db"`

4. **Given** que le gateway reçoit un `QualifiedContext` dégradé  
   **When** `context_quality != "full"`  
   **Then** le log structuré émet un `WARNING` avec les `missing_fields` et `degradation_reasons`

5. **Given** que `GatewayMeta` doit exposer les 3 axes orthogonaux  
   **When** les nouveaux champs sont ajoutés  
   **Then** `GatewayMeta` inclut : `execution_path: Literal["nominal", "repaired", "fallback_use_case", "test_fallback"] = "nominal"`, `context_quality: str = "unknown"`, `missing_context_fields: list[str] = Field(default_factory=list)`, `normalizations_applied: list[str] = Field(default_factory=list)`, `repair_attempts: int = 0`, `fallback_reason: Optional[str] = None` — tous avec valeurs par défaut pour rétrocompatibilité

6. **Given** que des consommateurs existants lisent `GatewayMeta`  
   **When** les nouveaux champs sont ajoutés  
   **Then** les champs existants (`latency_ms`, `cached`, `prompt_version_id`, `persona_id`, `model`, `model_override_active`, `output_schema_id`, `schema_version`, `validation_status`, `repair_attempted`, `fallback_triggered`, `validation_errors`) sont intégralement préservés avec les mêmes valeurs

7. **Given** que `repair_attempted` et `fallback_triggered` booléens existent  
   **When** les nouveaux champs sont ajoutés  
   **Then** ils sont synchronisés : `repair_attempted = repair_attempts > 0`, `fallback_triggered = fallback_reason is not None` — les anciens booléens restent pour rétrocompatibilité ; `execution_path` est le nouveau signal canonique

8. **Given** que les tests couvrent la qualification  
   **When** ils sont exécutés  
   **Then** les 3 valeurs de `context_quality`, les 3 valeurs de `source`, et les 4 valeurs d'`execution_path` sont chacune couvertes par au moins un test

## Tasks / Subtasks

- [ ] Créer le modèle `QualifiedContext` dans `backend/app/prompts/common_context.py` (AC: 1, 2, 3)
  - [ ] Définir : `payload: PromptCommonContext`, `source: str`, `missing_fields: list[str] = Field(default_factory=list)`, `context_quality: Literal["full", "partial", "minimal"] = "full"`, `degradation_reasons: list[str] = Field(default_factory=list)`
  - [ ] Définir les constantes de criticité dans la classe :
    ```python
    _CRITICAL_FIELDS = frozenset({"natal_data", "astrologer_profile"})
    _SECONDARY_FIELDS = frozenset({"natal_interpretation", "period_covered", "today_date"})
    ```
  - [ ] Implémenter `_compute_quality(missing: list[str]) -> Literal["full", "partial", "minimal"]` selon les règles de l'AC2 (méthode statique ou classmethod)
  - [ ] Méthode `def is_degraded(self) -> bool: return self.context_quality != "full"`

- [ ] Modifier `CommonContextBuilder.build()` pour retourner `QualifiedContext` (AC: 1, 2, 3, 4)
  - [ ] Initialiser `missing_fields: list[str] = []`, `degradation_reasons: list[str] = []`, `source = "db"`
  - [ ] Après **étape Persona** (lignes 88-96) : si persona non trouvée → `missing_fields.append("astrologer_profile")`, `degradation_reasons.append("persona_not_found")`
  - [ ] Après **étape User Profile** (lignes 98-104) : si profil incomplet → `missing_fields.append(...)` selon les champs absents
  - [ ] Après **étape Natal Source** (lignes 107-132) : si `natal_interpretation` absent → `missing_fields.append("natal_interpretation")` ; si `natal_data` également absent → `missing_fields.append("natal_data")`, `source = "fallback"`
  - [ ] Si `len(missing_fields) > 0` et `source != "fallback"` : `source = "partial_db"`
  - [ ] Calculer `context_quality` : si tout champ de `_CRITICAL_FIELDS` est dans `missing_fields` → `"minimal"` ; elif `missing_fields` non vide → `"partial"` ; else `"full"`
  - [ ] Construire et retourner `QualifiedContext(payload=prompt_common_context, source=source, missing_fields=missing_fields, context_quality=context_quality, degradation_reasons=degradation_reasons)`

- [ ] Mettre à jour les appelants du common context dans `backend/app/llm_orchestration/gateway.py` (AC: 1)
  - [ ] Dans `_resolve_plan()` (story 66.2) : `qualified_ctx = CommonContextBuilder.build(...)` retourne désormais un `QualifiedContext`
  - [ ] Pour le merge dict : `context_data = qualified_ctx.payload.model_dump()` — puis merge `{**context_data, **request.context.extra_context}`
  - [ ] Setter `plan.context_quality = qualified_ctx.context_quality` dans `ResolvedExecutionPlan`
  - [ ] Si `qualified_ctx.is_degraded()` : logger WARNING avec `missing_fields` et `degradation_reasons`

- [ ] Étendre `GatewayMeta` dans `backend/app/llm_orchestration/models.py` (AC: 5, 6, 7)
  - [ ] Ajouter avec valeurs par défaut : `execution_path: Literal["nominal", "repaired", "fallback_use_case", "test_fallback"] = "nominal"`, `context_quality: str = "unknown"`, `missing_context_fields: list[str] = Field(default_factory=list)`, `normalizations_applied: list[str] = Field(default_factory=list)`, `repair_attempts: int = 0`, `fallback_reason: Optional[str] = None`
  - [ ] Ne pas modifier les 12 champs existants
  - [ ] Note : `execution_path` **ne contient pas** `"degraded_context"` — le contexte dégradé est sur l'axe `context_quality`

- [ ] Mettre à jour `_build_result()` dans `gateway.py` (story 66.4) pour utiliser les nouveaux axes (AC: 5, 7)
  - [ ] `execution_path` : `"repaired"` si `repair_attempts > 0`, `"fallback_use_case"` si `fallback_reason is not None`, `"test_fallback"` si `request.flags.test_fallback_active`, `"nominal"` sinon
  - [ ] `context_quality` : depuis `plan.context_quality` (propagé depuis `QualifiedContext`)
  - [ ] `missing_context_fields` : depuis `qualified_ctx.missing_fields` (passer en paramètre de `_build_result()`)
  - [ ] `normalizations_applied` : depuis `validation_result.normalizations_applied` (story 66.5)
  - [ ] Synchroniser `repair_attempted = repair_attempts > 0` et `fallback_triggered = fallback_reason is not None`

- [ ] Créer `backend/app/prompts/tests/test_qualified_context.py` (AC: 8)
  - [ ] Test `context_quality = "full"` : tous les champs trouvés en DB
  - [ ] Test `context_quality = "partial"` : `natal_interpretation` manquant, mais `natal_data` présent
  - [ ] Test `context_quality = "minimal"` : `natal_data` manquant (champ critique)
  - [ ] Test `source = "fallback"` : ni natal_interpretation ni natal_data trouvés
  - [ ] Test `source = "partial_db"` : persona absente mais natal trouvé
  - [ ] Test `is_degraded()` : True si `context_quality != "full"`
  - [ ] Test règle `"minimal"` : `natal_data` ET `natal_interpretation` absents → `"minimal"`
  - [ ] Test règle `"minimal"` : `astrologer_profile` + une source natale absents → `"minimal"`
  - [ ] Test règle `"partial"` : `natal_interpretation` absent seul mais `natal_data` présent → `"partial"`
  - [ ] Test règle `"partial"` : `astrologer_profile` absent seul → `"partial"`
  - [ ] Test règle `"full"` : aucun champ manquant → `"full"`
  - [ ] Test non-régression — chemins sensibles obligatoires :
    - Common context `"partial"` → `context_quality = "partial"` dans `GatewayMeta`
    - Common context `"minimal"` → WARNING loggué et `missing_context_fields` renseigné
  - [ ] Test `build()` loggue un WARNING si `is_degraded()` (mock logger)

- [ ] Créer `backend/app/llm_orchestration/tests/test_gateway_meta_enrichi.py` (AC: 8)
  - [ ] Test `execution_path = "repaired"` : `repair_attempts=1`
  - [ ] Test `execution_path = "fallback_use_case"` : `fallback_reason="..."`
  - [ ] Test `execution_path = "test_fallback"` : `flags.test_fallback_active=True`
  - [ ] Test `execution_path = "nominal"` : chemin nominal sans repair ni fallback
  - [ ] Test rétrocompatibilité : `repair_attempted = True` quand `repair_attempts=1`
  - [ ] Test rétrocompatibilité : champs existants tous présents dans `GatewayMeta`

- [ ] Mettre à jour `docs/architecture/llm-processus-architecture.md` **avant merge**
  - [ ] Documenter `QualifiedContext` : champs, règles de criticité, valeurs de `context_quality` et `source`
  - [ ] Documenter la taxonomie des 3 axes orthogonaux : `execution_path`, `context_quality`, `normalizations_applied`
  - [ ] Documenter les 6 nouveaux champs de `GatewayMeta` et leur synchronisation avec les anciens booléens

### File List

- `backend/app/prompts/common_context.py` — ajout de `QualifiedContext`, modification de `build()` pour le retourner
- `backend/app/llm_orchestration/models.py` — extension de `GatewayMeta` avec 6 nouveaux champs
- `backend/app/llm_orchestration/gateway.py` — utilisation de `QualifiedContext` dans `_resolve_plan()` et `_build_result()`
- `docs/architecture/llm-processus-architecture.md` — mise à jour obligatoire avant merge

### Contexte architectural

- **`CommonContextBuilder.build()` actuelle** : `backend/app/prompts/common_context.py` ligne 82 — 5 étapes, retourne `PromptCommonContext`. Le merge dans `gateway.py` est `context = {**common_ctx.model_dump(), **context}`. Avec `QualifiedContext`, ce merge devient `{**qualified_ctx.payload.model_dump(), **...}` — changement minimal
- **`PromptCommonContext` validator** : si le modèle Pydantic lève sur des champs absents, `QualifiedContext` doit permettre de créer un payload partiel. Si `PromptCommonContext` a des champs `Optional`, pas de problème. Si certains champs sont requis mais réellement absents : le builder doit construire `PromptCommonContext` avec des valeurs de fallback documentées (ex : `precision_level = "dégradée"`, `astrologer_profile = {}`) plutôt que de lever — la qualification indique la dégradation
- **`GatewayMeta` actuelle** : `models.py` ligne 68 — 12 champs. Les 6 nouveaux champs ajoutés avec `= default` ou `Field(default_factory=...)` garantissent la rétrocompatibilité Pydantic
- **`execution_path` ne couvre pas la dégradation contextuelle** : un appel nominal avec contexte dégradé aura `execution_path="nominal"` et `context_quality="partial"` — les deux axes sont lisibles séparément dans les logs/dashboards
- **`plan.context_quality`** : le champ `context_quality: str = "unknown"` de `ResolvedExecutionPlan` (story 66.2) est mis à jour ici avec la valeur réelle de `QualifiedContext.context_quality`

### Project Structure Notes

- `QualifiedContext` ajouté dans `common_context.py` juste avant la classe `CommonContextBuilder`
- Tests : `backend/app/prompts/tests/` — créer avec `__init__.py` si inexistant
- Tests `GatewayMeta` : `backend/app/llm_orchestration/tests/test_gateway_meta_enrichi.py` (nouveau fichier)

### References

- `CommonContextBuilder.build()` : `backend/app/prompts/common_context.py` ligne 82
- `PromptCommonContext` : ligne 24
- Merge context dans gateway : `backend/app/llm_orchestration/gateway.py` lignes ~705-722
- `GatewayMeta` : `backend/app/llm_orchestration/models.py` ligne 68
- Epic 66 FR66-6, FR66-8, NFR66-3, NFR66-4 : `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md`
- Story 66.2 (`plan.context_quality`) : `_bmad-output/implementation-artifacts/66-2-resolved-execution-plan.md`
- Story 66.5 (`normalizations_applied`) : `_bmad-output/implementation-artifacts/66-5-pipeline-validation-explicite.md`
- Story 66.4 (`_build_result()` signature) : `_bmad-output/implementation-artifacts/66-4-pipeline-gateway-explicite.md`

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

# Story 66.5 — Séparer validation, normalisation et sanitization en étapes explicites

Status: draft

## Story

En tant que **plateforme LLM**,  
je veux **que le traitement de sortie soit structuré en une chaîne de fonctions nommées retournant des modèles explicites**,  
afin de **rendre visibles les transformations appliquées, catégoriser précisément les erreurs, et rendre chaque étape indépendamment testable**.

## Note d'architecture — ordre canonique et conservation de politique

**Ordre canonique non modifiable :** `parse_json` → `validate_schema` → `normalize_fields` → `sanitize_evidence` → agrégation des warnings.

**Conservation de politique métier actuelle :** cette story ne change **pas** la politique de blocage. Le comportement `strict=True` actuel est : warning + `secure_filter` (suppression silencieuse evidence hors catalog) — jamais blocage de la réponse. Cette story rend ce comportement visible et nommé, elle ne le durcit pas. Toute modification de seuil de blocage nécessiterait une décision produit séparée.

## Acceptance Criteria

1. **Given** qu'une réponse LLM brute doit être traitée  
   **When** la chaîne est appliquée  
   **Then** elle passe séquentiellement par 4 fonctions aux retours typés : `parse_json() -> ParseResult`, `validate_schema() -> SchemaValidationResult`, `normalize_fields() -> NormalizationResult`, `sanitize_evidence() -> SanitizationResult` — sans tuples positionnels

2. **Given** qu'une erreur de parsing survient  
   **When** `parse_json()` échoue  
   **Then** `ParseResult.error_category = "parse_error"` et `ParseResult.success = False` — distinct de `"schema_error"` retourné par `validate_schema()` si le schéma JSON est invalide

3. **Given** que des transformations sont appliquées  
   **When** la chaîne est exécutée  
   **Then** chaque étape alimente `normalizations_applied: list[str]` dans le `ValidationResult` final, avec des tags précis : `"v3_disclaimers_stripped"`, `"evidence_alias_normalized"`, `"evidence_filtered_non_catalog"`

4. **Given** que des warnings de cohérence sont détectés  
   **When** la chaîne est exécutée  
   **Then** ils apparaissent dans `ValidationResult.warnings` sans bloquer la réponse — **la politique `strict=True` ne modifie pas les seuils de blocage actuels** ; elle rend visible ce qui était implicite mais ne change pas le comportement produit

5. **Given** que `validate_output()` est la signature publique consommée par `_validate_and_normalize()` du gateway  
   **When** la chaîne est refactorisée  
   **Then** `validate_output()` conserve sa signature externe actuelle et retourne un `ValidationResult` étendu — rétrocompatibilité totale avec les consommateurs existants

6. **Given** que `ValidationResult` expose des listes  
   **When** il est défini  
   **Then** tous les champs liste utilisent `Field(default_factory=list)` pour éviter les mutable defaults Pydantic

7. **Given** que les 4 étapes sont testables indépendamment  
   **When** les tests sont exécutés  
   **Then** chaque fonction a ses propres tests unitaires directs, et `validate_output()` a des tests d'intégration de la chaîne complète

## Tasks / Subtasks

- [ ] Définir les 4 modèles de résultat intermédiaire dans `backend/app/llm_orchestration/services/output_validator.py` (AC: 1, 2)
  - [ ] `ParseResult` : `success: bool`, `data: Optional[dict[str, Any]] = None`, `error_message: Optional[str] = None`, `error_category: Optional[Literal["parse_error"]] = None`, `normalizations_applied: list[str] = Field(default_factory=list)`
  - [ ] `SchemaValidationResult` : `valid: bool`, `errors: list[str] = Field(default_factory=list)`, `error_category: Optional[Literal["schema_error"]] = None`
  - [ ] `NormalizationResult` : `data: dict[str, Any]`, `normalizations_applied: list[str] = Field(default_factory=list)`
  - [ ] `SanitizationResult` : `data: dict[str, Any]`, `normalizations_applied: list[str] = Field(default_factory=list)`, `warnings: list[str] = Field(default_factory=list)`

- [ ] Étendre `ValidationResult` dans `output_validator.py` (AC: 3, 5, 6)
  - [ ] Ajouter `error_category: Optional[Literal["parse_error", "schema_error"]] = None`
  - [ ] Ajouter `normalizations_applied: list[str] = Field(default_factory=list)`
  - [ ] Convertir `errors` et `warnings` existants en `Field(default_factory=list)` si pas déjà le cas
  - [ ] Conserver `valid`, `parsed`, `errors`, `warnings` sans modification de comportement

- [ ] Extraire `parse_json()` depuis `validate_output()` (AC: 1, 2, 3)
  - [ ] Signature : `def parse_json(raw_output: str, schema_version: str) -> ParseResult`
  - [ ] Contenu : `json.loads(raw_output)` ; si V3 : supprimer le champ `disclaimers` si présent → tag `"v3_disclaimers_stripped"` dans `normalizations_applied`
  - [ ] Si `json.loads` échoue : `ParseResult(success=False, error_message=f"parse_error: {e}", error_category="parse_error")`
  - [ ] Si succès : `ParseResult(success=True, data=parsed_dict, normalizations_applied=[...])`

- [ ] Extraire `validate_schema()` depuis `validate_output()` (AC: 1, 2)
  - [ ] Signature : `def validate_schema(data: dict, json_schema: dict) -> SchemaValidationResult`
  - [ ] Contenu : `Draft7Validator(json_schema).iter_errors(data)` formaté `"[path] message"`
  - [ ] Si erreurs : `SchemaValidationResult(valid=False, errors=[...], error_category="schema_error")`

- [ ] Extraire `normalize_fields()` depuis `validate_output()` (AC: 1, 3)
  - [ ] Signature : `def normalize_fields(data: dict, evidence_catalog: Optional[list | dict], use_case: str) -> NormalizationResult`
  - [ ] Contenu : normalisation des alias evidence (actuellement lignes ~245 — ex. "SUN" → "PLANET_SUN_...") → tag `"evidence_alias_normalized"` si au moins un alias transformé
  - [ ] Retourne données normalisées + liste des tags

- [ ] Extraire `sanitize_evidence()` depuis `validate_output()` (AC: 1, 3, 4)
  - [ ] Signature : `def sanitize_evidence(data: dict, evidence_catalog: Optional[list | dict], strict: bool) -> SanitizationResult`
  - [ ] Contenu :
    - Suppression silencieuse evidence non-catalog (lignes ~293-311) → tag `"evidence_filtered_non_catalog"`
    - Hallucination detection (lignes ~247-250) : warning non-bloquant même si `strict=True` — **ne pas bloquer, juste rendre visible**
    - Règle bidirectionnelle evidence/text (lignes ~254-291) → warning
    - Check espaces dans items (lignes ~313-318) → warning
  - [ ] Retourne `SanitizationResult` avec données nettoyées + tags + warnings

- [ ] Refactoriser `validate_output()` comme orchestrateur des 4 étapes (AC: 5)
  - [ ] `parse_result = parse_json(raw_output, schema_version)`
  - [ ] Si `not parse_result.success` : retourner `ValidationResult(valid=False, errors=[parse_result.error_message], error_category="parse_error")`
  - [ ] `schema_result = validate_schema(parse_result.data, json_schema)`
  - [ ] Si `not schema_result.valid` : retourner `ValidationResult(valid=False, parsed=parse_result.data, errors=schema_result.errors, error_category="schema_error")`
  - [ ] `norm_result = normalize_fields(parse_result.data, evidence_catalog, use_case)`
  - [ ] `sanit_result = sanitize_evidence(norm_result.data, evidence_catalog, strict)`
  - [ ] Agréger `normalizations_applied = parse_result.normalizations_applied + norm_result.normalizations_applied + sanit_result.normalizations_applied`
  - [ ] Retourner `ValidationResult(valid=True, parsed=sanit_result.data, warnings=sanit_result.warnings, normalizations_applied=normalizations_applied)`
  - [ ] Conserver les métriques Prometheus (lignes ~323-327) après la chaîne

- [ ] Créer `backend/app/llm_orchestration/tests/test_output_validator_pipeline.py` (AC: 7)
  - [ ] Test `parse_json()` : JSON invalide → `error_category="parse_error"`, `success=False`
  - [ ] Test `parse_json()` V3 : suppression `disclaimers` → tag `"v3_disclaimers_stripped"`
  - [ ] Test `parse_json()` V1 : `disclaimers` conservé si présent
  - [ ] Test `validate_schema()` : schema valide → `valid=True`
  - [ ] Test `validate_schema()` : champ manquant → `valid=False`, `error_category="schema_error"`, erreur formatée `"[field] message"`
  - [ ] Test `normalize_fields()` : alias evidence transformé → tag `"evidence_alias_normalized"`
  - [ ] Test `sanitize_evidence()` : evidence hors catalog supprimée → tag `"evidence_filtered_non_catalog"`
  - [ ] Test `sanitize_evidence()` strict=True : hallucination → warning non-bloquant (pas d'erreur)
  - [ ] Test `validate_output()` chaîne complète : `normalizations_applied` agrège tous les tags
  - [ ] Test `validate_output()` : `ValidationResult` rétrocompatible (champs existants présents)

- [ ] Mettre à jour `docs/architecture/llm-processus-architecture.md` **avant merge**
  - [ ] Documenter l'ordre canonique des 4 étapes et leurs types de retour
  - [ ] Documenter la politique `strict=True` : visible, non-bloquant — et sa sémantique actuelle preservée
  - [ ] Documenter les tags `normalizations_applied` et leur signification

### File List

- `backend/app/llm_orchestration/services/output_validator.py` — ajout de `ParseResult`, `SchemaValidationResult`, `NormalizationResult`, `SanitizationResult` ; extension de `ValidationResult` ; extraction de 4 fonctions ; refactorisation de `validate_output()`
- `docs/architecture/llm-processus-architecture.md` — mise à jour obligatoire avant merge

### Contexte architectural

- **`validate_output()` actuelle** : ligne 163, 333 lignes — une fonction avec 4 phases imbriquées. Préserver signature externe : `(raw_output, json_schema, evidence_catalog, strict, use_case, schema_version) -> ValidationResult`
- **Phase 1 parse (lignes 185-203)** : `json.loads()` + suppression V3 `disclaimers` → `parse_json()`
- **Phase 2 schema (lignes 205-224)** : `Draft7Validator` → `validate_schema()`
- **Phase 3a normalisation alias (ligne ~245)** : normalisation aliases → `normalize_fields()`
- **Phase 3b sanitization (lignes 247-311)** : hallucination check, bidirectional rule, secure filter → `sanitize_evidence()`
- **Métriques Prometheus (lignes 323-327)** : `natal_validation_pass_total` / `natal_validation_fail_total` — rester dans `validate_output()`, après la chaîne, mesurer le résultat final
- **`evidence_catalog` format** : `Optional[list[str] | dict[str, list[str]]]` — les sous-fonctions acceptent les deux types comme `validate_output()` aujourd'hui
- **`strict=True` sémantique actuelle** : dans le code réel, `strict` influence principalement la détection d'hallucination evidence. L'AC 4 dit explicitement de ne pas changer les seuils de blocage — se limiter à rendre visible, pas à durcir

### Project Structure Notes

- Les 4 nouvelles fonctions sont module-level dans `output_validator.py` (même niveau que `validate_output()`)
- Les 4 modèles de résultat intermédiaire sont en tête du fichier, avant `ValidationResult`
- Les tests dans `backend/app/llm_orchestration/tests/test_output_validator_pipeline.py` (nouveau fichier)

### References

- `validate_output()` : `backend/app/llm_orchestration/services/output_validator.py` ligne 163
- `ValidationResult` : ligne 17
- Phase parse : lignes 185-203
- Phase schema : lignes 205-224
- Evidence normalisation : ligne ~245
- Evidence sanitization : lignes 247-311
- Métriques : lignes 323-327
- Epic 66 FR66-7, NFR66-2 : `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md`
- Story 66.4 (`_validate_and_normalize()` consomme `ValidationResult`) : `_bmad-output/implementation-artifacts/66-4-pipeline-gateway-explicite.md`

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

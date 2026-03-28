# Story 61.34 : Normalisation des diffs et scoring de risque des mutations canoniques

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux que chaque ligne d'audit canonique expose un résumé de diff stable et un niveau de risque calculé,
afin de pouvoir identifier immédiatement les mutations sensibles sans devoir comparer manuellement `before_payload` et `after_payload`.

## Contexte

61.32 a créé la trace. 61.33 l'a exposée. 61.34 la rend exploitable.

Les payloads `before_payload` / `after_payload` exposés par 61.33 ont une structure connue et stable :

```json
{
  "is_enabled": bool,
  "access_mode": "quota" | "unlimited" | "disabled",
  "variant_code": str | null,
  "source_origin": str,
  "quotas": [
    {
      "quota_key": str,
      "quota_limit": int | null,
      "period_unit": str,
      "period_value": int,
      "reset_mode": str,
      "source_origin": str
    }
  ]
}
```

Les valeurs d'`access_mode` sont les valeurs `.value` de l'enum `AccessMode` (`backend/app/infra/db/models/product_entitlements.py`) : `"quota"`, `"unlimited"`, `"disabled"` (minuscules). **Ne jamais écrire `QUOTA` ou `UNLIMITED` en majuscules dans les tests ou les règles de scoring.**

`before_payload = {}` signifie création (aucun binding préexistant). Ce cas est détectable de manière fiable.

**Scope strict** : aucune écriture DB, aucune migration Alembic, aucune modification du contrat public métier. Service de diff entièrement stateless (calcul pur, pas d'accès DB).

## Acceptance Criteria

### AC 1 — Champs dérivés exposés dans chaque item d'audit

1. Chaque item retourné par les endpoints 61.33 contient, **en plus** des champs existants, **les 4 champs suivants toujours présents** (jamais `null`, jamais omis) :
   - `change_kind` (str)
   - `changed_fields` (list[str])
   - `risk_level` (str)
   - `quota_changes` (objet avec `added`, `removed`, `updated`)

2. Les payloads bruts `before_payload` / `after_payload` restent **conditionnels** : présents uniquement si `include_payloads=true`, absents sinon (comportement 61.33 inchangé).

> **Règle de schéma Pydantic** : dans `MutationAuditItem`, les 4 champs dérivés sont déclarés **non-optionnels** (sans `= None`). Seuls `before_payload` et `after_payload` restent `dict | None = None`.

### AC 2 — change_kind

3. `change_kind = "binding_created"` si `before_payload == {}`.
4. `change_kind = "binding_updated"` sinon.

### AC 3 — changed_fields

5. `changed_fields` est une liste stable et triée de chemins métier. Seuls les champs ayant effectivement changé entre `before_payload` et `after_payload` y figurent.
6. Chemins de binding reconnus : `binding.is_enabled`, `binding.access_mode`, `binding.variant_code`, `binding.source_origin`.
7. Chemin quota : `quotas[{quota_key},{period_unit},{period_value},{reset_mode}].quota_limit` — présent dans `changed_fields` uniquement si un quota **conservé** (présent dans before ET after avec la même clé composite) a vu son `quota_limit` changer.
8. **`changed_fields` ne porte PAS les ajouts ni suppressions de quotas** — ceux-ci sont portés exclusivement par `quota_changes.added` et `quota_changes.removed`. La liste `changed_fields` ne contient jamais de chemin du type `quotas[...].added` ou `quotas[...].removed`.
9. Si `change_kind = "binding_created"`, `changed_fields = []` (création complète — pas de champ individuellement modifié).
10. Si `before_payload == after_payload` (no-op historique), `changed_fields = []`.

### AC 4 — quota_changes

10. `quota_changes.added` : liste des quotas présents dans `after_payload.quotas` mais absents de `before_payload.quotas` (identifié par la clé composite `(quota_key, period_unit, period_value, reset_mode)`).
11. `quota_changes.removed` : liste des quotas présents dans `before_payload.quotas` mais absents de `after_payload.quotas`.
12. `quota_changes.updated` : liste des quotas présents dans les deux payloads dont `quota_limit` a changé.
13. Format exact de chaque entrée :
    - **`added`** : `{ quota_key, period_unit, period_value, reset_mode, quota_limit, source_origin }` — valeurs du `after_payload`
    - **`removed`** : `{ quota_key, period_unit, period_value, reset_mode, quota_limit, source_origin }` — valeurs du `before_payload`
    - **`updated`** : `{ quota_key, period_unit, period_value, reset_mode, quota_limit, source_origin, before_quota_limit }` — `quota_limit` = valeur after, `before_quota_limit` = valeur before
14. Si `change_kind = "binding_created"` : `quota_changes = {"added": [...quotas du after], "removed": [], "updated": []}`.

### AC 5 — risk_level

15. `risk_level = "high"` si **au moins une** des conditions suivantes est vraie :
    - `binding.access_mode` change
    - `binding.is_enabled` change
    - Un quota est supprimé (`quota_changes.removed` non vide)
    - Un `quota_limit` diminue (valeur numérique strictement inférieure dans `after`)
16. `risk_level = "medium"` si aucune condition `high` et **au moins une** :
    - Un quota est ajouté (`quota_changes.added` non vide)
    - Un `quota_limit` augmente
    - `binding.variant_code` change
17. `risk_level = "low"` sinon (seuls `binding.source_origin` et les champs purement descriptifs changent, ou aucun changement).
18. Pour `change_kind = "binding_created"` : `risk_level` calculé uniquement sur `after_payload.access_mode` :
    - `high` si `access_mode = "quota"`
    - `medium` si `access_mode = "unlimited"`
    - `low` si `access_mode = "disabled"`
    - `medium` si `access_mode` absent (cas dégradé)

### AC 6 — Enrichissement sans rupture des endpoints 61.33

19. `GET /v1/ops/entitlements/mutation-audits` : chaque item inclut les 4 champs dérivés.
20. `GET /v1/ops/entitlements/mutation-audits/{audit_id}` : l'item inclut les 4 champs dérivés.
21. `response_model_exclude_none=True` reste actif — les sous-champs optionnels nuls sont omis.
22. Les tests 61.33 existants (`test_ops_entitlement_mutation_audits_api.py`) restent verts (pas de régression).

### AC 7 — Nouveaux filtres ops (application-level)

23. `GET /v1/ops/entitlements/mutation-audits` accepte 3 nouveaux paramètres de filtre optionnels, **typés strictement** :
    - `risk_level` (valeurs valides : `high`, `medium`, `low` — toute autre valeur → 422 FastAPI natif)
    - `change_kind` (valeurs valides : `binding_created`, `binding_updated` — toute autre valeur → 422)
    - `changed_field` (str libre : chemin exact, ex. `binding.is_enabled`)
    - Déclarer `risk_level` et `change_kind` avec `Literal["high", "medium", "low"]` / `Literal["binding_created", "binding_updated"]` dans les paramètres Query pour obtenir la validation 422 automatiquement.
24. Quand ces filtres sont présents, le filtrage opère **après** le calcul du diff (application-level) — les filtres SQL existants sont appliqués d'abord.
25. La pagination dans la réponse (`total_count`, `page`, `page_size`) reflète les résultats **après** filtrage par diff.
26. En l'absence de ces filtres, le comportement et les performances sont inchangés (pagination SQL directe, diff calculé par page).
27. **Stratégie de chargement avec filtre diff** : charger jusqu'à un maximum de **10 000 audits** depuis SQL (après filtres SQL), calculer les diffs en mémoire, puis paginer manuellement. Si le nombre de résultats SQL dépasse 10 000, retourner une erreur **400** avec `code="diff_filter_result_set_too_large"` et `details={"sql_count": N, "max_allowed": 10000}`. La borne 10 000 est un garde-fou documenté, pas une limite silencieuse.

### AC 8 — Service de diff dédié

27. Un service `CanonicalEntitlementMutationDiffService` est créé dans `backend/app/services/canonical_entitlement_mutation_diff_service.py`.
28. Ce service est **purement stateless** : aucune injection DB, aucun accès réseau. Méthode(s) `@staticmethod`.
29. Interface publique minimale :
    - `compute_diff(before_payload: dict, after_payload: dict) -> MutationDiffResult`
30. `MutationDiffResult` est un dataclass ou Pydantic model interne (pas exposé dans le contrat API) contenant : `change_kind`, `changed_fields`, `risk_level`, `quota_changes`.
31. Le router est le seul responsable de la sérialisation de `MutationDiffResult` vers la réponse JSON.
32. `CanonicalEntitlementMutationAuditQueryService` n'est **pas modifié** (reste pure SQL).

### AC 9 — Tests unitaires du service de diff

33. `backend/app/tests/unit/test_canonical_entitlement_mutation_diff_service.py` est créé avec au minimum :
    - `test_binding_created_empty_before` : `before={}` → `change_kind=binding_created`
    - `test_binding_updated_is_enabled_change` : `is_enabled` true→false → `risk_level=high`, `binding.is_enabled` dans `changed_fields`
    - `test_access_mode_change_unlimited_to_quota` : `access_mode` change → `risk_level=high`
    - `test_quota_limit_decrease` : quota_limit diminue → `risk_level=high`
    - `test_quota_limit_increase` : quota_limit augmente → `risk_level=medium`
    - `test_quota_added` : quota ajouté → dans `quota_changes.added`, `risk_level=medium`
    - `test_quota_removed` : quota supprimé → dans `quota_changes.removed`, `risk_level=high`
    - `test_variant_code_change` : variant_code change → `risk_level=medium`, `binding.variant_code` dans `changed_fields`
    - `test_source_origin_only_change` : seul `source_origin` change → `risk_level=low`
    - `test_noop_before_equals_after` : before==after → `changed_fields=[]`, `risk_level=low`
    - `test_quota_key_path_format` : chemin quota dans `changed_fields` au bon format
    - `test_binding_created_quota_access_mode` : création avec `access_mode="quota"` → `risk_level=high`
    - `test_binding_created_disabled_access_mode` : création avec `access_mode="disabled"` → `risk_level=low`
    - `test_changed_fields_no_quota_path_for_added` : quota ajouté → chemin quota absent de `changed_fields`
    - `test_changed_fields_no_quota_path_for_removed` : quota supprimé → chemin quota absent de `changed_fields`

### AC 10 — Tests d'intégration des filtres diff

34. `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` est enrichi avec :
    - `test_list_includes_diff_fields` : chaque item contient `change_kind`, `risk_level`, `changed_fields`, `quota_changes`
    - `test_filter_by_risk_level` : filtre `risk_level=high` retourne uniquement les audits à risque élevé
    - `test_filter_by_change_kind` : filtre `change_kind=binding_created` retourne uniquement les créations
    - `test_filter_by_changed_field` : filtre `changed_field=binding.is_enabled` retourne uniquement les audits où ce champ a changé
    - `test_detail_includes_diff_fields` : endpoint détail inclut les champs dérivés
    - `test_filter_invalid_risk_level_returns_422` : `risk_level=extreme` → 422 FastAPI natif
    - `test_filter_invalid_change_kind_returns_422` : `change_kind=foo` → 422 FastAPI natif

### AC 11 — Aucune écriture DB, aucune migration

35. Aucune migration Alembic.
36. Aucune colonne ajoutée à `canonical_entitlement_mutation_audits`.
37. Aucun `db.add()`, `db.flush()`, `db.commit()` dans le diff service ou dans le chemin de calcul du diff.

### AC 12 — Documentation

38. `backend/docs/entitlements-canonical-platform.md` est mis à jour avec une section **"Story 61.34 — Normalisation des diffs et scoring de risque"** décrivant :
    - les 4 champs dérivés et leur sémantique
    - les règles de calcul de `risk_level`
    - les nouveaux filtres `risk_level`, `change_kind`, `changed_field`

---

## Tasks / Subtasks

- [x] **Créer `CanonicalEntitlementMutationDiffService`** (AC: 8, 9)
  - [x] Créer `backend/app/services/canonical_entitlement_mutation_diff_service.py`
  - [x] Définir dataclass/pydantic interne `QuotaChangeSummary` + `MutationDiffResult`
  - [x] Implémenter `compute_diff(before_payload, after_payload) -> MutationDiffResult`
  - [x] Implémenter logique `change_kind` (before=={} → created)
  - [x] Implémenter logique `changed_fields` (liste triée stable)
  - [x] Implémenter logique `quota_changes` (added/removed/updated avec clé composite)
  - [x] Implémenter logique `risk_level` (high/medium/low avec règles explicites)

- [x] **Étendre les schémas Pydantic du router** (AC: 1, 6)
  - [x] Ajouter `QuotaChangeSummary` schema (added, removed, updated)
  - [x] Étendre `MutationAuditItem` avec `change_kind`, `changed_fields`, `risk_level`, `quota_changes` (tous optionnels avec `= None` pour `exclude_none`)

- [x] **Étendre `_to_item` dans le router** (AC: 1, 6)
  - [x] Appeler `CanonicalEntitlementMutationDiffService.compute_diff(audit.before_payload, audit.after_payload)`
  - [x] Ajouter les 4 champs dérivés au dict retourné
  - [x] Conserver `response_model_exclude_none=True` sur les endpoints

- [x] **Ajouter les filtres diff au router** (AC: 7)
  - [x] Ajouter params `risk_level`, `change_kind`, `changed_field` à `list_mutation_audits`
  - [x] Si au moins un filtre diff actif : charger toutes les pages SQL correspondantes (loop), calculer diff, filtrer, paginer manuellement
  - [x] Sinon : comportement inchangé (SQL-paginated + diff calculé par page)

- [x] **Créer tests unitaires du service de diff** (AC: 9)
  - [x] `backend/app/tests/unit/test_canonical_entitlement_mutation_diff_service.py`
  - [x] Couvrir les 11 cas listés en AC 9

- [x] **Enrichir les tests d'intégration** (AC: 10)
  - [x] Ajouter les 5 nouveaux cas dans `test_ops_entitlement_mutation_audits_api.py`
  - [x] S'assurer que les 22 tests existants restent verts (AC 6, 11)

- [x] **Mettre à jour la documentation** (AC: 12)
  - [x] `backend/docs/entitlements-canonical-platform.md`

- [x] **Validation finale**
  - [x] `ruff check` sur les fichiers créés/modifiés
  - [x] `pytest backend/app/tests/unit/test_canonical_entitlement_mutation_diff_service.py`
  - [x] `pytest backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py`

---

## Dev Notes

### Architecture

**Fichiers à créer / modifier :**

| Fichier | Action |
|---------|--------|
| `backend/app/services/canonical_entitlement_mutation_diff_service.py` | Créer |
| `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` | Modifier — schémas + `_to_item` + filtres diff |
| `backend/app/tests/unit/test_canonical_entitlement_mutation_diff_service.py` | Créer |
| `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` | Modifier — 5 nouveaux tests |
| `backend/docs/entitlements-canonical-platform.md` | Mettre à jour |

**NE PAS modifier** :
- `backend/app/services/canonical_entitlement_mutation_audit_query_service.py` (reste pur SQL)
- `backend/app/infra/db/models/canonical_entitlement_mutation_audit.py` (aucune migration)
- Aucun autre contrat API public

### Project Structure Notes

- Services read-only / calcul pur : `backend/app/services/*.py`
- Router ops : `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` (déjà créé en 61.33)
- Tests unitaires : `backend/app/tests/unit/test_*.py`
- Tests intégration : `backend/app/tests/integration/test_*_api.py`

### Références

- [Source: backend/app/services/canonical_entitlement_mutation_service.py#_snapshot_binding_by_id] — structure exacte des payloads before/after
- [Source: backend/app/api/v1/routers/ops_entitlement_mutation_audits.py] — router 61.33 à étendre
- [Source: backend/app/services/canonical_entitlement_mutation_audit_query_service.py] — query service SQL (ne pas modifier)
- [Source: backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py] — tests 61.33 à étendre (22 tests existants)
- [Source: backend/docs/entitlements-canonical-platform.md] — doc à compléter

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/services/canonical_entitlement_mutation_diff_service.py`
- `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py`
- `backend/app/tests/unit/test_canonical_entitlement_mutation_diff_service.py`
- `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py`
- `backend/docs/entitlements-canonical-platform.md`

### Change Log

- 2026-03-28 : Story 61.34 créée.
- 2026-03-28 : Implémentation du service de diff et scoring de risque.
- 2026-03-28 : Extension du router ops avec enrichissement diff et filtres application-level.
- 2026-03-28 : Ajout des tests unitaires et d'intégration.
- 2026-03-28 : Mise à jour de la documentation architecture.

# Story 61.48 : Branchement runtime unifié des gates produit sur le resolver effectif

Status: done

## Story

En tant que système backend,
je veux que les contrôles d'accès produit utilisent le resolver de droits effectifs comme source de vérité unique,
afin que toutes les features appliquent exactement les mêmes règles de plan commercial, billing et quota.

---

## Contexte métier et enjeu architectural

La story 61.47 a introduit `EffectiveEntitlementResolverService`, qui produit un snapshot read-only des droits effectifs pour un sujet B2C ou B2B.

Le point qui reste à fermer est simple : les gates métier encore actives ne doivent plus reconstruire chacune leur propre logique d'accès à partir de services legacy, de lectures SQL directes ou de reason codes ad hoc. La décision d'accès doit venir d'une seule source : `EffectiveFeatureAccess`.

**Scope de la story :**
- `ChatEntitlementGate`
- `ThematicConsultationEntitlementGate`
- `NatalChartLongEntitlementGate`
- `B2BApiEntitlementGate`

**Hors scope :**
- nouveau modèle de données
- nouvelle API publique
- modification du resolver 61.47 lui-même
- suppression globale de `EntitlementService` pour ses autres usages éventuels

---

## Acceptance Criteria

### AC 1 — Branchement resolver sur les gates B2C

1. [x] `ChatEntitlementGate`, `ThematicConsultationEntitlementGate` et `NatalChartLongEntitlementGate` appellent `EffectiveEntitlementResolverService.resolve_b2c_user_snapshot()`.
2. [x] Chaque gate extrait l'entrée de sa feature cible depuis `snapshot.entitlements`.
3. [x] La décision d'accès se fait uniquement sur `access.granted` et `access.reason_code`.

### AC 2 — Branchement resolver sur la gate B2B

4. [x] `B2BApiEntitlementGate` appelle `EffectiveEntitlementResolverService.resolve_b2b_account_snapshot()`.
5. [x] La gate extrait `snapshot.entitlements["b2b_api_access"]`.
6. [x] Les lectures directes de `PlanFeatureBindingModel`, `PlanFeatureQuotaModel`, `FeatureCatalogModel` ou équivalent sont supprimées de la gate.

### AC 3 — Pattern de décision uniforme

7. [x] Le pattern d'exécution est identique dans les 4 gates :
   - résolution d'un snapshot read-only ;
   - lecture du `EffectiveFeatureAccess` cible ;
   - si `granted == false` :
     - `quota_exhausted` → erreur métier de quota (`429`) ;
     - toute autre raison (`feature_not_in_plan`, `billing_inactive`, `binding_disabled`, `subject_not_eligible`) → erreur métier d'accès (`403`) ;
   - si `granted == true` et `access_mode == "quota"` → consommation transactionnelle via le service de quota déjà en place ;
   - si `granted == true` et `access_mode == "unlimited"` → aucune consommation.

### AC 4 — Harmonisation des erreurs

8. [x] Les 4 chemins exposent un `reason_code` normalisé dans `details`.
9. [x] Les contrats HTTP existants ne sont pas cassés :
   - `403` pour refus structurel ;
   - `429` pour quota épuisé ;
   - les champs `code` et `message` existants sont conservés.

### AC 5 — Fin des lectures canoniques ad hoc dans les gates

10. [x] Après implémentation, aucun des 4 fichiers gate ne contient d'accès direct aux tables canoniques des plans/bindings/quotas.
11. [x] Les seules lectures autorisées dans les gates sont :
   - le resolver effectif ;
   - les services de consommation de quota déjà standardisés.

### AC 6 — Tests d'intégration

12. [x] Les tests d'intégration couvrent, pour chacune des 4 features :
   - accès autorisé ;
   - refus car feature absente du plan ;
   - refus car billing inactif ;
   - quota épuisé quand la feature est à quota.

### AC 7 — Non-régression

13. [x] Aucun endpoint public nouveau.
14. [x] Aucune migration Alembic.
15. [x] `EffectiveEntitlementResolverService` n'est pas modifié dans cette story.
16. [x] Les tests unitaires et d'intégration existants des gates restent verts après adaptation de leurs mocks au resolver.

---

## Tasks / Subtasks

- [x] **Migrer `ChatEntitlementGate`** (AC: 1, 3, 4, 5)
  - [x] Remplacer la lecture actuelle par `resolve_b2c_user_snapshot()`
  - [x] Extraire `snapshot.entitlements["astrologer_chat"]`
  - [x] Mapper `reason_code` vers les erreurs métier existantes
  - [x] Enrichir le payload d'erreur du routeur avec `details.reason_code`

- [x] **Migrer `ThematicConsultationEntitlementGate`** (AC: 1, 3, 4, 5)
  - [x] Remplacer la lecture actuelle par `resolve_b2c_user_snapshot()`
  - [x] Extraire `snapshot.entitlements["thematic_consultation"]`
  - [x] Mapper `reason_code` vers les erreurs métier existantes
  - [x] Enrichir le payload d'erreur du routeur avec `details.reason_code`

- [x] **Migrer `NatalChartLongEntitlementGate`** (AC: 1, 3, 4, 5)
  - [x] Remplacer la lecture actuelle par `resolve_b2c_user_snapshot()`
  - [x] Extraire `snapshot.entitlements["natal_chart_long"]`
  - [x] Mapper `reason_code` vers les erreurs métier existantes
  - [x] Enrichir le payload d'erreur du routeur avec `details.reason_code`

- [x] **Migrer `B2BApiEntitlementGate`** (AC: 2, 3, 4, 5)
  - [x] Remplacer la logique SQL ad hoc par `resolve_b2b_account_snapshot()`
  - [x] Extraire `snapshot.entitlements["b2b_api_access"]`
  - [x] Supprimer les imports canonique devenus inutiles
  - [x] Enrichir le payload d'erreur du routeur avec `details.reason_code`

- [x] **Aligner les tests** (AC: 6, 7)
  - [x] Adapter les tests unitaires des 4 gates au nouveau point d'entrée resolver
  - [x] Ajouter les scénarios d'intégration manquants
  - [x] Vérifier les mappings `403` / `429`

---

## Dev Notes

### Guardrails

- Aucune migration Alembic
- Aucun nouvel endpoint
- Aucune écriture dans le resolver
- La consommation de quota reste dans les gates, après décision d'accès

### Pattern recommandé

```python
snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
    db,
    app_user_id=user_id,
)
access = snapshot.entitlements.get(FEATURE_CODE)

if not access or not access.granted:
    reason_code = access.reason_code if access else "subject_not_eligible"
    if reason_code == "quota_exhausted":
        raise QuotaExceededError(...)
    raise AccessDeniedError(reason=reason_code, ...)

if access.access_mode == "unlimited":
    return ...

# access_mode == "quota"
# consommation transactionnelle via le service de quota déjà en place
```

### Important

- Le resolver décide **si** l'accès est accordé.
- Les gates restent responsables du **moment de consommation** et du rollback applicatif si l'opération métier échoue ensuite.
- Ne pas réintroduire de branchement sur des bindings/quotas canoniques dans les gates sous prétexte de reconstituer un quota : utiliser soit les métadonnées déjà exposées par le snapshot, soit un helper partagé déjà existant, mais pas une logique SQL parallèle.

### Fichiers cibles

```text
backend/app/services/chat_entitlement_gate.py
backend/app/services/thematic_consultation_entitlement_gate.py
backend/app/services/natal_chart_long_entitlement_gate.py
backend/app/services/b2b_api_entitlement_gate.py

backend/app/api/v1/routers/chat.py
backend/app/api/v1/routers/consultations.py
backend/app/api/v1/routers/natal_interpretation.py
backend/app/api/v1/routers/b2b_astrology.py
```

### References

- `backend/app/services/effective_entitlement_resolver_service.py`
- `backend/app/services/entitlement_types.py`
- `backend/app/tests/unit/test_effective_entitlement_resolver_service.py`
- `backend/app/tests/integration/test_chat_entitlement.py`
- `backend/app/tests/integration/test_thematic_consultation_entitlement.py`
- `backend/app/tests/integration/test_natal_chart_long_entitlement.py`
- `backend/app/tests/integration/test_b2b_api_entitlements.py`

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6 (via Gemini CLI)

### Debug Log References

- N/A

### Completion Notes List

- Migration des 4 gates (`Chat`, `ThematicConsultation`, `NatalChartLong`, `B2BApi`) vers `EffectiveEntitlementResolverService`.
- Suppression des lectures SQL directes dans `B2BApiEntitlementGate`.
- Harmonisation du pattern de décision (snapshot -> check access -> consume if needed).
- Revue corrective post-implémentation: restauration des contrats HTTP legacy (`code` / `reason`) avec ajout séparé de `details.reason_code`.
- Correction de la remontée du vrai `quota_key` et de la vraie fenêtre de quota depuis `usage_states` au lieu d'un fallback sur le code feature.
- Ajout d'un helper partagé pour éviter la duplication des mappings B2C et de la sélection du quota pertinent.
- Enrichissement des payloads d'erreur avec `reason_code` dans les 4 routeurs, y compris les réponses `429`.
- Création de nouveaux tests unitaires `_v2.py` pour chaque gate mockant le resolver.
- Mise à jour des tests unitaires existants pour utiliser le resolver.
- Mise à jour des tests d'intégration pour patcher le resolver via un helper dynamique simulant l'état de la DB seedée.
- Vérification locale après revue: `ruff check` ciblé vert et `80` tests unitaires/intégration ciblés verts (68 classiques + 12 `_v2`).

### File List

- `backend/app/services/effective_entitlement_gate_helpers.py`
- `backend/app/services/chat_entitlement_gate.py`
- `backend/app/services/thematic_consultation_entitlement_gate.py`
- `backend/app/services/natal_chart_long_entitlement_gate.py`
- `backend/app/services/b2b_api_entitlement_gate.py`
- `backend/app/api/v1/routers/chat.py`
- `backend/app/api/v1/routers/consultations.py`
- `backend/app/api/v1/routers/natal_interpretation.py`
- `backend/app/api/v1/routers/b2b_astrology.py`
- `backend/app/tests/unit/test_chat_entitlement_gate.py`
- `backend/app/tests/unit/test_chat_entitlement_gate_v2.py`
- `backend/app/tests/unit/test_thematic_consultation_entitlement_gate.py`
- `backend/app/tests/unit/test_thematic_consultation_entitlement_gate_v2.py`
- `backend/app/tests/unit/test_natal_chart_long_entitlement_gate.py`
- `backend/app/tests/unit/test_natal_chart_long_entitlement_gate_v2.py`
- `backend/app/tests/unit/test_b2b_api_entitlement_gate.py`
- `backend/app/tests/unit/test_b2b_api_entitlement_gate_v2.py`
- `backend/app/tests/integration/test_thematic_consultation_entitlement.py`
- `backend/app/tests/integration/test_natal_chart_long_entitlement.py`
- `backend/app/tests/integration/test_b2b_api_entitlements.py`

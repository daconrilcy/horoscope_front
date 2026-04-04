# Story 64.4 — Upgrade hints dans EntitlementsMeResponse (backward compatible)

Status: todo

## Story

En tant que frontend,
je veux que l'endpoint `/v1/entitlements/me` retourne, en plus des droits existants, une liste d'`upgrade_hints` structurés indiquant pour chaque feature bridée quel plan cibler et quel bénéfice débloquer,
afin de piloter les CTA d'upgrade sans contenir aucune logique métier de plan côté frontend.

## Context

**Indépendante des stories 64.1, 64.2, 64.3** — peut être développée en parallèle.

L'endpoint `/v1/entitlements/me` retourne déjà `EntitlementsMeResponse` avec `plan_code`, `billing_status`, et `features: list[FeatureEntitlementResponse]`.

Cette story enrichit la réponse de manière **additive** (aucun champ existant n'est modifié ou retiré) — backward compatible pour tous les consommateurs actuels.

**Contrat UpgradeHint arrêté :**
```python
{
  feature_code: str,
  current_plan_code: str,
  target_plan_code: str,
  benefit_key: str,        # clé i18n — résolue côté frontend
  cta_variant: Literal["banner", "inline", "modal"],
  priority: int            # ordre d'affichage si plusieurs hints
}
```

**Logique de calcul des hints :**
- Pour chaque feature du snapshot : si `granted=False` OU `variant_code` est restreint (ex: "summary_only", "free_short") → calculer le hint
- `target_plan_code` est déterminé depuis le plan catalog DB (plan suivant dans la hiérarchie)
- `benefit_key` est une clé de message i18n (ex: `"upgrade.horoscope_daily.full_access"`)
- `cta_variant` et `priority` sont configurés par feature (via mapping ou DB)

## Acceptance Criteria

**AC1 — Nouveau champ upgrade_hints dans EntitlementsMeData**
**Given** le schéma `EntitlementsMeData` (`backend/app/api/v1/schemas/entitlements.py`)  
**When** le fichier est inspecté  
**Then** `upgrade_hints: list[UpgradeHintResponse]` est présent avec une valeur par défaut de liste vide  
**And** le champ est optionnel (défaut `[]`) pour garantir la backward compatibility

**AC2 — Schéma UpgradeHintResponse défini**
**Given** `backend/app/api/v1/schemas/entitlements.py`  
**When** le fichier est inspecté  
**Then** `UpgradeHintResponse` est un `BaseModel` Pydantic avec les champs :
`feature_code`, `current_plan_code`, `target_plan_code`, `benefit_key`, `cta_variant`, `priority`  
**And** `cta_variant` est validé comme `Literal["banner", "inline", "modal"]`

**AC3 — Hints calculés dynamiquement pour les features bridées**
**Given** un utilisateur free  
**When** `GET /v1/entitlements/me` est appelé  
**Then** `upgrade_hints` contient au moins un hint pour les features accessibles en mode restreint (ex: `horoscope_daily` avec `variant_code="summary_only"`)  
**And** chaque hint contient `target_plan_code` cohérent avec le catalog en base

**AC4 — Backward compatibility : réponse inchangée structurellement**
**Given** un consommateur existant qui ne lit pas `upgrade_hints`  
**When** `GET /v1/entitlements/me` est appelé  
**Then** tous les champs existants (`plan_code`, `billing_status`, `features`) sont identiques à avant  
**And** `upgrade_hints` est simplement un champ additionnel qui peut être ignoré

**AC5 — Hints absents pour les utilisateurs premium**
**Given** un utilisateur premium  
**When** `GET /v1/entitlements/me` est appelé  
**Then** `upgrade_hints` est une liste vide `[]`

**AC6 — Tests unitaires**
**Given** `backend/app/tests/unit/test_entitlements_me_endpoint.py` (existant) et un nouveau test  
**When** les tests sont exécutés  
**Then** la génération des hints pour free, basic, et premium est couverte  
**And** la backward compatibility (champ optionnel avec défaut []) est vérifiée

**AC7 — Test d'intégration**
**Given** `backend/app/tests/integration/test_entitlements_me_contract.py` (existant)  
**When** le test est exécuté  
**Then** la réponse contient `upgrade_hints` avec le contrat attendu pour un utilisateur free

**AC8 — Zéro régression**
**When** `pytest backend/` est exécuté  
**Then** 0 régression sur les tests entitlements existants

## Tasks / Subtasks

- [ ] T1 — Définir `UpgradeHintResponse` dans les schémas (AC1, AC2)
  - [ ] T1.1 Lire entièrement `backend/app/api/v1/schemas/entitlements.py`
  - [ ] T1.2 Ajouter :
    ```python
    from typing import Literal

    class UpgradeHintResponse(BaseModel):
        feature_code: str
        current_plan_code: str
        target_plan_code: str
        benefit_key: str
        cta_variant: Literal["banner", "inline", "modal"]
        priority: int
    ```
  - [ ] T1.3 Ajouter `upgrade_hints: list[UpgradeHintResponse] = Field(default_factory=list)` dans `EntitlementsMeData`

- [ ] T2 — Définir le dataclass interne `UpgradeHint` côté services (AC3)
  - [ ] T2.1 Ajouter dans `backend/app/services/entitlement_types.py` :
    ```python
    @dataclass(frozen=True)
    class UpgradeHint:
        feature_code: str
        current_plan_code: str
        target_plan_code: str
        benefit_key: str
        cta_variant: str  # "banner" | "inline" | "modal"
        priority: int
    ```

- [ ] T3 — Implémenter `compute_upgrade_hints()` dans `EffectiveEntitlementResolverService` (AC3, AC5)
  - [ ] T3.1 Lire `backend/app/services/effective_entitlement_resolver_service.py`
  - [ ] T3.2 Créer une méthode statique `compute_upgrade_hints(snapshot: EffectiveEntitlementsSnapshot, db: Session) -> list[UpgradeHint]`
  - [ ] T3.3 Logique :
    ```python
    hints = []
    for feature_code, access in snapshot.entitlements.items():
        if not access.granted or _is_restricted_variant(access.variant_code):
            target_plan = _get_next_plan(snapshot.plan_code, db)  # depuis PlanCatalogModel
            if target_plan:
                hints.append(UpgradeHint(
                    feature_code=feature_code,
                    current_plan_code=snapshot.plan_code,
                    target_plan_code=target_plan.plan_code,
                    benefit_key=f"upgrade.{feature_code}.unlock",
                    cta_variant=_get_cta_variant(feature_code),
                    priority=_get_hint_priority(feature_code),
                ))
    return sorted(hints, key=lambda h: h.priority)
    ```
  - [ ] T3.4 Implémenter `_get_next_plan(current_plan_code, db)` en lisant `PlanCatalogModel` trié par prix
  - [ ] T3.5 Implémenter `_is_restricted_variant(variant_code)` : retourne True pour "summary_only", "free_short"
  - [ ] T3.6 Définir `_get_cta_variant(feature_code)` et `_get_hint_priority(feature_code)` avec un mapping de configuration

- [ ] T4 — Intégrer dans le router entitlements (AC3, AC4)
  - [ ] T4.1 Lire `backend/app/api/v1/routers/entitlements.py`
  - [ ] T4.2 Dans le handler `GET /me`, appeler `compute_upgrade_hints(snapshot, db)` après la résolution du snapshot
  - [ ] T4.3 Mapper `list[UpgradeHint]` → `list[UpgradeHintResponse]` avant la réponse

- [ ] T5 — Tests unitaires (AC6)
  - [ ] T5.1 Ajouter dans `backend/app/tests/unit/test_entitlements_me_endpoint.py` :
    - Test : user free → upgrade_hints non vide
    - Test : user premium → upgrade_hints vide
    - Test : backward compat — champ absent si liste vide (ou présent avec [])
  - [ ] T5.2 Créer `backend/app/tests/unit/test_upgrade_hints_service.py`
    - Test : `_is_restricted_variant("summary_only")` → True
    - Test : `_get_next_plan("free", ...)` → "basic"
    - Test : `_get_next_plan("premium", ...)` → None

- [ ] T6 — Test d'intégration (AC7)
  - [ ] T6.1 Mettre à jour `backend/app/tests/integration/test_entitlements_me_contract.py`
  - [ ] T6.2 Vérifier que la réponse JSON contient `upgrade_hints` avec le contrat attendu

- [ ] T7 — Validation finale (AC8)
  - [ ] T7.1 `pytest backend/` → 0 régression
  - [ ] T7.2 `ruff check backend/` → 0 erreur

## Dev Notes

### Backward compatibility garantie

Le champ `upgrade_hints` étant déclaré avec `default_factory=list` dans Pydantic, il sera présent dans toutes les réponses (même si vide). Cela est préférable à un champ `Optional` qui pourrait retourner `null` et casser les consommateurs TypeScript qui s'attendraient à un tableau.

### Hiérarchie des plans

La hiérarchie `free → basic → premium` est implicite dans les prix (`monthly_price_cents` croissant). Utiliser `PlanCatalogModel` trié par `monthly_price_cents ASC` pour déterminer le plan suivant. Si `plan_code` n'est pas dans le catalog (ex: "none"), aucun hint n'est généré.

### benefit_key convention

Les `benefit_key` suivent le pattern `"upgrade.{feature_code}.{benefit_type}"`. Exemples :
- `"upgrade.horoscope_daily.full_access"` → traduit côté frontend en "Accédez à l'horoscope complet"
- `"upgrade.natal_chart_long.full_interpretation"` → "Débloquez l'interprétation complète de votre thème"
- `"upgrade.astrologer_chat.unlimited_messages"` → "Échangez sans limite avec votre astrologue"

Ces clés sont résolues côté frontend dans `frontend/src/i18n/billing.ts`.

### cta_variant par feature

Mapping initial recommandé (peut être externalisé en DB plus tard) :
- `horoscope_daily` → `"inline"` (dans la page, non intrusif)
- `natal_chart_long` → `"inline"`
- `astrologer_chat` → `"banner"` (encart quota en haut du chat)

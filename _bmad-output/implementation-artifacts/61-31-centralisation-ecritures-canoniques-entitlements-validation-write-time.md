# Story 61.31 : Centralisation des écritures canoniques d'entitlements et validation write-time

Status: done

## Story

En tant que développeur backend ou opérateur,
je veux que toute création ou modification de `PlanFeatureBindingModel` / `PlanFeatureQuotaModel` passe obligatoirement par un service unique `CanonicalEntitlementMutationService`,
afin que les invariants canoniques (cohérence scope/audience, règles QUOTA/UNLIMITED/DISABLED, is_metered) soient appliqués **au moment même de l'écriture** et non seulement au démarrage ou en CI.

## Contexte

Les stories 61.28, 61.29 et 61.30 ont établi plusieurs couches de protection read-time :

| Story     | Niveau de protection                                                              | Déclenchement                            |
| --------- | --------------------------------------------------------------------------------- | ---------------------------------------- |
| **61.28** | Validation statique du registre de scope                                          | À la demande / en CI                     |
| **61.29** | Boot-time + CI explicite — bloque si registre incohérent                          | Au démarrage + CI                        |
| **61.30** | DB canonique — cohérence données persistées ↔ registre au démarrage              | Au démarrage + CLI CI                    |
| **61.31** | **Write-time — valide avant toute mutation DB**                                   | **À chaque écriture canonique**          |

Il reste une faille : les scripts `seed_product_entitlements.py`, `backfill_plan_catalog_from_legacy.py` et `b2b_entitlement_repair_service.py` créent et modifient directement `PlanFeatureBindingModel` et `PlanFeatureQuotaModel` sans valider les invariants canoniques avant écriture. Un seed mal configuré peut introduire une configuration incohérente qui ne sera détectée qu'au prochain démarrage.

## Acceptance Criteria

### AC 1 — Service `CanonicalEntitlementMutationService`

1. Un service `CanonicalEntitlementMutationService` est créé dans `backend/app/services/canonical_entitlement_mutation_service.py`.
2. Il expose comme unique point d'entrée public :
   - `upsert_plan_feature_configuration(db, plan, feature_code, *, is_enabled, access_mode, variant_code, quotas, source_origin)` — crée ou met à jour le binding et remplace ses quotas atomiquement.
3. Le remplacement des quotas est implémenté par un helper interne `_replace_plan_feature_quotas(...)` — non destiné à être appelé directement depuis les scripts ou services opérationnels.
4. Le service reçoit une `Session` SQLAlchemy et opère dans la transaction courante (pas de `db.commit()` interne).
5. Le service est idempotent : upsert si existant, création sinon.

### AC 2 — Validations write-time appliquées avant toute mutation

Avant toute écriture en base, le service applique systématiquement les invariants suivants :

6. `feature_code` est connu de `FEATURE_SCOPE_REGISTRY` (via `get_feature_scope()`) — sinon `CanonicalMutationValidationError`.
7. `feature_code` résout vers une entrée `FeatureCatalogModel` existante et `is_active=True` — sinon `CanonicalMutationValidationError`.
8. La compatibilité scope ↔ audience du plan est vérifiée :
   - Feature `B2C` → plan `audience=B2C` uniquement
   - Feature `B2B` → plan `audience=B2B` uniquement
9. `access_mode=QUOTA` → `quotas` non vide (au moins un quota avec `quota_limit > 0`).
10. `access_mode=UNLIMITED` ou `DISABLED` → `quotas` vide.
11. Cohérence `is_metered` : toute feature avec `access_mode=QUOTA` doit avoir `feature_catalog.is_metered=True`.
12. Normalisation `is_enabled` ↔ `access_mode` : le service impose la cohérence stricte :
    - `access_mode=DISABLED` → `is_enabled=False` (violation si `is_enabled=True`)
    - `access_mode=QUOTA` ou `UNLIMITED` → `is_enabled=True` (violation si `is_enabled=False`)
13. Les erreurs sont **agrégées** : toutes les violations sont collectées avant de lever `CanonicalMutationValidationError`, pas d'arrêt à la première.
14. Aucune écriture partielle en base si une violation est détectée.

### AC 3 — Migration des consommateurs existants

15. `backend/scripts/seed_product_entitlements.py` : la fonction locale `upsert_binding_and_quotas()` est remplacée par des appels à `CanonicalEntitlementMutationService.upsert_plan_feature_configuration(...)`.
16. `backend/scripts/backfill_plan_catalog_from_legacy.py` : les créations directes de `PlanFeatureBindingModel` / `PlanFeatureQuotaModel` sont remplacées par des appels au service.
17. `backend/app/services/b2b_entitlement_repair_service.py` : la méthode `_backfill_binding_and_quota` est remplacée par des appels au service. En mode `dry_run=True`, l'appel au service est effectué normalement (la validation canonique s'exécute), mais dans une transaction annulée — de sorte que le plan d'action dry_run et l'exécution réelle aient le même verdict métier.
18. Si d'autres scripts ops/backfill créent directement des bindings/quotas, ils sont migrés de la même manière.

### AC 4 — Vérification d'absence d'écritures directes

19. Un grep sur le repo (hors `canonical_entitlement_mutation_service.py`, tests et migrations Alembic) ne trouve plus :
    - de construction directe de `PlanFeatureBindingModel` (pattern `PlanFeatureBindingModel(`)
    - de construction directe de `PlanFeatureQuotaModel` (pattern `PlanFeatureQuotaModel(`)
    - ni de `db.add(` / `db.add_all(` portant sur ces modèles
    dans les scripts opérationnels et services du périmètre.

### AC 5 — Tests

20. `backend/app/tests/unit/test_canonical_entitlement_mutation_service.py` est créé avec :
    - `test_upsert_creates_binding_and_quotas_nominal` : création B2C avec quota → OK
    - `test_upsert_updates_existing_binding` : binding existant → mis à jour
    - `test_upsert_replaces_stale_quotas` : quotas obsolètes supprimés, nouveaux créés, tous les champs mutables mis à jour
    - `test_validation_fails_unknown_feature_code` : `feature_code` absent du registre
    - `test_validation_fails_feature_absent_from_catalog` : `feature_code` dans registre mais absent de `feature_catalog`
    - `test_validation_fails_feature_inactive_in_catalog` : `feature_code` présent mais `is_active=False`
    - `test_validation_fails_b2b_feature_on_b2c_plan` : scope B2B sur plan B2C
    - `test_validation_fails_b2c_feature_on_b2b_plan` : scope B2C sur plan B2B
    - `test_validation_fails_quota_mode_without_quotas` : `QUOTA` sans quotas
    - `test_validation_fails_unlimited_with_quotas` : `UNLIMITED` avec quotas
    - `test_validation_fails_disabled_with_quotas` : `DISABLED` avec quotas
    - `test_validation_fails_disabled_with_is_enabled_true` : `DISABLED` + `is_enabled=True`
    - `test_validation_fails_quota_with_is_enabled_false` : `QUOTA` + `is_enabled=False`
    - `test_validation_aggregates_multiple_errors` : plusieurs violations → toutes remontées, pas d'écriture partielle
    - `test_no_partial_write_on_validation_error` : aucune ligne insérée si validation échoue
21. Les tests utilisent une session SQLite in-memory (pattern 61.30).

### AC 6 — Non-régression

22. La suite pytest quota B2C/B2B existante reste verte.
23. Les scripts `seed_product_entitlements.py` et `backfill_plan_catalog_from_legacy.py` conservent leur comportement observable (idempotence, reporting).
24. Aucun contrat API public n'est modifié.
25. Aucune migration Alembic n'est créée.

---

## Tasks / Subtasks

- [x] **Créer `canonical_entitlement_mutation_service.py`** (AC: 1, 2)
  - [x] Définir `CanonicalMutationValidationError(ValueError)` — agrège les erreurs
  - [x] Implémenter `_validate(feature_code, plan_audience, access_mode, is_enabled, quotas, feature_row)` → `list[str]`
  - [x] Utiliser `get_feature_scope()` + `UnknownFeatureCodeError` (pas d'accès direct à `FEATURE_SCOPE_REGISTRY`)
  - [x] Ajouter check feature absente/inactive de `feature_catalog`
  - [x] Ajouter check normalisation `is_enabled` ↔ `access_mode`
  - [x] Implémenter `upsert_plan_feature_configuration(...)` — seule méthode publique
  - [x] Implémenter `_replace_plan_feature_quotas(...)` — helper privé, met à jour tous les champs mutables
  - [x] Pas de `db.commit()` dans le service

- [x] **Migrer `seed_product_entitlements.py`** (AC: 3)
  - [x] Supprimer la fonction locale `upsert_binding_and_quotas()`
  - [x] Remplacer chaque appel par `CanonicalEntitlementMutationService.upsert_plan_feature_configuration(...)`
  - [x] Vérifier idempotence + comportement inchangé

- [x] **Migrer `backfill_plan_catalog_from_legacy.py`** (AC: 3)
  - [x] Identifier toutes les constructions directes de `PlanFeatureBindingModel` et `PlanFeatureQuotaModel`
  - [x] Remplacer par appels au service
  - [x] Préserver le `BackfillReport` et ses compteurs

- [x] **Migrer `b2b_entitlement_repair_service.py`** (AC: 3)
  - [x] Remplacer `_backfill_binding_and_quota()` par un appel à `CanonicalEntitlementMutationService`
  - [x] En mode `dry_run=True` : exécuter la validation canonique via le service dans un savepoint annulé, retourner les dummy objects comme avant

- [x] **Scanner les autres scripts** (AC: 3, 4)
  - [x] `grep -r "PlanFeatureBindingModel\|PlanFeatureQuotaModel" backend/scripts/ backend/app/services/` (hors service + tests + migrations)
  - [x] Vérifier aussi l'absence de `db.add(` / `db.add_all(` sur ces modèles hors service central
  - [x] Migrer tout script ops identifié

- [x] **Créer les tests unitaires** (AC: 5)
  - [x] `test_canonical_entitlement_mutation_service.py` avec session SQLite in-memory
  - [x] Fixtures : `FeatureCatalogModel` + `PlanCatalogModel` + `b2b_plan` seed in-memory
  - [x] Couvrir les 15 cas listés en AC 5

- [x] **Validation finale** (AC: 6)
  - [x] `ruff check` sur tous les fichiers créés/modifiés
  - [x] `pytest backend/app/tests/unit/test_canonical_entitlement_mutation_service.py`
  - [x] Suite non-régression 61.27 / 61.28 / 61.29 / 61.30

---

## Dev Notes

### Architecture et responsabilités

Le service `CanonicalEntitlementMutationService` est le **seul chemin autorisé** pour créer ou modifier `PlanFeatureBindingModel` et `PlanFeatureQuotaModel` dans le code opérationnel.

**Ce que le service fait :**
- Valide les invariants canoniques avant toute mutation (registre, DB catalog, scope/audience, quotas, is_metered, normalisation is_enabled)
- Gère l'upsert binding + remplacement atomique des quotas via `_replace_plan_feature_quotas` (privé)
- Fonctionne dans la transaction courante (pas de commit interne)

**Ce que le service ne fait PAS :**
- Il ne crée pas de `PlanCatalogModel` ni `FeatureCatalogModel` (responsabilité des scripts)
- Il ne gère pas la session / transaction (l'appelant contrôle le commit)
- Il n'expose pas de méthode publique de modification des quotas en isolation — toute mutation passe par `upsert_plan_feature_configuration`

### Schéma DB pertinent

```
feature_catalog
  id, feature_code (unique), feature_name, is_metered, is_active

plan_catalog
  id, plan_code (unique), plan_name, audience (Audience enum: b2c/b2b/internal), is_active

plan_feature_bindings
  id, plan_id → plan_catalog.id, feature_id → feature_catalog.id
  is_enabled, access_mode (AccessMode enum: disabled/unlimited/quota), variant_code, source_origin

plan_feature_quotas
  id, plan_feature_binding_id → plan_feature_bindings.id
  quota_key, quota_limit (>0), period_unit, period_value, reset_mode, source_origin
```

### Imports à utiliser

```python
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
    SourceOrigin,
)
from app.services.feature_scope_registry import (
    FeatureScope,
    UnknownFeatureCodeError,
    get_feature_scope,
)
```

### Mapping scope ↔ audience (réutilisé de 61.30)

```python
_SCOPE_TO_AUDIENCE: dict[FeatureScope, Audience] = {
    FeatureScope.B2C: Audience.B2C,
    FeatureScope.B2B: Audience.B2B,
}
```

### Squelette recommandé du service

```python
from __future__ import annotations

import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.product_entitlements import (
    AccessMode, Audience, FeatureCatalogModel,
    PlanCatalogModel, PlanFeatureBindingModel, PlanFeatureQuotaModel, SourceOrigin,
)
from app.services.feature_scope_registry import (
    FeatureScope, UnknownFeatureCodeError, get_feature_scope,
)

logger = logging.getLogger(__name__)

_SCOPE_TO_AUDIENCE: dict[FeatureScope, Audience] = {
    FeatureScope.B2C: Audience.B2C,
    FeatureScope.B2B: Audience.B2B,
}


class CanonicalMutationValidationError(ValueError):
    """Exception levée si une mutation canonique viole les invariants.

    Agrège toutes les violations détectées.
    """
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(
            "Canonical mutation validation failed:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )


class CanonicalEntitlementMutationService:

    @staticmethod
    def upsert_plan_feature_configuration(
        db: Session,
        plan: PlanCatalogModel,
        feature_code: str,
        *,
        is_enabled: bool,
        access_mode: AccessMode,
        variant_code: str | None = None,
        quotas: list[dict],
        source_origin: SourceOrigin,
    ) -> PlanFeatureBindingModel:
        """Crée ou met à jour un binding plan↔feature + remplace ses quotas.

        Valide les invariants canoniques avant toute écriture.
        Lève CanonicalMutationValidationError si une règle est violée.
        Pas de db.commit() — l'appelant contrôle la transaction.
        """
        # 1. Récupérer la feature du catalog (peut être None — géré dans _validate)
        feature = db.scalar(
            select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == feature_code)
        )

        # 2. Valider — lève si erreurs
        errors = CanonicalEntitlementMutationService._validate(
            feature_code=feature_code,
            plan_audience=plan.audience,
            access_mode=access_mode,
            is_enabled=is_enabled,
            quotas=quotas,
            feature_row=feature,
        )
        if errors:
            raise CanonicalMutationValidationError(errors)

        # 3. Upsert binding
        binding = db.scalar(
            select(PlanFeatureBindingModel).where(
                PlanFeatureBindingModel.plan_id == plan.id,
                PlanFeatureBindingModel.feature_id == feature.id,
            )
        )
        if binding is None:
            binding = PlanFeatureBindingModel(
                plan_id=plan.id,
                feature_id=feature.id,
                is_enabled=is_enabled,
                access_mode=access_mode,
                variant_code=variant_code,
                source_origin=source_origin,
            )
            db.add(binding)
        else:
            binding.is_enabled = is_enabled
            binding.access_mode = access_mode
            binding.variant_code = variant_code
            binding.source_origin = source_origin
        db.flush()

        # 4. Remplacer les quotas atomiquement (helper privé)
        CanonicalEntitlementMutationService._replace_plan_feature_quotas(
            db, binding, quotas, source_origin=source_origin
        )
        return binding

    @staticmethod
    def _replace_plan_feature_quotas(
        db: Session,
        binding: PlanFeatureBindingModel,
        quotas: list[dict],
        *,
        source_origin: SourceOrigin,
    ) -> None:
        """Remplace atomiquement les quotas d'un binding — USAGE INTERNE UNIQUEMENT."""
        existing = db.scalars(
            select(PlanFeatureQuotaModel).where(
                PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
            )
        ).all()

        desired_keys = {
            (q["quota_key"], q["period_unit"], q["period_value"], q["reset_mode"])
            for q in quotas
        }

        # Supprimer les quotas devenus obsolètes
        for ex in existing:
            if (ex.quota_key, ex.period_unit, ex.period_value, ex.reset_mode) not in desired_keys:
                db.delete(ex)

        existing_map = {
            (ex.quota_key, ex.period_unit, ex.period_value, ex.reset_mode): ex
            for ex in existing
        }

        for q_data in quotas:
            key = (q_data["quota_key"], q_data["period_unit"], q_data["period_value"], q_data["reset_mode"])
            if key not in existing_map:
                db.add(PlanFeatureQuotaModel(
                    plan_feature_binding_id=binding.id,
                    source_origin=source_origin,
                    **q_data,
                ))
            else:
                # Mettre à jour tous les champs mutables (pas seulement quota_limit)
                row = existing_map[key]
                row.quota_limit = q_data["quota_limit"]
                row.source_origin = source_origin
        db.flush()

    @staticmethod
    def _validate(
        feature_code: str,
        plan_audience: Audience,
        access_mode: AccessMode,
        is_enabled: bool,
        quotas: list[dict],
        feature_row: FeatureCatalogModel | None,
    ) -> list[str]:
        errors: list[str] = []

        # Check 1 : feature_code connu du registre (via l'API officielle)
        scope: FeatureScope | None = None
        try:
            scope = get_feature_scope(feature_code)
        except UnknownFeatureCodeError:
            errors.append(f"feature_code '{feature_code}' absent de FEATURE_SCOPE_REGISTRY.")

        # Check 2 : feature présente et active en DB
        if feature_row is None:
            errors.append(f"feature_code '{feature_code}' absent de feature_catalog.")
        elif not feature_row.is_active:
            errors.append(
                f"feature_code '{feature_code}' présent dans feature_catalog mais is_active=False."
            )

        # Check 3 : compatibilité scope ↔ audience (uniquement si scope connu)
        if scope is not None:
            expected_audience = _SCOPE_TO_AUDIENCE[scope]
            if plan_audience != expected_audience:
                errors.append(
                    f"feature '{feature_code}' de scope {scope.value.upper()} "
                    f"ne peut être bindée qu'à un plan {expected_audience.value.upper()}, "
                    f"reçu {plan_audience.value.upper()}."
                )

        # Check 4 : règles QUOTA / UNLIMITED / DISABLED + is_metered
        if access_mode == AccessMode.QUOTA:
            if not quotas:
                errors.append(
                    f"access_mode=QUOTA pour '{feature_code}' requiert au moins un quota."
                )
            if feature_row is not None and not feature_row.is_metered:
                errors.append(
                    f"access_mode=QUOTA pour '{feature_code}' requiert is_metered=True dans feature_catalog."
                )
        elif access_mode in (AccessMode.UNLIMITED, AccessMode.DISABLED):
            if quotas:
                errors.append(
                    f"access_mode={access_mode.value.upper()} pour '{feature_code}' "
                    "ne doit pas avoir de quotas."
                )

        # Check 5 : normalisation is_enabled ↔ access_mode
        if access_mode == AccessMode.DISABLED and is_enabled:
            errors.append(
                f"access_mode=DISABLED pour '{feature_code}' requiert is_enabled=False."
            )
        elif access_mode in (AccessMode.QUOTA, AccessMode.UNLIMITED) and not is_enabled:
            errors.append(
                f"access_mode={access_mode.value.upper()} pour '{feature_code}' requiert is_enabled=True."
            )

        return errors
```

### Pattern de migration des scripts

**Avant (seed/backfill direct) :**
```python
binding = PlanFeatureBindingModel(
    plan_id=plan.id,
    feature_id=feature.id,
    access_mode=access_mode,
    ...
)
db.add(binding)
db.flush()
quota = PlanFeatureQuotaModel(plan_feature_binding_id=binding.id, ...)
db.add(quota)
```

**Après (via service) :**
```python
from app.services.canonical_entitlement_mutation_service import CanonicalEntitlementMutationService

CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
    db,
    plan=plan,
    feature_code=feature_code,
    is_enabled=is_enabled,
    access_mode=access_mode,
    variant_code=variant_code,
    quotas=quotas,  # liste de dicts (quota_key, quota_limit, period_unit, period_value, reset_mode)
    source_origin=source_origin,
)
```

### Gestion du `dry_run` dans `b2b_entitlement_repair_service.py`

Le service n'appelle jamais `db.commit()`. Le dry_run doit **quand même exécuter la validation** afin que le plan d'action dry_run et l'exécution réelle aient le même verdict métier. Le pattern recommandé :

```python
if not dry_run:
    CanonicalEntitlementMutationService.upsert_plan_feature_configuration(db, ...)
else:
    # Valider sans persister : utiliser un savepoint annulé
    sp = db.begin_nested()
    try:
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(db, ...)
    finally:
        sp.rollback()
    # Construire les dummy objects pour le rapport dry_run comme avant
    binding = PlanFeatureBindingModel(id=-(canonical_plan.id or 1), ...)
```

Les objets dummy (id négatif) restent utilisés uniquement pour les besoins du reporting dry_run, jamais via `db.add()`.

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/services/canonical_entitlement_mutation_service.py` | Créer |
| `backend/scripts/seed_product_entitlements.py` | Modifier — retirer `upsert_binding_and_quotas()` locale |
| `backend/scripts/backfill_plan_catalog_from_legacy.py` | Modifier — retirer constructions directes |
| `backend/app/services/b2b_entitlement_repair_service.py` | Modifier — `_backfill_binding_and_quota` |
| `backend/app/tests/unit/test_canonical_entitlement_mutation_service.py` | Créer |
| `backend/docs/entitlements-canonical-platform.md` | Mettre à jour (section Story 61.31) |

### Fixture de test recommandée

```python
@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture()
def b2c_plan(db):
    plan = PlanCatalogModel(
        plan_code="basic", plan_name="Basic", audience=Audience.B2C,
        is_active=True, source_type="manual",
    )
    db.add(plan)
    db.flush()
    return plan

@pytest.fixture()
def b2b_plan(db):
    plan = PlanCatalogModel(
        plan_code="enterprise", plan_name="Enterprise", audience=Audience.B2B,
        is_active=True, source_type="manual",
    )
    db.add(plan)
    db.flush()
    return plan

@pytest.fixture()
def chat_feature(db):
    feature = FeatureCatalogModel(
        feature_code="astrologer_chat", feature_name="Chat",
        is_metered=True, is_active=True,
    )
    db.add(feature)
    db.flush()
    return feature
```

### Dépendances de stories

- **61.30** : fournit les invariants canoniques à répliquer en write-time (check list complète)
- **61.29** : fournit le pattern de startup validation à ne pas casser
- **61.7** : définit les modèles `PlanFeatureBindingModel`, `PlanFeatureQuotaModel`, les enums

### References

- [Source: backend/app/services/canonical_entitlement_db_consistency_validator.py] — checks 61.30 à reproduire write-time
- [Source: backend/app/services/feature_scope_registry.py] — `get_feature_scope()`, `UnknownFeatureCodeError`, `FeatureScope`
- [Source: backend/scripts/seed_product_entitlements.py#upsert_binding_and_quotas] — fonction locale à migrer
- [Source: backend/app/services/b2b_entitlement_repair_service.py#_backfill_binding_and_quota] — méthode à migrer
- [Source: backend/app/infra/db/models/product_entitlements.py] — modèles ORM, enums AccessMode, Audience, SourceOrigin

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- [2026-03-28 14:15] Started implementation.
- [2026-03-28 14:15] Planned implementation:
  1. Create CanonicalEntitlementMutationService with validation logic.
  2. Create unit tests covering nominal and error cases.
  3. Migrate seed_product_entitlements.py.
  4. Migrate backfill_plan_catalog_from_legacy.py.
  5. Migrate b2b_entitlement_repair_service.py.
  6. Run full validation suite.
- [2026-03-28 14:45] Implementation completed.
- [2026-03-28 14:50] Unit tests passed (15/15).
- [2026-03-28 15:20] Code review performed: 2 issues majeures détectées.
- [2026-03-28 15:35] Fix: validation write-time explicite de `quota_limit > 0` ajoutée au service canonique + test dédié.
- [2026-03-28 15:40] Fix: reporting idempotent exact restauré dans `backfill_plan_catalog_from_legacy.py`.
- [2026-03-28 15:45] Fix: constructions directes résiduelles supprimées du `B2BEntitlementRepairService` en `dry_run` via previews mémoire.
- [2026-03-28 15:55] Validation revue/fixes: `pytest` ciblé + non-régression B2B + `ruff check` OK.

### Completion Notes List

- Service central `CanonicalEntitlementMutationService` créé dans `backend/app/services/`.
- Invariants validés : présence dans le registre, présence en DB, feature active, cohérence Audience/Scope, règles quotas/is_metered, et désormais `quota_limit > 0` avant écriture.
- Remplacement des quotas atomique implémenté.
- Migrations effectuées : `seed_product_entitlements.py`, `backfill_plan_catalog_from_legacy.py`, `B2BEntitlementRepairService`.
- Revue corrective effectuée : reporting `BackfillReport` réaligné sur le comportement observable attendu et `dry_run` B2B débarrassé des constructions ORM directes.
- Tests unitaires et de non-régression mis à jour et exécutés.

### File List

- `backend/app/services/canonical_entitlement_mutation_service.py`
- `backend/app/tests/unit/test_canonical_entitlement_mutation_service.py`
- `backend/scripts/seed_product_entitlements.py`
- `backend/scripts/backfill_plan_catalog_from_legacy.py`
- `backend/app/services/b2b_entitlement_repair_service.py`
- `backend/app/tests/unit/test_backfill_plan_catalog.py`
- `backend/app/tests/unit/test_b2b_entitlement_repair_service.py`
- `backend/docs/entitlements-canonical-platform.md`
- `docs/architecture/product-entitlements-model.md`

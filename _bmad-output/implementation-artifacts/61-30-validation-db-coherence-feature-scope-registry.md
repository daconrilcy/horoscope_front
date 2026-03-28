# Story 61.30 : Validation DB de cohérence entre FEATURE_SCOPE_REGISTRY, feature_catalog et les bindings de plans

Status: done

## Story

En tant que développeur backend ou opérateur,
je veux qu'un validateur contrôle la cohérence des données canoniques stockées en base avec le registre de scope (`FEATURE_SCOPE_REGISTRY`) et l'audience des plans (`plan_catalog.audience`),
afin d'empêcher toute configuration incohérente du type feature B2B liée à un plan B2C, ou feature B2C liée à un plan B2B, même si le code applicatif est correct.

## Contexte

Les stories 61.27, 61.28 et 61.29 ont sécurisé :

| Story     | Niveau de protection                                                          | Déclenchement                            |
| --------- |-------------------------------------------------------------------------------| ---------------------------------------- |
| **61.27** | Runtime — refuse le mauvais service de quota                                  | À chaque appel quota                     |
| **61.28** | Design-time / validation statique — détecte les incohérences de registre      | À la demande / en CI                     |
| **61.29** | Boot-time + CI explicite — bloque le démarrage ou la livraison si incohérence | Au démarrage de l'app + en validation CI |
| **61.30** | DB canonique — cohérence données persistées ↔ registre                        | Au démarrage de l'app + CLI CI           |

Il reste une faille : la DB peut contenir une configuration canonique incohérente si quelqu'un seed ou modifie mal `feature_catalog`, `plan_catalog`, `plan_feature_bindings` ou `plan_feature_quotas`.

**Exemples d'erreurs que 61.30 doit bloquer :**

- `b2b_api_access` bindé à un plan `audience='b2c'`
- `astrologer_chat` bindé à un plan `audience='b2b'`
- `access_mode=QUOTA` sans quota associé dans `plan_feature_quotas`
- quota défini pour un binding `UNLIMITED` ou `DISABLED`
- `feature_code` connu du registre mais absent de `feature_catalog` (ou inactif)

## Acceptance Criteria

### AC 1 — Validateur DB de cohérence canonique

1. Un service `CanonicalEntitlementDbConsistencyValidator` est créé dans `backend/app/services/canonical_entitlement_db_consistency_validator.py`.
2. Il expose `validate(db: Session) -> None`.
3. Il lève `CanonicalEntitlementDbConsistencyError(ValueError)` si une incohérence est détectée.
4. L'erreur agrège **toutes** les incohérences trouvées, sans s'arrêter à la première.

### AC 2 — Vérifications réalisées

5. Pour chaque `feature_code` de `FEATURE_SCOPE_REGISTRY`, une entrée **active** (`is_active=True`) existe dans `feature_catalog`.
6. Toute feature active `is_metered=True` de `feature_catalog` qui participe aux entitlements quota doit être enregistrée dans `FEATURE_SCOPE_REGISTRY` *(DB → registre)*.
7. Toute feature référencée dans `plan_feature_bindings` doit être enregistrée dans `FEATURE_SCOPE_REGISTRY` ; une feature bindée absente du registre est une incohérence bloquante *(DB → registre)*.
8. Toute feature de scope B2C ne peut être bindée qu'à des plans `plan_catalog.audience = B2C`.
9. Toute feature de scope B2B ne peut être bindée qu'à des plans `plan_catalog.audience = B2B`.
10. Tout binding `access_mode = QUOTA` possède au moins un `PlanFeatureQuotaModel` valide.
11. Aucun binding `access_mode = UNLIMITED` ou `DISABLED` ne possède de quota associé.
12. Les features quota connues du registre — actuellement `astrologer_chat`, `thematic_consultation`, `natal_chart_long` et `b2b_api_access` — sont présentes en DB avec `is_active=True`. Pour ces quatre features, `is_metered=True` est exigé.

### AC 3 — CLI de validation DB

11. Un script `backend/scripts/check_canonical_entitlement_db_consistency.py` est créé.
12. Il ouvre une session DB, exécute le validateur, affiche `[OK]` en cas de succès.
13. En cas d'échec, il affiche la liste complète des incohérences et retourne exit code 1.
14. En cas d'erreur inattendue, il retourne exit code 2 (cohérent avec `check_feature_scope_registry.py`).

### AC 4 — Enforcement startup

15. Le validateur DB est exécuté dans `_app_lifespan` (dans `backend/app/main.py`), **après** l'appel `run_feature_scope_startup_validation` de 61.29.
16. Une config dédiée est ajoutée dans `backend/app/core/config.py` :
    - nom Python : `canonical_db_validation_mode`
    - variable d'environnement : `CANONICAL_DB_VALIDATION_MODE`
    - valeurs valides : `"strict"`, `"warn"`, `"off"`
    - défaut : `"strict"`
    - valeur invalide → normalisée vers `"strict"` avec log WARNING (même pattern que `_parse_feature_scope_validation_mode`)
17. En mode `strict` : échec → exception, démarrage bloqué.
18. En mode `warn` : échec → log ERROR structuré, démarrage autorisé.
19. En mode `off` : validation non exécutée, log WARNING explicite.

### AC 5 — Tests

20. `backend/app/tests/unit/test_canonical_entitlement_db_consistency_validator.py` est créé avec :
    - `test_validator_ok_nominal` : registre + DB cohérents, pas d'exception
    - `test_validator_fails_feature_missing_from_catalog` : feature dans registre, absente de `feature_catalog`
    - `test_validator_fails_feature_inactive_in_catalog` : feature présente mais `is_active=False`
    - `test_validator_fails_b2b_feature_bound_to_b2c_plan` : `b2b_api_access` bindé à un plan B2C
    - `test_validator_fails_b2c_feature_bound_to_b2b_plan` : `astrologer_chat` bindé à un plan B2B
    - `test_validator_fails_quota_binding_without_quota` : `access_mode=QUOTA` sans quota
    - `test_validator_fails_unlimited_binding_with_quota` : `access_mode=UNLIMITED` avec quota parasite
    - `test_validator_fails_disabled_binding_with_quota` : `access_mode=DISABLED` avec quota parasite
    - `test_validator_fails_bound_feature_not_registered` : feature active en DB, bindée à un plan, mais absente de `FEATURE_SCOPE_REGISTRY`
    - `test_validator_fails_metered_feature_not_registered` : feature `is_metered=True` en DB active, mais absente du registre
    - `test_validator_aggregates_multiple_errors` : plusieurs incohérences → toutes remontées
21. `backend/app/tests/unit/test_check_canonical_entitlement_db_consistency_cli.py` est créé avec :
    - `test_cli_main_exit_0_on_consistent_db`
    - `test_cli_main_exit_1_on_inconsistent_db`
    - `test_cli_main_exit_2_on_unexpected_error`
22. `backend/app/tests/unit/test_canonical_db_startup_validation.py` est créé avec :
    - `test_startup_db_validation_strict_ok`
    - `test_startup_db_validation_strict_fails`
    - `test_startup_db_validation_warn_does_not_block`
    - `test_startup_db_validation_off_skips_validator`
    - `test_startup_db_validation_invalid_mode_falls_back_to_strict`

### AC 6 — Documentation

23. `backend/docs/entitlements-canonical-platform.md` est mis à jour avec une section **"Validation DB canonique (Story 61.30)"** précisant :
    - la distinction entre les 4 couches 61.27 / 61.28 / 61.29 / 61.30
    - les checks DB réalisés
    - les 3 modes `strict`, `warn`, `off`
    - la commande CLI à intégrer en CI
24. `scripts/quality-gate.ps1` est mis à jour pour inclure `python backend/scripts/check_canonical_entitlement_db_consistency.py` **dans la phase où la DB de validation est déjà provisionnée et migrée**. Si ce bootstrap DB n'existe pas dans un environnement donné (pipeline purement statique), la commande est au minimum documentée dans le runbook CI backend avec la précondition explicite : migrations appliquées + seed canonique minimal présent.

### AC 7 — Non-régression

25. La suite pytest quota B2C/B2B existante reste verte.
26. Aucun contrat API public n'est modifié.
27. Aucune migration Alembic n'est créée.

---

## Tasks / Subtasks

- [x] **Créer `canonical_entitlement_db_consistency_validator.py`** (AC: 1, 2)
  - [x] Définir `CanonicalEntitlementDbConsistencyError(ValueError)`
  - [x] Implémenter `CanonicalEntitlementDbConsistencyValidator.validate(db: Session) -> None`
  - [x] Check 1 : pour chaque feature du registre → entrée active dans `feature_catalog` (registre → DB)
  - [x] Check 2 : toute feature `is_metered=True` active dans `feature_catalog` est enregistrée dans le registre (DB → registre)
  - [x] Check 3 : toute feature utilisée dans `plan_feature_bindings` est enregistrée dans le registre (DB → registre)
  - [x] Check 4 & 5 : scope B2C/B2B ↔ audience plan (via `plan_feature_bindings` → `feature_catalog` → `plan_catalog`)
  - [x] Check 6 : binding QUOTA → au moins un quota dans `plan_feature_quotas`
  - [x] Check 7 : binding UNLIMITED/DISABLED → aucun quota dans `plan_feature_quotas`
  - [x] Agréger toutes les erreurs avant de lever l'exception

- [x] **Créer `backend/app/startup/canonical_db_validation.py`** (AC: 4)
  - [x] Implémenter `run_canonical_db_startup_validation(mode: str, db: Session) -> None`
  - [x] Mode `off` → log WARNING `canonical_db_startup_validation_disabled`, retour immédiat
  - [x] Mode `strict` → appel `validate(db)`, log INFO si OK (`canonical_db_startup_validation_ok`), log ERROR + re-raise sur échec (`canonical_db_startup_validation_failed`)
  - [x] Mode `warn` → appel `validate(db)`, log ERROR sur échec, ne pas propager
  - [x] Mode invalide → log WARNING + fallback `"strict"`

- [x] **Ajouter `canonical_db_validation_mode` dans `config.py`** (AC: 4)
  - [x] Ajouter méthode statique `_parse_canonical_db_validation_mode()` (calquée sur `_parse_feature_scope_validation_mode`)
  - [x] Ajouter `self.canonical_db_validation_mode = self._parse_canonical_db_validation_mode()` dans `__init__`

- [x] **Brancher dans `main.py`** (AC: 4)
  - [x] Importer `run_canonical_db_startup_validation` depuis `app.startup.canonical_db_validation`
  - [x] Appeler `run_canonical_db_startup_validation(settings.canonical_db_validation_mode, db)` dans `_app_lifespan`, au sein du bloc `with SessionLocal() as db:`, après `validate_catalog_vs_db(db)`

- [x] **Créer le script CLI** (AC: 3)
  - [x] `backend/scripts/check_canonical_entitlement_db_consistency.py`
  - [x] Pattern `_ensure_backend_root_on_path()` + `main() -> int` identique à `check_feature_scope_registry.py`
  - [x] Ouvrir une session `SessionLocal()`, appeler `validate(db)`, retourner 0/1/2

- [x] **Créer les tests unitaires** (AC: 5)
  - [x] `test_canonical_entitlement_db_consistency_validator.py` (fixture in-memory SQLite)
  - [x] `test_check_canonical_entitlement_db_consistency_cli.py` (patch du validateur)
  - [x] `test_canonical_db_startup_validation.py` (patch du validateur)

- [x] **Mettre à jour la documentation** (AC: 6)
  - [x] `backend/docs/entitlements-canonical-platform.md`
  - [x] `scripts/quality-gate.ps1`

- [x] **Validation finale** (AC: 7)
  - [x] `ruff check` sur tous les fichiers créés/modifiés
  - [x] `pytest backend/app/tests/unit/test_canonical_entitlement_db_consistency_validator.py`
  - [x] `pytest backend/app/tests/unit/test_check_canonical_entitlement_db_consistency_cli.py`
  - [x] `pytest backend/app/tests/unit/test_canonical_db_startup_validation.py`
  - [x] Suite non-régression 61.27 / 61.28 / 61.29

---

## Dev Notes

### Architecture et séparation des responsabilités

Le validateur DB est isolé dans `backend/app/services/canonical_entitlement_db_consistency_validator.py`.
Il reçoit une `Session` SQLAlchemy et applique les vérifications via des requêtes directes (pas d'ORM complexe — requêtes simples `db.query(...)` ou `select`).

Le bootstrap `backend/app/startup/canonical_db_validation.py` est calqué **exactement** sur `backend/app/startup/feature_scope_validation.py` : même signature, mêmes 3 modes, même convention de logs. La seule différence est qu'il reçoit aussi un `db: Session`.

### Schéma DB pertinent

```
feature_catalog
  id, feature_code (unique), feature_name, is_metered, is_active

plan_catalog
  id, plan_code (unique), plan_name, audience (Audience enum: b2c/b2b/internal), is_active

plan_feature_bindings
  id, plan_id → plan_catalog.id, feature_id → feature_catalog.id
  is_enabled, access_mode (AccessMode enum: disabled/unlimited/quota)

plan_feature_quotas
  id, plan_feature_binding_id → plan_feature_bindings.id
  quota_key, quota_limit (>0), period_unit, period_value, reset_mode
```

**Imports à utiliser :**

```python
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.services.feature_scope_registry import FEATURE_SCOPE_REGISTRY, FeatureScope
```

### Mapping scope ↔ audience

```python
_SCOPE_TO_AUDIENCE: dict[FeatureScope, Audience] = {
    FeatureScope.B2C: Audience.B2C,
    FeatureScope.B2B: Audience.B2B,
}
```

### Implémentation recommandée du validateur

```python
import logging
from sqlalchemy.orm import Session
from app.infra.db.models.product_entitlements import (
    AccessMode, Audience, FeatureCatalogModel,
    PlanCatalogModel, PlanFeatureBindingModel, PlanFeatureQuotaModel,
)
from app.services.feature_scope_registry import FEATURE_SCOPE_REGISTRY, FeatureScope

logger = logging.getLogger(__name__)

_SCOPE_TO_AUDIENCE: dict[FeatureScope, Audience] = {
    FeatureScope.B2C: Audience.B2C,
    FeatureScope.B2B: Audience.B2B,
}


class CanonicalEntitlementDbConsistencyError(ValueError):
    """Exception levée si la DB entitlements est incohérente avec le registre."""


class CanonicalEntitlementDbConsistencyValidator:

    @staticmethod
    def validate(db: Session) -> None:
        errors: list[str] = []

        # Check 1 : registre → DB (présence active)
        for feature_code in FEATURE_SCOPE_REGISTRY:
            row = (
                db.query(FeatureCatalogModel)
                .filter_by(feature_code=feature_code)
                .one_or_none()
            )
            if row is None:
                errors.append(
                    f"feature_code '{feature_code}' absent de feature_catalog."
                )
            elif not row.is_active:
                errors.append(
                    f"feature_code '{feature_code}' présent dans feature_catalog "
                    "mais is_active=False."
                )

        # Check 2 : DB → registre (features metered actives)
        metered_active = (
            db.query(FeatureCatalogModel)
            .filter_by(is_metered=True, is_active=True)
            .all()
        )
        for fc in metered_active:
            if fc.feature_code not in FEATURE_SCOPE_REGISTRY:
                errors.append(
                    f"feature_code '{fc.feature_code}' est is_metered=True et is_active=True "
                    "dans feature_catalog mais absent de FEATURE_SCOPE_REGISTRY."
                )

        # Check 3 : DB → registre (features dans les bindings)
        bindings = db.query(PlanFeatureBindingModel).all()
        for binding in bindings:
            feature_row = db.get(FeatureCatalogModel, binding.feature_id)
            if feature_row is None:
                continue
            if feature_row.feature_code not in FEATURE_SCOPE_REGISTRY:
                plan_row = db.get(PlanCatalogModel, binding.plan_id)
                pname = plan_row.plan_code if plan_row else f"plan_id={binding.plan_id}"
                errors.append(
                    f"feature_code '{feature_row.feature_code}' est utilisé dans "
                    f"plan_feature_bindings (plan='{pname}') mais absent de FEATURE_SCOPE_REGISTRY."
                )

        # Check 4 & 5 : scope B2C/B2B ↔ audience plan
        for binding in bindings:
            feature_row = db.get(FeatureCatalogModel, binding.feature_id)
            plan_row = db.get(PlanCatalogModel, binding.plan_id)
            if feature_row is None or plan_row is None:
                continue  # FK broken — not this validator's responsibility
            feature_code = feature_row.feature_code
            scope = FEATURE_SCOPE_REGISTRY.get(feature_code)
            if scope is None:
                continue  # Déjà signalé au check 3
            expected_audience = _SCOPE_TO_AUDIENCE.get(scope)
            if expected_audience is None:
                continue  # INTERNAL scope — no cross-check needed
            if plan_row.audience != expected_audience:
                errors.append(
                    f"Feature '{feature_code}' (scope {scope.value}) liée au plan "
                    f"'{plan_row.plan_code}' (audience={plan_row.audience.value}) : "
                    f"attendu audience={expected_audience.value}."
                )

        # Check 6 : QUOTA → au moins un quota
        quota_bindings = (
            db.query(PlanFeatureBindingModel)
            .filter_by(access_mode=AccessMode.QUOTA)
            .all()
        )
        for binding in quota_bindings:
            count = (
                db.query(PlanFeatureQuotaModel)
                .filter_by(plan_feature_binding_id=binding.id)
                .count()
            )
            if count == 0:
                feature_row = db.get(FeatureCatalogModel, binding.feature_id)
                plan_row = db.get(PlanCatalogModel, binding.plan_id)
                fname = feature_row.feature_code if feature_row else f"feature_id={binding.feature_id}"
                pname = plan_row.plan_code if plan_row else f"plan_id={binding.plan_id}"
                errors.append(
                    f"Binding QUOTA feature='{fname}' plan='{pname}' "
                    "n'a aucun quota dans plan_feature_quotas."
                )

        # Check 7 : UNLIMITED/DISABLED → aucun quota parasite
        non_quota_bindings = (
            db.query(PlanFeatureBindingModel)
            .filter(PlanFeatureBindingModel.access_mode.in_(
                [AccessMode.UNLIMITED, AccessMode.DISABLED]
            ))
            .all()
        )
        for binding in non_quota_bindings:
            count = (
                db.query(PlanFeatureQuotaModel)
                .filter_by(plan_feature_binding_id=binding.id)
                .count()
            )
            if count > 0:
                feature_row = db.get(FeatureCatalogModel, binding.feature_id)
                plan_row = db.get(PlanCatalogModel, binding.plan_id)
                fname = feature_row.feature_code if feature_row else f"feature_id={binding.feature_id}"
                pname = plan_row.plan_code if plan_row else f"plan_id={binding.plan_id}"
                errors.append(
                    f"Binding {binding.access_mode.value.upper()} feature='{fname}' "
                    f"plan='{pname}' a {count} quota(s) parasite(s)."
                )

        if errors:
            raise CanonicalEntitlementDbConsistencyError(
                "Canonical entitlement DB inconsistencies detected:\n"
                + "\n".join(f"  {i + 1}. {e}" for i, e in enumerate(errors))
            )
```

### Implémentation du bootstrap canonical_db_validation.py

```python
# backend/app/startup/canonical_db_validation.py
import logging
from sqlalchemy.orm import Session

from app.services.canonical_entitlement_db_consistency_validator import (
    CanonicalEntitlementDbConsistencyError,
    CanonicalEntitlementDbConsistencyValidator,
)

logger = logging.getLogger(__name__)
_VALID_MODES = frozenset({"strict", "warn", "off"})


def run_canonical_db_startup_validation(mode: str, db: Session) -> None:
    if mode not in _VALID_MODES:
        logger.warning(
            "canonical_db_startup_validation_invalid_mode mode=%s fallback=strict", mode
        )
        mode = "strict"

    if mode == "off":
        logger.warning("canonical_db_startup_validation_disabled")
        return

    try:
        CanonicalEntitlementDbConsistencyValidator.validate(db)
        logger.info("canonical_db_startup_validation_ok")
    except CanonicalEntitlementDbConsistencyError as exc:
        logger.error("canonical_db_startup_validation_failed errors=%s", exc)
        if mode == "strict":
            raise
```

### Intégration dans `_app_lifespan` (main.py)

L'appel s'insère dans le bloc `with SessionLocal() as db:` existant, **après** `validate_catalog_vs_db(db)` :

```python
# Actuel (61.29) :
run_feature_scope_startup_validation(settings.feature_scope_validation_mode)

# Story 59.2
from app.infra.db.session import SessionLocal
from app.prompts.validators import validate_catalog_vs_db

with SessionLocal() as db:
    validate_catalog_vs_db(db)

yield
```

Devient :

```python
# Story 61.29
run_feature_scope_startup_validation(settings.feature_scope_validation_mode)

# Story 59.2 + 61.30
from app.infra.db.session import SessionLocal
from app.prompts.validators import validate_catalog_vs_db
from app.startup.canonical_db_validation import run_canonical_db_startup_validation

with SessionLocal() as db:
    validate_catalog_vs_db(db)
    run_canonical_db_startup_validation(settings.canonical_db_validation_mode, db)

yield
```

**Important :** L'import de `run_canonical_db_startup_validation` doit être placé en haut du fichier avec les autres imports (pas dans le `with` bloc), pour rester cohérent avec le style du fichier. Vérifier les imports existants en haut de `main.py`.

### Config dans config.py

Pattern à ajouter (calqué exactement sur `_parse_feature_scope_validation_mode`) :

```python
@staticmethod
def _parse_canonical_db_validation_mode() -> str:
    raw_mode = os.getenv("CANONICAL_DB_VALIDATION_MODE", "strict").strip().lower()
    if raw_mode in {"strict", "warn", "off"}:
        return raw_mode
    logger.warning(
        "canonical_db_startup_validation_invalid_mode mode=%s fallback=strict",
        raw_mode,
    )
    return "strict"
```

Dans `__init__`, après `self.feature_scope_validation_mode = ...` :

```python
# Story 61.30
self.canonical_db_validation_mode = self._parse_canonical_db_validation_mode()
```

### Implémentation du script CLI

```python
# backend/scripts/check_canonical_entitlement_db_consistency.py
import sys
from pathlib import Path


def _ensure_backend_root_on_path() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def main() -> int:
    _ensure_backend_root_on_path()
    from app.infra.db.session import SessionLocal
    from app.services.canonical_entitlement_db_consistency_validator import (
        CanonicalEntitlementDbConsistencyError,
        CanonicalEntitlementDbConsistencyValidator,
    )

    try:
        with SessionLocal() as db:
            CanonicalEntitlementDbConsistencyValidator.validate(db)
        print("[OK] Canonical entitlement DB is consistent.")
        return 0
    except CanonicalEntitlementDbConsistencyError as exc:
        print(f"[ERROR] {exc}")
        return 1
    except Exception as exc:
        print(f"[CRITICAL] Unexpected error: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
```

### Tests du validateur (pattern in-memory SQLite)

Utiliser le même pattern que `test_entitlement_service.py` (in-memory SQLite + Base.metadata) :

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.infra.db.base import Base
from app.infra.db.models.product_entitlements import (
    AccessMode, Audience, FeatureCatalogModel, PlanCatalogModel,
    PlanFeatureBindingModel, PlanFeatureQuotaModel, PeriodUnit, ResetMode,
)

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)
```

**Exemple de fixture de DB cohérente (nominal OK) :**

```python
def _seed_consistent_db(db: Session) -> None:
    features = [
        FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat", is_metered=True, is_active=True),
        FeatureCatalogModel(feature_code="thematic_consultation", feature_name="Consult", is_metered=True, is_active=True),
        FeatureCatalogModel(feature_code="natal_chart_long", feature_name="Natal", is_metered=True, is_active=True),
        FeatureCatalogModel(feature_code="b2b_api_access", feature_name="B2B API", is_metered=False, is_active=True),
    ]
    db.add_all(features)
    db.flush()

    b2c_plan = PlanCatalogModel(plan_code="premium", plan_name="Premium", audience=Audience.B2C, is_active=True)
    b2b_plan = PlanCatalogModel(plan_code="enterprise", plan_name="Enterprise", audience=Audience.B2B, is_active=True)
    db.add_all([b2c_plan, b2b_plan])
    db.flush()

    # B2C feature bound to B2C plan (QUOTA with quota)
    chat_feature = next(f for f in features if f.feature_code == "astrologer_chat")
    binding = PlanFeatureBindingModel(
        plan_id=b2c_plan.id, feature_id=chat_feature.id,
        access_mode=AccessMode.QUOTA, is_enabled=True,
    )
    db.add(binding)
    db.flush()
    db.add(PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id, quota_key="daily", quota_limit=5,
        period_unit=PeriodUnit.DAY, period_value=1, reset_mode=ResetMode.CALENDAR,
    ))

    # B2B feature bound to B2B plan (UNLIMITED, no quota)
    b2b_feature = next(f for f in features if f.feature_code == "b2b_api_access")
    db.add(PlanFeatureBindingModel(
        plan_id=b2b_plan.id, feature_id=b2b_feature.id,
        access_mode=AccessMode.UNLIMITED, is_enabled=True,
    ))
    db.commit()
```

**Test DB → registre (feature bindée mais absente du registre) :**

```python
def test_validator_fails_bound_feature_not_registered(db):
    # Feature en DB, active, mais PAS dans FEATURE_SCOPE_REGISTRY
    unknown_feature = FeatureCatalogModel(
        feature_code="unknown_quota_feature", feature_name="Unknown", is_metered=True, is_active=True
    )
    db.add(unknown_feature)
    b2c_plan = PlanCatalogModel(plan_code="premium", plan_name="Premium", audience=Audience.B2C, is_active=True)
    db.add(b2c_plan)
    db.flush()
    db.add(PlanFeatureBindingModel(
        plan_id=b2c_plan.id, feature_id=unknown_feature.id,
        access_mode=AccessMode.UNLIMITED, is_enabled=True,
    ))
    # Seed les 4 features connues pour éviter les erreurs registre → DB
    _seed_known_features_only(db)
    db.commit()

    with pytest.raises(CanonicalEntitlementDbConsistencyError) as excinfo:
        CanonicalEntitlementDbConsistencyValidator.validate(db)
    assert "unknown_quota_feature" in str(excinfo.value)
    assert "FEATURE_SCOPE_REGISTRY" in str(excinfo.value)
```

**Note :** Pour `test_validator_fails_metered_feature_not_registered`, même pattern : créer une feature `is_metered=True, is_active=True` sans binding, absente du registre → le check 2 doit la signaler.

### Tests du bootstrap (pattern mock)

Calquer exactement `test_feature_scope_startup_validation.py` :

```python
VALIDATE_PATH = (
    "app.startup.canonical_db_validation"
    ".CanonicalEntitlementDbConsistencyValidator.validate"
)
```

Passer `db=MagicMock()` (ou `MagicMock(spec=Session)`) pour les tests du bootstrap ; le validateur est patché, donc la session ne sera pas vraiment utilisée.

### Tests CLI (pattern mock)

Calquer `test_check_feature_scope_registry_cli.py` :

```python
VALIDATE_PATH_CLI = (
    "app.services.canonical_entitlement_db_consistency_validator"
    ".CanonicalEntitlementDbConsistencyValidator.validate"
)
```

Patcher aussi `SessionLocal` pour éviter une vraie connexion DB :

```python
from unittest.mock import patch, MagicMock
from scripts.check_canonical_entitlement_db_consistency import main

def test_cli_main_exit_0_on_consistent_db():
    mock_db = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_db)
    mock_ctx.__exit__ = MagicMock(return_value=False)

    with patch("app.infra.db.session.SessionLocal", return_value=mock_ctx):
        with patch(VALIDATE_PATH_CLI):
            assert main() == 0
```

### Contraintes techniques

- Pas de migration Alembic (les tables existent déjà depuis 61.7–61.16)
- Pas de modification d'API publique
- Le module `backend/app/startup/` est déjà un package Python (61.29 a créé `__init__.py`)
- Tester uniquement avec `pytest` — pas de subprocess

### Séquence CI mise à jour

```bash
ruff check backend/
pytest backend/app/tests/
python backend/scripts/check_feature_scope_registry.py        # 61.28/61.29
python backend/scripts/check_canonical_entitlement_db_consistency.py  # 61.30 (nouveau)
```

### Project Structure Notes

**Nouveaux fichiers :**

- `backend/app/services/canonical_entitlement_db_consistency_validator.py`
- `backend/app/startup/canonical_db_validation.py`
- `backend/scripts/check_canonical_entitlement_db_consistency.py`
- `backend/app/tests/unit/test_canonical_entitlement_db_consistency_validator.py`
- `backend/app/tests/unit/test_check_canonical_entitlement_db_consistency_cli.py`
- `backend/app/tests/unit/test_canonical_db_startup_validation.py`

**Fichiers modifiés :**

- `backend/app/core/config.py` — ajouter `canonical_db_validation_mode`
- `backend/app/main.py` — brancher `run_canonical_db_startup_validation` dans `_app_lifespan`
- `backend/docs/entitlements-canonical-platform.md` — section 61.30
- `scripts/quality-gate.ps1` — ajouter le nouveau CLI comme étape CI uniquement quand la DB de validation est prête (`CANONICAL_DB_QUALITY_GATE_READY=1`)

### References

- [Source: backend/app/startup/feature_scope_validation.py] — pattern bootstrap à calquer exactement
- [Source: backend/app/core/config.py#L62-L70] — `_parse_feature_scope_validation_mode` à dupliquer pour la DB
- [Source: backend/app/main.py#L254-L264] — zone d'insertion dans `_app_lifespan`
- [Source: backend/app/services/feature_registry_consistency_validator.py] — pattern d'agrégation d'erreurs
- [Source: backend/scripts/check_feature_scope_registry.py] — pattern CLI `main() -> int`
- [Source: backend/app/tests/unit/test_entitlement_service.py#L23-L29] — fixture DB in-memory SQLite
- [Source: backend/app/tests/unit/test_feature_scope_startup_validation.py] — pattern tests bootstrap
- [Source: backend/app/tests/unit/test_check_feature_scope_registry_cli.py] — pattern tests CLI
- [Source: backend/app/infra/db/models/product_entitlements.py] — modèles DB (FeatureCatalogModel, PlanCatalogModel, PlanFeatureBindingModel, PlanFeatureQuotaModel, Audience, AccessMode)
- [Source: backend/app/services/feature_scope_registry.py] — FEATURE_SCOPE_REGISTRY, FeatureScope

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp (orchestrated by dev-story workflow)

### Debug Log References

- Résolution d'un conflit de configuration de logging via Alembic dans `backend/migrations/env.py`.
- Isolation des loggers dans les tests unitaires pour fiabiliser les captures `caplog`.
- Mise à jour du seeding dans les tests d'intégration pour satisfaire la nouvelle validation stricte.

### Completion Notes List

- Validateur DB complet implémenté et branché au démarrage.
- Check DB → registre resserré aux features réellement engagées dans des bindings `QUOTA`, pour éviter les faux positifs sur de futures features metered hors entitlement.
- Les erreurs du validateur ne dupliquent plus les absences déjà remontées par le check registre → DB pour les features obligatoires.
- Le quality gate n'exécute le CLI DB canonique que lorsque la DB est explicitement provisionnée, migrée et seedée (`CANONICAL_DB_QUALITY_GATE_READY=1`).
- Documentation et Quality Gate mis à jour après review corrective.

### File List

- `backend/app/core/config.py`
- `backend/app/main.py`
- `backend/app/services/canonical_entitlement_db_consistency_validator.py`
- `backend/app/startup/canonical_db_validation.py`
- `backend/app/tests/integration/_subprocess/secret_rotation_restart_runner.py`
- `backend/app/tests/integration/test_load_smoke_critical_flows.py`
- `backend/app/tests/integration/test_pipeline_scripts.py`
- `backend/app/tests/integration/test_secret_rotation_critical_flows.py`
- `backend/app/tests/unit/test_b2b_api_entitlement_gate.py`
- `backend/app/tests/unit/test_backfill_plan_catalog.py`
- `backend/app/tests/unit/test_canonical_db_startup_validation.py`
- `backend/app/tests/unit/test_canonical_entitlement_db_consistency_validator.py`
- `backend/app/tests/unit/test_check_canonical_entitlement_db_consistency_cli.py`
- `backend/app/tests/unit/test_feature_scope_startup_validation.py`
- `backend/app/tests/unit/test_migrate_legacy_quota_to_canonical.py`
- `backend/app/tests/unit/test_settings.py`
- `backend/docs/entitlements-canonical-platform.md`
- `backend/migrations/env.py`
- `backend/scripts/check_canonical_entitlement_db_consistency.py`
- `scripts/quality-gate.ps1`

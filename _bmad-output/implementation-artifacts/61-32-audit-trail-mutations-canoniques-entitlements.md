# Story 61.32 : Audit trail des mutations canoniques d'entitlements

Status: done

## Story

En tant qu'opérateur ou développeur backend,
je veux que toute mutation canonique d'entitlements effectuée via `CanonicalEntitlementMutationService` laisse une trace d'audit structurée,
afin de pouvoir reconstituer précisément les changements appliqués aux bindings et quotas, identifier leur origine, et faciliter l'investigation en cas de régression ou de mauvaise configuration.

## Contexte

La story 61.31 a centralisé les écritures canoniques dans `CanonicalEntitlementMutationService`.
C'est le point d'accroche idéal pour ajouter une traçabilité fiable.

Aujourd'hui, on sait :
- empêcher les mutations incohérentes,
- valider la cohérence au boot et en CI,
- centraliser les écritures.

Mais on ne sait pas encore répondre proprement à :
- quel script ou service a modifié un binding,
- quel était l'état avant/après,
- quel plan et quelle feature ont été touchés,
- si une modification provient d'un seed, d'un backfill, d'un repair ops, ou d'une future interface admin.

Cette story ajoute un **audit trail transactionnel**, sans modifier les contrats API publics.

## Acceptance Criteria

### AC 1 — Table d'audit des mutations canoniques

1. Une nouvelle table `canonical_entitlement_mutation_audits` est créée via Alembic.
2. Elle contient au minimum :
   - `id`
   - `occurred_at`
   - `operation` (`"upsert_plan_feature_configuration"`)
   - `plan_id`
   - `plan_code_snapshot`
   - `feature_code`
   - `actor_type` (`"script" | "service" | "ops" | "system"`)
   - `actor_identifier` (ex: `seed_product_entitlements.py`, `backfill_plan_catalog_from_legacy.py`, `b2b_entitlement_repair_service`)
   - `request_id` nullable
   - `source_origin`
   - `before_payload` JSON
   - `after_payload` JSON
3. `before_payload` et `after_payload` contiennent un snapshot structuré du binding et de ses quotas.

### AC 2 — Écriture d'audit centralisée

4. `CanonicalEntitlementMutationService.upsert_plan_feature_configuration(...)` écrit exactement **une** ligne d'audit par mutation effective réussie.
5. L'écriture d'audit est faite dans la **même transaction** que la mutation canonique.
6. Si la transaction principale rollback, la ligne d'audit rollback aussi.
7. **Règle no-op** : si l'appel est idempotent et ne change rien en base (diff réel nul), **aucune ligne d'audit n'est créée**. Cela évite le bruit dans la table.

### AC 3 — Pas d'audit sur validation échouée ou dry-run

8. Si `CanonicalMutationValidationError` est levée avant écriture, aucune ligne d'audit n'est créée.
9. En `dry_run=True` côté appelant, aucune ligne d'audit persistée n'est créée (le dry-run roule dans un savepoint annulé — voir 61.31).
10. Le dry-run peut calculer un diff mémoire pour son propre reporting métier, mais ne doit écrire aucune ligne dans `canonical_entitlement_mutation_audits` ni produire de pseudo-audit alternatif.

### AC 4 — Contexte d'origine obligatoire

11. Les appelants migrés en 61.31 passent un contexte d'origine explicite au service :
    - `seed_product_entitlements.py`
    - `backfill_plan_catalog_from_legacy.py`
    - `b2b_entitlement_repair_service.py`
12. Ce contexte est persisté dans `actor_type` + `actor_identifier`.
13. `source_origin` ORM continue d'être renseigné comme avant sur les bindings/quotas eux-mêmes ; l'audit ne le remplace pas, il le complète.
14. Les appelants doivent fournir un `CanonicalMutationContext` explicite ; aucun fallback implicite (`actor_type="system"` par défaut, etc.) n'est autorisé dans cette story.

### AC 5 — Snapshot avant / après normalisé

14. Le snapshot `before_payload` / `after_payload` contient au minimum :
    - binding : `is_enabled`, `access_mode`, `variant_code`, `source_origin`
    - quotas : liste triée avec `quota_key`, `quota_limit`, `period_unit`, `period_value`, `reset_mode`, `source_origin`
15. Les quotas sont ordonnés de manière déterministe dans le payload (par `(quota_key, period_unit, period_value, reset_mode)`) pour rendre les diffs stables.
16. Les enums sont sérialisés par leur `.value` (chaîne) dans les snapshots. La comparaison no-op est effectuée **après** normalisation complète — si `before_payload == after_payload`, aucun audit n'est écrit.

### AC 6 — Tests

17. `backend/app/tests/unit/test_canonical_entitlement_mutation_audit.py` est créé avec :
    - `test_audit_row_created_on_binding_create` : création → une ligne d'audit
    - `test_audit_row_created_on_binding_update` : mise à jour effective → une ligne d'audit
    - `test_audit_row_contains_before_and_after_payload` : les payloads avant/après sont corrects
    - `test_audit_row_contains_actor_context` : `actor_type`, `actor_identifier`, `request_id` sont persistés correctement
    - `test_no_audit_row_on_validation_error` : validation échouée → aucune ligne
    - `test_no_audit_row_on_dry_run` : dry_run simulé via savepoint rollback → aucune ligne persistée
    - `test_no_audit_row_when_no_effective_change` : appel idempotent sans diff → aucune ligne
    - `test_audit_row_is_rolled_back_with_transaction` : rollback transactionnel → aucune ligne persistée dans une nouvelle session

18. Les tests de 61.31 (`test_canonical_entitlement_mutation_service.py`) restent verts sans modification métier.

### AC 7 — Documentation

18. `backend/docs/entitlements-canonical-platform.md` est mis à jour avec une section **"Traçabilité write-time des mutations canoniques (Story 61.32)"**.
19. La doc précise :
    - que toute mutation canonique passe par `CanonicalEntitlementMutationService`,
    - qu'une mutation effective laisse un audit trail transactionnel,
    - que les dry-runs et validations échouées ne persistent rien,
    - que les no-ops ne génèrent pas de ligne d'audit.

### AC 8 — Non-régression

20. Aucun contrat API public modifié.
21. Une migration Alembic est créée uniquement pour la table d'audit.
22. Les suites entitlements/quota/B2B existantes restent vertes.

---

## Tasks / Subtasks

- [x] **Créer `CanonicalMutationContext` et le modèle ORM d'audit** (AC: 1, 4)
  - [x] Créer `backend/app/infra/db/models/canonical_entitlement_mutation_audit.py`
  - [x] Définir `CanonicalMutationContext` (dataclass) dans le service ou dans un module dédié
  - [x] Ajouter l'import du nouveau modèle dans `backend/app/infra/db/models/__init__.py`

- [x] **Créer la migration Alembic** (AC: 1)
  - [x] `20260328_0056_create_canonical_entitlement_mutation_audits.py`
  - [x] `down_revision = "20260327_0055"`
  - [x] Index sur `occurred_at`, `feature_code`, `plan_id`

- [x] **Ajouter l'audit dans `CanonicalEntitlementMutationService`** (AC: 2, 3, 5)
  - [x] Ajouter paramètre `mutation_context: CanonicalMutationContext` à `upsert_plan_feature_configuration`
  - [x] Calculer `before_payload` avant l'upsert (snapshot binding + quotas existants)
  - [x] Appliquer l'upsert (code existant inchangé)
  - [x] Calculer `after_payload` après l'upsert
  - [x] Comparer before/after → insérer la ligne d'audit seulement si diff réel
  - [x] Aucun `db.commit()` dans le service

- [x] **Migrer les appelants** (AC: 4)
  - [x] `seed_product_entitlements.py` — passer `mutation_context=CanonicalMutationContext(...)`
  - [x] `backfill_plan_catalog_from_legacy.py` — idem
  - [x] `b2b_entitlement_repair_service.py` — idem (dry_run via savepoint existant couvre AC 3.9)

- [x] **Créer les tests unitaires d'audit** (AC: 6)
  - [x] `backend/app/tests/unit/test_canonical_entitlement_mutation_audit.py`
  - [x] Session SQLite in-memory (même pattern 61.31)
  - [x] Couvrir les 8 cas listés en AC 6

- [x] **Mettre à jour la documentation** (AC: 7)
  - [x] `backend/docs/entitlements-canonical-platform.md`

- [x] **Validation finale** (AC: 8)
  - [x] `ruff check` sur tous les fichiers créés/modifiés
  - [x] `pytest backend/app/tests/unit/test_canonical_entitlement_mutation_audit.py`
  - [x] `pytest backend/app/tests/unit/test_canonical_entitlement_mutation_service.py`
  - [x] Suite non-régression 61.27–61.31

---

## Dev Notes

### Architecture et responsabilités

L'audit trail est **entièrement encapsulé dans `CanonicalEntitlementMutationService`**. Les appelants passent uniquement un `CanonicalMutationContext`, le service gère le reste.

**Ce que cette story fait :**
- Ajoute un modèle ORM `CanonicalEntitlementMutationAuditModel` + migration Alembic
- Étend la signature de `upsert_plan_feature_configuration` avec `mutation_context`
- Capture before/after snapshots et insère la ligne d'audit si diff réel
- Met à jour les 3 appelants pour fournir le contexte

**Ce que cette story ne fait PAS :**
- Pas d'endpoint API de consultation (story 61.33 potentielle)
- Pas de rollback assisté ou diff viewer
- Pas de modification des contrats API publics
- Pas de commit interne dans le service

### Nouveau modèle ORM

Fichier : `backend/app/infra/db/models/canonical_entitlement_mutation_audit.py`

```python
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CanonicalEntitlementMutationAuditModel(Base):
    __tablename__ = "canonical_entitlement_mutation_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )
    operation: Mapped[str] = mapped_column(String(64), nullable=False)
    plan_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    plan_code_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)
    feature_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_origin: Mapped[str] = mapped_column(String(64), nullable=False)
    before_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    after_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
```

**Pas de ForeignKey** sur `plan_id` → la table d'audit est append-only et doit survivre même si le plan est supprimé. `plan_code_snapshot` sevrt de lisibilité.

### `CanonicalMutationContext` dataclass

À définir dans `canonical_entitlement_mutation_service.py` (ou `canonical_entitlement_mutation_audit.py`) :

```python
from dataclasses import dataclass
from typing import Literal

ActorType = Literal["script", "service", "ops", "system"]

@dataclass(frozen=True)
class CanonicalMutationContext:
    actor_type: ActorType
    actor_identifier: str  # ex: "seed_product_entitlements.py"
    request_id: str | None = None
```

`actor_type` est borné par `Literal` pour éviter les chaînes libres et maintenir la valeur analytique de l'audit trail. Tout `actor_type` hors des 4 valeurs autorisées doit être rejeté par mypy/ruff à l'appel site.

### Modification de la signature du service

**Avant (61.31) :**
```python
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
```

**Après (61.32) :**
```python
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
    mutation_context: CanonicalMutationContext,
) -> PlanFeatureBindingModel:
```

### Logique d'audit dans le service

```python
# Avant l'upsert : capturer before_payload
before_payload = _snapshot_binding(db, plan.id, feature.id)

# ... upsert existant inchangé ...

# Après le flush : capturer after_payload
after_payload = _snapshot_binding_by_id(db, binding.id)

# Insérer l'audit seulement si diff réel
if before_payload != after_payload:
    db.add(CanonicalEntitlementMutationAuditModel(
        operation="upsert_plan_feature_configuration",
        plan_id=plan.id,
        plan_code_snapshot=plan.plan_code,
        feature_code=feature_code,
        actor_type=mutation_context.actor_type,
        actor_identifier=mutation_context.actor_identifier,
        request_id=mutation_context.request_id,
        source_origin=source_origin.value,
        before_payload=before_payload,
        after_payload=after_payload,
    ))
    db.flush()
```

### Format des snapshots

`before_payload` quand le binding n'existe pas encore → `{}` (dict vide, pas `None`).

Format d'un snapshot non vide :
```python
{
    "is_enabled": True,
    "access_mode": "quota",
    "variant_code": None,
    "source_origin": "manual",
    "quotas": [
        {
            "quota_key": "daily_chat",
            "quota_limit": 10,
            "period_unit": "day",
            "period_value": 1,
            "reset_mode": "calendar",
            "source_origin": "manual",
        }
    ]
}
```

Les quotas sont **triés par `(quota_key, period_unit, period_value, reset_mode)`** pour des diffs stables.

Les snapshots sont **entièrement normalisés** avant comparaison :
- tous les enums convertis en `.value` (chaîne)
- quotas triés de façon déterministe
- binding absent → `{}`

Si `before_payload == after_payload` après normalisation complète, aucune ligne d'audit n'est écrite (règle no-op).

### Helpers de snapshot (privés)

```python
@staticmethod
def _snapshot_binding(
    db: Session, plan_id: int, feature_id: int
) -> dict:
    """Retourne {} si le binding n'existe pas encore."""
    binding = db.scalar(
        select(PlanFeatureBindingModel).where(
            PlanFeatureBindingModel.plan_id == plan_id,
            PlanFeatureBindingModel.feature_id == feature_id,
        )
    )
    if binding is None:
        return {}
    return CanonicalEntitlementMutationService._snapshot_binding_by_id(db, binding.id)

@staticmethod
def _snapshot_binding_by_id(db: Session, binding_id: int) -> dict:
    binding = db.get(PlanFeatureBindingModel, binding_id)
    quotas = db.scalars(
        select(PlanFeatureQuotaModel)
        .where(PlanFeatureQuotaModel.plan_feature_binding_id == binding_id)
        .order_by(PlanFeatureQuotaModel.quota_key, PlanFeatureQuotaModel.period_unit)
    ).all()
    return {
        "is_enabled": binding.is_enabled,
        "access_mode": binding.access_mode.value,
        "variant_code": binding.variant_code,
        "source_origin": binding.source_origin.value,
        "quotas": [
            {
                "quota_key": q.quota_key,
                "quota_limit": q.quota_limit,
                "period_unit": q.period_unit.value if hasattr(q.period_unit, "value") else q.period_unit,
                "period_value": q.period_value,
                "reset_mode": q.reset_mode.value if hasattr(q.reset_mode, "value") else q.reset_mode,
                "source_origin": q.source_origin.value if hasattr(q.source_origin, "value") else q.source_origin,
            }
            for q in quotas
        ],
    }
```

**Attention SQLite** : après `db.flush()`, `db.get(PlanFeatureBindingModel, binding_id)` peut retourner l'objet depuis le cache d'identité SQLAlchemy. Cela convient pour les tests SQLite in-memory. En PostgreSQL (prod), le comportement est identique.

### Migration Alembic

Fichier : `backend/migrations/versions/20260328_0056_create_canonical_entitlement_mutation_audits.py`

```python
"""create canonical_entitlement_mutation_audits

Revision ID: 20260328_0056
Revises: 20260327_0055
Create Date: 2026-03-28
"""

import sqlalchemy as sa
from alembic import op

revision = "20260328_0056"
down_revision = "20260327_0055"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "canonical_entitlement_mutation_audits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("operation", sa.String(64), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("plan_code_snapshot", sa.String(64), nullable=False),
        sa.Column("feature_code", sa.String(64), nullable=False),
        sa.Column("actor_type", sa.String(32), nullable=False),
        sa.Column("actor_identifier", sa.String(128), nullable=False),
        sa.Column("request_id", sa.String(64), nullable=True),
        sa.Column("source_origin", sa.String(64), nullable=False),
        sa.Column("before_payload", sa.JSON(), nullable=False),
        sa.Column("after_payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cema_occurred_at", "canonical_entitlement_mutation_audits", ["occurred_at"])
    op.create_index("ix_cema_plan_id", "canonical_entitlement_mutation_audits", ["plan_id"])
    op.create_index("ix_cema_feature_code", "canonical_entitlement_mutation_audits", ["feature_code"])


def downgrade() -> None:
    op.drop_index("ix_cema_feature_code", table_name="canonical_entitlement_mutation_audits")
    op.drop_index("ix_cema_plan_id", table_name="canonical_entitlement_mutation_audits")
    op.drop_index("ix_cema_occurred_at", table_name="canonical_entitlement_mutation_audits")
    op.drop_table("canonical_entitlement_mutation_audits")
```

### Pattern de migration des appelants

**seed_product_entitlements.py** :
```python
from app.services.canonical_entitlement_mutation_service import (
    CanonicalEntitlementMutationService,
    CanonicalMutationContext,
)

_SEED_CONTEXT = CanonicalMutationContext(
    actor_type="script",
    actor_identifier="seed_product_entitlements.py",
)

# À l'appel :
CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
    db, plan=plan, feature_code=feature_code,
    ...,
    mutation_context=_SEED_CONTEXT,
)
```

Même pattern pour `backfill_plan_catalog_from_legacy.py` (`actor_identifier="backfill_plan_catalog_from_legacy.py"`) et `b2b_entitlement_repair_service.py` (`actor_identifier="b2b_entitlement_repair_service"`, `actor_type="service"`).

### Pattern de test

```python
@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

# Importer le nouveau modèle d'audit dans les fixtures :
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.services.canonical_entitlement_mutation_service import CanonicalMutationContext

_TEST_CONTEXT = CanonicalMutationContext(
    actor_type="script",
    actor_identifier="test_script.py",
)

def test_audit_row_created_on_binding_create(db, b2c_plan, chat_feature):
    CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
        db, b2c_plan, "astrologer_chat",
        is_enabled=True, access_mode=AccessMode.QUOTA,
        quotas=[{"quota_key": "daily", "quota_limit": 5,
                 "period_unit": PeriodUnit.DAY, "period_value": 1,
                 "reset_mode": ResetMode.CALENDAR}],
        source_origin=SourceOrigin.MANUAL,
        mutation_context=_TEST_CONTEXT,
    )
    audits = db.scalars(select(CanonicalEntitlementMutationAuditModel)).all()
    assert len(audits) == 1
    assert audits[0].before_payload == {}
    assert audits[0].after_payload["is_enabled"] is True
```

### Registre __init__.py

Ajouter dans `backend/app/infra/db/models/__init__.py` :
```python
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
# Et dans __all__ :
"CanonicalEntitlementMutationAuditModel",
```

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/infra/db/models/canonical_entitlement_mutation_audit.py` | Créer |
| `backend/app/infra/db/models/__init__.py` | Modifier — ajouter import + __all__ |
| `backend/migrations/versions/20260328_0056_create_canonical_entitlement_mutation_audits.py` | Créer |
| `backend/app/services/canonical_entitlement_mutation_service.py` | Modifier — context + audit |
| `backend/scripts/seed_product_entitlements.py` | Modifier — passer `mutation_context` |
| `backend/scripts/backfill_plan_catalog_from_legacy.py` | Modifier — passer `mutation_context` |
| `backend/app/services/b2b_entitlement_repair_service.py` | Modifier — passer `mutation_context` |
| `backend/app/tests/unit/test_canonical_entitlement_mutation_audit.py` | Créer |
| `backend/docs/entitlements-canonical-platform.md` | Mettre à jour |

### Dépendances de stories

- **61.31** : fournit `CanonicalEntitlementMutationService` et les 3 appelants migrés
- **61.30** : pattern SQLite in-memory pour les tests
- **61.7** : modèles ORM, enums

### Références

- [Source: backend/app/services/canonical_entitlement_mutation_service.py] — service à étendre
- [Source: backend/app/infra/db/models/audit_event.py] — pattern ORM avec JSON + DateTime(timezone=True)
- [Source: backend/migrations/versions/20260327_0055_create_enterprise_feature_usage_counters.py] — pattern migration Alembic (naming, structure)
- [Source: backend/app/infra/db/models/__init__.py] — registre des modèles à mettre à jour
- [Source: backend/app/tests/unit/test_canonical_entitlement_mutation_service.py] — fixtures SQLite in-memory réutilisables

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List
- Implémentation du modèle ORM `CanonicalEntitlementMutationAuditModel` pour l'audit des mutations.
- Extension de `CanonicalEntitlementMutationService` pour capturer les snapshots before/after et enregistrer l'audit.
- Migration des scripts de seed, backfill et repair pour fournir le `CanonicalMutationContext`.
- Création d'une suite de tests unitaires couvrant tous les cas d'acceptance (8 tests).
- Mise à jour de la documentation technique.
- Tous les tests de non-régression sont au vert.
- Revue post-implémentation: validation runtime ajoutée sur `CanonicalMutationContext` pour refuser un `actor_identifier` vide et normaliser `request_id`.
- Revue post-implémentation: la preuve de rollback transactionnel est désormais vérifiée depuis une nouvelle session SQLAlchemy, conformément à l'AC 17.

### File List
- `backend/app/infra/db/models/canonical_entitlement_mutation_audit.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/migrations/versions/20260328_0056_create_canonical_entitlement_mutation_audits.py`
- `backend/app/services/canonical_entitlement_mutation_service.py`
- `backend/scripts/seed_product_entitlements.py`
- `backend/scripts/backfill_plan_catalog_from_legacy.py`
- `backend/app/services/b2b_entitlement_repair_service.py`
- `backend/app/tests/unit/test_canonical_entitlement_mutation_audit.py`
- `backend/app/tests/unit/test_canonical_entitlement_mutation_service.py`
- `backend/docs/entitlements-canonical-platform.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log
- 2026-03-28: Implémentation complète de la story 61.32.
- 2026-03-28: Correctifs post-review sur la validation du contexte d'audit et le test de rollback transactionnel.

### Status
done

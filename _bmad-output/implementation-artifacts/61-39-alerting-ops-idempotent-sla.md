# Story 61.39 : Alerting ops idempotent sur la review queue SLA

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux que les mutations canoniques entrant en zone `due_soon` ou `overdue` génèrent des alertes ops idempotentes et traçables,
afin d'être notifié automatiquement des items critiques sans bruit de duplication et de pouvoir corréler chaque notification à un état précis de la work queue.

## Contexte

61.37 a livré la **work queue ops**.
61.38 a livré la **couche SLA** (`within_sla`, `due_soon`, `overdue`).

Il manque maintenant la couche d'**activation opérationnelle** : tant qu'un humain ne consulte pas la queue, une mutation critique peut rester invisible.

Cette story introduit un mécanisme d'alerting **idempotent**, **persisté** et **pilotable**, construit sur les données déjà existantes.

### Décision d'architecture

1. Table append-only `canonical_entitlement_mutation_alert_events`
2. Service `CanonicalEntitlementAlertService` qui réutilise la logique de la work queue via `CanonicalEntitlementReviewQueueService` (extrait du router)
3. Script CLI/cron externe au runtime HTTP

### Règle de déduplication

Clé métier : `(audit_id, effective_review_status, sla_status)`

- `audit:42:review:pending_review:sla:due_soon` → 1 alerte
- même audit → `overdue` → nouvelle alerte autorisée
- rerun sur état identique → **aucune nouvelle alerte**

### Scope strict

- pas de scheduler interne FastAPI
- pas d'email natif, pas de Slack/Teams SDK
- delivery : **webhook HTTP générique** + fallback log structuré
- endpoints 61.37/61.38 restent contractuellement inchangés

---

## Acceptance Criteria

### AC 1 — Service partagé `CanonicalEntitlementReviewQueueService`

1. `backend/app/services/canonical_entitlement_review_queue_service.py` créé.
2. Ce service encapsule la logique actuellement portée par `ops_entitlement_mutation_audits.py` pour :
   - chargement des audits candidats via `CanonicalEntitlementMutationAuditQueryService`
   - chargement batch des reviews
   - calcul du diff via `CanonicalEntitlementMutationDiffService`
   - calcul de `effective_review_status` (logique `_compute_review_state` actuelle)
   - calcul des champs SLA (`_compute_sla` / `_SLA_TARGETS` / `_SLA_DUE_SOON_RATIO`)
   - filtrage applicatif (`risk_level`, `effective_review_status`, `feature_code`, `actor_type`, `actor_identifier`, `incident_key`, `date_from`, `date_to`, `sla_status`)
   - tri métier des rows
3. Interface minimale publique :
   - `build_review_queue_rows(db, *, now_utc, risk_level=None, effective_review_status=None, feature_code=None, actor_type=None, actor_identifier=None, incident_key=None, date_from=None, date_to=None, sla_status=None, max_sql_rows=10000) -> list[ReviewQueueRow]`
   - `summarize_review_queue_rows(rows) -> ReviewQueueSummarySnapshot`
4. `ReviewQueueRow` dataclass interne avec au minimum :
   - `audit`, `diff`, `review_record`, `effective_review_status`
   - `sla_target_seconds`, `due_at`, `sla_status`, `overdue_seconds`
   - `age_seconds`, `age_hours`
5. Service strictement read-only : aucun `db.add()`, `db.flush()`, `db.commit()`.
6. Le service retourne toujours une liste complète de `ReviewQueueRow` : **pas de pagination dans le service**. La pagination HTTP, la sérialisation Pydantic et les codes d'erreur restent la responsabilité exclusive du router.
7. Les endpoints 61.37/61.38 migrent vers ce service **sans changer leur contrat HTTP**.

### AC 2 — Table append-only `canonical_entitlement_mutation_alert_events`

7. Migration Alembic `20260329_0059_create_canonical_entitlement_mutation_alert_events.py` créée.
8. Colonnes :
   - `id` (PK, autoincrement)
   - `audit_id` (FK → `canonical_entitlement_mutation_audits.id`, NOT NULL, index)
   - `dedupe_key` (str(255), NOT NULL, UNIQUE)
   - `alert_kind` (str(32), NOT NULL) — `sla_due_soon` ou `sla_overdue`
   - `risk_level_snapshot` (str(16), NOT NULL)
   - `effective_review_status_snapshot` (str(32), nullable)
   - `feature_code_snapshot` (str(64), NOT NULL)
   - `plan_id_snapshot` (int, NOT NULL)
   - `plan_code_snapshot` (str(64), NOT NULL)
   - `actor_type_snapshot` (str(32), NOT NULL)
   - `actor_identifier_snapshot` (str(128), NOT NULL)
   - `sla_target_seconds_snapshot` (int, nullable)
   - `due_at_snapshot` (datetime timezone=True, nullable)
   - `age_seconds_snapshot` (int, NOT NULL)
   - `delivery_channel` (str(32), NOT NULL) — `webhook` ou `log`
   - `delivery_status` (str(32), NOT NULL) — `sent`, `failed`
   - `delivery_error` (Text, nullable)
   - `request_id` (str(64), nullable)
   - `payload` (JSON, NOT NULL)
   - `created_at` (datetime timezone=True, NOT NULL, server_default=now(), index)
   - `delivered_at` (datetime timezone=True, nullable)
9. `down_revision` = `"20260328_0058"` (dernière migration `review_events`).

### AC 3 — Modèle SQLAlchemy `CanonicalEntitlementMutationAlertEventModel`

10. `backend/app/infra/db/models/canonical_entitlement_mutation_alert_event.py` créé.
11. Mapping SQLAlchemy moderne `Mapped[...] / mapped_column(...)`.
12. Enregistré dans `backend/app/infra/db/models/__init__.py` (import alphabétique cohérent avec les modèles existants).

### AC 4 — Service `CanonicalEntitlementAlertService`

13. `backend/app/services/canonical_entitlement_alert_service.py` créé.
14. Interface : `emit_sla_alerts(db, *, now_utc=None, dry_run=False, request_id=None, limit=None) -> AlertRunResult`
15. `AlertRunResult` dataclass : `sql_count`, `candidate_count`, `emitted_count`, `skipped_duplicate_count`, `failed_count`, `dry_run`
16. Candidats : `CanonicalEntitlementReviewQueueService.build_review_queue_rows(sla_status=None)` → filtrer `sla_status in {"due_soon", "overdue"}`.
17. Exclusion : `effective_review_status in {"closed", "expected"}` → jamais d'alerte.
18. `alert_kind = "sla_due_soon"` si `sla_status == "due_soon"`, `"sla_overdue"` si `sla_status == "overdue"`.
19. `dedupe_key = f"audit:{row.audit.id}:review:{row.effective_review_status or 'none'}:sla:{row.sla_status}"`.
20. Déduplication : charger en une requête les `dedupe_key` existants → si présent, skip.
21. Si nouveau : insérer la ligne → tenter delivery → mettre à jour `delivery_status`, `delivery_error`, `delivered_at`.
22. `db.flush()` autorisé, **jamais `db.commit()`**.
23. **Race condition** : si deux exécutions concurrentes insèrent simultanément le même `dedupe_key`, la contrainte unique lève une `IntegrityError`. Le service doit la capturer via savepoint + relecture, classer l'item en `skipped_duplicate` et poursuivre sans crash.

### AC 5 — Delivery webhook + fallback log structuré

24. Config ajoutée via le mécanisme de configuration existant dans `backend/app/core/config.py` :
    - `ops_review_queue_alerts_enabled: bool = False`
    - `ops_review_queue_alert_webhook_url: str | None = None`
    - `ops_review_queue_alert_base_url: str | None = None`
    - `ops_review_queue_alert_max_candidates: int = 100`
25. Variables d'environnement : `OPS_REVIEW_QUEUE_ALERTS_ENABLED`, `OPS_REVIEW_QUEUE_ALERT_WEBHOOK_URL`, `OPS_REVIEW_QUEUE_ALERT_BASE_URL`, `OPS_REVIEW_QUEUE_ALERT_MAX_CANDIDATES`.
26. `alerts_enabled == False` → retour immédiat sans création d'event.
27. Webhook configuré → POST HTTP JSON ; pas de webhook → log structuré (`delivery_channel="log"`, `delivery_status="sent"`).
28. Échec HTTP → event persisté avec `delivery_status="failed"`, `delivery_error` renseigné, `delivered_at=None`.
29. **Pas de retry automatique** : un event `failed` est dédupliqué par `dedupe_key` — un rerun identique ne réémet pas l'alerte. Le retry/replay des livraisons échouées est hors périmètre de 61.39.
30. Payload minimal :
    ```json
    {
      "alert_kind", "audit_id", "feature_code", "plan_id", "plan_code",
      "risk_level", "effective_review_status", "sla_status",
      "age_seconds", "age_hours", "due_at", "actor_type", "actor_identifier", "request_id"
    }
    ```
31. Si `ops_review_queue_alert_base_url` configuré : ajouter `queue_url` et `detail_url` au payload.

### AC 6 — Règle dry-run

32. `emit_sla_alerts(..., dry_run=True)` : calcule candidats, applique déduplication, **aucune écriture DB**, **aucun webhook**, retourne `AlertRunResult` fidèle.
33. Aucune ligne `canonical_entitlement_mutation_alert_events` créée en dry-run.
34. `candidate_count` dans `AlertRunResult` = nombre d'items après filtrage SLA (`due_soon` / `overdue`) et après application éventuelle de `limit`, **avant** déduplication.

### AC 7 — Script CLI

35. `backend/scripts/run_ops_review_queue_alerts.py` créé.
36. Arguments : `--dry-run`, `--limit`.
37. Ouvre session DB → appelle `emit_sla_alerts()` → `db.commit()` si OK, `db.rollback()` si exception.
38. Sortie : `[OK] emitted=X skipped_duplicate=Y failed=Z candidates=N`.
39. Codes de sortie : `0` succès/dry-run, `1` livraison partielle (`failed > 0`), `2` erreur inattendue.
40. Ne tourne **pas** au boot FastAPI. Conçu pour cron/scheduler externe.

### AC 8 — Pas de duplication logique queue/SLA

41. Le router délègue à `CanonicalEntitlementReviewQueueService` la construction read-only de la review queue : chargement, diff, `effective_review_status`, SLA, filtres applicatifs. Le router conserve uniquement les responsabilités HTTP : validation Query, pagination de réponse, sérialisation Pydantic et codes d'erreur.
42. Endpoints 61.37/61.38 contractuellement inchangés.
43. `CanonicalEntitlementMutationDiffService` non modifié.
44. `CanonicalEntitlementMutationAuditQueryService` non modifié.

### AC 9 — Tests unitaires

45. `backend/app/tests/unit/test_canonical_entitlement_alert_service.py` avec :
    - `test_emit_due_soon_alert_once`
    - `test_emit_overdue_alert_once`
    - `test_emit_skips_duplicate_dedupe_key`
    - `test_emit_new_alert_when_status_phase_changes`
    - `test_emit_dry_run_creates_no_rows`
    - `test_emit_failed_webhook_persists_failed_event`
    - `test_emit_ignores_closed_and_expected_items`
    - `test_emit_disabled_config_short_circuits`
    - `test_emit_concurrent_insert_handled_as_skipped_duplicate`
46. `backend/app/tests/unit/test_canonical_entitlement_review_queue_service.py` si service extrait.
47. Tests 61.37 et 61.38 restent verts sans changement de contrat.

### AC 10 — Tests d'intégration

48. `backend/app/tests/integration/test_ops_review_queue_alerts_script.py` avec :
    - `test_script_dry_run_no_persisted_rows`
    - `test_script_persists_alert_event_on_due_soon`
    - `test_script_exit_code_1_on_delivery_failure`
    - `test_script_no_duplicate_alert_on_second_run`
49. Tests d'intégration existants des endpoints ops 61.37/61.38 restent verts.

### AC 11 — Documentation

50. `backend/docs/entitlements-canonical-platform.md` mis à jour avec section **"Story 61.39 — Alerting ops idempotent"** : table, règle déduplication, script CLI, payload webhook, fallback log, comportement no-retry.
51. `backend/README.md` ou runbook mis à jour avec exemple cron.
52. `scripts/quality-gate.ps1` non modifié.

### AC 12 — Non-régression

53. Aucun contrat API public modifié.
54. Une seule migration Alembic créée.
55. Le runtime HTTP ne lance aucun job de fond.
56. Suites entitlements/quota/B2B existantes restent vertes.

---

## Tasks / Subtasks

- [x] **Créer `CanonicalEntitlementReviewQueueService`** (AC: 1, 8)
  - [x] Créer `backend/app/services/canonical_entitlement_review_queue_service.py`
  - [x] Définir `ReviewQueueRow` (dataclass)
  - [x] Extraire logique read-only depuis le router : `_build_filtered_review_queue_rows`, `_compute_review_state`, `_compute_sla`, `_SLA_TARGETS`, `_SLA_DUE_SOON_RATIO`, `_STATUS_PRIORITY`
  - [x] Implémenter `build_review_queue_rows(...)` et `summarize_review_queue_rows(...)`
  - [x] Migrer le router pour déléguer à ce service (sans changer la réponse HTTP)

- [x] **Créer le modèle ORM** (AC: 2, 3)
  - [x] Créer `backend/app/infra/db/models/canonical_entitlement_mutation_alert_event.py`
  - [x] Ajouter import dans `backend/app/infra/db/models/__init__.py`

- [x] **Créer la migration Alembic** (AC: 2)
  - [x] `backend/migrations/versions/20260329_0059_create_canonical_entitlement_mutation_alert_events.py`
  - [x] `down_revision = "20260328_0058"` (dernière migration review_events)
  - [x] `upgrade()` : create table + `UNIQUE INDEX dedupe_key` + indexes `audit_id`, `created_at`
  - [x] `downgrade()` : drop indexes + drop table

- [x] **Créer `CanonicalEntitlementAlertService`** (AC: 4, 5, 6)
  - [x] `backend/app/services/canonical_entitlement_alert_service.py`
  - [x] Définir `AlertRunResult`
  - [x] Implémenter chargement candidats via `CanonicalEntitlementReviewQueueService`
  - [x] Implémenter déduplication par `dedupe_key` (requête batch)
  - [x] Gérer la race condition : savepoint + catch `IntegrityError` → `skipped_duplicate`
  - [x] Implémenter persistance append-only
  - [x] Implémenter delivery webhook + fallback log
  - [x] Implémenter `dry_run=True`

- [x] **Ajouter la config** (AC: 5)
  - [x] Étendre `backend/app/core/config.py` avec les 4 champs `ops_review_queue_alert*`

- [x] **Créer le script CLI** (AC: 7)
  - [x] `backend/scripts/run_ops_review_queue_alerts.py`
  - [x] `--dry-run`, `--limit`
  - [x] `commit` / `rollback`, codes de sortie 0/1/2

- [x] **Tests unitaires** (AC: 9)
  - [x] `test_canonical_entitlement_alert_service.py` (8 tests)
  - [x] `test_canonical_entitlement_review_queue_service.py` si service extrait

- [x] **Tests d'intégration** (AC: 10)
  - [x] `test_ops_review_queue_alerts_script.py` (4 tests)
  - [x] Vérifier non-régression 61.37/61.38

- [x] **Documentation** (AC: 11)
  - [x] Section 61.39 dans `backend/docs/entitlements-canonical-platform.md`
  - [x] Runbook backend / README

- [x] **Validation finale**
  - [x] `ruff check` — zéro erreur
  - [x] `pytest unit`
  - [x] `pytest integration`
  - [x] `alembic upgrade head` / `alembic downgrade -1` / `alembic upgrade head`

---

## Dev Notes

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/services/canonical_entitlement_review_queue_service.py` | Créer |
| `backend/app/infra/db/models/canonical_entitlement_mutation_alert_event.py` | Créer |
| `backend/app/infra/db/models/__init__.py` | Modifier (import alphabétique) |
| `backend/migrations/versions/20260329_0059_create_canonical_entitlement_mutation_alert_events.py` | Créer |
| `backend/app/services/canonical_entitlement_alert_service.py` | Créer |
| `backend/app/core/config.py` | Modifier (ajouter 4 champs `ops_review_queue_alert*`) |
| `backend/scripts/run_ops_review_queue_alerts.py` | Créer |
| `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` | Modifier — refactor interne uniquement |
| `backend/app/tests/unit/test_canonical_entitlement_alert_service.py` | Créer |
| `backend/app/tests/unit/test_canonical_entitlement_review_queue_service.py` | Créer |
| `backend/app/tests/integration/test_ops_review_queue_alerts_script.py` | Créer |
| `backend/docs/entitlements-canonical-platform.md` | Modifier |
| `backend/README.md` (ou runbook) | Modifier |

### Ne pas modifier

- `canonical_entitlement_mutation_diff_service.py`
- `canonical_entitlement_mutation_service.py`
- `canonical_entitlement_mutation_audit_query_service.py`
- `canonical_entitlement_mutation_audit_review_service.py`
- Modèles SQLAlchemy de review / review history existants
- Pas d'endpoint public supplémentaire

---

### Contexte architectural issu du code existant (61.37/61.38)

Le router actuel `ops_entitlement_mutation_audits.py` contient les éléments suivants à extraire dans `CanonicalEntitlementReviewQueueService` :

```python
# À extraire/déplacer dans le service partagé :
_STATUS_PRIORITY: dict[str | None, int]  # déjà en haut du module
_SLA_TARGETS: dict[tuple[str, str | None], int]  # "high"+"pending_review" → 14400, etc.
_SLA_DUE_SOON_RATIO = 0.20

def _compute_sla(risk_level, eff_status, occurred_at, now_utc) -> dict  # helper pur
# logique _build_filtered_review_queue_rows → returns list[tuple(audit, diff, review_record, eff_status)]
# logique _to_queue_item → builds dict avec SLA fields
```

`_build_filtered_review_queue_rows()` retourne des tuples `(audit, diff, review_record, eff_status)`.
`_to_queue_item()` prend `(audit, *, diff, review_record, eff_status, now_utc)` et retourne un `dict`.

**Important** : la logique de calcul `effective_review_status` (basée sur `review_record`) doit rester dans le service partagé — elle était déjà dans `_build_filtered_review_queue_rows()`.

---

### Migration Alembic — numérotation

La chaîne de migrations canoniques existante :
- `20260328_0056` — `canonical_entitlement_mutation_audits`
- `20260328_0057` — `canonical_entitlement_mutation_audit_reviews`
- `20260328_0058` — `canonical_entitlement_mutation_audit_review_events`

Nouvelle migration :
```python
revision = "20260329_0059"
down_revision = "20260328_0058"
```

---

### Modèle SQLAlchemy — pattern recommandé

```python
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def _utc_now() -> datetime:
    from datetime import timezone
    return datetime.now(timezone.utc)


class CanonicalEntitlementMutationAlertEventModel(Base):
    __tablename__ = "canonical_entitlement_mutation_alert_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_audits.id"),
        nullable=False,
        index=True,
    )
    dedupe_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    alert_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_level_snapshot: Mapped[str] = mapped_column(String(16), nullable=False)
    effective_review_status_snapshot: Mapped[str | None] = mapped_column(String(32), nullable=True)
    feature_code_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)
    plan_id_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)
    plan_code_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_type_snapshot: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_identifier_snapshot: Mapped[str] = mapped_column(String(128), nullable=False)
    sla_target_seconds_snapshot: Mapped[int | None] = mapped_column(Integer, nullable=True)
    due_at_snapshot: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    age_seconds_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)
    delivery_channel: Mapped[str] = mapped_column(String(32), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(32), nullable=False)
    delivery_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, index=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

Vérifier le pattern exact de `Base` import dans les modèles voisins :
`from app.infra.db.base import Base` (cf. `canonical_entitlement_mutation_audit_review_event.py`).

---

### Enregistrement dans `__init__.py`

Le fichier `backend/app/infra/db/models/__init__.py` suit un ordre alphabétique par module. Ajouter après `canonical_entitlement_mutation_audit_review_event` :

```python
from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
```

---

### Clé de déduplication

```python
dedupe_key = (
    f"audit:{row.audit.id}:"
    f"review:{row.effective_review_status or 'none'}:"
    f"sla:{row.sla_status}"
)
```

Cette clé permet :
- alerte `due_soon` → puis alerte `overdue` (deux alertes distinctes)
- changement de phase review `pending_review` → `investigating` + `overdue` → nouvelle alerte
- rerun à état identique → **aucune duplication**

---

### Pattern du service d'alerting

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import httpx
import logging

from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class AlertRunResult:
    sql_count: int
    candidate_count: int
    emitted_count: int
    skipped_duplicate_count: int
    failed_count: int
    dry_run: bool


class CanonicalEntitlementAlertService:
    @staticmethod
    def emit_sla_alerts(
        db: Session,
        *,
        now_utc: datetime | None = None,
        dry_run: bool = False,
        request_id: str | None = None,
        limit: int | None = None,
    ) -> AlertRunResult:
        # 1. Vérifier config
        if not settings.ops_review_queue_alerts_enabled:
            return AlertRunResult(0, 0, 0, 0, 0, dry_run)

        # 2. Construire rows via CanonicalEntitlementReviewQueueService
        # 3. Filtrer sla_status in {"due_soon", "overdue"} + exclure closed/expected
        # 4. Appliquer limit (→ candidate_count = len après limit, avant dédup)
        # 5. Charger dedupe_keys existants en batch
        # 6. Pour chaque candidat non dupliqué :
        #    - dry_run → compter seulement (aucune écriture)
        #    - sinon → créer savepoint → insérer event → delivery → update status
        #    - IntegrityError sur dedupe_key → rollback savepoint → skipped_duplicate
        # 7. db.flush() jamais db.commit()
```

---

### Payload webhook

```json
{
  "alert_kind": "sla_overdue",
  "audit_id": 42,
  "feature_code": "astrologer_chat",
  "plan_id": 7,
  "plan_code": "premium",
  "risk_level": "high",
  "effective_review_status": "pending_review",
  "sla_status": "overdue",
  "age_seconds": 18100,
  "age_hours": 5.03,
  "due_at": "2026-03-29T10:00:00Z",
  "actor_type": "script",
  "actor_identifier": "seed_product_entitlements.py",
  "request_id": "req-123",
  "queue_url": "https://.../v1/ops/entitlements/mutation-audits/review-queue",
  "detail_url": "https://.../v1/ops/entitlements/mutation-audits/42"
}
```

---

### Script CLI — comportement

```bash
python backend/scripts/run_ops_review_queue_alerts.py --dry-run
python backend/scripts/run_ops_review_queue_alerts.py
python backend/scripts/run_ops_review_queue_alerts.py --limit 25
```

Sortie : `[OK] emitted=3 skipped_duplicate=7 failed=0 candidates=10`

Exit codes : `0` succès/dry-run, `1` si `failed > 0`, `2` exception.

---

### Config — mécanisme existant

Vérifier le pattern exact de `Settings` dans `config.py` avant d'ajouter les champs. Les nouveaux champs doivent suivre le même mécanisme de configuration que les champs existants :

```python
ops_review_queue_alerts_enabled: bool = False
ops_review_queue_alert_webhook_url: str | None = None
ops_review_queue_alert_base_url: str | None = None
ops_review_queue_alert_max_candidates: int = 100
```

Les noms de variables d'environnement correspondent automatiquement en majuscules préfixées par le `env_prefix` du projet (souvent vide ou `APP_`). Vérifier le `model_config` de `Settings` pour confirmer.

---

### Tests d'intégration — patterns de seed à réutiliser

Les helpers existants dans `test_ops_entitlement_mutation_audits_api.py` :

- `_seed_audit(db, before_payload, after_payload, occurred_at=None)` — créer un audit ; `occurred_at` doit être passable (déjà étendu en 61.38)
- `_cleanup_tables(db)` — nettoyage entre tests
- `_register_user_with_role_and_token(client, role="ops_admin")` — auth ops

Pour les tests d'intégration de 61.39, mocker le webhook avec `unittest.mock.patch` ou `httpx.MockTransport` pour éviter les appels réseau réels.

---

### Baseline tests (avant 61.39)

- 61.35 : 46 tests
- 61.36 : +8 → 54
- 61.37 : +12 → 66
- 61.38 : +9 → **75 tests**
- 61.39 unitaires : +8 (alert service) + N (queue service) → nouveau fichier
- 61.39 intégration : +4 → nouveaux fichiers

---

### Project Structure Notes

```
backend/
  app/
    api/v1/routers/
      ops_entitlement_mutation_audits.py  ← MODIFIER (refactor interne, déléguer au service)
    services/
      canonical_entitlement_review_queue_service.py  ← CRÉER
      canonical_entitlement_alert_service.py          ← CRÉER
    infra/db/models/
      canonical_entitlement_mutation_alert_event.py   ← CRÉER
      __init__.py                                      ← MODIFIER
    core/
      config.py                                        ← MODIFIER (+4 champs)
    tests/
      unit/
        test_canonical_entitlement_review_queue_service.py  ← CRÉER
        test_canonical_entitlement_alert_service.py         ← CRÉER
      integration/
        test_ops_review_queue_alerts_script.py              ← CRÉER
  migrations/versions/
    20260329_0059_create_canonical_entitlement_mutation_alert_events.py  ← CRÉER
  scripts/
    run_ops_review_queue_alerts.py  ← CRÉER
  docs/
    entitlements-canonical-platform.md  ← MODIFIER (section 61.39)
  README.md  ← MODIFIER (exemple cron)
```

---

### Références

- [Source: backend/app/api/v1/routers/ops_entitlement_mutation_audits.py] — logique actuelle `_STATUS_PRIORITY`, `_SLA_TARGETS`, `_compute_sla`, `_build_filtered_review_queue_rows`, `_to_queue_item`, `ReviewQueueItem`, `ReviewQueueSummaryData`
- [Source: backend/app/services/canonical_entitlement_mutation_audit_query_service.py] — chargement SQL des audits
- [Source: backend/app/services/canonical_entitlement_mutation_diff_service.py] — calcul `risk_level`
- [Source: backend/app/infra/db/models/__init__.py] — pattern d'enregistrement des modèles (ordre alphabétique)
- [Source: backend/app/infra/db/models/canonical_entitlement_mutation_audit_review_event.py] — pattern `Base`, `Mapped`, `mapped_column` à réutiliser
- [Source: backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py] — `_seed_audit`, `_cleanup_tables`, `_register_user_with_role_and_token`
- [Source: backend/docs/entitlements-canonical-platform.md] — documentation à compléter (section 61.39)
- [Story 61.38](61-38-sla-ops-mutations-canoniques.md) — source de `_compute_sla`, `ReviewQueueItem` avec SLA fields tels qu'implémentés
- [Story 61.37](61-37-work-queue-ops-mutations-canoniques.md) — source de `_build_filtered_review_queue_rows`, `ReviewQueueSummaryData`

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- 2026-03-29 : Revue de code exécutée sur l'implémentation 61.39, avec corrections directes des écarts relevés.
- 2026-03-29 : Le tri métier est désormais garanti dans `CanonicalEntitlementReviewQueueService`, ce qui aligne l'alerting limité (`--limit` / batch SQL) sur la priorité ops attendue.
- 2026-03-29 : `AlertRunResult.sql_count` reflète désormais le volume SQL réel avant filtrage, et le script CLI valide `--limit` puis rollback explicitement sur erreur inattendue.

### File List

- `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py`
- `backend/app/core/config.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/models/canonical_entitlement_mutation_alert_event.py`
- `backend/app/services/canonical_entitlement_alert_service.py`
- `backend/app/services/canonical_entitlement_review_queue_service.py`
- `backend/app/tests/integration/test_ops_review_queue_alerts_script.py`
- `backend/app/tests/unit/test_canonical_entitlement_alert_service.py`
- `backend/app/tests/unit/test_canonical_entitlement_review_queue_service.py`
- `backend/docs/entitlements-canonical-platform.md`
- `backend/migrations/versions/20260329_0059_create_canonical_entitlement_mutation_alert_events.py`
- `backend/scripts/run_ops_review_queue_alerts.py`
- `backend/README.md`
- `_bmad-output/implementation-artifacts/61-39-alerting-ops-idempotent-sla.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-03-29 : Story 61.39 créée.
- 2026-03-29 : Décision d'architecture actée : service partagé de review queue + alert events append-only + script CLI idempotent.
- 2026-03-29 : Corrections suite review : suppression `review_status` en doublon, `delivery_status` réduit à `sent`/`failed`, garde-fou race condition `dedupe_key` (savepoint + `IntegrityError`), clause no-retry explicite, `candidate_count` défini précisément, AC 8 reformulé (séparation router/service), mention `pydantic_settings` retirée des AC.
- 2026-03-29 : Code review 61.39 terminée, avec corrections sur le tri métier partagé, le comptage SQL remonté par l'alert service, la validation CLI de `--limit` et la cohérence du runbook backend.

# Story 61.56 : Idempotence du webhook Stripe — déduplication par event.id

Status: done

## Story

En tant que système backend,
je veux rendre le traitement des webhooks Stripe idempotent,
afin qu'un même événement rejoué, livré plusieurs fois ou retraité après incident ne provoque pas plusieurs mutations locales, plusieurs audits métier, ni plusieurs recalculs incohérents de l'état billing.

---

## Contexte

Stripe peut livrer plusieurs fois un même webhook et recommande de conserver les `event.id` déjà traités pour éviter un retraitement. Stripe peut également retenter la livraison automatique des événements non acquittés pendant jusqu'à 3 jours.

Le système actuel dispose déjà :
- d'un endpoint webhook signé (`POST /v1/billing/stripe-webhook`)
- d'un `StripeWebhookService` avec dispatch vers `StripeBillingProfileService`
- d'une réconciliation canonique via `update_from_event_payload()`
- d'un audit webhook best-effort
- d'une couverture complète des événements subscription/invoice (stories 61.4 à 61.55)

**Attention :** `StripeBillingProfileModel` possède déjà les champs `last_stripe_event_id`, `last_stripe_event_created`, `last_stripe_event_type` — **ce n'est pas une protection d'idempotence** au sens propre (pas de contrainte unique, pas d'atomicité, pas de statut processing/failed). Ces champs restent utiles pour l'observabilité mais ne doivent pas être confondus avec la nouvelle table dédiée.

Il manque la brique de robustesse prod : une table dédiée avec contrainte unique sur `stripe_event_id` garantissant qu'un même `event.id` ne déclenche les mutations billing qu'une seule fois.

---

## Acceptance Criteria

**AC1 — Une persistance locale des événements Stripe existe**

- [ ] Une table dédiée `stripe_webhook_events` est créée avec une migration Alembic
- [ ] Elle stocke au minimum : `stripe_event_id`, `event_type`, `stripe_object_id`, `livemode`, `received_at`, `processed_at`, `status`, `processing_attempts`, `last_error`
- [ ] `stripe_event_id` est soumis à une contrainte `UNIQUE` au niveau DB
- [ ] `status` accepte exactement : `processing`, `processed`, `failed`
- [ ] Le modèle SQLAlchemy est enregistré dans `backend/app/infra/db/models/__init__.py`

**AC2 — Un même event.id n'est jamais exécuté deux fois avec succès**

- [ ] Lorsqu'un webhook arrive avec un `event.id` déjà en `processed`, le backend n'exécute plus la réconciliation métier
- [ ] Lorsqu'un webhook arrive avec un `event.id` déjà en `processing`, le backend n'exécute pas un second traitement concurrent
- [ ] L'endpoint retourne HTTP 200 avec `{"status": "duplicate_ignored"}` pour les doublons `processed` ou `processing`
- [ ] Le duplicate est tracé dans les logs avec `outcome=duplicate_ignored`

**AC3 — La garde d'idempotence est atomique**

- [ ] Le code ne repose pas sur un SELECT préalable sans protection transactionnelle
- [ ] L'entrée est créée via une insertion DB qui lève une `IntegrityError` en cas de doublon (unicité garantie par la contrainte DB, pas par la logique applicative)
- [ ] Deux livraisons concurrentes du même `event.id` ne peuvent pas déclencher deux traitements complets

**AC4 — L'état de traitement est traçable**

- [ ] Un événement nouvellement claimé est marqué `processing`
- [ ] Après succès métier, il passe à `processed` avec `processed_at`
- [ ] En cas d'échec métier, il passe à `failed` avec `last_error`
- [ ] `processing_attempts` est incrémenté à chaque nouveau claim accepté (re-claim depuis `failed`)
- [ ] Les informations de diagnostic (`event_type`, `stripe_object_id`, `last_error`) sont exploitables pour l'ops

**AC5 — Le comportement en erreur reste compatible avec un retry futur**

- [ ] Si le traitement métier échoue après claim de l'événement, le statut est mis à `failed` avec `last_error`
- [ ] Un événement en `failed` n'est pas considéré comme définitivement traité
- [ ] Une nouvelle livraison ultérieure du même `event.id` peut re-claimer l'événement de manière atomique en le repassant à `processing` et en incrémentant `processing_attempts`
- [ ] Si un événement est déjà `processed`, toute nouvelle livraison du même `event.id` est absorbée avec HTTP 200 sans effet de bord

**AC6 — La solution reste compatible avec l'architecture billing existante**

- [ ] `StripeWebhookService.handle_event()` reste le point d'entrée métier et porte le guard d'idempotence — son interface publique ne change pas
- [ ] `StripeBillingProfileService.update_from_event_payload()` n'est pas modifié
- [ ] Les champs `last_stripe_event_id/created/type` existants sur `StripeBillingProfileModel` sont conservés à des fins d'observabilité
- [ ] L'endpoint `POST /v1/billing/stripe-webhook` dans `billing.py` continue d'appeler `handle_event()` puis de retourner `{"status": status}` sans modification

**AC7 — Documentation ops et dev**

- [ ] `docs/billing-webhook-idempotency.md` est créé
- [ ] La doc explique le cycle `processing → processed | failed`
- [ ] La doc précise pourquoi `event.id` suffit pour les replays exacts
- [ ] La doc note que Stripe peut émettre deux `Event` distincts pour un même objet — `(event.type, stripe_object_id)` pourra être utilisé comme garde complémentaire ultérieurement (hors périmètre de cette story)

**AC8 — Tests**

- [ ] Test unitaire : `claim_event()` premier passage → retourne `"accepted"`, ligne créée en `processing`
- [ ] Test unitaire : `claim_event()` second passage même `event.id` en `processed` → retourne `"duplicate_ignored"`
- [ ] Test unitaire : `claim_event()` sur un `event.id` en `failed` → retourne `"accepted"`, `processing_attempts` incrémenté
- [ ] Test unitaire : `claim_event()` sur un `event.id` en `processing` → retourne `"duplicate_ignored"`
- [ ] Test d'intégration : duplicate exact du webhook `invoice.paid` n'applique pas deux fois la mutation locale
- [ ] Test d'intégration : deux appels avec le même `event.id` → un seul traitement métier
- [ ] Test d'intégration : échec métier → statut `failed` persisté, retry suivant accepté

---

## Tasks / Subtasks

- [x] **Créer le modèle `StripeWebhookEventModel`** (AC: 1)
  - [x] Créer `backend/app/infra/db/models/stripe_webhook_event.py`
  - [x] Ajouter l'import dans `backend/app/infra/db/models/__init__.py` et le `__all__`

- [x] **Créer la migration Alembic** (AC: 1)
  - [x] Générer ou écrire `backend/migrations/versions/20260329_XXXX_add_stripe_webhook_events.py`
  - [x] `upgrade()` : `CREATE TABLE stripe_webhook_events` avec contrainte UNIQUE sur `stripe_event_id`
  - [x] `downgrade()` : `DROP TABLE stripe_webhook_events`

- [x] **Créer `StripeWebhookIdempotencyService`** (AC: 2, 3, 4, 5)
  - [x] Créer `backend/app/services/stripe_webhook_idempotency_service.py`
  - [x] Implémenter `claim_event(db, event) -> str` :
    - INSERT en `processing` si l'événement n'existe pas → retourne `"accepted"`
    - Sur `IntegrityError` : SELECT avec `with_for_update()` pour lire le statut existant
    - Si `processed` → retourne `"duplicate_ignored"`
    - Si `processing` → retourne `"duplicate_ignored"`
    - Si `failed` → UPDATE atomique vers `processing`, incrémente `processing_attempts`, remet `last_error = None` → retourne `"accepted"`
  - [x] Implémenter `mark_processed(db, event_id) -> None` : UPDATE status → `processed`, `processed_at = now()`
  - [x] Implémenter `mark_failed(db, event_id, error_message) -> None` : UPDATE status → `failed`, `last_error = message[:2000]`

- [x] **Intégrer le guard dans `StripeWebhookService.handle_event()`** (AC: 2, 3, 4, 5, 6)
  - [x] Appeler `claim_event()` avant la logique métier
  - [x] Si le résultat vaut `"duplicate_ignored"` → log `outcome=duplicate_ignored`, retourner `"duplicate_ignored"`
  - [x] Sinon exécuter la logique métier existante (tuple d'événements inchangé)
  - [x] En cas de succès → appeler `mark_processed()`
  - [x] En cas d'exception → appeler `mark_failed()` puis relancer l'exception

- [x] **Vérifier la cohérence des statuts de retour de l'endpoint** (AC: 2, 6)
  - [x] Aucune modification de `billing.py` nécessaire : `{"status": "duplicate_ignored"}` passe automatiquement

- [x] **Créer la documentation** (AC: 7)
  - [x] Créer `docs/billing-webhook-idempotency.md`

- [x] **Écrire les tests** (AC: 8)
  - [x] Tests unitaires dans `backend/app/tests/unit/test_stripe_webhook_idempotency_service.py` (nouveau)
  - [x] Tests d'intégration dans `backend/app/tests/integration/test_stripe_webhook_api.py` (compléter)

---

## Dev Notes

### Ce qui EXISTE déjà — NE PAS réinventer

**`StripeWebhookService` est déjà en place** (`backend/app/services/stripe_webhook_service.py`) :
```python
# handle_event() retourne déjà une chaîne de statut
def handle_event(db: Session, event: stripe.Event) -> str:
    # dispatch + update_from_event_payload + log
    return "processed" | "event_ignored" | "user_not_resolved"
```
L'intégration du guard s'y insère naturellement sans changer l'interface.

**L'endpoint webhook** (`billing.py` lignes ~1204-1256) appelle déjà `handle_event()` et retourne `{"status": status}`. Le nouveau statut `"duplicate_ignored"` passera automatiquement.

**Pattern de transaction** déjà en place dans `billing.py` :
```python
status = StripeWebhookService.handle_event(db, event)
db.commit()  # commit principal
# audit best-effort dans un second try/except avec db.rollback() sur erreur
```
La stratégie failed best-effort s'aligne sur ce pattern existant.

**Modèle DB existant** — `StripeBillingProfileModel` a `last_stripe_event_id` (String, nullable, non-unique). Ce champ **n'est pas** une garde d'idempotence — c'est de l'observabilité. Ne pas le confondre avec la nouvelle table.

**Migrations Alembic** : les fichiers récents dans `backend/migrations/versions/` utilisent soit le format `YYYYMMDD_NNNN_description.py` (ex : `20260307_0033_migration_b_...`), soit le hash auto-généré (ex : `fbdf4f0c6837_...`). Préférer le format daté pour cette story.

---

### Ce qui DOIT être créé

#### 1. Modèle SQLAlchemy

Fichier : `backend/app/infra/db/models/stripe_webhook_event.py`

```python
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StripeWebhookEventModel(Base):
    __tablename__ = "stripe_webhook_events"
    __table_args__ = (
        UniqueConstraint("stripe_event_id", name="uq_stripe_webhook_events_event_id"),
        Index("ix_stripe_webhook_events_event_type", "event_type"),
        Index("ix_stripe_webhook_events_stripe_object_id", "stripe_object_id"),
        Index("ix_stripe_webhook_events_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stripe_event_id: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    stripe_object_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    livemode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # processing | processed | failed
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="processing")
    processing_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
```

**`stripe_object_id`** : extraire via `getattr(event.data.object, "id", None)` dans `claim_event()`. Utile pour l'observabilité et pour un futur second niveau de déduplication métier par `(event.type, stripe_object_id)`.

#### 2. Enregistrement dans `__init__.py`

Fichier : `backend/app/infra/db/models/__init__.py`

Ajouter l'import après `StripeBillingProfileModel` :
```python
from app.infra.db.models.stripe_webhook_event import StripeWebhookEventModel
```
Et dans `__all__` :
```python
"StripeWebhookEventModel",
```

#### 3. Migration Alembic

Fichier : `backend/migrations/versions/20260329_XXXX_add_stripe_webhook_events.py`

```python
"""add_stripe_webhook_events

Revision ID: <généré>
Revises: <head actuelle>
Create Date: 2026-03-29 ...
"""
from alembic import op
import sqlalchemy as sa

revision = "<hash>"
down_revision = "<head>"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stripe_webhook_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("stripe_event_id", sa.String(255), nullable=False),
        sa.Column("event_type", sa.String(255), nullable=False),
        sa.Column("stripe_object_id", sa.String(255), nullable=True),
        sa.Column("livemode", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.String(32), nullable=False, server_default="processing"),
        sa.Column("processing_attempts", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.UniqueConstraint("stripe_event_id", name="uq_stripe_webhook_events_event_id"),
    )
    op.create_index("ix_stripe_webhook_events_event_type", "stripe_webhook_events", ["event_type"])
    op.create_index("ix_stripe_webhook_events_stripe_object_id", "stripe_webhook_events", ["stripe_object_id"])
    op.create_index("ix_stripe_webhook_events_status", "stripe_webhook_events", ["status"])


def downgrade() -> None:
    op.drop_index("ix_stripe_webhook_events_status", "stripe_webhook_events")
    op.drop_index("ix_stripe_webhook_events_stripe_object_id", "stripe_webhook_events")
    op.drop_index("ix_stripe_webhook_events_event_type", "stripe_webhook_events")
    op.drop_table("stripe_webhook_events")
```

#### 4. `StripeWebhookIdempotencyService`

Fichier : `backend/app/services/stripe_webhook_idempotency_service.py`

```python
from __future__ import annotations

import logging
from datetime import datetime, timezone

import stripe
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infra.db.models.stripe_webhook_event import StripeWebhookEventModel

logger = logging.getLogger(__name__)


class StripeWebhookIdempotencyService:

    @staticmethod
    def claim_event(db: Session, event: stripe.Event) -> str:
        """
        Tente de claimer l'événement pour traitement.
        Retourne :
          "accepted"          → nouvel événement ou re-claim d'un failed
          "duplicate_ignored" → déjà processed ou déjà processing
        """
        stripe_object_id = getattr(event.data.object, "id", None)
        try:
            record = StripeWebhookEventModel(
                stripe_event_id=event.id,
                event_type=event.type,
                stripe_object_id=stripe_object_id,
                livemode=getattr(event, "livemode", False),
                status="processing",
                processing_attempts=1,
            )
            db.add(record)
            db.flush()
            return "accepted"
        except IntegrityError:
            db.rollback()

        # L'événement existe déjà — lire son statut avec verrou row-level
        record = (
            db.query(StripeWebhookEventModel)
            .filter_by(stripe_event_id=event.id)
            .with_for_update()
            .first()
        )
        if record is None:
            # Race condition extrême : ligne disparue entre l'IntegrityError et le SELECT
            return "duplicate_ignored"

        if record.status in ("processed", "processing"):
            logger.info(
                "stripe_webhook_idempotency: duplicate event_id=%s event_type=%s "
                "existing_status=%s outcome=duplicate_ignored",
                event.id,
                event.type,
                record.status,
            )
            return "duplicate_ignored"

        if record.status == "failed":
            # Re-claim : l'événement a échoué lors d'un traitement précédent, on réessaie
            record.status = "processing"
            record.last_error = None
            record.processed_at = None
            record.processing_attempts += 1
            db.flush()
            logger.info(
                "stripe_webhook_idempotency: retry_from_failed event_id=%s event_type=%s "
                "attempt=%s",
                event.id,
                event.type,
                record.processing_attempts,
            )
            return "accepted"

        return "duplicate_ignored"

    @staticmethod
    def mark_processed(db: Session, event_id: str) -> None:
        """Met à jour la ligne vers 'processed'."""
        record = db.query(StripeWebhookEventModel).filter_by(stripe_event_id=event_id).first()
        if record:
            record.status = "processed"
            record.processed_at = datetime.now(timezone.utc)

    @staticmethod
    def mark_failed(db: Session, event_id: str, error_message: str) -> None:
        """Met à jour la ligne vers 'failed'. Appelé dans le bloc except de handle_event()."""
        record = db.query(StripeWebhookEventModel).filter_by(stripe_event_id=event_id).first()
        if record:
            record.status = "failed"
            record.last_error = error_message[:2000]
```

#### 5. Intégration dans `StripeWebhookService.handle_event()`

Fichier : `backend/app/services/stripe_webhook_service.py`

```python
from app.services.stripe_webhook_idempotency_service import StripeWebhookIdempotencyService

@staticmethod
def handle_event(db: Session, event: stripe.Event) -> str:
    event_type = event.type
    event_id = event.id
    customer_id = StripeWebhookService._extract_customer_id(event)

    logger.info(
        "stripe_webhook: received event_id=%s type=%s customer_id=%s",
        event_id, event_type, customer_id,
    )

    # --- GARDE D'IDEMPOTENCE ---
    claim_status = StripeWebhookIdempotencyService.claim_event(db, event)
    if claim_status == "duplicate_ignored":
        return "duplicate_ignored"

    try:
        user_id = StripeWebhookService._resolve_user_id(db, event)

        if event_type in (...):  # tuple existant inchangé
            if user_id is None:
                logger.warning("stripe_webhook: user not resolved ...")
                StripeWebhookIdempotencyService.mark_processed(db, event_id)
                return "user_not_resolved"

            StripeBillingProfileService.update_from_event_payload(db, user_id, event.to_dict())
            logger.info("stripe_webhook: processed event_id=%s ...", event_id, ...)
            StripeWebhookIdempotencyService.mark_processed(db, event_id)
            return "processed"

        StripeWebhookIdempotencyService.mark_processed(db, event_id)
        return "event_ignored"

    except Exception as exc:
        StripeWebhookIdempotencyService.mark_failed(db, event_id, str(exc))
        raise
```

**Note sur la transaction :**
La table d'idempotence ne doit pas dépendre du rollback de la mutation billing principale.

Le flux attendu est :

1. `claim_event()` inscrit ou re-claim l'événement dans `stripe_webhook_events` avec statut `processing`
2. la logique métier billing s'exécute dans la même session
3. en cas de succès, `mark_processed()` passe la ligne à `processed` — le routeur appelle ensuite `db.commit()` qui valide l'ensemble
4. en cas d'exception, `mark_failed()` passe la ligne à `failed` avant que le routeur rollbacke, ou le `db.commit()` du routeur propagera `failed` avant le rollback

Sémantique des statuts :
- `processed` = définitivement absorbé, toute nouvelle livraison retourne 200 sans effet
- `processing` = déjà en cours, protège contre la concurrence
- `failed` = échec diagnostiqué mais **réessayable** — la prochaine livraison du même `event.id` est acceptée et `processing_attempts` est incrémenté

#### 6. Statuts de retour de l'endpoint

L'endpoint `POST /v1/billing/stripe-webhook` retourne désormais `{"status": X}` avec X ∈ :
| Valeur | Signification |
|--------|--------------|
| `processed` | Traitement réussi |
| `duplicate_ignored` | event.id déjà connu — absorbé |
| `event_ignored` | Type d'événement non pris en charge |
| `user_not_resolved` | Stripe customer_id inconnu localement |
| `failed_internal` | Exception non gérée (endpoint catch-all) |
| `error_non_fatal` | Erreur de signature ou parsing (400 si signature invalide) |

---

### Stratégie de test

#### Tests unitaires (`test_stripe_webhook_idempotency_service.py`)

```python
# Utiliser une vraie DB SQLite en mémoire pour que la contrainte UNIQUE soit réelle

def test_claim_event_new_event_returns_accepted(db_session):
    event = make_mock_event("evt_new_001", "invoice.paid")
    result = StripeWebhookIdempotencyService.claim_event(db_session, event)
    assert result == "accepted"
    record = db_session.query(StripeWebhookEventModel).filter_by(stripe_event_id="evt_new_001").first()
    assert record.status == "processing"
    assert record.processing_attempts == 1

def test_claim_event_already_processed_returns_duplicate(db_session):
    event = make_mock_event("evt_dup_001", "invoice.paid")
    StripeWebhookIdempotencyService.claim_event(db_session, event)
    StripeWebhookIdempotencyService.mark_processed(db_session, "evt_dup_001")
    db_session.commit()
    result = StripeWebhookIdempotencyService.claim_event(db_session, event)
    assert result == "duplicate_ignored"

def test_claim_event_already_processing_returns_duplicate(db_session):
    event = make_mock_event("evt_proc_001", "invoice.paid")
    StripeWebhookIdempotencyService.claim_event(db_session, event)
    db_session.commit()  # ligne reste en processing
    result = StripeWebhookIdempotencyService.claim_event(db_session, event)
    assert result == "duplicate_ignored"

def test_claim_event_failed_returns_accepted_and_increments_attempts(db_session):
    event = make_mock_event("evt_fail_001", "invoice.paid")
    StripeWebhookIdempotencyService.claim_event(db_session, event)
    StripeWebhookIdempotencyService.mark_failed(db_session, "evt_fail_001", "some error")
    db_session.commit()
    result = StripeWebhookIdempotencyService.claim_event(db_session, event)
    assert result == "accepted"
    record = db_session.query(StripeWebhookEventModel).filter_by(stripe_event_id="evt_fail_001").first()
    assert record.processing_attempts == 2
    assert record.last_error is None

def test_mark_processed_updates_status(db_session): ...
def test_mark_failed_updates_status_and_error(db_session): ...
```

#### Tests d'intégration (`test_stripe_webhook_api.py` — compléter)

```python
def test_duplicate_webhook_invoice_paid_no_double_mutation():
    """Même event.id envoyé deux fois → un seul update_from_event_payload"""
    # Premier appel → {"status": "processed"}
    # Second appel → {"status": "duplicate_ignored"}, update_from_event_payload pas rappelé

def test_concurrent_same_event_id_single_treatment():
    """Deux appels avec le même event.id → un seul traitement métier"""
    # Simulable : mock claim_event pour que le second retourne "duplicate_ignored"

def test_business_failure_leaves_failed_retryable():
    """Exception dans update_from_event_payload → statut failed, retry suivant accepté"""
    # Premier appel : update_from_event_payload lève, statut → failed
    # Second appel : claim_event retourne "accepted", processing_attempts == 2
```

---

### Périmètre explicitement hors scope

- Déduplication par `(event.type, stripe_object_id)` — documenté dans la doc comme évolution future
- Nettoyage / purge automatique de la table `stripe_webhook_events` (rétention ops)
- Exposition d'une API d'admin pour lister les événements
- Réexécution manuelle d'un événement `failed`
- Monitoring / alerting sur les `failed` (hors périmètre de cette story)

---

### Project Structure Notes

- Nouveau modèle : `backend/app/infra/db/models/stripe_webhook_event.py`
- Enregistrement modèle : `backend/app/infra/db/models/__init__.py`
- Nouvelle migration : `backend/migrations/versions/20260329_XXXX_add_stripe_webhook_events.py`
- Nouveau service : `backend/app/services/stripe_webhook_idempotency_service.py`
- Modifié : `backend/app/services/stripe_webhook_service.py`
- Non modifié : `backend/app/api/v1/routers/billing.py` — `{"status": "duplicate_ignored"}` passe automatiquement
- Nouveaux tests unitaires : `backend/app/tests/unit/test_stripe_webhook_idempotency_service.py`
- Tests d'intégration complétés : `backend/app/tests/integration/test_stripe_webhook_api.py`
- Nouvelle doc : `docs/billing-webhook-idempotency.md`

**Conventions de migration** : utiliser le format daté `20260329_NNNN_add_stripe_webhook_events.py`. Le numéro séquentiel doit suivre le dernier fichier présent dans `backend/migrations/versions/`.

**`db.flush()` vs `db.commit()`** : `begin_event()` appelle `flush()` (pas `commit()`) pour déclencher la contrainte UNIQUE dans la même transaction que le traitement métier. Le `commit()` global est dans le routeur (`db.commit()` ligne ~1211 de `billing.py`).

---

## Dev Agent Record

### Agent Model Used

gemini-2-0-flash-001 (CLI)

### Debug Log References

- [2026-03-29] Début de l'implémentation. Statut passé à in-progress.

### Completion Notes List

- [2026-03-29] Code review réalisée: correction d'un test unitaire encore aligné sur l'ancien comportement non idempotent et ajout d'un test d'intégration couvrant `failed -> retry accepted`.

### File List

- `backend/app/infra/db/models/stripe_webhook_event.py` (nouveau)
- `backend/app/infra/db/models/__init__.py` (modifié)
- `backend/migrations/versions/20260329_0064_add_stripe_webhook_events.py` (nouveau)
- `backend/app/services/stripe_webhook_idempotency_service.py` (nouveau)
- `backend/app/services/stripe_webhook_service.py` (modifié)
- `docs/billing-webhook-idempotency.md` (nouveau)
- `backend/app/tests/unit/test_stripe_webhook_idempotency_service.py` (nouveau)
- `backend/app/tests/integration/test_stripe_webhook_api.py` (modifié)
- `backend/app/tests/unit/test_stripe_webhook_service.py` (modifié)
- `_bmad-output/test-artifacts/review-61-56.md` (nouveau)

### Change Log

- [2026-03-29] Initialisation de la story et mise à jour du statut.
- [2026-03-29] Implémentation complète : modèle, migration, service d'idempotence, intégration et tests.
- [2026-03-29] Correction review : passage aux savepoints (`begin_nested`) pour isoler la logique métier et permettre l'enregistrement du statut `failed` sans rollback global. Fix robustesse types (coercion string) pour les IDs.
- [2026-03-29] Revue corrective: réalignement des tests de service sur le contrat idempotent et ajout de la preuve d'intégration `failed -> processed` au retry.

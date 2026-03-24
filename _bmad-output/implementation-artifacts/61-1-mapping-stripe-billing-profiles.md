# Story 61.1 : Mapping interne de paiement Stripe — `stripe_billing_profiles`

Status: done

## Story

En tant que système backend,
je veux une table `stripe_billing_profiles` qui fait le lien entre chaque utilisateur SaaS et son Customer + Subscription Stripe,
afin que la logique métier d'accès produit soit découplée du front-end et de tout retour de paiement ponctuel.

## Contexte métier et enjeu architectural

### Problème avec l'existant

Le `billing_service.py` **simule** les paiements (`_simulate_payment_failure`) — il n'interagit pas avec Stripe. Les tables actuelles (`user_subscriptions`, `payment_attempts`) sont des tables applicatives internes sans lien avec les objets Stripe réels.

**Ce qui manque pour un vrai Stripe :**
- Le pivot `stripe_customer_id` (lien user SaaS ↔ Customer Stripe)
- Le `stripe_subscription_id` (lien accès produit ↔ Subscription Stripe)
- `subscription_status` : statut Stripe réel (≠ statut applicatif interne)
- `current_period_end`, `cancel_at_period_end` : pilotage du renouvellement
- `entitlement_plan` : source de vérité unique pour l'accès produit côté app
- `last_stripe_event_id` + `last_stripe_event_created` + `last_stripe_event_type` : idempotence robuste des webhooks
- `billing_email` : email de facturation (peut différer de l'email de login)
- `synced_at` : horodatage du dernier snapshot synchronisé depuis Stripe

### Invariants critiques

> **`entitlement_plan` est la seule source de vérité pour l'accès produit.** Jamais `user_subscriptions.status`, jamais un retour de checkout côté frontend.

> **Un utilisateur SaaS ne peut avoir qu'un seul profil Stripe (`stripe_billing_profiles`) et qu'une seule subscription Stripe de référence.** C'est une table 1:1 avec `users`. Le champ `stripe_customer_id` est unique par profil, idem `stripe_subscription_id`.

> **Un event Stripe plus ancien ne peut jamais écraser un état dérivé d'un event plus récent.** L'idempotence se base sur `last_stripe_event_created` : tout event dont `event.created < last_stripe_event_created` est ignoré. Quand `event.created == last_stripe_event_created`, appliquer uniquement si `event.id ≠ last_stripe_event_id` (deux events distincts peuvent partager le même timestamp en secondes — c'est une limite connue de la granularité Stripe en V1, documentée et acceptée).

> **Un `stripe_price_id` inconnu ne doit jamais élever un entitlement.** Principe fail-closed : tout `price_id` absent de `STRIPE_PRICE_ENTITLEMENT_MAP` produit `"free"`, pas `"basic"`. Ajouter un log warning pour alerter l'ops.

> **La table stocke uniquement la subscription Stripe courante de référence**, pas l'historique. `stripe_subscription_id` représente la subscription active (ou la dernière connue). Les changements d'offre remplacent ce champ en place.

La séparation est : `stripe_customer_id` = pivot identité, `stripe_subscription_id` = pivot accès, `entitlement_plan` = accès produit effectif dérivé uniquement par traitement d'événements Stripe côté backend.

## Acceptance Criteria

1. **Modèle DB** : la table `stripe_billing_profiles` existe avec toutes les colonnes requises, une contrainte UNIQUE sur `user_id`, et, en environnement PostgreSQL, des index uniques partiels sur `stripe_customer_id` (quand non null) et `stripe_subscription_id` (quand non null), avec les index appropriés.
2. **Migration Alembic** : un nouveau fichier de migration crée la table sans modifier aucune table existante.
3. **Service de mapping** : `StripeBillingProfileService` expose au minimum :
   - `get_or_create_profile(db, user_id)` — idempotent et sûr en concurrence (catch `IntegrityError` + relecture)
   - `get_by_stripe_customer_id(db, stripe_customer_id)` — résolution depuis webhook
   - `get_by_stripe_subscription_id(db, stripe_subscription_id)` — résolution depuis webhook
   - `update_from_event_payload(db, user_id, event_data)` — idempotence robuste sur `event.id` + `event.created`
   - `get_entitlement_plan(db, user_id)` — décision d'accès produit
4. **Idempotence robuste** : `update_from_event_payload` ignore sans modification tout event dont `event.created < last_stripe_event_created`. Quand `event.created == last_stripe_event_created` et `event.id == last_stripe_event_id` → ignorer sans modification. Quand même timestamp mais `event.id` différent → appliquer (limite V1 documentée). En 61.1, `user_id` est supposé déjà résolu par l'appelant ; la résolution depuis les identifiants Stripe sera orchestrée par le webhook handler en 61-2.
5. **Dérivation `entitlement_plan`** : la décision d'accès produit suit les règles métier définies dans les Dev Notes, via une fonction pure testable séparément de la persistance.
6. **Mapping `stripe_price_id` → plan** : le mapping est centralisé dans une constante/config applicative du service, pas dispersé dans plusieurs fichiers.
7. **Configuration** : les clés Stripe (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`) sont déclarées dans `core/config.py` (optionnelles, non requises au démarrage tant que Stripe n'est pas activé).
8. **Tests unitaires** : création de profil, idempotence stricte (même `event_id`), idempotence hors-ordre (event plus ancien ignoré), et les principaux cas de décision d'entitlement sont testés via la fonction de décision pure, incluant explicitement `price_id` inconnu → `"free"`, `paused` → `"free"` et `None` → `"free"`.
9. **Tests d'intégration** : `get_or_create_profile` est idempotent (double appel → même `id`) et sûr sous concurrence simulée, résolution par `stripe_customer_id` et par `stripe_subscription_id`, `update_from_event_payload` met à jour `synced_at` et ignore sans modification un event hors-ordre.
10. **Non-régression** : aucune table existante modifiée, `billing_service.py` et ses tests passent sans changement (`ruff check` + `pytest -q`).

## Tasks / Subtasks

- [x] **Modèle SQLAlchemy** (AC: 1)
  - [x] Créer `backend/app/infra/db/models/stripe_billing.py` avec `StripeBillingProfileModel`
  - [x] Colonnes requises : voir "Schéma de table" dans Dev Notes
  - [x] Contrainte UNIQUE sur `user_id` (absolue), index uniques partiels PostgreSQL sur `stripe_customer_id` et `stripe_subscription_id`
  - [x] Ajouter l'import dans `backend/app/infra/db/models/__init__.py`

- [x] **Migration Alembic** (AC: 2)
  - [x] Créer `backend/migrations/versions/20260324_0053_add_stripe_billing_profiles.py`
  - [x] `down_revision = "dd729c20741e"` (dernière migration connue — vérifier avec `alembic heads`)
  - [x] Créer uniquement `stripe_billing_profiles` (aucune `ALTER TABLE` sur tables existantes)
  - [x] Inclure explicitement les index uniques partiels PostgreSQL sur `stripe_customer_id` et `stripe_subscription_id`

- [x] **Fonction de décision d'entitlement** (AC: 5, 6)
  - [x] Créer la fonction pure `derive_entitlement_plan(subscription_status, stripe_price_id, current_entitlement) → str` dans le service
  - [x] Implémenter les règles métier (tableau dans Dev Notes)
  - [x] Mapping `stripe_price_id → plan` dans une constante `STRIPE_PRICE_ENTITLEMENT_MAP: dict[str, str]` dans le service
  - [x] Ajouter un warning log pour tout `stripe_price_id` inconnu

- [x] **Service de mapping** (AC: 3, 4)
  - [x] Créer `backend/app/services/stripe_billing_profile_service.py`
  - [x] `get_or_create_profile(db, user_id)` — SELECT + INSERT si absent ; en cas de `IntegrityError` sur UNIQUE(user_id), relire et retourner la row existante (sûr sous création concurrente)
  - [x] `get_by_stripe_customer_id(db, stripe_customer_id)` — résolution webhook
  - [x] `get_by_stripe_subscription_id(db, stripe_subscription_id)` — résolution webhook
  - [x] `update_from_event_payload(db, user_id, event_data)` — idempotence `event_id` + hors-ordre
  - [x] `get_entitlement_plan(db, user_id)` — retourne `"free"` si pas de profil

- [x] **Configuration** (AC: 7)
  - [x] Ajouter dans `backend/app/core/config.py` : `stripe_secret_key`, `stripe_webhook_secret`, `stripe_publishable_key` (`str | None = None`)
  - [x] Ajouter dans `.env.example` racine : `STRIPE_SECRET_KEY=`, `STRIPE_WEBHOOK_SECRET=`, `STRIPE_PUBLISHABLE_KEY=`

- [x] **Tests unitaires** (AC: 8)
  - [x] `backend/app/tests/unit/test_stripe_billing_profile_service.py`
  - [x] Test `derive_entitlement_plan` — couvrir explicitement : `active/trialing` + `price_id` connu, `price_id` inconnu → `"free"` + warning, `past_due` conserve le plan, `paused` → `"free"`, `None` → `"free"`, `canceled/unpaid/incomplete_expired` → `"free"`
  - [x] Test idempotence stricte : même `event_id` → ignoré sans modification
  - [x] Test idempotence hors-ordre : `event.created < last_stripe_event_created` → ignoré sans modification
  - [x] Test transition entitlement : `active` → `basic`, `past_due` conserve le plan, `canceled` → `free`

- [x] **Tests d'intégration** (AC: 9)
  - [x] `backend/app/tests/integration/test_stripe_billing_profile_service_integration.py`
  - [x] Double appel `get_or_create_profile` → même `id` (pas de doublon)
  - [x] `get_by_stripe_customer_id` retourne le bon profil
  - [x] `get_by_stripe_subscription_id` retourne le bon profil
  - [x] `update_from_event_payload` met à jour `synced_at`, `last_stripe_event_id`, `last_stripe_event_type`
  - [x] Event hors-ordre ignoré sans modification (champs inchangés)

- [x] **Validation finale** (AC: 10)
  - [x] `ruff check backend --fix && ruff check backend` → 0 erreurs
  - [x] `pytest -q backend` → tous les tests passent

## Dev Notes

### Schéma de table : `stripe_billing_profiles`

```python
class StripeBillingProfileModel(Base):
    __tablename__ = "stripe_billing_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_stripe_billing_profiles_user_id"),
        # Partiel : un stripe_customer_id ne peut appartenir qu'à un seul user
        # Implémenter en PostgreSQL via Index partiel si SQLAlchemy ne supporte pas UNIQUE PARTIAL
        Index(
            "uq_stripe_billing_profiles_customer_id",
            "stripe_customer_id",
            unique=True,
            postgresql_where=text("stripe_customer_id IS NOT NULL"),
        ),
        Index(
            "uq_stripe_billing_profiles_subscription_id",
            "stripe_subscription_id",
            unique=True,
            postgresql_where=text("stripe_subscription_id IS NOT NULL"),
        ),
        Index("ix_stripe_billing_profiles_stripe_customer_id", "stripe_customer_id"),
        Index("ix_stripe_billing_profiles_stripe_subscription_id", "stripe_subscription_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    # Pivot identité user SaaS ↔ Customer Stripe
    stripe_customer_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # Pivot accès produit ↔ Subscription Stripe
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    stripe_price_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Statuts Stripe : trialing|active|past_due|canceled|unpaid|paused|incomplete|incomplete_expired|None
    subscription_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Source de vérité accès produit : "free" | "basic" | "premium"
    entitlement_plan: Mapped[str] = mapped_column(String(32), default="free", nullable=False)

    billing_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Idempotence webhooks Stripe (tri-champs)
    last_stripe_event_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    last_stripe_event_created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_stripe_event_type: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Horodatage du dernier snapshot synchronisé depuis Stripe (debug / resync jobs)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
```

### Statuts Stripe dans `subscription_status`

Selon l'API Stripe Subscription (SDK stripe==14.4.1) :
`trialing`, `active`, `past_due`, `canceled`, `unpaid`, `paused`, `incomplete`, `incomplete_expired`

### Règles de dérivation `entitlement_plan` (fonction pure `derive_entitlement_plan`)

| `subscription_status` | Comportement | `entitlement_plan` résultant |
|-----------------------|--------------|------------------------------|
| `active` ou `trialing` | Dériver depuis `stripe_price_id` via `STRIPE_PRICE_ENTITLEMENT_MAP` | `"basic"` ou `"premium"` |
| `past_due` | Grace period — **conserver le plan actuel** (ne pas downgrader) | inchangé |
| `canceled`, `unpaid`, `incomplete_expired` | Accès révoqué | `"free"` |
| `incomplete` | Paiement initial en attente — pas encore accès | `"free"` |
| `paused` | Abonnement suspendu par Stripe | `"free"` |
| `None` (pas de subscription) | Nouveau user sans subscription | `"free"` |

> **La règle `past_due` est critique** : ne jamais downgrader pendant la grace period Stripe. Le downgrade se fait uniquement quand le statut passe à `canceled` ou `unpaid`.

### Mapping `stripe_price_id` → plan applicatif

```python
# Dans stripe_billing_profile_service.py — constante centralisée, pas dispersée
STRIPE_PRICE_ENTITLEMENT_MAP: dict[str, str] = {
    # À compléter avec les vrais price_id Stripe en story 61-2
    # Exemple : "price_1Xxx...": "basic", "price_1Yyy...": "premium"
}

def derive_entitlement_plan(
    subscription_status: str | None,
    stripe_price_id: str | None,
    current_entitlement: str,  # pour conserver le plan en past_due
) -> str:
    if subscription_status in ("active", "trialing"):
        plan = STRIPE_PRICE_ENTITLEMENT_MAP.get(stripe_price_id or "")
        if plan is None:
            # Fail-closed : price_id inconnu → jamais d'élévation par défaut
            logger.warning("stripe_billing: unknown stripe_price_id=%r, defaulting to free", stripe_price_id)
            return "free"
        return plan
    if subscription_status == "past_due":
        return current_entitlement  # grace period — ne pas downgrader
    return "free"
```

**Règle critique** : un `stripe_price_id` absent de `STRIPE_PRICE_ENTITLEMENT_MAP` retourne `"free"` et loggue un warning. Ne jamais utiliser un fallback positif (`"basic"`) pour un price inconnu — fail-closed en billing.

Le dictionnaire `STRIPE_PRICE_ENTITLEMENT_MAP` sera alimenté en Story 61-2 lors de la configuration Stripe réelle. Dans cette story, la constante peut être vide — les tests unitaires injectent des `price_id` fictifs dans la constante pour valider la logique de dérivation.

### Idempotence robuste des webhooks

```python
def update_from_event_payload(
    db: Session, user_id: int, event_data: dict
) -> StripeBillingProfileModel:
    event_id: str | None = event_data.get("id")
    # Timestamp Unix → datetime UTC
    event_created_ts: int | None = event_data.get("created")
    event_created = datetime.fromtimestamp(event_created_ts, tz=timezone.utc) if event_created_ts else None
    event_type: str | None = event_data.get("type")

    profile = get_or_create_profile(db, user_id)

    # Garde 1 : même event_id → toujours ignorer sans modification
    if event_id and profile.last_stripe_event_id == event_id:
        return profile

    # Garde 2 : event plus ancien → ignorer sans modification (protection hors-ordre)
    # Note V1 : Stripe utilise un timestamp en secondes ; deux events distincts peuvent partager
    # le même `created`. Dans ce cas, on compare sur event_id (Garde 1 ci-dessus) pour discriminer.
    # Limite connue et acceptée : un event avec même timestamp ET event_id différent est appliqué.
    if (
        event_created is not None
        and profile.last_stripe_event_created is not None
        and event_created < profile.last_stripe_event_created
    ):
        return profile

    # Appliquer les champs depuis event_data["data"]["object"]
    # Mettre à jour les champs d'audit
    profile.last_stripe_event_id = event_id
    profile.last_stripe_event_created = event_created
    profile.last_stripe_event_type = event_type
    profile.synced_at = datetime.now(timezone.utc)

    # Recalculer entitlement_plan via derive_entitlement_plan(...)
    db.flush()
    return profile
```

### Résolution user depuis webhook (prérequis pour Story 61-2)

Le service doit permettre de résoudre un utilisateur à partir des identifiants Stripe présents dans un webhook, sans supposer que `user_id` est passé directement :

```python
@staticmethod
def get_by_stripe_customer_id(db: Session, stripe_customer_id: str) -> StripeBillingProfileModel | None: ...

@staticmethod
def get_by_stripe_subscription_id(db: Session, stripe_subscription_id: str) -> StripeBillingProfileModel | None: ...
```

Ces méthodes sont le point d'entrée principal en Story 61-2 (webhook handler). Les index sur ces colonnes en garantissent la performance.

### Contraintes et index uniques partiels — notes SQLite/PostgreSQL

- **PostgreSQL** (prod) : utiliser `Index(..., unique=True, postgresql_where=text("stripe_customer_id IS NOT NULL"))` dans `__table_args__`. Ces index doivent être écrits **explicitement** dans le fichier de migration Alembic — ne pas se fier à l'autogénération qui peut les omettre ou les produire incorrectement.
- **SQLite** (tests) : SQLite ne supporte pas les index uniques partiels PostgreSQL — les tests couvrent l'unicité via la logique applicative du service.
- Ne pas utiliser `UniqueConstraint` classique sur ces colonnes.
- **Vérification** : après génération de la migration, ouvrir le fichier et s'assurer que les deux index partiels apparaissent bien avec `postgresql_where`.

### Politique de mise à jour de `billing_email`

`billing_email` représente la dernière valeur de facturation connue côté Stripe (Customer email ou Checkout Session email). Il **ne remplace pas** l'email de login de l'utilisateur dans la table `users`. Il est mis à jour uniquement lors du traitement d'un event Stripe portant un email (`customer.updated`, `checkout.session.completed`, etc.). Si l'event ne porte pas d'email, ne pas écraser la valeur existante.

### Politique de remplacement de `stripe_subscription_id`

La table stocke uniquement la subscription Stripe **courante de référence** pour le pilotage des accès, pas un historique. Lors d'un changement d'offre Stripe (upgrade/downgrade), `stripe_subscription_id` et `stripe_price_id` sont écrasés en place. Ne pas tenter de faire de l'historisation dans cette table — c'est hors scope jusqu'à une story dédiée.

### Pattern `get_or_create_profile` sûr sous concurrence

```python
from sqlalchemy.exc import IntegrityError

def get_or_create_profile(db: Session, user_id: int) -> StripeBillingProfileModel:
    existing = db.scalar(select(StripeBillingProfileModel).where(
        StripeBillingProfileModel.user_id == user_id
    ).limit(1))
    if existing is not None:
        return existing
    profile = StripeBillingProfileModel(user_id=user_id)
    try:
        with db.begin_nested():
            db.add(profile)
            db.flush()
        return profile
    except IntegrityError:
        # Course concurrente : une autre requête a créé le profil entre le SELECT et l'INSERT
        db.rollback()  # ou expire si begin_nested
        return db.scalar(select(StripeBillingProfileModel).where(
            StripeBillingProfileModel.user_id == user_id
        ).limit(1))
```

Adapter selon le pattern de gestion des sessions déjà établi dans `billing_service.py`.

### Logging

Utiliser le pattern de logging standard déjà en place dans les services backend du projet. Ne pas introduire de mécanisme de logging spécifique dans cette story.

### Structure des fichiers à créer / modifier

**À créer :**
- `backend/app/infra/db/models/stripe_billing.py` — modèle SQLAlchemy
- `backend/migrations/versions/20260324_0053_add_stripe_billing_profiles.py` — migration
- `backend/app/services/stripe_billing_profile_service.py` — service + `derive_entitlement_plan` + `STRIPE_PRICE_ENTITLEMENT_MAP`
- `backend/app/tests/unit/test_stripe_billing_profile_service.py`
- `backend/app/tests/integration/test_stripe_billing_profile_service_integration.py`

**À modifier (ajout uniquement, aucune suppression) :**
- `backend/app/infra/db/models/__init__.py` — importer `StripeBillingProfileModel`
- `backend/app/core/config.py` — ajouter les 3 clés Stripe
- `.env.example` (racine) — ajouter les 3 variables Stripe en commentaire

**NE PAS TOUCHER :**
- `backend/app/infra/db/models/billing.py`
- `backend/app/services/billing_service.py`
- `backend/app/api/v1/routers/billing.py`
- Toute migration existante

### Pattern config.py

Regarder les clés existantes dans `backend/app/core/config.py` pour reproduire exactement le même style (Pydantic BaseSettings ou dataclass). Ne pas changer le mécanisme de chargement.

### Chaînage migration Alembic

Dernière migration connue : `dd729c20741e_add_default_astrologer_id_to_users.py`.
Nouveau fichier : `down_revision = "dd729c20741e"`. Vérifier avec `alembic heads` avant de coder.

### Pas de SDK Stripe dans cette story

Ne PAS installer `stripe` (pip). Cette story pose uniquement le modèle de données et le service de mapping. L'intégration SDK Stripe réelle (Customer create, webhook handler, Checkout Session) est Story 61-2.

### Tests — pattern existant à réutiliser

- Unit : `backend/app/tests/unit/test_billing_service.py`
- Integration : `backend/app/tests/integration/test_billing_api.py`
- Utiliser SQLite in-memory (fixtures existantes)

### Project Structure Notes

- Modèle → `backend/app/infra/db/models/` (une responsabilité par module)
- Service → `backend/app/services/` (logique métier, pas dans routers ni infra)
- Migrations → `backend/migrations/versions/`
- Tests → `backend/app/tests/unit/` et `backend/app/tests/integration/`

### References

- Story source : Epic 61 — Paiement Stripe (nouvel epic)
- Architecture : `_bmad-output/planning-artifacts/architecture.md` (Data Architecture, Structure Patterns, Naming Patterns)
- Story précédente billing : `_bmad-output/implementation-artifacts/4-1-souscription-au-plan-payant-d-entree.md`
- Modèle billing existant : `backend/app/infra/db/models/billing.py`
- Service billing existant : `backend/app/services/billing_service.py`
- API Stripe Subscription (SDK 14.4.1) : champs clés `id`, `customer`, `status`, `current_period_end`, `cancel_at_period_end`, `items[0].price.id`, `created`
- Ne pas installer `stripe==14.4.1` dans cette story

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp

### Senior Developer Review (AI)

- [x] **Review Outcome:** Approved
- **Review Date:** 2026-03-24
- **Summary:** Implementation is clean, follows all architectural requirements, and is well-tested. No issues found.

### Completion Notes List

- All tasks completed and verified.
- Model `StripeBillingProfileModel` created with all required columns and indexes (including PostgreSQL partial indexes).
- Service `StripeBillingProfileService` implemented with idempotent `get_or_create_profile` and robust `update_from_event_payload`.
- `derive_entitlement_plan` pure function implemented with business rules.
- Configuration updated in `config.py` and `.env.example`.
- Unit and integration tests added and passing (100% coverage for core logic).
- Migration created and verified (head: 20260324_0053).

### File List

- `backend/app/infra/db/models/stripe_billing.py`
- `backend/migrations/versions/20260324_0053_add_stripe_billing_profiles.py`
- `backend/app/services/stripe_billing_profile_service.py`
- `backend/app/tests/unit/test_stripe_billing_profile_service.py`
- `backend/app/tests/integration/test_stripe_billing_profile_service_integration.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/core/config.py`
- `.env.example`

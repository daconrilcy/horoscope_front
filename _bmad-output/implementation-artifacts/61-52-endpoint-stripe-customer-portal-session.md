# Story 61.52 : Endpoint backend — Stripe Customer Portal Session

Status: done

## Story

En tant qu'utilisateur authentifié,
je veux pouvoir ouvrir un portail client Stripe sécurisé depuis l'application lorsque mon compte est rattaché à un customer Stripe,
afin de gérer moi-même mon abonnement (upgrade, downgrade, cancel, moyens de paiement, factures)
sans que l'application ne recode toute la logique de gestion d'abonnement dans son propre backend.

---

## Contexte

La story 61.51 a formellement clôturé le sous-chantier entitlements canoniques 61.7 à 61.50. Le système produit dispose d'un runtime unifié, d'un contrat frontend stable, et d'un webhook billing déjà en place pour réconcilier l'état Stripe vers le backend.

Cette story ouvre le self-service billing sans recoupler le produit à une logique d'édition d'abonnement codée localement. Elle **ne rouvre pas** le chantier 61.7–61.50 : elle s'appuie sur `stripe_billing_profiles` comme pivot de réconciliation `user ↔ Stripe Customer`.

**Principe fondamental (identique à 61.4)** : le navigateur n'est pas une source de vérité. Les changements d'abonnement effectués dans le portail Stripe restent réconciliés via les événements Stripe déjà gérés par le socle webhook existant.

---

## Acceptance Criteria

**AC1 — Endpoint de création de session portail**
`POST /v1/billing/stripe-customer-portal-session` — authentifié JWT obligatoire.

- [x] Identifie l'utilisateur courant via `Depends(require_authenticated_user)`
- [x] Charge son `StripeBillingProfile` via `StripeBillingProfileService`
- [x] Vérifie la présence d'un `stripe_customer_id`
- [x] Crée une session Stripe Customer Portal
- [x] Retourne `200 OK` avec `{"data": {"url": "https://billing.stripe.com/..."}, "meta": {"request_id": "..."}}`
- [x] Ne redirige **pas** par HTTP 302 : renvoie l'URL au frontend

**AC2 — Cas non éligibles**
Si aucun `StripeBillingProfile` exploitable n'existe pour l'utilisateur courant, ou si le profil existe mais ne porte pas de `stripe_customer_id` :
- [x] Retourner `404 Not Found` avec code d'erreur `stripe_billing_profile_not_found`
- [x] Ne pas appeler l'API Stripe
- [x] Message permettant au frontend de comprendre que l'utilisateur n'a pas encore de profil Stripe gérable en self-service

**Note de cadrage MVP** : dans cette story, l'absence de profil et l'absence de `stripe_customer_id` sont volontairement regroupées sous le même code d'erreur métier.

**AC3 — Source de vérité conservée côté webhook**
Cet endpoint ne mute **rien** :
- [x] Aucune modification de `plan_code`, `billing_status`, bindings canoniques ou entitlements
- [x] Aucun recalcul d'accès produit depuis cet endpoint
- [x] Les changements d'abonnement restent réconciliés via le pipeline webhook existant

**AC4 — `return_url` configurable**
La portal session est créée avec une `return_url` :
- [x] Injectée depuis `settings.stripe_portal_return_url`
- [x] Variable `STRIPE_PORTAL_RETURN_URL` ajoutée dans `config.py` avec valeur par défaut `http://localhost:5173/settings/subscription`
- [x] Jamais codée en dur dans le service métier

**AC5 — Surface MVP strictement limitée**
Cette story n'ajoute **pas** d'endpoint `change-plan`, `cancel-subscription` ni `resume-subscription`.

**AC6 — Documentation MVP**
Section ajoutée dans la doc billing/Stripe existante (ou dans un fichier dédié) explicitant :
- [x] Le choix du Customer Portal pour l'upgrade/downgrade/cancel self-service
- [x] Les limites du MVP (pas de commandes maison)
- [x] La source de vérité webhook pour les changements effectifs

**AC7 — Tests**
- [x] Succès : utilisateur avec `stripe_customer_id` valide → session créée, URL retournée
- [x] Utilisateur sans profil Stripe exploitable → 404 `stripe_billing_profile_not_found`
- [x] Erreur Stripe API → 502 `stripe_api_error`
- [x] Aucun champ du `StripeBillingProfile` n'est modifié par l'appel
- [x] Aucun recalcul synchrone des entitlements n'est déclenché par cet endpoint

---

## Tasks / Subtasks

- [x] **Ajouter `STRIPE_PORTAL_RETURN_URL` dans `config.py`** (AC: 4)
  - [x] `self.stripe_portal_return_url = os.getenv("STRIPE_PORTAL_RETURN_URL", "http://localhost:5173/settings/subscription").strip()`
  - [x] Documenter dans `.env.example` en précisant que la valeur par défaut est **uniquement acceptable en local** — en environnement déployé, `STRIPE_PORTAL_RETURN_URL` doit être explicitement configurée

- [x] **Créer `StripeCustomerPortalService`** dans `backend/app/services/stripe_customer_portal_service.py` (AC: 1, 2, 4)
  - [x] Classe `StripeCustomerPortalServiceError(Exception)` avec `code`, `message`, `details`
  - [x] Méthode statique `create_portal_session(db, *, user_id, return_url) -> str`
  - [x] Charger le profil Stripe existant de l'utilisateur **en lecture seule** via `StripeBillingProfileService` (sans création implicite — voir invariant dans Dev Notes)
  - [x] Si le profil est absent ou sans `stripe_customer_id`, lever `StripeCustomerPortalServiceError(code="stripe_billing_profile_not_found", ...)`
  - [x] Appeler l'API Stripe Customer Portal via `get_stripe_client()` selon le pattern SDK déjà utilisé dans le projet
  - [x] Retourner l'URL de session Stripe
  - [x] Capturer `stripe.StripeError` → lever `StripeCustomerPortalServiceError(code="stripe_api_error", ...)`
  - [x] Capturer `client is None` → lever `StripeCustomerPortalServiceError(code="stripe_unavailable", ...)`

- [x] **Ajouter l'endpoint dans `backend/app/api/v1/routers/billing.py`** (AC: 1, 2, 7)
  - [x] Ajouter les Pydantic models : `StripePortalResponse`, `StripePortalApiResponse`
  - [x] Déclarer `@router.post("/stripe-customer-portal-session", response_model=StripePortalApiResponse, ...)`
  - [x] Authentification : `Depends(require_authenticated_user)`
  - [x] Appeler `StripeCustomerPortalService.create_portal_session(db, user_id=..., return_url=settings.stripe_portal_return_url)`
  - [x] Audit via `_record_audit_event` (succès et erreur)
  - [x] Retourner `{"data": {"url": url}, "meta": {"request_id": request_id}}`
  - [x] Gérer `stripe_billing_profile_not_found` → 404
  - [x] Gérer `stripe_unavailable` → 503
  - [x] Gérer `stripe_api_error` → 502

- [x] **Créer les tests unitaires** `backend/app/tests/unit/test_stripe_customer_portal_service.py` (AC: 7)
  - [x] Succès : mock `get_stripe_client` + `billing_portal.sessions.create` → retourne `url`
  - [x] Profil sans `stripe_customer_id` → `StripeCustomerPortalServiceError(code="stripe_billing_profile_not_found")`
  - [x] `stripe.StripeError` → `StripeCustomerPortalServiceError(code="stripe_api_error")`
  - [x] `get_stripe_client()` retourne `None` → `StripeCustomerPortalServiceError(code="stripe_unavailable")`

- [x] **Créer les tests d'intégration** `backend/app/tests/integration/test_stripe_customer_portal_api.py` (AC: 7)
  - [x] `POST /v1/billing/stripe-customer-portal-session` avec `stripe_customer_id` valide → 200 + `url`
  - [x] Utilisateur sans `stripe_customer_id` → 404
  - [x] Erreur Stripe mockée → 502
  - [x] Pas de JWT → 401
  - [x] Vérifier absence de mutation sur le billing profile et les entitlements

- [x] **Documenter le MVP** (AC: 6)
  - [x] Ajouter une section dans `docs/` (ex. `docs/billing-self-service-mvp.md`) ou dans la doc billing existante

---

## Dev Notes

### Position dans l'Epic 61

```text
61-1 (done) : stripe_billing_profiles + StripeBillingProfileService
61-2 (done) : SDK stripe==14.4.1 + get_stripe_client() + secrets
61-3 (done) : POST /v1/billing/stripe-checkout-session
61-4 (done) : POST /v1/billing/stripe-webhook + vérification signature
61-5/61-6 (done) : sélection événements webhook + invoice events
61-7 à 61-50 (done) : chantier entitlements canoniques
61-51 (done) : clôture formelle du sous-chantier
61-52 (cette story) : POST /v1/billing/stripe-customer-portal-session
```

Le principe d'architecture reste inchangé :
- Stripe Billing = source de vérité du billing
- Backend réconcilie via webhooks
- Moteur canonique calcule les droits produit effectifs
- Frontend consomme le snapshot
- Portail Stripe = UI de self-service pour modifier l'abonnement

### Fichiers à modifier / créer

| Fichier | Action |
|---|---|
| `backend/app/core/config.py` | Ajouter `stripe_portal_return_url` |
| `.env.example` | Documenter `STRIPE_PORTAL_RETURN_URL` |
| `backend/app/services/stripe_customer_portal_service.py` | **Créer** |
| `backend/app/api/v1/routers/billing.py` | **Étendre** (ne pas créer un nouveau router) |
| `backend/app/services/stripe_billing_profile_service.py` | **Étendre** (ajout `get_by_user_id`) |
| `backend/app/tests/unit/test_stripe_customer_portal_service.py` | **Créer** |
| `backend/app/tests/integration/test_stripe_customer_portal_api.py` | **Créer** |
| `docs/billing-self-service-mvp.md` | **Créer** |

### Pattern de service à reproduire fidèlement

S'appuyer sur `StripeCheckoutService` comme modèle direct ([Source: `backend/app/services/stripe_checkout_service.py`]) :

```python
class StripeCustomerPortalServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

class StripeCustomerPortalService:
    @staticmethod
    def create_portal_session(
        db: Session,
        *,
        user_id: int,
        return_url: str,
    ) -> str:
        client = get_stripe_client()
        if client is None:
            raise StripeCustomerPortalServiceError(
                code="stripe_unavailable",
                message="Stripe client is not configured",
            )
        # Lecture seule — NE PAS utiliser get_or_create_profile ici
        profile = StripeBillingProfileService.get_by_user_id(db, user_id)  # ou équivalent read-only
        if profile is None or not profile.stripe_customer_id:
            raise StripeCustomerPortalServiceError(
                code="stripe_billing_profile_not_found",
                message="No Stripe customer ID found for this user",
            )
        try:
            # Reproduire le pattern SDK exact déjà utilisé dans StripeCheckoutService
            session = client.billing_portal.sessions.create(
                params={"customer": profile.stripe_customer_id, "return_url": return_url}
            )
            return session.url
        except stripe.StripeError as error:
            logger.exception("Stripe API error during portal session creation")
            raise StripeCustomerPortalServiceError(
                code="stripe_api_error",
                message="Stripe API error",
                details={"error_message": str(error)},
            ) from error
```

### Pattern de réponse API (à reproduire fidèlement)

```python
class StripePortalResponse(BaseModel):
    url: str

class StripePortalApiResponse(BaseModel):
    data: StripePortalResponse
    meta: dict  # ou MetaResponse si ce type existe déjà dans le router

# Réponse nominale :
return {
    "data": {"url": portal_url},
    "meta": {"request_id": request_id},
}
```

Vérifier si `MetaResponse` ou une classe équivalente est déjà définie dans `billing.py` avant d'en créer une nouvelle.

### Appel Stripe Customer Portal — SDK 14.4.1

L'API Stripe Customer Portal est documentée dans le module `billing_portal.sessions` :

```python
session = client.billing_portal.sessions.create(
    params={
        "customer": stripe_customer_id,   # OBLIGATOIRE
        "return_url": return_url,          # OPTIONNEL mais recommandé
    }
)
# session.url → URL à renvoyer au frontend
```

**Attention** : le Customer Portal doit être configuré dans le Dashboard Stripe avant de fonctionner (features activées, produits autorisés). Le backend ne peut pas configurer le portail via l'API — c'est une configuration Dashboard uniquement.

### Gestion des erreurs dans le router

Modèle à suivre (identique à `create_stripe_checkout_session`) :

```python
except StripeCustomerPortalServiceError as error:
    if error.code == "stripe_billing_profile_not_found":
        # 404
    elif error.code == "stripe_unavailable":
        # 503
    elif error.code == "stripe_api_error":
        # 502
    else:
        # 500 fallback
```

### Audit

Chaque appel (succès ou échec) doit être audité via `_record_audit_event` :
- `action="stripe_portal_session_created"` ou `"stripe_portal_session_failed"`
- `target_type="user"`, `target_id=str(current_user.id)`
- `status="success"` / `"failed"`

### Sécurité

- **Ne jamais accepter un `stripe_customer_id` fourni par le frontend** : toujours résoudre depuis `stripe_billing_profiles` via `user_id` extrait du JWT
- **Ne pas considérer le retour navigateur comme preuve de changement** : aucun polling, aucun recalcul synchrone des entitlements au retour du portail

### Hors périmètre explicite

- Implémentation de `change-plan`, `cancel-subscription`, `resume-subscription` applicatif
- Prévisualisation maison des proratas
- Synchronisation synchrone des entitlements au retour du portail
- Refonte frontend complète de la page billing
- Deep links de portail spécialisés (`subscription_update`, etc.) — MVP uniquement

### Invariant important sur `StripeBillingProfileService`

Cette story **ne doit pas créer implicitement** de `StripeBillingProfile`.

`get_or_create_profile` est réservé aux flux d'initialisation (checkout, onboarding). Ici, l'absence de profil exploitable est un cas métier normal de non-éligibilité au self-service — elle doit lever `stripe_billing_profile_not_found`, pas silencieusement créer un profil vide.

Utiliser la méthode de lecture seule exposée par `StripeBillingProfileService` (ex. `get_by_user_id`, ou équivalent à vérifier dans le service existant). Si aucune méthode de lecture seule n'existe, en créer une plutôt que de détourner `get_or_create_profile`.

### Dépendances vérifiées

- `stripe_billing_profiles` : table existante — [Source: `backend/app/infra/db/models/stripe_billing.py`]
- `StripeBillingProfileService` : service existant — [Source: `backend/app/services/stripe_billing_profile_service.py`]
- `get_stripe_client()` : intégration existante — [Source: `backend/app/integrations/stripe_client.py`]
- `_record_audit_event`, `_enforce_billing_limits`, `_error_response` : helpers existants dans `billing.py`
- `require_authenticated_user`, `get_db_session` : dépendances FastAPI existantes

### Structure des tests à respecter

Modèle : `backend/app/tests/unit/test_stripe_checkout_service.py` et `backend/app/tests/integration/test_stripe_checkout_api.py`.

Les tests d'intégration doivent utiliser les fixtures DB et l'injection de dépendances FastAPI établies dans le projet (vérifier `conftest.py`). Les mocks Stripe se font via `unittest.mock.patch` sur `app.integrations.stripe_client.get_stripe_client`.

### Project Structure Notes

- Tous les services Stripe sont dans `backend/app/services/stripe_*.py`
- Tous les endpoints billing sont dans `backend/app/api/v1/routers/billing.py` (préfixe `/v1/billing`)
- Config Stripe dans `backend/app/core/config.py` section "Stripe Configuration" (ligne ~314)
- Tests unitaires : `backend/app/tests/unit/`
- Tests d'intégration : `backend/app/tests/integration/`
- Aucun style inline frontend : CSS dans fichier `.css` dédié avec variables `var(--*)`
- i18n textes frontend : `frontend/src/i18n/billing.ts` (fichier existant)

### References

- [Source: `backend/app/services/stripe_checkout_service.py`] — modèle direct du service
- [Source: `backend/app/api/v1/routers/billing.py#L791-L890`] — modèle direct de l'endpoint
- [Source: `backend/app/core/config.py#L314-L328`] — bloc config Stripe existant
- [Source: `_bmad-output/implementation-artifacts/61-3-create-subscription-checkout-session.md`] — story de référence
- [Source: `_bmad-output/implementation-artifacts/61-4-webhook-stripe-et-retour-navigateur.md`] — principe webhook source de vérité
- [Source: `_bmad-output/implementation-artifacts/61-1-mapping-stripe-billing-profiles.md`] — invariants `stripe_billing_profiles`

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Fixed 503 error in integration tests by mocking `get_stripe_client` in `test_portal_session_profile_not_found` and `test_portal_session_no_customer_id`. The 503 was caused by the endpoint correctly identifying that Stripe was not configured (due to missing environment variables in the test environment) before checking the profile existence.

### Completion Notes List

- Added `stripe_portal_return_url` to `config.py` and `.env.example`.
- Added `get_by_user_id` to `StripeBillingProfileService` for read-only access.
- Created `StripeCustomerPortalService`.
- Added `POST /v1/billing/stripe-customer-portal-session` to `billing.py`.
- Created unit and integration tests with full coverage.
- Created documentation in `docs/billing-self-service-mvp.md`.

### File List

- `backend/app/core/config.py` (modified)
- `.env.example` (modified)
- `backend/app/services/stripe_billing_profile_service.py` (modified)
- `backend/app/api/v1/routers/billing.py` (modified)
- `backend/app/services/stripe_customer_portal_service.py` (new)
- `backend/app/tests/unit/test_stripe_customer_portal_service.py` (new)
- `backend/app/tests/integration/test_stripe_customer_portal_api.py` (new)
- `docs/billing-self-service-mvp.md` (new)

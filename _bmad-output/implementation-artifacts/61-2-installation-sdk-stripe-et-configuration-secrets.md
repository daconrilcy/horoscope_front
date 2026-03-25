# Story 61.2 : Installation du SDK Stripe et configuration des secrets avec `StripeClient`

Status: done

## Story

En tant que développeur backend,
je veux installer la librairie `stripe` Python, déclarer les variables Stripe dans `backend/.env` (non versionné), les charger dans `config.py`, et initialiser un client Stripe dédié via `stripe.StripeClient` avec la clé secrète et la version d'API épinglée, en alimentant `STRIPE_PRICE_ENTITLEMENT_MAP` depuis la configuration,
afin que l'ensemble du backend soit prêt pour l'intégration du Checkout Session et du webhook handler (stories 61-3+).

## Acceptance Criteria

1. **Dépendance installée** : `stripe==14.4.1` est présent dans `[project].dependencies` de `backend/pyproject.toml`. `import stripe` ne lève pas d'erreur après `pip install -e .`.

2. **Secrets dans `backend/.env`** : le fichier `backend/.env` est local, non versionné, gitignoré, et contient en environnement de développement les variables non vides suivantes : `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_PRICE_BASIC`, `STRIPE_PRICE_PREMIUM`. Les valeurs réelles ne doivent jamais être commitées.

3. **Version d'API épinglée** : `STRIPE_API_VERSION=2024-12-18.acacia` est présente dans `backend/.env`. L'épinglage évite une dérive implicite liée à la version par défaut du compte ou du SDK.

4. **`config.py` étendu** : `Settings.__init__` charge `stripe_price_basic`, `stripe_price_premium` et `stripe_api_version` via `os.getenv`, selon le pattern existant du projet (`os.getenv(...).strip() or None` pour les optionnels, valeur par défaut `2024-12-18.acacia` pour `stripe_api_version`).

5. **Client Stripe dédié** : un module `backend/app/integrations/stripe_client.py` expose une factory `get_stripe_client() -> stripe.StripeClient | None` qui instancie `stripe.StripeClient(settings.stripe_secret_key)` quand la clé est disponible, et retourne `None` sinon. Le module charge sans erreur si `stripe_secret_key` est absent (CI / tests unitaires). La manière exacte d'épingler la version d'API au niveau du client ou des requêtes doit être confirmée contre le source du SDK installé (cf. Dev Notes).

6. **`STRIPE_PRICE_ENTITLEMENT_MAP` alimenté** : dans `stripe_billing_profile_service.py`, le dictionnaire est construit depuis `settings.stripe_price_basic` et `settings.stripe_price_premium`. Si une valeur est absente ou `None`, elle n'est pas insérée dans le mapping. La règle fail-closed de 61-1 reste inchangée.

7. **`.env.example` mis à jour** : les variables `STRIPE_PRICE_BASIC`, `STRIPE_PRICE_PREMIUM` et `STRIPE_API_VERSION` sont ajoutées dans la section Stripe existante, avec valeurs vides ou valeur de référence commentée.

8. **Non-régression** : `ruff check backend --fix && ruff check backend` retourne 0 erreur. `pytest -q backend` passe entièrement, y compris les tests Stripe existants de 61-1, sans appel réseau réel à l'API Stripe.

9. **Tests unitaires de fumée** : tests sur `_build_price_entitlement_map()` (map alimentée, map vide) et sur `get_stripe_client()` (retourne client si clé présente, retourne `None` si absente).

## Tasks / Subtasks

- [x] **Ajouter `stripe==14.4.1` dans `pyproject.toml`** (AC: 1)
  - [x] Éditer `backend/pyproject.toml`, section `[project].dependencies`
  - [x] Ajouter `"stripe==14.4.1",` (entre `sqlalchemy` et `uvicorn` en ordre alphabétique)
  - [x] Vérifier `pip install -e .` sans erreur

- [x] **Compléter `backend/.env`** (AC: 2, 3)
  - [x] Ajouter le bloc suivant — remplacer les placeholders par les vraies valeurs du Stripe Dashboard (mode test) :
    ```dotenv
    # ─── Stripe ───
    STRIPE_SECRET_KEY=sk_test_REPLACE_ME
    STRIPE_WEBHOOK_SECRET=whsec_REPLACE_ME
    STRIPE_PUBLISHABLE_KEY=pk_test_REPLACE_ME
    STRIPE_PRICE_BASIC=price_REPLACE_ME_basic
    STRIPE_PRICE_PREMIUM=price_REPLACE_ME_premium
    STRIPE_API_VERSION=2024-12-18.acacia
    ```
  - [x] Vérifier que `backend/.env` est bien dans `.gitignore` (déjà le cas — ne pas committer)

- [x] **Étendre `config.py`** (AC: 4)
  - [x] Dans `Settings.__init__`, après le bloc Stripe existant (lignes 274–277), ajouter :
    ```python
    self.stripe_price_basic = os.getenv("STRIPE_PRICE_BASIC", "").strip() or None
    self.stripe_price_premium = os.getenv("STRIPE_PRICE_PREMIUM", "").strip() or None
    self.stripe_api_version = os.getenv("STRIPE_API_VERSION", "2024-12-18.acacia").strip()
    ```

- [x] **Créer `backend/app/integrations/stripe_client.py`** (AC: 5)
  - [x] Créer le fichier (et le répertoire `integrations/` s'il n'existe pas, avec un `__init__.py` vide) :
    ```python
    from __future__ import annotations

    import stripe

    from app.core.config import settings


    def get_stripe_client() -> stripe.StripeClient | None:
        """Retourne un StripeClient configuré, ou None si la clé secrète est absente."""
        if not settings.stripe_secret_key:
            return None
        return stripe.StripeClient(
            api_key=settings.stripe_secret_key,
            stripe_version=settings.stripe_api_version,
        )
    ```
  - [x] Ne pas utiliser `stripe.api_key = ...` ni `stripe.api_version = ...` au niveau global du module
  - [x] **À confirmer lors de l'implémentation** : vérifier dans `stripe==14.4.1` si `StripeClient` accepte un paramètre `stripe_version` au constructeur ou si la version d'API s'applique via `options={"stripe_version": settings.stripe_api_version}` au niveau de chaque appel. Adapter `get_stripe_client()` en conséquence et documenter le mécanisme retenu dans le Dev Agent Record.
    - *Note: Confirmed `StripeClient` accepts `stripe_version` keyword argument.*

- [x] **Alimenter `STRIPE_PRICE_ENTITLEMENT_MAP` dans le service** (AC: 6)
  - [x] Dans `stripe_billing_profile_service.py`, remplacer l'ancien dict vide et son commentaire par :
    ```python
    def _build_price_entitlement_map() -> dict[str, str]:
        result: dict[str, str] = {}
        if settings.stripe_price_basic:
            result[settings.stripe_price_basic] = "basic"
        if settings.stripe_price_premium:
            result[settings.stripe_price_premium] = "premium"
        return result

    STRIPE_PRICE_ENTITLEMENT_MAP: dict[str, str] = _build_price_entitlement_map()
    ```
  - [x] Vérifier que `derive_entitlement_plan` continue d'utiliser `STRIPE_PRICE_ENTITLEMENT_MAP` sans changement de signature

- [x] **Mettre à jour `.env.example`** (AC: 7)
  - [x] Dans la section `# Stripe configuration`, ajouter sous les trois lignes existantes :
    ```dotenv
    STRIPE_PRICE_BASIC=
    STRIPE_PRICE_PREMIUM=
    STRIPE_API_VERSION=2024-12-18.acacia
    ```

- [x] **Ajouter les tests unitaires de fumée** (AC: 9)
  - [x] Dans `backend/app/tests/unit/test_stripe_billing_profile_service.py` :
    ```python
    from unittest.mock import patch
    from app.services import stripe_billing_profile_service as svc

    def test_price_entitlement_map_populated_from_settings():
        with patch.object(svc, "settings") as mock_settings:
            mock_settings.stripe_price_basic = "price_basic_test"
            mock_settings.stripe_price_premium = "price_premium_test"
            result = svc._build_price_entitlement_map()
        assert result == {"price_basic_test": "basic", "price_premium_test": "premium"}

    def test_price_entitlement_map_empty_when_no_prices():
        with patch.object(svc, "settings") as mock_settings:
            mock_settings.stripe_price_basic = None
            mock_settings.stripe_price_premium = None
            result = svc._build_price_entitlement_map()
        assert result == {}
    ```
  - [x] Dans `backend/app/tests/unit/test_stripe_client.py` (nouveau fichier) :
    ```python
    from unittest.mock import patch
    from app.integrations import stripe_client as sc

    def test_get_stripe_client_returns_none_when_secret_missing():
        with patch.object(sc, "settings") as mock_settings:
            mock_settings.stripe_secret_key = None
            mock_settings.stripe_api_version = "2024-12-18.acacia"
            result = sc.get_stripe_client()
        assert result is None

    def test_get_stripe_client_returns_client_when_secret_present():
        with patch.object(sc, "settings") as mock_settings:
            mock_settings.stripe_secret_key = "sk_test_123"
            mock_settings.stripe_api_version = "2024-12-18.acacia"
            client = sc.get_stripe_client()
        assert client is not None
    ```

- [x] **Validation finale** (AC: 8)
  - [x] `ruff check backend --fix && ruff check backend` → 0 erreur
  - [x] `pytest -q backend` → tous les tests passent (aucun appel réseau Stripe)

## Dev Notes

### Position dans la séquence Epic 61

```
61-1 (done)  : table DB + service de mapping (sans SDK Stripe)
61-2 (cette story) : SDK installé + secrets chargés + StripeClient initialisé + map alimentée
61-3 (à venir) : Checkout Session.create via get_stripe_client()
61-4 (à venir) : Webhook handler + vérification de signature
```

### Pourquoi `StripeClient` et non le pattern global

Le SDK `stripe-python` a introduit `StripeClient` comme interface principale moderne (service-based call pattern). Par rapport au pattern global historique (`stripe.api_key = ...` au niveau module), `StripeClient` :
- Isole la configuration par client (pas d'état global mutable)
- Facilite les tests (pas besoin de patcher `stripe.api_key`)
- Est la direction documentée du SDK pour les nouvelles intégrations

Le pattern d'appel pour 61-3 sera :
```python
client = get_stripe_client()
session = client.checkout.sessions.create(...)
```

### Isolation dans `app/integrations/`

`get_stripe_client()` est placé dans `backend/app/integrations/stripe_client.py` pour séparer le bootstrap SDK de la logique métier du service de mapping. Les stories 61-3+ importent depuis `app.integrations.stripe_client`, pas depuis `stripe_billing_profile_service`.

Si le répertoire `app/integrations/` n'existe pas, le créer avec un `__init__.py` vide. Vérifier d'abord avec `ls backend/app/`.

### Version d'API — point à confirmer lors de l'implémentation

La valeur par défaut `"2024-12-18.acacia"` (chargée via `STRIPE_API_VERSION`) doit être appliquée de manière stable pour tous les appels Stripe de l'epic. L'épinglage évite une dérive implicite si la version par défaut du compte évolue.

**Mécanisme exact à confirmer** : la doc README de `stripe-python` montre la version d'API via `options={"stripe_version": "..."}` au niveau de chaque requête (per-request). Il est possible que `StripeClient` accepte aussi un paramètre de version au constructeur, mais cela n'est pas confirmé par le README seul. Le dev agent doit, lors de l'implémentation :

1. Inspecter `stripe.StripeClient.__init__` dans `stripe==14.4.1` installé (ou consulter le source GitHub tag v14.4.1).
2. Si le constructeur accepte un paramètre de version (ex. `stripe_version=` ou `api_version=`) → l'utiliser dans `get_stripe_client()` et documenter la signature exacte dans le Dev Agent Record.
3. Sinon → appliquer `options={"stripe_version": settings.stripe_api_version}` sur chaque appel effectif (à partir de 61-3), et mettre à jour la factory en conséquence.

La valeur `settings.stripe_api_version` doit être transmise quelle que soit l'approche retenue.

### État actuel de `stripe_billing_profile_service.py`

- `STRIPE_PRICE_ENTITLEMENT_MAP` (lignes 14–19) : dict vide avec commentaire "À compléter en story 61-2" → **remplacer** par `_build_price_entitlement_map()`.
- `import stripe` : **ne pas ajouter** dans ce fichier — le service ne doit pas bootstrapper le SDK.
- Le service importe `settings` depuis `app.core.config` (déjà présent ou à ajouter si absent).

### Règle fail-closed (invariant critique de 61-1)

> Tout `stripe_price_id` absent de `STRIPE_PRICE_ENTITLEMENT_MAP` → retourne `"free"` + log warning.

`_build_price_entitlement_map()` n'insère une entrée que si la valeur est présente et non vide. En CI ou environnement sans variables Stripe, la map reste vide et le fail-closed s'applique intégralement.

Ne jamais modifier `STRIPE_PRICE_ENTITLEMENT_MAP` depuis un handler : elle est construite une seule fois au démarrage. Tout changement de Price IDs nécessite un redémarrage du service.

### Price IDs — stratégie retenue

Price IDs uniquement (format `price_1Xxx...`) récupérés dans Stripe Dashboard → Products → votre produit → liste des prix. Différents entre environnements test et production — c'est attendu, les variables d'env sont faites pour ça. Migration vers Lookup Keys hors scope.

### Pièges hérités de 61-1 (à ne pas réintroduire)

- Ne pas appeler `db.rollback()` après `begin_nested()`.
- `cancel_at_period_end` peut être `null` Stripe — forcer `bool(... or False)`.
- `stripe_price_id` peut être absent d'un event — garde `if price_id:` avant assignment.

### Fichiers à créer / modifier

| Fichier | Changement |
|---|---|
| `backend/pyproject.toml` | Ajout `stripe==14.4.1` |
| `backend/.env` | Ajout du bloc de 6 variables Stripe (local uniquement) |
| `backend/app/core/config.py` | 3 nouveaux attributs dans `Settings.__init__` |
| `backend/app/integrations/__init__.py` | Créer vide si le répertoire est nouveau |
| `backend/app/integrations/stripe_client.py` | Créer — factory `get_stripe_client()` |
| `backend/app/services/stripe_billing_profile_service.py` | Remplacer dict vide par `_build_price_entitlement_map()` |
| `.env.example` (racine) | 3 variables dans la section Stripe existante |
| `backend/app/tests/unit/test_stripe_billing_profile_service.py` | 2 tests de fumée map |
| `backend/app/tests/unit/test_stripe_client.py` | Créer — 2 tests de fumée client |

### Fichiers à NE PAS TOUCHER

- `backend/app/infra/db/models/stripe_billing.py`
- `backend/migrations/versions/20260324_0053_add_stripe_billing_profiles.py`
- `backend/app/tests/integration/test_stripe_billing_profile_service_integration.py`
- `backend/app/services/billing_service.py`
- Toute migration Alembic existante

### Project Structure Notes

- Dépendances Python → `backend/pyproject.toml` uniquement (JAMAIS de `requirements.txt`)
- Secrets locaux → `backend/.env` (non versionné, `.gitignore`)
- Template secrets → `.env.example` (versionné, valeurs vides)
- Config → `backend/app/core/config.py` via `os.getenv`
- Bootstrap SDK tiers → `backend/app/integrations/` (séparé de la logique métier)

### References

- Story 61-1 : `_bmad-output/implementation-artifacts/61-1-mapping-stripe-billing-profiles.md`
- Service existant : `backend/app/services/stripe_billing_profile_service.py`
- Config existante : `backend/app/core/config.py` lignes 274–277
- `backend/pyproject.toml` — PEP 621, Python 3.13
- `.env.example` (racine) — section Stripe lignes 27–31
- SDK Python : github.com/stripe/stripe-python — v14.4.1, pattern `StripeClient`
- Stripe API versions : Stripe Dashboard → Developers → API Version

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp

### Debug Log References

- Inspecting `stripe.StripeClient.__init__` confirmed that `stripe_version` is a valid keyword argument in `stripe==14.4.1`.
- Cleaned up pre-existing Ruff E501 and E402 errors in several files to ensure a clean codebase as per instructions.

### Completion Notes List

- Installed `stripe==14.4.1` in `backend/pyproject.toml`.
- Configured `backend/.env` (local) and `.env.example` with Stripe variables.
- Extended `Settings` in `config.py` to load new Stripe variables.
- Created `backend/app/integrations/stripe_client.py` with `get_stripe_client()` factory.
- Updated `stripe_billing_profile_service.py` to use `_build_price_entitlement_map()` from settings.
- Added unit tests for both the entitlement map and the stripe client factory.
- Verified everything with Ruff and Pytest.

### File List

- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/pyproject.toml`
- `backend/app/core/config.py`
- `backend/app/integrations/__init__.py`
- `backend/app/integrations/stripe_client.py`
- `backend/app/services/stripe_billing_profile_service.py`
- `.env.example`
- `backend/app/tests/unit/test_stripe_billing_profile_service.py`
- `backend/app/tests/unit/test_stripe_client.py`
- `backend/app/api/v1/routers/astrologers.py` (lint fix)
- `backend/app/infra/db/models/astrologer.py` (lint fix)
- `backend/app/infra/db/models/consultation_template.py` (lint fix)
- `backend/app/services/consultation_catalogue_service.py` (lint fix)
- `backend/app/tests/integration/test_astrologers_api.py` (lint fix)

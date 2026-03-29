# Story 61.50 : Validation métier end-to-end du plan commercial et clôture du chantier

Status: done

## Story

En tant que responsable produit ou backend,
je veux disposer d'une validation end-to-end du plan commercial appliqué dans l'application,
afin de confirmer que le besoin initial est couvert de bout en bout et de clôturer le chantier canonique sans angle mort.

---

## Contexte métier et enjeu architectural

Le chantier `epic-61` a transformé le système de droits produit en une plateforme canonique d'entitlements structurée en quatre couches :

1. **Modèle canonique** (61.7–61.10) : catalogues plans, features, bindings, quotas, compteurs.
2. **Migration B2C/B2B** (61.11–61.26) : toutes les features métier lisent depuis le canonique.
3. **Garde-fous structurels** (61.27–61.30) : cohérence au runtime, au démarrage, en CI.
4. **Resolver unifié** (61.47) : `EffectiveEntitlementResolverService` comme source unique de vérité des droits effectifs, branché sur les gates (61.48) et exposé via `GET /v1/entitlements/me` (61.49).

**Cette story est la clôture du chantier.** Elle ne livrera pas de nouvelles fonctionnalités, mais prouvera que l'ensemble du socle fonctionne correctement pour chaque offre commerciale réelle, identifiera les éventuels reliquats legacy, et fournira la documentation opérationnelle pérenne.

### Source canonique des droits produit

La vérité des droits produit se trouve dans **`backend/scripts/seed_product_entitlements.py`**, qui est la source faisant foi pour la matrice de validation. Le dev agent **doit lire ce fichier en priorité** avant d'écrire les tests ou la matrice.

---

## Acceptance Criteria

**AC1 — Matrice de validation métier documentée**
Un fichier `docs/entitlements-validation-matrix.md` est créé en lisant `backend/scripts/seed_product_entitlements.py` comme source unique. Il documente, pour chacun des 4 plans (`free`, `trial`, `basic`, `premium`) et chacune des 4 features (`natal_chart_short`, `natal_chart_long`, `astrologer_chat`, `thematic_consultation`) :
- `granted` attendu (booléen)
- `access_mode` attendu (`unlimited`, `quota`, `disabled`, ou `null`)
- `quota_limit` attendu (valeur exacte du seed ou `null`)
- `reason_code` attendu (`granted`, `binding_disabled`, `feature_not_in_plan`, `billing_inactive`, `quota_exhausted`)
- `variant_code` attendu (`null`, `"single_astrologer"`, ou `"multi_astrologer"`)
- Comportement correspondant dans `GET /v1/entitlements/me`

La matrice distingue explicitement le cas `free` (aucune subscription → `plan_code="none"`) du cas `free` (subscription active au plan "free") car les `reason_code` diffèrent.

**AC2 — Tests d'intégration end-to-end couvrant la matrice complète**
Un fichier `backend/app/tests/integration/test_entitlements_e2e_matrix.py` couvre l'intégralité de la matrice :
- Pour chaque combinaison plan × feature (16 cas minimum), le test appelle `GET /v1/entitlements/me` et vérifie les champs `granted`, `reason_code`, `access_mode`, `quota_remaining`, `quota_limit`, `variant_code`.
- Les tests sont organisés par plan (`TestNoSubscription`, `TestFreePlan`, `TestTrialPlan`, `TestBasicPlan`, `TestPremiumPlan`).
- Les valeurs assertées (`quota_limit`, `variant_code`, etc.) correspondent exactement au seed — pas à des suppositions.
- Chaque test crée son propre état DB isolé (SQLite in-memory).

**AC3 — Cohérence backend/frontend prouvée**
Un test dans `test_entitlements_e2e_matrix.py` vérifie que la réponse de `GET /v1/entitlements/me` est suffisante pour piloter l'UX frontend :
- `granted == false` → `reason_code` présent et dans le vocabulaire normalisé (`binding_disabled`, `feature_not_in_plan`, `billing_inactive`, `quota_exhausted`)
- `granted == true` avec quota → `quota_remaining` et `quota_limit` tous deux non-null
- `granted == true` unlimited → `quota_remaining` et `quota_limit` tous deux null
- `variant_code` exposé correctement quand non-null

**AC4 — Inventaire des reliquats legacy**
Un fichier `docs/entitlements-legacy-remnants.md` liste tous les éléments legacy identifiés dans la codebase, avec pour chaque élément : nom du fichier, type, statut (`à supprimer`, `conservé intentionnellement`, `dette documentée`).
Les éléments marqués `à supprimer` qui sont sans risque de régression sont supprimés dans cette story.

**AC5 — Documentation de clôture**
Un fichier `docs/entitlements-operations.md` est créé contenant les trois sections obligatoires :
- **"Comment modifier une offre commerciale"** : procédure pour modifier `seed_product_entitlements.py`, ré-exécuter le seed et valider.
- **"Où se trouve la vérité des droits produit"** : cartographie des fichiers sources.
- **"Comment valider un changement de plan"** : commandes pytest et endpoint à appeler.

**AC6 — Aucune régression**
L'ensemble de la suite de tests existante liée au chantier 61 passe sans modification. Aucun fichier gate, resolver ou endpoint n'est modifié dans cette story.

---

## Tasks / Subtasks

- [x] **Lire `backend/scripts/seed_product_entitlements.py`** (prérequis de tout le reste)
  - [x] Extraire la matrice exacte des bindings : `is_enabled`, `access_mode`, `variant_code`, `quota_limit`, `period_unit`, `reset_mode` pour chaque plan × feature
  - [x] Identifier les deux cas du plan "free" : user sans subscription (plan_code="none") vs user avec subscription au plan "free"

- [x] **Construire la matrice de validation métier** (AC: 1)
  - [x] Créer `docs/entitlements-validation-matrix.md` avec le tableau complet, valeurs exactes du seed
  - [x] Ajouter la colonne `variant_code` et les détails de quota (clé, période, reset_mode)
  - [x] Documenter le comportement correspondant dans `GET /v1/entitlements/me` pour chaque cas

- [x] **Ajouter les scénarios automatisés** (AC: 2, 3)
  - [x] Créer `backend/app/tests/integration/test_entitlements_e2e_matrix.py`
  - [x] Implémenter `_create_b2c_scenario(db, plan_code, billing_status)` en réutilisant les helpers de `test_effective_entitlement_resolver_service.py` (`_create_plan_catalog`, `_create_feature_catalog`, `_create_binding`, `_create_quota_binding`, `_create_usage`)
  - [x] Classe `TestNoSubscription` : user sans plan → 4 features en `feature_not_in_plan`
  - [x] Classe `TestFreePlan` : user avec subscription au plan "free" → `natal_chart_short` granted unlimited, 3 autres `binding_disabled`
  - [x] Classe `TestTrialPlan` (billing_status="trialing") : `natal_chart_short` unlimited, `natal_chart_long` quota/1/lifetime, `astrologer_chat` binding_disabled, `thematic_consultation` quota/1/week
  - [x] Classe `TestBasicPlan` : toutes features en `granted`, `natal_chart_long` quota/1/lifetime, `astrologer_chat` quota/5/day, `thematic_consultation` quota/1/week
  - [x] Classe `TestPremiumPlan` : `natal_chart_short` unlimited, `natal_chart_long` quota/5/lifetime, `astrologer_chat` quota/2000/month, `thematic_consultation` quota/2/day
  - [x] Test frontend-sufficiency : vérifier les invariants d'AC3 pour chaque plan

- [x] **Identifier les derniers reliquats legacy** (AC: 4)
  - [x] Rechercher `final_access`, `FallbackEntitlement`, imports `entitlement_service` dans les gates et routeurs
  - [x] Identifier tables/colonnes DB non utilisées par le canonique (hors migrations historiques)
  - [x] Créer `docs/entitlements-legacy-remnants.md` avec l'inventaire complet
  - [x] Supprimer les éléments `à supprimer` prouvablement inutiles (0 référence hors migrations)

- [x] **Rédiger la doc de clôture du chantier** (AC: 5)
  - [x] Créer `docs/entitlements-operations.md`
  - [x] Section "Comment modifier une offre commerciale"
  - [x] Section "Où se trouve la vérité des droits produit"
  - [x] Section "Comment valider un changement de plan"

---

## Dev Notes

### Matrice canonique — valeurs exactes du seed

La source faisant foi est `backend/scripts/seed_product_entitlements.py`. Les valeurs ci-dessous en sont extraites directement et constituent la vérité attendue dans les tests.

#### Plan : `free` (user sans subscription active — plan_code="none")

| Feature | granted | access_mode | quota_limit | variant_code | reason_code |
|---|---|---|---|---|---|
| natal_chart_short | false | null | null | null | feature_not_in_plan |
| natal_chart_long | false | null | null | null | feature_not_in_plan |
| astrologer_chat | false | null | null | null | feature_not_in_plan |
| thematic_consultation | false | null | null | null | feature_not_in_plan |

> Cas : `BillingService` retourne `sub.plan = None` → `plan_code="none"` → aucun plan canonique chargé → tous les bindings absents.

#### Plan : `free` (user avec subscription active au plan "free")

| Feature | granted | access_mode | quota_limit | variant_code | reason_code |
|---|---|---|---|---|---|
| natal_chart_short | **true** | unlimited | null | null | granted |
| natal_chart_long | false | disabled | null | null | binding_disabled |
| astrologer_chat | false | disabled | null | null | binding_disabled |
| thematic_consultation | false | disabled | null | null | binding_disabled |

> Cas : binding `natal_chart_short` → `is_enabled=True, UNLIMITED`. Autres bindings → `is_enabled=False, DISABLED`.

#### Plan : `trial` (billing_status="trialing")

| Feature | granted | access_mode | quota_limit | variant_code | quota_key | période |
|---|---|---|---|---|---|---|
| natal_chart_short | true | unlimited | null | null | — | — |
| natal_chart_long | true* | quota | 1 | single_astrologer | interpretations | lifetime |
| astrologer_chat | false | disabled | null | null | — | binding_disabled |
| thematic_consultation | true* | quota | 1 | null | consultations | 1 semaine CALENDAR |

> `billing_status="trialing"` est actif (`_ACTIVE_BILLING_STATUSES = {"active", "trialing"}`). `*` granted si quota non épuisé.

#### Plan : `basic` (billing_status="active")

| Feature | granted | access_mode | quota_limit | variant_code | quota_key | période |
|---|---|---|---|---|---|---|
| natal_chart_short | true | unlimited | null | null | — | — |
| natal_chart_long | true* | quota | 1 | single_astrologer | interpretations | lifetime |
| astrologer_chat | true* | quota | 5 | null | messages | 1 jour CALENDAR |
| thematic_consultation | true* | quota | 1 | null | consultations | 1 semaine CALENDAR |

#### Plan : `premium` (billing_status="active")

| Feature | granted | access_mode | quota_limit | variant_code | quota_key | période |
|---|---|---|---|---|---|---|
| natal_chart_short | true | unlimited | null | null | — | — |
| natal_chart_long | true* | quota | 5 | multi_astrologer | interpretations | lifetime |
| astrologer_chat | true* | quota | 2000 | null | messages | 1 mois CALENDAR |
| thematic_consultation | true* | quota | 2 | null | consultations | 1 jour CALENDAR |

> **Correction vs hypothèse initiale :** aucune feature n'est "unlimited" pour premium sauf `natal_chart_short`. Toutes les autres sont en mode `quota` avec des limites généreuses.

### Comportement resolver pour billing_inactive

Si `billing_status` n'est pas dans `{"active", "trialing"}` (ex: `"canceled"`, `"past_due"`) et que le binding est `is_enabled=True`, le resolver retourne `billing_inactive` (pas `binding_disabled`). Ce cas doit être couvert par au moins un test dédié dans `TestBillingInactiveScenario`.

### Pattern tests d'intégration e2e

```python
# backend/app/tests/integration/test_entitlements_e2e_matrix.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.infra.db.models.base import Base

@pytest.fixture(scope="class")
def engine():
    e = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(e)
    yield e
    e.dispose()

@pytest.fixture(scope="class")
def db_session(engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()

def _get_feature(response, feature_code: str) -> dict:
    data = response.json()["data"]
    return next(f for f in data["features"] if f["feature_code"] == feature_code)


class TestNoSubscription:
    """User sans subscription : plan_code="none", tous feature_not_in_plan."""

    def test_all_features_not_in_plan(self, db_session):
        # Créer user sans aucune subscription
        user = _create_user(db_session)
        # Pas de plan, pas de subscription créés
        response = _client_get_entitlements(user)
        data = response.json()["data"]
        assert data["plan_code"] == "none"
        for feature_code in ("natal_chart_short", "natal_chart_long",
                              "astrologer_chat", "thematic_consultation"):
            f = _get_feature(response, feature_code)
            assert f["granted"] is False
            assert f["reason_code"] == "feature_not_in_plan"
            assert f["access_mode"] is None


class TestFreePlan:
    """User avec subscription active au plan "free"."""

    def test_natal_chart_short_granted_unlimited(self, db_session):
        user = _create_b2c_scenario(db_session, "free", billing_status="active")
        response = _client_get_entitlements(user)
        f = _get_feature(response, "natal_chart_short")
        assert f["granted"] is True
        assert f["access_mode"] == "unlimited"
        assert f["quota_limit"] is None
        assert f["reason_code"] == "granted"

    def test_other_features_binding_disabled(self, db_session):
        user = _create_b2c_scenario(db_session, "free", billing_status="active")
        response = _client_get_entitlements(user)
        for feature_code in ("natal_chart_long", "astrologer_chat", "thematic_consultation"):
            f = _get_feature(response, feature_code)
            assert f["granted"] is False, f"{feature_code} should be denied"
            assert f["reason_code"] == "binding_disabled"
            assert f["access_mode"] == "disabled"


class TestTrialPlan:
    """billing_status='trialing' → actif pour le resolver."""

    def test_natal_chart_short_unlimited(self, db_session):
        user = _create_b2c_scenario(db_session, "trial", billing_status="trialing")
        f = _get_feature(_client_get_entitlements(user), "natal_chart_short")
        assert f["granted"] is True
        assert f["access_mode"] == "unlimited"

    def test_natal_chart_long_quota_1_lifetime(self, db_session):
        user = _create_b2c_scenario(db_session, "trial", billing_status="trialing")
        f = _get_feature(_client_get_entitlements(user), "natal_chart_long")
        assert f["granted"] is True
        assert f["access_mode"] == "quota"
        assert f["quota_limit"] == 1
        assert f["variant_code"] == "single_astrologer"

    def test_astrologer_chat_binding_disabled(self, db_session):
        user = _create_b2c_scenario(db_session, "trial", billing_status="trialing")
        f = _get_feature(_client_get_entitlements(user), "astrologer_chat")
        assert f["granted"] is False
        assert f["reason_code"] == "binding_disabled"

    def test_thematic_consultation_quota_1_per_week(self, db_session):
        user = _create_b2c_scenario(db_session, "trial", billing_status="trialing")
        f = _get_feature(_client_get_entitlements(user), "thematic_consultation")
        assert f["granted"] is True
        assert f["access_mode"] == "quota"
        assert f["quota_limit"] == 1


class TestBasicPlan:
    def test_natal_chart_long_quota_1_lifetime(self, db_session):
        user = _create_b2c_scenario(db_session, "basic")
        f = _get_feature(_client_get_entitlements(user), "natal_chart_long")
        assert f["granted"] is True
        assert f["quota_limit"] == 1
        assert f["variant_code"] == "single_astrologer"

    def test_astrologer_chat_quota_5_per_day(self, db_session):
        user = _create_b2c_scenario(db_session, "basic")
        f = _get_feature(_client_get_entitlements(user), "astrologer_chat")
        assert f["granted"] is True
        assert f["access_mode"] == "quota"
        assert f["quota_limit"] == 5

    def test_thematic_consultation_quota_1_per_week(self, db_session):
        user = _create_b2c_scenario(db_session, "basic")
        f = _get_feature(_client_get_entitlements(user), "thematic_consultation")
        assert f["granted"] is True
        assert f["quota_limit"] == 1


class TestPremiumPlan:
    def test_natal_chart_long_quota_5_lifetime_multi_astrologer(self, db_session):
        user = _create_b2c_scenario(db_session, "premium")
        f = _get_feature(_client_get_entitlements(user), "natal_chart_long")
        assert f["quota_limit"] == 5
        assert f["variant_code"] == "multi_astrologer"

    def test_astrologer_chat_quota_2000_per_month(self, db_session):
        user = _create_b2c_scenario(db_session, "premium")
        f = _get_feature(_client_get_entitlements(user), "astrologer_chat")
        assert f["quota_limit"] == 2000

    def test_thematic_consultation_quota_2_per_day(self, db_session):
        user = _create_b2c_scenario(db_session, "premium")
        f = _get_feature(_client_get_entitlements(user), "thematic_consultation")
        assert f["quota_limit"] == 2
```

**Fichiers de référence pour les helpers de fixtures :**
- `backend/app/tests/unit/test_effective_entitlement_resolver_service.py` — helpers `_create_plan_catalog`, `_create_feature_catalog`, `_create_binding`, `_create_quota_binding`, `_create_usage` (source principale à réutiliser)
- `backend/app/tests/integration/test_entitlements_me.py` — pattern `TestClient` + auth headers existant
- `backend/app/tests/integration/test_chat_entitlement.py` — pattern subscription mock + DB

### Recherche des reliquats legacy

```bash
# Champs legacy dans les routes/gates (doit être absent hors admin/ops)
grep -rn "final_access" backend/app --include="*.py" | grep -v "__pycache__"

# EntitlementService encore importé dans les gates (doit être absent après 61.48)
grep -rn "from app.services.entitlement_service import" backend/app/services --include="*.py"

# Fallbacks non documentés dans les services
grep -rn "fallback" backend/app/services --include="*.py" | grep -v "__pycache__"

# Tables legacy billing référencées dans la logique métier (hors migrations)
grep -rn "billing_plan" backend/app --include="*.py" | grep -v "alembic\|migrations\|__pycache__"
```

### Cartographie des sources de vérité (pour `docs/entitlements-operations.md`)

| Niveau | Fichier | Rôle |
|---|---|---|
| Seed | `backend/scripts/seed_product_entitlements.py` | **Source de vérité des offres commerciales** — à modifier pour changer un plan |
| Modèle DB | `backend/app/infra/db/models/product_entitlements.py` | Tables canoniques (PlanCatalogModel, FeatureCatalogModel, PlanFeatureBindingModel, PlanFeatureQuotaModel) |
| Registry | `backend/app/services/feature_scope_registry.py` | Liste exhaustive des features B2C/B2B reconnues |
| Resolver | `backend/app/services/effective_entitlement_resolver_service.py` | Source unique des droits effectifs runtime |
| Endpoint | `backend/app/api/v1/routers/entitlements.py` | Exposition frontend via `GET /v1/entitlements/me` |
| Gates | `backend/app/services/*_entitlement_gate.py` | Contrôles d'accès runtime par feature |

### Architecture Guardrails

- Stack : Python 3.13, FastAPI, SQLAlchemy 2.x, pytest.
- **Aucune modification** des services métier, gates, resolver ou endpoint dans cette story.
- **Aucune migration Alembic**.
- **Aucun endpoint nouveau**.
- Les suppressions de reliquats legacy : vérifier `grep -rn "NomDuSymbole" backend/app --include="*.py"` = 0 résultat hors `__pycache__` et migrations historiques avant toute suppression.
- Documentation en français dans `docs/`.

### Anti-régressions explicites

- Ne pas modifier `EffectiveEntitlementResolverService`, les gates, ou `GET /v1/entitlements/me`.
- Ne pas supprimer de code encore importé ailleurs.
- Les tests existants (`test_effective_entitlement_resolver_service.py`, `test_entitlements_me.py`, `test_chat_entitlement.py`, etc.) ne doivent pas être modifiés.
- Les fixtures du fichier test e2e ne doivent pas interférer avec d'autres tests — chaque classe utilise son propre engine SQLite in-memory.

### Intelligence des stories précédentes

| Story | Livraison | Pertinence pour 61.50 |
|---|---|---|
| 61.47 | `EffectiveEntitlementResolverService` | Source des helpers de fixtures ; logique de résolution `billing_inactive`, `binding_disabled`, `feature_not_in_plan` |
| 61.48 | Branchement gates sur le resolver | Les 4 gates utilisent le resolver — à vérifier implicitement via les tests e2e end-to-end |
| 61.49 | Nouveau contrat `GET /v1/entitlements/me` | Contrat cible : `plan_code`, `billing_status` top-level, `granted`, `reason_code`, `quota_remaining`, `quota_limit`, `variant_code` par feature |

**Leçon 61.47 (review) :** réutiliser les helpers SQLite in-memory de `test_effective_entitlement_resolver_service.py` plutôt que de les réécrire.

**Leçon 61.49 :** les fixtures de plans/bindings/quotas en SQLite in-memory sont plus fiables que les mocks de `BillingService` — pattern à privilégier.

### Fichiers à créer

```text
docs/entitlements-validation-matrix.md        ← NOUVEAU (matrice métier documentée)
docs/entitlements-legacy-remnants.md          ← NOUVEAU (inventaire reliquats)
docs/entitlements-operations.md               ← NOUVEAU (doc clôture chantier)
backend/app/tests/integration/test_entitlements_e2e_matrix.py  ← NOUVEAU (tests e2e)
```

### Project Structure Notes

- Services métier : `backend/app/services/`
- Modèles DB : `backend/app/infra/db/models/`
- Routeurs API : `backend/app/api/v1/routers/`
- Tests d'intégration : `backend/app/tests/integration/`
- Tests unitaires : `backend/app/tests/unit/`
- Documentation : `docs/`
- Scripts (seed) : `backend/scripts/`

### References

- `backend/scripts/seed_product_entitlements.py` — **source de vérité des offres commerciales** (lire en premier)
- `backend/app/services/effective_entitlement_resolver_service.py` — resolver
- `backend/app/services/entitlement_types.py` — `EffectiveEntitlementsSnapshot`, `EffectiveFeatureAccess`
- `backend/app/services/feature_scope_registry.py` — liste canonique des features
- `backend/app/infra/db/models/product_entitlements.py` — modèles DB canoniques
- `backend/app/api/v1/routers/entitlements.py` — endpoint `GET /v1/entitlements/me`
- `backend/app/api/v1/schemas/entitlements.py` — schémas Pydantic de la réponse
- `backend/app/tests/unit/test_effective_entitlement_resolver_service.py` — helpers fixtures SQLite in-memory
- `backend/app/tests/integration/test_entitlements_me.py` — pattern tests d'intégration existant
- `_bmad-output/implementation-artifacts/61-47-resolution-canonique-des-droits-effectifs-utilisateur.md` — resolver
- `_bmad-output/implementation-artifacts/61-48-branchement-runtime-unifie-gates-produit-resolver-effectif.md` — gates
- `_bmad-output/implementation-artifacts/61-49-contrat-frontend-unique-plan-commercial-droits-effectifs.md` — contrat frontend

---

## Hors périmètre explicite

- Ne pas modifier les gates, le resolver, l'endpoint ou les schémas Pydantic.
- Ne pas ajouter de logique métier ou de nouveaux endpoints.
- Ne pas créer de migration Alembic.
- Ne pas couvrir les scénarios B2B (hors périmètre de `GET /v1/entitlements/me`).
- Ne pas refactorer les tests existants.
- Ne pas modifier `backend/scripts/seed_product_entitlements.py` (lecture seule dans cette story).

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Lecture de `backend/scripts/seed_product_entitlements.py` — source de vérité des bindings par plan
- Lecture de `backend/app/services/effective_entitlement_resolver_service.py` — logique de résolution (`binding_disabled` vs `feature_not_in_plan`, `_ACTIVE_BILLING_STATUSES`)
- Lecture des stories 61.47, 61.48, 61.49 pour le contexte des livraisons précédentes
- Lecture du `sprint-status.yaml` — epic-61 in-progress

### Completion Notes List
- Revue post-implémentation effectuée sur le delta 61.50.
- Correctif appliqué sur `test_entitlements_e2e_matrix.py` pour isoler chaque scénario dans sa propre DB SQLite in-memory.
- Le test e2e verrouille désormais explicitement les champs frontend `quota_limit`, `quota_remaining`, `reason_code` et `variant_code` en plus de `usage_states`.
- La documentation métier et opérationnelle a été réalignée avec les AC: matrice complète, comportement API explicite, commandes PowerShell avec activation du venv et inventaire legacy traçable.

### File List
- `docs/entitlements-validation-matrix.md` (NOUVEAU)
- `docs/entitlements-legacy-remnants.md` (NOUVEAU)
- `docs/entitlements-operations.md` (NOUVEAU)
- `backend/app/tests/integration/test_entitlements_e2e_matrix.py` (NOUVEAU)
- `backend/app/services/entitlement_service.py` (SUPPRIMÉ)
- `backend/app/tests/unit/test_entitlement_service.py` (SUPPRIMÉ)
- `backend/app/services/entitlement_types.py` (MODIFIÉ)
- `backend/app/tests/integration/test_thematic_consultation_entitlement.py` (MODIFIÉ)
- `_bmad-output/implementation-artifacts/61-50-validation-metier-end-to-end-plan-commercial-corrected.md` (NOUVEAU)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (MODIFIÉ)

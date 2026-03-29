# Story 61.49 : Contrat frontend unique du plan commercial et des droits effectifs

Status: done

## Story

En tant que frontend de l'application,
je veux consommer un contrat unique décrivant le plan commercial courant et les droits effectifs par feature,
afin d'afficher correctement les états d'accès, les quotas restants et les CTA de montée en gamme.

---

## Contexte métier et enjeu architectural

L'endpoint `GET /v1/entitlements/me` a été introduit en story 61.14 pour exposer les états d'accès au frontend. Il repose actuellement sur **`EntitlementService.get_feature_entitlement()`** — appelé 4 fois en boucle — et retourne un payload `data.features: list[FeatureEntitlementResponse]` avec des champs legacy (`final_access`, `reason`, `plan_code` et `billing_status` dupliqués par feature).

La story 61.47 a livré `EffectiveEntitlementResolverService` qui produit un `EffectiveEntitlementsSnapshot` complet en un seul appel. La story 61.48 a branché les gates produit sur ce resolver.

**Cette story finalise le contrat produit :** rebrancher `GET /v1/entitlements/me` sur le resolver, restructurer la réponse pour qu'elle soit lisible et stable, et garantir sa stabilité par des tests de contrat par plan.

---

## Acceptance Criteria

**AC1 — Top-level `plan_code` et `billing_status`**
La réponse expose `plan_code` et `billing_status` au niveau de `data` (pas en doublon par feature). Ces valeurs proviennent directement du snapshot `EffectiveEntitlementsSnapshot`.

**AC2 — Features prioritaires toujours présentes**
Les 4 features `natal_chart_short`, `natal_chart_long`, `astrologer_chat`, `thematic_consultation` sont toujours présentes dans la réponse, quel que soit le plan ou l'état de billing.

**AC3 — Champs par feature suffisants pour piloter l'UX**
Chaque entrée feature expose au minimum :
- `feature_code` — identifiant de la feature
- `granted` — booléen d'accès effectif
- `reason_code` — raison normalisée (`granted`, `feature_not_in_plan`, `billing_inactive`, `quota_exhausted`, `binding_disabled`, `subject_not_eligible`)
- `quota_remaining` — quotas restants (null si unlimited ou feature sans quota)
- `quota_limit` — limite de quota (null si unlimited)
- `variant_code` — variante du binding (null si aucune)
- `access_mode` — `quota`, `unlimited`, `disabled`, ou null

**AC4 — Suffisance frontend**
Le frontend peut, à partir de cette seule réponse, sans logique métier supplémentaire :
- désactiver un CTA si `granted == false`
- afficher le quota restant via `quota_remaining` et `quota_limit`
- afficher le motif de blocage via `reason_code`
- afficher un CTA d'upgrade si `reason_code in ["feature_not_in_plan", "billing_inactive", "quota_exhausted"]`

**AC5 — Rebanchement sur le resolver**
L'endpoint appelle `EffectiveEntitlementResolverService.resolve_b2c_user_snapshot()` une seule fois. Il ne boucle plus sur `EntitlementService.get_feature_entitlement()`.

**AC6 — Tests de contrat d'intégration**
Un fichier `backend/app/tests/integration/test_entitlements_me_contract.py` couvre les 4 situations structurelles, chacune avec ses propres fixtures DB explicites (pas de présupposition sur la matrice commerciale réelle) :
- **Cas sans plan actif** — utilisateur sans abonnement → `plan_code="none"`, `billing_status="none"`, toutes les features en `granted=False` avec `reason_code="feature_not_in_plan"` ou `"billing_inactive"`
- **Cas feature quota disponible** — binding QUOTA configuré + usage partiel → `granted=True`, `reason_code="granted"`, `quota_remaining` et `quota_limit` corrects
- **Cas feature quota épuisé** — binding QUOTA configuré + usage = limite → `granted=False`, `reason_code="quota_exhausted"`, `quota_remaining=0`
- **Cas feature unlimited** — binding UNLIMITED configuré → `granted=True`, `reason_code="granted"`, `quota_remaining=None`, `quota_limit=None`
- B2B est hors périmètre (B2B n'utilise pas `GET /v1/entitlements/me`)

Chaque cas ne teste que la situation structurelle qu'il configure — les codes de plan utilisés dans les fixtures (`"free"`, `"basic"`, etc.) sont arbitraires et ne doivent pas encoder la matrice commerciale réelle.

**AC7 — Périmètre exact de la compatibilité**
Ce changement de schéma est **intentionnellement breaking** sur les champs legacy.

Ce qui **casse** (les clients frontend doivent migrer) :
- `data.features[].final_access` → remplacé par `data.features[].granted`
- `data.features[].reason` → remplacé par `data.features[].reason_code`
- `data.features[].plan_code` → supprimé (déplacé en `data.plan_code`)
- `data.features[].billing_status` → supprimé (déplacé en `data.billing_status`)

Ce qui est **garanti préservé** (aucun client ne doit adapter ces points) :
- L'URL `GET /v1/entitlements/me`
- L'enveloppe `{ "data": {...}, "meta": { "request_id": "..." } }`
- Le code HTTP 200 en cas de succès
- Les codes HTTP 401/403 pour les erreurs d'auth
- Le champ `usage_states` par feature (conservé tel quel)
- L'ordre et la présence des 4 features prioritaires dans `data.features`

---

## Tasks / Subtasks

- [x] **Refactorer `GET /v1/entitlements/me`** (AC: 1, 2, 3, 5)
  - [x] Remplacer la boucle `EntitlementService.get_feature_entitlement()` par un appel unique à `EffectiveEntitlementResolverService.resolve_b2c_user_snapshot()`
  - [x] Extraire `plan_code` et `billing_status` du snapshot et les placer dans `data`
  - [x] Mapper `snapshot.entitlements` vers la liste de features de la réponse
  - [x] Garantir que les 4 features prioritaires sont toujours présentes (déjà couvert par le resolver qui couvre toutes les features B2C de `FEATURE_SCOPE_REGISTRY`)
  - [x] Supprimer l'import `EntitlementService` devenu inutile dans le routeur

- [x] **Refactorer les schémas Pydantic** (AC: 1, 3)
  - [x] Modifier `EntitlementsMeData` dans `backend/app/api/v1/schemas/entitlements.py` pour y ajouter `plan_code: str` et `billing_status: str`
  - [x] Modifier `FeatureEntitlementResponse` pour remplacer `final_access`/`reason` (legacy) par `granted: bool` et `reason_code: str`
  - [x] Ajouter `quota_remaining: int | None` et `quota_limit: int | None` comme champs de premier niveau dans `FeatureEntitlementResponse` (déjà résolvables depuis `EffectiveFeatureAccess`)
  - [x] Supprimer les champs `plan_code` et `billing_status` de `FeatureEntitlementResponse` (déplacés au top-level)
  - [x] Conserver `usage_states` pour compatibilité

- [x] **Documenter le contrat frontend** (AC: 4)
  - [x] Ajouter une docstring sur le schéma `EntitlementsMeResponse` décrivant sa suffisance pour le frontend
  - [x] Ajouter un commentaire dans le routeur sur le mapping `reason_code → action UX`

- [x] **Ajouter les tests de contrat d'intégration** (AC: 6)
  - [x] Créer `backend/app/tests/integration/test_entitlements_me_contract.py`
  - [x] Cas sans plan actif : utilisateur sans abonnement → `plan_code="none"`, `billing_status="none"`, toutes features `granted=False`
  - [x] Cas quota disponible : plan fictif + binding QUOTA (ex. `quota_limit=5`) + usage partiel (ex. `used=2`) → `granted=True`, `quota_remaining=3`, `quota_limit=5`
  - [x] Cas quota épuisé : même setup avec `used=5` → `granted=False`, `reason_code="quota_exhausted"`, `quota_remaining=0`
  - [x] Cas unlimited : plan fictif + binding UNLIMITED → `granted=True`, `quota_remaining=None`, `quota_limit=None`
  - [x] Vérifier dans chaque cas : `plan_code` et `billing_status` au niveau `data`, les 4 features prioritaires toujours présentes

---

## Dev Notes

### Mapping champs actuels → nouveaux champs

| Ancien champ (`FeatureEntitlementResponse`) | Nouveau champ | Source dans `EffectiveFeatureAccess` |
|---|---|---|
| `plan_code` (par feature) | `plan_code` dans `EntitlementsMeData` | `snapshot.plan_code` |
| `billing_status` (par feature) | `billing_status` dans `EntitlementsMeData` | `snapshot.billing_status` |
| `final_access: bool` | `granted: bool` | `access.granted` |
| `reason: str` (legacy) | `reason_code: str` (normalisé) | `access.reason_code` |
| `access_mode` | `access_mode` (inchangé) | `access.access_mode` |
| `variant_code` | `variant_code` (inchangé) | `access.variant_code` |
| — | `quota_remaining: int \| None` | `access.quota_remaining` |
| — | `quota_limit: int \| None` | `access.quota_limit` |
| `usage_states` | `usage_states` (conservé) | `access.usage_states` |

### Pattern d'implémentation — routeur

```python
# Avant (à supprimer)
for feature_code in FEATURES_TO_QUERY:
    entitlement = EntitlementService.get_feature_entitlement(
        db, user_id=current_user.id, feature_code=feature_code
    )
    features.append(_to_feature_response(feature_code, entitlement))

return {
    "data": {"features": features},
    "meta": {"request_id": request_id},
}

# Après
snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
    db, app_user_id=current_user.id
)

# Construire les features depuis le snapshot — toujours dans l'ordre FEATURES_TO_QUERY
features = [
    _to_feature_response(fc, snapshot.entitlements[fc])
    for fc in FEATURES_TO_QUERY
    if fc in snapshot.entitlements
]

return {
    "data": {
        "plan_code": snapshot.plan_code,
        "billing_status": snapshot.billing_status,
        "features": features,
    },
    "meta": {"request_id": request_id},
}
```

**Garde-fou :** si une feature de `FEATURES_TO_QUERY` est absente du snapshot (cas improbable mais défensif), l'ignorer plutôt que lever une erreur 500.

### Pattern d'implémentation — schémas

```python
# backend/app/api/v1/schemas/entitlements.py

class FeatureEntitlementResponse(BaseModel):
    feature_code: str
    granted: bool                   # remplace final_access
    reason_code: str                # remplace reason (normalisé)
    access_mode: str | None = None
    quota_remaining: int | None = None
    quota_limit: int | None = None
    variant_code: str | None = None
    usage_states: list[UsageStateResponse] = Field(default_factory=list)


class EntitlementsMeData(BaseModel):
    plan_code: str                  # top-level (ex-dupliqué par feature)
    billing_status: str             # top-level
    features: list[FeatureEntitlementResponse] = Field(default_factory=list)
```

### `_to_feature_response` — mapping depuis `EffectiveFeatureAccess`

```python
from app.services.entitlement_types import EffectiveFeatureAccess

def _to_feature_response(
    feature_code: str, access: EffectiveFeatureAccess
) -> FeatureEntitlementResponse:
    return FeatureEntitlementResponse(
        feature_code=feature_code,
        granted=access.granted,
        reason_code=access.reason_code,
        access_mode=access.access_mode,
        quota_remaining=access.quota_remaining,
        quota_limit=access.quota_limit,
        variant_code=access.variant_code,
        usage_states=[_to_usage_state_response(s) for s in access.usage_states],
    )
```

### Mapping `reason_code` → action UX (documentation)

| `reason_code` | `granted` | Action frontend recommandée |
|---|---|---|
| `granted` | `true` | CTA actif, afficher quota restant si applicable |
| `feature_not_in_plan` | `false` | Désactiver CTA, afficher badge "upgrade" |
| `billing_inactive` | `false` | Désactiver CTA, afficher lien renouvellement |
| `quota_exhausted` | `false` | Désactiver CTA, afficher quota `0 / {quota_limit}` |
| `binding_disabled` | `false` | Désactiver CTA, pas d'upgrade possible |
| `subject_not_eligible` | `false` | Désactiver CTA, message générique |

### Structure JSON de la réponse cible

L'exemple ci-dessous illustre la **forme du contrat** — les valeurs (`plan_code`, `granted`, `reason_code`, `quota_*`) dépendent des données en base, pas d'une matrice encodée dans le code.

```json
{
  "data": {
    "plan_code": "<code_du_plan_actif>",
    "billing_status": "<statut_billing>",
    "features": [
      {
        "feature_code": "astrologer_chat",
        "granted": true,
        "reason_code": "granted",
        "access_mode": "quota",
        "quota_remaining": 8,
        "quota_limit": 10,
        "variant_code": null,
        "usage_states": [...]
      },
      {
        "feature_code": "thematic_consultation",
        "granted": false,
        "reason_code": "feature_not_in_plan",
        "access_mode": null,
        "quota_remaining": null,
        "quota_limit": null,
        "variant_code": null,
        "usage_states": []
      },
      {
        "feature_code": "natal_chart_long",
        "granted": true,
        "reason_code": "granted",
        "access_mode": "unlimited",
        "quota_remaining": null,
        "quota_limit": null,
        "variant_code": null,
        "usage_states": []
      },
      {
        "feature_code": "natal_chart_short",
        "granted": true,
        "reason_code": "granted",
        "access_mode": "unlimited",
        "quota_remaining": null,
        "quota_limit": null,
        "variant_code": null,
        "usage_states": []
      }
    ]
  },
  "meta": {
    "request_id": "abc-123"
  }
}
```

Les combinaisons `(granted, reason_code, access_mode, quota_*)` pour chaque feature sont entièrement déterminées par les bindings du plan en base — voir `EffectiveEntitlementResolverService` pour la logique de résolution.

### Pattern tests d'intégration

Les tests de contrat doivent suivre le même pattern que les tests d'intégration existants des gates :
- `TestClient(app)` depuis `fastapi.testclient`
- DB SQLite in-memory via `SessionLocal` + `Base.metadata.create_all`
- Données créées directement en DB (plan catalog, bindings, quotas, utilisateur, subscription mock)
- `_auth_headers()` helper pour obtenir un JWT valide
- Assertions sur le code HTTP `200` et le contenu de la réponse JSON

**Structure type pour un cas de test de contrat :**

```python
def test_entitlements_me_quota_disponible(client, db_session):
    """Feature avec binding QUOTA partiellement consommé : contrat quota correct."""
    # Setup : plan fictif + 1 feature en QUOTA, 1 feature sans binding
    user = _create_user(db_session)
    plan = _create_plan(db_session, code="plan_test")
    _create_binding(db_session, plan, "astrologer_chat", AccessMode.QUOTA, quota_limit=10)
    # thematic_consultation : pas de binding → feature_not_in_plan
    _create_usage(db_session, user.id, "astrologer_chat", used=2)

    headers = _auth_headers(user)
    response = client.get("/v1/entitlements/me", headers=headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["plan_code"] == "plan_test"
    assert data["billing_status"] == "active"

    chat = next(f for f in data["features"] if f["feature_code"] == "astrologer_chat")
    assert chat["granted"] is True
    assert chat["reason_code"] == "granted"
    assert chat["quota_remaining"] == 8
    assert chat["quota_limit"] == 10

    consult = next(f for f in data["features"] if f["feature_code"] == "thematic_consultation")
    assert consult["granted"] is False
    assert consult["reason_code"] == "feature_not_in_plan"
```

**Règle** : les codes de plan dans les fixtures (`"plan_test"`, `"plan_unlimited"`, etc.) sont fictifs. Ne pas utiliser les codes de plan réels (`"basic"`, `"premium"`) pour éviter de coupler les tests à la matrice commerciale du produit.

**Fichiers de référence pour les patterns de fixtures :**
- `backend/app/tests/unit/test_effective_entitlement_resolver_service.py` — fixtures SQLite in-memory complètes B2C/B2B (référence principale)
- `backend/app/tests/integration/test_chat_entitlement.py` — pattern `TestClient` + auth headers
- `backend/app/tests/integration/test_thematic_consultation_entitlement.py` — pattern plan + binding + quota

### Fichiers cibles

```text
# Fichiers à modifier
backend/app/api/v1/routers/entitlements.py          ← MODIFIÉ (rebrancher resolver)
backend/app/api/v1/schemas/entitlements.py           ← MODIFIÉ (nouveaux schémas)

# Fichier à créer
backend/app/tests/integration/test_entitlements_me_contract.py ← NOUVEAU
```

### Architecture Guardrails

- Stack : Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.x, pytest.
- Aucune migration Alembic dans cette story.
- Aucun nouvel endpoint API.
- Aucune modification du modèle de données canonique.
- L'endpoint reste strictement **read-only** — ne jamais appeler `consume()`.
- `EffectiveEntitlementResolverService` est déjà implémenté en 61.47 et durci en review — ne pas le modifier.
- Conserver la structure `data` + `meta.request_id` pour ne pas casser les clients existants.

### Anti-régressions explicites

**Breaking change assumé — champs supprimés du schéma :**
Les champs `final_access`, `reason`, `plan_code` (par feature) et `billing_status` (par feature) sont supprimés de `FeatureEntitlementResponse`. C'est intentionnel. Si le frontend les consomme encore, il doit migrer en même temps que cette story (ou dans une story frontend dédiée planifiée en parallèle).

**Préservé sans condition :**
- URL `GET /v1/entitlements/me` inchangée.
- Enveloppe `{ "data": {...}, "meta": { "request_id": "..." } }` inchangée.
- Code HTTP 200 en succès, 401/403 en erreur d'auth inchangés.
- Champ `usage_states` conservé dans chaque feature.
- Présence des 4 features prioritaires dans `data.features` quel que soit le plan.

**Services à ne pas toucher :**
- Ne pas modifier `EffectiveEntitlementResolverService`.
- Ne pas modifier `EntitlementService` (usages subsistants dans admin/ops).
- Le contrôle d'accès (`role in {"user", "admin"}`) est conservé tel quel.

### Git Intelligence

Les 2 derniers commits concernent la story 61.47 (implémentation du resolver) et son correctif review. Le resolver est stabilisé. La story 61.48 (branchement gates) est `ready-for-dev` et indépendante de cette story (branches orthogonales).

Commit de référence : `feat(entitlements): implementation of EffectiveEntitlementResolverService (Story 61.47)` + `fix(entitlements): review and harden story 61-47`.

### Project Structure Notes

- Routeurs API : `backend/app/api/v1/routers/`
- Schémas Pydantic : `backend/app/api/v1/schemas/`
- Services métier : `backend/app/services/`
- Tests d'intégration : `backend/app/tests/integration/`
- Tests unitaires : `backend/app/tests/unit/`

### References

- `backend/app/api/v1/routers/entitlements.py` — routeur à refactorer
- `backend/app/api/v1/schemas/entitlements.py` — schémas à refactorer
- `backend/app/services/effective_entitlement_resolver_service.py` — resolver à utiliser
- `backend/app/services/entitlement_types.py` — `EffectiveEntitlementsSnapshot`, `EffectiveFeatureAccess`
- `backend/app/tests/unit/test_effective_entitlement_resolver_service.py` — fixtures SQLite in-memory de référence
- `backend/app/tests/integration/test_chat_entitlement.py` — pattern TestClient + auth
- `_bmad-output/implementation-artifacts/61-47-resolution-canonique-des-droits-effectifs-utilisateur.md` — resolver (story précédente N-2)
- `_bmad-output/implementation-artifacts/61-48-branchement-runtime-unifie-gates-produit-resolver-effectif.md` — gates (story précédente N-1)

---

## Hors périmètre explicite

- Ne pas créer d'endpoint B2B pour `GET /v1/entitlements/me` (B2B a ses propres endpoints d'accès).
- Ne pas modifier le modèle de données canonique (plans, bindings, quotas).
- Ne pas migrer d'autres endpoints vers le resolver.
- Ne pas supprimer `EntitlementService` (d'autres usages subsistent).
- Ne pas ajouter de logique de cache ou de préchargement.

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Lecture de `backend/app/api/v1/routers/entitlements.py` — état actuel de l'endpoint
- Lecture de `backend/app/api/v1/schemas/entitlements.py` — schémas Pydantic actuels
- Lecture de `backend/app/services/entitlement_types.py` — types `EffectiveEntitlementsSnapshot`, `EffectiveFeatureAccess`
- Lecture de `backend/app/services/effective_entitlement_resolver_service.py` — resolver livré en 61.47
- Lecture des stories 61.47 et 61.48 pour le contexte des livraisons précédentes
- Inspection du `sprint-status.yaml` — `epic-61: in-progress`, story 61.49 absente (ajoutée dans cette session)
- Analyse git : derniers commits sur 61.47 (resolver) et 61.46 (alertes ops)

### Completion Notes List
- Refactorisation complète de `GET /v1/entitlements/me` pour utiliser `EffectiveEntitlementResolverService`.
- Mise à jour des schémas Pydantic : `plan_code` et `billing_status` déplacés au top-level de `data`, `final_access` remplacé par `granted`, `reason` remplacé par `reason_code`.
- Ajout de `quota_remaining` et `quota_limit` comme champs de premier niveau par feature.
- Documentation du contrat frontend via docstrings et commentaires de code.
- Création de `backend/app/tests/integration/test_entitlements_me_contract.py` couvrant les 4 cas structurels (no plan, quota available, quota exhausted, unlimited).
- Correction des tests existants dans `backend/app/tests/integration/test_entitlements_me.py` impactés par le changement de schéma.
- Review post-implémentation : durcissement du routeur pour retourner défensivement les 4 features prioritaires même si le snapshot du resolver est incomplet.
- Ajout d'un test unitaire dédié pour verrouiller cette invariance de contrat.
- Alignement final Ruff et mise à jour de la documentation d'artefacts.

### File List
- `backend/app/api/v1/routers/entitlements.py`
- `backend/app/api/v1/schemas/entitlements.py`
- `backend/app/tests/integration/test_entitlements_me_contract.py`
- `backend/app/tests/integration/test_entitlements_me.py`
- `backend/app/tests/unit/test_entitlements_me_endpoint.py`
- `docs/api-contracts-backend.md`
- `_bmad-output/implementation-artifacts/61-49-code-review-findings.md`
- `_bmad-output/implementation-artifacts/61-49-contrat-frontend-unique-plan-commercial-droits-effectifs.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

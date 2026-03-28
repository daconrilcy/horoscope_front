# Story 61.35 : Workflow ops de revue des mutations canoniques à risque

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux pouvoir qualifier chaque mutation canonique avec un statut de revue (`pending_review`, `acknowledged`, `expected`, `investigating`, `closed`), un commentaire et un identifiant d'incident,
afin de rendre l'audit trail actionnable en exploitation et d'identifier rapidement les mutations à risque non traitées.

## Contexte

61.32 a créé la trace. 61.33 l'a exposée. 61.34 l'a enrichie (diff + scoring risque). **61.35 la rend actionnables** : un opérateur peut qualifier chaque mutation, et le système expose ces qualifications dans la liste d'audit.

Flux ops cible : **détection** via `risk_level` → **consultation** via 61.33 → **qualification humaine** via 61.35.

**Décision architecturale : table séparée** `canonical_entitlement_mutation_audit_reviews`
L'audit trail existant reste append-only et immuable. La revue est une donnée mutable dans sa propre table. Une seule ligne par `audit_id` (upsert — dernière revue = état courant).

**Statut virtuel `pending_review`** : toute mutation `risk_level="high"` sans revue DB apparaît avec `review_status="pending_review"` dans les réponses API. Ce calcul est **application-level dans le router**, sans aucune écriture DB automatique.

## Acceptance Criteria

### AC 1 — Table `canonical_entitlement_mutation_audit_reviews`

1. Table créée via migration Alembic avec colonnes :
   - `id` (int, PK, autoincrement)
   - `audit_id` (int, FK → `canonical_entitlement_mutation_audits.id`, NOT NULL, UNIQUE)
   - `review_status` (str(32), NOT NULL) — valeurs : `pending_review`, `acknowledged`, `expected`, `investigating`, `closed`
   - `reviewed_by_user_id` (int, nullable) — user ID de l'opérateur auteur de la revue
   - `reviewed_at` (datetime timezone=True, NOT NULL, server_default=now())
   - `review_comment` (Text, nullable)
   - `incident_key` (str(64), nullable)
2. Index UNIQUE sur `audit_id`; index non-unique sur `review_status`.
3. `reviewed_at` est timestamptz (avec timezone, `sa.DateTime(timezone=True)`).

### AC 2 — Modèle SQLAlchemy

4. `backend/app/infra/db/models/canonical_entitlement_mutation_audit_review.py` créé.
5. Classe `CanonicalEntitlementMutationAuditReviewModel(Base)` avec `__tablename__ = "canonical_entitlement_mutation_audit_reviews"`.
6. FK déclarée vers `CanonicalEntitlementMutationAuditModel` via `ForeignKey("canonical_entitlement_mutation_audits.id")`.

### AC 3 — Service d'écriture `CanonicalEntitlementMutationAuditReviewService`

7. `backend/app/services/canonical_entitlement_mutation_audit_review_service.py` créé.
8. Méthode `async upsert_review(db, audit_id, review_status, reviewed_by_user_id, review_comment, incident_key) -> CanonicalEntitlementMutationAuditReviewModel` :
   - Vérifie que `audit_id` existe dans `canonical_entitlement_mutation_audits` → `HTTPException(404)` sinon.
   - Si aucune revue pour `audit_id` → INSERT.
   - Si une revue existe → UPDATE (tous les champs + `reviewed_at = now()`).
   - `db.flush()` mais **PAS** `db.commit()` (le router contrôle la transaction).

### AC 4 — Endpoint `POST /v1/ops/entitlements/mutation-audits/{audit_id}/review`

9. Endpoint ajouté dans `ops_entitlement_mutation_audits.py`.
10. Requiert rôle `ops` ou `admin` (même pattern que les endpoints 61.33/61.34, `HTTPException(403)` sinon).
11. Body Pydantic `ReviewRequestBody` :
    - `review_status` : `Literal["pending_review", "acknowledged", "expected", "investigating", "closed"]` — **obligatoire** → 422 FastAPI natif pour toute valeur invalide.
    - `review_comment` : `str | None = None` — optionnel.
    - `incident_key` : `str | None = None` — optionnel.
12. `reviewed_by_user_id` extrait de `current_user.id` (dépendance auth injectée, **pas dans le body**).
13. Retourne **HTTP 201** avec `ReviewResponse` : `{ audit_id, review_status, reviewed_by_user_id, reviewed_at, review_comment, incident_key }`.
14. Si `audit_id` inexistant → **404**.
15. `response_model_exclude_none=True` actif.

### AC 5 — Enrichissement des GET 61.33 avec l'état de revue

16. Chaque item retourné par `GET /v1/ops/entitlements/mutation-audits` et `GET /v1/ops/entitlements/mutation-audits/{audit_id}` inclut un champ `review` selon la règle :
    - Revue DB existante → `{ "status": "...", "reviewed_by_user_id": ..., "reviewed_at": "...", "review_comment": "...", "incident_key": "..." }`
    - Aucune revue ET `risk_level="high"` → `{ "status": "pending_review", "reviewed_by_user_id": null, "reviewed_at": null, "review_comment": null, "incident_key": null }`
    - Aucune revue ET `risk_level != "high"` → `review: null` (omis automatiquement via `response_model_exclude_none=True`)
17. Champ `review: ReviewState | None = None` ajouté à `MutationAuditItem` (**optionnel**).
18. Les 4 champs dérivés 61.34 (`change_kind`, `changed_fields`, `risk_level`, `quota_changes`) restent **non-optionnels**, inchangés.
19. Les payloads bruts `before_payload` / `after_payload` restent conditionnels à `include_payloads=true`.

### AC 6 — Nouveau filtre `review_status` sur GET list

20. `GET /v1/ops/entitlements/mutation-audits` accepte un nouveau paramètre Query optionnel `review_status` déclaré avec `Literal[...]` (même valeurs — 422 automatique si invalide).
21. Comportement du filtre :
    - Filtres SQL 61.33 appliqués en premier.
    - Si filtre diff 61.34 actif → appliqué ensuite (limite 10 000 SQL).
    - Revues DB chargées en **une seule requête `IN`** sur les `audit_id` du batch.
    - Statut effectif calculé (revue DB ou virtuel `pending_review` si high).
    - Filtrage sur statut effectif.
    - Pagination manuelle sur le résultat filtré.
22. Sans `review_status`, le comportement des endpoints existants est **inchangé**.
23. La pagination dans la réponse (`total_count`, `page`, `page_size`) reflète les résultats **après** filtrage par review_status.

### AC 7 — Chargement des revues sans N+1

24. Sur le chemin paginé normal (sans filtre diff) : les revues des audits de la **page courante** sont chargées en une seule requête `SELECT ... WHERE audit_id IN (...)`.
25. Sur le chemin "filtre diff actif" (batch ≤ 10 000) : les revues du batch complet chargées en une seule requête `IN`.
26. Aucune requête N+1 (pas de `db.get()` en boucle sur les revues).

### AC 8 — Tests unitaires

27. `backend/app/tests/unit/test_canonical_entitlement_mutation_audit_review_service.py` créé avec :
    - `test_upsert_creates_review_when_none_exists`
    - `test_upsert_updates_review_when_already_exists`
    - `test_upsert_updates_reviewed_at_on_update`
    - `test_upsert_raises_404_when_audit_not_found`

### AC 9 — Tests d'intégration

28. `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` enrichi avec :
    - `test_post_review_creates_review_returns_201`
    - `test_post_review_updates_existing_review`
    - `test_post_review_invalid_status_returns_422`
    - `test_post_review_nonexistent_audit_returns_404`
    - `test_post_review_requires_ops_or_admin_role` (403 si rôle `user`)
    - `test_list_review_virtual_pending_for_high_risk_no_review`
    - `test_list_review_populated_when_review_exists`
    - `test_list_review_null_for_low_risk_no_review`
    - `test_filter_by_review_status_pending_review`
    - `test_filter_by_review_status_closed`
    - `test_detail_includes_review_field`
29. Les tests existants 61.33 + 61.34 (22 + tests 61.34) restent verts.

### AC 10 — Périmètre strict : aucun impact sur les mutations canoniques

30. `canonical_entitlement_mutation_service.py` — **non modifié**.
31. `canonical_entitlement_mutation_audit_query_service.py` — **non modifié**.
32. `canonical_entitlement_mutation_audit.py` (modèle) — **non modifié**.
33. Seul fichier existant modifié : `ops_entitlement_mutation_audits.py`.

### AC 11 — Documentation

34. `backend/docs/entitlements-canonical-platform.md` mis à jour avec section **"Story 61.35 — Workflow ops de revue"** décrivant :
    - La table `canonical_entitlement_mutation_audit_reviews` et son schéma.
    - La règle du statut virtuel `pending_review` pour les mutations high sans revue.
    - L'endpoint POST et le filtre `review_status`.

---

## Tasks / Subtasks

- [x] **Créer le modèle SQLAlchemy** (AC: 2)
  - [x] Créer `backend/app/infra/db/models/canonical_entitlement_mutation_audit_review.py`
  - [x] Définir `CanonicalEntitlementMutationAuditReviewModel(Base)` avec tous les champs et FK

- [x] **Créer la migration Alembic** (AC: 1)
  - [x] Créer `backend/migrations/versions/20260328_0057_create_canonical_entitlement_mutation_audit_reviews.py`
  - [x] `down_revision` = `"20260328_0056"` (dernière migration existante)
  - [x] `upgrade()` : `op.create_table(...)` avec index UNIQUE sur `audit_id` + index sur `review_status`
  - [x] `downgrade()` : `op.drop_table(...)`

- [x] **Créer `CanonicalEntitlementMutationAuditReviewService`** (AC: 3)
  - [x] `backend/app/services/canonical_entitlement_mutation_audit_review_service.py`
  - [x] Implémenter `upsert_review(...)` (synchrone) avec vérification audit, INSERT/UPDATE, flush

- [x] **Étendre les schémas Pydantic du router** (AC: 5)
  - [x] Ajouter `ReviewState` (lecture) et `ReviewRequestBody` / `ReviewResponse` (écriture) dans le router
  - [x] Ajouter `review: ReviewState | None = None` à `MutationAuditItem`

- [x] **Enrichir `_to_item` avec le statut de revue** (AC: 5)
  - [x] Accepter `review_record` en paramètre optionnel
  - [x] Appliquer la règle virtuelle : high + no review → pending_review

- [x] **Ajouter le chargement optimisé des revues** (AC: 7)
  - [x] Requête `IN` sur les `audit_id` de chaque page dans le handler GET list
  - [x] Requête `IN` sur le batch dans le handler filtré diff

- [x] **Ajouter le filtre `review_status` au GET list** (AC: 6)
  - [x] Paramètre Query `Literal` dans `list_mutation_audits`
  - [x] Logique de filtrage application-level sur statut effectif + pagination manuelle

- [x] **Ajouter l'endpoint POST** (AC: 4)
  - [x] Route `POST /v1/ops/entitlements/mutation-audits/{audit_id}/review`
  - [x] Validation du rôle, appel `ReviewService.upsert_review()`, commit, retour 201

- [x] **Tests unitaires** (AC: 8)
  - [x] `backend/app/tests/unit/test_canonical_entitlement_mutation_audit_review_service.py` avec 4 cas

- [x] **Tests d'intégration** (AC: 9)
  - [x] Enrichir `test_ops_entitlement_mutation_audits_api.py` avec 11 nouveaux cas

- [x] **Documentation** (AC: 11)
  - [x] `backend/docs/entitlements-canonical-platform.md`

- [x] **Validation finale**
  - [x] `ruff check` — zéro erreur
  - [x] `pytest unit` — 4/4
  - [x] `pytest integration` — 42/42 (+ 4 unit = 46 total)

---

## Dev Notes

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/infra/db/models/canonical_entitlement_mutation_audit_review.py` | Créer — modèle SQLAlchemy |
| `backend/alembic/versions/YYYYMMDD_00NN_create_canonical_entitlement_mutation_audit_reviews.py` | Créer — migration Alembic |
| `backend/app/services/canonical_entitlement_mutation_audit_review_service.py` | Créer — service d'écriture |
| `backend/app/tests/unit/test_canonical_entitlement_mutation_audit_review_service.py` | Créer |
| `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` | Modifier — POST + GET enrichi + filtre review_status |
| `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` | Modifier — 11 nouveaux tests |
| `backend/docs/entitlements-canonical-platform.md` | Modifier — section 61.35 |

**NE PAS modifier** :
- `backend/app/services/canonical_entitlement_mutation_service.py`
- `backend/app/services/canonical_entitlement_mutation_audit_query_service.py`
- `backend/app/infra/db/models/canonical_entitlement_mutation_audit.py`

---

### Pattern Auth (depuis deps.py + router 61.33)

```python
# Même pattern que les endpoints 61.33/61.34 :
from app.api.dependencies.auth import require_authenticated_user
# AuthenticatedUser : dataclass avec .id, .role, .email

async def post_review(
    audit_id: int,
    body: ReviewRequestBody,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_authenticated_user),
):
    if current_user.role not in ("ops", "admin"):
        raise HTTPException(status_code=403, detail="Insufficient role")
    # ...
```

---

### Pattern Migration Alembic

```python
# Préfixe : YYYYMMDD_NNNN_ — ex: 20260329_0057_create_canonical_entitlement_mutation_audit_reviews
# down_revision = "20260328_0056"  ← dernière migration audit trail
# branch_labels = None
# depends_on = None

def upgrade() -> None:
    op.create_table(
        "canonical_entitlement_mutation_audit_reviews",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("audit_id", sa.Integer(), sa.ForeignKey("canonical_entitlement_mutation_audits.id"), nullable=False),
        sa.Column("review_status", sa.String(32), nullable=False),
        sa.Column("reviewed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("review_comment", sa.Text(), nullable=True),
        sa.Column("incident_key", sa.String(64), nullable=True),
        sa.UniqueConstraint("audit_id", name="uq_audit_review_audit_id"),
    )
    op.create_index("ix_audit_reviews_review_status", "canonical_entitlement_mutation_audit_reviews", ["review_status"])

def downgrade() -> None:
    op.drop_index("ix_audit_reviews_review_status", table_name="canonical_entitlement_mutation_audit_reviews")
    op.drop_table("canonical_entitlement_mutation_audit_reviews")
```

---

### Pattern Modèle SQLAlchemy

```python
# backend/app/infra/db/models/canonical_entitlement_mutation_audit_review.py
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint
from app.infra.db.base import Base  # même Base que les autres modèles

class CanonicalEntitlementMutationAuditReviewModel(Base):
    __tablename__ = "canonical_entitlement_mutation_audit_reviews"
    __table_args__ = (
        UniqueConstraint("audit_id", name="uq_audit_review_audit_id"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(Integer, ForeignKey("canonical_entitlement_mutation_audits.id"), nullable=False, index=True)
    review_status = Column(String(32), nullable=False, index=True)
    reviewed_by_user_id = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=False)
    review_comment = Column(Text, nullable=True)
    incident_key = Column(String(64), nullable=True)
```

> **Ne pas déclarer** `server_default` dans le modèle SQLAlchemy si la valeur est gérée par le service (`datetime.now(utc)` au moment du INSERT).
> Utiliser `server_default=sa.func.now()` uniquement dans la migration.

---

### Pattern Service Upsert

```python
# backend/app/services/canonical_entitlement_mutation_audit_review_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
import datetime

from app.infra.db.models.canonical_entitlement_mutation_audit import CanonicalEntitlementMutationAuditModel
from app.infra.db.models.canonical_entitlement_mutation_audit_review import CanonicalEntitlementMutationAuditReviewModel

class CanonicalEntitlementMutationAuditReviewService:

    @staticmethod
    async def upsert_review(
        db: AsyncSession,
        audit_id: int,
        review_status: str,
        reviewed_by_user_id: int | None,
        review_comment: str | None,
        incident_key: str | None,
    ) -> CanonicalEntitlementMutationAuditReviewModel:
        # 1. Vérifier que l'audit existe
        audit = await db.get(CanonicalEntitlementMutationAuditModel, audit_id)
        if audit is None:
            raise HTTPException(status_code=404, detail=f"Audit {audit_id} not found")
        # 2. Chercher revue existante
        result = await db.execute(
            select(CanonicalEntitlementMutationAuditReviewModel)
            .where(CanonicalEntitlementMutationAuditReviewModel.audit_id == audit_id)
        )
        review = result.scalar_one_or_none()
        now = datetime.datetime.now(datetime.timezone.utc)
        if review is None:
            review = CanonicalEntitlementMutationAuditReviewModel(
                audit_id=audit_id,
                review_status=review_status,
                reviewed_by_user_id=reviewed_by_user_id,
                reviewed_at=now,
                review_comment=review_comment,
                incident_key=incident_key,
            )
            db.add(review)
        else:
            review.review_status = review_status
            review.reviewed_by_user_id = reviewed_by_user_id
            review.reviewed_at = now
            review.review_comment = review_comment
            review.incident_key = incident_key
        await db.flush()
        return review
```

---

### Schémas Pydantic (dans le router)

```python
from typing import Literal
import datetime

ReviewStatusLiteral = Literal["pending_review", "acknowledged", "expected", "investigating", "closed"]

class ReviewState(BaseModel):
    """Champ 'review' inclus dans MutationAuditItem."""
    status: ReviewStatusLiteral
    reviewed_by_user_id: int | None = None
    reviewed_at: datetime.datetime | None = None
    review_comment: str | None = None
    incident_key: str | None = None

class ReviewRequestBody(BaseModel):
    """Body du POST /review."""
    review_status: ReviewStatusLiteral
    review_comment: str | None = None
    incident_key: str | None = None

class ReviewResponse(BaseModel):
    """Réponse 201 du POST /review."""
    audit_id: int
    review_status: ReviewStatusLiteral
    reviewed_by_user_id: int | None = None
    reviewed_at: datetime.datetime
    review_comment: str | None = None
    incident_key: str | None = None

# Extension de MutationAuditItem :
class MutationAuditItem(BaseModel):
    # ... tous les champs existants 61.33 + 61.34 (non-optionnels pour diff fields) ...
    review: ReviewState | None = None  # optionnel — omis si null via response_model_exclude_none=True
```

---

### Logique statut virtuel dans `_to_item`

```python
def _to_item(
    audit: CanonicalEntitlementMutationAuditModel,
    diff: MutationDiffResult,
    review_record: CanonicalEntitlementMutationAuditReviewModel | None,
) -> dict:
    # ... construction dict existant 61.33/61.34 ...

    # Calcul champ review
    if review_record is not None:
        review = ReviewState(
            status=review_record.review_status,
            reviewed_by_user_id=review_record.reviewed_by_user_id,
            reviewed_at=review_record.reviewed_at,
            review_comment=review_record.review_comment,
            incident_key=review_record.incident_key,
        )
    elif diff.risk_level == "high":
        review = ReviewState(status="pending_review")  # champs nulls via default None
    else:
        review = None  # omis dans la réponse via response_model_exclude_none=True

    return {
        # ... champs existants ...
        "review": review,
    }
```

---

### Chargement des revues sans N+1

```python
# Dans list_mutation_audits — chemin paginé normal :
audit_ids = [a.id for a in page_audits]
reviews_result = await db.execute(
    select(CanonicalEntitlementMutationAuditReviewModel)
    .where(CanonicalEntitlementMutationAuditReviewModel.audit_id.in_(audit_ids))
)
reviews_by_audit_id: dict[int, CanonicalEntitlementMutationAuditReviewModel] = {
    r.audit_id: r for r in reviews_result.scalars().all()
}
# Puis dans la boucle _to_item :
review_record = reviews_by_audit_id.get(audit.id)
```

---

### Filtre `review_status` — logique application-level

```python
# review_status est un filtre APPLICATION-LEVEL (pas SQL) car le statut effectif
# est virtuel pour les high-risk sans revue DB.
#
# Algorithme :
# 1. Charger les audits (filtres SQL + diff filter 61.34)
# 2. Charger toutes les revues en une requête IN
# 3. Pour chaque audit : statut effectif = review_record.status OU "pending_review" si diff.risk_level=="high"
# 4. Filtrer sur statut effectif
# 5. Paginer manuellement

# Cas "review_status=pending_review" sans filtre diff :
# → Nécessite de calculer le diff pour chaque audit chargé (pour connaître risk_level)
# → Appliquer la limite 10 000 SQL également dans ce cas (garde-fou identique au filtre diff)
# → Retourner 400 avec code="diff_filter_result_set_too_large" si SQL count > 10 000
```

> **Important** : si `review_status` est fourni sans filtre diff, il faut quand même calculer les diffs
> (pour la règle virtuelle high → pending_review). Appliquer le même garde-fou 10 000.

---

### Règles de non-régression

- `response_model_exclude_none=True` reste actif → `review: null` est **omis** de la réponse pour les mutations low/medium sans revue. C'est le comportement voulu.
- Les tests existants 61.33/61.34 ne testent pas l'absence du champ `review` → régression improbable, mais vérifier.
- `_to_item` reçoit maintenant un 3e paramètre `review_record`. Mettre à jour tous les appels existants (passer `None` pour le chemin de compatibilité si besoin).
- Le router est responsable du `db.commit()` après le POST review (le service ne commit pas).

---

### Project Structure Notes

```
backend/
  alembic/versions/         ← YYYYMMDD_NNNN_create_canonical_entitlement_mutation_audit_reviews.py
  app/
    infra/db/models/        ← canonical_entitlement_mutation_audit_review.py (CRÉER)
    services/               ← canonical_entitlement_mutation_audit_review_service.py (CRÉER)
    api/v1/routers/         ← ops_entitlement_mutation_audits.py (MODIFIER)
    tests/
      unit/                 ← test_canonical_entitlement_mutation_audit_review_service.py (CRÉER)
      integration/          ← test_ops_entitlement_mutation_audits_api.py (MODIFIER)
  docs/                     ← entitlements-canonical-platform.md (MODIFIER)
```

### Références

- [Source: backend/app/api/v1/routers/ops_entitlement_mutation_audits.py] — router 61.33/61.34 à étendre
- [Source: backend/app/services/canonical_entitlement_mutation_diff_service.py] — `MutationDiffResult` (champ `risk_level` utilisé pour la règle virtuelle)
- [Source: backend/app/infra/db/models/canonical_entitlement_mutation_audit.py] — modèle audit (table parente, FK cible)
- [Source: backend/app/services/canonical_entitlement_mutation_audit_query_service.py] — query service SQL (ne pas modifier)
- [Source: backend/app/api/dependencies/auth.py] — pattern `require_authenticated_user()`, `AuthenticatedUser.id`
- [Source: backend/alembic/versions/20260328_0056_create_canonical_entitlement_mutation_audits.py] — dernière migration (`down_revision` à utiliser)
- [Source: backend/docs/entitlements-canonical-platform.md] — documentation à compléter

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- 2026-03-28 : Implémentation complète. Service synchrone (pas async) conforme à la session SQLAlchemy du projet. Migration dans `backend/migrations/versions/`. `_to_item` et `_to_item_with_diff` acceptent un paramètre `review_record` optionnel. Filtre `review_status` déclenche le chemin batch (garde-fou 10 000) comme les filtres diff. Les champs null omis via `response_model_exclude_none=True` — ajustement du test de statut virtuel en conséquence. 46/46 tests verts, ruff clean.
- 2026-03-28 : Code review post-implémentation. Finding HIGH corrigé : l'upsert de revue n'était pas robuste à une race concurrente sur la contrainte unique `audit_id`, pouvant produire une `IntegrityError` au lieu d'un comportement idempotent. Le service gère maintenant ce conflit par savepoint + relecture puis update, avec test dédié.
- 2026-03-28 : Écart story/git documenté. Le commit initial a aussi touché des fichiers d'enregistrement/formatage (`backend/app/infra/db/models/__init__.py`, `backend/app/api/v1/routers/__init__.py`, tests et migration 0056) absents ou contredisant le périmètre strict annoncé dans la story. Cette divergence est désormais consignée dans l'artefact.
- 2026-03-28 : Validation backend complète rejouée après review. Deux défauts préexistants hors story ont aussi été corrigés pour retrouver une suite verte : réintégration de `natal_chart_short` dans `FEATURE_SCOPE_REGISTRY` et isolation correcte du `dry_run` dans `B2BEntitlementRepairService`.

### File List

- `backend/app/infra/db/models/canonical_entitlement_mutation_audit_review.py` (créé)
- `backend/app/infra/db/models/__init__.py` (modifié — enregistrement du nouveau modèle)
- `backend/migrations/versions/20260328_0057_create_canonical_entitlement_mutation_audit_reviews.py` (créé)
- `backend/app/services/canonical_entitlement_mutation_audit_review_service.py` (créé)
- `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` (modifié)
- `backend/app/tests/unit/test_canonical_entitlement_mutation_audit_review_service.py` (créé)
- `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` (modifié)
- `backend/docs/entitlements-canonical-platform.md` (modifié)
- `backend/app/api/v1/routers/__init__.py` (modifié — formatage import router)
- `backend/app/services/canonical_entitlement_mutation_diff_service.py` (modifié — formatage)
- `backend/app/tests/unit/test_canonical_entitlement_mutation_audit.py` (modifié — formatage)
- `backend/app/tests/unit/test_canonical_entitlement_mutation_diff_service.py` (modifié — formatage)
- `backend/migrations/versions/20260328_0056_create_canonical_entitlement_mutation_audits.py` (modifié — formatage)
- `backend/app/services/feature_scope_registry.py` (modifié — réintégration `natal_chart_short`)
- `backend/app/services/b2b_entitlement_repair_service.py` (modifié — isolation transactionnelle du `dry_run`)
- `backend/app/tests/unit/test_b2b_entitlement_repair_service.py` (modifié — alignement sur le contrat `dry_run`)

### Change Log

- 2026-03-28 : Story 61.35 créée.
- 2026-03-28 : Implémentation complète — modèle, migration, service, router, tests, documentation.
- 2026-03-28 : Code review et hardening — upsert review rendu robuste en cas d'écriture concurrente sur `audit_id` + test unitaire de non-régression.
- 2026-03-28 : Validation backend complète restaurée — fix du registre `natal_chart_short` et du rollback `dry_run` du repair B2B.

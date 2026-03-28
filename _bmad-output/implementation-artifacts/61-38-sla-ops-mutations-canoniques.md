# Story 61.38 : SLA ops et escalade des mutations canoniques à risque

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux que chaque item de la review queue affiche explicitement son statut SLA (dans les temps, bientôt dû, en retard), ainsi que des compteurs d'escalade dans le résumé,
afin de prioriser immédiatement les items critiques sans avoir à calculer manuellement les délais de traitement.

## Contexte

61.37 a livré la work queue ops avec tri par priorité métier et résumé chiffré. La queue reste cependant **descriptive** : elle liste les items, mais ne formule pas d'urgence explicite. Un opérateur doit encore calculer mentalement si un item vieux de 3h est « acceptable » pour du `high+pending_review` (SLA 4h) ou non.

**Cette story ajoute la couche SLA** — entièrement calculée à la volée, sans écriture DB ni migration Alembic.

**Architecture** : 100 % read-only. Toute la logique SLA est injectée dans `_to_queue_item()` et `_build_filtered_review_queue_rows()` existants. Aucun nouveau service, aucune nouvelle table.

**Règles SLA** (définies comme constantes dans le router) :

| Combinaison | `sla_target_seconds` | `due_soon` si restant < |
|---|---|---|
| `high` + `pending_review` | 14 400 (4h) | 2 880s (48 min) |
| `high` + `investigating` | 86 400 (24h) | 17 280s (4h48) |
| `medium` + `pending_review` ou `None` | 86 400 (24h) | 17 280s (4h48) |
| tout autre cas | `None` (hors SLA) | — |

> `due_soon` : `due_soon_threshold_seconds = int(sla_target_seconds * 0.20)`. Règle déterministe :
> - `remaining_seconds <= 0` → **overdue**
> - `0 < remaining_seconds < due_soon_threshold_seconds` → **due_soon**
> - `remaining_seconds >= due_soon_threshold_seconds` → **within_sla**
>
> `remaining_seconds = 0` tombe donc systématiquement dans **overdue**, jamais dans **due_soon**.

**Flux ops complet** : détection (`risk_level`) → consultation (61.33) → qualification (61.35 POST) → historique (61.36 GET) → work queue (61.37 GET) → **SLA escalade (61.38 GET)**.

**Step suivant** : 61.39 — alerting/notifications ops sur les items `overdue` ou `due_soon` (nécessite que 61.38 normalise d'abord la notion de retard).

---

## Acceptance Criteria

### AC 1 — Nouveaux champs dérivés SLA dans `ReviewQueueItem`

1. `ReviewQueueItem` est étendu avec 4 champs supplémentaires (tous `None` si hors SLA) :
   - `sla_target_seconds: int | None = None` — durée SLA cible en secondes ; `None` si la combinaison `risk_level`/`eff_status` est hors SLA.
   - `due_at: datetime | None = None` — `occurred_at + timedelta(seconds=sla_target_seconds)` ; `None` si hors SLA.
   - `sla_status: Literal["within_sla", "due_soon", "overdue"] | None = None` — `None` si hors SLA ; **omis de la réponse JSON** via `exclude_none=True`.
   - `overdue_seconds: int | None = None` — `int(age_seconds - sla_target_seconds)` si `sla_status == "overdue"`, sinon `None`.
2. `occurred_at` est **toujours normalisé en UTC aware** avant tout calcul SLA (`replace(tzinfo=timezone.utc)` si naive). `due_at` est en conséquence **toujours renvoyé en UTC aware**.
3. `response_model_exclude_none=True` reste actif : `sla_target_seconds`, `due_at`, `sla_status`, `overdue_seconds` sont **omis** de la réponse JSON quand `None`.

### AC 2 — Helper `_compute_sla()` (fonction pure)

4. Un helper **privé** `_compute_sla(risk_level: str, eff_status: str | None, occurred_at: datetime, now_utc: datetime)` est créé dans le router.
5. Il retourne un `dict` avec les 4 clés SLA : `sla_target_seconds`, `due_at`, `sla_status`, `overdue_seconds`.
6. Logique interne :
   ```
   # occurred_at normalisé en UTC aware AVANT tout calcul
   if occurred_at.tzinfo is None:
       occurred_at = occurred_at.replace(tzinfo=timezone.utc)

   target = _SLA_TARGETS.get((risk_level, eff_status))  # None si hors SLA
   if target is None:
       return {sla_target_seconds: None, due_at: None, sla_status: None, overdue_seconds: None}

   due_soon_threshold = int(target * 0.20)
   age_s = int((now_utc - occurred_at).total_seconds())
   remaining = target - age_s

   if remaining <= 0:
       sla_status = "overdue"
       overdue_s = abs(remaining)   # toujours positif
   elif remaining < due_soon_threshold:
       sla_status = "due_soon"
       overdue_s = None
   else:
       sla_status = "within_sla"
       overdue_s = None

   due_at = occurred_at + timedelta(seconds=target)  # toujours UTC aware
   ```
7. La constante `SLA_TARGETS` est déclarée au niveau module (pas dans la fonction), adjacent à `_STATUS_PRIORITY`.

### AC 3 — Intégration dans `_to_queue_item()`

8. `_to_queue_item()` appelle `_compute_sla(diff.risk_level, eff_status, occurred_at_utc, now_utc)` et merge le résultat dans le dict retourné.
9. `_to_queue_item()` ne reçoit **pas** de nouveau paramètre — `diff.risk_level` est déjà disponible via le paramètre `diff` existant.
10. La signature de `_to_queue_item()` reste compatible avec les appels existants dans les deux endpoints.

### AC 4 — Nouveau filtre `sla_status` dans la review queue

11. `GET /v1/ops/entitlements/mutation-audits/review-queue` accepte un nouveau paramètre optionnel :
    - `sla_status_filter: Literal["within_sla", "due_soon", "overdue"] | None = Query(default=None, alias="sla_status")`
12. Le filtre est **applicatif post-SLA** : il s'applique **après** le calcul de `effective_review_status`, `risk_level` et des champs SLA (via `_to_queue_item()`), et **avant** la pagination. Séquence impérative : `_build_filtered_review_queue_rows()` → `_to_queue_item()` pour chaque row → filtre `sla_status` → `total_count = len(filtered)` → pagination.
13. `GET /v1/ops/entitlements/mutation-audits/review-queue/summary` accepte le **même filtre** `sla_status` (sans `page`/`page_size`). Quand `sla_status` est fourni, **tous** les compteurs du résumé (`total_count`, `overdue_count`, `due_soon_count`, `pending_review_count`, `oldest_pending_age_seconds`, etc.) portent exclusivement sur le sous-ensemble d'items dont le `sla_status` calculé correspond au filtre.

### AC 5 — Enrichissement du résumé (`ReviewQueueSummaryData`)

14. `ReviewQueueSummaryData` est étendu avec 3 nouveaux champs :
    - `overdue_count: int` — nombre d'items avec `sla_status == "overdue"`.
    - `due_soon_count: int` — nombre d'items avec `sla_status == "due_soon"`.
    - `oldest_pending_age_seconds: int | None` — `age_seconds` du plus ancien item avec `effective_review_status == "pending_review"` ; `None` si aucun item `pending_review` dans les résultats filtrés.
15. Ces champs sont **toujours présents** dans la réponse JSON (valeurs numériques, pas `None` pour `overdue_count` et `due_soon_count`), sauf `oldest_pending_age_seconds` qui peut être `None` et est omis via `exclude_none=True`.
16. L'endpoint summary retourne donc :
    ```json
    {
      "data": {
        "pending_review_count": 5,
        "investigating_count": 2,
        "acknowledged_count": 3,
        "closed_count": 10,
        "expected_count": 1,
        "no_review_count": 4,
        "high_unreviewed_count": 5,
        "total_count": 25,
        "overdue_count": 2,
        "due_soon_count": 1,
        "oldest_pending_age_seconds": 18400
      },
      "meta": { "request_id": "..." }
    }
    ```

### AC 6 — Schémas Pydantic mis à jour

17. `ReviewQueueItem` (étendu) :
    ```python
    class ReviewQueueItem(MutationAuditItem):
        effective_review_status: ReviewStatusLiteral | None = None
        age_seconds: int
        age_hours: float
        is_pending: bool
        is_closed: bool
        # Nouveaux champs SLA
        sla_target_seconds: int | None = None
        due_at: datetime | None = None
        sla_status: Literal["within_sla", "due_soon", "overdue"] | None = None
        overdue_seconds: int | None = None
    ```
18. `ReviewQueueSummaryData` (étendu) :
    ```python
    class ReviewQueueSummaryData(BaseModel):
        pending_review_count: int
        investigating_count: int
        acknowledged_count: int
        closed_count: int
        expected_count: int
        no_review_count: int
        high_unreviewed_count: int
        total_count: int
        # Nouveaux champs SLA
        overdue_count: int
        due_soon_count: int
        oldest_pending_age_seconds: int | None = None
    ```

### AC 7 — Périmètre strict

19. `canonical_entitlement_mutation_audit_query_service.py` — **non modifié**.
20. `canonical_entitlement_mutation_audit_review_service.py` — **non modifié**.
21. `canonical_entitlement_mutation_diff_service.py` — **non modifié**.
22. Tous les modèles SQLAlchemy — **non modifiés**.
23. Pas de migration Alembic.
24. Fichiers modifiés : uniquement `ops_entitlement_mutation_audits.py`, `test_ops_entitlement_mutation_audits_api.py`, `entitlements-canonical-platform.md`.

### AC 8 — Tests d'intégration

25. `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` enrichi avec :
    - `test_review_queue_sla_within_sla_high_pending` — audit `high+pending_review` créé à l'instant → `sla_status="within_sla"`, `sla_target_seconds=14400`, `due_at` présent, `overdue_seconds` absent
    - `test_review_queue_sla_overdue_high_pending` — audit `high+pending_review` avec `occurred_at = now - 5h` → `sla_status="overdue"`, `overdue_seconds >= 3600`
    - `test_review_queue_sla_due_soon_high_pending` — audit `high+pending_review` avec `occurred_at = now - 3h40` (restant ≈ 20min < 48min) → `sla_status="due_soon"`
    - `test_review_queue_sla_null_for_low_risk` — audit `low` risk → `sla_target_seconds` absent, `sla_status` absent
    - `test_review_queue_sla_null_for_closed` — audit `high+closed` → `sla_target_seconds` absent
    - `test_review_queue_filter_by_sla_status_overdue` — filtre `sla_status=overdue` ne retourne que les items overdue
    - `test_review_queue_summary_overdue_count` — 1 overdue + 1 within_sla → `overdue_count=1`, `due_soon_count=0`
    - `test_review_queue_summary_oldest_pending_age_seconds` — 1 pending vieux de >0s → `oldest_pending_age_seconds >= 0`
    - `test_review_queue_summary_oldest_pending_none_when_no_pending` — aucun pending → `oldest_pending_age_seconds` absent du JSON
26. Les 66 tests existants (61.35 + 61.36 + 61.37) restent **tous verts**.

### AC 9 — Documentation

27. `backend/docs/entitlements-canonical-platform.md` mis à jour avec section **"Story 61.38 — SLA ops"** décrivant :
    - Les règles SLA (tableau `SLA_TARGETS`).
    - Les 4 champs dérivés SLA et leur logique de calcul.
    - Le filtre `sla_status`.
    - Les 3 nouveaux champs du summary (`overdue_count`, `due_soon_count`, `oldest_pending_age_seconds`).

---

## Tasks / Subtasks

- [x] **Constante `SLA_TARGETS` + helper `_compute_sla()`** (AC: 2, 7)
  - [x] Déclarer `SLA_TARGETS: dict[tuple[str, str | None], int]` adjacent à `_STATUS_PRIORITY`
  - [x] Implémenter `_compute_sla(risk_level, eff_status, occurred_at, now_utc)` — retourne dict 4 clés
  - [x] Gérer `occurred_at` naive → normalisation UTC (`replace(tzinfo=timezone.utc)`)

- [x] **Étendre `ReviewQueueItem` avec les 4 champs SLA** (AC: 1, 6)
  - [x] Ajouter `sla_target_seconds`, `due_at`, `sla_status`, `overdue_seconds` avec `None` par défaut

- [x] **Étendre `ReviewQueueSummaryData` avec les 3 champs SLA** (AC: 5, 6)
  - [x] Ajouter `overdue_count`, `due_soon_count`, `oldest_pending_age_seconds`

- [x] **Intégrer `_compute_sla()` dans `_to_queue_item()`** (AC: 3)
  - [x] Appeler `_compute_sla(diff.risk_level, eff_status, occurred_at_utc, now_utc)` et merger dans le dict
  - [x] Vérifier que `diff` est bien accessible dans `_to_queue_item()` (paramètre existant)

- [x] **Ajouter le filtre `sla_status` dans les deux endpoints** (AC: 4)
  - [x] `review-queue` : nouveau `Query` param `sla_status_filter` avec alias `"sla_status"`
  - [x] `review-queue/summary` : même param (sans `page`/`page_size`)
  - [x] Filtre applicatif post-calcul SLA : exclure les items dont `sla_status != sla_status_filter`

- [x] **Enrichir l'agrégation summary** (AC: 5)
  - [x] Calculer `overdue_count`, `due_soon_count` sur les rows filtrées
  - [x] Calculer `oldest_pending_age_seconds` = max(`age_seconds`) des items `pending_review` (ou `None`)

- [x] **Tests d'intégration** (AC: 8)
  - [x] Ajouter `occurred_at` paramètre dans `_seed_audit()` si non existant (nécessaire pour simuler items anciens)
  - [x] Écrire les 9 nouveaux tests listés en AC 8

- [x] **Documentation** (AC: 9)
  - [x] Section 61.38 dans `backend/docs/entitlements-canonical-platform.md`

- [x] **Validation finale**
  - [x] `ruff check` — zéro erreur
  - [x] `pytest -q` backend complet — tous verts
  - [x] Vérifier baseline : 66 tests existants + 9 nouveaux = **75 tests** minimum

---

## Dev Notes

### Fichiers à modifier

| Fichier | Action |
|---------|--------|
| `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` | Modifier |
| `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` | Modifier (+9 tests) |
| `backend/docs/entitlements-canonical-platform.md` | Modifier |

**Aucun autre fichier.** Pas de migration Alembic, pas de nouveau service, pas de nouveau modèle.

---

### Constante `SLA_TARGETS` — position dans le fichier

Déclarer adjacent à `_STATUS_PRIORITY` (déjà en haut du module) :

```python
_STATUS_PRIORITY: dict[str | None, int] = {
    "pending_review": 0,
    "investigating": 1,
    "acknowledged": 2,
    "expected": 3,
    "closed": 4,
    None: 5,
}

# Durées SLA en secondes. Clé = (risk_level, effective_review_status).
# Toute combinaison absente est hors SLA (sla_target = None).
_SLA_TARGETS: dict[tuple[str, str | None], int] = {
    ("high", "pending_review"): 14_400,   # 4h
    ("high", "investigating"):  86_400,   # 24h
    ("medium", "pending_review"): 86_400, # 24h
    ("medium", None): 86_400,             # 24h (medium sans revue)
}
_SLA_DUE_SOON_RATIO = 0.20  # due_soon si remaining < 20% du SLA
```

---

### Helper `_compute_sla()` — implémentation type

```python
from datetime import timedelta

def _compute_sla(
    risk_level: str,
    eff_status: str | None,
    occurred_at: datetime,
    now_utc: datetime,
) -> dict[str, Any]:
    """Retourne les 4 champs SLA pour un item de la review queue."""
    # Normalisation timezone
    if occurred_at.tzinfo is None:
        occurred_at = occurred_at.replace(tzinfo=timezone.utc)

    target = _SLA_TARGETS.get((risk_level, eff_status))
    if target is None:
        return {
            "sla_target_seconds": None,
            "due_at": None,
            "sla_status": None,
            "overdue_seconds": None,
        }

    age_s = int((now_utc - occurred_at).total_seconds())
    remaining = target - age_s
    due_soon_threshold = int(target * _SLA_DUE_SOON_RATIO)
    due_at = occurred_at + timedelta(seconds=target)  # toujours UTC aware

    if remaining <= 0:
        sla_status = "overdue"
        overdue_s = abs(remaining)  # toujours positif ; remaining==0 → overdue(0)
    elif remaining < due_soon_threshold:
        sla_status = "due_soon"
        overdue_s = None
    else:
        sla_status = "within_sla"
        overdue_s = None

    return {
        "sla_target_seconds": target,
        "due_at": due_at,
        "sla_status": sla_status,
        "overdue_seconds": overdue_s,
    }
```

---

### Intégration dans `_to_queue_item()`

```python
def _to_queue_item(
    audit: Any,
    *,
    diff: Any,
    review_record: CanonicalEntitlementMutationAuditReviewModel | None,
    eff_status: str | None,
    now_utc: datetime,
) -> dict[str, Any]:
    base = _to_item_with_diff(audit, diff=diff, include_payloads=False, review_record=review_record)
    occurred_at = audit.occurred_at
    if occurred_at.tzinfo is None:
        occurred_at = occurred_at.replace(tzinfo=timezone.utc)
    age_seconds = int((now_utc - occurred_at).total_seconds())
    sla_fields = _compute_sla(diff.risk_level, eff_status, occurred_at, now_utc)
    return {
        **base,
        "effective_review_status": eff_status,
        "age_seconds": age_seconds,
        "age_hours": round(age_seconds / 3600, 2),
        "is_pending": eff_status == "pending_review",
        "is_closed": eff_status == "closed",
        **sla_fields,
    }
```

> **Note** : `diff.risk_level` est déjà présent dans `_to_queue_item()` via le paramètre `diff`. Pas de changement de signature.

---

### Filtre `sla_status` — position dans le pipeline

Le filtre `sla_status` est **applicatif post-SLA** : il ne peut pas être appliqué dans `_build_filtered_review_queue_rows()` car ce helper ne calcule pas les champs SLA (il retourne des tuples `(audit, diff, review_record, eff_status)`).

**Option recommandée** : appliquer le filtre dans les endpoints, après la boucle qui construit les items SLA, avant la pagination. Exemple dans `get_review_queue` :

```python
rows = _build_filtered_review_queue_rows(...)
if isinstance(rows, JSONResponse):
    return rows

rows.sort(key=lambda x: (_STATUS_PRIORITY.get(x[3], 5), x[0].occurred_at))
now_utc = datetime.now(timezone.utc)
all_items = [
    _to_queue_item(item, diff=diff, review_record=rev, eff_status=eff, now_utc=now_utc)
    for item, diff, rev, eff in rows
]
if sla_status_filter is not None:
    all_items = [i for i in all_items if i.get("sla_status") == sla_status_filter]
total_count = len(all_items)
start = (page - 1) * page_size
return {
    "data": {
        "items": all_items[start : start + page_size],
        "total_count": total_count,
        ...
    }
}
```

**Alternative** : passer `sla_status_filter` à `_build_filtered_review_queue_rows()` — mais cela force à calculer le SLA dans ce helper, ce qui crée un couplage. L'option ci-dessus est plus propre.

---

### Enrichissement du summary — agrégation SLA

```python
rows = _build_filtered_review_queue_rows(...)
if isinstance(rows, JSONResponse):
    return rows

counts: dict[str, int] = {}
high_unreviewed = 0
overdue_count = 0
due_soon_count = 0
oldest_pending_age: int | None = None
now_utc = datetime.now(timezone.utc)

for audit, diff, review_record, eff_status in rows:
    # Compteurs existants
    key = eff_status if eff_status is not None else "none"
    counts[key] = counts.get(key, 0) + 1
    if diff.risk_level == "high" and eff_status == "pending_review":
        high_unreviewed += 1
    # Nouveaux compteurs SLA
    occurred_at = audit.occurred_at
    if occurred_at.tzinfo is None:
        occurred_at = occurred_at.replace(tzinfo=timezone.utc)
    sla = _compute_sla(diff.risk_level, eff_status, occurred_at, now_utc)
    if sla["sla_status"] == "overdue":
        overdue_count += 1
    elif sla["sla_status"] == "due_soon":
        due_soon_count += 1
    if eff_status == "pending_review":
        age_s = int((now_utc - occurred_at).total_seconds())
        if oldest_pending_age is None or age_s > oldest_pending_age:
            oldest_pending_age = age_s

# Filtre sla_status (si passé au summary)
if sla_status_filter is not None:
    # Recalculer les rows après filtrage (ou filtrer la liste déjà itérée)
    # Solution la plus simple : recalculer overdue/due_soon counts après filtrage
    pass  # voir note ci-dessous
```

> **Note filtre summary + sla_status** : si `sla_status_filter` est fourni, les compteurs `overdue_count`, `due_soon_count`, `total_count`, etc. doivent tous porter sur les items qui passent le filtre. La façon la plus simple : construire d'abord `list[dict]` des items SLA, filtrer, puis agréger les compteurs sur la liste filtrée. Éviter de dupliquer `_compute_sla` — préférer itérer une seule fois.

---

### Tests d'intégration — seed avec `occurred_at` personnalisé

Pour simuler des items overdue ou due_soon, il faut insérer des audits avec `occurred_at` dans le passé. Vérifier si `_seed_audit()` accepte déjà `occurred_at` ; sinon, l'étendre.

Exemple de seed pour un item overdue (high+pending_review, vieux de 5h) :

```python
from datetime import datetime, timedelta, timezone

with SessionLocal() as db:
    _seed_audit(
        db,
        before_payload={},
        after_payload={"is_enabled": True, "access_mode": "quota", "quotas": []},
        occurred_at=datetime.now(timezone.utc) - timedelta(hours=5),
    )
    db.commit()
```

Pour due_soon (restant < 48min pour SLA 4h → age > 3h12 = 11520s) :
```python
occurred_at=datetime.now(timezone.utc) - timedelta(seconds=11_600),  # ~3h13
```

---

### Baseline tests (avant 61.38)

- 61.35 : 46 tests
- 61.36 : +8 tests → 54 total
- 61.37 : +12 tests → **66 tests** au total
- 61.38 : +9 tests → **75 tests** attendus après

---

### Imports additionnels

```python
from datetime import timedelta  # pour due_at = occurred_at + timedelta(seconds=target)
```

`timedelta` est probablement déjà importé via `from datetime import datetime, timezone` — à vérifier et compléter si besoin.

---

### Project Structure Notes

```
backend/
  app/
    api/v1/routers/
      ops_entitlement_mutation_audits.py  ← MODIFIER
        Ajouter/modifier dans cet ordre :
          1. Import timedelta (si absent)
          2. Constante _SLA_TARGETS + _SLA_DUE_SOON_RATIO (adjacent à _STATUS_PRIORITY)
          3. Helper _compute_sla()
          4. Schéma ReviewQueueItem : +4 champs SLA
          5. Schéma ReviewQueueSummaryData : +3 champs SLA
          6. _to_queue_item() : appel _compute_sla() + merge
          7. get_review_queue() : +param sla_status_filter, filtre post-items
          8. get_review_queue_summary() : +param sla_status_filter, +agrégation SLA
    tests/integration/
      test_ops_entitlement_mutation_audits_api.py  ← MODIFIER (+9 tests)
  docs/
    entitlements-canonical-platform.md  ← MODIFIER
```

**NE PAS modifier** :
- `canonical_entitlement_mutation_audit_query_service.py`
- `canonical_entitlement_mutation_audit_review_service.py`
- `canonical_entitlement_mutation_diff_service.py`
- Tout modèle SQLAlchemy sous `infra/db/models/`
- Pas de migration Alembic

---

### Références

- [Source: backend/app/api/v1/routers/ops_entitlement_mutation_audits.py] — `_STATUS_PRIORITY`, `_to_queue_item`, `_build_filtered_review_queue_rows`, `ReviewQueueItem`, `ReviewQueueSummaryData`, `get_review_queue`, `get_review_queue_summary`
- [Source: backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py] — `_seed_audit`, `_cleanup_tables`, `_register_user_with_role_and_token` (patterns à réutiliser tels quels)
- [Source: backend/docs/entitlements-canonical-platform.md] — section 61.37 à compléter avec 61.38
- [Story 61.37](61-37-work-queue-ops-mutations-canoniques.md) — source de `ReviewQueueItem`, `ReviewQueueSummaryData`, `_to_queue_item`, `_build_filtered_review_queue_rows` tels qu'implémentés

---

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

### Completion Notes List

- Implémentation du moteur de calcul SLA dans `ops_entitlement_mutation_audits.py`.
- Support des filtres `sla_status` dans la review queue et le summary.
- Extension des modèles Pydantic pour inclure les métriques SLA et l'âge du plus vieux dossier.
- Ajout de tests d'intégration couvrant tous les ACs.

### File List

- `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py`
- `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py`
- `backend/docs/entitlements-canonical-platform.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-03-28 : Story 61.38 créée.
- 2026-03-28 : Implémentation complète et tests validés.

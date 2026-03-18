# Story 60.2 : Introduire les scores publics sur 10 sans casser le moteur interne

Status: review

## Story

En tant qu'utilisateur grand public,
je veux voir mes scores de domaine affichés sur 10 avec un niveau lisible (favorable, stable, exigeant…),
afin de comprendre d'un coup d'œil quels domaines sont soutenus sans avoir à décoder une note sur 20.

## Acceptance Criteria

1. Chaque `PublicDomainEntry` dans le payload expose `score_10: float` (arrondi 1 décimale), `level: str`, `rank: int`.
2. `score_10` est dérivé de `note_20` du domaine public agrégé (Story 60.1) par la formule : `score_10 = round(note_20 / 2, 1)`.
3. Les 5 niveaux (`level`) sont :
   - `"très_favorable"` — score_10 ∈ [9.0, 10.0]
   - `"favorable"` — score_10 ∈ [7.5, 8.9]
   - `"stable"` — score_10 ∈ [6.0, 7.4]
   - `"mitigé"` — score_10 ∈ [4.5, 5.9]
   - `"exigeant"` — score_10 ∈ [0.0, 4.4]
4. `rank` classe les domaines publics par `score_10` décroissant (1 = meilleur).
5. Le score interne `note_20` est CONSERVÉ dans le payload (rétrocompatibilité).
6. Aucune logique de calcul de niveau ou de rang ne se trouve dans le code frontend.
7. Un champ optionnel `signal_label: str | None` peut être présent (ex: "en hausse", "pic") — `None` par défaut.
8. Tests unitaires couvrent tous les seuils (frontières incluses).
9. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [x] T1 — Créer `backend/app/prediction/public_score_mapper.py` (AC: 2, 3, 4)
  - [x] T1.1 Implémenter `to_score_10(note_20: float) -> float` → `round(note_20 / 2, 1)`
  - [x] T1.2 Implémenter `to_level(score_10: float) -> str` avec les 5 seuils
  - [x] T1.3 Implémenter `rank_domains(domains: list[PublicDomainScore]) -> list[PublicDomainScore]` — tri décroissant, rank 1-based
  - [x] T1.4 Définir dataclass `PublicDomainScore` : `key, label, score_10, level, rank, signal_label, note_20_internal`

- [x] T2 — Brancher dans `PublicPredictionAssembler` (AC: 1, 5)
  - [x] T2.1 Après agrégation publique (Story 60.1), appeler `to_score_10()` et `to_level()` pour chaque domaine public
  - [x] T2.2 Appeler `rank_domains()` pour calculer les rangs
  - [x] T2.3 Inclure dans la réponse `domain_ranking: list[PublicDomainScore]`
  - [x] T2.4 Conserver `categories: list[DailyPredictionCategory]` inchangé (note_20 présent)

- [x] T3 — Mettre à jour les DTOs Pydantic (AC: 6)
  - [x] T3.1 Dans `backend/app/api/v1/routers/predictions.py`, créer `DailyPredictionPublicDomainScore(BaseModel)` :
    ```python
    key: str
    label: str
    score_10: float
    level: str
    rank: int
    signal_label: str | None = None
    note_20_internal: float  # rétrocompat
    ```
  - [x] T3.2 Ajouter `domain_ranking: list[DailyPredictionPublicDomainScore] | None = None` dans `DailyPredictionResponse`

- [x] T4 — Tests unitaires (AC: 8)
  - [x] T4.1 Test : `to_score_10(20.0)` → `10.0`
  - [x] T4.2 Test : `to_score_10(0.0)` → `0.0`
  - [x] T4.3 Test : `to_score_10(15.0)` → `7.5` (frontière favorable)
  - [x] T4.4 Test : `to_level(9.0)` → `"très_favorable"` (frontière basse)
  - [x] T4.5 Test : `to_level(7.5)` → `"favorable"` (frontière basse)
  - [x] T4.6 Test : `to_level(6.0)` → `"stable"` (frontière basse)
  - [x] T4.7 Test : `to_level(4.5)` → `"mitigé"` (frontière basse)
  - [x] T4.8 Test : `to_level(4.4)` → `"exigeant"` (frontière haute)
  - [x] T4.9 Test : `rank_domains([...])` — les rangs sont 1-based et en ordre décroissant
  - [x] T4.10 Test : `rank_domains([])` → `[]` sans erreur

## Dev Notes

### Formule de projection
Le moteur interne utilise `note_20` ∈ [0, 20] (calibré par percentile). La division simple par 2 donne [0, 10]. Pas de recalibration supplémentaire nécessaire car `note_20` est déjà sur une distribution linéarisée.

### Seuils (AC3) — implémentation Python
```python
def to_level(score_10: float) -> str:
    if score_10 >= 9.0:
        return "très_favorable"
    elif score_10 >= 7.5:
        return "favorable"
    elif score_10 >= 6.0:
        return "stable"
    elif score_10 >= 4.5:
        return "mitigé"
    else:
        return "exigeant"
```

### Champ note_20 agrégé (domaine public)
Story 60.1 produit déjà un score agrégé (max des domaines internes). Ce score est `note_20_public`. C'est lui qui est divisé par 2, pas le `note_20` d'un domaine interne spécifique.

### PublicPredictionAssembler — pipeline complet Stories 60.1 + 60.2
1. `PublicCategoryPolicy.build()` → scores internes par catégorie
2. `aggregate_public_domain_score()` (60.1) → scores publics agrégés
3. `to_score_10() + to_level()` (60.2) → projection publique
4. `rank_domains()` (60.2) → classement

### Rétrocompatibilité
- `categories` (existant) → inchangé, contient note_20 par domaine interne
- `domain_ranking` (nouveau) → contient score_10 par domaine public

### Project Structure Notes
- Nouveau fichier: `backend/app/prediction/public_score_mapper.py`
- Modification: `backend/app/prediction/public_projection.py`
- Modification: `backend/app/api/v1/routers/predictions.py` (nouveau DTO)
- Dépend de: Story 60.1 (public_domain_taxonomy.py)

### References
- [Source: backend/app/prediction/calibrator.py] — calibration note_20 (ne pas modifier)
- [Source: backend/app/prediction/public_projection.py] — point d'injection
- [Source: backend/app/api/v1/routers/predictions.py] — DailyPredictionResponse
- [Source: _bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/prediction/public_score_mapper.py` (NEW)
- `backend/app/prediction/public_projection.py` (MOD)
- `backend/app/api/v1/routers/predictions.py` (MOD)
- `backend/tests/unit/prediction/test_public_score_mapper.py` (NEW)

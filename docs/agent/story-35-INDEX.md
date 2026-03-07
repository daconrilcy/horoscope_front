# Epic 35 — Persistance, explicabilité et audit

## Vue d'ensemble

L'epic 35 ferme la boucle du moteur de calcul : il branche le moteur sur les repositories DB existants, fournit la traçabilité des notes jusqu'aux événements contributeurs, verrouille le déterminisme par tests de non-régression, et prépare la couche éditoriale pour la future synthèse LLM.

**Le principe central de cet epic** : le moteur numérique ne rédige jamais de texte libre. Tout ce qu'il produit est dérivé mécaniquement des scores, métriques et pivots. La couche éditoriale future (LLM) exploitera ces sorties structurées sans que le moteur ne la contienne.

---

## Stories

| Story | Titre | Priorité | Dépendances |
|-------|-------|----------|-------------|
| [35-1](./story-35-1-persistence.md) | Persistance du run calculé | P0 | 34-5 |
| [35-2](./story-35-2-explainability.md) | Explicabilité : top contributeurs et mode debug | P0 | 35-1 |
| [35-3](./story-35-3-non-regression.md) | Non-régression et déterminisme moteur | P0 | 35-2 |
| [35-4](./story-35-4-editorial-prep.md) | Préparation de la couche éditoriale dérivée | P1 | 35-2 |

---

## Ordre d'implémentation

```
35-1 → 35-2 → 35-3
              ↓
            35-4
```

`35-3` et `35-4` peuvent être développées en parallèle après `35-2`.

---

## Nouveaux fichiers par story

### 35-1
- `backend/app/prediction/persistence_service.py` ← CRÉER (`PredictionPersistenceService`)
- `backend/app/tests/integration/test_prediction_persistence.py` ← CRÉER

### 35-2
- `backend/app/prediction/explainability.py` ← CRÉER (`ExplainabilityBuilder`)
- `backend/app/tests/unit/test_explainability.py` ← CRÉER

### 35-3
- `backend/app/tests/regression/` ← CRÉER (dossier)
- `backend/app/tests/regression/fixtures/` ← CRÉER (fixtures journée complète)
- `backend/app/tests/regression/test_engine_non_regression.py` ← CRÉER

### 35-4
- `backend/app/prediction/editorial_builder.py` ← CRÉER (`EditorialOutputBuilder`)
- `backend/app/tests/unit/test_editorial_builder.py` ← CRÉER

---

## Décisions figées pour cet epic

1. **Politique `input_hash`** : si hash existant en DB = hash calculé → réutiliser le run, pas de recalcul
2. **Transactionnel** : toutes les écritures (run + scores + pivots + blocs) dans une seule transaction SQLAlchemy
3. **Top contributeurs** : 3 événements max par catégorie, triés par `abs(Contribution)` décroissant
4. **Debug mode** : ne change pas les scores, stockable séparément
5. **Non-régression** : au moins 12 cas types + 2 snapshots complets de journée
6. **Couche éditoriale** : objet structuré dérivé (pas de LLM dans la boucle moteur)

---

## Checklist de validation finale

- [ ] Run créé ou réutilisé selon la politique `input_hash`
- [ ] Scores par catégorie : `raw_score`, `normalized_score`, `note_20`, `power`, `volatility`, `rank`
- [ ] Pivots et blocs persistés après calcul
- [ ] Toutes les écritures transactionnelles
- [ ] Top 3 contributeurs disponibles par catégorie
- [ ] Mode debug on/off sans divergence de scores
- [ ] Tests de non-régression sur ≥ 12 cas types
- [ ] Objet éditorial dérivé sans texte LLM

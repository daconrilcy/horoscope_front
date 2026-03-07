# Epic 34 — Scoring, notes et timeline UX

## Vue d'ensemble

L'epic 34 transforme les événements astrologiques produits par l'epic 33 en scores par catégorie, notes 1–20, blocs horaires et points de bascule. C'est le cœur du moteur : routage domaine, contribution pondérée, agrégation journalière, calibration percentile et génération de la timeline UX.

**Résultat attendu à l'issue de l'epic :** pour chaque catégorie (amour, travail, santé, etc.), une note 1–20 stable, calibrée, accompagnée d'une timeline de blocs horaires et de pivots identifiés.

---

## Stories

| Story | Titre | Priorité | Dépendances |
|-------|-------|----------|-------------|
| [34-1](./story-34-1-domain-routing.md) | Service de routage domaine `D(e,c)` | P0 | 33-2, 33-5 |
| [34-2](./story-34-2-contribution.md) | Service de contribution `Contribution(e,c,t)` | P0 | 33-5, 33-6, 34-1 |
| [34-3](./story-34-3-aggregator.md) | Agrégateur temporel `RawStep` / `RawDay` | P0 | 34-2 |
| [34-4](./story-34-4-calibrator.md) | Calibrateur percentile → note 1–20 | P0 | 34-3 |
| [34-5](./story-34-5-turning-points.md) | Détecteur de points de bascule + blocs UX | P0 | 34-4 |

---

## Ordre d'implémentation

```
34-1 → 34-2 → 34-3 → 34-4 → 34-5
```

Chaîne strictement séquentielle : chaque étape consomme la sortie de la précédente.

---

## Nouveaux fichiers par story

### 34-1
- `backend/app/prediction/domain_router.py` ← CRÉER (`DomainRouter`)
- `backend/app/tests/unit/test_domain_router.py` ← CRÉER

### 34-2
- `backend/app/prediction/contribution_calculator.py` ← CRÉER
- `backend/app/tests/unit/test_contribution_calculator.py` ← CRÉER

### 34-3
- `backend/app/prediction/aggregator.py` ← CRÉER (`TemporalAggregator`)
- `backend/app/tests/unit/test_aggregator.py` ← CRÉER

### 34-4
- `backend/app/prediction/calibrator.py` ← CRÉER (`PercentileCalibrator`)
- `backend/app/tests/unit/test_calibrator.py` ← CRÉER

### 34-5
- `backend/app/prediction/turning_point_detector.py` ← CRÉER
- `backend/app/prediction/block_generator.py` ← CRÉER
- `backend/app/tests/unit/test_turning_points.py` ← CRÉER

---

## Décisions figées pour cet epic

1. **Formule contribution** : `w_event × w_planet × w_aspect × f_orb × f_phase × f_target × NS(c) × D(e,c) × Pol(e,c)`
2. **f_orb** : `1 − (orb/orb_max)^2`, vaut 0 hors orbe
3. **f_phase** : `applying=1.05`, `exact=1.15`, `separating=0.95`
4. **RawDay** : `0.70×Mean + 0.20×Peak90 + 0.10×Close`
5. **Peak90** : fenêtre glissante de 90 minutes
6. **Close** : 2 dernières heures de la journée locale
7. **Pivot** : `ΔNote ≥ 2`, ou top 3 change, ou événement priorité ≥ 65
8. **Blocs UX** : 1 heure par défaut, découpés autour des pivots
9. **Calibration** : percentiles `P5, P25, P50, P75, P95` → cible `2, 6, 10, 14, 19`, saturation `1` et `20`
10. **Politique P5** : note 1 si en-dessous de P5

---

## Checklist de validation finale

- [ ] `D(e,c)` vecteur maison normalisé, blend planétaire dans `[0.5, 1.0]`
- [ ] Contribution hors orbe = 0
- [ ] Contribution bornée dans `[-1, +1]`
- [ ] `RawStep` borné dans `[-3, +3]`
- [ ] `RawDay` formule exacte avec Mean, Peak90, Close
- [ ] Interpolation piecewise linéaire correcte sur les 4 segments percentile
- [ ] Saturation à 1 (sous P5) et 20 (au-dessus de P95)
- [ ] Pivots générés pour `ΔNote ≥ 2`, changement top 3, événement priorité ≥ 65
- [ ] Blocs UX d'1 heure avec découpage adaptatif autour des pivots

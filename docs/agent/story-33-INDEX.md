# Epic 33 — Fondations du moteur de calcul quotidien

## Vue d'ensemble

L'epic 33 pose les fondations du moteur de prédiction astrologique journalier : contrat d'API interne, chargement du contexte de référence, grille temporelle, calcul astronomique intraday, détection d'événements astrologiques et calcul de la sensibilité natale `NS(c)`.

Le périmètre V1 est strict : 10 planètes, Asc/MC, 5 aspects majeurs ptolémaïques, positions géocentriques, maisons Placidus avec repli traçable, pas de 15 minutes, événements `enter_orb`, `exact`, `exit_orb`, `moon_sign_ingress`, `asc_sign_change`, `planetary_hour_change`.

**Résultat attendu à l'issue de l'epic :** un moteur numérique pur, déterministe, sans texte, capable de transformer un thème natal + une journée locale + un contexte de référence en événements calculés et signaux temporels.

---

## Stories

| Story | Titre | Priorité | Dépendances |
|-------|-------|----------|-------------|
| [33-1](./story-33-1-engine-contract.md) | Contrat d'entrée/sortie du moteur + orchestrateur de run | P0 | aucune |
| [33-2](./story-33-2-context-loader.md) | Loader de contexte de prédiction | P0 | 33-1 |
| [33-3](./story-33-3-temporal-sampler.md) | Sampler temporel journalier | P0 | 33-1 |
| [33-4](./story-33-4-astro-calculator.md) | Calculateur astro intraday V1 | P0 | 33-3 |
| [33-5](./story-33-5-event-detector.md) | Détecteur d'événements astrologiques V1 | P0 | 33-4 |
| [33-6](./story-33-6-natal-sensitivity.md) | Calculateur de sensibilité natale `NS(c)` | P0 | 33-2 |

---

## Ordre d'implémentation

```
33-1 → 33-2 → 33-3 → 33-4 → 33-5 → 33-6
```

`33-2` et `33-3` peuvent être développées en parallèle après `33-1`.
`33-6` peut démarrer dès `33-2` terminée, indépendamment de `33-4`/`33-5`.

---

## Nouveaux fichiers par story

### 33-1
- `backend/app/prediction/schemas.py` ← CRÉER (contrats entrée/sortie moteur)
- `backend/app/prediction/engine_orchestrator.py` ← CRÉER
- `backend/app/tests/unit/test_engine_orchestrator.py` ← CRÉER

### 33-2
- `backend/app/prediction/context_loader.py` ← CRÉER (`PredictionContextLoader`)
- `backend/app/tests/unit/test_context_loader.py` ← CRÉER

### 33-3
- `backend/app/prediction/temporal_sampler.py` ← CRÉER
- `backend/app/tests/unit/test_temporal_sampler.py` ← CRÉER

### 33-4
- `backend/app/prediction/astro_calculator.py` ← CRÉER
- `backend/app/tests/unit/test_astro_calculator.py` ← CRÉER

### 33-5
- `backend/app/prediction/event_detector.py` ← CRÉER
- `backend/app/tests/unit/test_event_detector.py` ← CRÉER

### 33-6
- `backend/app/prediction/natal_sensitivity.py` ← CRÉER (`NatalSensitivityCalculator`)
- `backend/app/tests/unit/test_natal_sensitivity.py` ← CRÉER

---

## Décisions figées pour cet epic

1. **Cibles natales V1** : 10 planètes natales (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto) + Asc + MC.
2. **Aspects V1** : `{0°, 60°, 90°, 120°, 180°}` uniquement.
3. **Système de maisons** : Placidus principal, repli Porphyre si non-convergence, `house_system_effective` tracé dans la sortie.
4. **Positions** : géocentriques (tropical, Swiss Ephemeris `swe_calc_ut`).
5. **Temps** : toutes les heures utilisateur converties en UT avant calcul, restituées en local pour l'affichage.
6. **Pas de sampling** : 15 minutes, avec raffinement local à 1 minute autour des transitions.

---

## Checklist de validation finale

- [ ] Moteur accepte un objet d'entrée canonique unique
- [ ] Hash d'entrée stable (natal + date locale + timezone + lat/lon + versions)
- [ ] Conversion local → UT → local sans perte de précision
- [ ] `house_system_requested` et `house_system_effective` présents dans la sortie
- [ ] 96 pas de 15 min sur une journée standard
- [ ] Positions calculées pour les 10 planètes + Asc/MC à chaque pas
- [ ] `enter_orb`, `exact`, `exit_orb` détectés correctement
- [ ] `applying` / `separating` dérivés de l'évolution d'orbe
- [ ] `NS(c)` bornée dans `[0.75, 1.25]` pour toutes les catégories actives
- [ ] Run déterministe : même entrée → même sortie

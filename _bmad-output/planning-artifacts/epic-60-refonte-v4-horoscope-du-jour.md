# Epic 60 — Refonte V4 de la page "Horoscope du jour"

**Status:** in-progress
**Créé le:** 2026-03-18
**Owner:** Cyril

---

## Objectif Produit

Rendre la page "Horoscope du jour" lisible, non redondante, plus premium et plus explicative, en alignant chaque bloc UI sur une couche métier distincte du moteur de prédiction.

**Principe central : Une section UI = un objet métier = une seule promesse de lecture.**

---

## Problème à Résoudre

La page actuelle mélange plusieurs objets métier différents (climat global, scores par domaine, fenêtres temporelles, turning points, meilleure fenêtre, conseil) avec pour conséquences :
- Redondance visuelle et sémantique
- Thématiques qui se recouvrent
- Notes peu lisibles (score /20 non intuitif)
- Absence de fondement astrologique explicite
- Difficulté pour l'utilisateur à comprendre quoi retenir et quoi faire

---

## Architecture Cible — Payload Public V4

```
day_climate
  label, tone, intensity, stability, summary
  top_domains (2 max), watchout (1 max), best_window_ref

domain_ranking (liste)
  domain, score_10, level, rank

time_windows (liste)
  time_range, label, regime, top_domains, action_hint

turning_point (optionnel)
  time, title, change_type, affected_domains, what_changes, do, avoid

best_window
  time_range, label, why, recommended_actions

astro_foundation
  headline, key_movements, activated_houses
  dominant_aspects, interpretation_bridge

daily_advice
  short_advice, long_advice
```

---

## Page Cible — Ordre des Sections

1. Hero / Climat du jour (`DayClimateHero`)
2. Domaines du jour (`DomainRankingCard`)
3. Moments de la journée (`DayTimelineSection`)
4. Point de bascule (`TurningPointCard`) — conditionnel
5. Meilleure fenêtre (`BestWindowCard`)
6. Conseil du jour (`DailyAdviceCard`) — existant refactoré
7. Fondements astrologiques (`AstroFoundationSection`)

---

## Périmètre

**Dans le périmètre :**
- Refonte de la projection publique (`public_projection.py`)
- Simplification et fusion des 12 domaines internes → 5 domaines publics
- Projection des scores internes [0-20] → score public sur 10
- Ajout d'une section "fondements astrologiques"
- Réorganisation de la page front React
- Mise à jour des composants, DTO Pydantic, types TypeScript, tests et fixtures

**Hors périmètre :**
- Refonte profonde des algorithmes de calcul astro (V3)
- Changement du modèle de persistance des runs (`PredictionRun`)
- Nouveau moteur de scoring
- Réécriture des calculs natal/transits

---

## Contraintes Techniques

- Backend: FastAPI Python, scores internes [0-20] à conserver
- Frontend: React/TypeScript, pas de Tailwind, CSS variables custom
- Domaines internes actuels (12): love, work, career, energy, mood, health, money, sex_intimacy, family_home, social_network, communication, pleasure_creativity
- Scores exposés actuellement: `note_20`, `score_20`, `intensity_20`
- Endpoint actuel: `GET /v1/predictions/daily` → `DailyPredictionResponse`
- Depuis l'Epic 64, l'accès runtime à `GET /v1/predictions/daily` passe par `HoroscopeDailyEntitlementGate` avec fallback de compatibilité tant que la migration canonique des droits n'est pas complète.

---

## Stories

| Story | Titre | Dépend de | Priorité |
|-------|-------|-----------|----------|
| 60.1 | Taxonomie publique des domaines | — | P0 |
| 60.2 | Scores publics sur 10 | 60.1 | P0 |
| 60.3 | Bloc day_climate | 60.1, 60.2 | P0 |
| 60.4 | Refonte time_windows | 60.1 | P1 |
| 60.5 | Turning point narratif | 60.1 | P1 |
| 60.6 | Best window dédié | 60.3 | P1 |
| 60.7 | Section astro_foundation | 60.1, 60.3 | P1 |
| 60.8 | Refonte page front | 60.1–60.7 | P2 |
| 60.9 | Wording & microcopies | 60.1–60.8 | P2 |
| 60.10 | Migration API sans casse | 60.1–60.7 | P0 |
| 60.11 | Tests, fixtures, QA | 60.1–60.9 | P2 |
| 60.12 | Cleanup legacy | 60.10, 60.11 | P3 |
| 60.13 | Module Événements Astrologiques du Jour | 60.7, 60.8 | P2 |
| 60.14 | Périodes du jour dans la timeline V4 | 60.4, 60.8 | P2 |

---

## Définition of Done

L'epic est terminé si :
- La page répond clairement aux 6 questions métier
- Les domaines publics ne sont plus redondants (5 catégories max)
- Les notes sont affichées sur 10 côté UI
- Un bloc astrologique explicatif existe
- Chaque composant front consomme un objet métier dédié
- La redondance de contenu est réduite de façon visible
- Les tests couvrent les nouveaux contrats

---

## Références Techniques

- `backend/app/prediction/public_projection.py` — `PublicPredictionAssembler`
- `backend/app/prediction/domain_router.py` — routing domaines internes
- `backend/app/prediction/decision_window_builder.py` — fenêtres (V3)
- `backend/app/prediction/turning_point_detector.py` — turning points (V3)
- `backend/app/prediction/aggregator.py` — `V3ThemeAggregator`, `V3DailyMetrics`
- `backend/app/prediction/calibrator.py` — `PercentileCalibrator`
- `backend/app/api/v1/routers/predictions.py` — endpoint + DTOs Pydantic
- `frontend/src/pages/DailyHoroscopePage.tsx` — page principale
- `frontend/src/types/dailyPrediction.ts` — types TypeScript actuels
- `frontend/src/api/dailyPrediction.ts` — client API

---

## Ajustements Récents

- durcissement du flux `/v1/predictions/daily` contre les appels concurrents pour un même utilisateur et une même journée ;
- ajout d'un garde backend de type single-flight dans `DailyPredictionService` pour éviter les recalculs multiples du moteur tant que le premier run n'est pas persisté ;
- validation par test unitaire de non-régression : deux appels simultanés doivent déclencher un seul calcul moteur, puis réutiliser le snapshot persisté ;
- la correction vise le symptôme observé sur la page horoscope V4 : rafale de recalculs `transit_signal_built` / `intraday_activation_built` / `impulse_signal_built` avant la première réponse HTTP.
- recalibrage du variant free de la narration LLM : le résumé `day-climate-hero__summary` conserve une structure proche de la version Basic, mais cible désormais 6–8 phrases et une longueur comprise entre 50% et 67% de la version complète, avec un budget tokens rehaussé pour éviter un rendu trop simpliste.

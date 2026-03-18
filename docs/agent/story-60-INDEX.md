# Epic 60 — Index des Stories : Refonte V4 "Horoscope du jour"

**Epic:** Refonte V4 de la page "Horoscope du jour"
**Principe:** Une section UI = un objet métier = une seule promesse de lecture
**Créé le:** 2026-03-18

---

## Graphe de dépendances

```
60.1 (taxonomie domaines)
  └─→ 60.2 (scores /10)
        └─→ 60.3 (day_climate)
              └─→ 60.6 (best_window)
  └─→ 60.4 (time_windows)
  └─→ 60.5 (turning_point)
  └─→ 60.7 (astro_foundation)
        ↑ aussi 60.3

60.1–60.7 ──→ 60.8 (refonte front)
60.1–60.8 ──→ 60.9 (wording)
60.1–60.7 ──→ 60.10 (migration API)
60.1–60.9 ──→ 60.11 (tests QA)
60.10+60.11 → 60.12 (cleanup)
```

---

## Stories

| # | Fichier | Titre | Status | Dépend de |
|---|---------|-------|--------|-----------|
| 60.1 | [60-1-taxonomie-domaines-publics.md](../../_bmad-output/implementation-artifacts/60-1-taxonomie-domaines-publics.md) | Taxonomie publique des domaines | ready-for-dev | — |
| 60.2 | [60-2-scores-publics-sur-10.md](../../_bmad-output/implementation-artifacts/60-2-scores-publics-sur-10.md) | Scores publics sur 10 | ready-for-dev | 60.1 |
| 60.3 | [60-3-day-climate.md](../../_bmad-output/implementation-artifacts/60-3-day-climate.md) | Bloc day_climate (hero séparé) | ready-for-dev | 60.1, 60.2 |
| 60.4 | [60-4-time-windows.md](../../_bmad-output/implementation-artifacts/60-4-time-windows.md) | Refonte fenêtres temporelles | ready-for-dev | 60.1 |
| 60.5 | [60-5-turning-point.md](../../_bmad-output/implementation-artifacts/60-5-turning-point.md) | Turning point narratif | ready-for-dev | 60.1 |
| 60.6 | [60-6-best-window.md](../../_bmad-output/implementation-artifacts/60-6-best-window.md) | Best window dédié | ready-for-dev | 60.1, 60.3 |
| 60.7 | [60-7-astro-foundation.md](../../_bmad-output/implementation-artifacts/60-7-astro-foundation.md) | Section fondements astrologiques | ready-for-dev | 60.1, 60.3 |
| 60.8 | [60-8-refonte-front.md](../../_bmad-output/implementation-artifacts/60-8-refonte-front.md) | Recomposition page front | ready-for-dev | 60.1–60.7 |
| 60.9 | [60-9-wording-microcopies.md](../../_bmad-output/implementation-artifacts/60-9-wording-microcopies.md) | Wording & microcopies | ready-for-dev | 60.1–60.8 |
| 60.10 | [60-10-migration-api.md](../../_bmad-output/implementation-artifacts/60-10-migration-api.md) | Migration API sans casse | ready-for-dev | 60.1–60.7 |
| 60.11 | [60-11-tests-fixtures-qa.md](../../_bmad-output/implementation-artifacts/60-11-tests-fixtures-qa.md) | Tests, fixtures, QA | ready-for-dev | 60.1–60.9 |
| 60.12 | [60-12-cleanup-legacy.md](../../_bmad-output/implementation-artifacts/60-12-cleanup-legacy.md) | Cleanup legacy | ready-for-dev | 60.10, 60.11 |

---

## Payload V4 — Structure cible

```json
{
  "meta": { "...", "payload_version": "v4" },
  "day_climate": {
    "label": "Élan favorable",
    "tone": "positive",
    "intensity": 7.2,
    "stability": 6.8,
    "summary": "Les sujets pro et relationnels sont bien soutenus.",
    "top_domains": ["pro_ambition", "relations_echanges"],
    "watchout": null,
    "best_window_ref": "14:00–16:00"
  },
  "domain_ranking": [
    { "key": "pro_ambition", "label": "Pro & Ambition", "score_10": 8.2, "level": "favorable", "rank": 1 },
    { "key": "relations_echanges", "label": "Relations & échanges", "score_10": 7.5, "level": "favorable", "rank": 2 }
  ],
  "time_windows": [
    { "time_range": "06:00–10:00", "label": "Mise en mouvement", "regime": "mise_en_route", "top_domains": ["pro_ambition"], "action_hint": "Lancez doucement" }
  ],
  "turning_point": {
    "time": "15:30",
    "title": "Virage côté pro",
    "change_type": "recomposition",
    "affected_domains": ["pro_ambition"],
    "what_changes": "Le focus se déplace vers l'ambition professionnelle.",
    "do": "Décidez, négociez",
    "avoid": "Reporter"
  },
  "best_window": {
    "time_range": "14:00–16:00",
    "label": "Votre meilleur créneau",
    "why": "Les conditions pro sont au maximum de leur dynamique.",
    "recommended_actions": ["Prendre des décisions importantes", "Négocier ou conclure"]
  },
  "astro_foundation": {
    "headline": "Jupiter en trigone facilite les initiatives professionnelles.",
    "key_movements": [...],
    "activated_houses": [...],
    "dominant_aspects": [...],
    "interpretation_bridge": "Ces transits expliquent pourquoi le secteur Pro est particulièrement actif."
  },
  "summary": { "..." },
  "categories": [ "..." ],
  "timeline": [ "..." ],
  "turning_points": [ "..." ],
  "decision_windows": [ "..." ]
}
```

---

## Fichiers Backend clés

| Rôle | Fichier |
|------|---------|
| Projection publique | `backend/app/prediction/public_projection.py` |
| Taxonomie domaines publics | `backend/app/prediction/public_domain_taxonomy.py` ← NEW |
| Mapper score /10 | `backend/app/prediction/public_score_mapper.py` ← NEW |
| Catalogue labels | `backend/app/prediction/public_label_catalog.py` ← NEW |
| Vocabulaire astro | `backend/app/prediction/public_astro_vocabulary.py` ← NEW |
| Endpoint API + DTOs | `backend/app/api/v1/routers/predictions.py` |
| Routing domaines internes | `backend/app/prediction/domain_router.py` |
| Fenêtres temporelles | `backend/app/prediction/decision_window_builder.py` |
| Turning points | `backend/app/prediction/turning_point_detector.py` |

## Fichiers Frontend clés

| Rôle | Fichier |
|------|---------|
| Page principale | `frontend/src/pages/DailyHoroscopePage.tsx` |
| Types TypeScript | `frontend/src/types/dailyPrediction.ts` |
| Client API | `frontend/src/api/dailyPrediction.ts` |
| Copy i18n | `frontend/src/i18n/horoscope_copy.ts` ← NEW |
| Composant hero | `frontend/src/components/DayClimateHero.tsx` ← NEW |
| Composant domaines | `frontend/src/components/DomainRankingCard.tsx` ← NEW |
| Composant timeline | `frontend/src/components/DayTimelineSection.tsx` (refactoré) |
| Composant pivot | `frontend/src/components/TurningPointCard.tsx` ← NEW |
| Composant best window | `frontend/src/components/BestWindowCard.tsx` ← NEW |
| Composant astro | `frontend/src/components/AstroFoundationSection.tsx` ← NEW |

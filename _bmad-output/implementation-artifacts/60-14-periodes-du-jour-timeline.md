# Story 60.14 : Périodes du Jour dans la Timeline V4

Status: done

## Story

En tant qu'utilisateur de la page Horoscope du jour,
je veux voir les 4 périodes fixes de ma journée (Nuit, Matin, Après-midi, Soirée) avec leurs icônes distinctives dans la section timeline,
afin de comprendre d'un coup d'œil comment ma journée s'articule par grande plage horaire.

## Acceptance Criteria

### Backend — Refonte de `PublicTimeWindowPolicy`

1. La policy produit toujours **exactement 4 fenêtres fixes** correspondant aux 4 périodes du jour, dans l'ordre : Nuit (22:00–06:00), Matin (06:00–12:00), Après-midi (12:00–18:00), Soirée (18:00–22:00).
2. Chaque fenêtre inclut un champ `period_key: str` avec les valeurs : `"nuit"`, `"matin"`, `"apres_midi"`, `"soiree"`.
3. Pour chaque période, le `regime` est déterminé en agrégeant les blocs V3 (`time_blocks`) dont le `start_local` (ou `start_at_local`) tombe dans la plage horaire :
   - Sélectionner l'orientation dominante (mode des orientations des blocs dans la période)
   - Appliquer `_resolve_regime()` sur la plage de la période avec un datetime représentatif
   - Si aucun bloc V3 ne tombe dans la période → `regime = "récupération"` pour Nuit, `"fluidité"` pour les autres
4. Les `top_domains` (max 2) sont agrégés depuis les `dominant_themes` de tous les blocs de la période, dans l'ordre de fréquence.
5. Le `time_range` de chaque fenêtre affiche la plage fixe canonique : `"22:00–06:00"`, `"06:00–12:00"`, `"12:00–18:00"`, `"18:00–22:00"`.
6. Si aucun bloc V3 n'est disponible (liste vide), les 4 fenêtres sont quand même émises avec des régimes par défaut et des `top_domains: []`.
7. Le DTO `DailyPredictionTimeWindow` est étendu avec `period_key: str` dans `predictions.py`.
8. Tests unitaires : 4 fenêtres émises même sans blocs, `period_key` présent, agrégation correcte des domaines par période.

### Frontend — Refonte de `DayTimelineSectionV4`

9. Le composant utilise le `period_key` pour afficher une **icône Lucide distincte** par période :
   - `nuit` → `Moon` (Lucide)
   - `matin` → `Sunrise` (Lucide)
   - `apres_midi` → `Sun` (Lucide)
   - `soiree` → `Sunset` (Lucide)
10. Chaque carte de période affiche : icône + nom de période (i18n), plage horaire fixe, badge régime, label, action_hint, icônes domaines.
11. Le nom de période est internationalisé via `PERIOD_LABELS` existant dans `frontend/src/i18n/predictions.ts` : `nuit`, `matin`, `apres_midi`, `soiree`.
12. Le layout reste une liste verticale de 4 cartes (pas de rail interactif, pas d'agenda expandable — garder la simplicité V4).
13. Le type `DailyPredictionTimeWindow` dans `frontend/src/types/dailyPrediction.ts` est étendu avec `period_key: string`.
14. Si un `time_window` reçu n'a pas de `period_key` reconnu, l'icône par défaut `✨` est utilisée (garde-fou).

## Tasks / Subtasks

- [x] T1 — Backend : refondre `PublicTimeWindowPolicy.build()` (AC: 1, 2, 3, 4, 5, 6)
  - [x] T1.1 — Définir les 4 périodes canoniques avec leurs plages horaires
  - [x] T1.2 — Pour chaque période, filtrer les blocs V3 par `start_local.hour` dans la plage
  - [x] T1.3 — Calculer l'orientation dominante par mode des orientations des blocs de la période
  - [x] T1.4 — Appeler `_resolve_regime()` avec un datetime représentatif de la période (ex: milieu de plage)
  - [x] T1.5 — Agréger `top_domains` depuis les `dominant_themes` de tous les blocs de la période
  - [x] T1.6 — Émettre 4 fenêtres même si aucun bloc disponible (régimes par défaut)
  - [x] T1.7 — Ajouter `period_key` à chaque fenêtre

- [x] T2 — Backend : DTO (AC: 7)
  - [x] T2.1 — Ajouter `period_key: str` à `DailyPredictionTimeWindow` dans `predictions.py`

- [x] T3 — Backend : tests (AC: 8)
  - [x] T3.1 — Adapter les tests existants dans `backend/tests/unit/prediction/test_public_time_window.py`
  - [x] T3.2 — Test : 4 fenêtres émises sans blocs avec régimes par défaut
  - [x] T3.3 — Test : `period_key` correct pour chaque période
  - [x] T3.4 — Test : agrégation des domaines par période
  - [x] T3.5 — Vérifier que les tests d'intégration existants (`test_v4_scenarios.py`) passent

- [x] T4 — Frontend : type étendu (AC: 13)
  - [x] T4.1 — Ajouter `period_key: string` à `DailyPredictionTimeWindow` dans `dailyPrediction.ts`

- [x] T5 — Frontend : refonte `DayTimelineSectionV4` (AC: 9, 10, 11, 12, 14)
  - [x] T5.1 — Importer `Moon, Sunrise, Sun, Sunset` depuis `lucide-react`
  - [x] T5.2 — Créer `PERIOD_ICONS` mapping `period_key → LucideIcon`
  - [x] T5.3 — Utiliser `PERIOD_LABELS[window.period_key]?.[lang]` pour le nom de période
  - [x] T5.4 — Afficher icône + nom période + time_range en header de chaque carte
  - [x] T5.5 — Conserver les styles existants (couleurs de régime, border, action_hint)
  - [x] T5.6 — Fallback icône si `period_key` non reconnu

- [x] T6 — Vérification finale
  - [x] T6.1 — `ruff check backend/` passe
  - [x] T6.2 — `pytest backend/` passe
  - [x] T6.3 — Les 4 périodes s'affichent toujours (même journée sans blocs)
  - [x] T6.4 — Les icônes Moon/Sunrise/Sun/Sunset apparaissent correctement

## Dev Notes

### Architecture critique

**Plages horaires des 4 périodes** (à définir comme constante au niveau de la class ou du module) :
```python
PERIOD_SLOTS = [
    {"key": "nuit",       "label_fr": "Nuit",        "hour_start": 22, "hour_end": 6,  "next_day_end": True},
    {"key": "matin",      "label_fr": "Matin",       "hour_start": 6,  "hour_end": 12},
    {"key": "apres_midi", "label_fr": "Après-midi",  "hour_start": 12, "hour_end": 18},
    {"key": "soiree",     "label_fr": "Soirée",      "hour_start": 18, "hour_end": 22},
]
```
La période `nuit` couvre les heures >= 22 OU < 6.

**Agrégation du régime par période** : Si la période contient plusieurs blocs V3 avec des orientations différentes, prendre l'orientation la plus fréquente (mode). Si égalité → `"stable"`. Ensuite appliquer `_resolve_regime()` avec un datetime représentatif :
```python
# datetime représentatif de milieu de période (ex: matin = 09:00 le jour local)
from datetime import datetime
representative_dt = snapshot.local_date  # utiliser pour créer un datetime avec heure fixe
mid_hour = (hour_start + (hour_end - hour_start) // 2) % 24
representative = datetime(snapshot.local_date.year, snapshot.local_date.month, snapshot.local_date.day, mid_hour, 0)
```

**Régimes par défaut** (si aucun bloc dans la période) :
- `nuit` → `"récupération"`
- `matin` → `"mise_en_route"`
- `apres_midi` → `"fluidité"`
- `soiree` → `"recentrage"`

**time_range canonique** : Utiliser les plages fixes, pas les timestamps des blocs :
- Nuit : `"22:00–06:00"` (NB: à traiter comme deux jours)
- Matin : `"06:00–12:00"`
- Après-midi : `"12:00–18:00"`
- Soirée : `"18:00–22:00"`

**Compatibilité `_resolve_regime()`** : La méthode actuelle prend `start: datetime` et `end: datetime`. Pour les régimes par défaut (aucun bloc), appeler directement avec un datetime représentatif valide, pas None. La correction du bug `None` (story 60.x fixes précédents) doit déjà être en place.

### Fichiers clés

**À modifier :**
- `backend/app/prediction/public_projection.py` — refonte `PublicTimeWindowPolicy.build()` (lignes 519-628)
- `backend/app/api/v1/routers/predictions.py` — ajouter `period_key: str` au DTO `DailyPredictionTimeWindow`
- `frontend/src/types/dailyPrediction.ts` — ajouter `period_key: string` à `DailyPredictionTimeWindow`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx` — refonte visuelle avec icônes par période

**Tests à adapter :**
- `backend/tests/unit/prediction/test_public_time_window.py` — adapter aux nouvelles 4 fenêtres fixes
- `backend/tests/integration/test_v4_scenarios.py` — vérifier que `time_windows` contient toujours 4 items avec `period_key`

### Frontend — Implémentation

**Icônes Lucide** — déjà disponibles dans le projet (utilisées dans `PeriodCard.tsx` legacy) :
```tsx
import { Moon, Sunrise, Sun, Sunset } from 'lucide-react';

const PERIOD_ICONS: Record<string, React.ComponentType<{ size?: number }>> = {
  nuit: Moon,
  matin: Sunrise,
  apres_midi: Sun,
  soiree: Sunset,
};
```

**Labels de période i18n** — `PERIOD_LABELS` existe déjà dans `frontend/src/i18n/predictions.ts` :
```ts
// Déjà présent :
PERIOD_LABELS: {
  nuit:      { fr: 'Nuit',        en: 'Night' },
  matin:     { fr: 'Matin',       en: 'Morning' },
  apres_midi:{ fr: 'Après-midi',  en: 'Afternoon' },
  soiree:    { fr: 'Soirée',      en: 'Evening' },
}
```
Utiliser : `PERIOD_LABELS[window.period_key]?.[lang] ?? window.period_key`

**Structure d'une carte de période** (exemple) :
```tsx
<div key={window.period_key || window.time_range} style={{ /* styles existants selon regime */ }}>
  {/* Header : icône + nom période + plage horaire */}
  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
    <PeriodIcon size={16} />
    <span style={{ fontWeight: 'bold', color: 'var(--text-1)' }}>
      {PERIOD_LABELS[window.period_key]?.[lang] ?? ''}
    </span>
    <span style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--text-2)' }}>
      {window.time_range}
    </span>
    <span>{/* badge regime existant */}</span>
  </div>
  {/* Corps : label, action_hint, domaines — identique à l'implémentation actuelle */}
  ...
</div>
```

**Ne pas ressusciter** `DayTimelineSection`, `PeriodCardsRow`, `TimelineRail`, `DayAgenda` — ces composants sont legacy et non utilisés. Story 60.12 a nettoyé, ne pas réintroduire.

### CSS — Ne pas utiliser Tailwind

Styles inline avec variables CSS, identiques au pattern existant dans `DayTimelineSectionV4.tsx` :
```tsx
style={{ color: 'var(--text-1)', background: 'var(--glass-2)', borderRadius: '12px', ... }}
```

### Relation avec les autres stories

- Cette story **modifie** `PublicTimeWindowPolicy` qui a été écrite en 60.4.
- Les tests de `test_public_time_window.py` (écrits en 60.11) doivent être adaptés.
- L'AC6 de 60.4 ("8 regimes") reste valide — les mêmes regimes sont utilisés, mais maintenant agrégés par période.
- 60.13 (AstroDailyEventsModule) est indépendant de cette story — pas de conflit.

### Project Structure Notes

- `DayTimelineSectionV4.tsx` reste dans `frontend/src/components/prediction/` (pas de déplacement)
- `PERIOD_LABELS` est dans `frontend/src/i18n/predictions.ts` — NE PAS dupliquer dans `horoscope_copy.ts`
- Le champ `period_key` dans le DTO backend doit être un `str` non-optionnel (toujours 4 périodes émises)

### References

- `backend/app/prediction/public_projection.py` lignes 519-628 — `PublicTimeWindowPolicy.build()` à refondre
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx` — composant à mettre à jour
- `frontend/src/components/prediction/PeriodCard.tsx` — référence visuelle (ne pas importer, juste s'en inspirer pour les icônes)
- `frontend/src/i18n/predictions.ts` — `PERIOD_LABELS` existant
- `frontend/src/types/dayTimeline.ts` — `DayPeriodKey` legacy (ne pas réimporter, juste référence)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/prediction/public_projection.py`
- `backend/app/api/v1/routers/predictions.py`
- `backend/tests/unit/prediction/test_public_time_window.py`
- `backend/tests/integration/test_v4_scenarios.py`
- `frontend/src/types/dailyPrediction.ts`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`

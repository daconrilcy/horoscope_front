# Story 58.11 : Section "Moments de la journée" — périodes agrégées avec agenda filtrable

Status: done

## Story

En tant qu'utilisateur de la page `/dashboard/horoscope`,
je veux voir la journée découpée en 4 grandes périodes (Nuit, Matin, Après-midi, Soirée) sous forme de cartes glassmorphism,
afin de pouvoir filtrer l'agenda détaillé par moment de la journée et avoir une vision macro de ma timeline via un rail de tonalités.

## Acceptance Criteria

1.  Les types `DayPeriodKey` ('nuit', 'matin', 'apres_midi', 'soiree') et `AggregatedDayPeriod` sont créés dans `frontend/src/types/dayTimeline.ts`.
2.  `AggregatedDayPeriod` contient : `key`, `label`, `icon`, `slots` (DailyAgendaSlot[]), `tone`, `dominantCategories` (string[]), `hasTurningPoint` (boolean).
3.  Les libellés sont définis dans `frontend/src/i18n/predictions.ts` via une constante `PERIOD_LABELS` (ex: `nuit: { fr: 'Nuit', en: 'Night' }`).
4.  Le mapper `buildDayTimelineSectionModel()` dans `frontend/src/utils/dayTimelineSectionMapper.ts` agrège les 12 slots de l'agenda (2h par slot) en 4 périodes de 6h (3 slots par période).
5.  Logique d'agrégation :
    *   **Tone** : Le tone dominant est dérivé des blocks de la timeline API correspondant à la période.
    *   **Categories** : Les `topCategories` des 3 slots sont fusionnées et dédoublonnées (max 3).
    *   **Pivot** : `hasTurningPoint` est vrai si au moins un des 3 slots contient un turning point.
6.  Le composant `PeriodCard` (et sa ligne `PeriodCardsRow`) est créé. Il affiche l'icône, le label, les icônes des catégories dominantes, et un indicateur visuel (point) si un pivot est présent.
7.  État de sélection : Une seule période peut être sélectionnée à la fois. Cliquer sur une période sélectionnée la désélectionne (toggle).
8.  Style Glassmorphism : Utilise `backdrop-filter: blur`, `background: rgba(255,255,255, 0.1)`, et `border: 1px solid var(--color-glass-border)`.
9.  Rail de tonalité (`TimelineRail`) : Barre horizontale sous les cartes montrant les 4 segments colorés par leur tonalité dominante. Le segment de la période sélectionnée est mis en avant (scaleY ou opacité).
10. Couleurs du rail : `positive` (success), `negative` (error), `neutral` (primary), `mixed` (warning/purple-2).
11. Intégration Agenda : Le composant `DayAgenda` existant n'est affiché **que si une période est sélectionnée**, et il ne montre que les slots de cette période.
12. `DailyHoroscopePage.tsx` remplace la Zone 4 (titre + DayAgenda complet) par le nouveau composant `DayTimelineSection`.
13. `tsc --noEmit` et tests Vitest passent.

## Tasks / Subtasks

- [x] T1 — Créer les types `DayPeriodKey`, `AggregatedDayPeriod` et `DayTimelineSectionModel` (AC: 1, 2)
  - [x] T1.1 Créer `frontend/src/types/dayTimeline.ts`

- [x] T2 — Ajouter les libellés de périodes `PERIOD_LABELS` (AC: 3)
  - [x] T2.1 Modifier `frontend/src/i18n/predictions.ts` pour exporter `PERIOD_LABELS` (fr/en)

- [x] T3 — Créer le mapper `buildDayTimelineSectionModel` (AC: 4, 5)
  - [x] T3.1 Créer `frontend/src/utils/dayTimelineSectionMapper.ts`
  - [x] T3.2 Implémenter le découpage 4x3 slots (0-6h, 6-12h, 12-18h, 18-24h)
  - [x] T3.3 Implémenter `derivePeriodTone` pour trouver le tone dominant sur les blocks timeline
  - [x] T3.4 Agréger les `topCategories` (union, max 3) et flagger `hasTurningPoint`

- [x] T4 — Créer le composant `PeriodCard` (AC: 6, 7, 8)
  - [x] T4.1 Créer `frontend/src/components/prediction/PeriodCard.tsx`
  - [x] T4.2 Créer `frontend/src/components/prediction/PeriodCard.css` (glassmorphism, states)

- [x] T5 — Créer `PeriodCardsRow` (AC: 6)
  - [x] T5.1 Créer `frontend/src/components/prediction/PeriodCardsRow.tsx/css` (layout row sans wrap)

- [x] T6 — Créer `TimelineRail` (AC: 10)
  - [x] T6.1 Créer `frontend/src/components/prediction/TimelineRail.tsx/css` (segments colorés, scale animation)

- [x] T7 — Créer `DayTimelineSection` (AC: 9, 11)
  - [x] T7.1 Créer `frontend/src/components/prediction/DayTimelineSection.tsx/css`
  - [x] T7.2 Gérer le state `selectedPeriod` et le filtrage des `agendaSlots`

- [x] T8 — Intégrer dans `DailyHoroscopePage.tsx` (AC: 12)
  - [x] T8.1 Remplacer la Zone 4 (actuel `DayAgenda`) par `<DayTimelineSection ... />`
  - [x] T8.2 Nettoyer les imports (mapper, types)

- [x] T9 — Validation et non-régression (AC: 13)
  - [x] T9.1 `tsc --noEmit` — 0 erreur TypeScript
  - [x] T9.2 `npx vitest run src/tests/DailyHoroscopePage.test.tsx` — tous les tests passent (test adapté pour simuler le clic sur période)
  - [x] T9.3 `npx vitest run` global — ≥ 1071 tests verts

## Dev Notes

### Architecture

- Le projet utilise `verbatimModuleSyntax: true` → **tous les types s'importent avec `import type`**.
- Pas de Tailwind. CSS pur.
- `DayAgenda` est déjà performant, il suffit de lui passer un sous-ensemble de `slots`.

### Mapper technique

Le découpage se base sur les 12 slots de 2h produits par `buildDailyAgendaSlots`.
*   Nuit : slots 0, 1, 2 (00:00 - 06:00)
*   Matin : slots 3, 4, 5 (06:00 - 12:00)
*   Après-midi : slots 6, 7, 8 (12:00 - 18:00)
*   Soirée : slots 9, 10, 11 (18:00 - 00:00)

Icônes suggérées : 🌙, ☀️, 🌤️, 🌆

### Timeline Rail

Le rail est un décoratif qui donne un "résumé visuel" de la journée.
Si aucun tone n'est trouvé pour une période, utiliser `neutral`.

### Tests adaptations

Comme l'agenda est désormais caché par défaut (nécessite un clic), les tests existants qui vérifient la présence de `data-testid="agenda-slot"` vont échouer s'ils ne simulent pas d'abord un clic sur une carte de période.
Il faudra ajouter `await userEvent.click(screen.getByText(/Matin/i))` dans les tests concernés.

### References

- Composant agenda actuel : `frontend/src/components/prediction/DayAgenda.tsx`
- Utilitaire agenda : `frontend/src/utils/dailyAstrology.ts` (`buildDailyAgendaSlots`)
- Page cible : `frontend/src/pages/DailyHoroscopePage.tsx` Zone 4.

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp (orchestrated by Gemini CLI)

### Debug Log References

- Created types and mapper for period aggregation.
- Updated i18n with period labels.
- Implemented `PeriodCard`, `PeriodCardsRow`, `TimelineRail`, and `DayTimelineSection`.
- Integrated in `DailyHoroscopePage.tsx`.
- Adapted `DailyHoroscopePage.test.tsx` to handle conditional rendering of the agenda (now requires a period click).
- Verified with `tsc` and `vitest`.

### Post-implementation design corrections (claude-sonnet-4-6, 2026-03-17)

Suite à un audit visuel comparatif avec la maquette, plusieurs corrections ont été apportées :

**Icônes** — Remplacement des emojis (`🌙☀️🌤️🌆`) par des icônes Lucide (`Moon`, `Sunrise`, `Sun`, `Sunset`) avec `strokeWidth={3}`. Constante `STROKE_ICON = 3` dans `PeriodCard.tsx`. Champ `icon: string` retiré de `AggregatedDayPeriod` et du mapper.

**PeriodCard — état actif premium** — Abandon du contour violet intégral. Remplacement par : barre d'accent 12px en haut (`::before`, gradient primary → lavande), `radial-gradient` fond pour l'état sélectionné, `scale(1.15)` + `box-shadow` 3 niveaux. Fond en `radial-gradient` clair en dark mode.

**PeriodCard — hover** — `scale(1.05)` sur survol (cartes non sélectionnées), `scale(1.15)` sur les cartes actives et au clic. `z-index: 1` pour éviter le chevauchement.

**PeriodCard — matière glassmorphism** — `border: 2px solid rgba(200,190,240,0.35)` (plus prononcée), `padding: var(--space-4)`, `transition: 0.25s ease` simplifié. Fond light : `rgba(252,250,255,0.58)`, fond dark : `radial-gradient` blanc-lavande.

**PeriodCard — hiérarchie typographique** — Nom : `1rem, 700, padding-top space-2`. Horaire : `0.7rem, muted`. Tone label : `0.9rem, 600`. Tone dot : `8px × 8px` avec `margin: 8px`.

**TimelineRail** — Refactorisé en rail continu unique (suppression des 4 mini-barres segmentées). Track complet + fill progressif jusqu'au thumb + 5 tick marks aux frontières + thumb circle animé. Prop `periods` supprimée (plus de coloration par segment). `DayTimelineSection` mis à jour en conséquence.

**SectionTitle** — Texte en `color-text-secondary` (prune, moins noir), dot 6px + opacity 0.7, ligne `opacity: 0.45`.

**DayAgenda pivot slots** — Différenciation macro/micro : les créneaux 2h pivot passent de `border-color: var(--primary)` (identique au signal période) à `border-top: 2px solid rgba(134,108,208,0.38)` + fond très léger, sans border complète.

**DayAgenda slots** — Même langage glassmorphism que `.period-card` non sélectionné : `backdrop-filter: blur(16px)`, fond blanc-lavande `rgba(252,250,255,0.58)`, `border: 2px solid rgba(200,190,240,0.35)`, `border-radius: 18px`, ombre diffuse `0 2px 12px rgba(134,108,208,0.06)`. Cohérence visuelle entre cartes de période et créneaux d'agenda.

### Completion Notes List

- Section "Moments de la journée" implémentée avec 4 cartes de période.
- Filtrage interactif : l'agenda n'est affiché que lorsqu'une période est sélectionnée.
- Rail temporel continu avec progression et thumb animés.
- Tests mis à jour pour simuler l'interaction utilisateur (sélection de période).
- Corrections visuelles post-implémentation alignées sur la maquette premium.

### File List

- `frontend/src/types/dayTimeline.ts`
- `frontend/src/utils/dayTimelineSectionMapper.ts`
- `frontend/src/components/prediction/PeriodCard.tsx`
- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/prediction/PeriodCardsRow.tsx`
- `frontend/src/components/prediction/PeriodCardsRow.css`
- `frontend/src/components/prediction/TimelineRail.tsx`
- `frontend/src/components/prediction/TimelineRail.css`
- `frontend/src/components/prediction/DayTimelineSection.tsx`
- `frontend/src/components/prediction/DayTimelineSection.css`
- `frontend/src/components/prediction/SectionTitle.css`
- `frontend/src/components/prediction/DayAgenda.css`
- `frontend/src/i18n/predictions.ts`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`

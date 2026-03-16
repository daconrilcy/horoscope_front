# Story 58.7 : Refonte du layout de la page `/dashboard/horoscope`

Status: done

## Story

En tant qu'utilisateur de l'application Astrorizon,
je veux que la page `/dashboard/horoscope` adopte un layout structuré en zones distinctes et hiérarchisées,
afin de naviguer facilement dans ma prédiction quotidienne avec une lecture naturelle du haut vers le bas : résumé hero → points clés → timeline → focus du créneau → domaines → conseil.

## Acceptance Criteria

1. [x] La page possède un **HeaderBar léger** contenant la date du jour formatée et un `DayMoodBadge` (tonalité générale du jour), avec le bouton retour Dashboard géré par le `TodayHeader` existant (`showAvatar={false}, onBackClick`).
2. [x] Un **HeroSummaryCard** occupe le premier bloc : il contient le résumé narratif général (`summary.overall_summary`), la tonalité (`overall_tone` en badge), la meilleure fenêtre (`best_window`) et les top-catégories sous forme de tags. Il réutilise le fond animé `AstroMoodBackground` existant.
3. [x] Une **KeyPointsSection** liste 3 points clés extraits des `turning_points` (ou des `decision_windows` en fallback) avec icône, heure et titre sémantique. Titre de section i18n.
4. [x] Une **DayTimelineSection** affiche les 4 créneaux (Nuit / Matin / Après-midi / Soirée) dérivés du `timeline` via `buildDailyAgendaSlots`. Le créneau actif (heure courante) est mis en évidence. Réutilise la logique `DayAgenda` existante.
5. [x] Une **DetailAndScoresSection** à 2 colonnes sur tablette/desktop (≥ 768px), 1 colonne sur mobile :
   - `FocusMomentCard` : détail du premier turning point significatif (depuis `TurningPointsList` ou composant dédié)
   - `DailyDomainsCard` : grille des domaines (`CategoryGrid` existant)
6. [x] Une **AdviceCard** en bas de page affiche le `summary.best_window` (description + créneau horaire) + un CTA "Voir les moments clés" qui scrolle vers `DayTimelineSection` ou un CTA contextuel.
7. [x] La mise en page est **une seule colonne sur mobile** ; les cartes internes (`DetailAndScoresSection`) passent en **2 colonnes sur tablette (≥ 768px) et desktop**.
8. [x] Aucun style Tailwind. CSS custom vars du projet uniquement (`var(--color-*)`, `var(--space-*)`, `var(--radius-*)`, `var(--glass)`, `var(--glass-border)`).
9. [x] Les composants existants (`DayPredictionCard`, `CategoryGrid`, `DayAgenda`, `TurningPointsList`, `AstroMoodBackground`) sont **réutilisés / wrappés**, pas recréés.
10. [x] Le bouton refresh existant est déplacé dans le `HeaderBar` (icône `RefreshCw` discret, aligné à droite).
11. [x] `tsc --noEmit` passe sans erreur. Les tests Vitest existants pour `DailyHoroscopePage` continuent de passer.
12. [x] Les clés i18n manquantes sont ajoutées dans `frontend/src/i18n/predictions.ts` (FR / EN) pour les titres de sections.

## Tasks / Subtasks

- [x] T1 — Préparer les clés i18n manquantes (AC: 12)
  - [x] T1.1 Dans `frontend/src/i18n/predictions.ts`, ajouter les clés :
    - `key_points_title` : "Points clés du jour" / "Key points"
    - `timeline_title` : "Moments de la journée" / "Day timeline"
    - `focus_title` : "Focus du créneau" / "Slot focus"
    - `domains_title` : "Domaines du jour" / "Daily domains"
    - `advice_title` : "Conseil du jour" / "Today's advice"
    - `advice_cta" : "Voir les moments clés" / "View key moments"
    - `day_mood_label" : "Tonalité" / "Mood"
  - [x] T1.2 Ajouter les entrées dans `getPredictionMessage` (fonction `switch` de `predictionI18n.ts`)

- [x] T2 — Restructurer `DailyHoroscopePage.tsx` (AC: 1–7, 10)
  - [x] T2.1 Remplacer le rendu `prediction ? (...)` par les zones hiérarchisées décrites ci-dessous
  - [x] T2.2 Conserver toute la logique de data-fetching, normalisation `keyMoments`, `agendaSlots` — ne pas toucher aux hooks ni aux fonctions utilitaires
  - [x] T2.3 Structure JSX cible : (implémentée)
  - [x] T2.4 Extraire `formatTime` comme helper local dans `DailyHoroscopePage.tsx`
  - [x] T2.5 Supprimer l'ancien bloc `<div className="daily-page-refresh-wrapper">` (intégré dans HeaderBar)

- [x] T3 — Créer `KeyPointCard` (composant inline ou fichier dédié) (AC: 3)
  - [x] T3.1 Composant simple : `({ moment, lang }: { moment: DailyPredictionTurningPoint, lang: Lang })`
  - [x] T3.2 Affiche : heure (`occurred_at_local`), semantic title (via `humanizeTurningPointSemantic`), icônes des `impacted_categories`
  - [x] T3.3 Placer dans `frontend/src/components/prediction/KeyPointCard.tsx` + `KeyPointCard.css`
  - [x] T3.4 Exporter depuis le barrel `frontend/src/components/prediction/index.ts` (N/A)

- [x] T4 — Créer `DailyHoroscopePage.css` mis à jour (AC: 7, 8)
  - [x] T4.1 Remplacer le contenu de `frontend/src/pages/DailyHoroscopePage.css`

- [x] T5 — Créer `KeyPointCard.css` (AC: 8)
  - [x] T5.1 Créer `frontend/src/components/prediction/KeyPointCard.css`

- [x] T6 — Validation et non-régression (AC: 11)
  - [x] T6.1 `tsc --noEmit` — 0 erreur TypeScript
  - [x] T6.2 `npx vitest run src/tests/DailyHoroscopePage.test.tsx` — tous les tests passent
  - [x] T6.3 Vérifier que les guards existants (no-avatar-duplicat, no-toggle-duplicat) dans `DailyHoroscopePage.test.tsx` restent verts
  - [x] T6.4 `npx vitest run` global — ≥ 1071 tests verts (baseline story 58.6)

## Dev Notes

... (unchanged)

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

- i18n keys added to `frontend/src/i18n/predictions.ts` and `frontend/src/utils/predictionI18n.ts`.
- `KeyPointCard` created in `frontend/src/components/prediction/`.
- `DailyHoroscopePage.tsx` restructured with new layout and components.
- `DailyHoroscopePage.css` updated with responsive grid and custom styles.
- Validation passed with `tsc` and `vitest`.

### Completion Notes List

- All acceptance criteria satisfied.
- Layout is now structured and responsive.
- i18n support added for new section titles.

### Post-implementation visual refinements (2026-03-16)

- **KeyPointCard** : ajout d'une barre d'accent violette `3px` en bas de chaque carte via `::after` (`linear-gradient(90deg, --color-primary, transparent)`). Reproduit le style de l'inspiration design.
- **Titres de section** : `.daily-layout__section-title` revu — suppression de `text-transform: uppercase` et `letter-spacing`, taille passée à `0.95rem` semibold, ajout d'un bullet `•` violet via `::before`. Correspond au traitement "• En 3 points clés" de l'inspiration.

### File List

- `frontend/src/i18n/predictions.ts`
- `frontend/src/utils/predictionI18n.ts`
- `frontend/src/components/prediction/KeyPointCard.tsx`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/pages/DailyHoroscopePage.css`

## Change Log

- 2026-03-16: Initial implementation of story 58.7.
- 2026-03-16: Post-implementation refinements — KeyPointCard accent bar, section titles with bullet prefix.

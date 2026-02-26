# Story 17.12: Correctifs P1 — Sections Raccourcis et Amour

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur consultant les sections de contenu,
I want des cartes Raccourcis et Amour conformes aux maquettes (lisibilité, badges, glass premium),
So that la page conserve une qualité visuelle homogène au-delà de la hero.

## Acceptance Criteria

1. **Suppression des soulignements non voulus (P1)**
   - Given les cards de raccourcis
   - When elles sont rendues comme liens
   - Then aucun texte n'est souligné (`text-decoration: none`) sur titre, sous-titre, statut.

2. **Shortcut cards glass conformes (P1)**
   - Given les shortcut cards
   - When thème dark
   - Then bg `rgba(255,255,255,0.06)`, border `rgba(255,255,255,0.10)`, blur actif
   - When thème light
   - Then bg `rgba(255,255,255,0.45)`, border `rgba(255,255,255,0.60)`, blur actif.

3. **Badges raccourcis conformes (P1)**
   - Given les badges icônes à gauche
   - When on inspecte taille et couleurs
   - Then taille 36x36 radius 14
   - And Chat: light `#E1F0EA`, dark `#E4F2EC`
   - And Tirage: light `#F8CAA5`, dark `#D5946A`.

4. **Typo raccourcis + statut en ligne (P1)**
   - Given les textes shortcuts
   - When on inspecte style
   - Then titre 14-15px semibold en `--text-1`
   - And sous-titre 13px en `--text-2`
   - And `En ligne` est vert doux sans soulignement.

5. **Mini cards Amour/Travail/Énergie glass + badges (P1)**
   - Given la section Amour
   - When on inspecte les 3 cartes
   - Then elles utilisent des surfaces glass conformes light/dark
   - And badge 36x36 radius 14 avec couleurs dédiées
   - And titre 15px semibold `--text-1`, description 13px `--text-2` limitée à 2 lignes.

6. **Lisibilité light mode garantie (P0)**
   - Given le thème light
   - When on observe ces sections
   - Then aucun texte principal n'est trop clair sur fond clair
   - And la hiérarchie de contraste reste conforme.

## Tasks / Subtasks

- [x] Task 1 (AC: #1)
  - [x] Supprimer décorations de liens dans `ShortcutCard`/`ShortcutsSection`
- [x] Task 2 (AC: #2, #3, #4)
  - [x] Ajuster styles glass, badges et typo des shortcuts
- [x] Task 3 (AC: #5, #6)
  - [x] Ajuster styles et truncation des mini-cards Amour/Travail/Énergie
- [x] Task 4 (AC: #1-#6)
  - [x] Mettre à jour tests unitaires des composants
  - [x] Ajouter assertions de non-régression sur contrastes et classes critiques

## Dev Notes

- Fichiers cible probables:
  - `frontend/src/components/ShortcutCard.tsx`
  - `frontend/src/components/ShortcutsSection.tsx`
  - `frontend/src/components/MiniInsightCard.tsx`
  - `frontend/src/components/DailyInsightsSection.tsx`
  - `frontend/src/App.css`
  - `frontend/src/styles/theme.css`
- Préserver les callbacks de navigation existants.

### Project Structure Notes

- Aucun changement de routing.
- Ajustements concentrés sur style + accessibilité + tests de composants.

### References

- [Source: docs/interfaces/horoscope-home-corrections.md#5-6]
- [Source: docs/interfaces/horoscope-ui-spec.md#7]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- Aucun blocage — implémentation directe sur base des specs docs/interfaces/horoscope-home-corrections.md §5-6.

### Completion Notes List

- Story créée en mode `ready-for-dev`.
- **Task 1 (AC#1)** : `text-decoration: none` ajouté sur `.shortcut-card` dans `App.css`. Harmonisation sémantique de `ShortcutCard` (utilisation de `h3`/`p`).
- **Task 2 (AC#2,#3,#4)** : Nouveaux tokens CSS `--glass-shortcut` et `--glass-shortcut-border` créés dans `theme.css`. Badge réduit à 36px. Ajout de `aria-hidden` sur les badges pour l'accessibilité.
- **Task 3 (AC#5,#6)** : Nouveaux tokens CSS `--glass-mini` et `--glass-mini-border` créés dans `theme.css`. Titre mini-card corrigé à 15px.
- **Task 4 (AC#1-#6)** : Analyses CSS statiques ajoutées dans `ShortcutCard.test.tsx`, `MiniInsightCard.test.tsx`, et `theme-tokens.test.ts`.

### File List

- `_bmad-output/implementation-artifacts/17-12-correctifs-p1-sections-raccourcis-et-amour.md`
- `frontend/src/styles/theme.css`
- `frontend/src/App.css`
- `frontend/src/components/ShortcutCard.tsx`
- `frontend/src/components/MiniInsightCard.tsx`
- `frontend/src/tests/ShortcutCard.test.tsx`
- `frontend/src/tests/MiniInsightCard.test.tsx`
- `frontend/src/tests/theme-tokens.test.ts`

### Change Log

- 2026-02-24 : Implémentation story 17-12 — correctifs P1 sections Raccourcis et Amour. Tokens glass dédiés, badge 36x36, text-decoration:none, titre mini-card 15px, tests de non-régression CSS statiques. 971/971 tests verts.

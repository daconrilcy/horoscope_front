# Story 17.10: Correctifs P0 — Contrastes, Tokens et Fonds premium

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur mobile de la page Horoscope,
I want un rendu light/dark conforme aux maquettes de référence sur les fondamentaux visuels,
So that le contenu soit lisible, premium, et immédiatement aligné avec l'intention design.

## Acceptance Criteria

1. **Suppression opacité globale (P0)**
   - Given la page `/dashboard` en mode light ou dark
   - When on inspecte les wrappers principaux (`AppShell`, `today-page`, overlays globaux)
   - Then aucune opacité globale (`opacity < 1`) n'est appliquée à un conteneur parent
   - And la douceur visuelle est obtenue via tokens alpha ciblés (`--glass`, `--text-2`, `--text-3`), pas via un voile global.

2. **Tokens design obligatoires actifs dans le DOM (P0)**
   - Given l'application est chargée
   - When on vérifie les variables CSS
   - Then les tokens `--text-1`, `--text-2`, `--text-3`, `--bg-top`, `--bg-mid`, `--bg-bot`, `--glass`, `--glass-2`, `--glass-border`, `--cta-l`, `--cta-r`, `--chip`, `--nav-glass`, `--nav-border`, `--shadow-card`, `--shadow-nav` existent en light et dark
   - And en light `--text-1 = #1E1B2E`
   - And en dark `--text-1 = rgba(245,245,255,0.92)`.

3. **Hiérarchie typographique conforme (P0)**
   - Given le header et la hero card sont rendus
   - When on mesure style et rendu
   - Then `Aujourd'hui` est à 13px/500 en `var(--text-2)`
   - And `Horoscope` est à 40px/~650 tracking négatif en `var(--text-1)`
   - And le headline hero est à 28px/~650 en `var(--text-1)`
   - And les titres de section sont à 18px/~650
   - And labels bottom nav sont à 12px/500 avec contraste conforme.

4. **Dark background starfield (sans bokeh) (P0)**
   - Given le mode dark est actif
   - When on observe le fond
   - Then aucun bokeh/cercle flottant n'est présent
   - And un layer starfield + gradient cosmique est visible
   - And les cartes translucides laissent percevoir le fond via transparence + blur.

5. **Light background pastel + noise (P0)**
   - Given le mode light est actif
   - When on observe le fond
   - Then le fond combine radial gradients doux + linear gradient pastel
   - And une noise subtile (opacité 0.06-0.10) est présente
   - And aucun overlay gris/noir ne réduit le contraste global.

6. **Icônes Lucide harmonisées (P1)**
   - Given les composants Today sont rendus
   - When on inspecte les icônes
   - Then `strokeWidth=1.75` est appliqué de manière homogène
   - And tailles conformes: nav 24, cards 20, chevrons CTA 18, inline 16.

## Tasks / Subtasks

- [x] Task 1 (AC: #1)
  - [x] Auditer et supprimer toute opacité globale sur wrappers/overlays parent
  - [x] Remplacer par usage de tokens alpha ciblés
- [x] Task 2 (AC: #2)
  - [x] Vérifier/completer la définition des tokens requis dans `frontend/src/styles/theme.css`
  - [x] Garantir la bascule light/dark effective dans le DOM
- [x] Task 3 (AC: #3)
  - [x] Ajuster les styles typographiques des composants `TodayHeader`, `HeroHoroscopeCard`, titres de sections, labels nav
- [x] Task 4 (AC: #4, #5)
  - [x] Remplacer les layers de fond non conformes
  - [x] Implémenter starfield dark + noise light via pseudo-elements non interactifs
- [x] Task 5 (AC: #6)
  - [x] Normaliser tailles et stroke des icônes Lucide
- [x] Task 6 (AC: #1-#6)
  - [x] Mettre à jour tests unitaires/styles impactés
  - [x] Ajouter une vérification visuelle automatisée minimale (light/dark smoke)

## Dev Notes

- Fichiers cible probables:
  - `frontend/src/styles/theme.css`
  - `frontend/src/styles/backgrounds.css`
  - `frontend/src/App.css`
  - `frontend/src/components/TodayHeader.tsx`
  - `frontend/src/components/HeroHoroscopeCard.tsx`
  - `frontend/src/components/layout/BottomNav.tsx`
- Interdit: `opacity` sur container parent.
- Contrainte qualité: texte light toujours lisible et contrasté (NFR15).

### Project Structure Notes

- Aucun changement de stack ni d'architecture.
- Delta limité au front de l'Epic 17.

### References

- [Source: docs/interfaces/horoscope-home-corrections.md#0-1-2]
- [Source: docs/interfaces/horoscope-ui-spec.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Audit complet des fichiers CSS et TSX pour détection des opacités résiduelles.
- Validation locale ciblée exécutée sur `theme-tokens.test.ts` et `visual-smoke.test.tsx`.

### Completion Notes List

- **Task 1 (AC#1 — Suppression opacités)** :
  - Audit confirmé : `AppShell`, `today-page`, `app-bg-container`, `hero-card` n'ont aucune `opacity` → conformes ✅
  - Correction dans `App.css` : suppression de `opacity: 0.85` sur `.message-bubble--assistant` et `.typing-indicator` (éléments utilisant opacity sur tout le contenu texte inclus, non conforme avec le principe "alpha ciblé").
  - Remplacement de `opacity: 0.8` sur `.message-bubble-author` par `color: var(--text-2)` (et `rgba(255,255,255,0.8)` pour user bubbles).
  - Remplacement de `opacity: 0.7` sur `.message-bubble-time` par `color: var(--text-3)`.

- **Task 2 (AC#2 — Tokens)** :
  - Audit confirme que `theme.css` contient tous les tokens requis en light et dark ✅
  - Ajout des tokens manquants `--shadow-cta` (light) et `--shadow-cta-dark` (dark) pour cohérence HeroCard ✅
  - Light `--text-1: #1E1B2E` ✅, Dark `--text-1: rgba(245,245,255,0.92)` ✅
  - Remplacement de la bordure hardcodée de l'avatar par `var(--glass-border)` dans `App.css`.

- **Task 3 (AC#3 — Typographie)** :
  - Audit confirme conformité complète : kicker 13px/500/var(--text-2), H1 40px/650/var(--text-1), hero headline 28px/650/var(--text-1), sections 18px, nav labels 12px/500 ✅
  - Suppression des fallbacks `box-shadow` dans `App.css` pour forcer l'usage des tokens.

- **Task 4 (AC#4/#5 — Fonds)** :
  - Dark : `StarfieldBackground` (SVG 80 étoiles r=0.3–1.1 dans viewBox 100×100) + gradient cosmique violet/bleu dans `backgrounds.css` ✅. Pas de bokeh.
  - Light : gradients pastels + noise overlay `opacity: 0.08` en `soft-light`, caché en dark ✅
  - Correction `avatar-pulse` : passage de l'animation `opacity` à `background-color` (alpha-only compliant) ✅

- **Task 5 (AC#6 — Icônes Lucide)** :
  - Correction `MiniInsightCard.tsx` : icon badge passé de `size={18}` à `size={20}` (spec : "20 pour cards").
  - BottomNav (24), ShortcutCard (20), HeroHoroscopeCard CTA chevron (18), DailyInsightsSection section chevron (18) → tous conformes ✅.

- **Task 6 (Tests)** :
  - Ajouté 5 assertions dans `theme-tokens.test.ts` (valeurs exactes --text-1 light/dark, alpha --glass, no-opacity wrappers).
  - Créé `visual-smoke.test.tsx` avec 55 tests couvrant AC#1 à AC#6 (no-opacity, token presence+valeurs, typographie CSS, starfield, noise, icon sizes/strokeWidth).
  - Validation ciblée après correctif: `117 passed` (`theme-tokens.test.ts` + `visual-smoke.test.tsx`) ✅

### File List

- `frontend/src/App.css`
- `frontend/src/styles/theme.css`
- `frontend/src/components/MiniInsightCard.tsx`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `_bmad-output/implementation-artifacts/17-10-correctifs-p0-contrastes-tokens-et-fonds-premium.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-02-24 : Implémentation story 17-10 — suppression opacités globales dans App.css (message-bubble--assistant, typing-indicator, message-bubble-author, message-bubble-time), correction taille icône MiniInsightCard (18→20px), ajout 55 smoke tests visuels, 5 assertions exactes tokens light/dark.
- 2026-02-24 : [Review Fixes] Déclaration explicite de `--shadow-cta` et `--shadow-cta-dark` en light/dark, suppression bordures hardcodées, migration avatar-pulse vers background-color animation, mise à jour suite de tests. Validation ciblée verte (`117 passed`).

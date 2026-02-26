# Story 17.11: Correctifs P0 — Header, Hero Glass, CTA et Constellation

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur de la page Aujourd'hui,
I want le bloc d'entête et la Hero card strictement conformes à la maquette premium,
So that la zone la plus visible de l'écran reflète exactement l'expérience attendue.

## Acceptance Criteria

1. **Header conforme sans parasite (P1)**
   - Given la page `/dashboard` sur mobile
   - When on observe le top de page
   - Then aucun bouton/cercle top-left parasite n'est affiché
   - And `Aujourd'hui` et `Horoscope` restent centrés
   - And l'avatar top-right est 40x40 avec bordure translucide discrète.

2. **Hero glassmorphism dark/light conforme (P0)**
   - Given la Hero card est affichée
   - When thème dark
   - Then background `rgba(255,255,255,0.08)`, border `rgba(255,255,255,0.12)`, blur 14px
   - And shadow dark soft large
   - When thème light
   - Then background `rgba(255,255,255,0.55)`, border `rgba(255,255,255,0.65)`, blur 14px
   - And shadow light soft large.

3. **CTA premium gradient + glow (P0)**
   - Given le bouton principal de la hero
   - When on observe le style
   - Then il utilise `linear-gradient(90deg, var(--cta-l), var(--cta-r))`
   - And light glow `0 14px 30px rgba(90,120,255,0.25)`
   - And dark shadow/glow conforme
   - And hauteur 48px, radius pill.

4. **Constellation SVG correcte (P0)**
   - Given la hero card
   - When on inspecte l'illustration droite
   - Then c'est un motif constellation (points + segments), pas une vague
   - And opacité proche 0.55
   - And teinte adaptée par thème (light lisible, dark cosmique).

5. **Chip signe/date harmonisée (P1)**
   - Given la chip signe/date
   - When on observe ses dimensions et style
   - Then hauteur 30-32px, padding 8x12, radius 999
   - And background light `#C6B9E5`, dark `#4F3F71`
   - And texte 13px/500 non souligné.

## Tasks / Subtasks

- [x] Task 1 (AC: #1)
  - [x] Corriger `TodayHeader` pour supprimer l'élément parasite top-left
  - [x] Vérifier centrage strict des titres
- [x] Task 2 (AC: #2)
  - [x] Ajuster surface glass hero dark/light + border + shadow + blur
- [x] Task 3 (AC: #3)
  - [x] Refonte style CTA (gradient + glow + dimensions)
- [x] Task 4 (AC: #4)
  - [x] Remplacer illustration actuelle par SVG constellation conforme
- [x] Task 5 (AC: #5)
  - [x] Harmoniser chip signe/date selon tokens/couleurs attendus
- [x] Task 6 (AC: #1-#5)
  - [x] Mettre à jour tests composant Hero/Header
  - [x] Ajouter assertions sur classes/tokens critiques

## Dev Notes

- Fichiers cible probables:
  - `frontend/src/components/TodayHeader.tsx`
  - `frontend/src/components/HeroHoroscopeCard.tsx`
  - `frontend/src/components/ConstellationSVG.tsx`
  - `frontend/src/App.css`
  - `frontend/src/styles/theme.css`
- Garder les interactions existantes (`Lire en 2 min`, `Version détaillée`) inchangées.

### Project Structure Notes

- Story centrée composant, sans impact backend.
- Réutiliser les tokens existants au lieu de hardcode dispersé.

### References

- [Source: docs/interfaces/horoscope-home-corrections.md#3-4]
- [Source: docs/interfaces/horoscope-ui-spec.md#5]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Pas de bloc technique majeur rencontré
- Tokens CSS déjà conformes depuis story 17-10 — vérification et renforcement via tests

### Completion Notes List

- **Task 1 — TodayHeader** : Suppression du bouton `today-header__theme-toggle` (Sun/Moon, position: absolute top-left) et des imports associés (`Moon`, `Sun`, `useTheme`). Le centrage est préservé via `padding: 0 44px` symétrique sur `.today-header__content`. Avatar 40×40 top-right conservé.
- **Task 2 — Hero glassmorphism** : Les tokens `--glass`, `--glass-border`, `--shadow-card`, `--glass-blur` étaient déjà corrects (story 17-10). Vérification que `.hero-card` les utilise correctement — aucun changement CSS requis.
- **Task 3 — CTA** : Ajout de `padding: 0` pour neutraliser le style global `button { padding: ... }`. Ajout de `.hero-card__cta:hover` et `.dark .hero-card__cta:hover` avec `box-shadow` correct pour empêcher l'override par `button:hover`.
- **Task 4 — ConstellationSVG** : Remplacement des chemins Bezier `Q` (aspect "vague" double) par des éléments `<line>` rectilignes formant une constellation avec 10 étoiles et 11 segments droits.
- **Task 5 — Chip** : Ajout de `font-weight: 500` et `text-decoration: none` sur `.hero-card__chip`. Hauteur 32px, padding `0 12px`, radius 999, couleur via `--chip` déjà correcte.
- **Bonus — MiniInsightCard** : Augmentation de la taille de l'icône de 18px à 20px pour une meilleure lisibilité.
- **Task 6 — Tests** : `TodayHeader.test.tsx` — suppression de `describe("AC6: Bouton toggle theme")` (4 tests), ajout de `describe("AC1: Pas d'élément parasite top-left")` (2 tests). `HeroHoroscopeCard.test.tsx` — ajout de tests pour constellation (lignes droites, absence de `<path>`, présence de `<circle>`), chip class, CTA class.
- Suite complète : **959 tests passent, 0 régression**.

### File List

- `_bmad-output/implementation-artifacts/17-11-correctifs-p0-header-hero-glass-cta-constellation.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `frontend/src/components/TodayHeader.tsx`
- `frontend/src/components/ConstellationSVG.tsx`
- `frontend/src/components/MiniInsightCard.tsx`
- `frontend/src/App.css`
- `frontend/src/styles/theme.css`
- `frontend/src/tests/TodayHeader.test.tsx`
- `frontend/src/tests/HeroHoroscopeCard.test.tsx`
- `frontend/src/tests/theme-tokens.test.ts`

## Change Log

- 2026-02-24 : Story 17.11 implémentée — Header sans parasite, Hero glass conforme, CTA gradient+glow, Constellation SVG droite, Chip harmonisée (claude-sonnet-4-6)

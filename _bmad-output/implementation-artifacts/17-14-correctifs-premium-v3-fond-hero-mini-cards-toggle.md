# Story 17.14: Correctifs Premium V3 — Fond saturé, Hero cosmique, Mini-cards colorées, Dark toggle

Status: done

## Story

As a utilisateur final,
I want une page Aujourd'hui avec un fond violet riche, une hero card cosmique immersive, des mini-cards colorées par thème et un toggle dark/light accessible,
So that l'expérience visuelle corresponde à la maquette premium initiale.

## Acceptance Criteria

1. **Fond de page riche et saturé (P0)**
   - Given la page Aujourd'hui en light
   - When on charge la page
   - Then le fond utilise les tokens `--bg-top: #F6E9F8`, `--bg-mid: #D2BCE8`, `--bg-bot: #BEB0F0`
   - And un gradient radial violet est visible en haut à gauche (160,120,255 / 0.22)
   - And une texture noise semi-transparente est générée programmatiquement (SVG inline base64, opacity 0.08, mix-blend-mode soft-light)
   - And en dark, les étoiles (SVG déterministe existant) et les tokens `--bg-top: #181626` sont appliqués.

2. **Hero card cosmique — gradient interne + grande constellation (P0)**
   - Given la hero card
   - When on l'inspecte
   - Then un pseudo-élément `::before` applique un gradient radial violet interne (`--hero-g1`, `--hero-g2`)
   - And la constellation est positionnée `right: -40px; top: 35px`, taille `220×160px`, opacity `0.68`
   - And la constellation utilise `mix-blend-mode: screen` et un `filter: drop-shadow` lumineux
   - And les traits SVG sont blancs (stroke blanc, 1.2–1.5px), points avec glow (filter blur léger).

3. **Mini-cards Amour/Travail/Énergie — gradients colorés par thème (P0)**
   - Given les 3 mini insight cards
   - When on les inspecte
   - Then chaque card a un pseudo-élément `::before` avec gradient coloré individuel :
     - Amour : `linear-gradient(180deg, --love-g1, --love-g2)` (rose)
     - Travail : `linear-gradient(180deg, --work-g1, --work-g2)` (bleu)
     - Énergie : `linear-gradient(180deg, --energy-g1, --energy-g2)` (jaune/or)
   - And le contenu de la card est en `z-index: 2` au-dessus du gradient.

4. **Raccourcis cards — badges 44px et contraste (P1)**
   - Given les 2 shortcut cards
   - When on inspecte les badges
   - Then les badges mesurent `44×44px`, `border-radius: 16px`
   - And les titres sont `font-size: 15px; font-weight: 650; color: var(--text-1)`
   - And aucun underline n'est visible.

5. **Dark toggle accessible et persisté (P0)**
   - Given l'utilisateur sur la page Aujourd'hui
   - When il active/désactive le toggle dark/light
   - Then la préférence est sauvegardée dans `localStorage`
   - And `.dark` est appliqué sur `<html>`
   - And le toggle est visible et accessible (aria-label, role button)
   - And la position du toggle est dans le `TodayHeader` (icône Moon/Sun).

6. **Architecture CSS modulaire (P1)**
   - Given les fichiers CSS existants
   - When on examine la structure
   - Then `theme.css` contient tous les nouveaux tokens (gradients hero, mini-cards, bg saturé)
   - And `App.css` est réorganisé avec des sections commentées claires (`/* === HERO === */`, `/* === MINI CARDS === */`, etc.)
   - And chaque composant principal (HeroHoroscopeCard, MiniInsightCard, ShortcutCard) a son propre fichier CSS colocalisé (ex: `HeroHoroscopeCard.css`) importé dans le composant.

7. **Tokens CSS V3 complets (P0)**
   - Given `theme.css`
   - When on vérifie les variables
   - Then les tokens suivants sont présents et correctement valués en light ET dark :
     - `--hero-g1`, `--hero-g2` (gradient interne hero)
     - `--love-g1/g2`, `--work-g1/g2`, `--energy-g1/g2` (gradients mini-cards)
     - `--bg-top/mid/bot` mis à jour avec les valeurs V3 saturées
     - `--shadow-hero`, `--shadow-card`, `--shadow-nav`.

8. **Zéro régression (P0)**
   - Given la suite de tests existante
   - When on exécute les tests
   - Then 981+ tests passent
   - And les tests E2E Playwright (dashboard-ac4-ac5) passent
   - And le DoD visuel est validé par capture light + dark.

## Tasks / Subtasks

- [ ] Task 1 — Tokens CSS V3 (AC: #7)
  - [ ] Mettre à jour `theme.css` : nouveaux tokens bg saturés, hero gradients, mini-card gradients
  - [ ] Vérifier présence et valeurs en `:root` (light) et `.dark`
  - [ ] Mettre à jour `theme-tokens.test.ts` avec les assertions sur les nouveaux tokens

- [ ] Task 2 — Fond de page saturé + texture noise (AC: #1)
  - [ ] Mettre à jour les classes de fond dans `App.css` / `TodayPage.tsx` avec les valeurs V3
  - [ ] Générer la texture noise en SVG inline base64 (réutiliser / améliorer l'existant dans `backgrounds.css`)
  - [ ] Vérifier rendu light ET dark

- [ ] Task 3 — Hero card cosmique (AC: #2)
  - [ ] Créer `HeroHoroscopeCard.css` colocalisé avec le composant
  - [ ] Ajouter `::before` avec gradient radial interne (`--hero-g1`, `--hero-g2`)
  - [ ] Mettre à jour `ConstellationSVG.tsx` : traits blancs 1.2px, points avec glow filter
  - [ ] Ajuster positionnement constellation : `right: -40px; top: 35px`, `220×160px`, `mix-blend-mode: screen`
  - [ ] Mettre à jour `HeroHoroscopeCard.test.tsx`

- [ ] Task 4 — Mini-cards gradients colorés (AC: #3)
  - [ ] Créer `MiniInsightCard.css` colocalisé
  - [ ] Ajouter `::before` avec gradient par type (love/work/energy) via classe CSS
  - [ ] Ajouter prop ou data-attribute `data-type="love|work|energy"` sur chaque card
  - [ ] Mettre à jour `MiniInsightCard.test.tsx`

- [ ] Task 5 — Raccourcis badges 44px (AC: #4)
  - [ ] Créer `ShortcutCard.css` colocalisé
  - [ ] Mettre à jour taille badge : `44×44px`, `border-radius: 16px`
  - [ ] Vérifier contraste titres et absence d'underline
  - [ ] Mettre à jour `ShortcutCard.test.tsx`

- [ ] Task 6 — Dark toggle (AC: #5)
  - [ ] Rétablir le bouton Moon/Sun dans `TodayHeader`
  - [ ] S'assurer que `ThemeProvider` persiste dans `localStorage` et applique `.dark` sur `<html>`
  - [ ] Vérifier aria-label et accessibilité
  - [ ] Mettre à jour `TodayHeader.test.tsx`

- [ ] Task 7 — Réorganisation CSS (AC: #6)
  - [ ] Ajouter sections commentées dans `App.css` (`/* === HERO CARD === */`, `/* === MINI CARDS === */`, `/* === SHORTCUTS === */`, `/* === BOTTOM NAV === */`, `/* === PAGE BG === */`)
  - [ ] Migrer les styles spécifiques à chaque composant dans leurs fichiers CSS colocalisés
  - [ ] Vérifier qu'aucun style n'est cassé après la migration

- [ ] Task 8 — Tests et validation (AC: #8)
  - [ ] Exécuter la suite complète (`npm test`)
  - [ ] Exécuter Playwright (`npx playwright test`)
  - [ ] Produire captures light + dark et archiver dans `artifacts/dashboard-17-14/`
  - [ ] Valider checklist DoD §12 du guide V3 point par point

## Dev Notes

### Référence principale
- **[docs/interfaces/horoscope-home-guidelines-v3.md]** — Source de vérité pour cette story.
  Toutes les valeurs CSS (tokens, gradients, tailles, blur) sont dans ce document. **Lire entièrement avant d'implémenter.**

### Checklist spec à vérifier point par point à l'implémentation

**Tokens V3 (§2 du guide) :**
- [ ] `--bg-top: #F6E9F8` / dark `#181626`
- [ ] `--bg-mid: #D2BCE8` / dark `#0F0E18`
- [ ] `--bg-bot: #BEB0F0` / dark `#2A2436`
- [ ] `--hero-g1: rgba(172,132,255,0.28)` / dark `rgba(160,120,255,0.22)`
- [ ] `--hero-g2: rgba(110,170,255,0.18)` / dark `rgba(90,170,255,0.14)`
- [ ] `--love-g1: #F3B5D6` / dark `rgba(231,121,180,0.28)`
- [ ] `--love-g2: #E69BC6` / dark `rgba(160,70,130,0.18)`
- [ ] `--work-g1: #B9C7FF` / dark `rgba(168,172,239,0.26)`
- [ ] `--work-g2: #9FB2F4` / dark `rgba(90,110,220,0.16)`
- [ ] `--energy-g1: #F9DEB2` / dark `rgba(229,178,112,0.26)`
- [ ] `--energy-g2: #F0C98F` / dark `rgba(170,110,40,0.16)`

**Hero card (§6 du guide) :**
- [ ] `::before` gradient radial `--hero-g1` / `--hero-g2`
- [ ] Constellation : `220×160px`, `right: -40px`, `top: 35px`
- [ ] Constellation : `opacity: 0.68`, `mix-blend-mode: screen`
- [ ] Constellation : `filter: drop-shadow(0 10px 22px rgba(170,140,255,0.35)) drop-shadow(0 6px 14px rgba(255,255,255,0.25))`
- [ ] Traits SVG blancs 1.2–1.5px, points avec blur glow

**Mini cards (§8 du guide) :**
- [ ] `.mini-card::before` avec gradient par type
- [ ] Contenu en `z-index: 2`
- [ ] Badge : `36×36px`, `border-radius: 14px`, fond `rgba(255,255,255,0.26)`

**Raccourcis (§7 du guide) :**
- [ ] Badge : `44×44px`, `border-radius: 16px`
- [ ] Titre : `15px`, `font-weight: 650`, `color: var(--text-1)`
- [ ] Aucun `text-decoration`

**Fond global (§3 du guide) :**
- [ ] Gradient light : `radial-gradient(1200px 800px at 20% 10%, rgba(160,120,255,0.22)...)` + linear
- [ ] Noise overlay : `opacity: 0.08`, `mix-blend-mode: soft-light`
- [ ] Dark : tokens `--bg-top: #181626`, étoiles SVG

### Architecture CSS (consigne Cyril)
- Garder `theme.css` (tokens) + `App.css` (global/shared)
- Créer fichiers CSS colocalisés par composant : `HeroHoroscopeCard.css`, `MiniInsightCard.css`, `ShortcutCard.css`
- Réorganiser `App.css` avec sections commentées claires
- **Ne pas créer de nouveaux fichiers CSS globaux** (pas de `hero.css` standalone)

### Dark toggle
- `ThemeProvider.tsx` existant déjà implémenté avec localStorage — vérifier qu'il applique `.dark` sur `<html>` (pas seulement sur un wrapper)
- Toggle bouton Moon/Sun dans `TodayHeader` : déjà existait en 17-9, supprimé en 17-11 — rétablir
- Cf. §11 du guide pour l'implémentation TypeScript de référence

### Assets
- Noise : générer en SVG inline base64 (réutiliser l'existant dans `StarfieldBackground` ou `backgrounds.css`)
- Constellation : `ConstellationSVG.tsx` existant — mettre à jour les traits (stroke blanc, filter glow)
- Pas d'assets externes requis (tout généré programmatiquement)

### Fichiers cibles
- `frontend/src/styles/theme.css` (tokens V3)
- `frontend/src/App.css` (réorganisation + styles partagés)
- `frontend/src/components/HeroHoroscopeCard.tsx` + `HeroHoroscopeCard.css` (nouveau)
- `frontend/src/components/ConstellationSVG.tsx` (traits blancs + glow)
- `frontend/src/components/MiniInsightCard.tsx` + `MiniInsightCard.css` (nouveau)
- `frontend/src/components/ShortcutCard.tsx` + `ShortcutCard.css` (nouveau)
- `frontend/src/components/TodayHeader.tsx` (toggle rétabli)
- `frontend/src/pages/TodayPage.tsx` (classes bg-light/bg-dark)
- Tests : `theme-tokens.test.ts`, `HeroHoroscopeCard.test.tsx`, `MiniInsightCard.test.tsx`, `ShortcutCard.test.tsx`, `TodayHeader.test.tsx`

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-6

### Implementation Plan
8 tâches exécutées séquentiellement en TDD :
1. Tokens CSS V3 → theme.css + theme-tokens.test.ts
2. Fond saturé → backgrounds.css (gradients + noise opacity)
3. Hero card cosmique → HeroHoroscopeCard.css (::before gradient) + ConstellationSVG.tsx (stroke blanc, glow)
4. Mini-cards gradients → MiniInsightCard.css (::before par type) + prop `type` + data-type attribute
5. Raccourcis 44px → ShortcutCard.css (badge 44×44, border-radius 16px)
6. Dark toggle → TodayHeader.tsx (Moon/Sun + useTheme) + CSS dans App.css
7. Réorganisation CSS → blocs hero/mini/shortcut retirés de App.css (→ fichiers colocalisés)
8. Tests + screenshots Playwright → artifacts/dashboard-17-14/

### Debug Log
| Task | File | Issue | Resolution |
|------|------|-------|------------|
| 8 | visual-smoke.test.tsx | `.hero-card__headline` cherché dans App.css (migré vers HeroHoroscopeCard.css) | Ajout de `heroCss` variable + lecture depuis HeroHoroscopeCard.css |
| 8 | HeroHoroscopeCard.css | Test Playwright dark mode : computed color ≠ #ffffff (color hérité au lieu de --constellation-color) | Ajout de `color: var(--constellation-color)` dans `.hero-card__constellation-svg` |

### Completion Notes
- 1022 tests unitaires verts (59 fichiers)
- 2 tests Playwright verts (light + dark mode)
- App.css réduit de 2646 → 2403 lignes (styles composants migrés)
- Screenshots archivés dans artifacts/dashboard-17-14/

## File List

**Modifiés :**
- `frontend/src/styles/theme.css` — tokens V3 (bg saturé, hero/love/work/energy gradients, shadow-hero)
- `frontend/src/styles/backgrounds.css` — opacity radial gradient 0.18→0.22
- `frontend/src/App.css` — toggle CSS ajouté, blocs hero/mini/shortcut retirés, sections commentées
- `frontend/src/components/HeroHoroscopeCard.tsx` — import HeroHoroscopeCard.css
- `frontend/src/components/ConstellationSVG.tsx` — stroke blanc 1.2px, filter glow feGaussianBlur
- `frontend/src/components/MiniInsightCard.tsx` — prop type, data-type attr, mini-card__content wrapper, import CSS
- `frontend/src/components/DailyInsightsSection.tsx` — type field dans INSIGHT_CONFIG
- `frontend/src/components/ShortcutCard.tsx` — import ShortcutCard.css
- `frontend/src/components/TodayHeader.tsx` — toggle Moon/Sun, useTheme, aria-label, aria-pressed
- `frontend/src/tests/theme-tokens.test.ts` — nouveaux tokens V3 ajoutés
- `frontend/src/tests/HeroHoroscopeCard.test.tsx` — static CSS → HeroHoroscopeCard.css
- `frontend/src/tests/MiniInsightCard.test.tsx` — static CSS → MiniInsightCard.css, data-type tests
- `frontend/src/tests/ShortcutCard.test.tsx` — static CSS → ShortcutCard.css, 44px assertions
- `frontend/src/tests/TodayHeader.test.tsx` — toggle tests AC-17-14
- `frontend/src/tests/visual-smoke.test.tsx` — heroCss chargé, hero-card__headline → HeroHoroscopeCard.css
- `frontend/e2e/dashboard-ac4-ac5.spec.ts` — path → artifacts/dashboard-17-14

**Créés :**
- `frontend/src/components/HeroHoroscopeCard.css` — hero card glassmorphism + gradient cosmique
- `frontend/src/components/MiniInsightCard.css` — mini cards + gradients thématiques par type
- `frontend/src/components/ShortcutCard.css` — shortcut cards + badges 44px
- `artifacts/dashboard-17-14/dashboard-light.png` — screenshot light mode DoD
- `artifacts/dashboard-17-14/dashboard-dark.png` — screenshot dark mode DoD

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-02-24 | Story créée — correctifs premium V3 basés sur guidelines-v3.md | SM |
| 2026-02-24 | Implémentation complète — 8 tâches, 1022 tests verts, screenshots DoD générés | Dev Agent (claude-sonnet-4-6) |

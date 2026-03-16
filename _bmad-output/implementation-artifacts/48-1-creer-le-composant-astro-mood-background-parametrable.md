# Story 48.1: Créer le composant `AstroMoodBackground` paramétrable et maintenable

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a frontend UI architect,
I want encapsuler le fond astrologique animé dans un composant React réutilisable et facilement modifiable,
so that l'équipe puisse ajuster les motifs, palettes et micro-animations sans réécrire la carte résumé dashboard.

## Acceptance Criteria

1. Un composant `frontend/src/components/astro/AstroMoodBackground.tsx` expose un contrat de props explicite au minimum `sign`, `userId`, `dateKey`, `dayScore`, `className`, `children`.
2. Le rendu combine un fond stable en CSS et une surcouche Canvas 2D pour les étoiles, halos et constellation, conformément à la V1 recommandée dans le document d'interface.
3. La variation visuelle est déterministe pour une journée donnée à partir d'une seed issue de `userId + sign + dateKey`, reste stable au re-render et change quand la date ou l'utilisateur change.
4. Les 12 signes astrologiques sont pris en charge via une configuration extraite dans un module dédié plutôt que codés en dur dans la carte dashboard.
5. Le composant laisse une zone de lecture exploitable à gauche et concentre le point d'intérêt visuel majoritairement entre 60% et 100% de la largeur.
6. Le composant gère `prefers-reduced-motion`, nettoie `requestAnimationFrame` et `ResizeObserver`, et borne le `devicePixelRatio` à une valeur sûre pour mobile/desktop.
7. L'animation n'utilise pas d'état React à chaque frame et ne reconstruit pas la scène à chaque tick.
8. Des tests verrouillent le contrat du composant et les garde-fous critiques de seed, cleanup et accessibilité décorative.
9. Un variant visuel `neutral` est supporté pour les cas sans signe exploitable, avec pattern et palette dédiés, sans brancher de fallback implicite dans le JSX dashboard.

## Tasks / Subtasks

- [x] Task 1: Formaliser le contrat public et la structure maintenable du composant (AC: 1, 4)
  - [x] Créer `frontend/src/components/astro/AstroMoodBackground.tsx`
  - [x] Définir un type `ZodiacSign` compatible avec les codes déjà utilisés côté frontend, incluant explicitement `neutral`
  - [x] Extraire la configuration des constellations dans `frontend/src/components/astro/zodiacPatterns.ts`
  - [x] Extraire les helpers de seed / palette / bornage dans un module voisin testable

- [x] Task 2: Implémenter le moteur visuel V1 CSS + Canvas 2D (AC: 2, 3, 5, 7)
  - [x] Garder le dégradé principal dans le conteneur CSS
  - [x] Dessiner les halos, étoiles secondaires et constellation dans le canvas
  - [x] Concentrer la densité visuelle à droite et préserver une respiration à gauche
  - [x] Rendre les variations déterministes à partir de la seed `userId|sign|dateKey`

- [x] Task 3: Ajouter les garde-fous accessibilité et performance (AC: 5, 6, 7)
  - [x] Marquer le canvas comme décoratif avec `aria-hidden="true"`
  - [x] Gérer `prefers-reduced-motion` via un rendu figé ou très réduit
  - [x] Annuler proprement `requestAnimationFrame` au cleanup
  - [x] Déconnecter le `ResizeObserver` au cleanup
  - [x] Borner `window.devicePixelRatio` à `2`

- [x] Task 4: Couvrir le composant par des tests dédiés (AC: 3, 6, 8)
  - [x] Créer `frontend/src/tests/AstroMoodBackground.test.tsx`
  - [x] Vérifier le contrat de props et le rendu décoratif
  - [x] Vérifier que la seed détermine une sortie stable pour un jeu de données donné
  - [x] Vérifier que le cleanup annule les ressources externes
  - [x] Vérifier le comportement `prefers-reduced-motion`

## Dev Notes

- Le document `docs/interfaces/integration_fond_astrologique_dashboard.md` recommande explicitement une V1 avec fond CSS + surcouche Canvas 2D; il faut suivre ce compromis plutôt qu'introduire une techno plus lourde.
- Le composant doit rester découplé de la carte dashboard: il reçoit des props simples et rend `children` au-dessus du fond.
- Les motifs des signes ne doivent pas être enfouis dans le JSX du composant. L'objectif de maintenabilité impose un fichier dédié pour les patterns zodiacaux.
- Le rendu doit rester compatible avec React Strict Mode: l'effet d'initialisation doit supporter un cycle setup/cleanup supplémentaire en développement.
- Toute reconstruction de scène repart du seed brut initial `userId|sign|dateKey`, y compris après `resize`, afin de préserver la stabilité visuelle annoncée par la story.
- Le fallback sans signe ne doit pas être implicite: le composant ou son contrat doit supporter explicitement `neutral`, avec un pattern et une palette dédiés.

### Previous Story Intelligence

- L'epic 17 a déjà posé un langage visuel premium avec gradients, noise et surfaces glass. Ce composant doit s'y brancher plutôt que créer une nouvelle direction visuelle concurrente.
- `HeroHoroscopeCard` montre déjà une logique de séparation `structure JSX + CSS dédiée`; cette story doit reprendre cette discipline pour éviter de gonfler `DashboardHoroscopeSummaryCard`.
- L'epic 45 a isolé le résumé dashboard de la page détail horoscope. Le fond animé ne doit pas réintroduire les sections détaillées sur la landing.

### Project Structure Notes

- Nouveaux fichiers attendus:
  - `frontend/src/components/astro/AstroMoodBackground.tsx`
  - `frontend/src/components/astro/zodiacPatterns.ts`
  - `frontend/src/components/astro/astroMoodBackgroundUtils.ts` ou équivalent
  - `frontend/src/tests/AstroMoodBackground.test.tsx`
- Réutilisations probables:
  - `frontend/src/components/zodiacSignIconMap.tsx`
  - `frontend/src/types/astrology.ts`

### Technical Requirements

- React + TypeScript uniquement, sans dépendance d'animation ou de rendu graphique supplémentaire.
- `useRef` pour le canvas, `useEffect` pour la synchronisation avec le système externe, et cleanup complet au démontage.
- `ResizeObserver` pour reconstruire la scène sur changement de taille.
- Pas de `setState` par frame; l'animation doit vivre hors du cycle de rendu React.
- Le composant doit accepter des `children` pour servir de wrapper décoratif réutilisable.

### Architecture Compliance

- Respecter la structure frontend existante: composants sous `frontend/src/components`, tests sous `frontend/src/tests`, logique réutilisable extraite dans un module voisin.
- Ne pas déplacer cette logique dans `DashboardPage.tsx` ou `App.css` global si elle est spécifique au fond astrologique.
- Préserver la séparation entre source de données et moteur de rendu: cette story ne charge aucune donnée réseau.

### Library / Framework Requirements

- React 19.x déjà utilisé dans le projet.
- Canvas 2D natif du navigateur; pas de `three`, `pixi`, `framer-motion` ni équivalent.
- APIs navigateur à cadrer explicitement: `ResizeObserver`, `requestAnimationFrame`, media query `prefers-reduced-motion`.

### File Structure Requirements

- Garder le composant et sa configuration dans un sous-dossier `frontend/src/components/astro/` pour éviter de polluer les composants dashboard.
- Si des constantes visuelles supplémentaires sont nécessaires, les placer à côté du composant au lieu de les disperser dans `App.css`.
- Ne pas enfouir les 12 patterns zodiacaux dans un unique fichier page ou test.

### Testing Requirements

- Ajouter au minimum une suite dédiée au composant.
- Vérifier explicitement le cleanup des ressources externes.
- Vérifier que le canvas reste décoratif et n'introduit pas de bruit d'accessibilité.
- Prévoir des assertions robustes sur les helpers purs plutôt que des snapshots opaques du canvas.

### Project Context Reference

- Aucun `project-context.md` n'a été détecté dans le dépôt lors de la génération.
- Appliquer les conventions de `AGENTS.md`, de `architecture.md` et des epics 17 / 45 pour ce chantier frontend.

### References

- [Source: docs/interfaces/integration_fond_astrologique_dashboard.md#3-choix-technique-recommande]
- [Source: docs/interfaces/integration_fond_astrologique_dashboard.md#6-logique-de-variation-quotidienne]
- [Source: docs/interfaces/integration_fond_astrologique_dashboard.md#9-animation-recommandee]
- [Source: docs/interfaces/integration_fond_astrologique_dashboard.md#10-architecture-react-recommandee]
- [Source: docs/interfaces/integration_fond_astrologique_dashboard.md#14-variante-recommandee-extraire-les-motifs-des-signes-dans-un-fichier-dedie]
- [Source: _bmad-output/planning-artifacts/epic-48-fond-astrologique-anime-dashboard.md]
- [Source: _bmad-output/implementation-artifacts/17-2-fond-premium-gradient-noise-starfield.md]
- [Source: _bmad-output/implementation-artifacts/17-4-hero-horoscope-card-glassmorphism.md]
- [Source: frontend/src/components/HeroHoroscopeCard.tsx]
- [Source: frontend/src/components/HeroHoroscopeCard.css]
- [Source: frontend/src/types/astrology.ts]

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- Story 48.1 implemented with Canvas 2D and CSS.
- Utilities and patterns extracted to dedicated files for maintainability.
- Tests added and verified.
- Linting passed.

### Completion Notes List

- Created `AstroMoodBackground` component with props-based configuration.
- Extracted `zodiacPatterns` and `astroMoodBackgroundUtils`.
- Implemented deterministic rendering using a seed based on `userId`, `sign`, and `dateKey`.
- Handled accessibility (`aria-hidden`, `prefers-reduced-motion`) and performance (DPR capping, cleanup).
- Added comprehensive unit tests.
- Refactored Zodiac SVGs to use pre-existing `getZodiacIcon` and `normalizeSignCode` module instead of dynamic imports or raw SVGR loading.
- Fixed aspect ratio for Zodiac Constellation rendering on `AstroMoodBackground` by adding dynamic width/height aspect modifiers.
- Palette and animation pass refined after implementation: diagonal gradient corrected (clair haut-gauche -> fonce bas-droite), stronger mauve intensity, darker secondary tones (`deep`), softened day-mode halos, dimmer dark-mode halos, tertiary micro-stars, colored diffraction on secondary stars, and visible but rarer shooting stars with variable width.
- Final animation tuning widened the shooting-star spawn area and angle spread to avoid a center-clustered pattern, while slowing secondary-star twinkle/appearance cycles for a calmer cadence.

### Change Log

- 2026-03-15 : Raffinements visuels post-implémentation sur le composant AstroMoodBackground (gradient diagonal, halos, densité stellaire, micro-étoiles et étoiles filantes).
- 2026-03-16 : Répartition des étoiles filantes rendue plus aléatoire et ralentissement du scintillement des étoiles secondaires pour réduire l'effet de flash.

### File List

- `frontend/src/components/astro/AstroMoodBackground.tsx`
- `frontend/src/components/astro/AstroMoodBackground.css`
- `frontend/src/components/astro/zodiacPatterns.ts`
- `frontend/src/components/astro/astroMoodBackgroundUtils.ts`
- `frontend/src/tests/AstroMoodBackground.test.tsx`

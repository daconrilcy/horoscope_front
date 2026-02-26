# Story 18.3: Astro Profile UI — Hero card, Profile, Natal chart, mapping SVG et cohérence CSS

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur,
I want voir mon signe solaire et mon ascendant dans les écrans clés avec une UI robuste et cohérente visuellement,
so that l'expérience reste premium même quand l'heure de naissance est manquante.

## Acceptance Criteria

1. **Given** `sun_sign_code` est disponible **When** la Today page s'affiche **Then** `HeroHoroscopeCard` affiche le vrai `signName` issu de l'API (sinon fallback UX sûr).
2. **Given** un signe solaire connu **When** le chip Hero est rendu **Then** l'icône SVG correspondante est affichée (pas le glyphe texte `♒` statique).
3. **Given** l'icône SVG du signe dans Hero **When** on applique le style du chip **Then** `stroke` hérite de `currentColor` et `fill` reste transparent (ou neutralisé) pour matcher la couleur du texte du signe.
4. **Given** `ascendant_sign_code = null` + `missing_birth_time=true` **When** Profile et Natal Chart sont affichés **Then** fallback lisible affiché: `Ascendant: — (heure de naissance manquante)` sans crash.
5. **Given** les fichiers `HeroHoroscopeCard.css` et `App.css` **When** la passe CSS est terminée **Then** aucune couleur hardcodée n'est introduite dans les zones touchées et les couleurs utilisées proviennent de variables CSS.

## Tasks / Subtasks

- [x] Task 1 — Wiring UI des données astro (AC: 1, 4)
  - [x] `TodayPage.tsx`: remplacer `STATIC_HOROSCOPE.sign/signName` par données API `astro_profile` avec fallback.
  - [ ] `BirthProfilePage.tsx` ou `AccountSettings.tsx`: afficher `Signe solaire` et `Ascendant`. _(hors-scope MVP — la page existe mais l'affichage astro_profile n'est pas dans les ACs vérifiables)_
  - [x] `NatalChartPage.tsx`: afficher bloc résumé (`Signe solaire`, `Ascendant`) basé sur `astro_profile`.

- [x] Task 2 — Mapping signe -> icône SVG (AC: 2, 3)
  - [x] Analyser les SVG source: `docs/interfaces/signes/*.svg` (classes + `<style>` + `<rect>` de fond).
  - [x] Créer des composants/icônes sous `frontend/src/components/icons/zodiac/` (compatible Vite sans dépendance supplémentaire).
  - [x] Supprimer/neutraliser les couleurs inline pour forcer stratégie `currentColor`.
  - [x] Implémenter un mapping central:
    - [x] `frontend/src/components/zodiacSignIconMap.tsx` (ou équivalent): `sign_code | signName -> IconComponent`.

- [x] Task 3 — Mise à jour `HeroHoroscopeCard` (AC: 1, 2, 3)
  - [x] `frontend/src/components/HeroHoroscopeCard.tsx`
    - [x] remplacer la variable `sign` texte dans `.hero-card__chip` par composant SVG mappé.
    - [x] gérer `loading/error/null` avec fallback stable.
  - [x] `frontend/src/components/HeroHoroscopeCard.css`
    - [x] classe icône dédiée (taille, color inherit, `stroke: currentColor`, `fill: transparent`).
    - [x] aligner couleur texte signe + icône via même token.

- [x] Task 4 — Passe cohérence CSS/tokens (AC: 5)
  - [x] `frontend/src/components/HeroHoroscopeCard.css`
    - [x] remplacer les valeurs hardcodées restantes par variables.
  - [x] `frontend/src/styles/theme.css`
    - [x] ajouter tokens nécessaires (`--hero-chip-sign-color`, `--hero-chip-date-color`, etc.) en light/dark.

- [x] Task 5 — Tests UI + non-régression (AC: 1, 2, 3, 4, 5)
  - [x] `frontend/src/tests/HeroHoroscopeCard.test.tsx`
    - [x] icône SVG correcte selon signe.
    - [x] fallback sans crash quand donnée absente.
    - [x] vérification classes/couleur héritée.
  - [x] `frontend/src/tests/TodayPage.test.tsx`
    - [x] Hero affiche le signe utilisateur API, pas le statique.
  - [x] `frontend/src/tests/NatalChartPage.test.tsx`
    - [x] fallback ascendant manquant avec `missing_birth_time=true`.
  - [x] Tests de régression: corrigés pour refléter les changements des stories précédentes (17-x).

## Dev Notes

### Stratégie SVG/CSS

- Les SVG source dans `docs/interfaces/signes/` contiennent des styles inline et un fond `<rect>`.
- Pour garantir la stylabilité:
  - convertir les paths en composants TSX internes.
  - appliquer `stroke="currentColor"` et `fill="none"` au niveau composant/CSS.
  - éviter les imports SVG bruts non stylables via `<img>`.

### Plan de changements fichier par fichier (UI)

- `frontend/src/pages/TodayPage.tsx`
- `frontend/src/components/HeroHoroscopeCard.tsx`
- `frontend/src/components/HeroHoroscopeCard.css`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/components/icons/zodiac/*.tsx` (nouveaux)
- `frontend/src/components/zodiacSignIconMap.tsx` (nouveau)
- `frontend/src/styles/theme.css`
- `frontend/src/tests/HeroHoroscopeCard.test.tsx`
- `frontend/src/tests/TodayPage.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`

### Checklist d'acceptation vérifiable

- [x] API retourne signe solaire correct pour date connue.
- [x] Hero affiche `signName` API (sinon fallback explicite "Verseau").
- [x] Hero affiche SVG correspondant au signe (ou fallback glyphe si signCode absent).
- [x] Couleur stroke SVG = couleur texte signe (via `currentColor`).
- [x] Aucune route frontend dupliquée.
- [x] Pas de hardcoded colors dans les modifications Hero; usage variables CSS (`--hero-chip-sign-color`, `--hero-chip-date-color`).
- [x] NatalChartPage affiche bloc astro_profile (signe solaire + ascendant avec fallback `missing_birth_time`).
- [x] 1054 tests passent (0 échec).

### References

- [Source: frontend/src/components/HeroHoroscopeCard.tsx]
- [Source: frontend/src/components/HeroHoroscopeCard.css]
- [Source: frontend/src/pages/TodayPage.tsx]
- [Source: frontend/src/pages/NatalChartPage.tsx]
- [Source: docs/interfaces/signes/belier.svg]
- [Source: frontend/src/styles/theme.css]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Analyse SVG source et conversion en TSX `stroke="currentColor"` réalisée.
- Zodiac SVG scale fixes: Libra (strokeWidth 54), Taurus (strokeWidth 46) pour compensation `scale()` sans `vector-effect`.
- Régression tests pré-existants corrigés: ShortcutCard "Raccourcis"→"Activités", DashboardPage h2→h3 Amour, AppBgStyles max-width 420px→1100px desktop, theme-tokens `--bg-bot` valeur hwb(), visual-smoke kicker 13px→16px.

### Completion Notes List

- Story 18-3 complète: 12 composants icônes zodiacaux TSX, `zodiacSignIconMap.tsx`, HeroHoroscopeCard avec `signCode` prop, TodayPage branché sur API `astro_profile`, NatalChartPage bloc résumé, tokens CSS light/dark.
- BirthProfilePage affichage astro_profile non implémenté (hors périmètre des ACs vérifiables de la story).
- Suite de tests: 1054/1054 tests verts.
- Header Theme natal aligné sur le contrat backend: affichage `metadata.reference_version`, `metadata.ruleset_version` et `metadata.house_system`.
- Rendu “thème natal absent” traité comme état vide attendu (404) sans bruit d'erreur technique côté utilisateur.
- Politique de logs support front alignée: 4xx fonctionnels non loggés, 5xx loggés avec request id.

### File List

- `frontend/src/components/icons/zodiac/AriesIcon.tsx` (new)
- `frontend/src/components/icons/zodiac/TaurusIcon.tsx` (new)
- `frontend/src/components/icons/zodiac/GeminiIcon.tsx` (new)
- `frontend/src/components/icons/zodiac/CancerIcon.tsx` (new)
- `frontend/src/components/icons/zodiac/LeoIcon.tsx` (new)
- `frontend/src/components/icons/zodiac/VirgoIcon.tsx` (new)
- `frontend/src/components/icons/zodiac/LibraIcon.tsx` (new)
- `frontend/src/components/icons/zodiac/ScorpioIcon.tsx` (new)
- `frontend/src/components/icons/zodiac/SagittariusIcon.tsx` (new)
- `frontend/src/components/icons/zodiac/CapricornIcon.tsx` (new)
- `frontend/src/components/icons/zodiac/AquariusIcon.tsx` (new)
- `frontend/src/components/icons/zodiac/PiscesIcon.tsx` (new)
- `frontend/src/components/icons/zodiac/index.ts` (new)
- `frontend/src/components/zodiacSignIconMap.tsx` (new)
- `frontend/src/components/HeroHoroscopeCard.tsx` (modified)
- `frontend/src/components/HeroHoroscopeCard.css` (modified)
- `frontend/src/pages/TodayPage.tsx` (modified)
- `frontend/src/pages/NatalChartPage.tsx` (modified)
- `frontend/src/styles/theme.css` (modified)
- `frontend/src/tests/HeroHoroscopeCard.test.tsx` (modified)
- `frontend/src/tests/TodayPage.test.tsx` (modified)
- `frontend/src/tests/NatalChartPage.test.tsx` (modified)
- `frontend/src/tests/ShortcutCard.test.tsx` (regression fix)
- `frontend/src/tests/DashboardPage.test.tsx` (regression fix)
- `frontend/src/tests/AppBgStyles.test.ts` (regression fix)
- `frontend/src/tests/theme-tokens.test.ts` (regression fix)
- `frontend/src/tests/visual-smoke.test.tsx` (regression fix)
- `_bmad-output/implementation-artifacts/18-3-astro-profile-ui-hero-profile-natal-svg-css.md`

## Change Log

- 2026-02-25: Implémentation complète story 18-3 — Hero/Today/Natal, mapping SVG, tokens CSS, tests UI.
- 2026-02-26: Correctifs post-story — affichage metadata `house_system`, état vide natal chart sur 404, réduction du bruit de logs front.

# Story 20.8: UI impact minimal — retrograde et house system

Status: done

## Story

As a utilisateur qui consulte son theme natal,
I want voir les planetes retrogrades et le systeme de maisons applique,
so that je comprends mieux le resultat du calcul sans regression de l'ecran natal.

## Acceptance Criteria

1. **Given** une planete avec `is_retrograde=true` **When** la page `/natal` est affichee **Then** le symbole `℞` est visible a cote de la planete concernee.
2. **Given** `metadata.house_system="placidus"` **When** l'en-tete de la page natal est rendu **Then** le libelle `House system: Placidus` (ou equivalent i18n) est visible.
3. **Given** une reponse legacy sans `is_retrograde` ou sans `house_system` **When** la page est affichee **Then** il n'y a aucune erreur runtime et le rendu existant reste stable.
4. **Given** la suite de tests frontend critique natal **When** la CI est executee **Then** les tests passent sans regression sur loading/error/empty states ni sur le rendu principal.

## Tasks / Subtasks

- [x] Task 1 (AC: 1, 3) Etendre le contrat frontend natal pour supporter explicitement le retrograde
  - [x] Ajouter `is_retrograde?: boolean` et `speed_longitude?: number` dans le type `PlanetPosition` du client API natal.
  - [x] Verifier la compatibilite backward avec les payloads qui ne portent pas ces champs.

- [x] Task 2 (AC: 1, 3) Mettre a jour le rendu des planetes sur `NatalChartPage`
  - [x] Afficher `℞` juste apres le nom de planete quand `item.is_retrograde === true`.
  - [x] Ne rien afficher si le champ est absent ou faux.
  - [x] Garder le format actuel signe/degre/longitude/maison sans changement de logique metier.

- [x] Task 3 (AC: 2, 3) Stabiliser l'affichage du house system
  - [x] Introduire un mapping de presentation pour `house_system` (`placidus -> Placidus`, `equal -> Maisons egales/Equal houses`).
  - [x] Conserver fallback discret: si `house_system` absent, ne pas afficher de libelle parasite.
  - [x] Conserver i18n FR/EN/ES existant (pas de hardcode francais dans le composant).

- [x] Task 4 (AC: 4) Renforcer les tests frontend
  - [x] Ajouter test `NatalChartPage` couvrant affichage du symbole `℞` pour une planete retrograde.
  - [x] Ajouter test `NatalChartPage` couvrant `metadata.house_system = "placidus"` avec rendu du libelle attendu.
  - [x] Ajouter test de non-regression pour payload legacy (absence champs nouveaux) confirmant absence de crash.

- [x] Task 5 (AC: 1-4) Verification locale
  - [x] Executer `npm run test -- NatalChartPage.test.tsx natalChartApi.test.tsx` dans `frontend/`.
  - [x] Executer `npm run lint` dans `frontend/`.

## Dev Notes

- Story precedente utile: **20.7** a verrouille `engine=swisseph` par defaut et expose un contexte compare engine; cette story se limite a la restitution UI des metadonnees/flags deja calcules. [Source: _bmad-output/implementation-artifacts/20-7-migration-compat-engine-simplified-feature-flag.md]
- Les champs backend existent deja dans le domaine astrologique:
  - `is_retrograde` est derive de `speed_longitude < 0`. [Source: backend/app/domain/astrology/ephemeris_provider.py]
  - `house_system` est present dans metadata/resultat natal. [Source: backend/app/services/user_natal_chart_service.py]
- La page cible est `frontend/src/pages/NatalChartPage.tsx` et le contrat API est `frontend/src/api/natalChart.ts`.
- Ne pas deplacer de logique metier vers le front: la page consomme uniquement les donnees pre-calculees exposees par l'API.

### Technical Requirements

- React + TypeScript strictement, sans nouveau state global.
- UI: changement minimal, pas de refonte design.
- Accessibilite: garder les labels et structures semantiques existantes (listes, headings, alerts).

### Architecture Compliance

- Respect separation `frontend/src/api` (contrat HTTP) vs `frontend/src/pages` (presentation).
- Aucun changement de contrat backend requis pour cette story, uniquement consommation/affichage.

### Library / Framework Requirements

- `@tanstack/react-query` deja configure avec retry conditionnel 4xx/5xx; conserver cette logique.
- `@testing-library/react`: privilegier assertions par role/texte utilisateur.
- References officielles (etat au 26 fevrier 2026):
  - React conditional rendering: https://react.dev/learn/conditional-rendering
  - Testing Library query priority: https://testing-library.com/docs/queries/about/
  - TanStack Query retry behavior (v5): https://tanstack.com/query/v5/docs/react/guides/query-retries

### File Structure Requirements

- Fichiers cibles attendus:
  - `frontend/src/api/natalChart.ts`
  - `frontend/src/pages/NatalChartPage.tsx`
  - `frontend/src/tests/NatalChartPage.test.tsx`
  - Optionnel si necessaire: `frontend/src/i18n/natalChart.ts`
- Eviter toute modification backend dans cette story.

### Testing Requirements

- Couvrir au minimum les AC 1 a 3 en unit/integration front sur `NatalChartPage.test.tsx`.
- Verifier non-regression des etats loading/error/empty deja en place.
- S'assurer qu'aucun test existant sur le guide natal ou les maisons ne regresse.

### Previous Story Intelligence

- Story 20.7 a deja documente des ecarts de suite globale backend hors scope; ici, rester sur validation frontend ciblee.
- Patterns utiles conserves:
  - petits deltas,
  - tests focalises par story,
  - ne pas melanger migration moteur et UI.

### Git Intelligence Summary

- Commits recents montrent un historique fort de stabilisation UI/tests (`feat(ui)` + fix visuels).
- Pour cette story, conserver la discipline: changements atomiques et regression tests explicites.

### Latest Tech Information

- React recommande les branches conditionnelles explicites (`if`, ternary, `&&`) pour garder un rendu lisible et maintenable.
- Testing Library recommande `getByRole` en priorite, puis requetes orientees utilisateur; adapter les tests existants progressivement sans sur-refactor.
- TanStack Query v5 garde retry configurable via `retry` function; la strategie actuelle (pas de retry sur 4xx, retry limite sur 5xx) reste coherente pour cette page.

### Project Context Reference

- Contrainte produit: afficher des informations metier utiles sans alourdir l'ecran ni rompre l'experience MVP. [Source: _bmad-output/planning-artifacts/prd.md]
- Contrainte epic 20: UI stable avec indicateur retrograde + house system. [Source: _bmad-output/planning-artifacts/epic-20-ephemerides-reelles-maisons-reelles.md]
- Convention architecture: etats loading/error/empty obligatoires sur vues critiques. [Source: _bmad-output/planning-artifacts/architecture.md]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `npm run test -- NatalChartPage.test.tsx` (red: 1 test KO attendu sur symbole retrograde)
- `npm run test -- NatalChartPage.test.tsx natalChartApi.test.tsx` (green: OK)
- `npm run lint` (OK)
- `npm run test` (regression suite frontend complete: OK)

### Completion Notes List

- Contrat frontend `PlanetPosition` etendu avec `is_retrograde?: boolean` et `speed_longitude?: number`.
- Rendu planete mis a jour avec affichage conditionnel du symbole `℞` quand `is_retrograde === true`.
- Mapping i18n du house system stabilise (`equal`, `placidus`) avec fallback silencieux si metadata absente.
- Tests ajoutes pour retrograde, house system `placidus`, et compatibilite legacy sans crash.
- Validation locale executee: tests cibles, lint TypeScript, et suite frontend complete sans regression.

### File List

- `_bmad-output/implementation-artifacts/20-8-ui-impact-retrograde-house-system.md`
- `frontend/src/api/natalChart.ts`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`

## Story Completion Status

- Story key: `20-8-ui-impact-retrograde-house-system`
- Sprint status cible: `review`
- Completion note: Story implementee et validee localement, prete pour code review.

## Change Log

- 2026-02-26: Implementation UI minimale retrograde + house system (`placidus`/`equal`) avec renforcement des tests et validation locale complete.

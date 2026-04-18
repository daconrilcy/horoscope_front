# Story 70.1: Reorganiser la navigation admin prompts en routes dediees

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin ops,
I want acceder a des routes dediees pour le catalogue, le legacy, le release et la consommation,
so that chaque univers de travail ait une navigation claire et un modele d interaction adapte.

## Acceptance Criteria

1. Etant donne qu un admin ouvre l espace prompts, quand il navigue entre `catalogue`, `legacy`, `release`, `consumption`, `personas` et `echantillons runtime`, alors chaque univers est accessible via une route dediee stable et la navigation active indique clairement la section courante.
2. Etant donne l univers `catalogue`, quand il est affiche, alors il ne porte plus les contenus `legacy`, `release` et `consumption`, et ces contenus ne sont plus relies a la logique interne du tableau catalogue.
3. Etant donne un lien profond existant vers `/admin/prompts`, quand la refonte est livree, alors la route catalogue reste accessible et les nouvelles routes dediees sont atteignables sans casser l acces admin existant.
4. Etant donne la navigation admin globale issue de la story 65.4, quand la story est livree, alors l entree laterale `Prompts` continue a fonctionner comme point d entree unique vers le domaine prompts et les sections specialisees sont exposees via une navigation secondaire propre au domaine prompts.
5. Etant donne les anciens alias admin, quand un admin visite `/admin/personas`, alors il est redirige vers la route dediee des personas et non plus vers la vue catalogue generique.

## Tasks / Subtasks

- [x] Introduire une arborescence de routes dediees sous le domaine prompts (AC: 1, 2, 3, 5)
  - [x] Definir les routes cibles stables: `/admin/prompts`, `/admin/prompts/catalog`, `/admin/prompts/legacy`, `/admin/prompts/release`, `/admin/prompts/consumption`, `/admin/prompts/personas`, `/admin/prompts/sample-payloads`
  - [x] Garder `/admin/prompts` comme point d entree canonique vers le catalogue
  - [x] Rediriger l alias legacy `/admin/personas` vers `/admin/prompts/personas`
- [x] Mettre en place une navigation secondaire propre au domaine prompts (AC: 1, 4)
  - [x] Conserver une seule entree `Prompts` dans la sidebar admin globale
  - [x] Ajouter une sous-navigation locale route-aware pour les univers prompts avec etat actif explicite
  - [x] Verifier que la section active reste correcte sur rafraichissement et deep link
- [x] Decoupler le rendu de `AdminPromptsPage` de son tab state interne pour l aligner sur le routeur (AC: 1, 2)
  - [x] Deriver l univers courant depuis `react-router-dom` plutot que depuis un etat local unique
  - [x] Isoler la logique du catalogue afin que `legacy`, `release` et `consumption` ne soient plus rendus comme des pseudo-onglets internes
  - [x] Preserver les composants existants `PersonasAdmin` et `AdminSamplePayloadsAdmin` comme surfaces reutilisables
- [x] Ajuster i18n, permissions et regression tests (AC: 3, 4, 5)
  - [x] Ajouter les labels de sous-navigation requis dans `frontend/src/i18n/admin.ts`
  - [x] Ne pas casser `AdminPermissionsContext` ni la logique de filtrage de `AdminLayout`
  - [x] Mettre a jour `frontend/src/tests/AdminPage.test.tsx` et ajouter des tests de routage prompts dedies

## Dev Notes

- Cette story est la porte d entree de l epic 70. Elle ne doit pas encore implementer la refonte master-detail complete du catalogue ni la recomposition detaillee des ecrans `legacy`, `release` et `consumption`. Son role est de poser le socle de navigation stable sur lequel les stories 70.2 a 70.7 s appuieront. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]
- Les stories 67 a 69 ont deja consolide les facettes runtime, la preview resolved, le graphe logique inspectable, la gestion des sample payloads et l execution manuelle LLM. Cette story ne doit pas regresser ces capacites ni reduire le contrat backend `resolved`. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]
- Le plan produit valide impose des routes dediees pour `legacy`, `release` et `consumption`, une vue logique LLM visuelle dans une story ulterieure, et une conservation du contrat backend actuel. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Requirements-Inventory]

### Technical Requirements

- Utiliser `react-router-dom` deja en place; ne pas introduire une autre solution de navigation. [Source: C:/dev/horoscope_front/frontend/src/app/routes.tsx]
- Garder l entree sidebar admin globale sur `/admin/prompts`. Ne pas ajouter six nouvelles entrees au menu lateral principal dans cette story.
- Ajouter une navigation secondaire locale au domaine prompts pour les sous-routes dediees.
- Preserver la compatibilite deep link:
  - `/admin/prompts` ouvre le catalogue
  - `/admin/prompts/catalog` ouvre aussi le catalogue
  - `/admin/personas` redirige vers `/admin/prompts/personas`
- Ne pas reduire ou remodeler le payload backend `resolved`; cette story est purement structure/navigation cote frontend. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Requirements-Inventory]

### Architecture Compliance

- Respecter la structure frontend existante sous `frontend/src/app`, `frontend/src/pages`, `frontend/src/layouts`, `frontend/src/state`, `frontend/src/tests`. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Project-Structure--Boundaries]
- Le frontend doit rester en React + TypeScript avec routage centralise dans `frontend/src/app/routes.tsx`. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- Reutiliser les composants existants avant d en creer de nouveaux. `PersonasAdmin` et `AdminSamplePayloadsAdmin` existent deja et doivent etre reintegres plutot que reecrits.
- Respecter les conventions de nommage et de tests frontend du projet. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Implementation-Patterns--Consistency-Rules]

### Library / Framework Requirements

- `react-router-dom`: routes imbriquees, `Navigate`, `Outlet`, `NavLink`, `useLocation` deja utilises dans le projet. [Source: C:/dev/horoscope_front/frontend/src/app/routes.tsx, C:/dev/horoscope_front/frontend/src/layouts/AdminLayout.tsx]
- `@tanstack/react-query`: deja utilise dans `AdminPromptsPage`; ne pas dupliquer la logique de fetch en dehors des hooks existants.
- Aucun ajout de bibliotheque n est necessaire pour cette story.

### File Structure Requirements

- Fichiers tres probablement touches:
  - `C:/dev/horoscope_front/frontend/src/app/routes.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/AdminPage.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/index.ts`
  - `C:/dev/horoscope_front/frontend/src/i18n/admin.ts`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPage.test.tsx`
- Si une navigation secondaire specifique prompts est extraite, la placer dans `frontend/src/pages/admin/` ou `frontend/src/components/` selon son niveau de reutilisation, sans casser la structure existante.

### Testing Requirements

- Mettre a jour ou etendre les tests Vitest/Testing Library pour couvrir:
  - le maintien de l entree sidebar `Prompts`
  - la navigation vers les sous-routes prompts
  - la redirection `/admin/personas -> /admin/prompts/personas`
  - la resolution correcte de `/admin/prompts` vers la vue catalogue
- Attention au test existant `AdminPage.test.tsx` qui verrouille aujourd hui la redirection legacy vers le heading `Catalogue prompts LLM`; il devra etre ajuste a la nouvelle cible tout en preservant l intention de regression. [Source: C:/dev/horoscope_front/frontend/src/tests/AdminPage.test.tsx]

### Implementation Guardrails

- `AdminLayout` filtre les sections de la sidebar via `section.path.split(\"/\").pop()`. Ajouter des sous-routes prompts directement dans la sidebar globale casserait la logique de permissions, car `legacy`, `release` ou `consumption` ne font pas partie de `ALL_ADMIN_SECTIONS`. Garder donc un seul item global `prompts` et une sous-nav locale. [Source: C:/dev/horoscope_front/frontend/src/layouts/AdminLayout.tsx, C:/dev/horoscope_front/frontend/src/state/AdminPermissionsContext.tsx]
- `AdminPage` expose actuellement exactement 10 sections en sidebar et `AdminPage.test.tsx` l affirme explicitement. Toute modification du nombre de sections globales serait une regression de la story 65.4.
- `AdminPromptsPage` repose encore sur `activeTab` et sur le type `PromptPageTab = \"catalog\" | \"legacy\" | \"release\" | \"consumption\" | \"personas\" | \"samplePayloads\"`. La story doit faire converger cette mecanique vers les routes dediees sans perdre les composants internes existants. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- La specification UX generale impose une navigation tres lisible, une charge cognitive reduite et une priorite mobile-first. La sous-navigation prompts doit donc etre explicite, simple et accessible. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

### Project Structure Notes

- Aucun `project-context.md` n a ete detecte dans le workspace.
- Le projet a deja un layout admin dedie et une page hub admin. La nouvelle navigation prompts doit s inserer dans ce cadre, pas le contourner.

### References

- Epic 70 et story 70.1: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]
- Architecture frontend et structure projet: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- Patterns responsive et accessibilite: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]
- Non-regression 67-69: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]
- Routeur admin actuel: [Source: C:/dev/horoscope_front/frontend/src/app/routes.tsx]
- Sidebar admin actuelle: [Source: C:/dev/horoscope_front/frontend/src/pages/AdminPage.tsx]
- Filtrage permissions sidebar: [Source: C:/dev/horoscope_front/frontend/src/layouts/AdminLayout.tsx]
- Permissions admin: [Source: C:/dev/horoscope_front/frontend/src/state/AdminPermissionsContext.tsx]
- Traductions admin: [Source: C:/dev/horoscope_front/frontend/src/i18n/admin.ts]
- Regression tests admin: [Source: C:/dev/horoscope_front/frontend/src/tests/AdminPage.test.tsx]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Recent git context:
  - `43c18fec docs(67-69): artefact non-régression + epics; tests intégration et Vitest alignés`
  - `79ee3af3 feat(admin-llm): clôturer 67-69 deferred work, facettes samples et placeholders`
  - `5bab55a1 fix(admin): share execute-sample route template for manual header`
  - `e9bd389e feat(admin): story 69.3 — exécution manuelle LLM sécurisée et QA`
  - `f02023bd fix(admin): aligner failure_kind audit et API (69.2)`

### Completion Notes List

- Story creee a partir de l epic 70 avec garde-fous explicites sur le routage, la sidebar admin, les permissions et les regressions 67-69.
- Story optimisee pour une implementation frontend incrementalement sure avant les refontes UX plus profondes des stories 70.2 a 70.7.
- Implementation 2026-04-18 : routes imbriquees sous `/admin/prompts` avec index -> `catalog`, alias `/admin/personas` -> `/admin/prompts/personas`, sous-navigation `NavLink` + `resolvePromptsTabFromPath`, i18n `promptsSubNav`, tests Vitest (`createTestMemoryRouter`, `AdminPromptsRoutesFixture`).
- Correctifs revue 2026-04-18 (alignement AC / isolation data-flow) :
  - `useAdminLlmUseCases` ne s’execute que sur l’onglet `legacy` (`enabled` dans `useAdminLlmUseCases`), evite les appels `/v1/admin/llm/use-cases` sur personas, release, consumption, sample-payloads, etc.
  - Suppression de l’entree navigation applicative globale `Persona` -> `/admin/personas` dans `ui/nav.ts` (sidebar grand public `getAllNavItems`) : le domaine prompts reste accessible via l’entree admin `Prompts` et la sous-nav locale ; l’alias URL `/admin/personas` est conserve.
  - Titres et intros de page par univers : i18n `promptsPageHeader` (fr/en/es) dans `admin.ts`, branche sur `activeTab` dans `AdminPromptsPage` (titres distincts, ex. « Personas LLM » en en-tete de page vs titre detail `PersonasAdmin`).
  - Tests : `ui-nav` / `ui-barrel` (13 entrees nav), `AdminPromptsRouting` (mock use-cases + historique legacy, titre legacy, titre page personas apres redirect).

### File List

- `frontend/src/app/routes.tsx`
- `frontend/src/app/router.tsx`
- `frontend/src/api/adminPrompts.ts` (`useAdminLlmUseCases` + option `enabled`)
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/i18n/admin.ts` (`promptsPageHeader`)
- `frontend/src/i18n/navigation.ts` (retrait cle `persona` nav grand public)
- `frontend/src/ui/nav.ts` (retrait entree top-level Persona)
- `frontend/src/tests/AdminPage.test.tsx`
- `frontend/src/tests/AdminPromptsRouting.test.tsx`
- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `frontend/src/tests/ui-nav.test.ts`
- `frontend/src/tests/ui-barrel.test.ts`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-04-18 — Navigation prompts basee sur le routeur ; redirection personas ; i18n sous-nav ; tests alignes (router memory).
- 2026-04-18 — Revue P2/P3 : requete legacy use-cases conditionnelle ; point d’entree Persona retire du nav global ; en-tetes `promptsPageHeader` par sous-route ; tests nav et routage mis a jour.

# Story 60.18: Alignement visuel du dashboard et préchargement de l'horoscope détaillé

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur authentifié,
I want retrouver sur `/dashboard` le même langage visuel premium que sur `/dashboard/horoscope` et voir le même résumé éditorial dès la landing,
so that le parcours dashboard → horoscope détaillé paraisse cohérent et que l'ouverture du détail soit instantanée car la donnée du jour est déjà calculée et mise en cache.

## Acceptance Criteria

1. La section horoscope de `/dashboard` adopte le même système visuel que `/dashboard/horoscope` pour les surfaces premium principales:
   - même palette dominante violet/lilas
   - mêmes logiques de glass surfaces, bordures, ombres, rayons et typographie
   - même niveau de contraste et de profondeur
   - sans recréer un deuxième design system parallèle dans `App.css`
2. `dashboard-summary-card__content` affiche la même narration que `day-climate-hero__summary`:
   - source primaire: `prediction.daily_synthesis`
   - fallback: le résumé issu du climat du jour déjà affiché dans `DayClimateHero`
   - le dashboard ne doit plus afficher un texte divergent basé uniquement sur `summary.overall_summary`
3. La logique de sélection de ce résumé est centralisée dans un helper, mapper ou hook partagé entre `/dashboard` et `/dashboard/horoscope`, afin d'empêcher toute divergence future de wording.
4. Le clic sur l'entrée de navigation menant à `/dashboard/horoscope` depuis la sidebar déclenche immédiatement le calcul/chargement de l'horoscope du jour et de son interprétation via l'endpoint daily existant, avant l'affichage de la page détail.
5. Le préchargement réutilise React Query et le cache frontend existant:
   - aucune duplication d'appel réseau direct dans les composants de présentation
   - aucun nouvel endpoint backend
   - si la donnée est déjà fraîche en cache, aucun recalcul/chargement supplémentaire n'est forcé
6. Après un clic sidebar vers `/dashboard/horoscope`, la page détail consomme en priorité la donnée préféetchée et n'affiche pas de chargement bloquant complet si le préchargement a abouti.
7. Le préchargement couvre au minimum les données nécessaires pour que la hero détaillée soit immédiatement cohérente:
   - `daily prediction`
   - `birth-data` utilisé pour `AstroMoodBackground`
   - avec fallback gracieux si `birth-data` est encore absent ou neutre
8. Les interactions existantes restent accessibles et cohérentes:
   - la carte résumé dashboard reste cliquable/activable au clavier
   - la sidebar conserve son comportement de navigation et de collapse
   - les états `loading`, `error` et `empty` restent gérés sur `/dashboard` et `/dashboard/horoscope`
9. Les tests frontend couvrent:
   - l'unification de la source du résumé entre dashboard et détail
   - le préchargement au clic de navigation sidebar
   - la réutilisation du cache sur `/dashboard/horoscope`
   - l'absence de régression sur les états dashboard/détail

## Tasks / Subtasks

- [x] Task 1: Unifier la source éditoriale du résumé dashboard et hero détail (AC: 2, 3)
  - [x] Identifier la source canonique du texte `day-climate-hero__summary`
  - [x] Extraire un helper ou mapper partagé pour produire ce résumé à partir de `DailyPredictionResponse`
  - [x] Brancher `DashboardHoroscopeSummaryCard` sur cette source canonique
  - [x] Brancher `/dashboard/horoscope` sur la même source partagée si nécessaire pour supprimer toute divergence implicite

- [x] Task 2: Aligner visuellement `/dashboard` sur `/dashboard/horoscope` (AC: 1, 8)
  - [x] Réutiliser les tokens, classes glass et choix typographiques déjà établis par 60-17
  - [x] Mettre à niveau la carte résumé dashboard et sa zone conteneur sans recréer un style concurrent
  - [x] Vérifier que la landing dashboard garde sa hiérarchie fonctionnelle (`résumé` puis `activités`) tout en reprenant la direction artistique premium
  - [x] Garder une cohérence de rayons, ombres, bordures, spacing et pills avec `DayClimateHero`

- [x] Task 3: Introduire un préchargement daily côté navigation horoscope (AC: 4, 5, 7)
  - [x] Centraliser un helper de préfetch React Query pour `daily-prediction` et `birth-data`
  - [x] Déclencher ce préfetch depuis l'entrée sidebar qui navigue vers `/dashboard/horoscope`
  - [x] Conserver le comportement existant de navigation/collapse de la sidebar
  - [x] Éviter tout couplage de composants UI à des appels `fetch` directs

- [x] Task 4: Faire consommer à la page détail la donnée préféetchée sans flicker inutile (AC: 5, 6, 8)
  - [x] Vérifier que `useDailyPrediction` et `useBirthData` réutilisent immédiatement le cache React Query après navigation
  - [x] Ajuster si nécessaire le bootstrap/refetch de `DailyHoroscopePage` pour ne pas casser le bénéfice du préchargement
  - [x] Préserver les fallbacks `loading/error/empty` quand le préchargement échoue ou n'a pas encore abouti

- [x] Task 5: Couvrir la navigation et les états par des tests ciblés (AC: 6, 8, 9)
  - [x] Mettre à jour les tests dashboard pour vérifier la nouvelle source de résumé
  - [x] Ajouter un test sidebar/navigation qui vérifie le préchargement de la query horoscope
  - [x] Ajouter ou adapter un test de la page détail pour confirmer la réutilisation du cache
  - [x] Vérifier qu'aucune régression n'affecte les états `loading/error/empty`

## Dev Notes

### Intent produit

- Cette story prolonge directement 45.2, 48.2, 60.16 et 60.17:
  - `/dashboard` doit devenir le teaser premium cohérent de `/dashboard/horoscope`
  - le résumé affiché sur la landing doit être éditorialement identique à celui porté par la hero détaillée
  - la navigation vers le détail doit paraître instantanée, le calcul étant déclenché au clic de navigation et non après arrivée sur la page

### Contexte existant à réutiliser

- `DashboardHoroscopeSummaryCard` consomme aujourd'hui `prediction.summary.overall_summary`; c'est précisément la divergence à supprimer.
- `DayClimateHero` affiche déjà `dailySynthesis || climate.summary`; cette règle doit devenir la source canonique du résumé éditorial court/long partagé.
- `useDashboardAstroSummary(token)` regroupe déjà:
  - `useDailyPrediction(token)`
  - `useBirthData(token)`
  - le calcul de `sign`, `dateKey` et `dayScore`
- `AppProviders` installe déjà `QueryClientProvider`; le préchargement doit donc passer par React Query (`queryClient.prefetchQuery` / `ensureQueryData` ou équivalent), pas par une deuxième couche réseau.
- `Sidebar.tsx` est actuellement le point de clic à instrumenter pour la navigation latérale vers `/dashboard/horoscope`.

### Architecture attendue

- Garder la séparation actuelle:
  - réseau et clés de query dans `frontend/src/api`
  - helper de préchargement ou orchestration dans un module dédié frontend
  - rendu dashboard dans les composants dashboard
  - rendu détail dans `DailyHoroscopePage`
- Ne pas introduire de nouveau contrat backend ni de variante `/prefetch`.
- Ne pas dupliquer la logique résumé dans deux composants différents.
- Ne pas déplacer de logique métier importante dans `Sidebar.tsx`; la sidebar doit appeler un helper dédié.

### File candidates

- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx`
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCardContainer.tsx`
- `frontend/src/components/dashboard/useDashboardAstroSummary.ts`
- `frontend/src/components/DayClimateHero.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/api/useDailyPrediction.ts`
- `frontend/src/api/useBirthData.ts`
- `frontend/src/api/dailyPrediction.ts`
- `frontend/src/App.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`
- tests navigation/layout liés à la sidebar si présents

### Implementation guidance

- Préférer un helper partagé du type:
  - sélecteur de résumé éditorial daily
  - helper `prefetchDailyHoroscope(...)`
- Le helper de résumé doit retourner une chaîne stable à partir du contrat `DailyPredictionResponse`:
  - primaire `daily_synthesis`
  - fallback `day_climate.summary` ou résultat équivalent du mapper climat
  - dernier fallback seulement si nécessaire vers `summary.overall_summary`
- Le préchargement ne doit pas dégrader la navigation:
  - navigation immédiate autorisée
  - préfetch lancé au clic
  - la page détail doit simplement profiter du cache si la réponse arrive avant ou pendant le changement de route
- Si plusieurs points d'entrée naviguent vers `/dashboard/horoscope`, l'implémentation doit favoriser un helper réutilisable plutôt qu'une logique réservée à un seul composant.

### Testing expectations

- Vérifier la cohérence visuelle et structurelle au niveau CSS/classes, sans snapshot fragile inutile.
- Vérifier que le résumé dashboard correspond bien à la même chaîne que celle injectée dans `DayClimateHero`.
- Vérifier le préchargement via la query key `daily-prediction` et, si applicable, `birth-data`.
- Vérifier qu'une donnée déjà en cache n'entraîne pas de double chargement bloquant sur `/dashboard/horoscope`.

### Project Structure Notes

- La story reste dans le périmètre frontend/orchestration.
- Le backend daily existe déjà et ne doit pas être modifié pour cette évolution, sauf découverte d'un bug bloquant pendant l'implémentation.
- Le style dashboard doit se réaligner sur la direction 60-17, pas lancer un nouveau chantier visuel indépendant.

### References

- [Source: _bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md]
- [Source: _bmad-output/implementation-artifacts/45-2-creer-la-landing-dashboard-avec-resume-et-hub-d-activites.md]
- [Source: _bmad-output/implementation-artifacts/45-3-restaurer-une-page-horoscope-detaillee-avec-retour-dashboard.md]
- [Source: _bmad-output/implementation-artifacts/48-2-integrer-le-fond-astrologique-anime-au-resume-dashboard.md]
- [Source: _bmad-output/implementation-artifacts/59-4-precalcul-astral.md]
- [Source: _bmad-output/implementation-artifacts/60-16-interpretation-llm.md]
- [Source: _bmad-output/implementation-artifacts/60-17-refonte-visuelle-premium-page-horoscope.md]
- [Source: frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx]
- [Source: frontend/src/components/dashboard/useDashboardAstroSummary.ts]
- [Source: frontend/src/components/DayClimateHero.tsx]
- [Source: frontend/src/components/layout/Sidebar.tsx]
- [Source: frontend/src/pages/DashboardPage.tsx]
- [Source: frontend/src/pages/DailyHoroscopePage.tsx]
- [Source: frontend/src/api/useDailyPrediction.ts]
- [Source: frontend/src/api/useBirthData.ts]
- [Source: frontend/src/state/providers.tsx]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée via le workflow BMAD `create-story`.
- Contexte consolidé depuis les stories 45.2, 45.3, 48.2, 59.4, 60.16 et 60.17 ainsi que depuis l'implémentation frontend courante.
- Post-review 2026-03-22: correction des régressions sur le préfetch daily, le halo dashboard et le contrat visuel `ShortcutCard`.

### Completion Notes List

- Le dashboard réutilise la même source éditoriale que la hero détaillée via `getDailyEditorialSummary`.
- Le style `/dashboard` est réaligné sur la direction premium/glass de `/dashboard/horoscope` avec tokens mutualisés.
- La landing dashboard a reçu plusieurs passes de finition premium:
  - hero horoscope plus dense et plus éditoriale
  - CTA principal plus intégré et plus contrasté
  - fond global enrichi de halos plus orchestrés
  - cartes Activités densifiées avec micro-pills harmonisées
- Les sections `Horoscope` et `Activités` reposent maintenant sur le même pattern de header de section, avec une hiérarchie typographique et un layout homogènes.
- Le préchargement au clic sidebar vers `/dashboard/horoscope` est branché via React Query sans nouvel endpoint backend.
- Les query options `daily-prediction` et `birth-data` sont désormais partagées entre hooks et préfetch pour garantir un comportement de cache cohérent.
- Les régressions post-review ont été corrigées:
  - le préfetch ne convertit plus une erreur backend en faux état vide mis en cache
  - le halo dashboard utilise la bonne classe CSS
  - `ShortcutCard` respecte à nouveau son contrat visuel couvert par les tests
- La page détail réutilise bien la donnée préféetchée sans chargement bloquant du daily quand le cache est déjà hydraté.
- Pendant le chargement initial sur `/dashboard`, la carte `dashboard-summary-card-wrapper` affiche désormais un spinner éditorial avec le message `Horoscope du jour en cours de rédaction`.
- Durant cet état de rédaction, la navigation vers `/dashboard/horoscope` est gelée côté UI et couverte par test.
- La carte loading conserve la même enveloppe premium que la carte finale, avec une largeur de lecture du résumé ensuite limitée par une contrainte de style sur `dashboard-summary-card__text`.

### Change Log

- 2026-03-21: Implémentation initiale de l’alignement visuel dashboard + préchargement horoscope.
- 2026-03-22: Corrections post-code-review sur le data-flow React Query, le halo dashboard et les non-régressions visuelles `ShortcutCard`.
- 2026-03-22: Ajout d’un état de rédaction bloquant dans la carte résumé dashboard avec spinner, message dédié et blocage de la navigation pendant la génération.
- 2026-03-22: Passes finales de finition premium sur `/dashboard` avec hero plus luxueuse, grille Activités plus matérielle, fond plus atmosphérique et headers de sections homogénéisés.

### File List

- `frontend/src/utils/dailySummaryHelper.ts`
- `frontend/src/utils/prefetchHelpers.ts`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/pages/DashboardPage.css`
- `frontend/src/main.tsx`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/App.css`
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx`
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCardContainer.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/ShortcutCard.tsx`
- `frontend/src/components/ShortcutCard.css`
- `frontend/src/components/ShortcutsSection.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/utils/dayClimateHeroMapper.ts`
- `frontend/src/api/useDailyPrediction.ts`
- `frontend/src/api/useBirthData.ts`
- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`
- `frontend/src/tests/layout/Sidebar.test.tsx`

- `_bmad-output/implementation-artifacts/60-18-alignement-dashboard-et-prechargement-horoscope.md`

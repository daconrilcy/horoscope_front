# CS-202 Frontend Expert Panel Before

## Flux actuel

- Route `/natal`: `frontend/src/app/routes.tsx` charge
  `frontend/src/pages/NatalChartPage.tsx`.
- Recuperation du dernier theme: `useLatestNatalChart()` dans
  `frontend/src/api/natal-chart/index.ts`.
- Endpoint consomme: `GET /v1/users/me/natal-chart/latest` via `apiFetch`.
- Type frontend actuel: `LatestNatalChart.result` contient les blocs natals de
  base `prepared_input`, `planet_positions`, `houses` et `aspects`.

## Rendu actuel

- `NatalChartPage.tsx` affiche les positions planetaires, maisons, aspects,
  profil astro simple, guide natal et interpretation.
- Les etats loading, erreur API, chart absent, donnees de naissance incompletes
  et mode degrade sont deja traites au niveau page.
- Aucun composant `NatalExpertPanel` ou panneau technique natal equivalent n'a
  ete trouve par recherche ciblee.

## Blocs CS-201 ignores avant implementation

- `dignities`
- `dignities.sect`
- `dignities.planets[*].sect_condition`
- `planet_condition_profiles`
- `planet_condition_signals`
- `advanced_conditions`
- `dominant_planets`
- `interpretation_adapter`

## Generated contract check

Aucun type OpenAPI genere dedie au chart natal n'a ete identifie pendant
l'inspection initiale. Le proprietaire du contrat frontend reste donc le module
manuel `frontend/src/api/natal-chart/index.ts`.

## Baseline no-calculation stance

Avant CS-202, le frontend affiche des faits basiques du payload public et
contient deja quelques transformations d'affichage pour les degres, maisons et
libelles. La story ne doit pas ajouter de calcul astrologique avance: le futur
panneau expert doit consommer uniquement les champs publics deja calcules par
le backend.

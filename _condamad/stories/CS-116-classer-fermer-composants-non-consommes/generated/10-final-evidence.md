<!-- Preuves finales CS-116. -->

# CS-116 Final Evidence

Status: done

Implementation:
- Ajout de `component-usage-allowlist.ts` et `component-usage-guards.test.ts`.
- Classification exacte de tous les candidats F-005 et des no-runtime candidates detectes par le guard global.
- Le guard scanne maintenant tout `frontend/src/components/**`, detecte les exports aliases et utilise un graphe d'import/export runtime atteignable depuis `main.tsx` plutot que des occurrences textuelles.
- Les imports `type` et les imports provenant de composants eux-memes non atteignables ne prouvent plus un usage runtime.
- Suppression de `frontend/src/components/AppShell.tsx`, prouve `remove` apres absence de consommateur runtime.
- Suppression des composants prediction non atteignables sans test direct ni barrel public, avec CSS associes.
- Classification exacte de `DashboardCard`, `Card`, `MiniInsightCard`, `ConstellationSVG`, `DayPredictionCard` et `TurningPointsList`.

Validation:
- `npm run test -- component-usage` - PASS.
- `npm run test -- component-usage component-architecture` - PASS.
- `npm run test -- components component-usage design-system` - PASS.
- `npm run test -- AppShell App` - PASS.
- `npm run lint` - PASS.
- `npm run build` - PASS.
- `rg --files src/components -g '*.tsx'` - executed for inventory.

Remaining risks: none identified in story scope.

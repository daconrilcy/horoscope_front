# CS-323 — Retirer Le Provider Matomo Dormant De L'Analytics Frontend

## Résumé

Retirer Matomo du chemin actif analytics frontend afin d'aligner le code sur la décision actuelle : préparer Plausible, conserver `noop` en local, ne pas maintenir un provider dormant non utilisé.

## Contexte

CS-321 prépare Plausible comme cible analytics.
Le code contient encore un support dormant Matomo :

- `frontend/src/config/analytics.ts` : `AnalyticsProvider = 'plausible' | 'matomo' | 'noop'`
- `frontend/src/hooks/useAnalytics.ts` : branche `_paq` Matomo

Matomo n'est pas utilisé pour l'instant. Garder ce chemin actif augmente la surface de maintenance, de tests et de consentement sans besoin produit immédiat.

## Objectif

Converger l'analytics frontend vers deux providers actifs seulement :

- `noop` par défaut local ;
- `plausible` comme provider préparé.

## Préalable obligatoire

Relire :

- `_story_briefs/cs-321-preparer-integration-plausible-analytics.md`
- `frontend/src/config/analytics.ts`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/tests/useAnalytics.test.tsx`
- `.env.example`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md`
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md`

## Périmètre inclus

1. Retirer `matomo` du type `AnalyticsProvider`.
2. Supprimer la branche `_paq` dans `useAnalytics.ts`.
3. Vérifier que Plausible et `noop` restent testés.
4. Mettre à jour les tests si nécessaire.
5. Mettre à jour les docs/env examples qui mentionnent Matomo comme option active.
6. Ajouter une preuve de scan montrant qu'aucun `_paq` ou `matomo` actif ne reste dans `frontend/src`.

## Hors périmètre

- Activer Plausible en production.
- Ajouter un autre provider analytics.
- Modifier la taxonomie des événements.
- Modifier l'instrumentation métier CS-311.
- Ajouter un dashboard ou de l'alerting.

## Critères d'acceptation

1. `AnalyticsProvider` ne contient plus `matomo`.
2. `useAnalytics.ts` ne contient plus de branche `_paq`.
3. Les tests analytics Plausible/noop passent.
4. Aucun appel provider direct n'apparaît hors `useAnalytics.ts`.
5. `.env.example` et les docs ne présentent plus Matomo comme option configurée.
6. Les événements CS-311/CS-316 continuent d'être redacted avant envoi.
7. Aucun backend, DB, migration, prompt ou provider LLM n'est modifié.

## Validation attendue

Frontend :

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run
```

Scans :

```powershell
rg -n "matomo|_paq" frontend/src .env.example docs _story_briefs
rg -n "plausible\(" frontend/src/features frontend/src/components frontend/src/pages frontend/src/api
rg -n "birth_date|birth_time|birth_place|latitude|longitude|provider_response|raw_runtime|replay_snapshot|prompt|api_key|password" frontend/src/hooks frontend/src/tests
```

## Risques

Le risque principal est de retirer un chemin qui était implicitement prévu mais non décidé. La story doit conserver l'historique dans les artefacts CONDAMAD si besoin, mais retirer Matomo du code actif tant que Plausible est la seule cible.

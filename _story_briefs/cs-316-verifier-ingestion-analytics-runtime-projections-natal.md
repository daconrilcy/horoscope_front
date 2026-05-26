# CS-316 — Vérifier L'Ingestion Runtime Des Analytics Projections /natal

## Résumé

CS-311 prouve l'émission frontend et la redaction des événements analytics, mais pas leur ingestion par un provider réel. Cette story ajoute un smoke runtime optionnel et borné lorsque l'environnement analytics est disponible.

## Contexte

`_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/observability-limits.md` exclut dashboard, alerting et nouveau provider. Le rapport consolidé classe l'ingestion provider comme preuve externe absente, pas comme bug CS-311.

## Objectif

Vérifier que les événements CS-311 réellement émis par `/natal` arrivent dans le sink analytics configuré, avec payload redacted, sans ajouter de provider ni exposer de données sensibles.

## Préalable obligatoire

Relire :

- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/redaction-proof.md`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/observability-limits.md`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`

## Périmètre inclus

1. Identifier le sink analytics réellement configuré en local/staging, sans créer de nouveau provider.
2. Déclencher les états started, success, api_error, entitlement_denied, empty, degraded et retry si l'environnement le permet.
3. Capturer une preuve que les noms d'événements et les champs publics correspondent à `event-catalog.json`.
4. Vérifier qu'aucun champ sensible n'est ingéré.
5. Documenter les limites si aucun provider ou environnement d'ingestion n'est disponible.

## Hors périmètre

- Ajouter un provider analytics.
- Créer un dashboard ou une alerte.
- Modifier backend, persistence, prompts, providers ou replay.
- Capturer des données de naissance réelles, coordonnées exactes, secrets ou payloads bruts.

## Critères d'acceptation

1. Une preuve d'ingestion existe, ou l'absence d'environnement provider est documentée comme validation externe requise.
2. Les événements observés correspondent aux sept événements CS-311.
3. Les payloads observés ne contiennent que des champs publics autorisés.
4. Les tests CS-311 existants restent passants.

## Validation attendue

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run
```

## Risques

Le risque principal est de confondre smoke d'ingestion et extension d'observabilité. Cette story doit rester une vérification, pas une refonte analytics.

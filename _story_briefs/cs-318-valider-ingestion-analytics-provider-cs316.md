# CS-318 — Valider L'Ingestion Provider Des Analytics CS-316

## Résumé

CS-316 est complet côté dépôt, mais l'ingestion réelle reste externe car le provider local est `noop`. Cette story exécute la validation dans un environnement où Plausible ou Matomo est configuré et observable.

## Contexte

Le rapport `_condamad/reports/CS-312-CS-316-delivery-report.md` classe CS-316 en `Requires business/QA validation`.
CS-316 prouve déjà :

- les sept événements attendus ;
- la comparaison ledger/catalog ;
- la redaction des champs sensibles ;
- les tests frontend et scans ;
- l'absence de provider observable en local.

Il manque une preuve d'ingestion par un vrai sink analytics.

## Objectif

Vérifier que les événements `/natal` CS-311/CS-316 arrivent réellement dans le provider analytics configuré, avec payload redacted.

## Préalable obligatoire

Relire :

- `_condamad/reports/CS-312-CS-316-delivery-report.md`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-runtime-config.json`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-ingestion-ledger.json`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/external-validation-required.md`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`

## Périmètre inclus

1. Identifier l'environnement staging ou production où le provider analytics est actif.
2. Déclencher les sept événements attendus : started, success, api_error, entitlement_denied, empty, degraded, retry.
3. Capturer une preuve d'ingestion côté provider, ou une preuve d'indisponibilité externe.
4. Vérifier que les champs ingérés restent limités aux champs publics du catalogue.
5. Mettre à jour l'évidence CS-316 ou créer un rapport d'acceptation externe dédié.
6. Ne modifier le code que si un bug d'émission/redaction est prouvé.

## Hors périmètre

- Ajouter un nouveau provider analytics.
- Créer un dashboard ou un système d'alerting.
- Modifier backend, replay, prompts, persistence ou providers LLM.
- Capturer des données de naissance, coordonnées, prompts, raw AI output, secrets ou payloads provider.

## Critères d'acceptation

1. Un environnement provider observable est identifié, ou son absence est documentée comme blocage externe.
2. Les sept événements CS-316 sont observés ou explicitement classés non déclenchables avec justification.
3. Les payloads observés ne contiennent aucun champ sensible.
4. La preuve d'ingestion cite le provider, l'environnement, la date, les événements et les champs publics.
5. Les tests frontend CS-316 restent passants après la validation.
6. Si une anomalie est détectée, elle est corrigée ou transformée en brief séparé.

## Validation attendue

Frontend local avant/après vérification :

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run
```

Scan sensible :

```powershell
rg -n "birth_date|birth_time|birth_place|latitude|longitude|provider_response|raw_runtime|replay_snapshot|prompt|api_key|password" _condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence
```

## Risques

Le risque principal est organisationnel : l'environnement provider peut ne pas être accessible depuis le poste de dev. Dans ce cas, la story doit produire un blocage externe précis au lieu de simuler une validation.

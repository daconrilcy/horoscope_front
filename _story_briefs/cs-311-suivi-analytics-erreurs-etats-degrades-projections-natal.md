# CS-311 — Suivi Analytics Erreurs Et États Dégradés Des Projections /natal

## Résumé

Mettre en place ou vérifier le suivi analytics et erreurs des projections `/natal`, avec attention particulière aux refus d'accès, erreurs API, états vides et modes dégradés.

## Contexte

Après le branchement B2C des projections, l'équipe doit pouvoir observer les problèmes réels : erreurs API, 403 entitlement, absence de données de naissance, mode dégradé sans heure, retry utilisateur et affichage vide. Sans instrumentation minimale, la qualité produit restera difficile à suivre après mise en production.

## Objectif

Définir et implémenter un suivi applicatif minimal pour les événements critiques des projections `/natal`, sans exposer de données sensibles ni payloads internes.

## Préalable obligatoire

Relire :

- `frontend/src/hooks/useAnalytics.ts` ou l'owner analytics existant.
- `frontend/src/api/astrologyProjections.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `docs/architecture/astrology-disclaimer-projection-policy.md`

## Périmètre inclus

1. Inventorier les hooks/services analytics existants avant d'ajouter quoi que ce soit.
2. Définir les événements minimaux : projection request started, success, API error, entitlement denied, empty state, degraded state, retry.
3. Vérifier que les événements ne contiennent aucun prompt, payload provider, replay snapshot, donnée de naissance brute, coordonnée exacte, secret ou réponse IA brute.
4. Ajouter l'instrumentation dans l'owner frontend approprié si elle n'existe pas déjà.
5. Ajouter des tests frontend qui prouvent les événements et leur redaction.
6. Documenter les erreurs suivies et les limites d'observabilité.
7. Conserver la décision d'accès au backend et ne pas introduire de fallback silencieux.

## Hors périmètre

- Ajouter un nouveau fournisseur analytics externe.
- Envoyer des données personnelles ou payloads de projection complets.
- Modifier les routes backend.
- Ajouter un dashboard analytics admin.
- Créer un système d'alerting complet.
- Instrumenter toute l'application hors `/natal` projections.

## Critères d'acceptation

1. Les événements analytics/erreurs pertinents sont listés et justifiés.
2. L'instrumentation réutilise l'owner analytics existant.
3. Les événements ne contiennent que des champs non sensibles : type de projection public, état, code d'erreur public, plan public si déjà exposé.
4. Les états success, API error, entitlement denied, empty, degraded et retry sont testés.
5. Les tests prouvent l'absence de données sensibles dans les payloads analytics.
6. Les validations frontend passent.
7. Toute limite d'observabilité restante est documentée.

## Validation attendue

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run
rg -n "birth_date|birth_time|birth_place|latitude|longitude|provider_response|raw_runtime|replay_snapshot|prompt|api_key|password" src
```

## Dépendances

- CS-303.
- CS-307.
- CS-309.
- CS-310.

## Risques

Le risque principal est d'améliorer l'observabilité en envoyant trop de contexte. Cette story doit privilégier des événements sobres, publics et non sensibles, avec tests de redaction.

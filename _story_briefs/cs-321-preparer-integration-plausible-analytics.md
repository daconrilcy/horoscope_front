# CS-321 — Préparer L'Intégration Plausible Analytics

## Résumé

Préparer l'application à utiliser Plausible comme provider analytics cible, sans activer encore une collecte production non validée. Matomo n'est pas utilisé pour l'instant et ne doit pas être configuré dans cette story.

## Contexte

Les stories CS-316 et CS-318 prouvent que l'émission analytics interne et la redaction sont prêtes côté dépôt, mais que le provider local reste `noop`.
La décision courante est de préparer Plausible.

État actuel observé :

- `frontend/src/config/analytics.ts` expose déjà `provider: 'plausible' | 'matomo' | 'noop'`.
- `frontend/src/hooks/useAnalytics.ts` sait appeler `window.plausible(...)` si Plausible est chargé.
- Aucun environnement Plausible observable n'est encore disponible.

## Objectif

Préparer une intégration Plausible propre, documentée et testable, en gardant `noop` comme défaut local tant que les variables d'environnement Plausible ne sont pas configurées.

## Préalable obligatoire

Relire :

- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md`
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md`
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/external-access-blocker.md`
- `frontend/src/config/analytics.ts`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/tests/useAnalytics.test.tsx`
- `.env.example`

## Périmètre inclus

1. Définir la configuration Plausible attendue côté frontend.
2. Documenter les variables d'environnement nécessaires dans `.env.example` ou un document d'exploitation approprié.
3. Vérifier que `noop` reste le défaut local quand Plausible n'est pas configuré.
4. Vérifier que l'appel provider reste centralisé dans `useAnalytics`.
5. Ajouter ou ajuster les tests qui prouvent le comportement Plausible configuré/non configuré.
6. Documenter la procédure de validation staging/production avant activation réelle.

## Hors périmètre

- Créer un compte Plausible ou configurer un domaine externe depuis le dépôt.
- Ajouter Matomo.
- Ajouter un dashboard ou de l'alerting.
- Modifier les événements métier CS-311.
- Capturer des données sensibles.
- Appeler Plausible directement depuis les composants, pages ou hooks métier.

## Critères d'acceptation

1. Le provider cible est explicitement Plausible.
2. Les variables Plausible attendues sont documentées.
3. Le défaut local reste `noop`.
4. Aucun appel provider direct n'est ajouté hors `frontend/src/hooks/useAnalytics.ts`.
5. Les tests prouvent que Plausible reçoit uniquement des props redacted.
6. La procédure d'activation et de validation externe est documentée.
7. CS-318 peut être repris plus tard avec un environnement Plausible observable.

## Validation attendue

Frontend :

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi
```

Scans :

```powershell
rg -n "plausible\(" frontend/src/features frontend/src/components frontend/src/pages frontend/src/api
rg -n "VITE_ANALYTICS_PROVIDER|VITE_ANALYTICS_DOMAIN|VITE_ANALYTICS_API_HOST|VITE_ANALYTICS_ENABLED" .env.example frontend docs
```

## Risques

Le risque principal est d'activer une collecte sans preuve de consentement, de domaine ou de redaction. Cette story prépare Plausible, mais l'activation observable reste une validation externe séparée.

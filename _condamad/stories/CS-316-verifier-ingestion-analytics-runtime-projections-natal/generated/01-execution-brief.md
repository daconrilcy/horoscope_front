# Execution Brief

Story: `CS-316-verifier-ingestion-analytics-runtime-projections-natal`

Objectif: verifier l'ingestion runtime des sept evenements analytics CS-311
pour `/natal`, ou documenter explicitement l'absence de sink provider
disponible.

Decision d'implementation:

- Le depot local ne configure pas `VITE_ANALYTICS_PROVIDER`; la configuration
  frontend charge donc `provider: "noop"`.
- Aucun provider, dashboard, backend, replay, persistance ou payload applicatif
  n'est ajoute.
- La fermeture est `external_validation_required`, avec ledger JSON couvrant
  les sept evenements et les champs publics du catalogue CS-311.

Surfaces inspectees:

- `_story_briefs/cs-316-verifier-ingestion-analytics-runtime-projections-natal.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/redaction-proof.md`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/observability-limits.md`
- `frontend/src/config/analytics.ts`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/tests/useAnalytics.test.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`

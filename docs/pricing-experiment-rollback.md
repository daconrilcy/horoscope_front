# Pricing Experiment Rollback

## Scope

This runbook covers rollback for pricing experiment instrumentation (`packaging_pricing_v1`).

## Kill Switch

- Environment variable: `PRICING_EXPERIMENT_ENABLED`
- Default: `true`
- Rollback value: `false`

When disabled, pricing experiment events are not emitted and a dropped-event counter is incremented:
- `pricing_experiment_events_dropped_total|reason=disabled`

## Rollback Procedure

1. Set `PRICING_EXPERIMENT_ENABLED=false` on the backend runtime.
2. Restart backend instances.
3. Verify startup log contains:
   - `pricing_experiment_state_changed enabled=False ...`
4. Verify no new pricing event counters are increasing:
   - `pricing_experiment_exposure_total|...`
   - `pricing_experiment_conversion_total|...`
   - `pricing_experiment_revenue_cents_total|...`
   - `pricing_experiment_retention_usage_total|...`
5. Verify dropped-event counter increases as expected:
   - `pricing_experiment_events_dropped_total|reason=disabled`

## Re-enable Procedure

1. Set `PRICING_EXPERIMENT_ENABLED=true`.
2. Restart backend instances.
3. Verify startup log contains:
   - `pricing_experiment_state_changed enabled=True ...`
4. Confirm KPI endpoint returns variant aggregates again:
   - `GET /v1/ops/monitoring/pricing-experiments-kpis?window=24h`

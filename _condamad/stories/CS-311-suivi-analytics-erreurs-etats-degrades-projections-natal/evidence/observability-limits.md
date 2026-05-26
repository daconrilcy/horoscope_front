<!-- Commentaire global: ce document explicite les limites volontaires de l'observabilite CS-311. -->

# Observability Limits

CS-311 intentionally adds minimal frontend analytics for `/natal` projections only.

Tracked states:

- request started;
- success;
- API error;
- entitlement denied;
- empty display or missing birth-data context;
- degraded without birth time;
- user retry.

Known limits:

- No analytics dashboard, alerting system, or new provider is added.
- No backend route, entitlement decision, persistence, prompt, provider payload, or projection builder is changed.
- No raw birth data, exact coordinates, provider response, replay snapshot, prompt, secret, or raw AI output is emitted.
- Retry analytics is emitted from the user retry button, not from React Query internal retry behavior.
- Public error tracking is limited to public error codes exposed through existing frontend error handling.

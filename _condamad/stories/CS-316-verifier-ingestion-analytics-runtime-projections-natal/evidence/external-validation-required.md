<!-- Commentaire global: cette preuve CS-316 documente l'absence de sink analytics externe disponible pour le smoke runtime. -->

# External Validation Required

Statut: `external_validation_required`

Le runtime frontend local charge `ANALYTICS_CONFIG` avec `provider: "noop"`.
Aucun environnement Plausible ou Matomo n'est configure dans le depot local,
donc l'ingestion par un service externe ne peut pas etre observee dans cette
execution sans acces environnemental supplementaire.

Preuves conservees:

- `analytics-runtime-config.json` consigne la configuration chargee.
- `analytics-ingestion-ledger.json` couvre les sept evenements CS-311 et les
  champs publics attendus.
- Les validations frontend CS-311 restent la preuve d'emission et de redaction
  locale; la verification provider reste un handoff externe explicite.

# Strategie de recalcul des agregats LLM canoniques

Ce document fixe la frontiere entre les journaux bruts LLM et le read model
`llm_canonical_consumption_aggregates`. Il sert de garde-fou pour les evolutions
de la story 70-18, notamment AC19.

## Source de verite

La source de verite reste `llm_call_logs`. Le read model
`llm_canonical_consumption_aggregates` est une projection recalculable, jamais une
source nominale pour reconstruire une periode.

Les dimensions canoniques d agregation sont :

- `period_start_utc`
- `granularity`
- `user_id`
- `subscription_plan`
- `feature`
- `subfeature`
- `locale`
- `executed_provider`
- `active_snapshot_version`
- `is_legacy_residual`

## Champs additifs

Ces champs peuvent etre sommes entre lignes deja agregees quand les dimensions
et la granularite cible restent coherentes :

- `tokens_in`
- `tokens_out`
- `total_tokens`
- `cost_usd_estimated_microusd`
- `call_count`

`error_rate_bps` ne doit pas etre moyenne directement. Si un regroupement de
plusieurs lignes agregees est necessaire, il doit etre pondere par `call_count`.

## Champs non additifs

Ces champs doivent etre recalcules depuis les `llm_call_logs` bruts pour la
periode et le filtre demandes :

- `latency_p50_ms`
- `latency_p95_ms`

Les percentiles ne sont pas composables a partir de percentiles deja agreges. Une
vue admin peut afficher un zero temporaire uniquement si elle remplace ensuite la
valeur par un calcul issu des logs bruts sur le meme perimetre.

## Frontiere canonique et legacy

Les nouvelles lectures nominales doivent filtrer `is_legacy_residual = false`.
Le scope `all` est reserve aux ecrans d audit, d export ou de migration qui
doivent rendre visibles les residus historiques.

La colonne historique `llm_call_logs.use_case` ne doit plus definir une nouvelle
dimension nominale. Elle peut seulement servir a reclasser d anciennes lignes
dont `feature` n etait pas encore renseigne, via la table de correspondance
legacy vers taxonomie canonique.

## Recalcul de periode

Un recalcul doit d abord supprimer les lignes du read model couvertes par la
fenetre demandee, puis relire les logs bruts sur une fenetre etendue aux bornes
de buckets. Cette regle evite les buckets journaliers ou mensuels partiellement
reconstruits.

Pour une regeneration complete, supprimer toutes les lignes du read model puis
rejouer `LlmCanonicalConsumptionService.refresh_read_model` sans borne.

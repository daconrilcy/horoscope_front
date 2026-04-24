# Structure des modeles LLM

Documentation generee depuis `app.infra.db.models.llm.llm_canonical_perimeter`.

## Perimetre canonique

- Tables autorisees : llm_active_releases, llm_assembly_configs, llm_call_log_operational_metadata, llm_call_logs, llm_canonical_consumption_aggregates, llm_execution_profiles, llm_output_schemas, llm_personas, llm_prompt_versions, llm_release_snapshots, llm_replay_snapshots, llm_sample_payloads, llm_use_case_configs
- Helpers autorises : llm_audit, llm_canonical_perimeter, llm_constraints, llm_field_lengths, llm_indexes, llm_json_validators
- Champs d execution autoritaires : execution_profile_ref, output_schema_id, requested_provider, resolved_provider, executed_provider

## Tables

### `llm_assembly_configs`

- Role : selection fonctionnelle d une cible runtime
- Source de verite : feature, subfeature, plan, locale, feature_template_ref, execution_profile_ref, output_schema_id
- Relations ORM : feature_template, subfeature_template, persona, execution_profile, output_schema
- Contraintes majeures : published_unique_index, component_state_checks, output_schema_fk
- Statut : canonical
- Compatibilite legacy toleree : aucune

### `llm_execution_profiles`

- Role : decisions d execution runtime
- Source de verite : provider, model, timeout_seconds, max_output_tokens, reasoning_profile, verbosity_profile
- Relations ORM : fallback_profile
- Contraintes majeures : published_unique_index, provider_check, profile_domain_checks
- Statut : canonical
- Compatibilite legacy toleree : aucune

### `llm_prompt_versions`

- Role : texte versionne des prompts
- Source de verite : developer_prompt
- Relations ORM : use_case
- Contraintes majeures : published_unique_index
- Statut : canonical
- Compatibilite legacy toleree : aucune

### `llm_output_schemas`

- Role : contrat JSON structure de sortie
- Source de verite : id, name, version, json_schema
- Relations ORM : assemblies
- Contraintes majeures : name_version_unique
- Statut : canonical
- Compatibilite legacy toleree : aucune

### `llm_call_logs`

- Role : journal coeur des appels LLM
- Source de verite : latency_ms, tokens_in, tokens_out, validation_status
- Relations ORM : operational_metadata, prompt_version, persona, replay_snapshot
- Contraintes majeures : environment_check, trace_indexes
- Statut : canonical
- Compatibilite legacy toleree : aucune

### `llm_call_log_operational_metadata`

- Role : metadonnees operationnelles et de release des appels
- Source de verite : requested_provider, resolved_provider, executed_provider, pipeline_kind, active_snapshot_version, manifest_entry_id
- Relations ORM : call_log
- Contraintes majeures : call_log_unique, pipeline_kind_check, breaker_state_check
- Statut : canonical
- Compatibilite legacy toleree : aucune

# Definition executable du perimetre canonique LLM.
"""Expose les conventions structurelles autorisees et le rendu documentaire associe."""

from __future__ import annotations

from dataclasses import dataclass

ALLOWED_MODEL_TABLES: tuple[str, ...] = (
    "llm_active_releases",
    "llm_assembly_configs",
    "llm_call_log_operational_metadata",
    "llm_call_logs",
    "llm_canonical_consumption_aggregates",
    "llm_execution_profiles",
    "llm_output_schemas",
    "llm_personas",
    "llm_prompt_versions",
    "llm_release_snapshots",
    "llm_replay_snapshots",
    "llm_sample_payloads",
    "llm_use_case_configs",
)
ALLOWED_HELPER_MODULES: tuple[str, ...] = (
    "llm_audit",
    "llm_canonical_perimeter",
    "llm_constraints",
    "llm_field_lengths",
    "llm_indexes",
    "llm_json_validators",
)
AUTHORITATIVE_EXECUTION_FIELDS: tuple[str, ...] = (
    "execution_profile_ref",
    "output_schema_id",
    "requested_provider",
    "resolved_provider",
    "executed_provider",
)


@dataclass(frozen=True, slots=True)
class ModelStructureEntry:
    """Resume le role et le statut canonique d un modele LLM."""

    table_name: str
    role: str
    source_of_truth: str
    canonical_relations: tuple[str, ...]
    major_constraints: tuple[str, ...]
    status: str = "canonical"


MODEL_STRUCTURE: tuple[ModelStructureEntry, ...] = (
    ModelStructureEntry(
        table_name="llm_assembly_configs",
        role="selection fonctionnelle d une cible runtime",
        source_of_truth=(
            "feature, subfeature, plan, locale, feature_template_ref, "
            "execution_profile_ref, output_schema_id"
        ),
        canonical_relations=(
            "feature_template",
            "subfeature_template",
            "persona",
            "execution_profile",
            "output_schema",
        ),
        major_constraints=("published_unique_index", "component_state_checks", "output_schema_fk"),
    ),
    ModelStructureEntry(
        table_name="llm_execution_profiles",
        role="decisions d execution runtime",
        source_of_truth=(
            "provider, model, timeout_seconds, max_output_tokens, "
            "reasoning_profile, verbosity_profile"
        ),
        canonical_relations=("fallback_profile",),
        major_constraints=("published_unique_index", "provider_check", "profile_domain_checks"),
    ),
    ModelStructureEntry(
        table_name="llm_prompt_versions",
        role="texte versionne des prompts",
        source_of_truth="developer_prompt",
        canonical_relations=("use_case",),
        major_constraints=("published_unique_index",),
    ),
    ModelStructureEntry(
        table_name="llm_output_schemas",
        role="contrat JSON structure de sortie",
        source_of_truth="id, name, version, json_schema",
        canonical_relations=("assemblies",),
        major_constraints=("name_version_unique",),
    ),
    ModelStructureEntry(
        table_name="llm_call_logs",
        role="journal coeur des appels LLM",
        source_of_truth="latency_ms, tokens_in, tokens_out, validation_status",
        canonical_relations=(
            "operational_metadata",
            "prompt_version",
            "persona",
            "replay_snapshot",
        ),
        major_constraints=("environment_check", "trace_indexes"),
    ),
    ModelStructureEntry(
        table_name="llm_call_log_operational_metadata",
        role="metadonnees operationnelles et de release des appels",
        source_of_truth=(
            "requested_provider, resolved_provider, executed_provider, "
            "pipeline_kind, active_snapshot_version, manifest_entry_id"
        ),
        canonical_relations=("call_log",),
        major_constraints=("call_log_unique", "pipeline_kind_check", "breaker_state_check"),
    ),
)


def render_structure_markdown() -> str:
    """Genere la documentation Markdown synchronisee avec le perimetre canonique."""
    lines: list[str] = [
        "# Structure des modeles LLM",
        "",
        "Documentation generee depuis `app.infra.db.models.llm.llm_canonical_perimeter`.",
        "",
        "## Perimetre canonique",
        "",
        f"- Tables autorisees : {', '.join(ALLOWED_MODEL_TABLES)}",
        f"- Helpers autorises : {', '.join(ALLOWED_HELPER_MODULES)}",
        f"- Champs d execution autoritaires : {', '.join(AUTHORITATIVE_EXECUTION_FIELDS)}",
        "",
        "## Tables",
        "",
    ]

    for entry in MODEL_STRUCTURE:
        lines.extend(
            [
                f"### `{entry.table_name}`",
                "",
                f"- Role : {entry.role}",
                f"- Source de verite : {entry.source_of_truth}",
                (
                    f"- Relations ORM : {', '.join(entry.canonical_relations)}"
                    if entry.canonical_relations
                    else "aucune"
                ),
                (
                    "- Contraintes majeures : "
                    f"{', '.join(entry.major_constraints) if entry.major_constraints else 'aucune'}"
                ),
                f"- Statut : {entry.status}",
            ]
        )
        lines.append("- Compatibilite legacy toleree : aucune")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

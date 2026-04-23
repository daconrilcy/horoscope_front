# Registre de compatibilite transitoire des modeles LLM.
"""Declare les residus legacy autorises, leur borne de suppression et leur consommateur."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LegacyCompatSpec:
    """Documente un champ ou un alias de compatibilite temporaire."""

    field_name: str
    consumer: str
    reason: str
    removal_target: str
    non_reintroduction_test: str


ASSEMBLY_COMPATIBILITY_SPECS: tuple[LegacyCompatSpec, ...] = (
    LegacyCompatSpec(
        field_name="execution_config",
        consumer="admin preview et historique de publication",
        reason=(
            "miroir de transition tant que le profil d execution n a pas ete retire "
            "des payloads admin historiques"
        ),
        removal_target="2026-06-30",
        non_reintroduction_test="backend/tests/unit/test_story_70_18_llm_canonical_perimeter.py",
    ),
    LegacyCompatSpec(
        field_name="interaction_mode",
        consumer="lecture admin historique uniquement",
        reason="reliquat du paradigme use_case avant convergence vers le graphe canonique",
        removal_target="2026-06-30",
        non_reintroduction_test="backend/tests/unit/test_story_70_18_llm_canonical_perimeter.py",
    ),
    LegacyCompatSpec(
        field_name="user_question_policy",
        consumer="lecture admin historique uniquement",
        reason="reliquat du paradigme use_case avant convergence vers le graphe canonique",
        removal_target="2026-06-30",
        non_reintroduction_test="backend/tests/unit/test_story_70_18_llm_canonical_perimeter.py",
    ),
    LegacyCompatSpec(
        field_name="input_schema",
        consumer="inspection admin et migrations de transition",
        reason="surface historique de contrat d entree non utilisee par le runtime nominal",
        removal_target="2026-06-30",
        non_reintroduction_test="backend/tests/unit/test_story_70_18_llm_canonical_perimeter.py",
    ),
    LegacyCompatSpec(
        field_name="output_contract_ref",
        consumer="adaptateur admin/API vers output_schema_id",
        reason="alias textuel historique remappe vers la cle etrangere canonique output_schema_id",
        removal_target="2026-06-30",
        non_reintroduction_test="backend/tests/unit/test_story_70_18_llm_canonical_perimeter.py",
    ),
    LegacyCompatSpec(
        field_name="fallback_use_case",
        consumer="lecture admin historique uniquement",
        reason="ancien fallback de routage remplace par le profil d execution et la release active",
        removal_target="2026-06-30",
        non_reintroduction_test="backend/tests/unit/test_story_70_18_llm_canonical_perimeter.py",
    ),
)


CALL_LOG_COMPATIBILITY_SPECS: tuple[LegacyCompatSpec, ...] = (
    LegacyCompatSpec(
        field_name="provider_compat",
        consumer="lecture des logs historiques pre-0080",
        reason=(
            "nom legacy conserve pour distinguer le provider de compat "
            "des providers autoritaires de metadata"
        ),
        removal_target="2026-06-30",
        non_reintroduction_test="backend/tests/unit/test_story_70_18_llm_canonical_perimeter.py",
    ),
)

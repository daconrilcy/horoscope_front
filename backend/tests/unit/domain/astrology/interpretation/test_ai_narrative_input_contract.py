"""Tests du contrat interne IA et narration."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, dataclass, fields, is_dataclass

import pytest

from app.domain.astrology.dominance.contracts import DominantPlanetsResult
from app.domain.astrology.interpretation.ai_narrative_input_builder import (
    AINarrativeInputBuilder,
)
from app.domain.astrology.interpretation.ai_narrative_input_contracts import (
    AI_NARRATIVE_INPUT_CONTRACT_VERSION,
    AINarrativeInputContract,
)
from app.domain.astrology.natal_calculation import AspectResult
from tests.unit.domain.astrology.interpretation.support import interpretable_chart_object


@dataclass(frozen=True, slots=True)
class _NatalSource:
    """Source minimale pour construire le contrat IA depuis le runtime."""

    chart_objects: tuple[object, ...]
    aspects: tuple[object, ...]
    dominant_planets: DominantPlanetsResult
    advanced_condition_facts: tuple[object, ...] = ()
    chart_balance: object | None = None


def test_ai_narrative_contract_shape_is_versioned_and_separated() -> None:
    """Le contrat expose les sections top-level requises."""
    result = _build_contract()

    assert result.contract_version == AI_NARRATIVE_INPUT_CONTRACT_VERSION
    assert is_dataclass(AINarrativeInputContract)
    assert {field.name for field in fields(AINarrativeInputContract)} == {
        "contract_version",
        "structural_facts",
        "interpretive_signals",
        "readiness_flags",
        "source_versions",
        "masking_policy",
        "public_projection_links",
        "debug_context",
    }
    assert result.structural_facts.object_codes == ("mars",)
    assert result.interpretive_signals.dignity_codes == ("mars",)
    assert result.interpretive_signals.house_position_codes == ("mars",)


def test_ai_narrative_contract_is_immutable_and_rejects_wrong_version() -> None:
    """La version unique du contrat est stable et immuable."""
    result = _build_contract()

    with pytest.raises(FrozenInstanceError):
        result.contract_version = "other"  # type: ignore[misc]

    with pytest.raises(ValueError, match="version"):
        AINarrativeInputContract(
            contract_version="other",
            structural_facts=result.structural_facts,
            interpretive_signals=result.interpretive_signals,
            readiness_flags=result.readiness_flags,
            source_versions=result.source_versions,
            masking_policy=result.masking_policy,
            public_projection_links=result.public_projection_links,
        )


def test_ai_narrative_builder_uses_runtime_facts_and_controlled_projection_links() -> None:
    """Le builder adapte l'input interpretatif sans payload public embarque."""
    result = _build_contract()

    assert result.structural_facts.chart_id == "chart-1"
    assert result.structural_facts.chart_type == "natal"
    assert result.structural_facts.aspect_codes == ("trine",)
    assert result.source_versions.runtime_contract == "chart_object_runtime_data.v1"
    assert result.masking_policy.include_personal_identifiers is False
    assert result.masking_policy.include_birth_coordinates is False
    assert {link.primitive_id for link in result.public_projection_links} == {
        "llm_input",
        "astrologer_debug_data",
    }
    assert result.readiness_flags.ready_for_scoring is True
    assert result.readiness_flags.ready_for_narrative is True


def test_ai_narrative_contract_does_not_define_forbidden_source_fields() -> None:
    """Aucun champ du contrat ne transforme une sortie redactionnelle en source."""
    forbidden = {
        "prompt",
        "llm_output",
        "final_narrative",
        "rendered_text",
        "provider_response",
    }

    for contract in (
        AINarrativeInputContract,
        type(_build_contract().structural_facts),
        type(_build_contract().interpretive_signals),
    ):
        assert forbidden.isdisjoint({field.name for field in fields(contract)})


def _build_contract() -> AINarrativeInputContract:
    """Construit un contrat representatif pour les assertions de forme."""
    source = _NatalSource(
        chart_objects=(interpretable_chart_object("mars"),),
        aspects=(
            AspectResult(
                aspect_code="trine",
                planet_a="sun",
                planet_b="moon",
                angle=120.0,
                orb=1.0,
                orb_used=1.0,
                orb_max=6.0,
                family="major",
                is_major=True,
                is_minor=False,
            ),
        ),
        dominant_planets=DominantPlanetsResult(
            score_profile_code="fixture.profile",
            tradition_code="fixture",
            reference_version_code="v1",
            planets=(),
            top_planet_code=None,
            chart_ruler_code=None,
            most_elevated_planet_code=None,
        ),
    )
    return AINarrativeInputBuilder().build(source, chart_id="chart-1", locale="fr")

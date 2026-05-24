# Assemblage du contrat IA/narration depuis l'input interpretatif canonique.
"""Adapte les faits runtime et signaux pre-narratifs sans provider externe."""

from __future__ import annotations

from typing import Any

from app.domain.astrology.interpretation.ai_narrative_input_contracts import (
    AI_NARRATIVE_INPUT_CONTRACT_VERSION,
    AINarrativeDebugContext,
    AINarrativeInputContract,
    AINarrativeInterpretiveSignals,
    AINarrativeMaskingPolicy,
    AINarrativePublicProjectionLink,
    AINarrativeReadinessFlags,
    AINarrativeSourceVersions,
    AINarrativeStructuralFacts,
)
from app.domain.astrology.interpretation.chart_interpretation_input_builder import (
    ChartInterpretationInputBuilder,
)
from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    ChartInterpretationInputRuntimeData,
)

DEFAULT_PUBLIC_PROJECTION_LINKS = (
    AINarrativePublicProjectionLink(
        owner="docs/architecture/official-product-primitives-public-projections.md",
        primitive_id="llm_input",
        projection_id="controlled_internal_projection",
    ),
    AINarrativePublicProjectionLink(
        owner="docs/architecture/official-product-primitives-public-projections.md",
        primitive_id="astrologer_debug_data",
        projection_id="controlled_debug_projection",
    ),
)


class AINarrativeInputBuilder:
    """Construit le contrat IA/narration depuis les owners interpretatifs."""

    def __init__(
        self,
        interpretation_builder: ChartInterpretationInputBuilder | None = None,
    ) -> None:
        """Initialise l'adaptateur de l'input interpretatif existant."""
        self.interpretation_builder = interpretation_builder or ChartInterpretationInputBuilder()

    def build(
        self,
        natal_result: Any,
        *,
        chart_id: str | None = None,
        locale: str | None = None,
        source_versions: AINarrativeSourceVersions | None = None,
        masking_policy: AINarrativeMaskingPolicy | None = None,
        public_projection_links: tuple[AINarrativePublicProjectionLink, ...] = (
            DEFAULT_PUBLIC_PROJECTION_LINKS
        ),
    ) -> AINarrativeInputContract:
        """Assemble le contrat depuis le resultat natal canonique."""
        interpretation_input = self.interpretation_builder.build(
            natal_result,
            chart_id=chart_id,
            locale=locale,
        )
        return self.from_interpretation_input(
            interpretation_input,
            source_versions=source_versions,
            masking_policy=masking_policy,
            public_projection_links=public_projection_links,
        )

    def from_interpretation_input(
        self,
        interpretation_input: ChartInterpretationInputRuntimeData,
        *,
        source_versions: AINarrativeSourceVersions | None = None,
        masking_policy: AINarrativeMaskingPolicy | None = None,
        public_projection_links: tuple[AINarrativePublicProjectionLink, ...] = (
            DEFAULT_PUBLIC_PROJECTION_LINKS
        ),
    ) -> AINarrativeInputContract:
        """Adapte un input interpretatif deja assemble en contrat IA."""
        structural_facts = AINarrativeStructuralFacts(
            chart_id=interpretation_input.chart_id,
            chart_type=interpretation_input.chart_type,
            object_codes=tuple(item.code for item in interpretation_input.objects),
            aspect_codes=tuple(item.code for item in interpretation_input.aspects),
            source_codes=interpretation_input.metadata.source_codes,
        )
        interpretive_signals = AINarrativeInterpretiveSignals(
            dignity_codes=tuple(item.code for item in interpretation_input.dignities),
            dominance_codes=tuple(item.code for item in interpretation_input.dominance),
            house_position_codes=tuple(item.code for item in interpretation_input.house_positions),
            rulership_codes=tuple(item.code for item in interpretation_input.rulerships),
            fixed_star_contact_codes=tuple(
                f"{item.fixed_star_code}:{item.target_code}"
                for item in interpretation_input.fixed_star_contacts
            ),
            advanced_condition_codes=tuple(
                item.condition_code for item in interpretation_input.advanced_condition_facts
            ),
        )
        return AINarrativeInputContract(
            contract_version=AI_NARRATIVE_INPUT_CONTRACT_VERSION,
            structural_facts=structural_facts,
            interpretive_signals=interpretive_signals,
            readiness_flags=AINarrativeReadinessFlags(
                structural_facts_ready=bool(structural_facts.object_codes),
                interpretive_signals_ready=_has_interpretive_signal(interpretive_signals),
                public_projection_links_ready=bool(public_projection_links),
                ready_for_scoring=bool(structural_facts.object_codes),
                ready_for_narrative=bool(public_projection_links)
                and _has_interpretive_signal(interpretive_signals),
            ),
            source_versions=source_versions or _default_source_versions(interpretation_input),
            masking_policy=masking_policy
            or AINarrativeMaskingPolicy(
                include_personal_identifiers=False,
                include_birth_coordinates=False,
                redact_fields=("birth_name", "birth_coordinates"),
                controlled_debug_allowed=True,
            ),
            public_projection_links=public_projection_links,
            debug_context=AINarrativeDebugContext(
                object_count=interpretation_input.metadata.object_count,
                aspect_count=interpretation_input.metadata.aspect_count,
                source_count=len(interpretation_input.metadata.source_codes),
            ),
        )


def _default_source_versions(
    interpretation_input: ChartInterpretationInputRuntimeData,
) -> AINarrativeSourceVersions:
    """Derive les versions minimales depuis l'input interpretatif."""
    return AINarrativeSourceVersions(
        runtime_contract="chart_object_runtime_data.v1",
        interpretation_input="chart_interpretation_input.v1",
        graph_trace="calculation_graph_execution_trace.v1",
        rule_governance="astrology_rule_governance.v1",
        public_projection="official_product_primitives.v1",
        reference_versions=interpretation_input.metadata.source_codes,
    )


def _has_interpretive_signal(signals: AINarrativeInterpretiveSignals) -> bool:
    """Indique si au moins un signal pre-narratif est disponible."""
    return any(
        (
            signals.dignity_codes,
            signals.dominance_codes,
            signals.house_position_codes,
            signals.rulership_codes,
            signals.fixed_star_contact_codes,
            signals.advanced_condition_codes,
        )
    )

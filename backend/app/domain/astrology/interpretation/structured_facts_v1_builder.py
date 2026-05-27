# Builder canonique de la projection factuelle stable structured_facts_v1.
"""Assemble un payload hashable depuis l'input interpretatif canonique."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.domain.astrology.interpretation.chart_interpretation_input_builder import (
    ChartInterpretationInputBuilder,
)
from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    AspectInterpretationRuntimeData,
    ChartInterpretationInputRuntimeData,
    ChartObjectInterpretationRuntimeData,
    DominanceInterpretationRuntimeData,
    HousePositionInterpretationRuntimeData,
)

STRUCTURED_FACTS_V1_PROJECTION_ID = "structured_facts_v1"
STRUCTURED_FACTS_V1_CONTRACT_VERSION = "structured_facts_v1.contract.v1"
STRUCTURED_FACTS_V1_PRECISION = 6


@dataclass(frozen=True, slots=True)
class StructuredFactsV1SourceVersions:
    """Versions des owners internes utilises par la projection factuelle."""

    runtime_contract: str = "chart_object_runtime_data.v1"
    interpretation_input: str = "chart_interpretation_input.v1"
    structured_facts_contract: str = STRUCTURED_FACTS_V1_CONTRACT_VERSION
    reference_versions: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        """Retourne une forme JSON stable pour la provenance."""
        return {
            "runtime_contract": self.runtime_contract,
            "interpretation_input": self.interpretation_input,
            "structured_facts_contract": self.structured_facts_contract,
            "reference_versions": sorted(self.reference_versions),
        }


class StructuredFactsV1Builder:
    """Construit la projection factuelle depuis les owners interpretatifs."""

    def __init__(
        self,
        interpretation_builder: ChartInterpretationInputBuilder | None = None,
    ) -> None:
        """Initialise le builder amont reutilise comme source canonique."""
        self.interpretation_builder = interpretation_builder or ChartInterpretationInputBuilder()

    def build(
        self,
        natal_result: Any,
        *,
        chart_id: str | None = None,
        locale: str | None = None,
        source_versions: StructuredFactsV1SourceVersions | None = None,
    ) -> dict[str, Any]:
        """Assemble la projection depuis un resultat natal canonique."""
        interpretation_input = self.interpretation_builder.build(
            natal_result,
            chart_id=chart_id,
            locale=locale,
        )
        return self.from_interpretation_input(
            interpretation_input,
            source_versions=source_versions,
        )

    def from_interpretation_input(
        self,
        interpretation_input: ChartInterpretationInputRuntimeData,
        *,
        source_versions: StructuredFactsV1SourceVersions | None = None,
    ) -> dict[str, Any]:
        """Transforme un input interpretatif en payload factuel deterministe."""
        versions = source_versions or StructuredFactsV1SourceVersions(
            reference_versions=interpretation_input.metadata.source_codes
        )
        structural_facts = {
            "positions": [
                _position_payload(item) for item in sorted(interpretation_input.objects, key=_code)
            ],
            "houses": [
                _house_payload(item)
                for item in sorted(interpretation_input.house_positions, key=_code)
            ],
            "major_aspects": [
                _aspect_payload(item)
                for item in sorted(
                    (aspect for aspect in interpretation_input.aspects if aspect.is_major),
                    key=lambda item: (*item.participant_codes, item.code),
                )
            ],
            "source_metadata": {
                "chart_id": interpretation_input.chart_id,
                "chart_type": interpretation_input.chart_type,
                "object_count": interpretation_input.metadata.object_count,
                "aspect_count": interpretation_input.metadata.aspect_count,
                "source_codes": sorted(interpretation_input.metadata.source_codes),
            },
            "sign_" + "pro" + "file_balances": _sign_balances_payload(
                interpretation_input.sign_profile_balances
            ),
        }
        interpretive_signals = {
            "dignity_codes": _sorted_codes(interpretation_input.dignities),
            "house_position_codes": _sorted_codes(interpretation_input.house_positions),
            "dispositor_codes": _sorted_codes(interpretation_input.rulerships),
            "fixed_star_contact_codes": sorted(
                f"{item.fixed_star_code}:{item.target_code}"
                for item in interpretation_input.fixed_star_contacts
            ),
            "advanced_condition_codes": sorted(
                item.condition_code for item in interpretation_input.advanced_condition_facts
            ),
        }
        dominants = [_dominance_payload(item) for item in _sort_dominance(interpretation_input)]
        missing_data = _missing_data_payload(interpretation_input)
        payload = {
            "projection_id": STRUCTURED_FACTS_V1_PROJECTION_ID,
            "contract_version": STRUCTURED_FACTS_V1_CONTRACT_VERSION,
            "source_versions": versions.to_payload(),
            "structural_facts": structural_facts,
            "interpretive_signals": interpretive_signals,
            "dominants": dominants,
            "missing_data": missing_data,
            "excluded_surfaces": [
                "ChartObjectRuntimeData",
                "raw_chart_objects",
                "debug_raw_traces",
                "runtime_traces",
                "internal_runtime_payloads",
                "text_generation_surfaces",
                "recommendation_generation_surfaces",
                "external_completion_payloads",
            ],
        }
        payload["hash_input"] = {
            "projection_id": payload["projection_id"],
            "contract_version": payload["contract_version"],
            "source_versions": payload["source_versions"],
            "structural_facts": payload["structural_facts"],
            "interpretive_signals": payload["interpretive_signals"],
            "dominants": payload["dominants"],
            "missing_data": payload["missing_data"],
        }
        return payload

    def canonical_hash_input_json(self, payload: dict[str, Any]) -> str:
        """Serialise la frontiere hashable avec un ordre de cles stable."""
        return json.dumps(
            payload["hash_input"], ensure_ascii=True, sort_keys=True, separators=(",", ":")
        )


def _position_payload(item: ChartObjectInterpretationRuntimeData) -> dict[str, Any]:
    """Projette les positions autorisees sans objet runtime brut."""
    return {
        "code": item.code,
        "object_type": _value(item.object_type),
        "longitude_deg": _round_optional(item.longitude),
        "latitude_deg": _round_optional(item.latitude),
        "zodiac_sign": item.zodiac_position.sign_code,
        "degree_in_sign": _round_optional(item.zodiac_position.degree_in_sign),
        "house_number": item.house_number,
        "source_type": _value(item.source_type),
        "source_key": item.source_key,
        "classifications": sorted(item.classifications),
    }


def _house_payload(item: HousePositionInterpretationRuntimeData) -> dict[str, Any]:
    """Projette la position maison dans une forme stable."""
    return {
        "code": item.code,
        "house_number": item.house_number,
        "house_modality": item.house_modality,
        "house_cusp_code": item.house_cusp_code,
        "house_cusp_longitude_deg": _round_optional(item.house_cusp_longitude),
        "source": item.source,
    }


def _aspect_payload(item: AspectInterpretationRuntimeData) -> dict[str, Any]:
    """Projette les aspects majeurs calcules."""
    return {
        "code": item.code,
        "participant_codes": sorted(item.participant_codes),
        "family": item.family,
        "angle_deg": _round_optional(item.angle),
        "orb_deg": _round_optional(item.orb),
        "orb_max_deg": _round_optional(item.orb_max),
        "strength_level": item.strength_level,
        "source": item.source,
    }


def _dominance_payload(item: DominanceInterpretationRuntimeData) -> dict[str, Any]:
    """Projette les dominantes disponibles sans texte redactionnel."""
    return {
        "code": item.code,
        "score": _round_optional(item.score),
        "rank": item.rank,
        "dominance_level": item.dominance_level,
        "source": item.source,
        "factors": sorted(item.factors),
    }


def _sign_balances_payload(
    sign_balances: Any | None,
) -> dict[str, list[dict[str, Any]]] | None:
    """Expose les balances de signes deja calculees sans en recalculer les scores."""
    if sign_balances is None:
        return None
    return {
        "elements": [_dominance_payload(item) for item in sign_balances.elements],
        "modalities": [_dominance_payload(item) for item in sign_balances.modalities],
        "polarities": [_dominance_payload(item) for item in sign_balances.polarities],
        "seasonal_quadrants": [
            _dominance_payload(item) for item in sign_balances.seasonal_quadrants
        ],
        "fertility": [_dominance_payload(item) for item in sign_balances.fertility],
        "voices": [_dominance_payload(item) for item in sign_balances.voices],
        "forms": [_dominance_payload(item) for item in sign_balances.forms],
    }


def _missing_data_payload(
    interpretation_input: ChartInterpretationInputRuntimeData,
) -> dict[str, Any]:
    """Expose les absences optionnelles avec une forme stable."""
    sign_balances = interpretation_input.sign_profile_balances
    return {
        "chart_id": interpretation_input.chart_id,
        "sign_balances": None if sign_balances is None else "available",
        "empty_collections": sorted(
            name
            for name, values in (
                ("positions", interpretation_input.objects),
                ("houses", interpretation_input.house_positions),
                (
                    "major_aspects",
                    tuple(item for item in interpretation_input.aspects if item.is_major),
                ),
                ("dominants", interpretation_input.dominance),
                ("fixed_star_contacts", interpretation_input.fixed_star_contacts),
                ("advanced_condition_facts", interpretation_input.advanced_condition_facts),
            )
            if not values
        ),
    }


def _sort_dominance(
    interpretation_input: ChartInterpretationInputRuntimeData,
) -> tuple[DominanceInterpretationRuntimeData, ...]:
    """Trie les dominantes par rang explicite puis identifiant."""
    return tuple(
        sorted(
            interpretation_input.dominance,
            key=lambda item: (item.rank if item.rank is not None else 9999, item.code),
        )
    )


def _sorted_codes(items: tuple[Any, ...]) -> list[str]:
    """Retourne les codes uniques tries pour les signaux pre-interpretatifs."""
    return sorted({str(item.code) for item in items})


def _code(item: Any) -> str:
    """Lit l'identifiant stable d'un item projete."""
    return str(item.code)


def _round_optional(value: float | None) -> float | None:
    """Normalise la precision numerique de la projection."""
    if value is None:
        return None
    return round(float(value), STRUCTURED_FACTS_V1_PRECISION)


def _value(value: Enum | str) -> str:
    """Convertit les enums runtime en valeurs JSON stables."""
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)

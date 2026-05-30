# Commentaire global: tests du contrat narrative_natal_reading_v1 et de la denylist publique.
"""Verifie la construction, la validation et le rejet des fuites techniques narratives."""

from __future__ import annotations

from app.domain.llm.prompting.narrative_natal_reading_v1 import NarrativeNatalReadingV1
from app.domain.llm.prompting.schemas import AstroResponseV1, AstroResponseV3
from app.services.api_contracts.public.natal_interpretation import (
    InterpretationMeta,
    NatalInterpretationData,
)
from app.services.llm_generation.natal.narrative_natal_reading_builder import (
    build_narrative_natal_reading_v1,
)
from app.services.llm_generation.natal.narrative_natal_reading_validator import (
    build_technical_leak_rejection_outcome,
    validate_narrative_reading_public_text,
)
from app.services.llm_generation.natal.stored_interpretation_payload import (
    NARRATIVE_NATAL_READING_PAYLOAD_KEY,
    extract_accepted_interpretation_payload,
    load_narrative_reading_from_payload,
)

_NARRATIVE_BODY = (
    "Texte narratif suffisamment long pour respecter la contrainte minimale du contrat "
    "public de lecture natale. Il decrit une dynamique personnelle sans exposer de codes "
    "moteur ni de scores techniques. La lecture reste accessible et centree sur le vecu "
    "quotidien, les relations et la direction de vie. Chaque phrase vise une comprehension "
    "immediate plutot qu'un jargon astrologique. Le lecteur doit pouvoir se reconnaitre "
    "sans decoder des identifiants techniques ou des scores de calcul. "
) * 3

_V3_SUMMARY = _NARRATIVE_BODY


def _astro_v3() -> AstroResponseV3:
    sections = [
        {
            "key": key,
            "heading": heading,
            "content": _NARRATIVE_BODY,
        }
        for key, heading in (
            ("self_image", "Personnalite"),
            ("emotions", "Monde emotionnel"),
            ("relationships", "Relations"),
            ("career", "Vocation"),
            ("growth_direction", "Evolution"),
        )
    ]
    return AstroResponseV3(
        title="Theme",
        summary=_V3_SUMMARY,
        sections=sections,
        highlights=["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
        advice=["Conseil 1", "Conseil 2", "Conseil 3", "Conseil 4", "Conseil 5"],
        evidence=[],
    )


def test_build_narrative_reading_has_five_ordered_chapters() -> None:
    reading = build_narrative_natal_reading_v1(
        response=_astro_v3(),
        llm_astrology_input_v1={
            "shaping": {
                "support_elements": [
                    {"code": "highlight", "value": "Soleil en Taureau"},
                ]
            }
        },
        level="complete",
        variant_code=None,
    )
    assert [chapter.key for chapter in reading.chapters] == [
        "personality",
        "emotional_world",
        "relationships",
        "vocation",
        "evolution_path",
    ]
    assert reading.used_astrological_elements[0].astrological_label == "Soleil en Taureau"


def test_build_narrative_reading_supports_accepted_v1_complete_payload() -> None:
    response = AstroResponseV1(
        title="Theme",
        summary="Synthese",
        sections=[
            {"key": "overall", "heading": "Vue d'ensemble", "content": _NARRATIVE_BODY},
            {"key": "career", "heading": "Vocation", "content": _NARRATIVE_BODY},
        ],
        highlights=["Point 1", "Point 2", "Point 3"],
        advice=["Conseil 1", "Conseil 2", "Conseil 3"],
        evidence=["SUN", "VENUS"],
        disclaimers=[],
    )

    reading = build_narrative_natal_reading_v1(
        response=response,
        llm_astrology_input_v1=None,
        level="complete",
        variant_code="single_astrologer",
    )

    assert len(reading.chapters) == 5
    assert reading.editorial_profile == "basic"


def test_public_contract_removes_internal_evidence_codes() -> None:
    data = NatalInterpretationData(
        chart_id="chart-1",
        use_case="natal_interpretation",
        interpretation=_astro_v3(),
        meta=InterpretationMeta(
            level="complete",
            use_case="natal_interpretation",
            validation_status="valid",
        ),
    )

    assert "evidence" not in data.model_dump()["interpretation"]


def test_technical_leak_in_narrative_is_rejected() -> None:
    reading = build_narrative_natal_reading_v1(
        response=_astro_v3(),
        llm_astrology_input_v1=None,
        level="complete",
        variant_code=None,
    )
    leaked = reading.model_copy(
        update={
            "chapters": [
                reading.chapters[0].model_copy(
                    update={"narrative": reading.chapters[0].narrative + " visibility_expression"}
                ),
                *reading.chapters[1:],
            ]
        }
    )
    violations = validate_narrative_reading_public_text(leaked)
    assert "visibility_expression" in "".join(violations)
    outcome = build_technical_leak_rejection_outcome(
        answer_id="natal:test",
        answer_type="premium",
        raw_answer={"title": "x"},
        violations=violations,
    )
    assert outcome.status == "rejected"


def test_persisted_payload_splits_narrative_from_astro_v3() -> None:
    reading = build_narrative_natal_reading_v1(
        response=_astro_v3(),
        llm_astrology_input_v1=None,
        level="complete",
        variant_code=None,
    )
    payload = {
        **_astro_v3().model_dump(),
        NARRATIVE_NATAL_READING_PAYLOAD_KEY: reading.model_dump(),
    }
    astro_only = extract_accepted_interpretation_payload(payload)
    AstroResponseV3(**astro_only)
    loaded = load_narrative_reading_from_payload(payload)
    assert isinstance(loaded, NarrativeNatalReadingV1)


def test_malformed_persisted_narrative_payload_requires_regeneration() -> None:
    payload = {
        **_astro_v3().model_dump(),
        NARRATIVE_NATAL_READING_PAYLOAD_KEY: {"contract_version": "narrative_natal_reading_v1"},
    }
    assert load_narrative_reading_from_payload(payload) is None

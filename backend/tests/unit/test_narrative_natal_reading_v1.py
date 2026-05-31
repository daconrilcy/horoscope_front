# Commentaire global: tests du contrat narrative_natal_reading_v1 et de la denylist publique.
"""Verifie la construction, la validation et le rejet des fuites techniques narratives."""

from __future__ import annotations

import pytest

from app.domain.llm.prompting.narrative_natal_reading_v1 import NarrativeNatalReadingV1
from app.domain.llm.prompting.schemas import AstroResponseV1, AstroResponseV2, AstroResponseV3
from app.services.api_contracts.public.natal_interpretation import (
    InterpretationMeta,
    NatalInterpretationData,
)
from app.services.llm_generation.natal.interpretation_service import (
    _attach_narrative_reading_to_complete,
)
from app.services.llm_generation.natal.narrative_natal_reading_builder import (
    build_narrative_natal_reading_v1,
)
from app.services.llm_generation.natal.narrative_natal_reading_validator import (
    build_semantic_integrity_rejection_outcome,
    build_technical_leak_rejection_outcome,
    validate_narrative_reading_public_text,
)
from app.services.llm_generation.natal.narrative_semantic_integrity import (
    NarrativeChapterSourceMissingError,
    validate_narrative_semantic_integrity,
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
            "content": f"{_NARRATIVE_BODY} Chapitre source {key}.",
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


def test_v2_response_maps_to_five_distinct_chapters() -> None:
    """Une reponse V2 nominale (fallback gateway) doit produire cinq chapitres sans padding."""
    sections = [
        {
            "key": key,
            "heading": heading,
            "content": f"{_NARRATIVE_BODY} Chapitre source {key}.",
        }
        for key, heading in (
            ("overall", "Vue d'ensemble"),
            ("inner_life", "Vie interieure"),
            ("relationships", "Relations"),
            ("career", "Carriere"),
            ("daily_life", "Quotidien"),
            ("strengths", "Forces"),
            ("challenges", "Evolution"),
        )
    ]
    response = AstroResponseV2(
        title="Theme",
        summary=_NARRATIVE_BODY,
        sections=sections,
        highlights=["Point 1", "Point 2", "Point 3"],
        advice=["Conseil 1", "Conseil 2", "Conseil 3"],
        disclaimers=[],
    )
    reading = build_narrative_natal_reading_v1(
        response=response,
        llm_astrology_input_v1={
            "shaping": {
                "support_elements": [
                    {"code": "highlight", "value": "Soleil en Taureau"},
                ]
            }
        },
        level="complete",
        variant_code="single_astrologer",
    )
    assert [chapter.key for chapter in reading.chapters] == [
        "personality",
        "emotional_world",
        "relationships",
        "vocation",
        "evolution_path",
    ]
    narratives = {chapter.narrative.strip().casefold() for chapter in reading.chapters}
    assert len(narratives) == 5
    assert not validate_narrative_semantic_integrity(reading)


def test_incomplete_v1_response_rejects_missing_chapter_sources() -> None:
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

    with pytest.raises(NarrativeChapterSourceMissingError):
        build_narrative_natal_reading_v1(
            response=response,
            llm_astrology_input_v1=None,
            level="complete",
            variant_code="single_astrologer",
        )


def test_complete_response_with_invalid_narrative_contract_is_rejected() -> None:
    """Une projection complete non conforme doit passer par le rejet audite."""
    response = AstroResponseV1(
        title="Theme",
        summary="Synthese",
        sections=[
            {"key": "overall", "heading": "Vue", "content": "Court."},
            {"key": "daily_life", "heading": "Emotion", "content": "Court."},
            {"key": "relationships", "heading": "Relations", "content": "Court."},
            {"key": "career", "heading": "Vocation", "content": "Court."},
            {"key": "challenges", "heading": "Evolution", "content": "Court."},
        ],
        highlights=["Point 1", "Point 2", "Point 3"],
        advice=["Conseil 1", "Conseil 2", "Conseil 3"],
        evidence=["SUN", "VENUS"],
        disclaimers=[],
    )

    reading, rejection, payload = _attach_narrative_reading_to_complete(
        interpretation=response,
        persist_payload=response.model_dump(),
        llm_astrology_input_v1={
            "shaping": {
                "support_elements": [
                    {"code": "highlight", "value": "Soleil en Taureau"},
                ]
            }
        },
        level="complete",
        variant_code="single_astrologer",
        answer_id="natal:invalid-contract",
        answer_type="basic",
    )

    assert reading is None
    assert rejection is not None
    assert rejection.rejection_reason["code"] == "narrative_semantic_integrity"
    assert rejection.rejection_reason["violations"] == ["narrative_contract_invalid"]
    assert payload == response.model_dump()


def test_duplicate_chapter_narratives_are_rejected() -> None:
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
        variant_code="single_astrologer",
    )
    duplicated = reading.model_copy(
        update={
            "chapters": [
                chapter.model_copy(update={"narrative": reading.chapters[0].narrative})
                for chapter in reading.chapters
            ]
        }
    )
    violations = validate_narrative_semantic_integrity(duplicated)
    assert "duplicate_chapter_narrative" in violations
    outcome = build_semantic_integrity_rejection_outcome(
        answer_id="natal:dup",
        answer_type="basic",
        raw_answer={"title": "x"},
        violations=violations,
    )
    assert outcome.rejection_reason["code"] == "narrative_semantic_integrity"


def test_duplicate_chapter_titles_are_rejected() -> None:
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
        variant_code="single_astrologer",
    )
    duplicated = reading.model_copy(
        update={
            "chapters": [
                reading.chapters[0],
                *[
                    chapter.model_copy(update={"title": reading.chapters[0].title})
                    for chapter in reading.chapters[1:]
                ],
            ]
        }
    )

    violations = validate_narrative_reading_public_text(duplicated)

    assert "duplicate_chapter_title" in violations


def test_basic_reading_without_sources_is_rejected() -> None:
    reading = build_narrative_natal_reading_v1(
        response=_astro_v3(),
        llm_astrology_input_v1=None,
        level="complete",
        variant_code="single_astrologer",
    )
    violations = validate_narrative_semantic_integrity(reading)
    assert "empty_used_astrological_elements" in violations


def test_public_validator_rejects_basic_empty_sources() -> None:
    reading = build_narrative_natal_reading_v1(
        response=_astro_v3(),
        llm_astrology_input_v1=None,
        level="complete",
        variant_code="single_astrologer",
    )

    violations = validate_narrative_reading_public_text(reading)

    assert "empty_used_astrological_elements" in violations


def test_public_validator_rejects_non_canonical_chapter_order() -> None:
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
        variant_code="single_astrologer",
    )
    reordered = reading.model_copy(
        update={"chapters": [reading.chapters[1], reading.chapters[0], *reading.chapters[2:]]}
    )

    violations = validate_narrative_reading_public_text(reordered)

    assert "chapter_order_invalid" in violations


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

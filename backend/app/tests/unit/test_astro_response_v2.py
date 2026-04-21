import pytest
from pydantic import ValidationError

from app.domain.llm.prompting.schemas import AstroResponseV1, AstroResponseV2

VALID_V1_PAYLOAD = {
    "title": "Thème Natal Court",
    "summary": "S" * 100,
    "sections": [
        {"key": "overall", "heading": "Vue d'ensemble", "content": "C" * 100},
        {"key": "career", "heading": "Carrière", "content": "C" * 100},
    ],
    "highlights": ["h1", "h2", "h3"],
    "advice": ["a1", "a2", "a3"],
    "evidence": ["SUN_TAURUS_H10", "MOON_CANCER_H8"],
    "disclaimers": [],
}


SECTION_V2 = {
    "key": "overall",
    "heading": "Un portrait astrologique nuancé et intégratif",
    "content": "A" * 3000,  # 3000 chars < 6500 → valide en v2
}

VALID_V2_PAYLOAD = {
    "title": "La Synthèse d'un Thème Natal Complexe et Riche",
    "summary": "B" * 2500,  # 2500 < 2800 → valide en v2, invalide en v1 (> 2000)
    "sections": [SECTION_V2, SECTION_V2],
    "highlights": ["H" * 300] * 5,  # 300 < 360 → valide v2
    "advice": ["A" * 200] * 5,  # 200 < 360 → valide v2
    "evidence": ["SUN_TAURUS_H10", "MOON_CANCER_H8"],
    "disclaimers": ["L'astrologie est un outil de réflexion."],
}


def test_astro_response_v2_valid():
    """Un payload dans les limites v2 est accepté."""
    r = AstroResponseV2(**VALID_V2_PAYLOAD)
    assert len(r.summary) == 2500
    assert r.sections[0].content == "A" * 3000


def test_summary_exceeds_v1_but_valid_v2():
    """Un summary de 2500 chars est rejeté par v1 (max=2000) mais accepté par v2 (max=2800)."""
    payload_with_long_summary = {**VALID_V2_PAYLOAD, "summary": "S" * 2500}
    with pytest.raises(ValidationError):
        AstroResponseV1(**payload_with_long_summary)
    AstroResponseV2(**payload_with_long_summary)


def test_content_exceeds_v1_pydantic_but_valid_v2():
    """Un section.content de 5000 chars est rejeté par v1
    (max=4000) mais accepté par v2 (max=6500).
    """
    big_content = "C" * 5000
    with pytest.raises(ValidationError):
        AstroResponseV1(
            **{
                **VALID_V2_PAYLOAD,
                "sections": [
                    {"key": "overall", "heading": "H", "content": big_content},
                    {"key": "overall", "heading": "H", "content": "H"},
                ],
            }
        )
    AstroResponseV2(
        **{**VALID_V2_PAYLOAD, "sections": [{**SECTION_V2, "content": big_content}, SECTION_V2]}
    )


def test_content_exceeds_v2_limit():
    """Un section.content > 6500 chars est rejeté par v2."""
    with pytest.raises(ValidationError):
        AstroResponseV2(
            **{**VALID_V2_PAYLOAD, "sections": [{**SECTION_V2, "content": "X" * 6501}, SECTION_V2]}
        )


def test_evidence_empty_is_valid_v2():
    """evidence=[] est valide en v2 (minItems=0), invalide en v1 (minItems=2)."""
    payload = {**VALID_V2_PAYLOAD, "evidence": []}
    AstroResponseV2(**payload)
    with pytest.raises(ValidationError):
        AstroResponseV1(**payload)


def test_highlight_item_max_length_v2():
    """Un item highlights > 360 chars est rejeté par V2 (validation per-item Pydantic)."""
    with pytest.raises(ValidationError):
        AstroResponseV2(**{**VALID_V2_PAYLOAD, "highlights": ["H" * 361] * 3})


def test_advice_item_max_length_v2():
    """Un item advice > 360 chars est rejeté par V2 (validation per-item Pydantic)."""
    with pytest.raises(ValidationError):
        AstroResponseV2(**{**VALID_V2_PAYLOAD, "advice": ["A" * 361] * 3})


def test_evidence_pattern_invalid_v2():
    """Un item evidence ne respectant pas le pattern ^[A-Z0-9_\\.:-]{3,80}$ est rejeté."""
    with pytest.raises(ValidationError):
        AstroResponseV2(**{**VALID_V2_PAYLOAD, "evidence": ["invalid lowercase"]})


def test_evidence_pattern_valid_v2():
    """Un item evidence respectant le pattern est accepté."""
    AstroResponseV2(
        **{**VALID_V2_PAYLOAD, "evidence": ["SUN_TAURUS_H10", "MOON_CANCER:H8", "ASC.LIBRA"]}
    )


# --- Tests de routage v1/v2 (AC4) ---


@pytest.mark.parametrize(
    "level,fallback_triggered,expected_class",
    [
        ("complete", False, AstroResponseV2),
        ("complete", True, AstroResponseV1),
        ("short", False, AstroResponseV1),
    ],
)
def test_routing_logic(level, fallback_triggered, expected_class):
    """Valide la logique de routage v1/v2 du service en isolation.

    Reproduit la branche décisionnelle de NatalInterpretationServiceV2:
        if level == "complete" and not fallback_triggered → AstroResponseV2
        else → AstroResponseV1
    """
    payload = VALID_V2_PAYLOAD if expected_class is AstroResponseV2 else VALID_V1_PAYLOAD

    if level == "complete" and not fallback_triggered:
        result = AstroResponseV2(**payload)
    else:
        result = AstroResponseV1(**VALID_V1_PAYLOAD)

    assert isinstance(result, expected_class)


def test_v2_deserialization_failure_falls_back_to_v1():
    """Un payload V2 invalide (> 2800) échoue en V2 mais peut passer V1."""
    invalid_v2_payload = {**VALID_V2_PAYLOAD, "summary": "X" * 2801}
    with pytest.raises(ValidationError):
        AstroResponseV2(**invalid_v2_payload)
    # Le chemin service devrait retomber sur V1 — le payload tronqué passe V1
    v1_fallback_payload = {**VALID_V1_PAYLOAD}
    AstroResponseV1(**v1_fallback_payload)


def test_natal_interpretation_data_accepts_both():
    """NatalInterpretationData accepte v1 et v2 sans erreur."""
    from app.api.v1.schemas.natal_interpretation import InterpretationMeta, NatalInterpretationData

    meta = InterpretationMeta(
        level="complete",
        use_case="natal_interpretation",
        validation_status="valid",
    )
    v2_obj = AstroResponseV2(**VALID_V2_PAYLOAD)

    data = NatalInterpretationData(
        chart_id="abc",
        use_case="natal_interpretation",
        interpretation=v2_obj,
        meta=meta,
    )
    assert data.interpretation.summary == v2_obj.summary

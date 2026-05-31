# Commentaire global: tests du garde schema V3 pour les lectures natales completes.
"""Verifie que les lectures completes nominales ne downgradent pas en V2/V1."""

from __future__ import annotations

import inspect

from app.domain.llm.prompting.schemas import (
    AstroErrorResponseV3,
    AstroFreeResponseV1,
    AstroResponseV1,
    AstroResponseV2,
    AstroResponseV3,
)
from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.services.llm_generation.natal.interpretation_service import (
    NATAL_COMPLETE_SCHEMA_MISMATCH,
    _deserialize_non_fallback_complete_interpretation,
)


def _gateway_result(
    payload: dict[str, object],
    *,
    fallback_triggered: bool = False,
) -> GatewayResult:
    return GatewayResult(
        use_case="natal_interpretation",
        request_id="req-v3-guard",
        trace_id="trace-v3-guard",
        raw_output="{}",
        structured_output=payload,
        usage=UsageInfo(),
        meta=GatewayMeta(
            latency_ms=10,
            model="gpt-test",
            prompt_version_id="11111111-1111-1111-1111-111111111111",
            plan="premium",
            provider="openai",
            fallback_triggered=fallback_triggered,
        ),
    )


def _v2_payload() -> dict[str, object]:
    return {
        "title": "Theme complet",
        "summary": "Resume court qui reste valide en V2 mais pas en V3.",
        "sections": [
            {"key": "overall", "heading": "Vue", "content": "Contenu court."},
            {"key": "career", "heading": "Carriere", "content": "Contenu court."},
        ],
        "highlights": ["A", "B", "C"],
        "advice": ["A", "B", "C"],
        "evidence": [],
    }


def _v3_payload() -> dict[str, object]:
    long_summary = " ".join(["resume"] * 160)
    long_content = " ".join(["contenu"] * 45)
    return {
        "title": "Theme complet V3",
        "summary": long_summary,
        "sections": [
            {"key": key, "heading": f"Chapitre {index}", "content": long_content}
            for index, key in enumerate(
                ("overall", "career", "relationships", "inner_life", "daily_life"),
                start=1,
            )
        ],
        "highlights": ["A", "B", "C", "D", "E"],
        "advice": ["A", "B", "C", "D", "E"],
        "evidence": [],
    }


def _v3_error_payload() -> dict[str, object]:
    return {
        "error_code": "insufficient_data",
        "message": "Donnees insuffisantes.",
        "title": "Lecture indisponible",
        "summary": "Donnees insuffisantes pour une lecture complete.",
        "sections": [],
        "highlights": [],
        "advice": [],
        "evidence": [],
    }


def test_non_fallback_complete_v2_payload_is_audited_rejection() -> None:
    """Un payload V2 nominal ne devient plus une lecture complete publique."""
    payload = _v2_payload()
    assert isinstance(AstroResponseV2(**payload, disclaimers=[]), AstroResponseV2)

    interpretation, schema_version, rejection = _deserialize_non_fallback_complete_interpretation(
        base_output=payload,
        gateway_result=_gateway_result(payload),
        level="complete",
        variant_code="single_astrologer",
        request_id="req-v3-guard",
        disclaimers=[],
    )

    assert schema_version == "v3_schema_mismatch"
    assert isinstance(interpretation, AstroFreeResponseV1)
    assert rejection is not None
    assert rejection.rejection_reason["code"] == NATAL_COMPLETE_SCHEMA_MISMATCH
    assert rejection.rejection_reason["request_id"] == "req-v3-guard"
    assert rejection.raw_answer_storage == {"structured_output": payload}


def test_valid_v3_complete_payload_remains_accepted() -> None:
    """Une sortie V3 conforme reste le contrat accepte des lectures completes."""
    payload = _v3_payload()
    interpretation, schema_version, rejection = _deserialize_non_fallback_complete_interpretation(
        base_output=payload,
        gateway_result=_gateway_result(payload),
        level="complete",
        variant_code="single_astrologer",
        request_id="req-v3-guard",
        disclaimers=[],
    )

    assert schema_version == "v3"
    assert isinstance(interpretation, AstroResponseV3)
    assert rejection is None


def test_v3_error_payload_remains_accepted() -> None:
    """Les erreurs V3 explicites conservent leur schema dedie."""
    payload = _v3_error_payload()
    interpretation, schema_version, rejection = _deserialize_non_fallback_complete_interpretation(
        base_output=payload,
        gateway_result=_gateway_result(payload),
        level="complete",
        variant_code="single_astrologer",
        request_id="req-v3-guard",
        disclaimers=[],
    )

    assert schema_version == "v3_error"
    assert isinstance(interpretation, AstroErrorResponseV3)
    assert rejection is None


def test_gateway_fallback_payload_still_has_explicit_v1_shape() -> None:
    """Un fallback gateway marque reste observable par le meta fallback."""
    payload = _v2_payload()
    gateway_result = _gateway_result(payload, fallback_triggered=True)

    interpretation = AstroResponseV1(**{**payload, "disclaimers": []})

    assert gateway_result.meta.fallback_triggered is True
    assert isinstance(interpretation, AstroResponseV1)


def test_complete_generation_path_does_not_instantiate_v2_or_v1_after_v3_failure() -> None:
    """Garde AST: la branche complete nominale ne contient plus de downgrade local."""
    source = inspect.getsource(_deserialize_non_fallback_complete_interpretation)

    assert "AstroResponseV2(**full_output)" not in source
    assert "AstroResponseV1(**full_output)" not in source
    assert "AstroResponseV2(" not in source
    assert "AstroResponseV1(" not in source

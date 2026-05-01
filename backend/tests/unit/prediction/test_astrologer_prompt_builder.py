from pathlib import Path

from app.domain.llm.prompting.context import PromptCommonContext
from app.prediction.astrologer_prompt_builder import AstrologerPromptBuilder


def _make_common_context() -> PromptCommonContext:
    return PromptCommonContext(
        precision_level="précision complète",
        astrologer_profile={"tonality": "bienveillant"},
        period_covered="journée",
        today_date="samedi 21 mars 2026",
        use_case_name="daily-prediction-narrator-v1",
        use_case_key="daily_prediction",
        natal_interpretation="Vous avancez mieux quand un cap clair se dégage.",
    )


FORBIDDEN_DURABLE_INSTRUCTIONS = (
    "Format attendu",
    "Interdiction",
    "daily_synthesis : strictement",
)


def test_build_keeps_summary_variant_as_context_without_length_instruction() -> None:
    prompt = AstrologerPromptBuilder().build(
        common_context=_make_common_context(),
        time_windows=[],
        variant_code="summary_only",
    )

    assert "Variante de narration : summary_only" in prompt
    assert "strictement 7 à 8 phrases complètes" not in prompt
    assert "comprise entre 50% et 67% de la version complète" not in prompt
    assert "450 à 700 caractères" not in prompt


def test_build_keeps_full_variant_as_context_without_length_instruction() -> None:
    prompt = AstrologerPromptBuilder().build(
        common_context=_make_common_context(),
        time_windows=[],
    )

    assert "Variante de narration : standard" in prompt
    assert "strictement 10 à 12 phrases complètes" not in prompt


def test_builder_source_does_not_reintroduce_durable_narration_instructions() -> None:
    source = Path("app/prediction/astrologer_prompt_builder.py").read_text(encoding="utf-8")

    for forbidden in FORBIDDEN_DURABLE_INSTRUCTIONS:
        assert forbidden not in source

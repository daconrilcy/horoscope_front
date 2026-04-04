from app.prediction.astrologer_prompt_builder import AstrologerPromptBuilder
from app.prompts.common_context import PromptCommonContext


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


def test_build_uses_shorter_daily_synthesis_instruction_for_summary_only() -> None:
    prompt = AstrologerPromptBuilder().build(
        common_context=_make_common_context(),
        time_windows=[],
        variant_code="summary_only",
    )

    assert "strictement 6 à 8 phrases complètes" in prompt
    assert "comprise entre 50% et 67% de la version complète" in prompt
    assert "strictement 10 à 12 phrases complètes" not in prompt


def test_build_uses_full_daily_synthesis_instruction_by_default() -> None:
    prompt = AstrologerPromptBuilder().build(
        common_context=_make_common_context(),
        time_windows=[],
    )

    assert "strictement 10 à 12 phrases complètes" in prompt

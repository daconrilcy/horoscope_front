from app.prediction.astrologer_prompt_builder import AstrologerPromptBuilder
from app.prompts.common_context import PromptCommonContext


def test_prompt_builder_contains_style():
    builder = AstrologerPromptBuilder()
    ctx = PromptCommonContext(
        precision_level="précision complète",
        astrologer_profile={"tonality": "bienveillant"},
        period_covered="journée",
        today_date="2026-03-20",
        use_case_name="Test",
        use_case_key="test",
        natal_interpretation="Vous êtes un Lion fier.",
    )

    prompt = builder.build(ctx, [], [], "vedique", "fr")
    assert "nakshatra" in prompt
    assert "Lion fier" in prompt


def test_prompt_builder_formats_windows():
    builder = AstrologerPromptBuilder()
    ctx = PromptCommonContext(
        precision_level="H1",
        astrologer_profile={"tonality": "fun"},
        period_covered="day",
        today_date="today",
        use_case_name="U",
        use_case_key="K",
        natal_interpretation="X",
    )
    windows = [
        {
            "period_key": "matin",
            "time_range": "06:00-12:00",
            "regime": "progression",
            "top_domains": ["pro"],
        }
    ]

    prompt = builder.build(ctx, windows, [], "standard", "fr")
    assert "[matin]" in prompt
    assert "06:00-12:00" in prompt
    assert "progression" in prompt


def test_prompt_builder_empty_natal_data_shows_unavailable():
    builder = AstrologerPromptBuilder()
    ctx = PromptCommonContext(
        precision_level="précision complète",
        astrologer_profile={"tonality": "bienveillant"},
        period_covered="journée",
        today_date="2026-03-20",
        use_case_name="Test",
        use_case_key="test",
        natal_interpretation=None,
        natal_data={},  # present but empty → falsy → triggers "non disponible" branch
    )

    prompt = builder.build(ctx, [], [], "standard", "fr")
    assert "non disponible" in prompt

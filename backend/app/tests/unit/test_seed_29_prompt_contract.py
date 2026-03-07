from scripts.seed_29_prompts import PROMPTS_TO_SEED


def test_seed_29_natal_complete_requires_chart_json() -> None:
    config = next(c for c in PROMPTS_TO_SEED if c["use_case_key"] == "natal_interpretation")
    assert "chart_json" in config["required_prompt_placeholders"]


def test_seed_29_natal_short_requires_chart_json() -> None:
    config = next(c for c in PROMPTS_TO_SEED if c["use_case_key"] == "natal_interpretation_short")
    assert "chart_json" in config["required_prompt_placeholders"]

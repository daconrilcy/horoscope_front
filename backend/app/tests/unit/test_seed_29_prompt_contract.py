from scripts.seed_29_prompts import PROMPTS_TO_SEED


def test_seed_29_natal_complete_requires_llm_astrology_input_v1() -> None:
    config = next(c for c in PROMPTS_TO_SEED if c["use_case_key"] == "natal_interpretation")
    assert "llm_astrology_input_v1" in config["required_prompt_placeholders"]
    assert "chart_json" not in config["required_prompt_placeholders"]
    assert "{{chart_json}}" not in config["developer_prompt"]


def test_seed_29_natal_short_requires_llm_astrology_input_v1() -> None:
    config = next(c for c in PROMPTS_TO_SEED if c["use_case_key"] == "natal_interpretation_short")
    assert "llm_astrology_input_v1" in config["required_prompt_placeholders"]
    assert "chart_json" not in config["required_prompt_placeholders"]
    assert "{{chart_json}}" not in config["developer_prompt"]

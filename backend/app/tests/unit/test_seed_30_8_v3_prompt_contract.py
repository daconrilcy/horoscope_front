from __future__ import annotations

from app.ops.llm.prompt_lint import PromptLint
from scripts.seed_30_8_v3_prompts import (
    ALL_PROMPT_CONFIGS,
    GPT5_V3_CONFIG,
    LINT_REQUIRED_PLACEHOLDERS,
    NATAL_COMPLETE_PROMPT_V3,
)


def test_v3_prompt_enforces_anti_jargon_and_section_microstructure() -> None:
    prompt = NATAL_COMPLETE_PROMPT_V3
    assert "ANTI-JARGON" in prompt
    assert "intégré au flux de la phrase" in prompt
    assert "micro-structure" in prompt
    assert "si… alors…" in prompt


def test_v3_prompt_enforces_editorial_readability_rules() -> None:
    prompt = NATAL_COMPLETE_PROMPT_V3
    assert "FLUIDITÉ PÉDAGOGIQUE" in prompt
    assert "TANGIBLE" in prompt
    assert "NON-REDONDANCE" in prompt
    assert 'éviter la forme "Le terme X désigne..."' in prompt
    assert "bénéfice ET le risque" in prompt
    assert "durée, une fréquence" in prompt
    assert "déclencheur concret" in prompt
    assert "une seule fois dans tout le document" in prompt
    assert "comportement concret et une situation typique du réel" in prompt
    assert "effet concret + bénéfice + vigilance" in prompt
    assert "VARIÉTÉ INTER-SECTIONS" in prompt
    assert "même paire planète+aspect" in prompt


def test_v3_prompt_avoids_legacy_paragraph_length_constraints() -> None:
    prompt = NATAL_COMPLETE_PROMPT_V3.lower()
    assert "3-5 paragraphes" not in prompt
    assert "1-2 paragraphes" not in prompt


def test_v3_reasoning_effort_is_low() -> None:
    assert GPT5_V3_CONFIG["reasoning_effort"] == "low"


def test_v3_prompt_scopes_to_standard_complete_mode() -> None:
    prompt = NATAL_COMPLETE_PROMPT_V3
    assert 'mode "complete enrichi"' in prompt
    assert "socle standard ET des thématiques additionnelles" in prompt


def test_v3_prompt_embeds_thematic_section_catalog() -> None:
    prompt = NATAL_COMPLETE_PROMPT_V3
    assert "Au total, produire entre 9 et 10 sections" in prompt
    assert "self_image" in prompt
    assert "leadership_signature" in prompt
    assert "creative_engine" in prompt
    assert "values_core" in prompt


def test_v3_prompt_explicitly_embeds_chart_json() -> None:
    prompt = NATAL_COMPLETE_PROMPT_V3
    assert "{{chart_json}}" in prompt
    assert "données présentes dans l'entrée ({{chart_json}})" in prompt


def test_v3_prompt_blocks_compatibility_scope_creep() -> None:
    prompt = NATAL_COMPLETE_PROMPT_V3
    assert "N'introduis aucun critère de compatibilité amoureuse" in prompt
    assert "profil partenaire idéal" in prompt


def test_all_story_30_8_prompts_pass_lint_contract() -> None:
    for cfg in ALL_PROMPT_CONFIGS:
        lint_res = PromptLint.lint_prompt(
            cfg["developer_prompt"],
            use_case_required_placeholders=LINT_REQUIRED_PLACEHOLDERS,
        )
        assert lint_res.passed, f"Lint failed for {cfg['use_case_key']}: {lint_res.errors}"

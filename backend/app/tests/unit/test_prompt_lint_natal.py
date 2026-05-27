from app.ops.llm.prompt_lint import PromptLint


def test_lint_short_valid():
    """Le prompt SHORT avec la cle canonique, {{locale}}, {{use_case}} passe."""
    text = "Langue: {{locale}}. UC: {{use_case}}. Input: {{llm_astrology_input_v1}}"
    res = PromptLint.lint_prompt(text, use_case_required_placeholders=["llm_astrology_input_v1"])
    assert res.passed
    assert not res.errors


def test_lint_short_missing_llm_astrology_input_v1():
    """Le prompt SHORT sans {{llm_astrology_input_v1}} echoue avec erreur."""
    text = "Langue: {{locale}}. UC: {{use_case}}."
    res = PromptLint.lint_prompt(text, use_case_required_placeholders=["llm_astrology_input_v1"])
    assert not res.passed
    assert any("llm_astrology_input_v1" in e for e in res.errors)


def test_lint_complete_valid():
    """Le prompt COMPLETE avec tous les placeholders passe."""
    text = (
        "Langue: {{locale}}. UC: {{use_case}}. Persona: {{persona_name}}. "
        "Input: {{llm_astrology_input_v1}}"
    )
    res = PromptLint.lint_prompt(
        text, use_case_required_placeholders=["llm_astrology_input_v1", "persona_name"]
    )
    assert res.passed
    assert not res.errors


def test_lint_complete_missing_persona_name():
    """Le prompt COMPLETE sans {{persona_name}} échoue avec erreur."""
    text = "Langue: {{locale}}. UC: {{use_case}}. Input: {{llm_astrology_input_v1}}"
    res = PromptLint.lint_prompt(
        text, use_case_required_placeholders=["llm_astrology_input_v1", "persona_name"]
    )
    assert not res.passed
    assert any("persona_name" in e for e in res.errors)


def test_lint_missing_platform_placeholders():
    """Le lint échoue si {{locale}} ou {{use_case}} manque (inclus par défaut)."""
    text = "Input: {{llm_astrology_input_v1}}"
    res = PromptLint.lint_prompt(text, use_case_required_placeholders=["llm_astrology_input_v1"])
    assert not res.passed
    # Should find missing locale and use_case
    assert any("locale" in e for e in res.errors)
    assert any("use_case" in e for e in res.errors)
    # La cle canonique est presente, donc pas dans les erreurs.
    assert not any("llm_astrology_input_v1" in e for e in res.errors)


def test_lint_prompt_too_long():
    """Un prompt > 8000 chars échoue au lint."""
    text = "A" * 8001 + "{{locale}} {{use_case}} {{llm_astrology_input_v1}}"
    res = PromptLint.lint_prompt(text, use_case_required_placeholders=["llm_astrology_input_v1"])
    assert not res.passed
    assert any("too long" in e for e in res.errors)


def test_lint_prompt_warning_long():
    """Un prompt entre 4000 et 8000 chars passe avec warning."""
    text = "A" * 4001 + "{{locale}} {{use_case}} {{llm_astrology_input_v1}}"
    res = PromptLint.lint_prompt(text, use_case_required_placeholders=["llm_astrology_input_v1"])
    assert res.passed
    assert any("quite long" in w for w in res.warnings)


def test_lint_jinja2_syntax_error():
    """Un prompt avec une erreur de syntaxe Jinja2 échoue."""
    text = "Langue: {{ locale }. UC: {{ use_case }}."
    res = PromptLint.lint_prompt(text, use_case_required_placeholders=[])
    assert not res.passed
    assert any("Jinja2 Syntax Error" in e for e in res.errors)

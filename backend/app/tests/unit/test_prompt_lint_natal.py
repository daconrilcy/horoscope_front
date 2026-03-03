from app.llm_orchestration.services.prompt_lint import PromptLint


def test_lint_short_valid():
    """Le prompt SHORT avec {{chart_json}}, {{locale}}, {{use_case}} passe."""
    text = "Langue: {{locale}}. UC: {{use_case}}. Chart: {{chart_json}}"
    res = PromptLint.lint_prompt(text, use_case_required_placeholders=["chart_json"])
    assert res.passed
    assert not res.errors


def test_lint_short_missing_chart_json():
    """Le prompt SHORT sans {{chart_json}} échoue avec erreur."""
    text = "Langue: {{locale}}. UC: {{use_case}}."
    res = PromptLint.lint_prompt(text, use_case_required_placeholders=["chart_json"])
    assert not res.passed
    assert any("chart_json" in e for e in res.errors)


def test_lint_complete_valid():
    """Le prompt COMPLETE avec tous les placeholders passe."""
    text = "Langue: {{locale}}. UC: {{use_case}}. Persona: {{persona_name}}. Chart: {{chart_json}}"
    res = PromptLint.lint_prompt(
        text, use_case_required_placeholders=["chart_json", "persona_name"]
    )
    assert res.passed
    assert not res.errors


def test_lint_complete_missing_persona_name():
    """Le prompt COMPLETE sans {{persona_name}} échoue avec erreur."""
    text = "Langue: {{locale}}. UC: {{use_case}}. Chart: {{chart_json}}"
    res = PromptLint.lint_prompt(
        text, use_case_required_placeholders=["chart_json", "persona_name"]
    )
    assert not res.passed
    assert any("persona_name" in e for e in res.errors)


def test_lint_missing_platform_placeholders():
    """Le lint échoue si {{locale}} ou {{use_case}} manque (inclus par défaut)."""
    text = "Chart: {{chart_json}}"
    res = PromptLint.lint_prompt(text, use_case_required_placeholders=["chart_json"])
    assert not res.passed
    # Should find missing locale and use_case
    assert any("locale" in e for e in res.errors)
    assert any("use_case" in e for e in res.errors)
    # chart_json is present, so not in errors
    assert not any("chart_json" in e for e in res.errors)


def test_lint_prompt_too_long():
    """Un prompt > 8000 chars échoue au lint."""
    text = "A" * 8001 + "{{locale}} {{use_case}} {{chart_json}}"
    res = PromptLint.lint_prompt(text, use_case_required_placeholders=["chart_json"])
    assert not res.passed
    assert any("too long" in e for e in res.errors)


def test_lint_prompt_warning_long():
    """Un prompt entre 4000 et 8000 chars passe avec warning."""
    text = "A" * 4001 + "{{locale}} {{use_case}} {{chart_json}}"
    res = PromptLint.lint_prompt(text, use_case_required_placeholders=["chart_json"])
    assert res.passed
    assert any("quite long" in w for w in res.warnings)


def test_lint_jinja2_syntax_error():
    """Un prompt avec une erreur de syntaxe Jinja2 échoue."""
    text = "Langue: {{ locale }. UC: {{ use_case }}."
    res = PromptLint.lint_prompt(text, use_case_required_placeholders=[])
    assert not res.passed
    assert any("Jinja2 Syntax Error" in e for e in res.errors)

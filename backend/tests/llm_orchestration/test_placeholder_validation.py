# Tests de validation des placeholders gouvernes du runtime LLM.
"""Verifie les comportements requis, optionnels et fallback du renderer."""

import pytest

from app.domain.llm.prompting.prompt_renderer import PromptRenderer
from app.domain.llm.runtime.contracts import PromptRenderError


def test_placeholder_required_missing_blocking(caplog):
    """Une cle requise manquante dans une feature bloquante leve une erreur."""
    template = "Hello {{llm_astrology_input_v1}}"
    vars = {"locale": "fr-FR"}

    with pytest.raises(PromptRenderError) as exc:
        PromptRenderer.render(template, vars, feature="natal")

    assert "Required placeholder '{{llm_astrology_input_v1}}' not resolved" in str(exc.value)


def test_placeholder_required_missing_non_blocking(caplog):
    """Test Story 66.13: Required missing in non-blocking feature logs error but continues."""
    template = "Hello {{last_user_msg}}"
    vars = {"locale": "fr-FR"}

    # We use 'chat' as non-blocking (blocking list is ["natal", "guidance_contextual"])
    rendered = PromptRenderer.render(template, vars, feature="chat")

    assert rendered == "Hello "
    assert "placeholder_not_resolved" in caplog.text
    assert "classification=required" in caplog.text


def test_placeholder_optional_missing(caplog):
    """Test Story 66.13: Optional missing is replaced by empty and logs warning."""
    template = "Hello {{persona_name}}"
    vars = {"locale": "fr-FR"}

    rendered = PromptRenderer.render(template, vars, feature="chat")

    assert rendered == "Hello "
    assert "placeholder_not_resolved" in caplog.text
    assert "classification=optional" in caplog.text


def test_placeholder_optional_fallback(caplog):
    """Test Story 66.13: Optional with fallback used."""
    template = "Language: {{locale}}"
    vars = {}  # Missing locale

    import logging

    with caplog.at_level(logging.INFO):
        rendered = PromptRenderer.render(template, vars, feature="chat")

    assert rendered == "Language: fr-FR"
    assert "placeholder_fallback_used" in caplog.text


def test_placeholder_unknown(caplog):
    """Test Story 66.13: Unknown placeholder is removed and logs error."""
    template = "Hello {{unknown_var}}"
    vars = {}

    rendered = PromptRenderer.render(template, vars, feature="chat")

    assert rendered == "Hello "
    assert "placeholder_unauthorized_detected" in caplog.text


def test_no_surviving_placeholders():
    """Test Story 66.13: No {{...}} should survive."""
    template = "Hello {{missing}} {{other}}"
    vars = {}

    rendered = PromptRenderer.render(template, vars, feature="chat")

    assert "{{" not in rendered
    assert "}}" not in rendered

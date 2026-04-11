from app.llm_orchestration.services.context_quality_injector import ContextQualityInjector


def test_injector_handled_by_template_partial():
    """AC2: Detects when partial quality is handled by template."""
    prompt = "Base. {{#context_quality:partial}}Handling...{{/context_quality}}"
    augmented, injected, handled = ContextQualityInjector.inject(prompt, "natal", "partial")

    assert augmented == prompt
    assert injected is False
    assert handled is True


def test_injector_handled_by_template_minimal():
    """AC2: Detects when minimal quality is handled by template."""
    prompt = "Base. {{#context_quality:minimal}}Handling...{{/context_quality}}"
    augmented, injected, handled = ContextQualityInjector.inject(prompt, "natal", "minimal")

    assert augmented == prompt
    assert injected is False
    assert handled is True


def test_injector_not_handled_triggers_injection():
    """AC2: Triggers injection when not handled by template."""
    prompt = "Base prompt without quality blocks."
    augmented, injected, handled = ContextQualityInjector.inject(prompt, "natal", "partial")

    assert "Base prompt without quality blocks." in augmented
    assert "[CONTEXTE NATAL PARTIEL]" in augmented
    assert injected is True
    assert handled is False


def test_injector_full_quality_no_action():
    """AC2: No action when quality is full."""
    prompt = "Base prompt."
    augmented, injected, handled = ContextQualityInjector.inject(prompt, "natal", "full")

    assert augmented == prompt
    assert injected is False
    assert handled is False


def test_injector_unknown_quality_no_action():
    """AC2: No action when quality is unknown."""
    prompt = "Base prompt."
    # The injector logic treats unknown like any other level that doesn't have an instruction
    # and isn't 'full'.
    augmented, injected, handled = ContextQualityInjector.inject(prompt, "natal", "unknown")

    assert augmented == prompt
    assert injected is False
    assert handled is False

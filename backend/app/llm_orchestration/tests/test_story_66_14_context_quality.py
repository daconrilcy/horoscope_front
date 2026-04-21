import pytest

from app.domain.llm.prompting.prompt_renderer import PromptRenderer
from app.llm_orchestration.services.context_quality_injector import ContextQualityInjector


def test_context_quality_conditional_blocks():
    """Test Story 66.14: Conditional blocks resolution based on context_quality."""
    template = (
        "Base. {{#context_quality:minimal}}MINIMAL CONTENT{{/context_quality}}"
        "{{#context_quality:full}}FULL CONTENT{{/context_quality}}"
    )

    # 1. Test minimal
    rendered = PromptRenderer.render(template, {"context_quality": "minimal"})
    assert "Base. MINIMAL CONTENT" in rendered
    assert "FULL CONTENT" not in rendered

    # 2. Test full
    rendered = PromptRenderer.render(template, {"context_quality": "full"})
    assert "Base. FULL CONTENT" in rendered
    assert "MINIMAL CONTENT" not in rendered


def test_context_quality_injector_generic():
    """Test Story 66.14: Generic compensation instructions."""
    prompt = "Base prompt"

    # 1. Minimal quality
    augmented, injected, handled = ContextQualityInjector.inject(prompt, "any_feat", "minimal")
    assert injected is True
    assert "[CONTEXTE LIMITÉ]" in augmented

    # 2. Full quality
    augmented, injected, handled = ContextQualityInjector.inject(prompt, "any_feat", "full")
    assert injected is False
    assert augmented == prompt


def test_context_quality_injector_specific():
    """Test Story 66.14: Feature-specific compensation instructions."""
    prompt = "Base prompt"

    # Natal specific
    augmented, injected, handled = ContextQualityInjector.inject(prompt, "natal", "minimal")
    assert injected is True
    assert "[CONTEXTE NATAL LIMITÉ]" in augmented


def test_context_quality_injector_no_duplicate():
    """Test Story 66.14: No automatic injection if template already handles it."""
    prompt = "Base. {{#context_quality:minimal}}Manual warning{{/context_quality}}"

    augmented, injected, handled = ContextQualityInjector.inject(prompt, "natal", "minimal")
    assert injected is False
    assert augmented == prompt


@pytest.mark.asyncio
async def test_gateway_context_quality_propagation(db):
    """Test Story 66.14: Context quality propagation in gateway."""
    from app.llm_orchestration.gateway import LLMGateway
    from app.llm_orchestration.models import (
        ExecutionContext,
        ExecutionUserInput,
        LLMExecutionRequest,
    )

    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="natal_long_free", feature="natal_test"),
        context=ExecutionContext(chart_json='{"planets": []}'),
        request_id="req-cq",
        trace_id="tr-cq",
    )

    # We don't mock CommonContextBuilder here, we just check how Stage 1 handles it
    # Default is 'unknown' if no qualified context
    plan, _ = await gateway._resolve_plan(request, db)

    assert hasattr(plan, "context_quality")
    assert hasattr(plan, "context_quality_instruction_injected")

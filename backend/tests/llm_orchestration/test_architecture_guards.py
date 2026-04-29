import pytest

from app.domain.llm.prompting.validators import (
    validate_plan_rules_content,
    validate_template_content,
)
from app.domain.llm.runtime.contracts import ResolvedExecutionPlan


def test_template_content_guard_violation():
    """Test Story 66.17: Template content guard detects execution concerns."""
    template = "Analyse ce thème. Use model gpt-4o for best results."
    violations = validate_template_content(template)
    assert any(v.violation_type == "template_content_violation:model_reference" for v in violations)
    assert "gpt-4o" in violations[0].excerpt


def test_plan_rules_guard_violation():
    """Test Story 66.17: Plan rules guard detects feature selection concerns."""
    plan_rules = "Si premium, utilise la feature natal_deep."
    violations = validate_plan_rules_content(plan_rules)
    assert any(v.violation_type == "plan_rules_violation:feature_selection" for v in violations)
    assert "Si premium" in violations[0].excerpt


def test_resolved_execution_plan_immutability():
    """Test Story 66.17: ResolvedExecutionPlan is immutable (frozen)."""

    plan = ResolvedExecutionPlan(
        model_id="m",
        model_source="config",
        rendered_developer_prompt="p",
        system_core="s",
        interaction_mode="chat",
        user_question_policy="none",
        temperature=0.7,
        max_output_tokens=100,
        request_id="r",
        trace_id="t",
    )

    with pytest.raises(Exception):  # Pydantic raises ValidationError or TypeError when frozen
        plan.model_id = "new-model"

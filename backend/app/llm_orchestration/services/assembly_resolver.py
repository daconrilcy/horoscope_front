from __future__ import annotations

import logging
from typing import Optional

from pydantic import BaseModel

from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.llm_orchestration.admin_models import (
    ExecutionConfigAdmin,
    PlaceholderInfo,
    PromptAssemblyPreview,
    PromptAssemblyTarget,
    ResolvedAssembly,
)
from app.llm_orchestration.policies.hard_policy import get_hard_policy
from app.llm_orchestration.prompt_governance_registry import (
    PLACEHOLDER_ALLOWLIST,
    get_prompt_governance_registry,
)
from app.llm_orchestration.services.persona_composer import compose_persona_block
from app.llm_orchestration.services.prompt_renderer import PromptRenderer

logger = logging.getLogger(__name__)


class PlanRule(BaseModel):
    instruction: Optional[str] = None
    max_output_tokens_override: Optional[int] = None


# AC6: Placeholder allowlist — registre central versionné (Story 66.42), réexport ci-dessous.

# AC11: Plan Rules Registry
PLAN_RULES_REGISTRY: dict[str, PlanRule] = {
    "premium_depth": PlanRule(
        instruction="Pour ce compte premium, inclure une analyse approfondie "
        "des maisons angulaires.",
        max_output_tokens_override=None,
    ),
    "free_limit": PlanRule(
        instruction="Contrainte : sois très concis, maximum 2 paragraphes.",
        max_output_tokens_override=800,
    ),
    "plan_free_concise": PlanRule(
        instruction=(
            "CONSIGNE ABONNEMENT FREE : Sois très concis et direct. "
            "Limite-toi à l'essentiel (environ 5 à 7 phrases pour la synthèse)."
        ),
        max_output_tokens_override=1000,
    ),
    "plan_premium_full": PlanRule(
        instruction=(
            "CONSIGNE ABONNEMENT PREMIUM : Fournis une analyse riche, "
            "détaillée et nuancée (au moins 10 à 12 phrases pour la synthèse)."
        ),
        max_output_tokens_override=None,
    ),
}


def validate_placeholders(template: str, feature: str) -> list[str]:
    """
    Extracts placeholders from template and validates them against the central registry.
    Returns a list of unknown/forbidden placeholders.
    """
    reg = get_prompt_governance_registry()
    invalid, _violations = reg.validate_placeholders_in_template(
        template, feature, source="validate_placeholders"
    )
    return invalid


def build_assembly_preview(
    config: PromptAssemblyConfigModel, simulated_context_quality: str = "full"
) -> PromptAssemblyPreview:
    """
    Builds a full preview of an assembly rendering (AC7, AC12).
    Now supports simulated context quality (Story 66.14 AC6).
    """
    resolved = resolve_assembly(config, context_quality=simulated_context_quality)
    rendered_prompt = assemble_developer_prompt(resolved, config)

    # AC4: Hard policy is visible but separate
    # M2 Fix: Default safety_profile to astrology
    safety_profile = "astrology"
    hard_policy = get_hard_policy(safety_profile)

    # AC7: Available variables extraction
    found_placeholders = PromptRenderer.extract_placeholders(rendered_prompt)

    variables = []
    resolution_statuses = []

    # Mock some context for preview resolution
    mock_vars = {
        "locale": "fr-FR",
        "context_quality": simulated_context_quality,
        "use_case": config.feature_template.use_case_key,
    }

    # Feature-specific mock context
    if config.feature == "chat":
        mock_vars["last_user_msg"] = "Hello Luna!"
    if config.feature == "natal":
        mock_vars["chart_json"] = '{"planets": {}}'
        mock_vars["natal_data"] = '{"birth_date": "1990-01-01"}'

    reg = get_prompt_governance_registry()
    feat_key = reg.resolve_placeholder_family(config.feature)
    allowlist = PLACEHOLDER_ALLOWLIST.get(feat_key, [])
    placeholder_defs = {d.name: d for d in allowlist}

    for p in found_placeholders:
        # 1. Available variables info
        variables.append(
            PlaceholderInfo(name=p, type="string", origin="context", example=f"example_{p}")
        )

        # 2. Resolution status (Story 66.13 AC5)
        p_def = placeholder_defs.get(p)
        status = "unknown"
        val_preview = None

        if p in mock_vars:
            status = "resolved"
            val_preview = str(mock_vars[p])[:10]
        elif p_def:
            if p_def.classification == "required":
                status = "missing_required"
            elif p_def.classification == "optional":
                status = "missing_optional"
            elif p_def.classification == "optional_with_fallback":
                status = "fallback_used"
                val_preview = (p_def.fallback or "")[:10]

        from app.llm_orchestration.admin_models import PlaceholderResolutionStatus

        resolution_statuses.append(
            PlaceholderResolutionStatus(name=p, status=status, value_preview=val_preview)
        )

    from app.infra.db.models.llm_prompt import PromptStatus

    return PromptAssemblyPreview(
        target=resolved.target,
        feature_block=resolved.feature_template_prompt,
        subfeature_block=resolved.subfeature_template_prompt,
        persona_block=resolved.persona_block,
        plan_rules_block=resolved.plan_rules_content,
        template_source=resolved.template_source,
        rendered_developer_prompt=rendered_prompt,
        hard_policy_block=hard_policy,
        output_contract_ref=resolved.output_contract_ref,
        available_variables=variables,
        placeholder_resolution_status=resolution_statuses,
        resolved_execution_config=resolved.execution_config,
        length_budget=resolved.length_budget,
        draft_preview=(config.status != PromptStatus.PUBLISHED),
    )


def resolve_assembly(
    config: PromptAssemblyConfigModel, context_quality: str = "full"
) -> ResolvedAssembly:
    """
    Orchestrates the resolution of an assembly config into a ResolvedAssembly artifact.
    Implements AC1, AC2, AC11.
    """
    target = PromptAssemblyTarget(
        feature=config.feature,
        subfeature=config.subfeature,
        plan=config.plan,
        locale=config.locale,
    )

    # 1. Resolve template source and prompts (AC2)
    template_source = "explicit_subfeature"
    feature_prompt = config.feature_template.developer_prompt
    subfeature_prompt = None
    subfeature_id = None

    if config.subfeature_template_ref:
        subfeature_prompt = config.subfeature_template.developer_prompt
        subfeature_id = config.subfeature_template_ref
    else:
        template_source = "fallback_default"

    # 2. Resolve Persona (AC1)
    persona_block = None
    if config.persona_enabled and config.persona:
        try:
            persona_block = compose_persona_block(config.persona)
        except Exception as e:
            logger.error("assembly_resolver_persona_failed id=%s error=%s", config.persona_ref, e)

    # 3. Resolve Plan Rules (AC11)
    plan_rules_content = None
    exec_dict = config.execution_config

    if config.plan_rules_enabled and config.plan_rules_ref:
        rule = PLAN_RULES_REGISTRY.get(config.plan_rules_ref)
        if rule:
            plan_rules_content = rule.instruction

            # Story 66.17 AC4: Plan rules guard
            from app.prompts.validators import validate_plan_rules_content

            arch_violations = validate_plan_rules_content(plan_rules_content)
            for v in arch_violations:
                logger.warning(
                    "plan_rules_violation: %s detected in plan rules. Excerpt: %s",
                    v.violation_type,
                    v.excerpt,
                )

            if rule.max_output_tokens_override is not None:
                # AC11: Constraint max_output_tokens downwards
                current_max = exec_dict.get("max_output_tokens", 2048)
                exec_dict["max_output_tokens"] = min(current_max, rule.max_output_tokens_override)

    # 4. Execution Config (AC5)
    execution_config = ExecutionConfigAdmin(**exec_dict)

    # 5. Policy Layer (Architectural Note 1)
    # M2 Fix: Default safety_profile to astrology
    safety_profile = "astrology"
    policy_layer_content = get_hard_policy(safety_profile)

    # 6. Length Budget (Story 66.12)
    length_budget = None
    if config.length_budget:
        from app.llm_orchestration.admin_models import LengthBudget

        length_budget = LengthBudget(**config.length_budget)

    return ResolvedAssembly(
        target=target,
        feature_template_id=config.feature_template_ref,
        feature_template_prompt=feature_prompt,
        subfeature_template_id=subfeature_id,
        subfeature_template_prompt=subfeature_prompt,
        template_source=template_source,
        persona_ref=config.persona_ref,
        persona_block=persona_block,
        plan_rules_content=plan_rules_content,
        execution_config=execution_config,
        output_contract_ref=config.output_contract_ref,
        input_schema=config.input_schema,
        length_budget=length_budget,
        context_quality=context_quality,
        policy_layer_content=policy_layer_content,
    )


def assemble_developer_prompt(resolved: ResolvedAssembly, config: PromptAssemblyConfigModel) -> str:
    """
    Concatenates the resolved blocks into the final developer prompt.
    Implements the composition logic: feature + subfeature + plan_rules.
    Persona is handled separately in LLMGateway layers.
    """
    blocks = []

    if config.feature_enabled:
        blocks.append(resolved.feature_template_prompt)

    if config.subfeature_enabled and resolved.subfeature_template_prompt:
        blocks.append(resolved.subfeature_template_prompt)

    if config.plan_rules_enabled and resolved.plan_rules_content:
        blocks.append(resolved.plan_rules_content)

    prompt = "\n\n".join(blocks)

    # Story 66.12: Length Budget injection
    if resolved.length_budget:
        from app.llm_orchestration.services.length_budget_injector import LengthBudgetInjector

        prompt = LengthBudgetInjector.inject_into_developer_prompt(prompt, resolved.length_budget)

    # Story 66.14: Context Quality injection (compensation instructions)
    # We use 'full' as default if not provided yet (resolved in gateway)
    context_quality = "full"
    injected = False
    if hasattr(
        resolved, "context_quality"
    ):  # Should be there if coming from build_assembly_preview
        context_quality = resolved.context_quality
        from app.llm_orchestration.services.context_quality_injector import ContextQualityInjector

        prompt, injected, handled = ContextQualityInjector.inject(
            prompt, config.feature, context_quality
        )

    # Store injection status in resolved object if possible (it's a Pydantic model)
    # Actually, ResolvedAssembly doesn't have this field yet.

    return prompt

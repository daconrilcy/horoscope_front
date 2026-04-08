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
from app.llm_orchestration.services.persona_composer import compose_persona_block
from app.llm_orchestration.services.prompt_renderer import PromptRenderer

logger = logging.getLogger(__name__)

class PlanRule(BaseModel):
    instruction: Optional[str] = None
    max_output_tokens_override: Optional[int] = None

# AC6: Placeholder allowlist indexed by feature
PLACEHOLDER_ALLOWLIST: dict[str, list[str]] = {
    "guidance": ["locale", "use_case", "situation", "last_user_msg"],
    "natal": ["locale", "use_case", "chart_json", "natal_data", "birth_date", "birth_time", "birth_timezone"],
    "chat": ["locale", "use_case", "last_user_msg", "persona_name"],
}

# AC11: Plan Rules Registry
PLAN_RULES_REGISTRY: dict[str, PlanRule] = {
    "premium_depth": PlanRule(
        instruction="Pour ce compte premium, inclure une analyse approfondie des maisons angulaires.",
        max_output_tokens_override=None,
    ),
    "free_limit": PlanRule(
        instruction="Contrainte : sois très concis, maximum 2 paragraphes.",
        max_output_tokens_override=800,
    ),
}


def validate_placeholders(template: str, feature: str) -> list[str]:
    """
    Extracts placeholders from template and validates them against the feature allowlist.
    Returns a list of unknown/forbidden placeholders.
    """
    found = PromptRenderer.extract_placeholders(template)
    # Normalize feature key for lookup
    feat_key = feature.split("_")[0] if "_" in feature else feature
    allowed = PLACEHOLDER_ALLOWLIST.get(feat_key, [])
    
    # Allow some universal placeholders if not explicitly in list
    universal = {"locale", "use_case", "persona_name", "last_user_msg"}
    
    invalid = [p for p in found if p not in allowed and p not in universal]
    return invalid


def build_assembly_preview(config: PromptAssemblyConfigModel) -> PromptAssemblyPreview:
    """
    Builds a full preview of an assembly rendering (AC7, AC12).
    """
    resolved = resolve_assembly(config)
    rendered_prompt = assemble_developer_prompt(resolved, config)
    
    # AC4: Hard policy is visible but separate
    # M2 Fix: Derive safety_profile from feature template
    from app.prompts.catalog import PROMPT_CATALOG
    use_case_key = config.feature_template.use_case_key
    catalog_entry = PROMPT_CATALOG.get(use_case_key)
    safety_profile = "astrology"
    if catalog_entry and catalog_entry.safety_profile:
        safety_profile = catalog_entry.safety_profile
    
    hard_policy = get_hard_policy(safety_profile)

    # AC7: Available variables extraction
    found_placeholders = PromptRenderer.extract_placeholders(rendered_prompt)
    
    variables = []
    for p in found_placeholders:
        # Placeholder enrichment could be more complex, but here we provide basic info
        variables.append(PlaceholderInfo(
            name=p,
            type="string",
            origin="context",
            example=f"example_{p}"
        ))

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
        resolved_execution_config=resolved.execution_config,
        draft_preview=(config.status != PromptStatus.PUBLISHED)
    )


def resolve_assembly(config: PromptAssemblyConfigModel) -> ResolvedAssembly:
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
            if rule.max_output_tokens_override is not None:
                # AC11: Constraint max_output_tokens downwards
                current_max = exec_dict.get("max_output_tokens", 2048)
                exec_dict["max_output_tokens"] = min(current_max, rule.max_output_tokens_override)

    # 4. Execution Config (AC5)
    execution_config = ExecutionConfigAdmin(**exec_dict)

    # 5. Policy Layer (Architectural Note 1)
    # M2 Fix: Derive safety_profile from feature template use_case_key
    from app.prompts.catalog import PROMPT_CATALOG
    use_case_key = config.feature_template.use_case_key
    catalog_entry = PROMPT_CATALOG.get(use_case_key)
    safety_profile = "astrology"
    if catalog_entry and catalog_entry.safety_profile:
        safety_profile = catalog_entry.safety_profile
    
    policy_layer_content = get_hard_policy(safety_profile)

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
        
    return "\n\n".join(blocks)

import logging
import re
from typing import Any, Dict, List, Optional

from app.llm_orchestration.models import PromptRenderError

logger = logging.getLogger(__name__)


class PromptRenderer:
    """Renders prompt templates using {{snake_case}} variables."""

    @staticmethod
    def render(
        template: str, 
        variables: Dict[str, Any], 
        required_variables: List[str] = None, # Legacy support
        feature: str = "unknown"
    ) -> str:
        """
        Render a template with variables and enforcement policy (Story 66.13, 66.14).
        """
        # 0. Story 66.14: Resolve context_quality conditional blocks BEFORE anything else
        context_quality = variables.get("context_quality", "full")
        
        # Pattern: {{#context_quality:VALUE}}...{{/context_quality}}
        def resolve_quality_block(match):
            target_quality = match.group(1)
            content = match.group(2)
            if target_quality == context_quality:
                return content
            return ""

        template = re.sub(
            r"\{\{#context_quality:([a-z]+)\}\}(.*?)\{\{/context_quality\}\}", 
            resolve_quality_block, 
            template, 
            flags=re.DOTALL
        )

        from app.llm_orchestration.placeholder_policy import PLACEHOLDER_POLICY
        from app.llm_orchestration.services.assembly_resolver import PLACEHOLDER_ALLOWLIST

        # 1. Check legacy required_variables first
        required_variables = required_variables or []
        # We only check for variables that match the strict {{snake_case}} pattern
        missing_legacy = [v for v in required_variables if f"{{{{{v}}}}}" in template and v not in variables]
        if missing_legacy:
            raise PromptRenderError(
                f"Missing required legacy variables: {', '.join(missing_legacy)}",
                details={"missing_variables": missing_legacy},
            )

        # 2. Advanced resolution based on classification (D2)
        feat_key = feature.split("_")[0] if "_" in feature else feature
        allowlist = PLACEHOLDER_ALLOWLIST.get(feat_key, [])
        placeholder_defs = {d.name: d for d in allowlist}
        
        found_placeholders = PromptRenderer.extract_placeholders(template)
        effective_vars = variables.copy()
        
        # Universal placeholders (Story 66.13 AC6)
        universal = {"locale", "use_case", "persona_name", "last_user_msg"}
        
        for p_name in found_placeholders:
            if p_name in variables:
                continue
                
            p_def = placeholder_defs.get(p_name)
            
            if not p_def and p_name not in universal:
                # Unknown placeholder (AC4)
                logger.error(
                    "placeholder_unknown_detected placeholder=%s feature=%s",
                    p_name, feature
                )
                effective_vars[p_name] = ""
                continue
                
            # If it's universal but not provided, treat as optional empty for safety
            if p_name in universal and not p_def:
                effective_vars[p_name] = ""
                continue

            if p_def.classification == "required":
                msg = f"Required placeholder '{{{{{p_name}}}}}' not resolved for feature '{feature}'"
                if feature in PLACEHOLDER_POLICY.blocking_features or feat_key in PLACEHOLDER_POLICY.blocking_features:
                    raise PromptRenderError(msg, details={"placeholder": p_name, "feature": feature})
                else:
                    logger.error(
                        "placeholder_not_resolved placeholder=%s feature=%s classification=required", 
                        p_name, feature
                    )
                    effective_vars[p_name] = ""
            
            elif p_def.classification == "optional":
                logger.warning(
                    "placeholder_not_resolved placeholder=%s feature=%s classification=optional", 
                    p_name, feature
                )
                effective_vars[p_name] = ""
                
            elif p_def.classification == "optional_with_fallback":
                fallback_val = p_def.fallback or ""
                logger.info("placeholder_fallback_used placeholder=%s fallback=%s", p_name, fallback_val)
                effective_vars[p_name] = fallback_val

        # 3. Perform final substitution
        def replace(match):
            key = match.group(1)
            if key in effective_vars:
                return str(effective_vars[key])
            # Preserve the placeholder if not found in effective_vars
            return f"{{{{{key}}}}}"

        # Match ONLY strict {{variable_name}}
        rendered = re.sub(r"\{\{([a-zA-Z0-9_]+)\}\}", replace, template)

        return rendered

    @staticmethod
    def extract_placeholders(template: str) -> List[str]:
        if not template:
            return []
        # Match ONLY strict {{variable_name}}
        matches = re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}", template)
        return list(dict.fromkeys(matches))

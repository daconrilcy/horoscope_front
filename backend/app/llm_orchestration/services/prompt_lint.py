from __future__ import annotations

from dataclasses import dataclass, field

from app.ai_engine.config import ai_engine_settings


@dataclass
class LintResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class PromptLint:
    @staticmethod
    def lint_prompt(
        text: str, use_case_required_placeholders: list[str] | None = None
    ) -> LintResult:
        errors = []
        warnings = []

        # 1. Size rules
        if len(text) > 8000:
            errors.append("Prompt is too long (max 8,000 characters).")
        elif len(text) > 4000:
            warnings.append("Prompt is quite long (> 4,000 characters).")

        # 2. Mandatory placeholders (Global)
        if "{{locale}}" not in text:
            errors.append("Mandatory placeholder '{{locale}}' is missing.")
        if "{{use_case}}" not in text:
            errors.append("Mandatory placeholder '{{use_case}}' is missing.")

        # 3. Mandatory placeholders (Use-case specific)
        if use_case_required_placeholders:
            for placeholder in use_case_required_placeholders:
                # Add braces for check if missing
                full_p = (
                    f"{{{{{placeholder}}}}}"
                    if not (placeholder.startswith("{{") and placeholder.endswith("}}"))
                    else placeholder
                )
                if full_p not in text:
                    errors.append(f"Use-case specific placeholder '{full_p}' is missing.")

        # 4. Forbidden words (configurable via AI_ENGINE_LLM_PROMPT_FORBIDDEN_WORDS)
        forbidden_words = ai_engine_settings.llm_prompt_forbidden_words
        for word in forbidden_words:
            if word.lower() in text.lower():
                errors.append(f"Forbidden word sequence found: '{word}'.")

        return LintResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

import logging
from dataclasses import dataclass, field

from jinja2 import Environment, TemplateSyntaxError

from app.core.llm_settings import ai_engine_settings

logger = logging.getLogger(__name__)


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
        """
        Validates a prompt for syntax, length, and mandatory placeholders.
        """
        errors = []
        warnings = []

        # 1. Jinja2 Syntax Validation
        env = Environment()
        try:
            env.parse(text)
        except TemplateSyntaxError as e:
            errors.append(f"Jinja2 Syntax Error at line {e.lineno}: {e.message}")

        # 2. Size rules
        if len(text) > 8000:
            errors.append("Prompt is too long (max 8,000 characters).")
        elif len(text) > 4000:
            warnings.append("Prompt is quite long (> 4,000 characters).")

        # 3a. Platform-mandatory placeholders
        platform_required = {"locale", "use_case"}
        for p in sorted(list(platform_required)):
            clean_p = p.replace("{", "").replace("}", "")
            full_p = f"{{{{{clean_p}}}}}"
            if full_p not in text:
                errors.append(f"Mandatory placeholder '{full_p}' is missing.")

        # 3b. Use-case-specific placeholders (separate error message)
        if use_case_required_placeholders:
            for p in sorted(list(use_case_required_placeholders)):
                clean_p = p.replace("{", "").replace("}", "")
                full_p = f"{{{{{clean_p}}}}}"
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

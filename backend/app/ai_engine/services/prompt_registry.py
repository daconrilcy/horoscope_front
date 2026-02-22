"""Prompt Registry for managing and rendering prompt templates."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.ai_engine.exceptions import UnknownUseCaseError, ValidationError

if TYPE_CHECKING:
    from app.ai_engine.schemas import GenerateContext, GenerateInput

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


@dataclass
class PromptConfig:
    """Configuration for a prompt template."""

    template_name: str
    model: str = "AUTO"
    max_tokens: int = 1500
    temperature: float = 0.7


USE_CASE_REGISTRY: dict[str, PromptConfig] = {
    "chat": PromptConfig(
        template_name="chat_system.jinja2",
        max_tokens=1000,
        temperature=0.8,
    ),
    "natal_chart_interpretation": PromptConfig(
        template_name="natal_chart_interpretation_v1.jinja2",
        max_tokens=2000,
        temperature=0.7,
    ),
    "card_reading": PromptConfig(
        template_name="card_reading_v1.jinja2",
        max_tokens=1500,
        temperature=0.75,
    ),
}


class PromptRegistry:
    """Registry for managing and rendering prompt templates."""

    _env: Environment | None = None

    @classmethod
    def _get_env(cls) -> Environment:
        """Get or create Jinja2 environment."""
        if cls._env is None:
            cls._env = Environment(
                loader=FileSystemLoader(str(PROMPTS_DIR)),
                autoescape=False,
            )
        return cls._env

    @classmethod
    def get_config(cls, use_case: str) -> PromptConfig:
        """
        Get prompt configuration for a use case.

        Args:
            use_case: The use case identifier

        Returns:
            PromptConfig for the use case

        Raises:
            UnknownUseCaseError: If use case is not registered
        """
        config = USE_CASE_REGISTRY.get(use_case)
        if config is None:
            raise UnknownUseCaseError(use_case)
        return config

    @classmethod
    def list_use_cases(cls) -> list[str]:
        """List all registered use cases."""
        return list(USE_CASE_REGISTRY.keys())

    @classmethod
    def render_prompt(
        cls,
        use_case: str,
        locale: str,
        input_data: "GenerateInput",
        context: "GenerateContext",
    ) -> str:
        """
        Render a prompt template for a given use case.

        Args:
            use_case: The use case identifier
            locale: Locale for the response
            input_data: Input data for template rendering
            context: Context data for template rendering

        Returns:
            Rendered prompt string

        Raises:
            UnknownUseCaseError: If use case is not registered
            ValidationError: If template rendering fails
        """
        config = cls.get_config(use_case)
        env = cls._get_env()

        try:
            template = env.get_template(config.template_name)
        except TemplateNotFound as err:
            logger.error(
                "prompt_template_not_found use_case=%s template=%s", use_case, config.template_name
            )
            raise ValidationError(
                f"prompt template not found for use_case: {use_case}",
                details={"use_case": use_case, "template": config.template_name},
            ) from err

        locale_lang = cls._extract_language(locale)
        template_vars = {
            "locale": locale_lang,
            "input": input_data.model_dump() if hasattr(input_data, "model_dump") else input_data,
            "context": context.model_dump() if hasattr(context, "model_dump") else context,
        }

        try:
            rendered = template.render(**template_vars)
        except Exception as err:
            logger.error(
                "prompt_render_failed use_case=%s error=%s",
                use_case,
                str(err),
            )
            raise ValidationError(
                f"failed to render prompt for use_case: {use_case}",
                details={"use_case": use_case, "error": str(err)},
            ) from err

        logger.debug(
            "prompt_rendered use_case=%s locale=%s length=%d",
            use_case,
            locale_lang,
            len(rendered),
        )
        return rendered

    @staticmethod
    def _extract_language(locale: str) -> str:
        """Extract language name from locale code."""
        locale_map = {
            "fr": "français",
            "en": "English",
            "es": "español",
            "de": "Deutsch",
            "it": "italiano",
            "pt": "português",
        }
        lang_code = locale.split("-")[0].lower() if "-" in locale else locale.lower()
        return locale_map.get(lang_code, locale)

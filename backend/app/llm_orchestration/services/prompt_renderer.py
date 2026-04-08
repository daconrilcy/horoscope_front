import re
from typing import Any, Dict, List

from app.llm_orchestration.models import PromptRenderError


class PromptRenderer:
    """Renders prompt templates using {{snake_case}} variables."""

    @staticmethod
    def render(
        template: str, variables: Dict[str, Any], required_variables: List[str] = None
    ) -> str:
        """
        Render a template with variables.

        Args:
            template: The string template with {{variable_name}} placeholders.
            variables: A dictionary of variables for interpolation.
            required_variables: A list of variable names that MUST be present.

        Returns:
            The rendered string.

        Raises:
            PromptRenderError: If a required variable is missing from the variables dictionary.
        """
        required_variables = required_variables or []

        # Check for missing required variables
        missing = [v for v in required_variables if v not in variables]
        if missing:
            raise PromptRenderError(
                f"Missing required variables for prompt rendering: {', '.join(missing)}",
                details={"missing_variables": missing},
            )

        # Basic rendering using regex for {{snake_case}}
        def replace(match):
            key = match.group(1)
            return str(variables.get(key, match.group(0)))

        # Match {{variable_name}}
        rendered = re.sub(r"\{\{([a-zA-Z0-9_]+)\}\}", replace, template)

        return rendered

    @staticmethod
    def extract_placeholders(template: str) -> List[str]:
        """
        Extract all {{variable_name}} placeholders from a template string.

        Args:
            template: The string template to analyze.

        Returns:
            A list of unique placeholder names found (without curly braces).
        """
        if not template:
            return []
        matches = re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}", template)
        return list(dict.fromkeys(matches))  # Maintain order and remove duplicates

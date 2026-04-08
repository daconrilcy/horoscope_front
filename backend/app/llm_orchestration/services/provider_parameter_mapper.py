from __future__ import annotations

from typing import Any, Optional
from app.llm_orchestration.execution_profiles_types import (
    ReasoningProfile,
    VerbosityProfile,
    OutputMode,
    ToolMode,
)

class ProviderParameterMapper:
    """
    Maps stable internal execution profiles to provider-specific parameters (Story 66.11 D4, D6).
    """

    @staticmethod
    def map_for_openai(
        reasoning_profile: ReasoningProfile,
        verbosity_profile: VerbosityProfile,
        output_mode: OutputMode,
        tool_mode: ToolMode,
    ) -> dict[str, Any]:
        """
        Maps profiles to OpenAI parameters (D6).
        Note: Multi-provider support and detailed verbosity handling are in Story 66.18.
        """
        params = {}

        # 1. Reasoning profile (D6)
        if reasoning_profile == "off":
            # temperature remains applicable
            pass
        elif reasoning_profile == "light":
            params["reasoning_effort"] = "low"
            params["temperature"] = None
        elif reasoning_profile == "medium":
            params["reasoning_effort"] = "medium"
            params["temperature"] = None
        elif reasoning_profile == "deep":
            params["reasoning_effort"] = "high"
            params["temperature"] = None

        # 2. Output mode
        if output_mode == "structured_json":
            # This usually triggers response_format={"type": "json_object"} 
            # or structured outputs (handled by ResponsesClient)
            params["response_format"] = {"type": "json_object"}

        # 3. Tool mode
        if tool_mode == "none":
            params["tool_choice"] = "none"
        elif tool_mode == "required":
            params["tool_choice"] = "required"
        # "optional" is usually the default (None or "auto")

        return params

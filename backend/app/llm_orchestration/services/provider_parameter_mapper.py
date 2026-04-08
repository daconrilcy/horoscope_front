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
    Maps stable internal execution profiles to provider-specific parameters (Story 66.11, 66.18).
    """

    @staticmethod
    def map(
        provider: str,
        reasoning_profile: ReasoningProfile,
        verbosity_profile: VerbosityProfile,
        output_mode: OutputMode,
        tool_mode: ToolMode,
    ) -> dict[str, Any]:
        """Dispatch mapping based on provider (Story 66.18)."""
        if provider == "openai":
            return ProviderParameterMapper.map_for_openai(
                reasoning_profile, verbosity_profile, output_mode, tool_mode
            )
        elif provider == "anthropic":
            return ProviderParameterMapper.map_for_anthropic(
                reasoning_profile, verbosity_profile, output_mode, tool_mode
            )
        
        raise NotImplementedError(
            f"No parameter mapping for provider: {provider}. "
            f"Please implement map_for_{provider}() in ProviderParameterMapper."
        )

    @staticmethod
    def map_for_openai(
        reasoning_profile: ReasoningProfile,
        verbosity_profile: VerbosityProfile,
        output_mode: OutputMode,
        tool_mode: ToolMode,
    ) -> dict[str, Any]:
        """Maps profiles to OpenAI parameters (D6 in 66.11)."""
        params = {}

        # 1. Reasoning profile
        if reasoning_profile == "off":
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
            params["response_format"] = {"type": "json_object"}

        # 3. Tool mode
        if tool_mode == "none":
            params["tool_choice"] = "none"
        elif tool_mode == "required":
            params["tool_choice"] = "required"

        return params

    @staticmethod
    def map_for_anthropic(
        reasoning_profile: ReasoningProfile,
        verbosity_profile: VerbosityProfile,
        output_mode: OutputMode,
        tool_mode: ToolMode,
    ) -> dict[str, Any]:
        """Maps profiles to Anthropic parameters (Story 66.18 AC4)."""
        params = {}

        # 1. Reasoning profile (Anthropic 'thinking' mode)
        if reasoning_profile == "deep":
            params["thinking"] = {"type": "enabled", "budget_tokens": 16000}
            # Extended thinking requires higher max_tokens usually
        elif reasoning_profile == "medium":
            params["thinking"] = {"type": "enabled", "budget_tokens": 4000}
        
        # 2. Tool mode
        if tool_mode == "none":
            params["tool_choice"] = {"type": "none"}
        elif tool_mode == "required":
            params["tool_choice"] = {"type": "any"} # Anthropic 'any' means at least one tool must be used

        return params

    @staticmethod
    def resolve_verbosity_instruction(verbosity_profile: VerbosityProfile) -> tuple[str, Optional[int]]:
        """
        Translates verbosity profile into a textual instruction and a recommended max_tokens (Story 66.18 D3, D4).
        """
        if verbosity_profile == "concise":
            return "Réponds de façon très concise et directe, va droit à l'essentiel.", 800
        elif verbosity_profile == "detailed":
            return "Fournis une réponse riche, détaillée et nuancée avec des explications approfondies.", 4000
        
        # Balanced / Default
        return "", None

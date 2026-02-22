"""Shared utilities for AI Engine services."""

from __future__ import annotations

import threading

from app.ai_engine.config import ai_engine_settings
from app.ai_engine.exceptions import ValidationError
from app.ai_engine.providers.base import ProviderClient
from app.ai_engine.providers.openai_client import OpenAIClient

_provider_clients: dict[str, ProviderClient] = {}
_provider_lock = threading.Lock()


def get_provider_client(provider_name: str) -> ProviderClient:
    """
    Get provider client by name (singleton per provider, thread-safe).

    Args:
        provider_name: Name of the provider ("openai")

    Returns:
        ProviderClient instance (reused across requests)

    Raises:
        ValidationError: If provider is not supported
    """
    with _provider_lock:
        if provider_name in _provider_clients:
            return _provider_clients[provider_name]

        if provider_name == "openai":
            client = OpenAIClient()
            _provider_clients[provider_name] = client
            return client

        raise ValidationError(
            f"unsupported provider: {provider_name}",
            details={"provider": provider_name, "supported": "openai"},
        )


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost in USD based on token usage."""
    input_cost = (input_tokens / 1000) * ai_engine_settings.cost_per_1k_input_tokens
    output_cost = (output_tokens / 1000) * ai_engine_settings.cost_per_1k_output_tokens
    return round(input_cost + output_cost, 6)

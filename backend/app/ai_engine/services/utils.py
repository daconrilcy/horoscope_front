"""Shared utilities for AI Engine services."""

from __future__ import annotations

from app.ai_engine.config import ai_engine_settings


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost in USD based on token usage."""
    input_cost = (input_tokens / 1000) * ai_engine_settings.cost_per_1k_input_tokens
    output_cost = (output_tokens / 1000) * ai_engine_settings.cost_per_1k_output_tokens
    return round(input_cost + output_cost, 6)

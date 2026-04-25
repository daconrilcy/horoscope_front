"""Expose le namespace de generation LLM dedie a l horoscope quotidien."""

from app.services.llm_generation.horoscope_daily.narration_service import (
    generate_horoscope_narration_via_gateway,
    map_gateway_result_to_narrator_result,
)

__all__ = ["generate_horoscope_narration_via_gateway", "map_gateway_result_to_narrator_result"]

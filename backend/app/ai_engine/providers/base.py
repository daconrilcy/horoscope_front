"""Abstract base class for AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, AsyncIterator

if TYPE_CHECKING:
    from app.ai_engine.schemas import ChatMessage


@dataclass
class ProviderResult:
    """Result from a provider call."""

    text: str
    input_tokens: int = field(default=0)
    output_tokens: int = field(default=0)
    model: str = field(default="")

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.input_tokens + self.output_tokens


class ProviderClient(ABC):
    """Abstract base class for AI provider clients."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        ...

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        timeout_seconds: int = 30,
    ) -> ProviderResult:
        """
        Generate text from a single prompt.

        Args:
            prompt: The input prompt
            model: Model to use (None for default)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            timeout_seconds: Request timeout

        Returns:
            ProviderResult with generated text and usage info

        Raises:
            UpstreamError: On provider error
            UpstreamTimeoutError: On timeout
            UpstreamRateLimitError: On rate limit
        """
        ...

    @abstractmethod
    async def chat(
        self,
        messages: list["ChatMessage"],
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        timeout_seconds: int = 30,
        stream: bool = False,
    ) -> ProviderResult | AsyncIterator[str]:
        """
        Generate a chat completion.

        Args:
            messages: List of chat messages
            model: Model to use (None for default)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            timeout_seconds: Request timeout
            stream: Whether to stream the response

        Returns:
            ProviderResult for non-streaming, AsyncIterator[str] for streaming

        Raises:
            UpstreamError: On provider error
            UpstreamTimeoutError: On timeout
            UpstreamRateLimitError: On rate limit
        """
        ...

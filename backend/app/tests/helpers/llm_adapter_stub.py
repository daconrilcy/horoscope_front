"""Fournit des doubles de tests explicites pour la façade `AIEngineAdapter`."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

ChatGenerator = Callable[
    [list[dict[str, str]], dict[str, str | None], int, str, str, str],
    Awaitable[Any],
]
GuidanceGenerator = Callable[
    [str, dict[str, str | None], int, str, str, str],
    Awaitable[Any],
]

_chat_generator: ChatGenerator | None = None
_guidance_generator: GuidanceGenerator | None = None


def set_test_chat_generator(generator: ChatGenerator | None) -> None:
    """Enregistre un générateur de test pour les appels chat de la façade."""
    global _chat_generator
    _chat_generator = generator


def set_test_guidance_generator(generator: GuidanceGenerator | None) -> None:
    """Enregistre un générateur de test pour les appels guidance de la façade."""
    global _guidance_generator
    _guidance_generator = generator


def get_test_chat_generator() -> ChatGenerator | None:
    """Retourne le générateur de test chat actif."""
    return _chat_generator


def get_test_guidance_generator() -> GuidanceGenerator | None:
    """Retourne le générateur de test guidance actif."""
    return _guidance_generator


def reset_test_generators() -> None:
    """Réinitialise les générateurs de test afin d'éviter les fuites inter-tests."""
    global _chat_generator, _guidance_generator
    _chat_generator = None
    _guidance_generator = None


def get_test_generators_state() -> tuple[bool, bool]:
    """Expose l'état des doubles actifs pour les tests de structure."""
    return (_chat_generator is not None, _guidance_generator is not None)

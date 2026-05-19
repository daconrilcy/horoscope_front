"""Contrats immutables des signaux semantiques d'interpretation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InterpretationSignal:
    """Signal normalise produit depuis un fait astrologique deja calcule."""

    signal_code: str
    theme_code: str
    source_type: str
    source_code: str
    priority: str
    priority_rank: int
    weight: float
    semantic_category: str
    theme_category: str
    explanation_fact: str


@dataclass(frozen=True, slots=True)
class InterpretationThemeActivation:
    """Activation agregee d'un theme par un ensemble de signaux."""

    theme_code: str
    theme_category: str
    activation_score: float
    priority: str
    priority_rank: int
    contributing_signals: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class InterpretationAdapterResult:
    """Resultat canonique pret pour les couches de rendu aval."""

    signals: tuple[InterpretationSignal, ...]
    activated_themes: tuple[InterpretationThemeActivation, ...]
    dominant_topics: tuple[str, ...]
    dominant_axes: tuple[str, ...]
    tension_patterns: tuple[str, ...]
    support_patterns: tuple[str, ...]
    critical_patterns: tuple[str, ...]
    narrative_priorities: tuple[str, ...]

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PublicDomainScore:
    key: str
    label: str
    score_10: float
    level: str
    rank: int
    note_20_internal: float
    internal_codes: list[str]
    display_order: int
    signal_label: str | None = None


def to_score_10(note_20: float) -> float:
    """Derives a score out of 10 from a note out of 20."""
    return round(note_20 / 2.0, 1)


def to_level(score_10: float) -> str:
    """Maps a score out of 10 to a readable level."""
    if score_10 >= 9.0:
        return "très_favorable"
    elif score_10 >= 7.5:
        return "favorable"
    elif score_10 >= 6.0:
        return "stable"
    elif score_10 >= 4.5:
        return "mitigé"
    else:
        return "exigeant"


def rank_domains(domains: list[PublicDomainScore]) -> list[PublicDomainScore]:
    """Ranks domains by score_10 descending (1-based)."""
    if not domains:
        return []

    sorted_domains = sorted(domains, key=lambda x: x.score_10, reverse=True)
    for i, domain in enumerate(sorted_domains):
        domain.rank = i + 1
    return sorted_domains

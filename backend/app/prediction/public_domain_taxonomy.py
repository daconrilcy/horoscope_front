from __future__ import annotations

from pydantic import BaseModel


class PublicDomainEntry(BaseModel):
    key: str
    label_fr: str
    label_en: str
    icon: str
    internal_codes: list[str]
    display_order: int


PUBLIC_DOMAINS: dict[str, PublicDomainEntry] = {
    "pro_ambition": PublicDomainEntry(
        key="pro_ambition",
        label_fr="Pro & Ambition",
        label_en="Pro & Ambition",
        icon="💼",
        internal_codes=["work", "career"],
        display_order=1,
    ),
    "relations_echanges": PublicDomainEntry(
        key="relations_echanges",
        label_fr="Relations & échanges",
        label_en="Relations & Exchanges",
        icon="🤝",
        internal_codes=["love", "communication", "social_network", "sex_intimacy"],
        display_order=2,
    ),
    "energie_bienetre": PublicDomainEntry(
        key="energie_bienetre",
        label_fr="Énergie & bien-être",
        label_en="Energy & Well-being",
        icon="⚡",
        internal_codes=["energy", "health", "mood"],
        display_order=3,
    ),
    "argent_ressources": PublicDomainEntry(
        key="argent_ressources",
        label_fr="Argent & ressources",
        label_en="Money & Resources",
        icon="💰",
        internal_codes=["money"],
        display_order=4,
    ),
    "vie_personnelle": PublicDomainEntry(
        key="vie_personnelle",
        label_fr="Vie personnelle",
        label_en="Personal Life",
        icon="🎨",
        internal_codes=["pleasure_creativity", "family_home"],
        display_order=5,
    ),
}

DISPLAY_ORDER: list[str] = [
    "pro_ambition",
    "relations_echanges",
    "energie_bienetre",
    "argent_ressources",
    "vie_personnelle",
]

_REVERSE_LOOKUP: dict[str, str] = {
    internal_code: public_key
    for public_key, entry in PUBLIC_DOMAINS.items()
    for internal_code in entry.internal_codes
}


def map_internal_to_public(code: str) -> str | None:
    """Maps an internal domain code to its public domain key."""
    return _REVERSE_LOOKUP.get(code)


def aggregate_public_domain_score(internal_scores: dict[str, float]) -> dict[str, float]:
    """
    Aggregates internal scores into public domain scores using the max rule.
    Returns a dict of public_domain_key -> max_score.
    """
    public_scores: dict[str, list[float]] = {}

    for internal_code, score in internal_scores.items():
        if score is None:
            continue
        public_key = map_internal_to_public(internal_code)
        if public_key:
            public_scores.setdefault(public_key, []).append(score)

    return {
        public_key: max(scores)
        for public_key, scores in public_scores.items()
        if scores
    }


# Validation: Ensure all 12 internal codes are covered
EXPECTED_INTERNAL_CODES = {
    "love",
    "work",
    "career",
    "energy",
    "mood",
    "health",
    "money",
    "sex_intimacy",
    "family_home",
    "social_network",
    "communication",
    "pleasure_creativity",
}

if not EXPECTED_INTERNAL_CODES.issubset(set(_REVERSE_LOOKUP.keys())):
    missing = EXPECTED_INTERNAL_CODES - set(_REVERSE_LOOKUP.keys())
    raise ImportError(f"Missing internal codes in public domain taxonomy: {missing}")

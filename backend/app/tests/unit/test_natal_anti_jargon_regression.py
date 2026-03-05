from __future__ import annotations

import re

PEDAGOGY_MARKERS = (
    "signifie",
    "veut dire",
    "c'est",
    "correspond",
    "représente",
    "represente",
    "désigne",
    "designe",
    "indique",
    "concerne",
    "en pratique",
    "autrement dit",
)

JARGON_PATTERNS = (
    r"\bconjonction\b",
    r"\btrigone\b",
    r"\bcarr[eé]\b",
    r"\bopposition\b",
    r"\bsextile\b",
    r"\bmilieu du ciel\b",
    r"\bascendant\b",
    r"\bdescendant\b",
    r"\bfond du ciel\b",
    r"\bmaison\s+\d{1,2}\b",
)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _anti_jargon_violations(text: str) -> list[str]:
    sentences = _split_sentences(text)
    violations: list[str] = []

    for idx, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        next_sentence_lower = sentences[idx + 1].lower() if idx + 1 < len(sentences) else ""
        window = f"{sentence_lower} {next_sentence_lower}".strip()

        for pattern in JARGON_PATTERNS:
            if not re.search(pattern, sentence_lower):
                continue
            if any(marker in window for marker in PEDAGOGY_MARKERS):
                continue
            violations.append(sentence)
            break

    return violations


def test_anti_jargon_regression_on_sample_outputs() -> None:
    # Echantillon représentatif de sorties attendues en production.
    samples = [
        (
            "Une conjonction Soleil-Vénus signifie que les deux planètes sont proches, "
            "donc identité et valeurs se mélangent. "
            "Le Milieu du Ciel représente la vie publique, ce qui indique une image visible. "
            "La Maison 10 concerne le domaine professionnel et montre où ta contribution se voit."
        ),
        (
            "Un trigone entre Mars et Saturne veut dire que l'action et la discipline coopèrent "
            "facilement. L'Ascendant représente la manière d'entrer en relation avec le monde. "
            "La Maison 7 correspond au secteur du couple et des partenariats."
        ),
        (
            "Un carré Mercure-Neptune désigne une tension entre logique et imagination. "
            "Le Descendant indique le type de partenaire recherché. "
            "Le Fond du Ciel représente les racines et l'espace intime."
        ),
    ]

    for sample in samples:
        assert _anti_jargon_violations(sample) == []


def test_anti_jargon_detector_flags_undefined_terms() -> None:
    bad_output = (
        "La conjonction Soleil-Vénus est forte. "
        "Milieu du Ciel en Taureau. "
        "Maison 10 active toute la période."
    )
    violations = _anti_jargon_violations(bad_output)
    assert len(violations) >= 2

# Commentaire global: validation anti-fuite technique du texte narratif natal public.
"""Refuse les sorties narratives qui exposent des surfaces techniques interdites."""

from __future__ import annotations

import re
from collections.abc import Iterable

from app.domain.llm.prompting.narrative_natal_reading_v1 import (
    NARRATIVE_CHAPTER_ORDER,
    NarrativeNatalReadingV1,
)
from app.services.llm_generation.natal.narrative_semantic_integrity import (
    validate_narrative_semantic_integrity,
)
from app.services.llm_generation.natal.rejected_answer_workflow import (
    CONTROLLED_REJECTED_CLIENT_MESSAGE,
    REJECTED_NARRATIVE_LOG_EVENT,
    RejectedNarrativeAnswerOutcome,
)

_TECHNICAL_LEAK_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bvisibility_expression\b",
        r"\bfrustration_pressure\b",
        r"\bcondition_axis\s*:",
        r"\bcentrality\s+score\b",
        r"\binterpretive_signal_ids\b",
        r"\baudit_input\b",
        r"\bexplanation_facts\b",
        r"\binterpretation_adapter\b",
        r"\bprojection_version\b",
        r"\bprompt_payloads\b",
        r"\btechnical_scores\b",
        r"\bchart_json\b",
        r"\bnatal_data\b",
        r"\bevidence_refs\b",
    )
)


def find_narrative_public_technical_leaks(text: str) -> list[str]:
    """Retourne les motifs interdits detectes dans un texte utilisateur."""
    leaks: list[str] = []
    for pattern in _TECHNICAL_LEAK_PATTERNS:
        if pattern.search(text):
            leaks.append(pattern.pattern)
    return leaks


def validate_narrative_reading_public_text(reading: NarrativeNatalReadingV1) -> list[str]:
    """Valide l'integralite du contenu narratif avant persistance ou exposition."""
    violations: list[str] = []
    texts: Iterable[str] = [
        chapter.title + "\n" + chapter.narrative + "\n" + "\n".join(chapter.key_points)
        for chapter in reading.chapters
    ]
    for element in reading.used_astrological_elements:
        texts = (*texts, element.astrological_label, element.consequence)
    for text in texts:
        for leak in find_narrative_public_technical_leaks(text):
            violations.append(leak)
    if [chapter.key for chapter in reading.chapters] != list(NARRATIVE_CHAPTER_ORDER):
        violations.append("chapter_order_invalid")
    violations.extend(validate_narrative_semantic_integrity(reading))
    return sorted(set(violations))


def build_semantic_integrity_rejection_outcome(
    *,
    answer_id: str,
    answer_type: str,
    raw_answer: dict[str, object],
    violations: list[str],
) -> RejectedNarrativeAnswerOutcome:
    """Construit un rejet interne lorsque la lecture narrative manque d'integrite semantique."""
    return RejectedNarrativeAnswerOutcome(
        answer_id=answer_id,
        answer_type=answer_type,
        status="rejected",
        grounding_status="ungrounded",
        rejection_reason={
            "code": "narrative_semantic_integrity",
            "violations": violations,
        },
        validation_context=[
            {
                "section_id": "narrative_semantic_integrity",
                "section_status": "rejected",
                "validation_errors": violations,
            }
        ],
        raw_answer_storage={"structured_output": raw_answer},
        client_message=CONTROLLED_REJECTED_CLIENT_MESSAGE,
        log_event=REJECTED_NARRATIVE_LOG_EVENT,
    )


def build_technical_leak_rejection_outcome(
    *,
    answer_id: str,
    answer_type: str,
    raw_answer: dict[str, object],
    violations: list[str],
) -> RejectedNarrativeAnswerOutcome:
    """Construit un rejet interne lorsque le texte narratif public fuit des surfaces techniques."""
    return RejectedNarrativeAnswerOutcome(
        answer_id=answer_id,
        answer_type=answer_type,
        status="rejected",
        grounding_status="ungrounded",
        rejection_reason={
            "code": "narrative_public_technical_leak",
            "violations": violations,
        },
        validation_context=[
            {
                "section_id": "narrative_public_denylist",
                "section_status": "rejected",
                "validation_errors": violations,
            }
        ],
        raw_answer_storage={"structured_output": raw_answer},
        client_message=CONTROLLED_REJECTED_CLIENT_MESSAGE,
        log_event=REJECTED_NARRATIVE_LOG_EVENT,
    )

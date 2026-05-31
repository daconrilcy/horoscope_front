# Commentaire global: validation anti-fuite technique du texte narratif natal public.
"""Refuse les sorties narratives qui exposent des surfaces techniques interdites."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Callable

from app.domain.astrology.interpretation.basic_natal_reading_plan import BasicNatalReadingPlan
from app.domain.astrology.reading.basic_natal_contracts import BASIC_NATAL_PUBLIC_SCHEMA_VERSION
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
_BASIC_NATAL_FORBIDDEN_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\branking_score\b",
        r"\bcondition_axis\b",
        r"\baudit_input\b",
        r"\bvisibility_expression\b",
        r"\binterpretive_signal_ids\b",
        r"\btechnical_scores?\b",
        r"\bevidence_refs\b",
        r"\bscore\b",
        r"\borbe\b",
        r"\bdignite\b",
    )
)
_DATE_ONLY_FORBIDDEN_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bAscendant\b",
        r"\bMC\b",
        r"\bmaison(?:s)?\b",
        r"\bmaitre de maison\b",
        r"\bangularite\b",
    )
)
_PRESCRIPTIVE_ADVICE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bvous devez\b",
        r"\bil faut absolument\b",
        r"\bprenez cette decision\b",
        r"\bquittez\b",
        r"\binvestissez\b",
    )
)
_KNOWN_ASTROLOGICAL_FACT_TERMS = frozenset(
    {
        "soleil",
        "lune",
        "mercure",
        "venus",
        "mars",
        "jupiter",
        "saturne",
        "ascendant",
        "mc",
        "maison",
        "maisons",
    }
)


@dataclass(frozen=True, slots=True)
class BasicNatalDraftValidationResult:
    """Resultat structure de validation d'un brouillon narratif Basic."""

    is_valid: bool
    validation_errors: list[str]
    request_id: str
    engine_version: str
    schema_version: str
    fallback_used: bool = False

    def to_metadata(self) -> dict[str, object]:
        """Expose les champs d'audit exiges par le workflow de rejet."""
        return {
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "request_id": self.request_id,
            "engine_version": self.engine_version,
            "schema_version": self.schema_version,
            "fallback_used": self.fallback_used,
        }


@dataclass(frozen=True, slots=True)
class BasicNatalDraftRepairOutcome:
    """Expose le resultat controle apres validation, reparation puis fallback."""

    accepted_draft: dict[str, object] | None
    validation_result: BasicNatalDraftValidationResult
    repair_attempted: bool
    fallback_used: bool
    rejection_outcome: RejectedNarrativeAnswerOutcome | None


BasicNatalRepairCallback = Callable[
    [Mapping[str, object], BasicNatalReadingPlan, BasicNatalDraftValidationResult],
    Mapping[str, object] | None,
]


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


def validate_basic_natal_draft_against_plan(
    *,
    draft: Mapping[str, object],
    reading_plan: BasicNatalReadingPlan,
    request_id: str,
    schema_version: str = BASIC_NATAL_PUBLIC_SCHEMA_VERSION,
    fallback_used: bool = False,
) -> BasicNatalDraftValidationResult:
    """Valide un brouillon Basic contre le plan de lecture canonique."""
    errors: list[str] = []
    errors.extend(_draft_section_shape_errors(draft))
    section_items = _draft_sections(draft)
    expected_codes = tuple(section.section_code for section in reading_plan.sections)
    observed_codes = tuple(
        str(section.get("section_code") or "").strip() for section in section_items
    )

    if missing := sorted(set(expected_codes).difference(observed_codes)):
        errors.extend(f"missing_requested_section:{code}" for code in missing)
    if unauthorized := sorted(set(observed_codes).difference(expected_codes)):
        errors.extend(f"unauthorized_section:{code}" for code in unauthorized)
    if len(observed_codes) != len(set(observed_codes)):
        errors.append("duplicate_section")

    allowed_evidence_ids = {evidence.id for evidence in reading_plan.public_evidence}
    allowed_fact_ids = {
        fact_id for section in reading_plan.sections for fact_id in section.required_fact_ids
    }
    sections_by_code = {section.section_code: section for section in reading_plan.sections}
    for section in section_items:
        section_code = str(section.get("section_code") or "").strip()
        content = _string_value(section.get("content"))
        if not content:
            errors.append(f"empty_section:{section_code or 'unknown'}")
        if _word_count(content) > _section_word_limit(sections_by_code.get(section_code)):
            errors.append(f"section_too_long:{section_code}")

        section_evidence_ids = set(_string_sequence(section.get("evidence_ids")))
        expected_evidence_ids = set(
            sections_by_code.get(section_code, _EmptyPlanSection()).supporting_evidence_ids
        )
        if not section_evidence_ids:
            errors.append(f"missing_section_public_source:{section_code or 'unknown'}")
        if unexpected_evidence := sorted(section_evidence_ids.difference(expected_evidence_ids)):
            errors.extend(
                f"unsupported_section_source:{section_code}:{item}" for item in unexpected_evidence
            )

        section_fact_ids = set(_string_sequence(section.get("fact_ids")))
        if unexpected_facts := sorted(section_fact_ids.difference(allowed_fact_ids)):
            errors.extend(f"unsupported_generated_fact:{item}" for item in unexpected_facts)

    if missing_limitations := _missing_required_items(
        draft.get("limitations"), reading_plan.limitations
    ):
        errors.extend(f"missing_limitation:{item}" for item in missing_limitations)
    if missing_disclaimers := _missing_required_items(
        draft.get("disclaimers"), reading_plan.disclaimers
    ):
        errors.extend(f"missing_disclaimer:{item}" for item in missing_disclaimers)
    if not set(_string_sequence(draft.get("public_evidence_ids"))).issubset(allowed_evidence_ids):
        errors.append("unsupported_public_source")
    if not _string_sequence(draft.get("public_evidence_ids")) and not _string_sequence(
        draft.get("public_sources")
    ):
        errors.append("missing_public_sources")

    serialized = json.dumps(
        {
            "sections": draft.get("sections"),
            "public_sources": draft.get("public_sources"),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    errors.extend(_basic_public_text_errors(serialized, reading_plan, expected_codes))
    errors = sorted(set(errors))
    return BasicNatalDraftValidationResult(
        is_valid=not errors,
        validation_errors=errors,
        request_id=request_id,
        engine_version=reading_plan.engine_version,
        schema_version=schema_version,
        fallback_used=fallback_used,
    )


def build_basic_natal_rejection_outcome(
    *,
    answer_id: str,
    raw_answer: Mapping[str, object],
    validation_result: BasicNatalDraftValidationResult,
) -> RejectedNarrativeAnswerOutcome:
    """Construit l'audit de rejet Basic avec les metadonnees de validation."""
    metadata = validation_result.to_metadata()
    return RejectedNarrativeAnswerOutcome(
        answer_id=answer_id,
        answer_type="basic",
        status="rejected",
        grounding_status="ungrounded",
        rejection_reason={"code": "basic_natal_draft_validation", **metadata},
        validation_context=[
            {
                "section_id": "basic_natal_draft",
                "section_status": "rejected",
                **metadata,
            }
        ],
        raw_answer_storage={"structured_output": dict(raw_answer)},
        client_message=CONTROLLED_REJECTED_CLIENT_MESSAGE,
        log_event=REJECTED_NARRATIVE_LOG_EVENT,
    )


def build_basic_natal_deterministic_fallback(
    reading_plan: BasicNatalReadingPlan,
) -> dict[str, object]:
    """Construit un fallback court uniquement depuis les preuves publiques du plan."""
    evidence_by_section = _evidence_by_section(reading_plan)
    return {
        "sections": [
            {
                "section_code": section.section_code,
                "heading": section.heading_intent,
                "content": _fallback_section_text(
                    section.heading_intent, evidence_by_section[section.section_code]
                ),
                "evidence_ids": [
                    evidence.id for evidence in evidence_by_section[section.section_code]
                ],
                "fact_ids": list(section.required_fact_ids),
            }
            for section in reading_plan.sections
        ],
        "limitations": list(reading_plan.limitations),
        "disclaimers": list(reading_plan.disclaimers),
        "public_evidence_ids": [evidence.id for evidence in reading_plan.public_evidence],
        "public_sources": [evidence.label for evidence in reading_plan.public_evidence],
    }


def validate_repair_or_fallback_basic_natal_draft(
    *,
    draft: Mapping[str, object],
    reading_plan: BasicNatalReadingPlan,
    request_id: str,
    answer_id: str,
    repair_callback: BasicNatalRepairCallback | None = None,
) -> BasicNatalDraftRepairOutcome:
    """Applique validation, une reparation contrainte puis un fallback valide."""
    initial_result = validate_basic_natal_draft_against_plan(
        draft=draft, reading_plan=reading_plan, request_id=request_id
    )
    if initial_result.is_valid:
        return BasicNatalDraftRepairOutcome(
            accepted_draft=dict(draft),
            validation_result=initial_result,
            repair_attempted=False,
            fallback_used=False,
            rejection_outcome=None,
        )

    if repair_callback is not None:
        repaired_draft = repair_callback(draft, reading_plan, initial_result)
        if repaired_draft is not None:
            repaired_result = validate_basic_natal_draft_against_plan(
                draft=repaired_draft,
                reading_plan=reading_plan,
                request_id=request_id,
            )
            if repaired_result.is_valid:
                return BasicNatalDraftRepairOutcome(
                    accepted_draft=dict(repaired_draft),
                    validation_result=repaired_result,
                    repair_attempted=True,
                    fallback_used=False,
                    rejection_outcome=None,
                )

    fallback = build_basic_natal_deterministic_fallback(reading_plan)
    fallback_result = validate_basic_natal_draft_against_plan(
        draft=fallback,
        reading_plan=reading_plan,
        request_id=request_id,
        fallback_used=True,
    )
    if fallback_result.is_valid:
        return BasicNatalDraftRepairOutcome(
            accepted_draft=fallback,
            validation_result=fallback_result,
            repair_attempted=repair_callback is not None,
            fallback_used=True,
            rejection_outcome=None,
        )

    rejection = build_basic_natal_rejection_outcome(
        answer_id=answer_id,
        raw_answer=draft,
        validation_result=fallback_result,
    )
    return BasicNatalDraftRepairOutcome(
        accepted_draft=None,
        validation_result=fallback_result,
        repair_attempted=repair_callback is not None,
        fallback_used=False,
        rejection_outcome=rejection,
    )


@dataclass(frozen=True, slots=True)
class _EmptyPlanSection:
    """Section vide utilisee pour eviter un fallback implicite sur les sections inconnues."""

    supporting_evidence_ids: tuple[str, ...] = ()
    target_length_words: int = 120


def _draft_sections(draft: Mapping[str, object]) -> list[Mapping[str, object]]:
    """Retourne les sections du brouillon sans accepter de forme non structuree."""
    raw_sections = draft.get("sections")
    if not isinstance(raw_sections, Sequence) or isinstance(raw_sections, (str, bytes)):
        return []
    return [section for section in raw_sections if isinstance(section, Mapping)]


def _draft_section_shape_errors(draft: Mapping[str, object]) -> list[str]:
    """Signale les formes de sections que le contrat Basic ne peut pas auditer."""
    raw_sections = draft.get("sections")
    if not isinstance(raw_sections, Sequence) or isinstance(raw_sections, (str, bytes)):
        return ["invalid_sections_shape"]
    if any(not isinstance(section, Mapping) for section in raw_sections):
        return ["invalid_section_entry"]
    return []


def _string_value(value: object) -> str:
    """Normalise une valeur textuelle facultative."""
    return value.strip() if isinstance(value, str) else ""


def _string_sequence(value: object) -> tuple[str, ...]:
    """Extrait une sequence de chaines non vides sans coercition silencieuse large."""
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())


def _word_count(text: str) -> int:
    """Compte les mots pour appliquer les bornes redactionnelles du plan."""
    return len(re.findall(r"\b\w+\b", text, re.UNICODE))


def _section_word_limit(section: object) -> int:
    """Calcule une limite de longueur locale sans assouplir le contrat public."""
    target = getattr(section, "target_length_words", 120)
    if not isinstance(target, int):
        target = 120
    return max(80, int(target * 1.6))


def _missing_required_items(value: object, required_items: Sequence[str]) -> list[str]:
    """Retourne les mentions obligatoires absentes d'un champ liste."""
    present = set(_string_sequence(value))
    return [item for item in required_items if item not in present]


def _basic_public_text_errors(
    serialized_draft: str,
    reading_plan: BasicNatalReadingPlan,
    expected_section_codes: Sequence[str],
) -> list[str]:
    """Centralise les controles textuels publics du Basic plan-backed validator."""
    errors: list[str] = []
    for pattern in _BASIC_NATAL_FORBIDDEN_PATTERNS:
        if pattern.search(serialized_draft):
            errors.append("technical_or_jargon_marker")
    if _plan_is_date_only(reading_plan):
        for pattern in _DATE_ONLY_FORBIDDEN_PATTERNS:
            if pattern.search(serialized_draft):
                errors.append("date_only_time_based_fact")
    for pattern in _PRESCRIPTIVE_ADVICE_PATTERNS:
        if pattern.search(serialized_draft):
            errors.append("prescriptive_advice")
    lowered = serialized_draft.casefold()
    if re.search(r"\btu\b|\bton\b|\btes\b", lowered) and re.search(
        r"\bvous\b|\bvotre\b|\bvos\b", lowered
    ):
        errors.append("mixed_grammatical_person")
    if "vocation" not in expected_section_codes and re.search(
        r"\bvocation\b|\bcarriere\b", lowered
    ):
        errors.append("unsupported_vocation_section")
    errors.extend(_unsupported_fact_terms(serialized_draft, reading_plan))
    return errors


def _plan_is_date_only(reading_plan: BasicNatalReadingPlan) -> bool:
    """Detecte un plan date-only depuis ses limitations publiques."""
    return any("sans heure" in limitation.casefold() for limitation in reading_plan.limitations)


def _unsupported_fact_terms(
    serialized_draft: str, reading_plan: BasicNatalReadingPlan
) -> list[str]:
    """Refuse les termes astrologiques connus absents des preuves publiques du plan."""
    allowed_text = " ".join(
        (
            *(section.heading_intent for section in reading_plan.sections),
            *(evidence.label for evidence in reading_plan.public_evidence),
            *(evidence.explanation for evidence in reading_plan.public_evidence),
        )
    ).casefold()
    draft_text = serialized_draft.casefold()
    unsupported_terms = sorted(
        term
        for term in _KNOWN_ASTROLOGICAL_FACT_TERMS
        if re.search(rf"\b{re.escape(term)}\b", draft_text)
        and not re.search(rf"\b{re.escape(term)}\b", allowed_text)
    )
    return [f"unsupported_generated_fact:{term}" for term in unsupported_terms]


def _evidence_by_section(
    reading_plan: BasicNatalReadingPlan,
) -> dict[str, tuple[object, ...]]:
    """Indexe les preuves publiques autorisees par section du plan."""
    by_id = {evidence.id: evidence for evidence in reading_plan.public_evidence}
    return {
        section.section_code: tuple(
            by_id[evidence_id]
            for evidence_id in section.supporting_evidence_ids
            if evidence_id in by_id
        )
        for section in reading_plan.sections
    }


def _fallback_section_text(heading_intent: str, evidence: Sequence[object]) -> str:
    """Produit un texte court depuis une preuve publique sans ajouter de fait."""
    if not evidence:
        return f"{heading_intent}: les informations disponibles restent a lire avec nuance."
    labels = ", ".join(
        str(getattr(item, "label", "")).strip() for item in evidence if getattr(item, "label", "")
    )
    return f"{heading_intent}: cette lecture s'appuie uniquement sur {labels}, avec nuance."


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

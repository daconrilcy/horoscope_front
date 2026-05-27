# Commentaire global: ce module applique le rejet interne des reponses narratives non ancrees.
"""Workflow canonique de rejet des reponses narratives non ancrees."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from app.domain.astrology.interpretation.evidence_refs_validation import (
    EvidenceRefsValidationResult,
    EvidenceSectionRequirement,
    build_audit_source_proofs,
    validate_evidence_refs_by_section,
)

CONTROLLED_REJECTED_CLIENT_MESSAGE = (
    "Nous n'avons pas assez de preuves fiables pour afficher cette interpretation. "
    "Votre demande reste enregistree pour analyse interne."
)
REJECTED_NARRATIVE_LOG_EVENT = "narrative_answer_rejected"

RejectionGroundingStatus = Literal["grounded", "partial", "ungrounded", "not_checked"]


@dataclass(frozen=True, slots=True)
class RejectedNarrativeAnswerOutcome:
    """Expose le payload interne et le message client d'une reponse rejetee."""

    answer_id: str
    answer_type: str
    status: Literal["rejected"]
    grounding_status: Literal["ungrounded"]
    rejection_reason: dict[str, object]
    validation_context: list[dict[str, object]]
    raw_answer_storage: dict[str, object]
    client_message: str
    log_event: str
    retry_policy: Literal["out_of_scope"] = "out_of_scope"

    def to_persisted_payload(self) -> dict[str, object]:
        """Prepare le fragment stocke dans l'audit narratif interne."""
        return {
            "status": self.status,
            "rejection_reason": self.rejection_reason,
            "validation_context": self.validation_context,
            "raw_answer_storage": self.raw_answer_storage,
            "client_message": self.client_message,
            "retry_policy": self.retry_policy,
        }

    def to_client_payload(self) -> dict[str, object]:
        """Retourne uniquement le wording controle autorise cote client."""
        return {
            "status": self.status,
            "message": self.client_message,
        }


def build_rejected_narrative_answer_outcome(
    *,
    answer_id: str,
    answer_type: str,
    validation_result: EvidenceRefsValidationResult,
    raw_answer: dict[str, object],
) -> RejectedNarrativeAnswerOutcome | None:
    """Construit un rejet si la validation CS-289 conclut a `ungrounded`."""
    if validation_result.grounding_status != "ungrounded":
        return None
    validation_context = validation_result.to_audit_payload()
    return RejectedNarrativeAnswerOutcome(
        answer_id=answer_id,
        answer_type=answer_type,
        status="rejected",
        grounding_status="ungrounded",
        rejection_reason=_build_rejection_reason(validation_context),
        validation_context=validation_context,
        raw_answer_storage={"structured_output": raw_answer},
        client_message=CONTROLLED_REJECTED_CLIENT_MESSAGE,
        log_event=REJECTED_NARRATIVE_LOG_EVENT,
    )


def build_rejected_narrative_answer_outcome_from_payload(
    *,
    answer_id: str,
    answer_type: str,
    raw_answer: Mapping[str, object],
    projection_version: str,
    projection_hash: str,
    llm_input_version: str,
    llm_input_hash: str,
    llm_astrology_input_v1: Mapping[str, object] | None = None,
) -> RejectedNarrativeAnswerOutcome | None:
    """Reutilise CS-289 pour rejeter un payload porteur de `evidence_refs`."""
    if answer_type == "basic" and "evidence_refs" not in raw_answer:
        return None

    section_requirements = _section_requirements(raw_answer)
    policy_context = _payload_policy_violation_context(
        raw_answer,
        llm_astrology_input_v1=llm_astrology_input_v1,
    )
    if policy_context:
        return RejectedNarrativeAnswerOutcome(
            answer_id=answer_id,
            answer_type=answer_type,
            status="rejected",
            grounding_status="ungrounded",
            rejection_reason=_build_rejection_reason(policy_context),
            validation_context=policy_context,
            raw_answer_storage={"structured_output": dict(raw_answer)},
            client_message=CONTROLLED_REJECTED_CLIENT_MESSAGE,
            log_event=REJECTED_NARRATIVE_LOG_EVENT,
        )
    if not section_requirements:
        return None
    evidence_refs = raw_answer.get("evidence_refs", ())
    if not isinstance(evidence_refs, Sequence) or isinstance(evidence_refs, (str, bytes)):
        evidence_refs = ()
    validation_result = validate_evidence_refs_by_section(
        section_requirements=section_requirements,
        evidence_refs=evidence_refs,
        authorized_sources=build_audit_source_proofs(
            projection_version=projection_version,
            projection_hash=projection_hash,
            llm_input_version=llm_input_version,
            llm_input_hash=llm_input_hash,
        ),
    )
    return build_rejected_narrative_answer_outcome(
        answer_id=answer_id,
        answer_type=answer_type,
        validation_result=validation_result,
        raw_answer=dict(raw_answer),
    )


def emit_rejected_narrative_answer_log(
    logger: logging.Logger,
    *,
    outcome: RejectedNarrativeAnswerOutcome,
    request_id: str,
    trace_id: str,
    use_case: str,
) -> None:
    """Emet un log interne sans exposer le payload narratif brut."""
    logger.info(
        "narrative_answer_rejected request_id=%s trace_id=%s answer_id=%s "
        "answer_type=%s use_case=%s reason_code=%s",
        request_id,
        trace_id,
        outcome.answer_id,
        outcome.answer_type,
        use_case,
        outcome.rejection_reason["code"],
        extra={
            "event": outcome.log_event,
            "request_id": request_id,
            "trace_id": trace_id,
            "answer_id": outcome.answer_id,
            "answer_type": outcome.answer_type,
            "use_case": use_case,
            "rejection_reason": outcome.rejection_reason,
        },
    )


def _build_rejection_reason(validation_context: list[dict[str, object]]) -> dict[str, object]:
    """Derive une raison structuree a partir du contexte de validation."""
    validation_errors: list[str] = []
    failed_sections: list[str] = []
    for section in validation_context:
        if section.get("section_status") != "grounded":
            failed_sections.append(str(section.get("section_id", "unknown")))
        refs = section.get("evidence_refs", [])
        if isinstance(refs, list):
            for ref in refs:
                if isinstance(ref, dict):
                    for error in ref.get("validation_errors", []) or []:
                        validation_errors.append(str(error))
    code = "ungrounded_evidence_refs"
    if any(
        error in {"unsupported_generated_claim", "critical_limit_ignored"}
        for error in validation_errors
    ):
        code = "natal_output_policy_violation"
    return {
        "code": code,
        "failed_sections": failed_sections,
        "validation_errors": sorted(set(validation_errors)),
    }


def _section_requirements(
    raw_answer: Mapping[str, object],
) -> tuple[EvidenceSectionRequirement, ...]:
    """Deduit les sections narratives qui doivent porter des preuves."""
    sections = raw_answer.get("sections")
    if not isinstance(sections, Sequence) or isinstance(sections, (str, bytes)):
        return ()
    requirements: list[EvidenceSectionRequirement] = []
    for index, section in enumerate(sections):
        section_id = ""
        if isinstance(section, Mapping):
            section_id = str(section.get("key") or section.get("section_id") or "").strip()
        if not section_id:
            section_id = f"section_{index}"
        requirements.append(EvidenceSectionRequirement(section_id, requires_evidence=True))
    return tuple(requirements)


def _payload_policy_violation_context(
    raw_answer: Mapping[str, object],
    *,
    llm_astrology_input_v1: Mapping[str, object] | None = None,
) -> list[dict[str, object]]:
    """Detecte les assertions non supportees et les limites critiques ignorees."""
    violations: list[dict[str, object]] = []
    unsupported_claims = _non_empty_string_items(raw_answer.get("unsupported_claims"))
    ignored_limits = _non_empty_string_items(raw_answer.get("ignored_critical_limits"))
    if llm_astrology_input_v1 is not None:
        backend_claims, backend_limits = _backend_policy_violations(
            raw_answer,
            llm_astrology_input_v1,
        )
        unsupported_claims.extend(backend_claims)
        ignored_limits.extend(backend_limits)
    if unsupported_claims:
        violations.append(
            {
                "section_id": "unsupported_claims",
                "requires_evidence": True,
                "section_status": "ungrounded",
                "evidence_refs": [
                    {
                        "validation_state": "unsupported_source_type",
                        "validation_errors": ["unsupported_generated_claim"],
                        "claims": unsupported_claims,
                    }
                ],
            }
        )
    if ignored_limits:
        violations.append(
            {
                "section_id": "limits",
                "requires_evidence": True,
                "section_status": "ungrounded",
                "evidence_refs": [
                    {
                        "validation_state": "missing_source",
                        "validation_errors": ["critical_limit_ignored"],
                        "limits": ignored_limits,
                    }
                ],
            }
        )
    return violations


def _backend_policy_violations(
    raw_answer: Mapping[str, object],
    llm_astrology_input_v1: Mapping[str, object],
) -> tuple[list[str], list[str]]:
    """Controle le texte genere contre les faits et limites backend disponibles."""
    text = _answer_text(raw_answer)
    if not text:
        return [], []

    facts = llm_astrology_input_v1.get("facts")
    signals = llm_astrology_input_v1.get("signals")
    limits = llm_astrology_input_v1.get("limits")
    if not isinstance(facts, Mapping) or not isinstance(signals, Mapping):
        return [], []

    supported_terms = _supported_astrology_terms(facts, signals)
    unsupported = [
        term for term in _KNOWN_ASTROLOGY_TERMS if term in text and term not in supported_terms
    ]
    ignored = _ignored_limit_markers(text, limits if isinstance(limits, Mapping) else {})
    return unsupported, ignored


def _answer_text(raw_answer: Mapping[str, object]) -> str:
    """Concatene les champs narratifs existants sans dependre d'un schema LLM nouveau."""
    parts: list[str] = []
    for key in ("title", "summary"):
        value = raw_answer.get(key)
        if isinstance(value, str):
            parts.append(value)
    sections = raw_answer.get("sections")
    if isinstance(sections, Sequence) and not isinstance(sections, (str, bytes)):
        for section in sections:
            if not isinstance(section, Mapping):
                continue
            for key in ("heading", "content"):
                value = section.get(key)
                if isinstance(value, str):
                    parts.append(value)
    for key in ("highlights", "advice"):
        values = raw_answer.get(key)
        if isinstance(values, Sequence) and not isinstance(values, (str, bytes)):
            parts.extend(str(value) for value in values)
    return " ".join(parts).lower()


def _supported_astrology_terms(
    facts: Mapping[str, object],
    signals: Mapping[str, object],
) -> set[str]:
    """Derive les termes astrologiques autorises depuis facts et signaux internes."""
    terms: set[str] = set()
    for collection_key in ("positions", "houses", "major_aspects", "dominants"):
        collection = facts.get(collection_key)
        if isinstance(collection, Sequence) and not isinstance(collection, (str, bytes)):
            for item in collection:
                if isinstance(item, Mapping):
                    terms.update(_string_values_from_mapping(item))
                    house_number = item.get("house_number")
                    if isinstance(house_number, int):
                        terms.add(f"maison {house_number}")
                        terms.add(f"house {house_number}")

    signal_codes = signals.get("interpretive_signal_codes")
    if isinstance(signal_codes, Mapping):
        terms.update(_string_values_from_mapping(signal_codes))
    return {term.lower().replace("_", " ") for term in terms if term}


def _string_values_from_mapping(value: Mapping[str, object]) -> set[str]:
    """Collecte les valeurs textuelles d'un mapping pour les comparaisons de garde."""
    values: set[str] = set()
    for item in value.values():
        if isinstance(item, str):
            values.add(item)
            values.update(part for part in item.replace(":", " ").split() if part)
        elif isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
            values.update(str(part) for part in item if str(part).strip())
    return values


def _ignored_limit_markers(text: str, limits: Mapping[str, object]) -> list[str]:
    """Repere une redaction qui affirme une surface marquee indisponible."""
    missing_data = limits.get("missing_data")
    empty_collections: set[str] = set()
    if isinstance(missing_data, Mapping):
        raw_empty_collections = missing_data.get("empty_collections")
        if isinstance(raw_empty_collections, Sequence) and not isinstance(
            raw_empty_collections, (str, bytes)
        ):
            empty_collections = {str(item) for item in raw_empty_collections}
        if missing_data.get("sign_balances") is None and _mentions_any(
            text,
            ("equilibre element", "equilibre des signes", "balance des signes", "sign balance"),
        ):
            empty_collections.add("sign_balances")

    ignored: list[str] = []
    if "houses" in empty_collections and _mentions_any(text, ("maison", "house")):
        ignored.append("houses")
    if "major_aspects" in empty_collections and _mentions_any(
        text,
        ("aspect", "trigone", "carre", "square", "opposition", "conjonction", "sextile"),
    ):
        ignored.append("major_aspects")
    if "dominants" in empty_collections and _mentions_any(text, ("dominant", "dominante")):
        ignored.append("dominants")
    if "sign_balances" in empty_collections:
        ignored.append("sign_balances")
    return ignored


def _mentions_any(text: str, markers: Sequence[str]) -> bool:
    """Indique si le texte contient au moins un marqueur de surface controlee."""
    return any(marker in text for marker in markers)


def _non_empty_string_items(value: object) -> list[str]:
    """Normalise une liste de marqueurs narratifs sans accepter de texte vide."""
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


_KNOWN_ASTROLOGY_TERMS = frozenset(
    {
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
        "aries",
        "taurus",
        "gemini",
        "cancer",
        "leo",
        "virgo",
        "libra",
        "scorpio",
        "sagittarius",
        "capricorn",
        "aquarius",
        "pisces",
        "trine",
        "square",
        "opposition",
        "conjunction",
        "sextile",
        "soleil",
        "lune",
        "mercure",
        "venus",
        "vénus",
        "jupiter",
        "saturne",
        "uranus",
        "neptune",
        "pluton",
        "belier",
        "bélier",
        "taureau",
        "gemeaux",
        "gémeaux",
        "cancer",
        "lion",
        "vierge",
        "balance",
        "scorpion",
        "sagittaire",
        "capricorne",
        "verseau",
        "poissons",
        "trigone",
        "carre",
        "carré",
        "opposition",
        "conjonction",
        "sextile",
    }
)

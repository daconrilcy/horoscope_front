# Commentaire global: ce module valide les preuves narratives internes section par section.
"""Validation canonique des `evidence_refs` pour l'audit narratif."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

EvidenceSourceType = Literal[
    "structured_fact",
    "interpretive_signal",
    "projection_version",
    "llm_input",
]
EvidenceValidationState = Literal[
    "valid",
    "missing_source",
    "unsupported_source_type",
    "missing_hash",
    "hash_mismatch",
    "not_required",
]
EvidenceSectionStatus = Literal["grounded", "partial", "ungrounded", "not_required"]
NarrativeGroundingStatus = Literal["grounded", "partial", "ungrounded", "not_checked"]

AUTHORIZED_EVIDENCE_SOURCE_TYPES: tuple[str, ...] = (
    "structured_fact",
    "interpretive_signal",
    "projection_version",
    "llm_input",
)


@dataclass(frozen=True, slots=True)
class EvidenceSourceProof:
    """Decrit une source validee disponible pour rattacher une preuve."""

    source_type: EvidenceSourceType
    source_id: str
    source_version: str
    source_hash: str

    def __post_init__(self) -> None:
        """Refuse les ancres source incompletes avant comparaison de hash."""
        _require_non_empty("source_id", self.source_id)
        _require_non_empty("source_version", self.source_version)
        _require_hash(self.source_hash)


@dataclass(frozen=True, slots=True)
class EvidenceSectionRequirement:
    """Declare si une section narrative doit porter au moins une preuve."""

    section_id: str
    requires_evidence: bool

    def __post_init__(self) -> None:
        """Garantit un identifiant de section stable et non vide."""
        _require_non_empty("section_id", self.section_id)


@dataclass(frozen=True, slots=True)
class EvidenceRefValidation:
    """Resultat de validation d'une reference de preuve unitaire."""

    evidence_ref_id: str | None
    section_id: str
    source_type: str | None
    source_id: str | None
    source_version: str | None
    source_hash: str | None
    validation_state: EvidenceValidationState
    validation_errors: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        """Indique si la reference prouve une source autorisee et hashee."""
        return self.validation_state == "valid"

    def to_audit_payload(self) -> dict[str, object]:
        """Serialise le resultat interne pour le JSON d'audit persistant."""
        payload: dict[str, object] = {
            "evidence_ref_id": self.evidence_ref_id,
            "section_id": self.section_id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "source_version": self.source_version,
            "source_hash": self.source_hash,
            "validation_state": self.validation_state,
        }
        if self.validation_errors:
            payload["validation_errors"] = list(self.validation_errors)
        return payload


@dataclass(frozen=True, slots=True)
class EvidenceSectionValidation:
    """Resultat agrege pour une section narrative auditee."""

    section_id: str
    requires_evidence: bool
    section_status: EvidenceSectionStatus
    references: tuple[EvidenceRefValidation, ...]

    def to_audit_payload(self) -> dict[str, object]:
        """Serialise la section et ses preuves pour `narrative_answer_audit_v1`."""
        return {
            "section_id": self.section_id,
            "requires_evidence": self.requires_evidence,
            "section_status": self.section_status,
            "evidence_refs": [reference.to_audit_payload() for reference in self.references],
        }


@dataclass(frozen=True, slots=True)
class EvidenceRefsValidationResult:
    """Expose les statuts par section et le statut global d'audit."""

    sections: tuple[EvidenceSectionValidation, ...]
    grounding_status: NarrativeGroundingStatus

    def to_audit_payload(self) -> list[dict[str, object]]:
        """Retourne le payload stockable dans `UserNatalInterpretationModel.evidence_refs`."""
        return [section.to_audit_payload() for section in self.sections]


def build_audit_source_proofs(
    *,
    projection_version: str,
    projection_hash: str,
    llm_input_version: str,
    llm_input_hash: str,
) -> tuple[EvidenceSourceProof, ...]:
    """Construit les ancres hashées portées par `narrative_answer_audit_v1`."""
    return (
        EvidenceSourceProof(
            source_type="projection_version",
            source_id="projection",
            source_version=projection_version,
            source_hash=projection_hash,
        ),
        EvidenceSourceProof(
            source_type="llm_input",
            source_id="llm_input",
            source_version=llm_input_version,
            source_hash=llm_input_hash,
        ),
    )


def validate_evidence_refs_by_section(
    *,
    section_requirements: Sequence[EvidenceSectionRequirement],
    evidence_refs: Sequence[Mapping[str, object] | object],
    authorized_sources: Sequence[EvidenceSourceProof],
) -> EvidenceRefsValidationResult:
    """Valide les references par section contre des sources autorisees et hashees."""
    source_index = {
        (source.source_type, source.source_id, source.source_version): source
        for source in authorized_sources
    }
    refs_by_section = _group_refs_by_section(evidence_refs)
    unscoped_refs = refs_by_section.get("", ())
    has_single_section = len(section_requirements) == 1
    known_section_ids = {requirement.section_id for requirement in section_requirements}
    sections = tuple(
        _validate_section(
            requirement=requirement,
            section_refs=refs_by_section.get(requirement.section_id, ())
            + (unscoped_refs if has_single_section else ()),
            source_index=source_index,
        )
        for requirement in section_requirements
    )
    orphan_sections = tuple(
        _validate_orphan_section(
            section_id=section_id or "__unscoped__",
            section_refs=section_refs,
            error="unscoped_evidence_ref" if section_id == "" else "unknown_section",
        )
        for section_id, section_refs in refs_by_section.items()
        if section_id not in known_section_ids and not (section_id == "" and has_single_section)
    )
    return EvidenceRefsValidationResult(
        sections=sections + orphan_sections,
        grounding_status=_aggregate_grounding_status(sections + orphan_sections),
    )


def _validate_section(
    *,
    requirement: EvidenceSectionRequirement,
    section_refs: tuple[Mapping[str, object] | object, ...],
    source_index: Mapping[tuple[str, str, str], EvidenceSourceProof],
) -> EvidenceSectionValidation:
    if not requirement.requires_evidence and not section_refs:
        return EvidenceSectionValidation(
            section_id=requirement.section_id,
            requires_evidence=False,
            section_status="not_required",
            references=(),
        )

    references = tuple(
        _validate_ref(ref, section_id=requirement.section_id, source_index=source_index)
        for ref in section_refs
    )
    if not requirement.requires_evidence:
        return EvidenceSectionValidation(
            section_id=requirement.section_id,
            requires_evidence=False,
            section_status="not_required",
            references=references,
        )
    if not references:
        missing_ref = EvidenceRefValidation(
            evidence_ref_id=None,
            section_id=requirement.section_id,
            source_type=None,
            source_id=None,
            source_version=None,
            source_hash=None,
            validation_state="missing_source",
            validation_errors=("missing_required_evidence_ref",),
        )
        return EvidenceSectionValidation(
            section_id=requirement.section_id,
            requires_evidence=True,
            section_status="ungrounded",
            references=(missing_ref,),
        )
    valid_count = sum(1 for reference in references if reference.is_valid)
    if valid_count == len(references):
        section_status: EvidenceSectionStatus = "grounded"
    elif valid_count > 0:
        section_status = "partial"
    else:
        section_status = "ungrounded"
    return EvidenceSectionValidation(
        section_id=requirement.section_id,
        requires_evidence=True,
        section_status=section_status,
        references=references,
    )


def _validate_orphan_section(
    *,
    section_id: str,
    section_refs: tuple[Mapping[str, object] | object, ...],
    error: str,
) -> EvidenceSectionValidation:
    references = tuple(_orphan_ref(ref, section_id=section_id, error=error) for ref in section_refs)
    return EvidenceSectionValidation(
        section_id=section_id,
        requires_evidence=True,
        section_status="ungrounded",
        references=references,
    )


def _orphan_ref(
    ref: Mapping[str, object] | object,
    *,
    section_id: str,
    error: str,
) -> EvidenceRefValidation:
    if not isinstance(ref, Mapping):
        return EvidenceRefValidation(
            evidence_ref_id=None,
            section_id=section_id,
            source_type=None,
            source_id=None,
            source_version=None,
            source_hash=None,
            validation_state="unsupported_source_type",
            validation_errors=("decorative_evidence_ref", error),
        )
    return EvidenceRefValidation(
        evidence_ref_id=_string_field(ref, "evidence_ref_id") or None,
        section_id=section_id,
        source_type=_string_field(ref, "source_type") or None,
        source_id=_string_field(ref, "source_id") or None,
        source_version=_string_field(ref, "source_version") or None,
        source_hash=_string_field(ref, "source_hash") or None,
        validation_state="missing_source",
        validation_errors=(error,),
    )


def _group_refs_by_section(
    evidence_refs: Sequence[Mapping[str, object] | object],
) -> dict[str, tuple[Mapping[str, object] | object, ...]]:
    refs_by_section: dict[str, list[Mapping[str, object] | object]] = {}
    for ref in evidence_refs:
        if isinstance(ref, Mapping):
            section_id = str(ref.get("section_id", "")).strip()
            if section_id:
                refs_by_section.setdefault(section_id, []).append(ref)
                continue
        refs_by_section.setdefault("", []).append(ref)
    return {section_id: tuple(section_refs) for section_id, section_refs in refs_by_section.items()}


def _validate_ref(
    ref: Mapping[str, object] | object,
    *,
    section_id: str,
    source_index: Mapping[tuple[str, str, str], EvidenceSourceProof],
) -> EvidenceRefValidation:
    if not isinstance(ref, Mapping):
        return EvidenceRefValidation(
            evidence_ref_id=None,
            section_id=section_id,
            source_type=None,
            source_id=None,
            source_version=None,
            source_hash=None,
            validation_state="unsupported_source_type",
            validation_errors=("decorative_evidence_ref",),
        )
    source_type = _string_field(ref, "source_type")
    source_id = _string_field(ref, "source_id")
    source_version = _string_field(ref, "source_version")
    source_hash = _string_field(ref, "source_hash")
    evidence_ref_id = _string_field(ref, "evidence_ref_id")
    if source_type not in AUTHORIZED_EVIDENCE_SOURCE_TYPES:
        return _invalid_ref(
            ref,
            section_id=section_id,
            state="unsupported_source_type",
            error="unsupported_source_type",
        )
    if not source_hash:
        return _invalid_ref(ref, section_id=section_id, state="missing_hash", error="missing_hash")
    if not _is_sha256_hex(source_hash):
        return _invalid_ref(ref, section_id=section_id, state="missing_hash", error="invalid_hash")
    if not source_id or not source_version:
        return _invalid_ref(
            ref,
            section_id=section_id,
            state="missing_source",
            error="missing_source_identity",
        )
    source = source_index.get((source_type, source_id, source_version))
    if source is None:
        return _invalid_ref(
            ref,
            section_id=section_id,
            state="missing_source",
            error="missing_source",
        )
    if source.source_hash != source_hash:
        return _invalid_ref(
            ref,
            section_id=section_id,
            state="hash_mismatch",
            error="hash_mismatch",
        )
    return EvidenceRefValidation(
        evidence_ref_id=evidence_ref_id or None,
        section_id=section_id,
        source_type=source_type,
        source_id=source_id,
        source_version=source_version,
        source_hash=source_hash,
        validation_state="valid",
    )


def _invalid_ref(
    ref: Mapping[str, object],
    *,
    section_id: str,
    state: EvidenceValidationState,
    error: str,
) -> EvidenceRefValidation:
    return EvidenceRefValidation(
        evidence_ref_id=_string_field(ref, "evidence_ref_id") or None,
        section_id=section_id,
        source_type=_string_field(ref, "source_type") or None,
        source_id=_string_field(ref, "source_id") or None,
        source_version=_string_field(ref, "source_version") or None,
        source_hash=_string_field(ref, "source_hash") or None,
        validation_state=state,
        validation_errors=(error,),
    )


def _aggregate_grounding_status(
    sections: tuple[EvidenceSectionValidation, ...],
) -> NarrativeGroundingStatus:
    required_statuses = [
        section.section_status for section in sections if section.requires_evidence
    ]
    if not required_statuses:
        return "not_checked"
    if all(status == "grounded" for status in required_statuses):
        return "grounded"
    if any(status == "grounded" for status in required_statuses) or any(
        status == "partial" for status in required_statuses
    ):
        return "partial"
    return "ungrounded"


def _string_field(ref: Mapping[str, object], field_name: str) -> str:
    value = ref.get(field_name)
    if value is None:
        return ""
    return str(value).strip()


def _require_non_empty(field_name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} is required")


def _require_hash(value: str) -> None:
    _require_non_empty("source_hash", value)
    if not _is_sha256_hex(value):
        raise ValueError("source_hash must be a sha256 hex digest")


def _is_sha256_hex(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdefABCDEF" for character in value)

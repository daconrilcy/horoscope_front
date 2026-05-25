# Contrat interne des faits transmis au scoring IA et a la preparation narrative.
"""Structures versionnees entre runtime canonique, scoring et narration."""

from __future__ import annotations

from dataclasses import dataclass

AI_NARRATIVE_INPUT_CONTRACT_VERSION = "ai_narrative_input.v1"


@dataclass(frozen=True, slots=True)
class AINarrativeStructuralFacts:
    """Faits calculatoires issus du runtime canonique et de ses projections."""

    chart_id: str | None
    chart_type: str
    object_codes: tuple[str, ...]
    aspect_codes: tuple[str, ...]
    source_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        """Valide les identifiants structurels minimaux sans source narrative."""
        if not self.chart_type.strip():
            raise ValueError("AI narrative structural facts require chart_type")
        _reject_empty_items("object_codes", self.object_codes)
        _reject_empty_items("aspect_codes", self.aspect_codes)
        _reject_empty_items("source_codes", self.source_codes)


@dataclass(frozen=True, slots=True)
class AINarrativeInterpretiveSignals:
    """Signaux pre-narratifs structures derives des owners interpretatifs."""

    dignity_codes: tuple[str, ...]
    dominance_codes: tuple[str, ...]
    house_position_codes: tuple[str, ...]
    rulership_codes: tuple[str, ...]
    fixed_star_contact_codes: tuple[str, ...]
    advanced_condition_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        """Refuse les signaux anonymes qui rendraient le debug ambigu."""
        for field_name, values in (
            ("dignity_codes", self.dignity_codes),
            ("dominance_codes", self.dominance_codes),
            ("house_position_codes", self.house_position_codes),
            ("rulership_codes", self.rulership_codes),
            ("fixed_star_contact_codes", self.fixed_star_contact_codes),
            ("advanced_condition_codes", self.advanced_condition_codes),
        ):
            _reject_empty_items(field_name, values)


@dataclass(frozen=True, slots=True)
class AINarrativeReadinessFlags:
    """Etat explicite de completude pour scoring et preparation narrative."""

    structural_facts_ready: bool
    interpretive_signals_ready: bool
    public_projection_links_ready: bool
    ready_for_scoring: bool
    ready_for_narrative: bool


@dataclass(frozen=True, slots=True)
class AINarrativeSourceVersions:
    """Versions des sources internes qui ont produit le contrat."""

    runtime_contract: str
    interpretation_input: str
    graph_trace: str | None = None
    rule_governance: str | None = None
    public_projection: str | None = None
    reference_versions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Garantit une provenance versionnee minimale."""
        if not self.runtime_contract.strip():
            raise ValueError("AI narrative source versions require runtime_contract")
        if not self.interpretation_input.strip():
            raise ValueError("AI narrative source versions require interpretation_input")
        _reject_empty_items("reference_versions", self.reference_versions)


@dataclass(frozen=True, slots=True)
class AINarrativeMaskingPolicy:
    """Politique de masquage pour les consommateurs IA internes."""

    include_personal_identifiers: bool
    include_birth_coordinates: bool
    redact_fields: tuple[str, ...] = ()
    controlled_debug_allowed: bool = False

    def __post_init__(self) -> None:
        """Refuse les noms de champs de redaction vides."""
        _reject_empty_items("redact_fields", self.redact_fields)


@dataclass(frozen=True, slots=True)
class AINarrativePersistedProjectionIdentity:
    """Identite d'une projection persistée référencable par l'audit narratif."""

    projection_type: str
    projection_version: str
    projection_hash: str

    def __post_init__(self) -> None:
        """Valide l'ancre minimale de `narrative_answer_audit_v1`."""
        for field_name in ("projection_type", "projection_version", "projection_hash"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"AI narrative persisted projection requires {field_name}")
        if len(self.projection_hash) != 64:
            raise ValueError("AI narrative persisted projection requires sha256 projection_hash")


@dataclass(frozen=True, slots=True)
class AINarrativePublicProjectionLink:
    """Lien vers un owner de projection publique sans embarquer son payload."""

    owner: str
    primitive_id: str
    projection_id: str
    persisted_projection: AINarrativePersistedProjectionIdentity | None = None

    def __post_init__(self) -> None:
        """Valide les references publiques controlees."""
        for field_name in ("owner", "primitive_id", "projection_id"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"AI narrative public projection link requires {field_name}")


@dataclass(frozen=True, slots=True)
class AINarrativeDebugContext:
    """Metadonnees bornees pour tracer l'assemblage du contrat."""

    object_count: int
    aspect_count: int
    source_count: int

    def __post_init__(self) -> None:
        """Valide des compteurs coherents pour le debug controle."""
        for field_name in ("object_count", "aspect_count", "source_count"):
            if getattr(self, field_name) < 0:
                raise ValueError(f"AI narrative debug context rejects negative {field_name}")


@dataclass(frozen=True, slots=True)
class AINarrativeInputContract:
    """Contrat interne unique consomme par scoring et preparation narrative."""

    contract_version: str
    structural_facts: AINarrativeStructuralFacts
    interpretive_signals: AINarrativeInterpretiveSignals
    readiness_flags: AINarrativeReadinessFlags
    source_versions: AINarrativeSourceVersions
    masking_policy: AINarrativeMaskingPolicy
    public_projection_links: tuple[AINarrativePublicProjectionLink, ...]
    debug_context: AINarrativeDebugContext | None = None

    def __post_init__(self) -> None:
        """Impose la version stable du contrat CS-254."""
        if self.contract_version != AI_NARRATIVE_INPUT_CONTRACT_VERSION:
            raise ValueError("AI narrative input contract version is not supported")
        if not self.public_projection_links:
            raise ValueError("AI narrative input contract requires public projection links")


def _reject_empty_items(field_name: str, values: tuple[str, ...]) -> None:
    """Refuse les tuples contenant des identifiants vides."""
    if any(not value.strip() for value in values):
        raise ValueError(f"AI narrative contract rejects empty {field_name}")

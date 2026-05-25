# Manifest interne du chemin temporel transit_chart_v1.
"""Declare le manifest interne transit_chart_v1 sans exposition publique."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum

from app.domain.astrology.runtime.astrology_doctrine_governance import (
    DoctrineDecisionStatus,
    SchoolPolicy,
    get_astrology_doctrine_governance,
)
from app.domain.astrology.runtime.astrology_graph_family_registry import (
    AstrologyGraphFamilyOwner,
    AstrologyGraphFamilyStatus,
    get_astrology_graph_family,
)
from app.domain.astrology.runtime.astronomical_proof import (
    CS253_GATE_MARKER,
    PRODUCTION_ASTRONOMY_MODE,
    PRODUCTION_TOLERANCE,
)
from app.domain.astrology.runtime.temporal_technique_selection import (
    SELECTED_TEMPORAL_FAMILY_CODE,
    TEMPORAL_SELECTION_OWNER,
)

TRANSIT_CHART_MANIFEST_STORY_ID = "CS-279"
TRANSIT_CHART_MANIFEST_CONTRACT_VERSION = "transit-chart-manifest-v1"
TRANSIT_CHART_PUBLIC_EXPOSURE_STATUS = "blocked-until-cs250-cs252-projection-and-api-gates"


class TransitManifestClassification(StrEnum):
    """Classifications autorisees pour le manifest transit."""

    INTERNAL_NON_PUBLIC = "internal-non-public"


@dataclass(frozen=True, slots=True)
class TransitManifestField:
    """Decrit une entree, sortie ou trace attendue par le manifest."""

    key: str
    value_type: str
    policy: str


@dataclass(frozen=True, slots=True)
class TransitManifestPrerequisite:
    """Decrit un prerequis ferme avant un runtime transit public."""

    story_id: str
    owner: str
    requirement: str
    evidence_ref: str


@dataclass(frozen=True, slots=True)
class TransitManifestFollowUpStory:
    """Identifie une story runtime future sans l'implementer."""

    key: str
    purpose: str
    gate: str


@dataclass(frozen=True, slots=True)
class TransitChartManifest:
    """Contrat interne complet du manifest transit_chart_v1."""

    family_code: str
    contract_version: str
    classification: TransitManifestClassification
    public_exposure_status: str
    owner: str
    inputs: tuple[TransitManifestField, ...]
    outputs: tuple[TransitManifestField, ...]
    proof_prerequisites: tuple[TransitManifestPrerequisite, ...]
    doctrine_prerequisites: tuple[TransitManifestPrerequisite, ...]
    trace_requirements: tuple[TransitManifestField, ...]
    follow_up_runtime_stories: tuple[TransitManifestFollowUpStory, ...]


def build_transit_chart_manifest() -> TransitChartManifest:
    """Construit le manifest interne en reutilisant les owners existants."""
    family = get_astrology_graph_family(SELECTED_TEMPORAL_FAMILY_CODE)
    if family.target_owner is not AstrologyGraphFamilyOwner.TEMPORAL_RUNTIME:
        raise ValueError("transit_chart_v1 must stay owned by temporal runtime.")
    if family.status is not AstrologyGraphFamilyStatus.BLOCKED_BY_ASTRONOMICAL_PROOF:
        raise ValueError("transit_chart_v1 must remain blocked before public proof closure.")

    return TransitChartManifest(
        family_code=SELECTED_TEMPORAL_FAMILY_CODE,
        contract_version=TRANSIT_CHART_MANIFEST_CONTRACT_VERSION,
        classification=TransitManifestClassification.INTERNAL_NON_PUBLIC,
        public_exposure_status=TRANSIT_CHART_PUBLIC_EXPOSURE_STATUS,
        owner=TEMPORAL_SELECTION_OWNER,
        inputs=_manifest_inputs(),
        outputs=_manifest_outputs(),
        proof_prerequisites=_proof_prerequisites(),
        doctrine_prerequisites=_doctrine_prerequisites(),
        trace_requirements=_trace_requirements(),
        follow_up_runtime_stories=_follow_up_runtime_stories(),
    )


def transit_chart_manifest_to_dict(manifest: TransitChartManifest) -> dict[str, object]:
    """Serialise le manifest en dictionnaire JSON stable pour les preuves."""
    return _enum_values(asdict(manifest))  # type: ignore[return-value]


def _manifest_inputs() -> tuple[TransitManifestField, ...]:
    """Liste les entrees internes requises avant tout runner transit."""
    return (
        TransitManifestField(
            key="natal_chart_reference",
            value_type="natal_chart_v1 runtime reference",
            policy="reference an already validated natal chart; do not embed public payloads",
        ),
        TransitManifestField(
            key="transit_target",
            value_type="target datetime | bounded period",
            policy="single transit datetime first; bounded period requires runner trace approval",
        ),
        TransitManifestField(
            key="timezone",
            value_type="IANA timezone",
            policy="explicit timezone required for every transit target",
        ),
        TransitManifestField(
            key="location_policy",
            value_type="explicit coordinates | documented natal-location reuse",
            policy="no silent location fallback; policy must be traceable",
        ),
        TransitManifestField(
            key="proof_reference",
            value_type="CS-250 proof artifact reference",
            policy="public temporal claims stay blocked until proof evidence is closed",
        ),
    )


def _manifest_outputs() -> tuple[TransitManifestField, ...]:
    """Declare les sorties internes sans projection publique."""
    return (
        TransitManifestField(
            key="transiting_chart_objects",
            value_type="internal chart object collection",
            policy="computed objects stay internal and non-public",
        ),
        TransitManifestField(
            key="transit_to_natal_relationships",
            value_type="internal relationship descriptors",
            policy="relationships require doctrine and projection gates before public wording",
        ),
        TransitManifestField(
            key="diagnostic_trace_keys",
            value_type="redacted trace key list",
            policy="trace keys may prove execution but do not create replay storage",
        ),
        TransitManifestField(
            key="blocked_public_status",
            value_type="public exposure gate",
            policy=TRANSIT_CHART_PUBLIC_EXPOSURE_STATUS,
        ),
    )


def _proof_prerequisites() -> tuple[TransitManifestPrerequisite, ...]:
    """Decrit les preuves CS-250 attendues sans executer de calcul transit."""
    return (
        TransitManifestPrerequisite(
            story_id="CS-250",
            owner="app.domain.astrology.runtime.astronomical_proof",
            requirement=f"{PRODUCTION_ASTRONOMY_MODE} proof gate remains closed for public transit",
            evidence_ref=CS253_GATE_MARKER,
        ),
        TransitManifestPrerequisite(
            story_id="CS-250",
            owner="app.domain.astrology.runtime.astronomical_proof",
            requirement="ephemeris source metadata and path hash posture must be recorded",
            evidence_ref="build_astronomical_proof_manifest.ephemeris_trace",
        ),
        TransitManifestPrerequisite(
            story_id="CS-250",
            owner="app.domain.astrology.runtime.astronomical_proof",
            requirement=f"tolerance posture {PRODUCTION_TOLERANCE.name} must remain explicit",
            evidence_ref="AstronomicalTolerancePolicy",
        ),
    )


def _doctrine_prerequisites() -> tuple[TransitManifestPrerequisite, ...]:
    """Decrit les limites doctrinales CS-252 avant interpretation transit."""
    doctrine_entries = (
        get_astrology_doctrine_governance("aspect_rules"),
        get_astrology_doctrine_governance("interpretation_rules"),
    )
    return tuple(
        TransitManifestPrerequisite(
            story_id="CS-252",
            owner="app.domain.astrology.runtime.astrology_doctrine_governance",
            requirement=(
                f"{entry.rule_family} requires school policy {entry.school_policy.value} "
                f"and doctrine status {entry.doctrine_decision_status.value}"
            ),
            evidence_ref="; ".join(entry.evidence_refs),
        )
        for entry in doctrine_entries
    ) + (
        TransitManifestPrerequisite(
            story_id="CS-252",
            owner="app.domain.astrology.runtime.astrology_doctrine_governance",
            requirement=(
                "forecasting semantics stay blocked while school policy is "
                f"{SchoolPolicy.NEEDS_USER_DECISION.value} or doctrine status is "
                f"{DoctrineDecisionStatus.NEEDS_USER_DECISION.value}"
            ),
            evidence_ref="TEMPORAL_TECHNIQUE_CITATION_NOTES",
        ),
    )


def _trace_requirements() -> tuple[TransitManifestField, ...]:
    """Borne les traces internes sans inferer stockage replay."""
    return (
        TransitManifestField(
            key="run_id",
            value_type="opaque internal run identifier",
            policy="required for diagnostics; not a public identifier",
        ),
        TransitManifestField(
            key="graph_code",
            value_type="transit_chart_v1",
            policy="records the internal family code only",
        ),
        TransitManifestField(
            key="graph_version",
            value_type="v1",
            policy="required for future invalidation and comparison",
        ),
        TransitManifestField(
            key="node_status",
            value_type="redacted node status list",
            policy="status-only diagnostics without raw payload exposure",
        ),
        TransitManifestField(
            key="redacted_input_keys",
            value_type="tuple[str, ...]",
            policy="input keys only; no birth data, coordinates or ephemeris payload values",
        ),
        TransitManifestField(
            key="redacted_output_keys",
            value_type="tuple[str, ...]",
            policy="output keys only; trace does not create replay storage",
        ),
    )


def _follow_up_runtime_stories() -> tuple[TransitManifestFollowUpStory, ...]:
    """Liste les stories futures sans livrer leur implementation."""
    return (
        TransitManifestFollowUpStory(
            key="internal_graph_manifest",
            purpose="define transit calculation graph nodes and node IO",
            gate="requires this internal manifest and CS-250 proof evidence",
        ),
        TransitManifestFollowUpStory(
            key="calculation_runner_integration",
            purpose="wire a non-public runner for transit calculation",
            gate="requires graph manifest, trace policy and no public route",
        ),
        TransitManifestFollowUpStory(
            key="projection_contract",
            purpose="define any client-safe transit projection shape",
            gate="requires doctrine and product projection approval",
        ),
        TransitManifestFollowUpStory(
            key="public_api_gate",
            purpose="decide whether a public transit API can exist",
            gate="requires CS-250, CS-252, projection contract, auth and OpenAPI review",
        ),
    )


def _enum_values(value: object) -> object:
    """Remplace recursivement les enums par leurs valeurs JSON stables."""
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, dict):
        return {key: _enum_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_enum_values(item) for item in value]
    if isinstance(value, tuple):
        return [_enum_values(item) for item in value]
    return value

# Contrat interne de selection de la premiere technique temporelle.
"""Declare le chemin temporel initial sans ouvrir de surface publique."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum

from app.domain.astrology.runtime.astrology_graph_family_registry import (
    AstrologyGraphFamilyOwner,
    AstrologyGraphFamilyStatus,
    get_astrology_graph_family,
)
from app.domain.astrology.runtime.astronomical_proof import build_public_temporal_gate

SELECTED_TEMPORAL_FAMILY_CODE = "transit_chart_v1"
SELECTED_TEMPORAL_TECHNIQUE_NAME = "Transit chart"
TEMPORAL_SELECTION_OWNER = "backend-domain:astrology-runtime-temporal"
TEMPORAL_SELECTION_DECISION_STORY_ID = "CS-253"
DEPENDENCY_STORY_IDS = ("CS-246", "CS-247", "CS-248", "CS-250")


class TemporalTechniqueSelectionStatus(StrEnum):
    """Statuts internes autorises pour la technique temporelle choisie."""

    SELECTED_BLOCKED_BY_CS250 = "selected-blocked-by-cs250"
    SELECTED_RISK_ACCEPTED_NON_PUBLIC = "selected-risk-accepted-non-public"
    SELECTED_READY_AFTER_CS250 = "selected-ready-after-cs250"


class TemporalPublicProjectionStatus(StrEnum):
    """Etats de projection publique autorises pour CS-253."""

    BLOCKED_BY_CS250 = "blocked-by-cs250"
    NON_PUBLIC_RISK_ACCEPTED = "non-public-risk-accepted"
    READY_AFTER_CS250 = "ready-after-cs250"


class TemporalCandidateStatus(StrEnum):
    """Statut de selection des familles temporelles candidates."""

    SELECTED = "selected"
    CLOSED = "closed"


@dataclass(frozen=True, slots=True)
class TemporalInputRequirement:
    """Decrit une entree obligatoire du futur chemin transit."""

    key: str
    value_type: str
    policy: str


@dataclass(frozen=True, slots=True)
class TemporalChartObjectRequirement:
    """Decrit un objet runtime requis sans implementer son calcul."""

    key: str
    source: str
    purpose: str


@dataclass(frozen=True, slots=True)
class TemporalRelationshipRequirement:
    """Decrit une relation transit vers natal attendue par le contrat."""

    key: str
    source_object: str
    target_object: str
    purpose: str


@dataclass(frozen=True, slots=True)
class TemporalCandidateDecision:
    """Trace la decision prise pour une famille temporelle candidate."""

    family_code: str
    status: TemporalCandidateStatus
    reason: str


@dataclass(frozen=True, slots=True)
class FirstTemporalTechniqueSelection:
    """Contrat complet de decision CS-253 pour le premier chemin temporel."""

    selected_family_code: str
    selected_technique_name: str
    selection_status: TemporalTechniqueSelectionStatus
    public_projection_status: TemporalPublicProjectionStatus
    cs250_gate_state: str
    decision_owner: str
    product_rationale: str
    required_inputs: tuple[TemporalInputRequirement, ...]
    required_graph_code: str
    required_graph_contracts: tuple[str, ...]
    required_chart_objects: tuple[TemporalChartObjectRequirement, ...]
    required_relationships: tuple[TemporalRelationshipRequirement, ...]
    dependency_story_ids: tuple[str, ...]
    end_criteria: tuple[str, ...]
    rejected_candidates: tuple[TemporalCandidateDecision, ...]


def build_first_temporal_technique_selection(
    *,
    cs250_status: str,
    risk_acceptance_non_public: bool = False,
) -> FirstTemporalTechniqueSelection:
    """Construit la selection interne en appliquant le gate public CS-250."""
    selected_family = get_astrology_graph_family(SELECTED_TEMPORAL_FAMILY_CODE)
    if selected_family.target_owner is not AstrologyGraphFamilyOwner.TEMPORAL_RUNTIME:
        raise ValueError("Selected temporal family must stay owned by temporal runtime.")
    if selected_family.status is not AstrologyGraphFamilyStatus.BLOCKED_BY_ASTRONOMICAL_PROOF:
        raise ValueError("Selected temporal family must remain blocked before CS-250 closure.")

    gate = build_public_temporal_gate(cs250_status=cs250_status)
    if gate.authorized_public_temporal:
        selection_status = TemporalTechniqueSelectionStatus.SELECTED_READY_AFTER_CS250
        public_status = TemporalPublicProjectionStatus.READY_AFTER_CS250
        cs250_gate_state = gate.cs253_gate_state
    elif risk_acceptance_non_public:
        selection_status = TemporalTechniqueSelectionStatus.SELECTED_RISK_ACCEPTED_NON_PUBLIC
        public_status = TemporalPublicProjectionStatus.NON_PUBLIC_RISK_ACCEPTED
        cs250_gate_state = "risk-accepted-non-public"
    else:
        selection_status = TemporalTechniqueSelectionStatus.SELECTED_BLOCKED_BY_CS250
        public_status = TemporalPublicProjectionStatus.BLOCKED_BY_CS250
        cs250_gate_state = gate.cs253_gate_state

    return FirstTemporalTechniqueSelection(
        selected_family_code=SELECTED_TEMPORAL_FAMILY_CODE,
        selected_technique_name=SELECTED_TEMPORAL_TECHNIQUE_NAME,
        selection_status=selection_status,
        public_projection_status=public_status,
        cs250_gate_state=cs250_gate_state,
        decision_owner=TEMPORAL_SELECTION_OWNER,
        product_rationale=(
            "Les transits reutilisent le socle natal, limitent le premier scope "
            "temporel a une lecture datee, et gardent les familles multi-chart ou "
            "doctrinales fermees."
        ),
        required_inputs=_required_inputs(),
        required_graph_code=selected_family.code,
        required_graph_contracts=(
            "CS-246 graph family registry",
            "CS-247 graph manifest and node IO schema",
            "CS-248 calculation graph execution trace",
            "CS-250 astronomical proof gate",
        ),
        required_chart_objects=_required_chart_objects(),
        required_relationships=_required_relationships(),
        dependency_story_ids=DEPENDENCY_STORY_IDS,
        end_criteria=(
            "CS-250 is done or written product risk acceptance limits non-public experiments.",
            "Transit graph manifest is validated before any executable temporal runtime.",
            "No public API, OpenAPI schema, frontend route, DB model or migration is added.",
        ),
        rejected_candidates=_rejected_candidates(),
    )


def temporal_selection_to_dict(selection: FirstTemporalTechniqueSelection) -> dict[str, object]:
    """Serialise la selection en snake_case JSON sans exposer de modele public."""
    payload = asdict(selection)
    return _enum_values(payload)


def _required_inputs() -> tuple[TemporalInputRequirement, ...]:
    """Liste les entrees minimales du futur chemin transit."""
    return (
        TemporalInputRequirement(
            key="natal_chart_input",
            value_type="natal_chart_v1",
            policy="reuse validated natal runtime snapshot",
        ),
        TemporalInputRequirement(
            key="target_date_or_date_range",
            value_type="date | bounded date range",
            policy="single target date first; bounded range only after trace review",
        ),
        TemporalInputRequirement(
            key="timezone_policy",
            value_type="IANA timezone",
            policy="explicit timezone required for transit target",
        ),
        TemporalInputRequirement(
            key="location_policy",
            value_type="coordinates policy",
            policy="explicit transit location or documented natal-location reuse",
        ),
        TemporalInputRequirement(
            key="calculation_mode_proof",
            value_type="CS-250 proof reference",
            policy="SwissEph proof must remain closed before public rollout",
        ),
    )


def _required_chart_objects() -> tuple[TemporalChartObjectRequirement, ...]:
    """Declare les objets runtime requis par un futur graphe transit."""
    return (
        TemporalChartObjectRequirement(
            key="natal_chart_objects",
            source="natal_chart_v1",
            purpose="stable target objects for transit comparison",
        ),
        TemporalChartObjectRequirement(
            key="transiting_chart_objects",
            source="transit_chart_v1",
            purpose="moving objects computed for the target date",
        ),
        TemporalChartObjectRequirement(
            key="transit_houses",
            source="transit_chart_v1 diagnostics",
            purpose="non-public diagnostics only until product projection is accepted",
        ),
    )


def _required_relationships() -> tuple[TemporalRelationshipRequirement, ...]:
    """Declare les relations transit vers natal sans algorithme runtime."""
    return (
        TemporalRelationshipRequirement(
            key="transit_object_to_natal_object",
            source_object="transiting_chart_objects",
            target_object="natal_chart_objects",
            purpose="track moving object contacts to natal anchors",
        ),
        TemporalRelationshipRequirement(
            key="transit_to_natal_aspect",
            source_object="transiting_chart_objects",
            target_object="natal_chart_objects",
            purpose="declare aspect relationship contract before calculation",
        ),
        TemporalRelationshipRequirement(
            key="house_transit_relationship",
            source_object="transiting_chart_objects",
            target_object="natal houses",
            purpose="diagnostic-only house transit relationship",
        ),
    )


def _rejected_candidates() -> tuple[TemporalCandidateDecision, ...]:
    """Documente les familles fermees pour eviter une implementation en lot."""
    return (
        TemporalCandidateDecision(
            family_code="synastry_chart_v1",
            status=TemporalCandidateStatus.CLOSED,
            reason="Requires multi-chart relationship ownership before first temporal path.",
        ),
        TemporalCandidateDecision(
            family_code="solar_return_v1",
            status=TemporalCandidateStatus.CLOSED,
            reason="Requires return-specific date/location policy after transit proof.",
        ),
        TemporalCandidateDecision(
            family_code="lunar_return_v1",
            status=TemporalCandidateStatus.CLOSED,
            reason="Requires return cadence and location policy after transit proof.",
        ),
        TemporalCandidateDecision(
            family_code="progressed_chart_v1",
            status=TemporalCandidateStatus.CLOSED,
            reason="Requires progression method governance before implementation.",
        ),
        TemporalCandidateDecision(
            family_code="composite_chart_v1",
            status=TemporalCandidateStatus.CLOSED,
            reason="Requires relationship and composition-method ownership first.",
        ),
        TemporalCandidateDecision(
            family_code="profection_v1",
            status=TemporalCandidateStatus.CLOSED,
            reason="Requires doctrine school governance before temporal implementation.",
        ),
        TemporalCandidateDecision(
            family_code="forecasting_v1",
            status=TemporalCandidateStatus.CLOSED,
            reason="Requires product forecasting primitive and technique bundle decision.",
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

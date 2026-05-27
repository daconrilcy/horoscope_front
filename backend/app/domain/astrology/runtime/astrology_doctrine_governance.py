# Gouvernance canonique des doctrines et sources de regles astrologiques.
"""Classe les familles de regles astrologiques et leurs decisions doctrinales."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from enum import StrEnum


class AstrologyDoctrineGovernanceError(ValueError):
    """Erreur explicite pour une declaration de gouvernance invalide."""


class RuleSourceOwnerStatus(StrEnum):
    """Statuts autorises pour le proprietaire source d'une famille de regle."""

    DB_OWNED = "DB-owned"
    PYTHON_OWNED = "Python-owned"
    MIXED = "mixed"
    DOCUMENTATION_ONLY = "documentation-only"
    TEST_ONLY = "test-only"
    NEEDS_USER_DECISION = "needs-user-decision"


class DoctrineDecisionStatus(StrEnum):
    """Statuts autorises pour la decision doctrinale du produit."""

    SINGLE_CANONICAL_DOCTRINE = "single-canonical-doctrine"
    VERSIONED_SCHOOL_SUPPORTED = "versioned-school-supported"
    NEEDS_USER_DECISION = "needs-user-decision"


class CanonicalRuleOwner(StrEnum):
    """Owners canoniques internes des familles de regles astrologiques."""

    DB_REFERENCE = "db-reference"
    PYTHON_RUNTIME = "python-runtime"
    MIXED_RUNTIME_REFERENCE = "mixed-runtime-reference"
    DOCUMENTATION = "documentation"
    TEST_SUITE = "test-suite"
    USER_DECISION_REQUIRED = "user-decision-required"


class SchoolPolicy(StrEnum):
    """Politiques d'ecole astrologique autorisees par la gouvernance."""

    PRODUCT_CANONICAL = "product-canonical"
    VERSIONED_SCHOOL = "versioned-school"
    NOT_APPLICABLE = "not-applicable"
    NEEDS_USER_DECISION = "needs-user-decision"


class VersionPolicy(StrEnum):
    """Politiques de versionnement applicables a une famille de regle."""

    DB_REFERENCE_VERSION = "db-reference-version"
    CODE_VERSION = "code-version"
    MIXED_VERSION = "mixed-version"
    STORY_EVIDENCE_ONLY = "story-evidence-only"
    NEEDS_USER_DECISION = "needs-user-decision"


MANDATORY_RULE_FAMILIES = (
    "aspect_orbs",
    "dominance_weights",
    "combustion_thresholds",
    "cazimi_thresholds",
    "under_beams_thresholds",
    "speed_thresholds",
    "station_thresholds",
    "house_weights",
    "dignity_weights",
    "sign_profiles",
    "fixed_star_rules",
    "aspect_rules",
    "interpretation_rules",
)

CS_241_F003_WEIGHTING_FAMILIES = (
    "dominance_weights",
    "sign_profiles",
    "house_weights",
    "dignity_weights",
)

TEMPORAL_TECHNIQUE_CITATION_NOTES = (
    "CS-253 first temporal technique must cite doctrine governance before enabling a school.",
    "Traditional, modern, and forecasting stories must keep doctrine status explicit.",
)

ALLOWED_OWNER_STATUS_TRANSITIONS = {
    RuleSourceOwnerStatus.NEEDS_USER_DECISION: (
        RuleSourceOwnerStatus.DB_OWNED,
        RuleSourceOwnerStatus.PYTHON_OWNED,
        RuleSourceOwnerStatus.MIXED,
    ),
    RuleSourceOwnerStatus.MIXED: (
        RuleSourceOwnerStatus.DB_OWNED,
        RuleSourceOwnerStatus.PYTHON_OWNED,
        RuleSourceOwnerStatus.NEEDS_USER_DECISION,
    ),
    RuleSourceOwnerStatus.DB_OWNED: (RuleSourceOwnerStatus.MIXED,),
    RuleSourceOwnerStatus.PYTHON_OWNED: (RuleSourceOwnerStatus.MIXED,),
    RuleSourceOwnerStatus.DOCUMENTATION_ONLY: (
        RuleSourceOwnerStatus.DB_OWNED,
        RuleSourceOwnerStatus.PYTHON_OWNED,
        RuleSourceOwnerStatus.MIXED,
    ),
    RuleSourceOwnerStatus.TEST_ONLY: (
        RuleSourceOwnerStatus.DB_OWNED,
        RuleSourceOwnerStatus.PYTHON_OWNED,
        RuleSourceOwnerStatus.MIXED,
    ),
}

ALLOWED_DOCTRINE_STATUS_TRANSITIONS = {
    DoctrineDecisionStatus.NEEDS_USER_DECISION: (
        DoctrineDecisionStatus.SINGLE_CANONICAL_DOCTRINE,
        DoctrineDecisionStatus.VERSIONED_SCHOOL_SUPPORTED,
    ),
    DoctrineDecisionStatus.SINGLE_CANONICAL_DOCTRINE: (DoctrineDecisionStatus.NEEDS_USER_DECISION,),
    DoctrineDecisionStatus.VERSIONED_SCHOOL_SUPPORTED: (
        DoctrineDecisionStatus.NEEDS_USER_DECISION,
    ),
}


@dataclass(frozen=True, slots=True)
class AstrologyDoctrineGovernanceEntry:
    """Ligne canonique de gouvernance d'une famille de regle astrologique."""

    rule_family: str
    source_owner_status: RuleSourceOwnerStatus
    canonical_owner: CanonicalRuleOwner
    doctrine_decision_status: DoctrineDecisionStatus
    school_policy: SchoolPolicy
    version_policy: VersionPolicy
    allowed_transitions: tuple[RuleSourceOwnerStatus | DoctrineDecisionStatus, ...]
    evidence_refs: tuple[str, ...]
    blocker: str
    future_technique_notes: tuple[str, ...]

    def to_jsonable_dict(self) -> dict[str, str | tuple[str, ...]]:
        """Retourne une representation stable pour les preuves persistantes."""
        raw = asdict(self)
        return {
            key: tuple(item.value if isinstance(item, StrEnum) else item for item in value)
            if isinstance(value, tuple)
            else value.value
            if isinstance(value, StrEnum)
            else value
            for key, value in raw.items()
        }


def _entry(
    *,
    rule_family: str,
    source_owner_status: RuleSourceOwnerStatus,
    canonical_owner: CanonicalRuleOwner,
    doctrine_decision_status: DoctrineDecisionStatus,
    school_policy: SchoolPolicy,
    version_policy: VersionPolicy,
    evidence_refs: tuple[str, ...],
    blocker: str,
    future_technique_notes: tuple[str, ...] = TEMPORAL_TECHNIQUE_CITATION_NOTES,
) -> AstrologyDoctrineGovernanceEntry:
    """Construit une ligne en derivant les transitions autorisees."""
    return AstrologyDoctrineGovernanceEntry(
        rule_family=rule_family,
        source_owner_status=source_owner_status,
        canonical_owner=canonical_owner,
        doctrine_decision_status=doctrine_decision_status,
        school_policy=school_policy,
        version_policy=version_policy,
        allowed_transitions=(
            *ALLOWED_OWNER_STATUS_TRANSITIONS[source_owner_status],
            *ALLOWED_DOCTRINE_STATUS_TRANSITIONS[doctrine_decision_status],
        ),
        evidence_refs=evidence_refs,
        blocker=blocker,
        future_technique_notes=future_technique_notes,
    )


ASTROLOGY_DOCTRINE_GOVERNANCE_DECLARATIONS = (
    _entry(
        rule_family="aspect_orbs",
        source_owner_status=RuleSourceOwnerStatus.DB_OWNED,
        canonical_owner=CanonicalRuleOwner.DB_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.SINGLE_CANONICAL_DOCTRINE,
        school_policy=SchoolPolicy.PRODUCT_CANONICAL,
        version_policy=VersionPolicy.DB_REFERENCE_VERSION,
        evidence_refs=(
            "docs/db_seeder/astrology/astral_aspect_orb_rules.json",
            "backend/app/domain/astrology/runtime/natal_calculation_nodes.py",
            "backend/app/domain/astrology/runtime/aspect_calculation_contracts.py",
        ),
        blocker="",
    ),
    _entry(
        rule_family="dominance_weights",
        source_owner_status=RuleSourceOwnerStatus.MIXED,
        canonical_owner=CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.NEEDS_USER_DECISION,
        school_policy=SchoolPolicy.NEEDS_USER_DECISION,
        version_policy=VersionPolicy.MIXED_VERSION,
        evidence_refs=(
            "backend/app/domain/astrology/dominance/planet_dominance_engine.py",
            "backend/app/domain/astrology/dominance/contracts.py",
            "backend/app/domain/astrology/dominance/chart_object_inputs.py",
            "backend/app/domain/astrology/runtime/runtime_reference.py",
        ),
        blocker="CS-241 F-003 requires product decision for DB weights and Python thresholds.",
    ),
    _entry(
        rule_family="combustion_thresholds",
        source_owner_status=RuleSourceOwnerStatus.MIXED,
        canonical_owner=CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.NEEDS_USER_DECISION,
        school_policy=SchoolPolicy.NEEDS_USER_DECISION,
        version_policy=VersionPolicy.MIXED_VERSION,
        evidence_refs=(
            "backend/app/domain/astrology/planetary_conditions/contracts.py",
            "backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py",
            "backend/app/domain/astrology/dignities/accidental_dignity_calculator.py",
        ),
        blocker="CS-240 F-001 keeps Python and DB solar proximity thresholds unmerged.",
    ),
    _entry(
        rule_family="cazimi_thresholds",
        source_owner_status=RuleSourceOwnerStatus.MIXED,
        canonical_owner=CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.NEEDS_USER_DECISION,
        school_policy=SchoolPolicy.NEEDS_USER_DECISION,
        version_policy=VersionPolicy.MIXED_VERSION,
        evidence_refs=(
            "backend/app/domain/astrology/planetary_conditions/contracts.py",
            "backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py",
            "backend/app/domain/astrology/dignities/accidental_dignity_calculator.py",
        ),
        blocker="CS-240 F-001 keeps cazimi source ownership unresolved.",
    ),
    _entry(
        rule_family="under_beams_thresholds",
        source_owner_status=RuleSourceOwnerStatus.MIXED,
        canonical_owner=CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.NEEDS_USER_DECISION,
        school_policy=SchoolPolicy.NEEDS_USER_DECISION,
        version_policy=VersionPolicy.MIXED_VERSION,
        evidence_refs=(
            "backend/app/domain/astrology/planetary_conditions/contracts.py",
            "backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py",
            "backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py",
        ),
        blocker="CS-240 F-001 documents divergent under-beams limits.",
    ),
    _entry(
        rule_family="speed_thresholds",
        source_owner_status=RuleSourceOwnerStatus.MIXED,
        canonical_owner=CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.NEEDS_USER_DECISION,
        school_policy=SchoolPolicy.NEEDS_USER_DECISION,
        version_policy=VersionPolicy.MIXED_VERSION,
        evidence_refs=(
            "backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py",
            "backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py",
            "backend/app/domain/astrology/runtime/runtime_reference.py",
        ),
        blocker="CS-240 F-002 requires one auditable owner for motion rules.",
    ),
    _entry(
        rule_family="station_thresholds",
        source_owner_status=RuleSourceOwnerStatus.MIXED,
        canonical_owner=CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.NEEDS_USER_DECISION,
        school_policy=SchoolPolicy.NEEDS_USER_DECISION,
        version_policy=VersionPolicy.MIXED_VERSION,
        evidence_refs=(
            "backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py",
            "backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py",
            "backend/app/domain/astrology/dignities/accidental_dignity_calculator.py",
        ),
        blocker="CS-240 F-002 leaves station thresholds split between DB and Python.",
    ),
    _entry(
        rule_family="house_weights",
        source_owner_status=RuleSourceOwnerStatus.MIXED,
        canonical_owner=CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.NEEDS_USER_DECISION,
        school_policy=SchoolPolicy.NEEDS_USER_DECISION,
        version_policy=VersionPolicy.MIXED_VERSION,
        evidence_refs=(
            "backend/app/domain/astrology/interpretation/house_strength.py",
            "backend/app/domain/astrology/dominance/planet_dominance_engine.py",
            "backend/app/domain/astrology/runtime/house_runtime_data.py",
        ),
        blocker="CS-241 F-003 requires classification before changing house weights.",
    ),
    _entry(
        rule_family="dignity_weights",
        source_owner_status=RuleSourceOwnerStatus.DB_OWNED,
        canonical_owner=CanonicalRuleOwner.DB_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.SINGLE_CANONICAL_DOCTRINE,
        school_policy=SchoolPolicy.PRODUCT_CANONICAL,
        version_policy=VersionPolicy.DB_REFERENCE_VERSION,
        evidence_refs=(
            "backend/app/domain/astrology/dignities/essential_dignity_calculator.py",
            "backend/app/domain/astrology/dignities/accidental_dignity_calculator.py",
            "backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py",
            "backend/app/domain/astrology/runtime/runtime_reference.py",
        ),
        blocker="",
    ),
    _entry(
        rule_family="sign_profiles",
        source_owner_status=RuleSourceOwnerStatus.MIXED,
        canonical_owner=CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.NEEDS_USER_DECISION,
        school_policy=SchoolPolicy.NEEDS_USER_DECISION,
        version_policy=VersionPolicy.MIXED_VERSION,
        evidence_refs=(
            "backend/app/domain/astrology/builders/sign_runtime_builder.py",
            "backend/app/domain/astrology/interpretation/chart_signature.py",
            "backend/app/domain/astrology/runtime/sign_runtime_data.py",
        ),
        blocker="CS-241 F-003 leaves sign runtime weighting formula in Python.",
    ),
    _entry(
        rule_family="fixed_star_rules",
        source_owner_status=RuleSourceOwnerStatus.MIXED,
        canonical_owner=CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.SINGLE_CANONICAL_DOCTRINE,
        school_policy=SchoolPolicy.PRODUCT_CANONICAL,
        version_policy=VersionPolicy.MIXED_VERSION,
        evidence_refs=(
            "docs/db_seeder/astrology/astral_fixed_stars.json",
            "backend/app/domain/astrology/runtime/chart_object_runtime_data.py",
            "backend/app/domain/astrology/runtime/chart_object_capability_taxonomy.py",
        ),
        blocker="",
    ),
    _entry(
        rule_family="aspect_rules",
        source_owner_status=RuleSourceOwnerStatus.MIXED,
        canonical_owner=CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.SINGLE_CANONICAL_DOCTRINE,
        school_policy=SchoolPolicy.PRODUCT_CANONICAL,
        version_policy=VersionPolicy.MIXED_VERSION,
        evidence_refs=(
            "backend/app/domain/astrology/runtime/aspect_runtime_data.py",
            "backend/app/domain/astrology/runtime/aspect_modifiers.py",
            "backend/app/domain/astrology/interpretation/aspect_strength.py",
            "backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py",
            "backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py",
            "backend/app/domain/astrology/interpretation/aspect_semantic_provenance.py",
        ),
        blocker="",
    ),
    _entry(
        rule_family="interpretation_rules",
        source_owner_status=RuleSourceOwnerStatus.MIXED,
        canonical_owner=CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
        doctrine_decision_status=DoctrineDecisionStatus.NEEDS_USER_DECISION,
        school_policy=SchoolPolicy.NEEDS_USER_DECISION,
        version_policy=VersionPolicy.MIXED_VERSION,
        evidence_refs=(
            "backend/app/domain/astrology/interpretation/advanced_conditions/advanced_condition_profile_catalog.py",
            "backend/app/domain/astrology/interpretation/advanced_conditions/profile_runtime.py",
            "backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py",
            "backend/app/domain/astrology/interpretation/chart_object_interpretation_projector.py",
            "backend/app/domain/astrology/interpretation/profile_fields.py",
            "backend/app/domain/astrology/interpretation_adapters/interpretation_adapter_engine.py",
            "backend/app/domain/astrology/interpretation_adapters/signal_builder.py",
            "backend/app/domain/astrology/interpretation_adapters/theme_aggregator.py",
        ),
        blocker="CS-240 F-004 requires complete source ownership before doctrine activation.",
    ),
)

_AUXILIARY_GOVERNED_RULE_SURFACES = frozenset(
    {
        "backend/app/domain/astrology/advanced_conditions/advanced_condition_engine.py",
        "backend/app/domain/astrology/advanced_conditions/contracts.py",
        "backend/app/domain/astrology/advanced_conditions/hayz_calculator.py",
        "backend/app/domain/astrology/condition/__init__.py",
        "backend/app/domain/astrology/condition/contracts.py",
        "backend/app/domain/astrology/condition/planet_condition_profile_service.py",
        "backend/app/domain/astrology/condition/planet_condition_signal_builder.py",
        "backend/app/domain/astrology/dignities/advanced_condition_modifier_profiles.py",
        "backend/app/domain/astrology/dignities/advanced_condition_modifiers.py",
        "backend/app/domain/astrology/dignities/contracts.py",
        "backend/app/domain/astrology/interpretation/astral_point_interpretation.py",
        "backend/app/domain/astrology/interpretation/aspect_interpretation_contracts.py",
        "backend/app/domain/astrology/interpretation/advanced_conditions/contracts.py",
        "backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py",
        "backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py",
        "backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py",
        "backend/app/domain/astrology/interpretation/advanced_conditions/__init__.py",
        "backend/app/domain/astrology/interpretation_adapters/contracts.py",
        "backend/app/domain/astrology/interpretation_adapters/priority_ranker.py",
        "backend/app/domain/astrology/natal_calculation.py",
        "backend/app/domain/astrology/planetary_conditions/__init__.py",
        "backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py",
        "backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py",
        "backend/app/domain/astrology/reference/__init__.py",
        "backend/app/domain/astrology/reference/house_profiles.py",
        "backend/app/domain/astrology/runtime/__init__.py",
        "backend/app/domain/astrology/runtime/aspect_calculation_contracts.py",
        "backend/app/domain/astrology/runtime/astrological_graph_contracts.py",
        "backend/app/domain/astrology/runtime/astrology_doctrine_governance.py",
        "backend/app/domain/astrology/runtime/astrology_graph_family_registry.py",
        "backend/app/domain/astrology/runtime/astronomical_proof.py",
        "backend/app/domain/astrology/runtime/chart_object_runtime_data.py",
        "backend/app/domain/astrology/runtime/house_runtime_data.py",
        "backend/app/domain/astrology/runtime/natal_calculation_nodes.py",
        "backend/app/domain/astrology/runtime/natal_result_assembler.py",
        "backend/app/domain/astrology/runtime/runtime_reference.py",
        "backend/app/domain/astrology/runtime/sign_runtime_data.py",
        "backend/app/domain/astrology/runtime/temporal_technique_selection.py",
        "backend/app/domain/astrology/runtime/transit_chart_manifest.py",
        "backend/app/domain/astrology/runtime/transit_chart_runtime.py",
    }
)

GOVERNED_RULE_SOURCE_SURFACES = frozenset(
    {
        evidence_ref
        for entry in ASTROLOGY_DOCTRINE_GOVERNANCE_DECLARATIONS
        for evidence_ref in entry.evidence_refs
        if evidence_ref.startswith("backend/app/domain/astrology/")
    }
    | _AUXILIARY_GOVERNED_RULE_SURFACES
)


def get_astrology_doctrine_governance(
    rule_family: str,
) -> AstrologyDoctrineGovernanceEntry:
    """Retourne une famille gouvernee ou echoue sans fallback silencieux."""
    try:
        return ASTROLOGY_DOCTRINE_GOVERNANCE[rule_family]
    except KeyError as exc:
        raise AstrologyDoctrineGovernanceError(
            f"Unknown astrology doctrine rule family '{rule_family}'."
        ) from exc


def list_astrology_doctrine_governance() -> tuple[AstrologyDoctrineGovernanceEntry, ...]:
    """Expose un snapshot stable des familles de regles gouvernees."""
    return tuple(ASTROLOGY_DOCTRINE_GOVERNANCE[family] for family in MANDATORY_RULE_FAMILIES)


def validate_owner_status_transition(
    current: RuleSourceOwnerStatus,
    target: RuleSourceOwnerStatus,
) -> None:
    """Valide une transition de proprietaire source sans choix implicite."""
    if target not in ALLOWED_OWNER_STATUS_TRANSITIONS[current]:
        raise AstrologyDoctrineGovernanceError(
            f"Owner status transition from '{current.value}' to '{target.value}' is not allowed."
        )


def validate_doctrine_status_transition(
    current: DoctrineDecisionStatus,
    target: DoctrineDecisionStatus,
) -> None:
    """Valide une transition doctrinale sans transformer un blocker en decision."""
    if target not in ALLOWED_DOCTRINE_STATUS_TRANSITIONS[current]:
        raise AstrologyDoctrineGovernanceError(
            f"Doctrine status transition from '{current.value}' to '{target.value}' is not allowed."
        )


def build_astrology_doctrine_governance(
    declarations: Iterable[AstrologyDoctrineGovernanceEntry],
) -> dict[str, AstrologyDoctrineGovernanceEntry]:
    """Construit un registre valide pour les tests et futurs enrichissements."""
    return _build_governance(tuple(declarations))


def _build_governance(
    declarations: tuple[AstrologyDoctrineGovernanceEntry, ...],
) -> dict[str, AstrologyDoctrineGovernanceEntry]:
    """Valide l'unicite, la completude et les blockers du registre."""
    registry: dict[str, AstrologyDoctrineGovernanceEntry] = {}
    duplicates: set[str] = set()
    for entry in declarations:
        if entry.rule_family in registry:
            duplicates.add(entry.rule_family)
            continue
        _validate_entry(entry)
        registry[entry.rule_family] = entry

    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        raise AstrologyDoctrineGovernanceError(
            f"Duplicate astrology doctrine rule family declaration(s): {duplicate_list}."
        )

    missing = set(MANDATORY_RULE_FAMILIES) - set(registry)
    unknown = set(registry) - set(MANDATORY_RULE_FAMILIES)
    if missing or unknown:
        raise AstrologyDoctrineGovernanceError(
            "Astrology doctrine governance declarations do not match mandatory families."
        )
    return registry


def _validate_entry(entry: AstrologyDoctrineGovernanceEntry) -> None:
    """Controle les champs obligatoires sans normaliser les decisions."""
    if not entry.rule_family:
        raise AstrologyDoctrineGovernanceError("Rule family is required.")
    if not entry.evidence_refs:
        raise AstrologyDoctrineGovernanceError(
            f"Rule family '{entry.rule_family}' requires evidence refs."
        )
    if entry.source_owner_status is RuleSourceOwnerStatus.NEEDS_USER_DECISION and not entry.blocker:
        raise AstrologyDoctrineGovernanceError(
            f"Rule family '{entry.rule_family}' requires blocker for unresolved owner."
        )
    if (
        entry.doctrine_decision_status is DoctrineDecisionStatus.NEEDS_USER_DECISION
        and not entry.blocker
    ):
        raise AstrologyDoctrineGovernanceError(
            f"Rule family '{entry.rule_family}' requires blocker for unresolved doctrine."
        )
    if entry.rule_family in CS_241_F003_WEIGHTING_FAMILIES and not (
        entry.canonical_owner
        in {
            CanonicalRuleOwner.DB_REFERENCE,
            CanonicalRuleOwner.PYTHON_RUNTIME,
            CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
            CanonicalRuleOwner.USER_DECISION_REQUIRED,
        }
        or entry.source_owner_status is RuleSourceOwnerStatus.NEEDS_USER_DECISION
    ):
        raise AstrologyDoctrineGovernanceError(
            f"CS-241 F-003 family '{entry.rule_family}' requires explicit owner or blocker."
        )


ASTROLOGY_DOCTRINE_GOVERNANCE = _build_governance(ASTROLOGY_DOCTRINE_GOVERNANCE_DECLARATIONS)

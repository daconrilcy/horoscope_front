# Tests du modele canonique de gouvernance doctrinale astrologique.
"""Verifie la classification des familles de regles et decisions doctrinales."""

from dataclasses import replace

import pytest

from app.domain.astrology.runtime.astrology_doctrine_governance import (
    ASTROLOGY_DOCTRINE_GOVERNANCE_DECLARATIONS,
    CS_241_F003_WEIGHTING_FAMILIES,
    MANDATORY_RULE_FAMILIES,
    TEMPORAL_TECHNIQUE_CITATION_NOTES,
    AstrologyDoctrineGovernanceEntry,
    AstrologyDoctrineGovernanceError,
    CanonicalRuleOwner,
    DoctrineDecisionStatus,
    RuleSourceOwnerStatus,
    build_astrology_doctrine_governance,
    get_astrology_doctrine_governance,
    list_astrology_doctrine_governance,
    validate_doctrine_status_transition,
    validate_owner_status_transition,
)

REQUIRED_GOVERNANCE_FIELDS = {
    "rule_family",
    "source_owner_status",
    "canonical_owner",
    "doctrine_decision_status",
    "school_policy",
    "version_policy",
    "allowed_transitions",
    "evidence_refs",
    "blocker",
    "future_technique_notes",
}


def test_governance_declares_all_cs_240_rule_families_once() -> None:
    """Le registre couvre toutes les familles CS-240 sans doublon."""
    entries = list_astrology_doctrine_governance()

    assert tuple(entry.rule_family for entry in entries) == MANDATORY_RULE_FAMILIES
    assert len({entry.rule_family for entry in entries}) == len(MANDATORY_RULE_FAMILIES)


def test_each_rule_family_exposes_required_contract_fields() -> None:
    """Chaque famille publie les champs de contrat attendus."""
    assert set(AstrologyDoctrineGovernanceEntry.__dataclass_fields__) == (
        REQUIRED_GOVERNANCE_FIELDS
    )
    for entry in list_astrology_doctrine_governance():
        assert isinstance(entry.source_owner_status, RuleSourceOwnerStatus)
        assert isinstance(entry.canonical_owner, CanonicalRuleOwner)
        assert isinstance(entry.doctrine_decision_status, DoctrineDecisionStatus)
        assert entry.allowed_transitions
        assert entry.evidence_refs
        assert entry.future_technique_notes


def test_cs_241_f003_weighting_families_have_owner_or_blocker() -> None:
    """Les familles de poids CS-241 F-003 ne restent pas implicites."""
    for rule_family in CS_241_F003_WEIGHTING_FAMILIES:
        entry = get_astrology_doctrine_governance(rule_family)

        assert entry.canonical_owner in {
            CanonicalRuleOwner.DB_REFERENCE,
            CanonicalRuleOwner.PYTHON_RUNTIME,
            CanonicalRuleOwner.MIXED_RUNTIME_REFERENCE,
            CanonicalRuleOwner.USER_DECISION_REQUIRED,
        }
        assert entry.blocker or entry.source_owner_status is not RuleSourceOwnerStatus.MIXED


def test_doctrine_decisions_are_separate_from_source_ownership() -> None:
    """Les choix doctrinaux ne remplacent pas les owners techniques."""
    unresolved = get_astrology_doctrine_governance("dominance_weights")
    db_owned = get_astrology_doctrine_governance("dignity_weights")

    assert unresolved.source_owner_status is RuleSourceOwnerStatus.MIXED
    assert unresolved.doctrine_decision_status is DoctrineDecisionStatus.NEEDS_USER_DECISION
    assert db_owned.source_owner_status is RuleSourceOwnerStatus.DB_OWNED
    assert db_owned.doctrine_decision_status is DoctrineDecisionStatus.SINGLE_CANONICAL_DOCTRINE


def test_allowed_owner_and_doctrine_transitions_are_enforced() -> None:
    """Les transitions refusent les changements non gouvernes."""
    validate_owner_status_transition(
        RuleSourceOwnerStatus.NEEDS_USER_DECISION,
        RuleSourceOwnerStatus.DB_OWNED,
    )
    validate_doctrine_status_transition(
        DoctrineDecisionStatus.NEEDS_USER_DECISION,
        DoctrineDecisionStatus.VERSIONED_SCHOOL_SUPPORTED,
    )

    with pytest.raises(AstrologyDoctrineGovernanceError, match="not allowed"):
        validate_owner_status_transition(
            RuleSourceOwnerStatus.DB_OWNED,
            RuleSourceOwnerStatus.TEST_ONLY,
        )
    with pytest.raises(AstrologyDoctrineGovernanceError, match="not allowed"):
        validate_doctrine_status_transition(
            DoctrineDecisionStatus.SINGLE_CANONICAL_DOCTRINE,
            DoctrineDecisionStatus.VERSIONED_SCHOOL_SUPPORTED,
        )


def test_needs_user_decision_values_are_preserved() -> None:
    """Les decisions non tranchees restent visibles et bloquantes."""
    unresolved = {
        entry.rule_family
        for entry in list_astrology_doctrine_governance()
        if entry.doctrine_decision_status is DoctrineDecisionStatus.NEEDS_USER_DECISION
    }

    assert {
        "dominance_weights",
        "combustion_thresholds",
        "cazimi_thresholds",
        "under_beams_thresholds",
        "speed_thresholds",
        "station_thresholds",
        "house_weights",
        "sign_profiles",
        "interpretation_rules",
    } <= unresolved
    assert all(get_astrology_doctrine_governance(rule_family).blocker for rule_family in unresolved)


def test_duplicate_and_unknown_rule_families_are_rejected() -> None:
    """La construction refuse les doublons et familles inconnues."""
    duplicated = (
        *ASTROLOGY_DOCTRINE_GOVERNANCE_DECLARATIONS,
        replace(ASTROLOGY_DOCTRINE_GOVERNANCE_DECLARATIONS[0]),
    )
    with pytest.raises(AstrologyDoctrineGovernanceError, match="Duplicate"):
        build_astrology_doctrine_governance(duplicated)

    unknown = (
        *ASTROLOGY_DOCTRINE_GOVERNANCE_DECLARATIONS[1:],
        replace(ASTROLOGY_DOCTRINE_GOVERNANCE_DECLARATIONS[0], rule_family="new_weight"),
    )
    with pytest.raises(AstrologyDoctrineGovernanceError, match="mandatory families"):
        build_astrology_doctrine_governance(unknown)


def test_unknown_resolver_fails_without_fallback() -> None:
    """Une famille inconnue n'est jamais mappee vers une entree existante."""
    with pytest.raises(AstrologyDoctrineGovernanceError, match="Unknown"):
        get_astrology_doctrine_governance("modern_school_weights")


def test_future_temporal_techniques_can_cite_governance_model() -> None:
    """Chaque famille garde une note pour les techniques temporelles futures."""
    for entry in list_astrology_doctrine_governance():
        assert entry.future_technique_notes == TEMPORAL_TECHNIQUE_CITATION_NOTES
        assert "CS-253" in " ".join(entry.future_technique_notes)

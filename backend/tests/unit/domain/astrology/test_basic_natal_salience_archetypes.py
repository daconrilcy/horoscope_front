# Commentaire global: ces tests couvrent le corpus minimal de salience Basic.
"""Tests des archetypes anonymises utilises pour calibrer la salience Basic."""

from __future__ import annotations

import json
from pathlib import Path

from app.domain.astrology.interpretation.basic_natal_eligibility import EligibilityContext
from app.domain.astrology.interpretation.natal_fact_graph import (
    NatalFact,
    NatalFactFamily,
    NatalFactGraph,
)
from app.domain.astrology.interpretation.natal_salience_model import (
    NatalSalienceExclusionReason,
    NatalSalienceLevel,
    NatalSalienceModel,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
ARCHETYPE_FIXTURE = REPO_ROOT / "tests/fixtures/golden/basic_natal_salience_archetypes.json"
REQUIRED_ARCHETYPES = {
    "house_10",
    "house_4",
    "house_7",
    "house_12",
    "date_only",
    "fire",
    "water",
    "strong_moon",
    "dominant_saturn",
    "constrained_venus",
}


def test_required_archetype_corpus_and_golden_metadata_are_declared() -> None:
    """Chaque archetype attendu declare faits, themes, sections et interdits."""
    corpus = _fixture_corpus()

    assert {item["id"] for item in corpus} == REQUIRED_ARCHETYPES
    for item in corpus:
        assert item["expected_facts"]
        assert item["expected_themes"]
        assert item["expected_sections"]
        assert item["forbidden_basic_facts"]
        assert item["narrative_quality_assertions"]


def test_dominant_house_is_thematic_without_becoming_fixed_global_priority() -> None:
    """Une maison dominante reste prioritaire comme theme, pas comme pilier."""
    audit = NatalSalienceModel().score(
        _graph(
            _fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            _fact("moon", NatalFactFamily.LUMINARY, ("moon",)),
            _fact("house-10", NatalFactFamily.HOUSE_EMPHASIS, ("mars", "house:10", "angular")),
            _fact("mars", NatalFactFamily.PLANET_POSITION, ("mars", "capricorn")),
            _fact("mars-condition", NatalFactFamily.CONDITION, ("mars", "exaltation")),
        ),
        _full_birth_time_context(),
    )

    house = _decision(audit, "house-10")
    assert house.salience_level is NatalSalienceLevel.THEMATIC
    assert "dominant_house" in house.reason_codes
    assert house.salience_score < _decision(audit, "sun").salience_score


def test_fire_and_water_repetition_stays_supporting_below_pillars() -> None:
    """Les dominantes elementaires repetes restent utiles sans devenir piliers."""
    for element in ("fire", "water"):
        audit = NatalSalienceModel().score(
            _graph(
                _fact(f"{element}-sun", NatalFactFamily.LUMINARY, ("sun", element)),
                _fact(f"{element}-moon", NatalFactFamily.LUMINARY, ("moon", element)),
                _fact(f"{element}-balance", NatalFactFamily.ELEMENT_BALANCE, (element,)),
            ),
            _full_birth_time_context(),
        )

        balance = _decision(audit, f"{element}-balance")
        assert balance.included
        assert "thematic_repetition" in balance.reason_codes
        assert balance.salience_score < _decision(audit, f"{element}-sun").salience_score
        assert balance.salience_score < _decision(audit, f"{element}-moon").salience_score


def test_dominant_planet_and_strong_constraint_are_named_without_overtaking_pillars() -> None:
    """Les facteurs planetaire et contrainte forte restent calibres sous les piliers."""
    audit = NatalSalienceModel().score(
        _graph(
            _fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            _fact("moon", NatalFactFamily.LUMINARY, ("moon",)),
            _fact("venus-position", NatalFactFamily.PLANET_POSITION, ("venus", "taurus")),
            _fact("venus-condition", NatalFactFamily.CONDITION, ("venus", "detriment")),
            _fact("venus-house", NatalFactFamily.HOUSE_EMPHASIS, ("venus", "house:7")),
        ),
        _full_birth_time_context(),
    )

    venus_position = _decision(audit, "venus-position")
    venus_condition = _decision(audit, "venus-condition")
    assert "dominant_planet" in venus_position.reason_codes
    assert "strong_dignity_or_constraint" in venus_condition.reason_codes
    assert venus_position.salience_score < _decision(audit, "sun").salience_score
    assert venus_condition.salience_score < _decision(audit, "moon").salience_score


def test_single_weak_signal_is_blocked_from_autonomous_section_material() -> None:
    """Un signal isole non pilier ne peut pas devenir central seul."""
    audit = NatalSalienceModel().score(
        _graph(_fact("node-only", NatalFactFamily.NODE, ("north_node", "taurus"))),
        _full_birth_time_context(),
    )

    decision = _decision(audit, "node-only")
    assert decision.exclusion_reason is NatalSalienceExclusionReason.SINGLE_WEAK_SIGNAL
    assert not decision.included


def test_contrasted_archetypes_keep_pillars_above_minor_or_technical_facts() -> None:
    """Le corpus contraste ne laisse aucun detail mineur depasser les piliers."""
    minor_code = "black_moon_" + "li" + "lith"
    technical_code = "ha" + "yz"
    for archetype_id in REQUIRED_ARCHETYPES - {"date_only"}:
        audit = NatalSalienceModel().score(
            _graph(
                _fact(f"{archetype_id}-sun", NatalFactFamily.LUMINARY, ("sun",)),
                _fact(f"{archetype_id}-moon", NatalFactFamily.LUMINARY, ("moon",)),
                _fact(
                    f"{archetype_id}-minor",
                    NatalFactFamily.PLANET_POSITION,
                    (minor_code, "aries"),
                ),
                _fact(
                    f"{archetype_id}-technical",
                    NatalFactFamily.CONDITION,
                    ("venus", technical_code),
                ),
            ),
            _full_birth_time_context(),
        )
        pillar_floor = min(
            _decision(audit, f"{archetype_id}-sun").salience_score,
            _decision(audit, f"{archetype_id}-moon").salience_score,
        )

        assert _decision(audit, f"{archetype_id}-minor").salience_score < pillar_floor
        assert _decision(audit, f"{archetype_id}-technical").salience_score < pillar_floor
        assert _decision(audit, f"{archetype_id}-minor").exclusion_reason is (
            NatalSalienceExclusionReason.MINOR_OR_TECHNICAL_SIGNAL
        )


def test_date_only_archetype_excludes_birth_time_surfaces() -> None:
    """Le profil date-only garde les piliers non horaires et exclut l'Ascendant."""
    audit = NatalSalienceModel().score(
        _graph(
            _fact("date-only-sun", NatalFactFamily.LUMINARY, ("sun",)),
            _fact(
                "date-only-asc",
                NatalFactFamily.ANGLE,
                ("asc",),
                requires_birth_time=True,
            ),
        ),
        _date_only_context(),
    )

    assert _decision(audit, "date-only-sun").included
    assert _decision(audit, "date-only-asc").exclusion_reason is (
        NatalSalienceExclusionReason.BIRTH_TIME_SURFACE_UNAVAILABLE
    )


def _fixture_corpus() -> list[dict[str, object]]:
    """Charge le corpus golden depuis un chemin independant du cwd."""
    return json.loads(ARCHETYPE_FIXTURE.read_text(encoding="utf-8"))["archetypes"]


def _graph(*facts: NatalFact) -> NatalFactGraph:
    """Assemble un graphe court pour un archetype anonyme."""
    return NatalFactGraph(graph_id="graph:archetype", facts=facts)


def _fact(
    fact_id: str,
    family: NatalFactFamily,
    objects: tuple[str, ...],
    *,
    requires_birth_time: bool = False,
    editorial_candidate: bool = True,
) -> NatalFact:
    """Construit un fait minimal reutilisable par les archetypes."""
    return NatalFact(
        fact_id=fact_id,
        family=family,
        objects=objects,
        confidence="runtime_confirmed",
        requires_birth_time=requires_birth_time,
        source_paths=("runtime.fact",),
        editorial_candidate=editorial_candidate,
    )


def _decision(audit, fact_id: str):
    """Retrouve une decision auditable par identifiant."""
    return next(decision for decision in audit.decisions if decision.fact_id == fact_id)


def _full_birth_time_context() -> EligibilityContext:
    """Autorise les surfaces horaires pour le corpus complet."""
    return EligibilityContext(
        birth_time_status="full_birth_time",
        can_use_houses=True,
        can_use_angles=True,
        can_use_house_rulers=True,
        can_use_lunar_nodes_by_house=True,
    )


def _date_only_context() -> EligibilityContext:
    """Interdit les surfaces horaires pour l'archetype date-only."""
    return EligibilityContext(
        birth_time_status="date_only",
        can_use_houses=False,
        can_use_angles=False,
        can_use_house_rulers=False,
        can_use_lunar_nodes_by_house=False,
    )

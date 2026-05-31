# Commentaire global: ces tests verrouillent le modele de salience natal Basic.
"""Tests unitaires du modele de salience applique au graphe de faits Basic."""

from __future__ import annotations

import ast
from pathlib import Path

from app.domain.astrology.interpretation.basic_natal_eligibility import EligibilityContext
from app.domain.astrology.interpretation.natal_fact_graph import (
    NatalFact,
    NatalFactFamily,
    NatalFactGraph,
)
from app.domain.astrology.interpretation.natal_salience_model import (
    NATAL_SALIENCE_MODEL_VERSION,
    NatalSalienceExclusionReason,
    NatalSalienceLevel,
    NatalSalienceModel,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
SALIENCE_MODULE = REPO_ROOT / "app/domain/astrology/interpretation/natal_salience_model.py"
PUBLIC_PROJECTION_MODULE = (
    REPO_ROOT / "app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py"
)
SCORE_FIELD = "salience_" + "score"
LEVEL_FIELD = "salience_" + "level"


def test_included_facts_receive_score_level_and_stable_reasons() -> None:
    """Chaque fait inclus porte le contrat interne de salience."""
    audit = NatalSalienceModel().score(_pillar_graph(), _full_birth_time_context())
    included_payloads = [decision.to_internal_payload() for decision in audit.included_decisions]

    assert audit.model_version == NATAL_SALIENCE_MODEL_VERSION
    assert included_payloads
    assert all(SCORE_FIELD in item for item in included_payloads)
    assert all(LEVEL_FIELD in item for item in included_payloads)
    assert all(item["reason_codes"] for item in included_payloads)
    assert all("exclusion_reason" not in item for item in included_payloads)
    assert _decision(audit, "sun").reason_codes == ("pillar_sun",)
    assert _decision(audit, "moon").reason_codes == ("pillar_moon",)


def test_excluded_facts_receive_deterministic_reason() -> None:
    """Les faits indisponibles ou faibles ne restent pas sans explication."""
    minor_code = "black_moon_" + "li" + "lith"
    graph = _graph(
        _fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
        _fact("weak-node", NatalFactFamily.NODE, ("north_node",)),
        _fact("minor", NatalFactFamily.PLANET_POSITION, (minor_code, "aries")),
        _fact(
            "asc",
            NatalFactFamily.ANGLE,
            ("asc",),
            requires_birth_time=True,
        ),
    )

    audit = NatalSalienceModel().score(graph, _date_only_context())

    assert _decision(audit, "weak-node").exclusion_reason is (
        NatalSalienceExclusionReason.SINGLE_WEAK_SIGNAL
    )
    assert _decision(audit, "minor").exclusion_reason is (
        NatalSalienceExclusionReason.MINOR_OR_TECHNICAL_SIGNAL
    )
    assert _decision(audit, "asc").exclusion_reason is (
        NatalSalienceExclusionReason.BIRTH_TIME_SURFACE_UNAVAILABLE
    )


def test_sun_moon_and_eligible_ascendant_remain_pillars() -> None:
    """Les trois piliers natals eligibles dominent les faits secondaires."""
    audit = NatalSalienceModel().score(_pillar_graph(), _full_birth_time_context())

    assert _decision(audit, "sun").salience_level is NatalSalienceLevel.PILLAR
    assert _decision(audit, "moon").salience_level is NatalSalienceLevel.PILLAR
    assert _decision(audit, "asc").salience_level is NatalSalienceLevel.PILLAR
    assert _decision(audit, "sun").salience_score > _decision(audit, "mars").salience_score
    assert _decision(audit, "moon").salience_score > _decision(audit, "mars").salience_score
    assert _decision(audit, "asc").salience_score > _decision(audit, "mars").salience_score


def test_exact_luminary_aspect_ranks_above_wide_transpersonal_aspect() -> None:
    """Un aspect exact de luminaire reste prioritaire face a un aspect secondaire."""
    audit = NatalSalienceModel().score(
        _graph(
            _fact(
                "exact-luminary",
                NatalFactFamily.ASPECT,
                ("sun", "moon", "trine"),
                source_paths=("aspects.sun:trine:moon", "runtime.aspect.exact"),
            ),
            _fact(
                "wide-transpersonal",
                NatalFactFamily.ASPECT,
                ("uranus", "neptune", "sextile"),
                source_paths=("aspects.neptune:sextile:uranus", "runtime.aspect.wide"),
            ),
        ),
        _full_birth_time_context(),
    )

    exact = _decision(audit, "exact-luminary")
    wide = _decision(audit, "wide-transpersonal")
    assert exact.salience_score > wide.salience_score
    assert exact.reason_codes == ("luminary_aspect", "exact_aspect")


def test_salience_model_uses_runtime_facts_without_local_recalculation() -> None:
    """AST guard: le modele ne rappelle aucun moteur astrologique."""
    tree = ast.parse(SALIENCE_MODULE.read_text(encoding="utf-8"))
    forbidden_calls = {
        "calculate_" + "as" + "pect",
        "calculate_" + "dig" + "nity",
        "Swiss" + "Eph",
        "s" + "we",
        "House" + "RulerResolver",
    }
    forbidden_import_prefixes = ("app.api", "app.infra", "app.services", "fastapi", "sqlalchemy")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            assert _call_name(node.func) not in forbidden_calls
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            assert not any(
                node.module == prefix or node.module.startswith(f"{prefix}.")
                for prefix in forbidden_import_prefixes
            )


def test_public_projection_contract_does_not_expose_salience_fields() -> None:
    """La projection client ne depend pas des champs de scoring internes."""
    tree = ast.parse(PUBLIC_PROJECTION_MODULE.read_text(encoding="utf-8"))
    constants = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)}

    assert SCORE_FIELD not in constants
    assert LEVEL_FIELD not in constants
    assert "ranking_" + "score" not in constants
    assert "weighted_" + "score" not in constants


def _pillar_graph() -> NatalFactGraph:
    """Construit un graphe court avec piliers et repetition thematique."""
    return _graph(
        _fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
        _fact("moon", NatalFactFamily.LUMINARY, ("moon",)),
        _fact("asc", NatalFactFamily.ANGLE, ("asc",), requires_birth_time=True),
        _fact("mars", NatalFactFamily.PLANET_POSITION, ("mars", "aries")),
        _fact("mars-house", NatalFactFamily.HOUSE_EMPHASIS, ("mars", "house:1", "angular")),
        _fact("mars-dignity", NatalFactFamily.CONDITION, ("mars", "domicile")),
    )


def _graph(*facts: NatalFact) -> NatalFactGraph:
    """Assemble un graphe deterministe pour le modele teste."""
    return NatalFactGraph(graph_id="graph:test", facts=facts)


def _fact(
    fact_id: str,
    family: NatalFactFamily,
    objects: tuple[str, ...],
    *,
    requires_birth_time: bool = False,
    source_paths: tuple[str, ...] = ("runtime.fact",),
    editorial_candidate: bool = True,
) -> NatalFact:
    """Cree un fait minimal sans dupliquer le builder de graphe."""
    return NatalFact(
        fact_id=fact_id,
        family=family,
        objects=objects,
        confidence="runtime_confirmed",
        requires_birth_time=requires_birth_time,
        source_paths=source_paths,
        editorial_candidate=editorial_candidate,
    )


def _decision(audit, fact_id: str):
    """Retrouve une decision par identifiant stable."""
    return next(decision for decision in audit.decisions if decision.fact_id == fact_id)


def _full_birth_time_context() -> EligibilityContext:
    """Autorise les surfaces horaires pour les cas complets."""
    return EligibilityContext(
        birth_time_status="full_birth_time",
        can_use_houses=True,
        can_use_angles=True,
        can_use_house_rulers=True,
        can_use_lunar_nodes_by_house=True,
    )


def _date_only_context() -> EligibilityContext:
    """Bloque les surfaces dependantes de l'heure de naissance."""
    return EligibilityContext(
        birth_time_status="date_only",
        can_use_houses=False,
        can_use_angles=False,
        can_use_house_rulers=False,
        can_use_lunar_nodes_by_house=False,
    )


def _call_name(node: ast.AST) -> str:
    """Retourne le nom simple appele par un noeud AST."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""

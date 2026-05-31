# Commentaire global: ces tests prouvent l'activation deterministe des themes natals Basic.
"""Tests unitaires de l'activation des themes narratifs Basic."""

from __future__ import annotations

from app.domain.astrology.interpretation.basic_natal_eligibility import EligibilityContext
from app.domain.astrology.interpretation.natal_fact_graph import (
    NatalFact,
    NatalFactFamily,
    NatalFactGraph,
)
from app.domain.astrology.interpretation.natal_salience_model import NatalSalienceModel
from app.domain.astrology.interpretation.natal_theme_taxonomy import (
    NATAL_NARRATIVE_THEME_TAXONOMY_VERSION,
    BasicThemeCode,
    NatalNarrativeThemeTaxonomy,
)


def test_identity_and_functional_themes_activate_with_selected_fact_ids() -> None:
    """Les themes principaux conservent faits selectionnes et metadonnees."""
    themes = _activate(
        _full_graph(),
        _full_birth_time_context(),
    )
    by_code = _themes_by_code(themes)

    assert BasicThemeCode.CORE_IDENTITY in by_code
    assert BasicThemeCode.EMOTIONAL_PATTERN in by_code
    assert BasicThemeCode.MENTAL_STYLE in by_code
    assert BasicThemeCode.ACTION_AND_DRIVE in by_code
    assert BasicThemeCode.RELATIONSHIP_PATTERN in by_code
    assert BasicThemeCode.RESOURCES_AND_VALUES in by_code

    core = by_code[BasicThemeCode.CORE_IDENTITY]
    assert core.taxonomy_version == NATAL_NARRATIVE_THEME_TAXONOMY_VERSION
    assert core.selected_fact_ids
    assert "sun" in core.must_mention
    assert core.activation_metadata["matched_fact_count"] >= 1
    assert core.activation_score > 0


def test_house_and_angle_themes_respect_birth_time_availability() -> None:
    """Les themes maison ou angle disparaissent quand l'heure est indisponible."""
    full_codes = set(_themes_by_code(_activate(_full_graph(), _full_birth_time_context())))
    date_only_codes = set(_themes_by_code(_activate(_full_graph(), _date_only_context())))

    assert BasicThemeCode.PUBLIC_VOCATION in full_codes
    assert BasicThemeCode.PUBLIC_VOCATION not in date_only_codes
    assert BasicThemeCode.CORE_IDENTITY in date_only_codes
    assert BasicThemeCode.ACTION_AND_DRIVE in date_only_codes


def test_growth_theme_requires_repeated_or_high_node_material() -> None:
    """Un noeud isole reste bloque par la salience et ne cree pas de theme."""
    weak_themes = _activate(
        _graph(_fact("node-only", NatalFactFamily.NODE, ("north_node", "taurus"))),
        _full_birth_time_context(),
    )
    repeated_themes = _activate(
        _graph(
            _fact("node-axis", NatalFactFamily.NODE, ("north_node", "taurus")),
            _fact("node-aspect", NatalFactFamily.ASPECT, ("north_node", "sun", "trine")),
            _fact("node-ruler", NatalFactFamily.RULERSHIP, ("north_node", "house:9")),
        ),
        _full_birth_time_context(),
    )

    assert BasicThemeCode.GROWTH_DIRECTION not in _themes_by_code(weak_themes)
    assert BasicThemeCode.GROWTH_DIRECTION in _themes_by_code(repeated_themes)


def test_tension_theme_preserves_tension_and_do_not_mention_facts() -> None:
    """Les tensions actives gardent les faits contraints et voisins interdits."""
    themes = _activate(
        _graph(
            _fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            _fact("venus-detriment", NatalFactFamily.CONDITION, ("venus", "detriment")),
            _fact("venus-square-mars", NatalFactFamily.ASPECT, ("venus", "mars", "square")),
            _fact(
                "venus-soft-aspect",
                NatalFactFamily.ASPECT,
                ("venus", "mars", "trine"),
                editorial_candidate=False,
            ),
        ),
        _full_birth_time_context(),
    )
    tension = _themes_by_code(themes)[BasicThemeCode.TENSION_TO_INTEGRATE]

    assert "venus-detriment" in tension.constraints
    assert "venus-square-mars" in tension.tensions
    assert "venus-detriment" in tension.must_mention
    assert "venus-soft-aspect" in tension.do_not_mention


def test_distinct_talent_theme_stays_active_next_to_unrelated_tension() -> None:
    """Un appui non voisin ne doit pas etre masque par une tension active."""
    themes = _activate(
        _graph(
            _fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            _fact("venus-detriment", NatalFactFamily.CONDITION, ("venus", "detriment")),
            _fact("venus-square-mars", NatalFactFamily.ASPECT, ("venus", "mars", "square")),
            _fact("jupiter-trine-saturn", NatalFactFamily.ASPECT, ("jupiter", "saturn", "trine")),
            _fact("jupiter-exaltation", NatalFactFamily.CONDITION, ("jupiter", "exaltation")),
            _fact("saturn-domicile", NatalFactFamily.CONDITION, ("saturn", "domicile")),
        ),
        _full_birth_time_context(),
    )
    codes = set(_themes_by_code(themes))

    assert BasicThemeCode.TENSION_TO_INTEGRATE in codes
    assert BasicThemeCode.TALENTS_AND_SUPPORTS in codes


def test_redundant_support_theme_is_hierarchized_below_tension_theme() -> None:
    """Un theme d'appui voisin ne double pas le theme de tension actif."""
    themes = _activate(
        _graph(
            _fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
            _fact("venus-detriment", NatalFactFamily.CONDITION, ("venus", "detriment")),
            _fact("venus-square-mars", NatalFactFamily.ASPECT, ("venus", "mars", "square")),
            _fact("venus-trine-jupiter", NatalFactFamily.ASPECT, ("venus", "jupiter", "trine")),
            _fact("venus-exaltation", NatalFactFamily.CONDITION, ("venus", "exaltation")),
        ),
        _full_birth_time_context(),
    )
    codes = set(_themes_by_code(themes))

    assert BasicThemeCode.TENSION_TO_INTEGRATE in codes
    assert BasicThemeCode.TALENTS_AND_SUPPORTS not in codes


def _activate(
    graph: NatalFactGraph,
    eligibility_context: EligibilityContext,
):
    """Active la taxonomie depuis le modele de salience canonique."""
    salience_audit = NatalSalienceModel().score(graph, eligibility_context)
    return NatalNarrativeThemeTaxonomy().activate(
        graph=graph,
        salience_audit=salience_audit,
        eligibility_context=eligibility_context,
    )


def _themes_by_code(themes):
    """Indexe les themes par code canonique."""
    return {theme.theme_code: theme for theme in themes}


def _full_graph() -> NatalFactGraph:
    """Construit un graphe couvrant les familles fonctionnelles Basic."""
    return _graph(
        _fact("sun", NatalFactFamily.LUMINARY, ("sun",)),
        _fact("moon", NatalFactFamily.LUMINARY, ("moon", "water")),
        _fact("asc", NatalFactFamily.ANGLE, ("asc", "angular"), requires_birth_time=True),
        _fact("mc", NatalFactFamily.ANGLE, ("mc", "angular"), requires_birth_time=True),
        _fact("house-10", NatalFactFamily.HOUSE_EMPHASIS, ("mars", "house:10", "angular")),
        _fact("venus-position", NatalFactFamily.PLANET_POSITION, ("venus", "taurus")),
        _fact("venus-house", NatalFactFamily.HOUSE_EMPHASIS, ("venus", "house:7")),
        _fact("mercury-position", NatalFactFamily.PLANET_POSITION, ("mercury", "gemini")),
        _fact("mercury-aspect", NatalFactFamily.ASPECT, ("mercury", "moon", "trine")),
        _fact("mars-position", NatalFactFamily.PLANET_POSITION, ("mars", "aries")),
        _fact("mars-house", NatalFactFamily.HOUSE_EMPHASIS, ("mars", "house:1")),
        _fact("mars-condition", NatalFactFamily.CONDITION, ("mars", "domicile")),
    )


def _graph(*facts: NatalFact) -> NatalFactGraph:
    """Assemble un graphe deterministe pour la taxonomie."""
    return NatalFactGraph(graph_id="graph:theme-taxonomy", facts=facts)


def _fact(
    fact_id: str,
    family: NatalFactFamily,
    objects: tuple[str, ...],
    *,
    requires_birth_time: bool = False,
    editorial_candidate: bool = True,
) -> NatalFact:
    """Cree un fait minimal aligne sur le graphe Basic existant."""
    return NatalFact(
        fact_id=fact_id,
        family=family,
        objects=objects,
        confidence="runtime_confirmed",
        requires_birth_time=requires_birth_time,
        source_paths=("runtime.fact",),
        editorial_candidate=editorial_candidate,
    )


def _full_birth_time_context() -> EligibilityContext:
    """Autorise les surfaces dependantes de l'heure."""
    return EligibilityContext(
        birth_time_status="full_birth_time",
        can_use_houses=True,
        can_use_angles=True,
        can_use_house_rulers=True,
        can_use_lunar_nodes_by_house=True,
    )


def _date_only_context() -> EligibilityContext:
    """Interdit les surfaces dependantes de l'heure."""
    return EligibilityContext(
        birth_time_status="date_only",
        can_use_houses=False,
        can_use_angles=False,
        can_use_house_rulers=False,
        can_use_lunar_nodes_by_house=False,
    )

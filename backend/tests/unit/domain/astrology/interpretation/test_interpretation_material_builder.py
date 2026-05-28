"""Tests du builder de materiau interpretatif theme astral."""

from __future__ import annotations

import ast
from pathlib import Path

from app.domain.astrology.dominance.contracts import (
    DominantPlanetsResult,
    PlanetDominanceFactor,
    PlanetDominanceResult,
)
from app.domain.astrology.interpretation.chart_interpretation_input_builder import (
    ChartInterpretationInputBuilder,
)
from app.domain.astrology.interpretation.interpretation_material_builder import (
    InterpretationMaterialBuilder,
)
from app.domain.astrology.interpretation.interpretation_material_contracts import (
    INTERPRETATION_MATERIAL_KEYS,
    InterpretationMaterialSource,
)
from app.domain.astrology.natal_calculation import AspectResult
from app.domain.astrology.natal_preparation import BirthPreparedData
from tests.unit.domain.astrology.interpretation.support import interpretable_chart_object

REPO_ROOT = Path(__file__).resolve().parents[5]
INTERPRETATION_DIR = REPO_ROOT / "app/domain/astrology/interpretation"


class _NatalSource:
    """Source runtime minimale pour alimenter le builder de faits."""

    def __init__(
        self,
        *,
        chart_objects: tuple[object, ...],
        aspects: tuple[object, ...],
        prepared_input: BirthPreparedData | None = None,
    ) -> None:
        self.chart_objects = chart_objects
        self.aspects = aspects
        self.prepared_input = prepared_input or _prepared_paris_birth()
        self.dominant_planets = DominantPlanetsResult(
            score_profile_code="fixture.profile",
            tradition_code="fixture",
            reference_version_code="v1",
            planets=(
                PlanetDominanceResult(
                    planet_code="mars",
                    total_score=0.82,
                    rank=1,
                    dominance_level="dominant",
                    factors=(
                        PlanetDominanceFactor(
                            factor_code="angularity",
                            raw_value=1.0,
                            normalized_value=1.0,
                            weight=0.5,
                            weighted_score=0.5,
                            reason="fixture",
                        ),
                    ),
                    explanation_facts=(),
                ),
            ),
            top_planet_code="mars",
            chart_ruler_code="mars",
            most_elevated_planet_code="mars",
        )
        self.advanced_condition_facts = ()
        self.chart_balance = None


def test_material_keys_are_stable_for_all_profiles() -> None:
    """Les profils changent les volumes sans changer le contrat de cles."""
    chart_input = _build_chart_input(aspect_codes=("trine", "square", "opposition"))
    sources = _sources_for(chart_input)

    free = InterpretationMaterialBuilder().build(
        chart_input, sources=sources, delivery_profile="free"
    )
    basic = InterpretationMaterialBuilder().build(
        chart_input, sources=sources, delivery_profile="basic"
    )
    premium = InterpretationMaterialBuilder().build(
        chart_input, sources=sources, delivery_profile="premium"
    )

    assert tuple(free.to_payload()) == INTERPRETATION_MATERIAL_KEYS
    assert tuple(basic.to_payload()) == INTERPRETATION_MATERIAL_KEYS
    assert tuple(premium.to_payload()) == INTERPRETATION_MATERIAL_KEYS
    assert len(free.aspect_interpretations) == 1
    assert len(basic.aspect_interpretations) == 3
    assert len(premium.aspect_interpretations) == 3


def test_planet_sign_house_and_aspect_facts_match_sourced_text() -> None:
    """Chaque famille principale s'attache a un fait calcule et une source."""
    chart_input = _build_chart_input(aspect_codes=("trine",))
    material = InterpretationMaterialBuilder().build(
        chart_input,
        sources=_sources_for(chart_input),
        delivery_profile="premium",
    )

    assert material.planet_sign_interpretations[0].fact_ref == "object:mars:sign:aries"
    assert material.planet_sign_interpretations[0].source_ref.startswith(
        "astral_planet_interpretation_profiles:"
    )
    assert material.planet_house_interpretations[0].fact_ref == "object:mars:house:1"
    assert material.aspect_interpretations[0].fact_ref == "aspect:trine:sun-moon"
    assert material.aspect_interpretations[0].interpretive_text == "Aspect source trine"


def test_items_always_keep_source_fact_and_text_or_hint() -> None:
    """Aucun item ne sort sans provenance ni contenu source."""
    chart_input = _build_chart_input(aspect_codes=("trine",))
    payload = (
        InterpretationMaterialBuilder()
        .build(chart_input, sources=_sources_for(chart_input), delivery_profile="premium")
        .to_payload()
    )

    emitted_items = [item for values in payload.values() for item in values]
    assert emitted_items
    for item in emitted_items:
        assert item["source_ref"]
        assert item["fact_ref"]
        assert item["theme"]
        assert item["keywords"]
        assert "interpretive_text" in item or "writing_hint" in item


def test_missing_source_text_emits_no_material_item() -> None:
    """Un fait calcule sans source compatible ne genere aucun contenu."""
    chart_input = _build_chart_input(aspect_codes=("trine",))

    material = InterpretationMaterialBuilder().build(
        chart_input,
        sources=(
            _source(
                "planet_sign_interpretations",
                source_id="mars-taurus",
                planet_code="mars",
                sign_code="taurus",
            ),
        ),
        delivery_profile="premium",
    )

    assert material.planet_sign_interpretations == ()
    assert material.to_payload()["planet_sign_interpretations"] == []


def test_interpretation_material_builder_has_one_domain_owner() -> None:
    """AST guard: le builder reste dans son owner domaine et sans SQL."""
    builder_files = [
        path
        for path in INTERPRETATION_DIR.glob("*.py")
        if "class InterpretationMaterialBuilder" in path.read_text(encoding="utf-8")
    ]
    tree = ast.parse(
        (INTERPRETATION_DIR / "interpretation_material_builder.py").read_text(encoding="utf-8")
    )
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert builder_files == [INTERPRETATION_DIR / "interpretation_material_builder.py"]
    assert all(not module.startswith("sqlalchemy") for module in imported_modules)
    assert all(".infra." not in module for module in imported_modules)


def _build_chart_input(
    *,
    aspect_codes: tuple[str, ...],
    prepared_input: BirthPreparedData | None = None,
) -> object:
    """Construit un input interpretatif representatif depuis les builders existants."""
    aspects = tuple(
        AspectResult(
            aspect_code=code,
            planet_a="sun",
            planet_b="moon",
            angle=120.0,
            orb=1.0,
            orb_used=1.0,
            orb_max=6.0,
            family="major",
            is_major=True,
            is_minor=False,
        )
        for code in aspect_codes
    )
    return ChartInterpretationInputBuilder().build(
        _NatalSource(
            chart_objects=(interpretable_chart_object("mars"),),
            aspects=aspects,
            prepared_input=prepared_input,
        ),
        chart_id="chart-1",
        locale="fr-FR",
    )


def _prepared_paris_birth(*, birth_time_local: str | None = "11:00") -> BirthPreparedData:
    """Construit le contexte de naissance canonique utilise par les payloads tests."""
    return BirthPreparedData(
        birth_datetime_local="1973-04-24T11:00:00+01:00",
        birth_datetime_utc="1973-04-24T10:00:00+00:00",
        timestamp_utc=104580000,
        julian_day=2441796.916666667,
        birth_timezone="Europe/Paris",
        birth_date="1973-04-24",
        birth_time_local=birth_time_local,
        birth_place="Paris",
        birth_city="Paris",
        birth_country="France",
        birth_lat=48.8566,
        birth_lon=2.3522,
        jd_ut=2441796.916666667,
        timezone_used="Europe/Paris",
        timezone_iana="Europe/Paris",
        timezone_source="user_provided",
    )


def _sources_for(chart_input: object) -> tuple[InterpretationMaterialSource, ...]:
    """Fabrique les sources auditees minimales rattachees aux faits du test."""
    aspect_sources = tuple(
        _source(
            "aspect_interpretations",
            source_owner="astral_aspect_interpretation_profiles",
            source_id=f"aspect-{aspect.code}",
            aspect_code=aspect.code,
            text=f"Aspect source {aspect.code}",
            weight=0.4,
        )
        for aspect in chart_input.aspects
    )
    return (
        _source(
            "planet_sign_interpretations",
            source_owner="astral_planet_interpretation_profiles",
            source_id="mars-aries",
            planet_code="mars",
            sign_code="aries",
            text="Mars en Belier source",
        ),
        _source(
            "planet_house_interpretations",
            source_owner="astral_house_interpretation_profiles",
            source_id="mars-house-1",
            planet_code="mars",
            house_number=1,
            text="Mars maison 1 source",
        ),
        *aspect_sources,
        _source(
            "dominant_themes",
            source_owner="dominance_reference",
            source_id="dominance-mars",
            dominance_code="mars",
            text="Dominance Mars source",
        ),
        _source(
            "tensions",
            source_id="tension-trine",
            aspect_code="trine",
            writing_hint="Nuancer la tension de l'aspect.",
        ),
        _source(
            "resources",
            source_id="resource-mars",
            dominance_code="mars",
            writing_hint="Transformer la dominance en ressource.",
        ),
        _source(
            "integration_levers",
            source_id="lever-mars",
            dominance_code="mars",
            writing_hint="Proposer un levier d'integration concret.",
        ),
        _source(
            "warnings",
            source_id="warning-trine",
            aspect_code="trine",
            writing_hint="Rappeler la limite de lecture symbolique.",
        ),
    )


def _source(
    section: str,
    *,
    source_owner: str = "fixture_source_owner",
    source_id: str,
    planet_code: str | None = None,
    sign_code: str | None = None,
    house_number: int | None = None,
    aspect_code: str | None = None,
    dominance_code: str | None = None,
    text: str | None = "Texte source",
    writing_hint: str | None = None,
    weight: float = 0.25,
) -> InterpretationMaterialSource:
    """Cree une source compacte pour les cas de selection."""
    return InterpretationMaterialSource(
        section=section,
        source_owner=source_owner,
        source_id=source_id,
        source_version="v1",
        theme=f"theme:{source_id}",
        keywords=("force", "integration"),
        interpretive_text=text,
        writing_hint=writing_hint,
        risk="surinterpretation",
        resource="fact_source",
        base_weight=weight,
        planet_code=planet_code,
        sign_code=sign_code,
        house_number=house_number,
        aspect_code=aspect_code,
        dominance_code=dominance_code,
    )

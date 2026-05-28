"""Tests du repository de sources pour le materiau interpretatif theme astral."""

from __future__ import annotations

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.domain.astrology.dominance.contracts import DominantPlanetsResult
from app.domain.astrology.interpretation.chart_interpretation_input_builder import (
    ChartInterpretationInputBuilder,
)
from app.domain.astrology.interpretation.theme_astral_llm_input_v1_builder import (
    ThemeAstralLLMInputV1Builder,
)
from app.domain.astrology.natal_calculation import AspectResult
from app.infra.db.base import Base
from app.infra.db.models import (
    AspectModel,
    AstralAspectFamilyModel,
    AstralAspectInterpretationProfileModel,
    AstralPlanetInterpretationProfileModel,
    AstralSystemModel,
    HouseInterpretationProfileModel,
    HouseModel,
    LanguageModel,
    PlanetModel,
    ReferenceVersionModel,
)
from app.infra.db.repositories.interpretation_material_source_repository import (
    InterpretationMaterialSourceRepository,
)
from tests.unit.domain.astrology.interpretation.support import interpretable_chart_object


class _NatalSource:
    """Source minimale avec faits calcules pour verifier le handoff LLM."""

    chart_objects = (interpretable_chart_object("mars"),)
    aspects = (
        AspectResult(
            aspect_code="trine",
            planet_a="sun",
            planet_b="moon",
            angle=120.0,
            orb=1.0,
            orb_used=1.0,
            orb_max=6.0,
            family="major",
            is_major=True,
            is_minor=False,
        ),
    )
    dominant_planets = DominantPlanetsResult(
        score_profile_code="fixture.profile",
        tradition_code="fixture",
        reference_version_code="v1",
        planets=(),
        top_planet_code=None,
        chart_ruler_code=None,
        most_elevated_planet_code=None,
    )
    advanced_condition_facts = ()
    chart_balance = None


def test_repository_sources_from_db_profiles_reach_theme_astral_llm_input() -> None:
    """Les profils DB existants alimentent le contrat LLM sans constante inventee."""
    with _open_seeded_session() as db:
        sources = InterpretationMaterialSourceRepository(db).load_sources(
            reference_version="1.0.0",
            language_code="fr-FR",
            astral_system="modern",
        )

    chart_input = ChartInterpretationInputBuilder().build(_NatalSource(), chart_id="chart-1")
    payload = ThemeAstralLLMInputV1Builder().build(
        chart_input=chart_input,
        interpretation_sources=sources,
        delivery_profile="premium",
    )
    material = payload["input_data"]["interpretation_material"]

    assert material["planet_sign_interpretations"][0]["source_ref"].startswith(
        "astral_planet_interpretation_profiles:"
    )
    assert material["planet_sign_interpretations"][0]["fact_ref"] == "object:mars:sign:aries"
    assert material["planet_house_interpretations"][0]["source_ref"].startswith(
        "astral_house_interpretation_profiles:"
    )
    assert material["aspect_interpretations"][0]["source_ref"].startswith(
        "astral_aspect_interpretation_profiles:"
    )
    assert material["aspect_interpretations"][0]["fact_ref"] == "aspect:trine:sun-moon"


def _open_seeded_session() -> Session:
    """Ouvre une DB SQLite locale avec les tables de reference necessaires."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    _seed_reference_rows(session)
    return session


def _seed_reference_rows(db: Session) -> None:
    """Insere les profils planetes, maisons et aspects minimaux."""
    version = ReferenceVersionModel(version="1.0.0", description="test", is_locked=False)
    language = LanguageModel(code="en", name="English")
    system = AstralSystemModel(name="modern")
    planet = PlanetModel(code="mars", name="Mars", swe_id=4)
    house = HouseModel(number=1, name="House 1")
    aspect_family = AstralAspectFamilyModel(name="major")
    aspect = AspectModel(code="trine", name="Trine", angle=120.0, aspect_family=aspect_family)
    db.add_all((version, language, system, planet, house, aspect_family, aspect))
    db.flush()
    db.add_all(
        (
            AstralPlanetInterpretationProfileModel(
                reference_version_id=version.id,
                planet_id=planet.id,
                astral_system_id=system.id,
                language_id=language.id,
                title="Mars source",
                summary="Texte source Mars",
                core_keywords_json=_json("elan"),
                shadow_keywords_json=_json("impulsivite"),
                psychological_expression_json=_json("affirmation"),
                growth_patterns_json=_json("initiative"),
                prompt_hints_json=_json("Relier Mars au signe calcule."),
            ),
            HouseInterpretationProfileModel(
                reference_version_id=version.id,
                house_id=house.id,
                language_id=language.id,
                astral_system_id=system.id,
                title="Maison 1 source",
                summary="Texte source Maison 1",
                core_keywords_json=_json("identite"),
                shadow_keywords_json=_json("reaction"),
                psychological_keywords_json=_json("presence"),
                material_keywords_json=_json("corps"),
                prompt_hints_json=_json("Relier la maison au fait calcule."),
            ),
            AstralAspectInterpretationProfileModel(
                reference_version_id=version.id,
                aspect_id=aspect.id,
                astral_system_id=system.id,
                language_id=language.id,
                title="Trigone source",
                summary="Texte source Trigone",
                core_keywords_json=_json("fluidite"),
                shadow_keywords_json=_json("facilite"),
                psychological_keywords_json=_json("cooperation"),
                growth_patterns_json=_json("circulation"),
                prompt_hints_json=_json("Relier l'aspect aux deux participants."),
            ),
        )
    )
    db.commit()


def _json(*values: str) -> str:
    """Encode les champs listes des profils editoriaux."""
    return json.dumps(list(values), ensure_ascii=False)

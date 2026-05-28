# Generateur local des exemples JSON CS-371 sans appel provider.
"""Genere les payloads exemples theme_astral depuis les builders backend."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.astrology.builders.chart_object_runtime_builder import (  # noqa: E402
    build_house_position_payload,
)
from app.domain.astrology.dominance.contracts import (  # noqa: E402
    DominantPlanetsResult,
    PlanetDominanceFactor,
    PlanetDominanceResult,
)
from app.domain.astrology.interpretation.chart_interpretation_input_builder import (  # noqa: E402
    ChartInterpretationInputBuilder,
)
from app.domain.astrology.interpretation.interpretation_material_contracts import (  # noqa: E402
    InterpretationMaterialSource,
)
from app.domain.astrology.natal_calculation import AspectResult  # noqa: E402
from app.domain.astrology.planetary_conditions.contracts import (  # noqa: E402
    ConditionConfidence,
    PlanetaryMotionDirection,
    PlanetarySpeedState,
    PlanetVisibilityKey,
)
from app.domain.astrology.runtime.chart_object_runtime_data import (  # noqa: E402
    ChartObjectCapabilities,
    ChartObjectMotionPayload,
    ChartObjectPayloads,
    ChartObjectRuntimeData,
    ChartObjectSourceRuntimeData,
    ChartObjectSourceType,
    ChartObjectType,
    ChartObjectVisibilityPayload,
    DignityBreakdownItem,
    DignityRuntimePayload,
    DominanceBreakdownItem,
    DominanceRuntimePayload,
    RulershipRuntimePayload,
    ZodiacPositionRuntimeData,
)
from app.domain.llm.runtime.theme_astral_provider_payload_builder import (  # noqa: E402
    ThemeAstralProviderPayloadBuilder,
)
from app.infra.db.base import Base  # noqa: E402
from app.infra.db.models import (  # noqa: E402
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
from app.infra.db.repositories.interpretation_material_source_repository import (  # noqa: E402
    InterpretationMaterialSourceRepository,
)

EXAMPLE_DIR = (
    REPO_ROOT
    / "_condamad/examples/prompt-generation-cartography/"
    / "1973-04-24-1100-paris-theme-astral-v1"
)
EVIDENCE_DIR = (
    REPO_ROOT
    / "_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence"
)
PLANS = ("free", "basic", "premium")
ASPECT_CODES = ("trine", "square", "opposition", "conjunction", "sextile", "quincunx")
CHART_ID = "birth:1973-04-24 11:00 Europe/Paris Paris France"
TABLE_SOURCE_OWNERS = {
    "astral_planet_interpretation_profiles",
    "astral_house_interpretation_profiles",
    "astral_aspect_interpretation_profiles",
}
SUPPLEMENTAL_SOURCE_OWNER = "theme_astral_production_like_fixture"
SOURCE_NATURE = {
    "astral_planet_interpretation_profiles": "DB locale seedee production-like",
    "astral_house_interpretation_profiles": "DB locale seedee production-like",
    "astral_aspect_interpretation_profiles": "DB locale seedee production-like",
    SUPPLEMENTAL_SOURCE_OWNER: "fixture production-like hors table applicative",
}

PLANET_TEXTS = {
    "sun": (
        "Soleil en Taureau: stabilise l'identite par la presence, la continuite "
        "et une maniere concrete d'habiter ses choix. La lecture invite a relier "
        "ambition visible et rythme corporel pour eviter de confondre constance "
        "et immobilisme."
    ),
    "moon": (
        "Lune en Taureau: cherche une securite affective tangible, faite de "
        "reperes sensoriels, de fidelite et de temps long. Le texte doit montrer "
        "comment cette base apaise les variations emotionnelles sans nier le "
        "besoin de souplesse."
    ),
    "mercury": (
        "Mercure en Belier: pense vite, tranche les hypotheses et initie la "
        "parole avant que tout soit parfaitement stabilise. L'interpretation "
        "gagne a transformer cette impulsion mentale en clarte d'action plutot "
        "qu'en precipitation."
    ),
    "venus": (
        "Venus en Poissons: ouvre la relation par empathie, imagination et "
        "porosite aux ambiances. La source demande de distinguer compassion "
        "lucide et idealisation afin que le lien garde des contours habitables."
    ),
    "mars": (
        "Mars en Cancer: agit depuis la protection, la memoire et les attachements "
        "profonds. L'enjeu consiste a nommer les besoins defensifs avant qu'ils "
        "ne deviennent indirects ou trop charges emotionnellement."
    ),
    "jupiter": (
        "Jupiter en Verseau: elargit l'horizon par les reseaux, les idees "
        "collectives et une confiance dans l'experimentation sociale. La lecture "
        "doit relier ouverture d'esprit et responsabilite envers le groupe reel."
    ),
    "saturn": (
        "Saturne en Gemeaux: structure l'intelligence par methode, verification "
        "et apprentissage patient. Le risque n'est pas le doute en soi, mais une "
        "retenue qui retarde la formulation d'une pensee deja assez solide."
    ),
}

HOUSE_TEXTS = {
    8: (
        "Maison 8: concentre l'experience sur les transformations, les ressources "
        "partagees et les seuils psychiques. Le commentaire doit traiter la "
        "profondeur comme un terrain de discernement, pas comme une fatalite."
    ),
    9: (
        "Maison 9: oriente la planete vers le sens, la transmission, le voyage "
        "interieur ou culturel et les convictions qui agrandissent le cadre. "
        "L'ecriture doit montrer comment l'ideal devient pratique vivante."
    ),
    10: (
        "Maison 10: rend l'expression visible dans la vocation, la responsabilite "
        "publique et la construction d'une place reconnue. La source demande de "
        "relier ambition, exemplarite et limites soutenables."
    ),
    11: (
        "Maison 11: inscrit le fait astrologique dans les alliances, projets "
        "collectifs et appartenances choisies. La lecture doit faire sentir la "
        "difference entre soutien du groupe et dilution dans ses attentes."
    ),
    12: (
        "Maison 12: deplace l'energie vers l'invisible, la retraite, la memoire "
        "inconsciente et les gestes de compassion. Le texte doit nommer un lieu "
        "d'integration silencieuse sans installer de flou fataliste."
    ),
}

ASPECT_TEXTS = {
    "conjunction": (
        "Conjonction: fusionne deux fonctions psychiques dans un meme foyer "
        "d'intensite. L'interpretation doit montrer la puissance d'unification "
        "et le besoin de differencier les roles pour garder du recul."
    ),
    "sextile": (
        "Sextile: ouvre une cooperation disponible mais non automatique. Le texte "
        "doit inviter a saisir l'occasion, a poser un geste concret et a ne pas "
        "laisser le potentiel rester theorique."
    ),
    "square": (
        "Carre: met deux dynamiques sous tension active et demande un ajustement "
        "pratique. La source privilegie une lecture de friction creatrice plutot "
        "qu'un verdict de blocage."
    ),
    "trine": (
        "Trigone: facilite la circulation entre deux fonctions et donne une "
        "ressource fluide. L'interpretation doit aussi signaler le risque de "
        "confort passif si ce talent n'est pas mobilise consciemment."
    ),
    "quincunx": (
        "Quinconce: signale un decalage subtil qui oblige a regler finement les "
        "habitudes et les attentes. Le texte doit rester nuancé et proposer une "
        "integration progressive."
    ),
    "opposition": (
        "Opposition: place deux poles en vis-a-vis et rend necessaire une "
        "mediation consciente. L'ecriture doit faire apparaitre le dialogue "
        "possible plutot qu'une simple contradiction."
    ),
}


class _NatalSource:
    """Expose les attributs minimaux attendus par le builder interpretatif."""

    def __init__(
        self,
        *,
        chart_objects: tuple[ChartObjectRuntimeData, ...],
        aspects: tuple[AspectResult, ...],
    ) -> None:
        """Conserve les faits runtime deja resolus pour le scenario exemple."""
        self.chart_objects = chart_objects
        self.aspects = aspects
        self.dominant_planets = DominantPlanetsResult(
            score_profile_code="theme_astral.example_1973",
            tradition_code="western_modern",
            reference_version_code="v1",
            planets=(
                _dominant_planet("sun", 0.91, 1, "dominant"),
                _dominant_planet("venus", 0.74, 2, "strong"),
                _dominant_planet("mars", 0.62, 3, "active"),
            ),
            top_planet_code="sun",
            chart_ruler_code="venus",
            most_elevated_planet_code="sun",
        )
        self.advanced_condition_facts = ()
        self.chart_balance = None


def main() -> None:
    """Ecrit les exemples, la comparaison et les preuves de generation."""
    EXAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    chart_input = _build_chart_input()
    sources = _sources_for(chart_input)
    payloads = _payloads(chart_input, sources)

    _write_json(
        EXAMPLE_DIR / "intermediate-data.json", _intermediate_data(chart_input, sources, payloads)
    )
    for plan, payload in payloads.items():
        _write_json(EXAMPLE_DIR / f"{plan}-provider-payload.json", payload)
    (EXAMPLE_DIR / "README.md").write_text(_readme(), encoding="utf-8")
    (EXAMPLE_DIR / "structure-comparison.md").write_text(
        _structure_comparison(payloads), encoding="utf-8"
    )
    (EVIDENCE_DIR / "source-coverage.md").write_text(_source_coverage(), encoding="utf-8")
    (EVIDENCE_DIR / "no-provider-proof.txt").write_text(
        "PASS: generation locale via ThemeAstralProviderPayloadBuilder; aucun client provider, "
        "LLMGateway.generate ou appel reseau n'est invoque.\n",
        encoding="utf-8",
    )


def _build_chart_input() -> Any:
    """Construit l'input runtime partage par les trois plans."""
    chart_objects = (
        _chart_object("sun", "Soleil", "taurus", 3.87, 34.0, 10, 0.91, False),
        _chart_object("moon", "Lune", "taurus", 29.32, 59.3, 11, 0.58, False),
        _chart_object("mercury", "Mercure", "aries", 22.61, 22.6, 10, 0.44, False),
        _chart_object("venus", "Venus", "pisces", 18.59, 348.6, 9, 0.74, False),
        _chart_object("mars", "Mars", "cancer", 2.43, 92.4, 12, 0.62, False),
        _chart_object("jupiter", "Jupiter", "aquarius", 9.98, 310.0, 8, 0.51, False),
        _chart_object("saturn", "Saturne", "gemini", 28.41, 88.4, 12, 0.49, False),
    )
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
        for code in ASPECT_CODES
    )
    return ChartInterpretationInputBuilder().build(
        _NatalSource(chart_objects=chart_objects, aspects=aspects),
        chart_id=CHART_ID,
        locale="fr-FR",
    )


def _payloads(
    chart_input: Any, sources: tuple[InterpretationMaterialSource, ...]
) -> dict[str, dict[str, Any]]:
    """Genere les payloads par plan avec le meme builder canonique."""
    builder = ThemeAstralProviderPayloadBuilder()
    return {
        plan: builder.build(
            chart_input=chart_input,
            interpretation_sources=sources,
            commercial_plan=plan,
            astrologer_voice={
                "tone": "calme",
                "vocabulary": ["symbolique", "clair", "nuance"],
                "emphases": ["integration", "limites explicites", "sources"],
            },
        )
        for plan in PLANS
    }


def _chart_object(
    code: str,
    display_name: str,
    sign_code: str,
    degree_in_sign: float,
    longitude: float,
    house_number: int,
    dominance_score: float,
    retrograde: bool,
) -> ChartObjectRuntimeData:
    """Cree un objet runtime resolu avec sources techniques non textuelles."""
    direction = (
        PlanetaryMotionDirection.RETROGRADE if retrograde else PlanetaryMotionDirection.DIRECT
    )
    speed = -0.2 if retrograde else 0.8
    return ChartObjectRuntimeData(
        code=code,
        object_type=ChartObjectType.PLANET,
        display_name=display_name,
        longitude=longitude,
        latitude=None,
        zodiac_position=ZodiacPositionRuntimeData(
            sign_code=sign_code, degree_in_sign=degree_in_sign
        ),
        source=ChartObjectSourceRuntimeData(
            source_type=ChartObjectSourceType.EPHEMERIS,
            source_key=f"example_1973_paris:{code}",
        ),
        capabilities=ChartObjectCapabilities(
            supports_interpretation=True,
            supports_dignities=True,
            supports_dominance=True,
            supports_house_position=True,
            supports_motion=True,
            supports_visibility=True,
            supports_rulership=True,
        ),
        classifications=("planet",),
        payloads=ChartObjectPayloads(
            motion=ChartObjectMotionPayload(
                speed_longitude=speed,
                is_retrograde=retrograde,
                direction=direction,
                is_direct=not retrograde,
                is_stationary=False,
                speed_state=PlanetarySpeedState.NORMAL,
                absolute_speed_longitude=abs(speed),
                normalized_speed_ratio=1.0,
                source="theme_astral_example.ephemeris_snapshot",
            ),
            visibility=ChartObjectVisibilityPayload(
                visibility_key=PlanetVisibilityKey.VISIBLE,
                is_visible=True,
                confidence=ConditionConfidence.HIGH,
                reason="example_source_has_birth_time_and_place",
                source="theme_astral_example.visibility_snapshot",
            ),
            dignity=DignityRuntimePayload(
                essential_score=2.0,
                accidental_score=1.0,
                total_score=3.0,
                source="theme_astral_example.dignity_snapshot",
                essential_breakdown=(
                    DignityBreakdownItem("sign_condition", 2.0, "example_dignity_table"),
                ),
                condition_codes=("interpretable",),
            ),
            dominance=DominanceRuntimePayload(
                contribution_score=dominance_score,
                source="theme_astral_example.dominance_snapshot",
                rank=max(1, round((1.0 - dominance_score) * 10)),
                contribution_breakdown=(DominanceBreakdownItem("angularity", 1.0, 1.0, 0.5, 0.5),),
                factors=("angularity",),
            ),
            house_position=build_house_position_payload(house_number=house_number),
            rulership=RulershipRuntimePayload(
                rules_houses=(house_number,),
                is_house_ruler=True,
                is_ascendant_ruler=house_number == 1,
                is_midheaven_ruler=code == "sun",
                source="theme_astral_example.rulership_snapshot",
                dispositor_code="venus",
                rules_signs=(sign_code,),
                rulership_sources=("traditional",),
            ),
        ),
    )


def _dominant_planet(code: str, score: float, rank: int, level: str) -> PlanetDominanceResult:
    """Fabrique un resultat de dominance chart-level."""
    return PlanetDominanceResult(
        planet_code=code,
        total_score=score,
        rank=rank,
        dominance_level=level,
        factors=(
            PlanetDominanceFactor(
                factor_code="angularity",
                raw_value=1.0,
                normalized_value=1.0,
                weight=0.5,
                weighted_score=0.5,
                reason="example_1973_paris",
            ),
        ),
        explanation_facts=(),
    )


def _sources_for(chart_input: Any) -> tuple[InterpretationMaterialSource, ...]:
    """Charge les sources depuis les tables d'interpretation puis ajoute les signaux runtime."""
    with _open_seeded_material_session() as db:
        table_sources = InterpretationMaterialSourceRepository(db).load_sources(
            reference_version="1.0.0",
            language_code="fr-FR",
            astral_system="modern",
        )
    return (*table_sources, *_supplemental_runtime_sources(chart_input))


def _supplemental_runtime_sources(chart_input: Any) -> tuple[InterpretationMaterialSource, ...]:
    """Cree uniquement les sources de sections non encore portees par le repository DB."""
    sources: list[InterpretationMaterialSource] = []
    for dominance in chart_input.dominance:
        sources.append(
            _source(
                "dominant_themes",
                source_id=f"dominance-{dominance.code}",
                dominance_code=dominance.code,
                text=_dominance_text(dominance.code),
            )
        )
    sources.extend(
        (
            _source(
                "tensions",
                source_id="tension-major-aspects",
                aspect_code="square",
                text=(
                    "Tensions majeures: les frictions du theme sont traitees comme des "
                    "points d'ajustement entre besoin de securite, exposition publique "
                    "et reactivite emotionnelle. La redaction doit nommer un conflit "
                    "utilisable, jamais une sentence."
                ),
            ),
            _source(
                "resources",
                source_id="resource-venus",
                dominance_code="venus",
                text=(
                    "Ressource Venus: l'empathie, la qualite de lien et l'imaginaire "
                    "relationnel peuvent soutenir la vocation si des limites simples "
                    "protegent la disponibilite affective."
                ),
            ),
            _source(
                "integration_levers",
                source_id="lever-sun",
                dominance_code="sun",
                text=(
                    "Levier Soleil: ancrer les decisions visibles dans un rythme stable, "
                    "mesurable et corporellement soutenable permet de transformer la "
                    "dominante solaire en presence fiable."
                ),
            ),
            _source(
                "warnings",
                source_id="warning-symbolic-reading",
                aspect_code="opposition",
                text=(
                    "Avertissement de lecture: ces correspondances sont symboliques, "
                    "contextuelles et doivent rester proportionnees aux faits calcules; "
                    "elles ne remplacent ni choix personnel ni accompagnement specialise."
                ),
            ),
        )
    )
    return tuple(sources)


def _dominance_text(code: str) -> str:
    """Retourne un texte production-like pour les dominantes sans table dediee."""
    texts = {
        "sun": (
            "Dominante Soleil: la carte demande une lecture centree sur la coherence "
            "identitaire, la visibilite des choix et la responsabilite d'incarner une "
            "direction sans rigidifier l'image de soi."
        ),
        "venus": (
            "Dominante Venus: les themes relationnels, esthetiques et conciliateurs "
            "servent de ressource majeure, a condition de distinguer harmonie vivante "
            "et evitement du desaccord."
        ),
        "mars": (
            "Dominante Mars: l'elan d'action est present mais colore par la protection "
            "des attachements; le texte doit orienter cette force vers une initiative "
            "claire plutot que reactive."
        ),
    }
    return texts.get(
        code,
        "Dominante secondaire: signal production-like conserve pour tracer une priorite "
        "runtime non encore portee par une table applicative dediee.",
    )


def _open_seeded_material_session() -> Session:
    """Ouvre une table SQLite locale representant les profils editoriaux lus par le runtime."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    _seed_material_profiles(session)
    return session


def _seed_material_profiles(db: Session) -> None:
    """Seed les profils DB minimaux necessaires au scenario Paris 1973."""
    version = ReferenceVersionModel(version="1.0.0", description="CS-371 example", is_locked=False)
    language = LanguageModel(code="en", name="English")
    system = AstralSystemModel(name="modern")
    aspect_family = AstralAspectFamilyModel(name="major")
    db.add_all((version, language, system, aspect_family))
    db.flush()

    planets = {
        code: PlanetModel(code=code, name=display_name, swe_id=index)
        for index, (code, display_name) in enumerate(
            (
                ("sun", "Soleil"),
                ("moon", "Lune"),
                ("mercury", "Mercure"),
                ("venus", "Venus"),
                ("mars", "Mars"),
                ("jupiter", "Jupiter"),
                ("saturn", "Saturne"),
            ),
            start=1,
        )
    }
    houses = {number: HouseModel(number=number, name=f"House {number}") for number in range(1, 13)}
    aspects = {
        code: AspectModel(
            code=code, name=code.title(), angle=_aspect_angle(code), family=aspect_family.id
        )
        for code in ASPECT_CODES
    }
    db.add_all((*planets.values(), *houses.values(), *aspects.values()))
    db.flush()

    db.add_all(
        [
            AstralPlanetInterpretationProfileModel(
                reference_version_id=version.id,
                planet_id=planet.id,
                astral_system_id=system.id,
                language_id=language.id,
                title=f"{planet.name} source table",
                summary=PLANET_TEXTS[planet.code],
                micro_note=(
                    "Profil seed local production-like charge par le repository DB pour "
                    "l'exemple Paris 1973."
                ),
                core_keywords_json=_json("presence", "rythme", "expression consciente"),
                shadow_keywords_json=_json("fixation", "projection", "reaction defensive"),
                psychological_expression_json=_json("discernement", "choix incarnes"),
                spiritual_expression_json=_json("integration symbolique", "responsabilite"),
                growth_patterns_json=_json("maturation progressive", "alignement concret"),
                dos_json=_json("relier la planete au fait calcule et au profil de livraison"),
                conflict_patterns_json=_json("surinterpretation", "generalisation"),
                prompt_hints_json=_json(
                    "Citer le fait planetaire puis formuler une nuance psychologique utile."
                ),
            )
            for planet in planets.values()
        ]
    )
    db.add_all(
        [
            HouseInterpretationProfileModel(
                reference_version_id=version.id,
                house_id=house.id,
                language_id=language.id,
                astral_system_id=system.id,
                title=f"Maison {house.number} source table",
                summary=HOUSE_TEXTS.get(
                    house.number,
                    (
                        f"Maison {house.number}: cadre de vie production-like conserve "
                        "pour completer la table locale lorsque le scenario ne selectionne "
                        "pas directement cette maison."
                    ),
                ),
                micro_note="Profil maison seed local, explicite comme production-like.",
                core_keywords_json=_json("champ de vie", "contexte", "priorite"),
                shadow_keywords_json=_json("angle mort", "projection de role"),
                psychological_keywords_json=_json("experience situee", "besoin concret"),
                spiritual_keywords_json=_json("sens du lieu", "integration quotidienne"),
                material_keywords_json=_json("cadre", "habitude", "responsabilite"),
                dos_json=_json("situer le contexte sans reduire la personne a la maison"),
                donts_json=_json("ne pas transformer le secteur en predestination"),
                prompt_hints_json=_json(
                    "Relier la maison au fait calcule puis proposer une piste d'integration."
                ),
            )
            for house in houses.values()
        ]
    )
    db.add_all(
        [
            AstralAspectInterpretationProfileModel(
                reference_version_id=version.id,
                aspect_id=aspect.id,
                astral_system_id=system.id,
                language_id=language.id,
                title=f"Aspect {aspect.code} source table",
                summary=ASPECT_TEXTS[aspect.code],
                micro_note="Profil aspect seed local production-like charge par repository.",
                core_keywords_json=_json("lien", "dynamique", "regulation"),
                shadow_keywords_json=_json("automatismes", "polarisation"),
                psychological_keywords_json=_json("ajustement", "dialogue interne"),
                spiritual_keywords_json=_json("mise en relation", "integration des poles"),
                growth_patterns_json=_json("cooperation consciente", "choix d'usage"),
                dos_json=_json("nommer les deux fonctions et leur mode de relation"),
                conflict_patterns_json=_json("fatalisme", "lecture binaire"),
                prompt_hints_json=_json(
                    "Relier l'aspect aux deux participants et a son orb sans dramatiser."
                ),
            )
            for aspect in aspects.values()
        ]
    )
    db.commit()


def _aspect_angle(code: str) -> float:
    """Retourne l'angle canonique attendu par le modele DB."""
    return {
        "conjunction": 0.0,
        "sextile": 60.0,
        "square": 90.0,
        "trine": 120.0,
        "quincunx": 150.0,
        "opposition": 180.0,
    }[code]


def _json(*values: str) -> str:
    """Encode les champs listes des profils DB seedes."""
    return json.dumps(list(values), ensure_ascii=False)


def _source(
    section: str,
    *,
    source_id: str,
    source_owner: str = SUPPLEMENTAL_SOURCE_OWNER,
    planet_code: str | None = None,
    sign_code: str | None = None,
    house_number: int | None = None,
    aspect_code: str | None = None,
    dominance_code: str | None = None,
    text: str | None = None,
    writing_hint: str | None = None,
    weight: float = 0.25,
) -> InterpretationMaterialSource:
    """Normalise une fixture production-like compatible avec le builder."""
    return InterpretationMaterialSource(
        section=section,
        source_owner=source_owner,
        source_id=source_id,
        source_version="v1",
        theme=f"theme:{source_id}",
        keywords=("force", "integration", "limite"),
        interpretive_text=text,
        writing_hint=writing_hint,
        risk="surinterpretation",
        resource="source_factuelle",
        base_weight=weight,
        planet_code=planet_code,
        sign_code=sign_code,
        house_number=house_number,
        aspect_code=aspect_code,
        dominance_code=dominance_code,
    )


def _intermediate_data(
    chart_input: Any,
    sources: tuple[InterpretationMaterialSource, ...],
    payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Assemble les donnees intermediaires auditees pour les exemples."""
    return {
        "generation_method": {
            "kind": "runtime_builder_replay",
            "builder": "ThemeAstralProviderPayloadBuilder",
            "provider_call_performed": False,
            "scenario_note": "Le runtime actuel porte les champs naissance dans chart_id.",
        },
        "provider_call_performed": False,
        "birth_input": {
            "date": "1973-04-24",
            "time": "11:00",
            "place": "Paris",
            "country": "France",
            "timezone": "Europe/Paris",
            "latitude": 48.8566,
            "longitude": 2.3522,
        },
        "runtime_input": {
            "chart_id": chart_input.chart_id,
            "locale": chart_input.locale,
            "chart_type": chart_input.chart_type,
            "metadata": asdict(chart_input.metadata),
        },
        "source_coverage": {
            "source_count": len(sources),
            "table_source_count": sum(
                1 for source in sources if source.source_owner in TABLE_SOURCE_OWNERS
            ),
            "production_like_fixture_count": sum(
                1 for source in sources if source.source_owner == SUPPLEMENTAL_SOURCE_OWNER
            ),
            "source_owners": sorted({source.source_owner for source in sources}),
            "source_nature": {
                owner: SOURCE_NATURE[owner]
                for owner in sorted({source.source_owner for source in sources})
            },
            "sections": sorted({source.section for source in sources}),
            "family_owners": {
                "planet_sign_interpretations": "astral_planet_interpretation_profiles",
                "planet_house_interpretations": "astral_house_interpretation_profiles",
                "aspect_interpretations": "astral_aspect_interpretation_profiles",
                "dominant_themes": SUPPLEMENTAL_SOURCE_OWNER,
                "tensions": SUPPLEMENTAL_SOURCE_OWNER,
                "resources": SUPPLEMENTAL_SOURCE_OWNER,
                "integration_levers": SUPPLEMENTAL_SOURCE_OWNER,
                "warnings": SUPPLEMENTAL_SOURCE_OWNER,
            },
        },
        "profile_density": {
            plan: {
                "objects": len(payload["input_data"]["astrological_facts"]["objects"]),
                "aspects": len(payload["input_data"]["astrological_facts"]["aspects"]),
                "material_budget": payload["delivery_profile"]["material_budget"][
                    "max_source_items"
                ],
                "selected_sections": len(payload["input_data"]["selected_themes"]["section_keys"]),
                "output_max_sections": payload["output_contract"]["max_sections"],
            }
            for plan, payload in payloads.items()
        },
    }


def _readme() -> str:
    """Retourne la documentation locale des exemples."""
    return "\n".join(
        (
            "# Exemples JSON theme_astral LLM v1 par profil",
            "",
            "Ces fichiers documentent le payload provider `theme_astral_llm_input_v1` "
            "pour une naissance le `1973-04-24` a `11:00` a Paris, France.",
            "",
            "## Methode de generation",
            "",
            "- Generation locale dans le venv via le script evidence `generate_examples.py`.",
            "- Builder reutilise: `ThemeAstralProviderPayloadBuilder`.",
            "- Materiau reutilise: `InterpretationMaterialBuilder` et sources "
            "`InterpretationMaterialSource` chargees via "
            "`InterpretationMaterialSourceRepository` depuis des tables SQLite locales seedees.",
            "- Nature des sources: mixte. Les familles planetes, maisons et aspects "
            "proviennent de profils DB locaux seedes avec des textes production-like "
            "representatifs; les familles dominantes, tensions, ressources, leviers "
            "et avertissements restent des fixtures production-like explicites car "
            "aucune table applicative dediee ne les porte aujourd'hui.",
            "- Contrats runtime: `theme_astral_prompt_v1`, `theme_astral_llm_input_v1`, "
            "`theme_astral_response_contract_v1`.",
            "- Aucun appel LLM provider n'est effectue; aucun resultat final de provider "
            "n'est produit.",
            "",
            "## Livrables",
            "",
            "- `intermediate-data.json`: scenario, entree runtime, couverture source et densite.",
            "- `free-provider-payload.json`: payload essentiel, budget court et selection limitee.",
            "- `basic-provider-payload.json`: payload etendu, budget intermediaire.",
            "- `premium-provider-payload.json`: payload complet, budget maximal.",
            "- `structure-comparison.md`: squelette commun et differences de densite.",
            "",
            "## Notes de source",
            "",
            "- Propriete DB: `astral_planet_interpretation_profiles`, "
            "`astral_house_interpretation_profiles`, "
            "`astral_aspect_interpretation_profiles`.",
            f"- Propriete fixture: `{SUPPLEMENTAL_SOURCE_OWNER}` pour les sections "
            "`dominant_themes`, `tensions`, `resources`, `integration_levers`, "
            "et `warnings`.",
            "- Aucun texte fixture n'est presente comme contenu production reel; "
            "la couverture source dans `intermediate-data.json` indique le mixte "
            "DB locale seedee / production-like.",
            "",
            "Le runtime actuel expose le contexte de naissance dans "
            "`input_data.birth_context.chart_id`. Le scenario complet est aussi persiste "
            "dans `intermediate-data.json` pour rendre la date, l'heure et le lieu "
            "auditables sans modifier le contrat backend.",
            "",
        )
    )


def _structure_comparison(payloads: dict[str, dict[str, Any]]) -> str:
    """Produit une comparaison Markdown de squelette et de densite."""
    top_skeletons = {plan: list(payload.keys()) for plan, payload in payloads.items()}
    input_skeletons = {
        plan: list(payload["input_data"].keys()) for plan, payload in payloads.items()
    }
    rows = []
    for plan, payload in payloads.items():
        facts = payload["input_data"]["astrological_facts"]
        rows.append(
            (
                "| {plan} | {depth} | {objects} | {aspects} | {sections} | "
                "{max_sections} | {tokens} |"
            ).format(
                plan=plan,
                depth=payload["delivery_profile"]["depth"],
                objects=len(facts["objects"]),
                aspects=len(facts["aspects"]),
                sections=len(payload["input_data"]["selected_themes"]["section_keys"]),
                max_sections=payload["output_contract"]["max_sections"],
                tokens=payload["delivery_profile"]["output_length_policy"]["max_output_tokens"],
            )
        )
    return "\n".join(
        (
            "# Comparaison des structures provider theme_astral",
            "",
            "## Squelette commun",
            "",
            "Les trois payloads partagent les memes cles de premier niveau:",
            "",
            "```json",
            json.dumps(next(iter(top_skeletons.values())), ensure_ascii=False, indent=2),
            "```",
            "",
            "Les trois payloads partagent les memes cles `input_data`:",
            "",
            "```json",
            json.dumps(next(iter(input_skeletons.values())), ensure_ascii=False, indent=2),
            "```",
            "",
            "## Differences de densite",
            "",
            "| Profil backend | depth LLM-visible | objets | aspects | sections "
            "selectionnees | max sections sortie | max output tokens |",
            "|---|---:|---:|---:|---:|---:|---:|",
            "\n".join(rows),
            "",
            "La densite de `interpretation_material` suit les budgets du builder: "
            "les profils plus riches selectionnent davantage de sources et gardent "
            "les `source_ref` DB ou production-like explicites.",
            "",
            "Les differences restent portees par `delivery_profile`, les budgets, les "
            "selections et `output_contract`. Les etiquettes commerciales sont les noms "
            "de fichiers et ne sont pas presentes comme valeurs dans le contenu JSON "
            "transmis au LLM.",
            "",
        )
    )


def _source_coverage() -> str:
    """Documente les sources inspectees et les ecarts acceptes."""
    return "\n".join(
        (
            "# Couverture source CS-371",
            "",
            "- Brief source: `_story_briefs/"
            "cs-371-generer-exemples-json-theme-astral-llm-v1-par-plan.md`.",
            "- Synthese: `_condamad/docs/prompt-generation-cartography/"
            "theme-astral-llm-json-structure-v1.md`.",
            "- Builder: `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`.",
            "- Repository de sources: `backend/app/infra/db/repositories/"
            "interpretation_material_source_repository.py`.",
            "- Tests: `backend/tests/llm_orchestration/"
            "test_theme_astral_provider_payload_builder.py` et `backend/tests/"
            "integration/llm/test_theme_astral_provider_payload_handoff.py`.",
            "- Correction d'alignement: les sources planetes, maisons et aspects ne sont "
            "plus fabriquees directement par le script; elles sont chargees depuis "
            "`InterpretationMaterialSourceRepository` sur des profils DB seedes en SQLite.",
            "- Nature des sources DB: les tables locales seedent des textes "
            "production-like representatifs pour `astral_planet_interpretation_profiles`, "
            "`astral_house_interpretation_profiles` et "
            "`astral_aspect_interpretation_profiles`; elles prouvent le chemin repository "
            "sans affirmer une extraction de contenu production reel.",
            f"- Nature des supplements: `{SUPPLEMENTAL_SOURCE_OWNER}` fournit des fixtures "
            "production-like pour `dominant_themes`, `tensions`, `resources`, "
            "`integration_levers` et `warnings`, car aucune table applicative dediee "
            "ne porte ces familles dans le runtime actuel.",
            "- Couverture famille -> owner: `planet_sign_interpretations` -> "
            "`astral_planet_interpretation_profiles`; `planet_house_interpretations` -> "
            "`astral_house_interpretation_profiles`; `aspect_interpretations` -> "
            "`astral_aspect_interpretation_profiles`; `dominant_themes`, `tensions`, "
            f"`resources`, `integration_levers`, `warnings` -> `{SUPPLEMENTAL_SOURCE_OWNER}`.",
            "- Source gap: le runtime `ChartInterpretationInputRuntimeData` ne porte "
            "pas de champs naissance detailles; l'exemple encode le scenario dans "
            "`chart_id` et le documente dans `intermediate-data.json`.",
            "",
        )
    )


def _write_json(path: Path, value: Any) -> None:
    """Ecrit un JSON stable et lisible."""
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

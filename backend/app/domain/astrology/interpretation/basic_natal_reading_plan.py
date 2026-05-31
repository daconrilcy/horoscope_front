# Commentaire global: ce module construit le plan natal Basic inspectable avant redaction.
"""Construction deterministe du BasicNatalReadingPlan a partir des owners Basic."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Any, Literal

from app.domain.astrology.interpretation.basic_natal_eligibility import EligibilityContext
from app.domain.astrology.interpretation.natal_fact_graph import (
    NatalFact,
    NatalFactFamily,
    NatalFactGraph,
)
from app.domain.astrology.interpretation.natal_salience_model import (
    NatalSalienceAudit,
    NatalSalienceModel,
)
from app.domain.astrology.interpretation.natal_synthesis_resolver import (
    ResolvedThemeSynthesis,
    SynthesisResolver,
)
from app.domain.astrology.interpretation.natal_theme_taxonomy import BasicThemeCode, ThemeModel
from app.domain.astrology.reading.basic_natal_contracts import (
    BASIC_NATAL_ENGINE_VERSION,
    BASIC_NATAL_LEVEL,
)

BASIC_NATAL_READING_PLAN_ENGINE_VERSION = BASIC_NATAL_ENGINE_VERSION
BASIC_NATAL_READING_PLAN_LEVEL = BASIC_NATAL_LEVEL
MIN_SECTION_TARGET_WORDS = 90
MAX_SECTION_TARGET_WORDS = 170
MAX_READING_PLAN_SECTIONS = 8

_DATE_ONLY_FORBIDDEN_FAMILIES = frozenset(
    {
        NatalFactFamily.ANGLE,
        NatalFactFamily.HOUSE_EMPHASIS,
        NatalFactFamily.RULERSHIP,
    }
)
_HOUSE_MARKERS = ("house:",)
_ANGLE_OBJECTS = frozenset({"asc", "mc", "desc"})
_PUBLIC_LIMITATION = (
    "Cette lecture Basic reste une synthese symbolique: elle ne remplace pas un avis "
    "medical, juridique, financier ou psychologique."
)
_PUBLIC_DISCLAIMER = (
    "Le plan organise des themes astrologiques a titre de lecture personnelle, sans "
    "prediction certaine ni decision obligatoire."
)
_STYLE_CONSTRAINTS = (
    "Employer un ton clair, nuance et non fataliste.",
    "Ne pas ajouter de fait astrologique absent du plan.",
    "Garder les preuves publiques lisibles sans scores ni traces techniques.",
)
_FULL_SECTION_ORDER = (
    "synthesis",
    "identity",
    "inner_life",
    "vocation",
    "relationships",
    "talents",
    "tensions",
    "growth",
    "mental_style",
    "values",
    "action",
)
_DATE_ONLY_SECTION_ORDER = (
    "synthesis",
    "identity",
    "inner_life",
    "values",
    "action",
    "mental_style",
    "relationships",
    "tensions",
    "talents",
    "growth",
)
_THEME_SECTION_CODES = {
    BasicThemeCode.CORE_IDENTITY: "identity",
    BasicThemeCode.EMOTIONAL_PATTERN: "inner_life",
    BasicThemeCode.PUBLIC_VOCATION: "vocation",
    BasicThemeCode.RELATIONSHIP_PATTERN: "relationships",
    BasicThemeCode.MENTAL_STYLE: "mental_style",
    BasicThemeCode.RESOURCES_AND_VALUES: "values",
    BasicThemeCode.ACTION_AND_DRIVE: "action",
    BasicThemeCode.GROWTH_DIRECTION: "growth",
    BasicThemeCode.TENSION_TO_INTEGRATE: "tensions",
    BasicThemeCode.TALENTS_AND_SUPPORTS: "talents",
}
_SECTION_LABELS = {
    "synthesis": "Fil conducteur",
    "identity": "Identite et elan central",
    "inner_life": "Vie interieure et besoins",
    "vocation": "Direction visible",
    "relationships": "Liens et reciprocite",
    "talents": "Appuis disponibles",
    "tensions": "Tensions a integrer",
    "growth": "Axe d'apprentissage",
    "mental_style": "Style mental",
    "values": "Valeurs et ressources",
    "action": "Maniere d'agir",
}
_FAMILY_LABELS = {
    NatalFactFamily.LUMINARY: "Luminaire",
    NatalFactFamily.ANGLE: "Angle natal",
    NatalFactFamily.PLANET_POSITION: "Position planetaire",
    NatalFactFamily.HOUSE_EMPHASIS: "Maison mise en avant",
    NatalFactFamily.SIGN_EMPHASIS: "Signe mis en avant",
    NatalFactFamily.ELEMENT_BALANCE: "Element dominant",
    NatalFactFamily.MODALITY_BALANCE: "Modalite dominante",
    NatalFactFamily.ASPECT: "Aspect",
    NatalFactFamily.RULERSHIP: "Maitrise",
    NatalFactFamily.CONDITION: "Condition planetaire",
    NatalFactFamily.NODE: "Axe nodal",
}
_HOUSE_SECTION_OVERRIDES = {
    "house:4": "inner_life",
    "house:7": "relationships",
    "house:10": "vocation",
    "house:12": "tensions",
}


@dataclass(frozen=True, slots=True)
class BasicNatalPlanSection:
    """Section inspectable du plan avec ses faits requis et preuves publiques."""

    section_code: str
    heading_intent: str
    target_length_words: int
    theme_codes: tuple[str, ...]
    required_fact_ids: tuple[str, ...]
    forbidden_fact_ids: tuple[str, ...]
    forbidden_fact_families: tuple[str, ...]
    supporting_evidence_ids: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        """Retourne la forme JSON stable exposee aux etapes aval."""
        return {
            "section_code": self.section_code,
            "heading_intent": self.heading_intent,
            "target_length_words": self.target_length_words,
            "theme_codes": list(self.theme_codes),
            "required_fact_ids": list(self.required_fact_ids),
            "forbidden_fact_ids": list(self.forbidden_fact_ids),
            "forbidden_fact_families": list(self.forbidden_fact_families),
            "supporting_evidence_ids": list(self.supporting_evidence_ids),
        }


@dataclass(frozen=True, slots=True)
class BasicNatalPublicEvidence:
    """Preuve vulgarisee autorisee dans le plan public inspectable."""

    id: str
    label: str
    explanation: str
    source_section_codes: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        """Retourne la forme JSON publique sans trace interne brute."""
        return {
            "id": self.id,
            "label": self.label,
            "explanation": self.explanation,
            "source_section_codes": list(self.source_section_codes),
        }


@dataclass(frozen=True, slots=True)
class BasicNatalReadingPlan:
    """Contrat inspectable qui cadre la lecture Basic avant tout appel LLM."""

    level: Literal["basic"]
    locale: str
    engine_version: Literal["basic-natal-reading-v1"]
    sections: tuple[BasicNatalPlanSection, ...]
    public_evidence: tuple[BasicNatalPublicEvidence, ...]
    style_constraints: tuple[str, ...]
    limitations: tuple[str, ...]
    disclaimers: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        """Retourne le contrat JSON stable du plan de lecture Basic."""
        return {
            "level": self.level,
            "locale": self.locale,
            "engine_version": self.engine_version,
            "sections": [section.to_payload() for section in self.sections],
            "public_evidence": [evidence.to_payload() for evidence in self.public_evidence],
            "style_constraints": list(self.style_constraints),
            "limitations": list(self.limitations),
            "disclaimers": list(self.disclaimers),
        }


@dataclass(frozen=True, slots=True)
class BasicNatalReadingPlanBuilder:
    """Assemble un plan Basic depuis les contrats de faits, salience et themes."""

    max_sections: int = MAX_READING_PLAN_SECTIONS

    def build(
        self,
        *,
        eligibility_context: EligibilityContext,
        fact_graph: NatalFactGraph,
        salience_model: NatalSalienceModel,
        themes: Sequence[ThemeModel],
        synthesis_resolver: SynthesisResolver,
        locale: str = "fr-FR",
    ) -> BasicNatalReadingPlan:
        """Construit le plan inspectable sans produire de prose finale."""
        salience_audit = salience_model.score(fact_graph, eligibility_context)
        syntheses = synthesis_resolver.resolve(themes, eligibility_context=eligibility_context)
        candidate_sections = _candidate_sections(
            themes=themes,
            syntheses=syntheses,
            fact_graph=fact_graph,
            salience_audit=salience_audit,
            eligibility_context=eligibility_context,
        )
        selected_sections = _select_sections(
            candidate_sections,
            eligibility_context=eligibility_context,
            max_sections=self.max_sections,
        )
        selected_sections = _sections_with_public_evidence_ids(selected_sections)
        public_evidence = _public_evidence_for_sections(selected_sections, fact_graph)
        limitations = tuple(dict.fromkeys((*eligibility_context.limitations, _PUBLIC_LIMITATION)))
        return BasicNatalReadingPlan(
            level=BASIC_NATAL_READING_PLAN_LEVEL,
            locale=locale,
            engine_version=BASIC_NATAL_READING_PLAN_ENGINE_VERSION,
            sections=selected_sections,
            public_evidence=public_evidence,
            style_constraints=_STYLE_CONSTRAINTS,
            limitations=limitations,
            disclaimers=(_PUBLIC_DISCLAIMER,),
        )


def _candidate_sections(
    *,
    themes: Sequence[ThemeModel],
    syntheses: Sequence[ResolvedThemeSynthesis],
    fact_graph: NatalFactGraph,
    salience_audit: NatalSalienceAudit,
    eligibility_context: EligibilityContext,
) -> tuple[BasicNatalPlanSection, ...]:
    """Construit les sections eligibles avant arbitrage de budget."""
    fact_by_id = {fact.fact_id: fact for fact in fact_graph.facts}
    synthesis_by_theme = {synthesis.theme_code: synthesis for synthesis in syntheses}
    forbidden_families = _forbidden_fact_families(eligibility_context)
    sections: list[BasicNatalPlanSection] = []
    synthesis_section = _synthesis_section(
        themes=themes,
        syntheses=syntheses,
        fact_by_id=fact_by_id,
        salience_audit=salience_audit,
        eligibility_context=eligibility_context,
        forbidden_families=forbidden_families,
    )
    if synthesis_section is not None:
        sections.append(synthesis_section)

    for theme in themes:
        synthesis = synthesis_by_theme.get(theme.theme_code)
        if synthesis is None or not synthesis.section_eligible:
            continue
        section = _section_for_theme(
            theme,
            fact_by_id=fact_by_id,
            salience_audit=salience_audit,
            eligibility_context=eligibility_context,
            forbidden_families=forbidden_families,
        )
        if section is not None:
            sections.append(section)
    return tuple(sections)


def _synthesis_section(
    *,
    themes: Sequence[ThemeModel],
    syntheses: Sequence[ResolvedThemeSynthesis],
    fact_by_id: Mapping[str, NatalFact],
    salience_audit: NatalSalienceAudit,
    eligibility_context: EligibilityContext,
    forbidden_families: tuple[NatalFactFamily, ...],
) -> BasicNatalPlanSection | None:
    """Cree la section de fil conducteur depuis les themes les mieux prouves."""
    eligible_codes = {synthesis.theme_code for synthesis in syntheses if synthesis.section_eligible}
    selected_themes = tuple(theme for theme in themes if theme.theme_code in eligible_codes)
    if len(selected_themes) < 2:
        return None
    ordered_fact_ids = _ordered_allowed_fact_ids(
        tuple(fact_id for theme in selected_themes[:3] for fact_id in theme.selected_fact_ids),
        fact_by_id=fact_by_id,
        salience_audit=salience_audit,
        eligibility_context=eligibility_context,
        forbidden_families=forbidden_families,
    )
    if not ordered_fact_ids:
        return None
    theme_codes = tuple(theme.theme_code.value for theme in selected_themes[:3])
    return BasicNatalPlanSection(
        section_code="synthesis",
        heading_intent=_SECTION_LABELS["synthesis"],
        target_length_words=MAX_SECTION_TARGET_WORDS,
        theme_codes=theme_codes,
        required_fact_ids=ordered_fact_ids[:5],
        forbidden_fact_ids=(),
        forbidden_fact_families=tuple(family.value for family in forbidden_families),
        supporting_evidence_ids=(),
    )


def _section_for_theme(
    theme: ThemeModel,
    *,
    fact_by_id: Mapping[str, NatalFact],
    salience_audit: NatalSalienceAudit,
    eligibility_context: EligibilityContext,
    forbidden_families: tuple[NatalFactFamily, ...],
) -> BasicNatalPlanSection | None:
    """Transforme un theme actif en section prouvee et publiquement inspectable."""
    required_fact_ids = _ordered_allowed_fact_ids(
        theme.selected_fact_ids,
        fact_by_id=fact_by_id,
        salience_audit=salience_audit,
        eligibility_context=eligibility_context,
        forbidden_families=forbidden_families,
    )
    if not required_fact_ids:
        return None
    section_code = _section_code_for_theme(theme, required_fact_ids, fact_by_id)
    forbidden_fact_ids = tuple(
        fact_id
        for fact_id in theme.do_not_mention
        if fact_id in fact_by_id and fact_id not in required_fact_ids
    )
    return BasicNatalPlanSection(
        section_code=section_code,
        heading_intent=_SECTION_LABELS[section_code],
        target_length_words=_target_length_words(theme),
        theme_codes=(theme.theme_code.value,),
        required_fact_ids=required_fact_ids,
        forbidden_fact_ids=forbidden_fact_ids,
        forbidden_fact_families=tuple(family.value for family in forbidden_families),
        supporting_evidence_ids=(),
    )


def _ordered_allowed_fact_ids(
    fact_ids: Sequence[str],
    *,
    fact_by_id: Mapping[str, NatalFact],
    salience_audit: NatalSalienceAudit,
    eligibility_context: EligibilityContext,
    forbidden_families: tuple[NatalFactFamily, ...],
) -> tuple[str, ...]:
    """Filtre puis ordonne les faits selon la salience canonique deja calculee."""
    salience_rank = {
        decision.fact_id: (decision.exclusion_reason is not None, -decision.salience_score)
        for decision in salience_audit.decisions
    }
    allowed = tuple(
        dict.fromkeys(
            fact_id
            for fact_id in fact_ids
            if (fact := fact_by_id.get(fact_id)) is not None
            and _fact_allowed(fact, eligibility_context, forbidden_families)
        )
    )
    return tuple(
        sorted(
            allowed,
            key=lambda fact_id: (*salience_rank.get(fact_id, (True, 0.0)), fact_id),
        )
    )


def _fact_allowed(
    fact: NatalFact,
    eligibility_context: EligibilityContext,
    forbidden_families: tuple[NatalFactFamily, ...],
) -> bool:
    """Applique les gates d'eligibilite sans inventer de chemin secondaire."""
    if fact.family in forbidden_families:
        return False
    if fact.requires_birth_time and not (
        eligibility_context.can_use_houses
        or eligibility_context.can_use_angles
        or eligibility_context.can_use_house_rulers
    ):
        return False
    if not eligibility_context.can_use_houses and _objects_include_house(fact.objects):
        return False
    if not eligibility_context.can_use_angles and set(fact.objects).intersection(_ANGLE_OBJECTS):
        return False
    return True


def _select_sections(
    sections: Sequence[BasicNatalPlanSection],
    *,
    eligibility_context: EligibilityContext,
    max_sections: int,
) -> tuple[BasicNatalPlanSection, ...]:
    """Selectionne au plus huit sections puis restaure l'ordre editorial stable."""
    order = (
        _DATE_ONLY_SECTION_ORDER
        if eligibility_context.birth_time_status == "date_only"
        else _FULL_SECTION_ORDER
    )
    strongest_by_code: dict[str, BasicNatalPlanSection] = {}
    for section in sorted(sections, key=_section_strength_sort_key):
        strongest_by_code.setdefault(section.section_code, section)
    pinned_codes = {"synthesis", "identity", "inner_life"}
    selected_by_code = {
        code: section for code, section in strongest_by_code.items() if code in pinned_codes
    }
    for section in sorted(strongest_by_code.values(), key=_section_strength_sort_key):
        if section.section_code in selected_by_code:
            continue
        selected_by_code[section.section_code] = section
        if len(selected_by_code) >= max_sections:
            break
    return tuple(selected_by_code[code] for code in order if code in selected_by_code)


def _sections_with_public_evidence_ids(
    sections: Sequence[BasicNatalPlanSection],
) -> tuple[BasicNatalPlanSection, ...]:
    """Attribue des identifiants publics opaques sans reutiliser les fact_id internes."""
    evidence_id_by_fact_id: dict[str, str] = {}
    next_index = 1
    normalized_sections: list[BasicNatalPlanSection] = []
    for section in sections:
        supporting_evidence_ids: list[str] = []
        for fact_id in section.required_fact_ids:
            evidence_id = evidence_id_by_fact_id.get(fact_id)
            if evidence_id is None:
                evidence_id = f"pe-{next_index:03d}"
                evidence_id_by_fact_id[fact_id] = evidence_id
                next_index += 1
            supporting_evidence_ids.append(evidence_id)
        normalized_sections.append(
            replace(section, supporting_evidence_ids=tuple(supporting_evidence_ids))
        )
    return tuple(normalized_sections)


def _section_strength_sort_key(section: BasicNatalPlanSection) -> tuple[int, int, str]:
    """Favorise les sections les mieux documentees quand le budget est atteint."""
    synthesis_bonus = 0 if section.section_code == "synthesis" else 1
    return (synthesis_bonus, -len(section.required_fact_ids), section.section_code)


def _section_code_for_theme(
    theme: ThemeModel,
    required_fact_ids: Sequence[str],
    fact_by_id: Mapping[str, NatalFact],
) -> str:
    """Route un theme vers la section canonique, avec archetypes maison explicites."""
    objects = tuple(
        object_code for fact_id in required_fact_ids for object_code in fact_by_id[fact_id].objects
    )
    for house_marker, section_code in _HOUSE_SECTION_OVERRIDES.items():
        if house_marker in objects:
            return section_code
    return _THEME_SECTION_CODES[theme.theme_code]


def _target_length_words(theme: ThemeModel) -> int:
    """Calibre une longueur courte sans augmenter le budget Basic."""
    if theme.activation_score >= 120.0:
        return MAX_SECTION_TARGET_WORDS
    if theme.activation_score >= 70.0:
        return 130
    return MIN_SECTION_TARGET_WORDS


def _forbidden_fact_families(
    eligibility_context: EligibilityContext,
) -> tuple[NatalFactFamily, ...]:
    """Retourne les familles interdites par le contexte horaire Basic."""
    if eligibility_context.birth_time_status == "date_only":
        return tuple(sorted(_DATE_ONLY_FORBIDDEN_FAMILIES, key=lambda family: family.value))
    return ()


def _public_evidence_for_sections(
    sections: Sequence[BasicNatalPlanSection],
    fact_graph: NatalFactGraph,
) -> tuple[BasicNatalPublicEvidence, ...]:
    """Construit des preuves publiques lisibles depuis les faits requis."""
    fact_by_id = {fact.fact_id: fact for fact in fact_graph.facts}
    fact_by_evidence_id: dict[str, NatalFact] = {}
    section_codes_by_evidence: dict[str, list[str]] = {}
    for section in sections:
        for fact_id, evidence_id in zip(
            section.required_fact_ids, section.supporting_evidence_ids, strict=True
        ):
            fact = fact_by_id.get(fact_id)
            if fact is not None:
                fact_by_evidence_id.setdefault(evidence_id, fact)
            section_codes_by_evidence.setdefault(evidence_id, []).append(section.section_code)
    evidence_items: list[BasicNatalPublicEvidence] = []
    for evidence_id in sorted(section_codes_by_evidence, key=_public_evidence_sort_key):
        fact = fact_by_evidence_id.get(evidence_id)
        if fact is None:
            continue
        evidence_items.append(
            BasicNatalPublicEvidence(
                id=evidence_id,
                label=_public_label(fact),
                explanation=_public_explanation(fact),
                source_section_codes=tuple(dict.fromkeys(section_codes_by_evidence[evidence_id])),
            )
        )
    return tuple(evidence_items)


def _public_evidence_sort_key(evidence_id: str) -> tuple[str, str]:
    """Trie les preuves publiques par numero local puis libelle."""
    prefix, _, suffix = evidence_id.partition("-")
    return (prefix, suffix)


def _public_label(fact: NatalFact) -> str:
    """Produit un libelle lisible sans chemin de source ni score."""
    family_label = _FAMILY_LABELS[fact.family]
    object_label = ", ".join(_readable_object(item) for item in fact.objects[:3])
    return f"{family_label}: {object_label}"


def _public_explanation(fact: NatalFact) -> str:
    """Explique une preuve au lecteur sans fuite de scoring interne."""
    objects = ", ".join(_readable_object(item) for item in fact.objects[:3])
    return (
        f"Ce repere retient {objects} comme matiere astrologique disponible "
        "pour cadrer le theme, avec une confiance editoriale controlee."
    )


def _readable_object(value: str) -> str:
    """Transforme les codes runtime simples en mots lisibles."""
    return value.replace("house:", "maison ").replace("_", " ")


def _objects_include_house(objects: Sequence[str]) -> bool:
    """Detecte les references de maison dans les objets deja projetes."""
    return any(item.startswith(_HOUSE_MARKERS) for item in objects)

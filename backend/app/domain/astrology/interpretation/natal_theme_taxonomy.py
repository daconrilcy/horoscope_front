# Commentaire global: ce module definit la taxonomie narrative interne des themes natals Basic.
"""Taxonomie versionnee et activation deterministe des themes narratifs Basic."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from app.domain.astrology.interpretation.basic_natal_eligibility import (
    BirthTimeStatus,
    EligibilityContext,
)
from app.domain.astrology.interpretation.natal_fact_graph import (
    NatalFact,
    NatalFactFamily,
    NatalFactGraph,
)
from app.domain.astrology.interpretation.natal_salience_model import (
    NatalSalienceAudit,
    NatalSalienceDecision,
    NatalSalienceLevel,
)
from app.domain.astrology.reading.basic_natal_contracts import (
    BASIC_NATAL_THEME_TAXONOMY_VERSION,
)

NATAL_NARRATIVE_THEME_TAXONOMY_VERSION = BASIC_NATAL_THEME_TAXONOMY_VERSION
MIN_THEME_FACTS = 2
MIN_AUTONOMOUS_THEME_SCORE = 60.0


class BasicThemeCode(StrEnum):
    """Codes canoniques des dix themes narratifs Basic."""

    CORE_IDENTITY = "core_identity"
    EMOTIONAL_PATTERN = "emotional_pattern"
    PUBLIC_VOCATION = "public_vocation"
    RELATIONSHIP_PATTERN = "relationship_pattern"
    MENTAL_STYLE = "mental_style"
    RESOURCES_AND_VALUES = "resources_and_values"
    ACTION_AND_DRIVE = "action_and_drive"
    GROWTH_DIRECTION = "growth_direction"
    TENSION_TO_INTEGRATE = "tension_to_integrate"
    TALENTS_AND_SUPPORTS = "talents_and_supports"


@dataclass(frozen=True, slots=True)
class ThemeDefinition:
    """Definition stable d'un theme et de ses contraintes editoriales."""

    theme_code: BasicThemeCode
    priority_level: int
    trigger_families: tuple[NatalFactFamily, ...]
    trigger_objects: tuple[str, ...]
    exclusions: tuple[str, ...]
    availability: tuple[BirthTimeStatus, ...]
    compatible_sections: tuple[str, ...]
    advised_vocabulary: tuple[str, ...]
    forbidden_formulations: tuple[str, ...]
    hierarchy_parent: BasicThemeCode | None = None
    requires_houses: bool = False
    requires_angles: bool = False
    requires_house_rulers: bool = False
    tension_objects: tuple[str, ...] = ()

    def to_contract_payload(self) -> dict[str, Any]:
        """Retourne la forme JSON interne de la definition de theme."""
        payload: dict[str, Any] = {
            "theme_code": self.theme_code.value,
            "priority_level": self.priority_level,
            "triggers": {
                "families": [family.value for family in self.trigger_families],
                "objects": list(self.trigger_objects),
            },
            "exclusions": list(self.exclusions),
            "availability": list(self.availability),
            "compatible_sections": list(self.compatible_sections),
            "advised_vocabulary": list(self.advised_vocabulary),
            "forbidden_formulations": list(self.forbidden_formulations),
        }
        if self.hierarchy_parent is not None:
            payload["hierarchy_parent"] = self.hierarchy_parent.value
        return payload


@dataclass(frozen=True, slots=True)
class ThemeModel:
    """Theme actif avec metadonnees d'activation et faits selectionnes."""

    taxonomy_version: str
    theme_code: BasicThemeCode
    activation_score: float
    priority_level: int
    resources: tuple[str, ...]
    constraints: tuple[str, ...]
    tensions: tuple[str, ...]
    must_mention: tuple[str, ...]
    may_mention: tuple[str, ...]
    do_not_mention: tuple[str, ...]
    availability: tuple[BirthTimeStatus, ...]
    compatible_sections: tuple[str, ...]
    advised_vocabulary: tuple[str, ...]
    forbidden_formulations: tuple[str, ...]
    activation_metadata: Mapping[str, Any]

    @property
    def selected_fact_ids(self) -> tuple[str, ...]:
        """Regroupe les faits retenus pour tracer la selection du theme."""
        return tuple(
            dict.fromkeys(
                (
                    *self.resources,
                    *self.constraints,
                    *self.tensions,
                    *self.must_mention,
                    *self.may_mention,
                )
            )
        )

    def to_internal_payload(self) -> dict[str, Any]:
        """Retourne une forme auditable non destinee aux champs narratifs publics."""
        return {
            "taxonomy_version": self.taxonomy_version,
            "theme_code": self.theme_code.value,
            "activation_score": self.activation_score,
            "priority_level": self.priority_level,
            "resources": list(self.resources),
            "constraints": list(self.constraints),
            "tensions": list(self.tensions),
            "must_mention": list(self.must_mention),
            "may_mention": list(self.may_mention),
            "do_not_mention": list(self.do_not_mention),
            "selected_fact_ids": list(self.selected_fact_ids),
            "availability": list(self.availability),
            "compatible_sections": list(self.compatible_sections),
            "advised_vocabulary": list(self.advised_vocabulary),
            "forbidden_formulations": list(self.forbidden_formulations),
            "activation_metadata": dict(self.activation_metadata),
        }


class NatalNarrativeThemeTaxonomy:
    """Catalogue canonique et activateur des themes narratifs Basic."""

    version = NATAL_NARRATIVE_THEME_TAXONOMY_VERSION

    def __init__(
        self,
        definitions: Sequence[ThemeDefinition] = (),
    ) -> None:
        """Initialise le catalogue avec les definitions Basic canoniques."""
        self._definitions = tuple(definitions) if definitions else _default_theme_definitions()
        self._definition_by_code = {
            definition.theme_code: definition for definition in self._definitions
        }
        if tuple(self._definition_by_code) != tuple(BasicThemeCode):
            raise ValueError("Basic theme taxonomy requires the ten canonical theme codes")

    @property
    def catalog(self) -> tuple[ThemeDefinition, ...]:
        """Expose le catalogue ordonne par priorite editoriale stable."""
        return self._definitions

    def to_contract_payload(self) -> dict[str, Any]:
        """Expose la version et le catalogue pour les preuves de contrat."""
        return {
            "taxonomy_version": self.version,
            "theme_codes": [definition.theme_code.value for definition in self._definitions],
            "themes": [definition.to_contract_payload() for definition in self._definitions],
        }

    def activate(
        self,
        *,
        graph: NatalFactGraph,
        salience_audit: NatalSalienceAudit,
        eligibility_context: EligibilityContext,
    ) -> tuple[ThemeModel, ...]:
        """Active les themes depuis les faits priorises sans recalcul astrologique."""
        fact_by_id = {fact.fact_id: fact for fact in graph.facts}
        decisions_by_id = {
            decision.fact_id: decision for decision in salience_audit.included_decisions
        }
        active_themes = [
            theme
            for definition in self._definitions
            if self._definition_available(definition, eligibility_context)
            for theme in (self._activate_definition(definition, fact_by_id, decisions_by_id),)
            if theme is not None
        ]
        return tuple(sorted(_drop_redundant_children(active_themes), key=_theme_sort_key))

    def _activate_definition(
        self,
        definition: ThemeDefinition,
        fact_by_id: Mapping[str, NatalFact],
        decisions_by_id: Mapping[str, NatalSalienceDecision],
    ) -> ThemeModel | None:
        """Construit un theme actif si les signaux inclus sont assez solides."""
        matched_facts = tuple(
            fact
            for fact_id, fact in fact_by_id.items()
            if fact_id in decisions_by_id and _matches_definition(fact, definition)
        )
        if not matched_facts:
            return None

        matched_ids = tuple(fact.fact_id for fact in matched_facts)
        decisions = tuple(decisions_by_id[fact_id] for fact_id in matched_ids)
        score = round(sum(decision.salience_score for decision in decisions), 3)
        has_pillar_or_high = any(
            decision.salience_level in {NatalSalienceLevel.PILLAR, NatalSalienceLevel.HIGH}
            for decision in decisions
        )
        if len(matched_ids) < MIN_THEME_FACTS and not (
            has_pillar_or_high and score >= MIN_AUTONOMOUS_THEME_SCORE
        ):
            return None

        constraints = _ids_for_families(matched_facts, {NatalFactFamily.CONDITION})
        tensions = _ids_for_tensions(matched_facts, definition)
        resources = tuple(
            fact.fact_id for fact in matched_facts if fact.fact_id not in constraints + tensions
        )
        mandatory_fact_ids = set(constraints + tensions)
        must_mention = tuple(
            fact_id
            for fact_id, decision in zip(matched_ids, decisions, strict=True)
            if decision.salience_level in {NatalSalienceLevel.PILLAR, NatalSalienceLevel.HIGH}
            or fact_id in mandatory_fact_ids
        )
        may_mention = tuple(fact_id for fact_id in matched_ids if fact_id not in must_mention)
        do_not_mention = tuple(
            sorted(
                fact_id
                for fact_id in fact_by_id
                if fact_id not in matched_ids
                and _shares_theme_surface(fact_by_id[fact_id], definition)
            )
        )

        return ThemeModel(
            taxonomy_version=self.version,
            theme_code=definition.theme_code,
            activation_score=score,
            priority_level=definition.priority_level,
            resources=resources,
            constraints=constraints,
            tensions=tensions,
            must_mention=must_mention,
            may_mention=may_mention,
            do_not_mention=do_not_mention,
            availability=definition.availability,
            compatible_sections=definition.compatible_sections,
            advised_vocabulary=definition.advised_vocabulary,
            forbidden_formulations=definition.forbidden_formulations,
            activation_metadata={
                "matched_fact_count": len(matched_ids),
                "matched_objects": sorted(
                    {matched_object for fact in matched_facts for matched_object in fact.objects}
                ),
                "highest_salience_level": min(
                    decision.salience_level.value for decision in decisions
                ),
                "reason_codes": sorted(
                    {reason for decision in decisions for reason in decision.reason_codes}
                ),
            },
        )

    @staticmethod
    def _definition_available(
        definition: ThemeDefinition,
        eligibility_context: EligibilityContext,
    ) -> bool:
        """Applique les contraintes d'heure de naissance du catalogue."""
        if eligibility_context.birth_time_status not in definition.availability:
            return False
        if definition.requires_houses and not eligibility_context.can_use_houses:
            return False
        if definition.requires_angles and not eligibility_context.can_use_angles:
            return False
        if definition.requires_house_rulers and not eligibility_context.can_use_house_rulers:
            return False
        return True


def _default_theme_definitions() -> tuple[ThemeDefinition, ...]:
    """Declare en un seul endroit les dix themes Basic versionnes."""
    all_statuses: tuple[BirthTimeStatus, ...] = (
        "full_birth_time",
        "approximate_birth_time",
        "date_only",
    )
    timed_statuses: tuple[BirthTimeStatus, ...] = ("full_birth_time", "approximate_birth_time")
    guarded_formulations = (
        "fatalisme absolu",
        "promesse garantie",
        "diagnostic psychologique",
        "jugement essentialisant",
        "qualificatif sans preuve",
    )
    return (
        ThemeDefinition(
            theme_code=BasicThemeCode.CORE_IDENTITY,
            priority_level=10,
            trigger_families=(NatalFactFamily.LUMINARY, NatalFactFamily.SIGN_EMPHASIS),
            trigger_objects=("sun",),
            exclusions=("surface horaire absente",),
            availability=all_statuses,
            compatible_sections=("identity_anchor", "life_orientation"),
            advised_vocabulary=("identite", "elan", "coherence", "orientation"),
            forbidden_formulations=guarded_formulations,
        ),
        ThemeDefinition(
            theme_code=BasicThemeCode.EMOTIONAL_PATTERN,
            priority_level=20,
            trigger_families=(NatalFactFamily.LUMINARY, NatalFactFamily.ELEMENT_BALANCE),
            trigger_objects=("moon", "water"),
            exclusions=("materiau lunaire absent",),
            availability=all_statuses,
            compatible_sections=("emotional_needs", "inner_rhythm"),
            advised_vocabulary=("besoin", "rythme", "securite", "reaction"),
            forbidden_formulations=guarded_formulations,
        ),
        ThemeDefinition(
            theme_code=BasicThemeCode.PUBLIC_VOCATION,
            priority_level=30,
            trigger_families=(
                NatalFactFamily.ANGLE,
                NatalFactFamily.HOUSE_EMPHASIS,
                NatalFactFamily.RULERSHIP,
            ),
            trigger_objects=("mc", "house:10", "angular"),
            exclusions=("date-only", "maison dix non fiable"),
            availability=timed_statuses,
            compatible_sections=("public_direction", "work_visibility"),
            advised_vocabulary=("direction", "place", "responsabilite", "contribution"),
            forbidden_formulations=guarded_formulations,
            requires_houses=True,
            requires_angles=True,
        ),
        ThemeDefinition(
            theme_code=BasicThemeCode.RELATIONSHIP_PATTERN,
            priority_level=40,
            trigger_families=(NatalFactFamily.HOUSE_EMPHASIS, NatalFactFamily.PLANET_POSITION),
            trigger_objects=("venus", "house:7", "desc"),
            exclusions=("partenariat non etaye",),
            availability=all_statuses,
            compatible_sections=("relationship_style", "bonding_needs"),
            advised_vocabulary=("lien", "accord", "reciprocite", "attachement"),
            forbidden_formulations=guarded_formulations,
        ),
        ThemeDefinition(
            theme_code=BasicThemeCode.MENTAL_STYLE,
            priority_level=50,
            trigger_families=(NatalFactFamily.PLANET_POSITION, NatalFactFamily.ASPECT),
            trigger_objects=("mercury", "gemini", "virgo"),
            exclusions=("style mental non recurrent",),
            availability=all_statuses,
            compatible_sections=("mental_process", "communication"),
            advised_vocabulary=("analyse", "langage", "tri", "curiosite"),
            forbidden_formulations=guarded_formulations,
        ),
        ThemeDefinition(
            theme_code=BasicThemeCode.RESOURCES_AND_VALUES,
            priority_level=60,
            trigger_families=(NatalFactFamily.PLANET_POSITION, NatalFactFamily.HOUSE_EMPHASIS),
            trigger_objects=("venus", "taurus", "house:2"),
            exclusions=("valeur isolee sans repetition",),
            availability=all_statuses,
            compatible_sections=("values", "resources"),
            advised_vocabulary=("valeur", "ressource", "stabilite", "choix"),
            forbidden_formulations=guarded_formulations,
        ),
        ThemeDefinition(
            theme_code=BasicThemeCode.ACTION_AND_DRIVE,
            priority_level=70,
            trigger_families=(NatalFactFamily.PLANET_POSITION, NatalFactFamily.HOUSE_EMPHASIS),
            trigger_objects=("mars", "aries", "house:1"),
            exclusions=("impulsion non centrale",),
            availability=all_statuses,
            compatible_sections=("action_style", "initiative"),
            advised_vocabulary=("initiative", "energie", "decision", "rythme"),
            forbidden_formulations=guarded_formulations,
        ),
        ThemeDefinition(
            theme_code=BasicThemeCode.GROWTH_DIRECTION,
            priority_level=80,
            trigger_families=(NatalFactFamily.NODE, NatalFactFamily.RULERSHIP),
            trigger_objects=("north_node", "south_node"),
            exclusions=("noeud isole", "noeud par maison indisponible"),
            availability=all_statuses,
            compatible_sections=("growth_axis", "learning_direction"),
            advised_vocabulary=("apprentissage", "direction", "ajustement", "progression"),
            forbidden_formulations=guarded_formulations,
        ),
        ThemeDefinition(
            theme_code=BasicThemeCode.TENSION_TO_INTEGRATE,
            priority_level=90,
            trigger_families=(NatalFactFamily.ASPECT, NatalFactFamily.CONDITION),
            trigger_objects=("square", "opposition", "detriment", "fall", "retrograde", "combust"),
            exclusions=("contrainte mineure",),
            availability=all_statuses,
            compatible_sections=("integration_tension", "inner_work"),
            advised_vocabulary=("tension", "ajustement", "arbitrage", "integration"),
            forbidden_formulations=guarded_formulations,
            tension_objects=("square", "opposition", "detriment", "fall", "retrograde", "combust"),
        ),
        ThemeDefinition(
            theme_code=BasicThemeCode.TALENTS_AND_SUPPORTS,
            priority_level=100,
            trigger_families=(NatalFactFamily.ASPECT, NatalFactFamily.CONDITION),
            trigger_objects=("trine", "sextile", "domicile", "exaltation"),
            exclusions=("facilite isolee",),
            availability=all_statuses,
            compatible_sections=("supports", "available_strengths"),
            advised_vocabulary=("appui", "facilite", "soutien", "competence"),
            forbidden_formulations=guarded_formulations,
            hierarchy_parent=BasicThemeCode.TENSION_TO_INTEGRATE,
        ),
    )


def _matches_definition(fact: NatalFact, definition: ThemeDefinition) -> bool:
    """Verifie si un fait inclus nourrit le theme sans recalculer sa portee."""
    return fact.family in definition.trigger_families and (
        not definition.trigger_objects
        or bool(set(fact.objects).intersection(definition.trigger_objects))
    )


def _shares_theme_surface(fact: NatalFact, definition: ThemeDefinition) -> bool:
    """Repere les faits voisins a exclure de la redaction du meme theme."""
    if bool(set(fact.objects).intersection(definition.trigger_objects)):
        return True
    return fact.family in definition.trigger_families and bool(definition.tension_objects)


def _ids_for_families(
    facts: Sequence[NatalFact],
    families: set[NatalFactFamily],
) -> tuple[str, ...]:
    """Selectionne les identifiants de faits appartenant a certaines familles."""
    return tuple(fact.fact_id for fact in facts if fact.family in families)


def _ids_for_tensions(
    facts: Sequence[NatalFact],
    definition: ThemeDefinition,
) -> tuple[str, ...]:
    """Selectionne les faits de tension declares par la definition du theme."""
    tension_objects = set(definition.tension_objects)
    return tuple(
        fact.fact_id
        for fact in facts
        if tension_objects and tension_objects.intersection(fact.objects)
    )


def _drop_redundant_children(themes: Sequence[ThemeModel]) -> tuple[ThemeModel, ...]:
    """Supprime un theme enfant quand le parent couvre deja la meme matiere."""
    theme_by_code = {theme.theme_code: theme for theme in themes}
    definition_by_code = {
        definition.theme_code: definition for definition in _default_theme_definitions()
    }
    return tuple(
        theme
        for theme in themes
        if not _covered_by_redundant_parent(
            theme,
            theme_by_code=theme_by_code,
            definition_by_code=definition_by_code,
        )
    )


def _covered_by_redundant_parent(
    theme: ThemeModel,
    *,
    theme_by_code: Mapping[BasicThemeCode, ThemeModel],
    definition_by_code: Mapping[BasicThemeCode, ThemeDefinition],
) -> bool:
    """Detecte uniquement les themes enfants qui partagent la matiere du parent."""
    parent_code = definition_by_code[theme.theme_code].hierarchy_parent
    if parent_code is None or parent_code not in theme_by_code:
        return False
    return _themes_share_surface(theme, theme_by_code[parent_code])


def _themes_share_surface(theme: ThemeModel, parent_theme: ThemeModel) -> bool:
    """Compare les objets source pour eviter de masquer un appui distinct."""
    theme_objects = set(theme.activation_metadata.get("matched_objects", ()))
    parent_objects = set(parent_theme.activation_metadata.get("matched_objects", ()))
    return bool(theme_objects.intersection(parent_objects))


def _theme_sort_key(theme: ThemeModel) -> tuple[int, float, str]:
    """Trie les themes par priorite catalogue puis score decroissant."""
    return (theme.priority_level, -theme.activation_score, theme.theme_code.value)

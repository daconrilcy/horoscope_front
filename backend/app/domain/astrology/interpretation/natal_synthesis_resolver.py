# Commentaire global: ce module resout les themes natals Basic en syntheses editoriales internes.
"""Resolution deterministe des contradictions dans les themes natals Basic."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from app.domain.astrology.interpretation.basic_natal_eligibility import EligibilityContext
from app.domain.astrology.interpretation.natal_theme_taxonomy import (
    MIN_AUTONOMOUS_THEME_SCORE,
    BasicThemeCode,
    ThemeModel,
)

NATAL_SYNTHESIS_RESOLVER_VERSION = "natal_synthesis.basic.v1"

_STRONG_SIGNAL_THRESHOLD = MIN_AUTONOMOUS_THEME_SCORE
_HIGH_CONFIDENCE_THRESHOLD = 150.0
_MEDIUM_CONFIDENCE_THRESHOLD = 90.0
_WEAK_AUTONOMOUS_FACT_LIMIT = 1
_BIRTH_TIME_OBJECTS = frozenset(("asc", "mc", "desc"))
_BIRTH_TIME_PREFIXES = ("house:",)
_FORBIDDEN_WORD_PARTS = (
    ("tou", "jours"),
    ("ja", "mais"),
    ("des", "tin"),
    ("ob", "lige"),
    ("doit ", "absolument"),
    ("medi", "cal"),
    ("juri", "dique"),
    ("finan", "cier"),
)
_FORBIDDEN_WORDING_PATTERN = re.compile(
    "|".join(re.escape("".join(parts)) for parts in _FORBIDDEN_WORD_PARTS),
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class ResolvedThemeSynthesis:
    """Synthese editoriale structuree, separee du texte public final."""

    theme_code: BasicThemeCode
    core_statement: str
    resource_statement: str
    constraint_statement: str
    integration_statement: str
    confidence: str
    section_eligible: bool = True
    merge_group: str | None = None
    omission_reason: str | None = None

    def to_internal_payload(self) -> dict[str, Any]:
        """Expose le contrat interne attendu par les etapes editoriales aval."""
        payload: dict[str, Any] = {
            "theme_code": self.theme_code.value,
            "core_statement": self.core_statement,
            "resource_statement": self.resource_statement,
            "constraint_statement": self.constraint_statement,
            "integration_statement": self.integration_statement,
            "confidence": self.confidence,
            "section_eligible": self.section_eligible,
        }
        if self.merge_group is not None:
            payload["merge_group"] = self.merge_group
        if self.omission_reason is not None:
            payload["omission_reason"] = self.omission_reason
        return payload


@dataclass(frozen=True, slots=True)
class SynthesisResolver:
    """Transforme des themes Basic actifs en syntheses internes nuancees."""

    version: str = NATAL_SYNTHESIS_RESOLVER_VERSION

    def resolve(
        self,
        themes: Sequence[ThemeModel],
        *,
        eligibility_context: EligibilityContext,
    ) -> tuple[ResolvedThemeSynthesis, ...]:
        """Resout les themes deja actives sans refaire la detection thematique."""
        merge_groups = _shared_fact_merge_groups(themes)
        syntheses = tuple(
            self._resolve_theme(
                theme,
                eligibility_context=eligibility_context,
                merge_group=merge_groups.get(theme.theme_code),
            )
            for theme in themes
        )
        return tuple(sorted(syntheses, key=_synthesis_sort_key))

    def _resolve_theme(
        self,
        theme: ThemeModel,
        *,
        eligibility_context: EligibilityContext,
        merge_group: str | None,
    ) -> ResolvedThemeSynthesis:
        """Applique les decisions de nuance, eligibilite et formulation controlee."""
        omission_reason = _omission_reason(theme, eligibility_context)
        section_eligible = omission_reason is None
        resource_strength = _signal_strength(theme.resources, theme.activation_score)
        constraint_strength = _signal_strength(theme.constraints, theme.activation_score)
        has_strong_mixed_signals = resource_strength == "strong" and constraint_strength == "strong"

        if omission_reason == "weak_single_fact":
            core_statement = _statement(theme, "reste un indice editorial d'appui")
            resource_statement = _statement(
                theme, "apporte un signal isole a conserver en contexte"
            )
            constraint_statement = _statement(theme, "ne suffit pas a porter une section autonome")
            integration_statement = _statement(
                theme,
                "demande un rattachement a un theme mieux documente",
            )
        elif omission_reason == "birth_time_surface_unavailable":
            core_statement = _statement(theme, "depend d'une surface horaire indisponible")
            resource_statement = _statement(theme, "garde les signaux non horaires en appui")
            constraint_statement = _statement(
                theme,
                "retire les maisons, angles et maitres de maisons du cadrage",
            )
            integration_statement = _statement(
                theme,
                "recentre la synthese sur signes, luminaires, aspects et equilibres",
            )
        else:
            core_statement = _statement(theme, "organise le theme actif avec priorite stable")
            resource_statement = _fact_statement(theme, theme.resources, "ressource")
            constraint_statement = _fact_statement(theme, theme.constraints, "contrainte")
            integration_statement = _integration_statement(theme, has_strong_mixed_signals)

        synthesis = ResolvedThemeSynthesis(
            theme_code=theme.theme_code,
            core_statement=core_statement,
            resource_statement=resource_statement,
            constraint_statement=constraint_statement,
            integration_statement=integration_statement,
            confidence=_confidence_for_theme(theme),
            section_eligible=section_eligible,
            merge_group=merge_group,
            omission_reason=omission_reason,
        )
        _ensure_controlled_wording(synthesis)
        return synthesis


def _shared_fact_merge_groups(themes: Sequence[ThemeModel]) -> dict[BasicThemeCode, str]:
    """Identifie les themes qui racontent la meme surface factuelle."""
    by_facts: dict[tuple[str, ...], list[ThemeModel]] = defaultdict(list)
    for theme in themes:
        by_facts[tuple(sorted(theme.selected_fact_ids))].append(theme)
    groups: dict[BasicThemeCode, str] = {}
    for fact_ids, grouped_themes in by_facts.items():
        if len(grouped_themes) < 2:
            continue
        group_key = "shared:" + "+".join(fact_ids)
        for theme in grouped_themes:
            groups[theme.theme_code] = group_key
    return groups


def _omission_reason(theme: ThemeModel, eligibility_context: EligibilityContext) -> str | None:
    """Retourne la raison de retrait editorial, si le theme ne peut pas etre autonome."""
    if _uses_unavailable_birth_time_surface(theme, eligibility_context):
        return "birth_time_surface_unavailable"
    if (
        len(theme.selected_fact_ids) <= _WEAK_AUTONOMOUS_FACT_LIMIT
        and theme.activation_score < MIN_AUTONOMOUS_THEME_SCORE
    ):
        return "weak_single_fact"
    return None


def _uses_unavailable_birth_time_surface(
    theme: ThemeModel,
    eligibility_context: EligibilityContext,
) -> bool:
    """Detecte les references horaires quand le contexte date-only les interdit."""
    if (
        eligibility_context.can_use_houses
        and eligibility_context.can_use_angles
        and eligibility_context.can_use_house_rulers
    ):
        return False
    objects = set(_metadata_objects(theme))
    has_house_surface = any(item.startswith(_BIRTH_TIME_PREFIXES) for item in objects)
    has_angle_surface = bool(objects.intersection(_BIRTH_TIME_OBJECTS))
    return has_house_surface or has_angle_surface


def _metadata_objects(theme: ThemeModel) -> tuple[str, ...]:
    """Lit les objets de surface deja exposes par l'activation CS-413."""
    raw_objects = theme.activation_metadata.get("matched_objects", ())
    if isinstance(raw_objects, Sequence) and not isinstance(raw_objects, str):
        return tuple(str(item) for item in raw_objects)
    return ()


def _signal_strength(fact_ids: Sequence[str], activation_score: float) -> str:
    """Classe la force d'un paquet de faits sans exposer les scores au public."""
    if fact_ids and activation_score >= _STRONG_SIGNAL_THRESHOLD:
        return "strong"
    if fact_ids:
        return "present"
    return "absent"


def _confidence_for_theme(theme: ThemeModel) -> str:
    """Produit une confiance bornee et non numerique pour le contrat editorial."""
    if theme.activation_score >= _HIGH_CONFIDENCE_THRESHOLD:
        return "high"
    if theme.activation_score >= _MEDIUM_CONFIDENCE_THRESHOLD:
        return "medium"
    return "low"


def _statement(theme: ThemeModel, predicate: str) -> str:
    """Construit une ligne controlee a partir du code theme canonique."""
    return f"{theme.theme_code.value}: {predicate}."


def _fact_statement(theme: ThemeModel, fact_ids: Sequence[str], label: str) -> str:
    """Decrit la presence ou l'absence d'un paquet de faits nommes."""
    if not fact_ids:
        return _statement(theme, f"ne contient pas de {label} distincte")
    count = len(tuple(dict.fromkeys(fact_ids)))
    return _statement(theme, f"integre {count} fait(s) de {label}")


def _integration_statement(theme: ThemeModel, has_strong_mixed_signals: bool) -> str:
    """Formule la synthese des tensions sans prose publique finale."""
    if has_strong_mixed_signals:
        return _statement(
            theme,
            "met en relation l'appui fort et la limite forte dans une nuance explicite",
        )
    if theme.tensions:
        return _statement(theme, "relie les tensions au theme principal avec prudence")
    return _statement(theme, "reste disponible comme entree editoriale structuree")


def _ensure_controlled_wording(synthesis: ResolvedThemeSynthesis) -> None:
    """Bloque les formulations trop absolues ou hors domaine avant l'aval."""
    fields = (
        synthesis.core_statement,
        synthesis.resource_statement,
        synthesis.constraint_statement,
        synthesis.integration_statement,
    )
    for field in fields:
        if _FORBIDDEN_WORDING_PATTERN.search(field):
            raise ValueError("resolved synthesis rejects uncontrolled wording")


def _synthesis_sort_key(synthesis: ResolvedThemeSynthesis) -> tuple[bool, str]:
    """Stabilise l'ordre sans dependance aux details de score."""
    return (not synthesis.section_eligible, synthesis.theme_code.value)

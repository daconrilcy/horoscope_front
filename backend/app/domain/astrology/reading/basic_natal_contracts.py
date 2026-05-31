# Commentaire global: contrats purs du pipeline versionne de lecture natale Basic V2.
"""Modeles Pydantic du socle contractuel Basic natal, sans dependance runtime."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

BASIC_NATAL_LEVEL = "basic"
BASIC_NATAL_ENGINE_VERSION = "basic-natal-reading-v1"
BASIC_NATAL_PUBLIC_SCHEMA_VERSION = "basic_natal_interpretation_v2"
BASIC_NATAL_FACT_TAXONOMY_VERSION = "basic-natal-fact-taxonomy-v1"
BASIC_NATAL_SALIENCE_MODEL_VERSION = "basic-natal-salience-v1"
BASIC_NATAL_THEME_TAXONOMY_VERSION = "basic-natal-theme-taxonomy-v1"
BASIC_NATAL_PLAN_BUILDER_VERSION = "basic-natal-reading-plan-v1"
BASIC_NATAL_PROMPT_VERSION = "basic-natal-draft-prompt-v1"
BASIC_NATAL_VALIDATOR_VERSION = "basic-natal-validator-v1"

_PUBLIC_FORBIDDEN_KEYS = frozenset(
    {
        "ranking_score",
        "condition_axis",
        "score_profile",
        "weighted_score",
        "prompt_hint",
        "audit_input",
        "user_id",
        "provider_id",
        "raw_place_id",
        "backend_trace_id",
    }
)


def _reject_forbidden_public_keys(value: Any) -> Any:
    """Refuse recursivement les cles techniques dans un payload public."""
    if isinstance(value, dict):
        forbidden = _PUBLIC_FORBIDDEN_KEYS.intersection(value)
        if forbidden:
            names = ", ".join(sorted(forbidden))
            raise ValueError(f"forbidden public Basic natal keys: {names}")
        for nested in value.values():
            _reject_forbidden_public_keys(nested)
    elif isinstance(value, list | tuple):
        for nested in value:
            _reject_forbidden_public_keys(nested)
    return value


class _StrictContract(BaseModel):
    """Base stricte commune aux contrats versionnes Basic."""

    model_config = ConfigDict(extra="forbid")


class InternalEvidence(_StrictContract):
    """Preuve backend reservee au diagnostic, a l'audit et a la validation."""

    source_ref: str = Field(..., min_length=1, max_length=160)
    rule_ref: str = Field(..., min_length=1, max_length=160)
    diagnostic_note: str | None = Field(default=None, max_length=500)


class EditorialEvidence(_StrictContract):
    """Preuve controlee transmise au redacteur LLM pour cadrer la narration."""

    theme_ref: str = Field(..., min_length=1, max_length=120)
    astrological_label: str = Field(..., min_length=2, max_length=200)
    editorial_angle: str = Field(..., min_length=5, max_length=500)


class PublicEvidence(_StrictContract):
    """Preuve vulgarisee autorisee dans le payload public."""

    label: str = Field(..., min_length=2, max_length=200)
    meaning: str = Field(..., min_length=10, max_length=500)
    theme: str = Field(..., min_length=2, max_length=80)

    @model_validator(mode="before")
    @classmethod
    def reject_technical_keys(cls, data: Any) -> Any:
        """Bloque les marqueurs techniques avant coercition Pydantic."""
        return _reject_forbidden_public_keys(data)


class EligibilityContext(_StrictContract):
    """Contexte declaratif qui determine si la lecture Basic peut etre produite."""

    locale: str = Field(..., pattern=r"^[a-z]{2}-[A-Z]{2}$")
    level: Literal["basic"] = BASIC_NATAL_LEVEL
    engine_version: Literal["basic-natal-reading-v1"] = BASIC_NATAL_ENGINE_VERSION
    eligible: bool
    limitations: list[str] = Field(default_factory=list, max_length=8)
    internal_evidence: list[InternalEvidence] = Field(default_factory=list, max_length=20)


class NatalFact(_StrictContract):
    """Fait astrologique selectionne avant ponderation editoriale."""

    fact_key: str = Field(..., min_length=1, max_length=120)
    subject: str = Field(..., min_length=1, max_length=120)
    statement: str = Field(..., min_length=5, max_length=500)
    internal_evidence: list[InternalEvidence] = Field(default_factory=list, max_length=12)
    editorial_evidence: list[EditorialEvidence] = Field(default_factory=list, max_length=12)


class NatalFactGraph(_StrictContract):
    """Graphe contractuel des faits natals exploites par Basic V2."""

    fact_taxonomy_version: Literal["basic-natal-fact-taxonomy-v1"] = (
        BASIC_NATAL_FACT_TAXONOMY_VERSION
    )
    facts: list[NatalFact] = Field(..., min_length=1, max_length=80)
    internal_evidence: list[InternalEvidence] = Field(default_factory=list, max_length=20)


class NatalSalience(_StrictContract):
    """Importance editoriale d'un fait sans exposer de score public."""

    fact_key: str = Field(..., min_length=1, max_length=120)
    salience_band: Literal["primary", "secondary", "supporting"]
    rationale: str = Field(..., min_length=5, max_length=500)
    editorial_evidence: list[EditorialEvidence] = Field(default_factory=list, max_length=12)


class NatalSalienceModel(_StrictContract):
    """Modele de saillance stable pour ordonner la matiere editoriale."""

    salience_model_version: Literal["basic-natal-salience-v1"] = BASIC_NATAL_SALIENCE_MODEL_VERSION
    items: list[NatalSalience] = Field(..., min_length=1, max_length=80)
    internal_evidence: list[InternalEvidence] = Field(default_factory=list, max_length=20)


class NatalNarrativeTheme(_StrictContract):
    """Theme narratif construit depuis les faits et la saillance."""

    theme_key: str = Field(..., min_length=1, max_length=80)
    title: str = Field(..., min_length=2, max_length=120)
    editorial_intent: str = Field(..., min_length=10, max_length=500)
    supporting_fact_keys: list[str] = Field(..., min_length=1, max_length=12)
    editorial_evidence: list[EditorialEvidence] = Field(..., min_length=1, max_length=12)
    public_evidence: list[PublicEvidence] = Field(..., min_length=1, max_length=8)


class NatalNarrativeThemeModel(_StrictContract):
    """Taxonomie des themes narratifs autorises pour la lecture Basic."""

    theme_taxonomy_version: Literal["basic-natal-theme-taxonomy-v1"] = (
        BASIC_NATAL_THEME_TAXONOMY_VERSION
    )
    themes: list[NatalNarrativeTheme] = Field(..., min_length=1, max_length=12)
    editorial_evidence: list[EditorialEvidence] = Field(default_factory=list, max_length=20)


class NatalPublicTheme(_StrictContract):
    """Theme narratif vulgarise autorise dans la synthese publique."""

    title: str = Field(..., min_length=2, max_length=120)
    narrative: str = Field(..., min_length=20, max_length=1200)
    public_evidence: list[PublicEvidence] = Field(..., min_length=1, max_length=8)

    @model_validator(mode="before")
    @classmethod
    def reject_technical_keys(cls, data: Any) -> Any:
        """Bloque les marqueurs techniques dans les themes publics."""
        return _reject_forbidden_public_keys(data)


class NatalSynthesis(_StrictContract):
    """Synthese publique issue du plan, sans donnees de scoring ni trace brute."""

    title: str = Field(..., min_length=2, max_length=120)
    introduction: str = Field(..., min_length=20, max_length=1200)
    themes: list[NatalPublicTheme] = Field(..., min_length=1, max_length=12)
    conclusion: str = Field(..., min_length=20, max_length=1200)
    public_evidence: list[PublicEvidence] = Field(..., min_length=1, max_length=12)

    @model_validator(mode="before")
    @classmethod
    def reject_technical_keys(cls, data: Any) -> Any:
        """Garantit que la synthese publique ne porte aucun marqueur technique."""
        return _reject_forbidden_public_keys(data)


class BasicNatalReadingPlan(_StrictContract):
    """Plan de lecture remis au redacteur controle avant validation narrative."""

    plan_builder_version: Literal["basic-natal-reading-plan-v1"] = BASIC_NATAL_PLAN_BUILDER_VERSION
    prompt_version: Literal["basic-natal-draft-prompt-v1"] = BASIC_NATAL_PROMPT_VERSION
    validator_version: Literal["basic-natal-validator-v1"] = BASIC_NATAL_VALIDATOR_VERSION
    locale: str = Field(..., pattern=r"^[a-z]{2}-[A-Z]{2}$")
    themes: list[NatalNarrativeTheme] = Field(..., min_length=1, max_length=12)
    editorial_evidence: list[EditorialEvidence] = Field(..., min_length=1, max_length=20)
    internal_evidence: list[InternalEvidence] = Field(default_factory=list, max_length=20)


class BasicNatalInterpretationV2(_StrictContract):
    """Contrat public versionne retourne par la lecture natale Basic V2."""

    locale: str = Field(..., pattern=r"^[a-z]{2}-[A-Z]{2}$")
    level: Literal["basic"] = BASIC_NATAL_LEVEL
    engine_version: Literal["basic-natal-reading-v1"] = BASIC_NATAL_ENGINE_VERSION
    schema_version: Literal["basic_natal_interpretation_v2"] = BASIC_NATAL_PUBLIC_SCHEMA_VERSION
    taxonomy_version: Literal["basic-natal-theme-taxonomy-v1"] = BASIC_NATAL_THEME_TAXONOMY_VERSION
    salience_version: Literal["basic-natal-salience-v1"] = BASIC_NATAL_SALIENCE_MODEL_VERSION
    prompt_version: Literal["basic-natal-draft-prompt-v1"] = BASIC_NATAL_PROMPT_VERSION
    validator_version: Literal["basic-natal-validator-v1"] = BASIC_NATAL_VALIDATOR_VERSION
    interpretation: NatalSynthesis
    limitations: list[str] = Field(default_factory=list, max_length=8)
    disclaimers: list[str] = Field(default_factory=list, max_length=8)
    public_evidence: list[PublicEvidence] = Field(..., min_length=1, max_length=12)

    @model_validator(mode="before")
    @classmethod
    def reject_technical_keys(cls, data: Any) -> Any:
        """Bloque les champs techniques dans toute projection publique Basic V2."""
        return _reject_forbidden_public_keys(data)


__all__ = [
    "BASIC_NATAL_ENGINE_VERSION",
    "BASIC_NATAL_FACT_TAXONOMY_VERSION",
    "BASIC_NATAL_LEVEL",
    "BASIC_NATAL_PLAN_BUILDER_VERSION",
    "BASIC_NATAL_PROMPT_VERSION",
    "BASIC_NATAL_PUBLIC_SCHEMA_VERSION",
    "BASIC_NATAL_SALIENCE_MODEL_VERSION",
    "BASIC_NATAL_THEME_TAXONOMY_VERSION",
    "BASIC_NATAL_VALIDATOR_VERSION",
    "BasicNatalInterpretationV2",
    "BasicNatalReadingPlan",
    "EditorialEvidence",
    "EligibilityContext",
    "InternalEvidence",
    "NatalFact",
    "NatalFactGraph",
    "NatalNarrativeTheme",
    "NatalNarrativeThemeModel",
    "NatalPublicTheme",
    "NatalSalience",
    "NatalSalienceModel",
    "NatalSynthesis",
    "PublicEvidence",
]

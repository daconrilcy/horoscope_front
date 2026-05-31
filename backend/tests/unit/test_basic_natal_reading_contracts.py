# Commentaire global: tests du contrat versionne Basic natal reading V2.
"""Verifie la serialisation et les limites publiques du contrat Basic V2."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain.astrology.reading import (
    BASIC_NATAL_ENGINE_VERSION,
    BASIC_NATAL_FACT_TAXONOMY_VERSION,
    BASIC_NATAL_LEVEL,
    BASIC_NATAL_PLAN_BUILDER_VERSION,
    BASIC_NATAL_PROMPT_VERSION,
    BASIC_NATAL_PUBLIC_SCHEMA_VERSION,
    BASIC_NATAL_SALIENCE_MODEL_VERSION,
    BASIC_NATAL_THEME_TAXONOMY_VERSION,
    BASIC_NATAL_VALIDATOR_VERSION,
    BasicNatalInterpretationV2,
    BasicNatalReadingPlan,
    EditorialEvidence,
    EligibilityContext,
    InternalEvidence,
    NatalFact,
    NatalFactGraph,
    NatalNarrativeTheme,
    NatalNarrativeThemeModel,
    NatalSalience,
    NatalSalienceModel,
    NatalSynthesis,
    PublicEvidence,
)

FORBIDDEN_PUBLIC_MARKERS = (
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
)


def _internal_evidence() -> InternalEvidence:
    """Construit une preuve interne minimale pour les contrats amont."""
    return InternalEvidence(source_ref="natal-result", rule_ref="birth-data-complete")


def _editorial_evidence() -> EditorialEvidence:
    """Construit une preuve editoriale utilisable par le redacteur controle."""
    return EditorialEvidence(
        theme_ref="identity",
        astrological_label="Soleil en Maison X",
        editorial_angle="Relier l'identite a la trajectoire visible.",
    )


def _public_evidence() -> PublicEvidence:
    """Construit une preuve publique sans identifiant technique."""
    return PublicEvidence(
        label="Soleil valorise",
        meaning="Votre expression personnelle cherche une place claire et visible.",
        theme="identite",
    )


def _theme() -> NatalNarrativeTheme:
    """Construit un theme narratif complet avec preuves separees."""
    return NatalNarrativeTheme(
        theme_key="identity",
        title="Identite et rayonnement",
        editorial_intent="Structurer une lecture accessible de l'expression personnelle.",
        supporting_fact_keys=["sun-house-10"],
        editorial_evidence=[_editorial_evidence()],
        public_evidence=[_public_evidence()],
    )


def _synthesis() -> NatalSynthesis:
    """Construit la synthese publique minimale attendue."""
    return NatalSynthesis(
        title="Lecture natale Basic",
        introduction="Cette lecture met en avant les fils conducteurs les plus lisibles.",
        themes=[_theme()],
        conclusion="Elle propose une synthese claire sans remplacer votre libre arbitre.",
        public_evidence=[_public_evidence()],
    )


def _public_contract() -> BasicNatalInterpretationV2:
    """Construit le contrat public Basic V2 nominal."""
    return BasicNatalInterpretationV2(
        locale="fr-FR",
        interpretation=_synthesis(),
        public_evidence=[_public_evidence()],
    )


def test_basic_versions_are_centralized_and_serialized() -> None:
    """Verifie les versions publiques et internes exposees par les contrats."""
    assert BASIC_NATAL_LEVEL == "basic"
    assert BASIC_NATAL_ENGINE_VERSION == "basic-natal-reading-v1"
    assert BASIC_NATAL_PUBLIC_SCHEMA_VERSION == "basic_natal_interpretation_v2"
    assert BASIC_NATAL_FACT_TAXONOMY_VERSION == "basic-natal-fact-taxonomy-v1"
    assert BASIC_NATAL_SALIENCE_MODEL_VERSION == "basic-natal-salience-v1"
    assert BASIC_NATAL_THEME_TAXONOMY_VERSION == "basic-natal-theme-taxonomy-v1"
    assert BASIC_NATAL_PLAN_BUILDER_VERSION == "basic-natal-reading-plan-v1"
    assert BASIC_NATAL_PROMPT_VERSION == "basic-natal-draft-prompt-v1"
    assert BASIC_NATAL_VALIDATOR_VERSION == "basic-natal-validator-v1"

    payload = _public_contract().model_dump()

    assert payload["level"] == "basic"
    assert payload["engine_version"] == "basic-natal-reading-v1"
    assert payload["schema_version"] == "basic_natal_interpretation_v2"
    assert payload["locale"] == "fr-FR"


def test_contract_models_separate_internal_editorial_and_public_evidence() -> None:
    """Prouve que chaque niveau de preuve reste porte par un champ dedie."""
    fact_graph = NatalFactGraph(
        facts=[
            NatalFact(
                fact_key="sun-house-10",
                subject="Soleil",
                statement="Le Soleil occupe une zone de visibilite sociale.",
                internal_evidence=[_internal_evidence()],
                editorial_evidence=[_editorial_evidence()],
            )
        ],
        internal_evidence=[_internal_evidence()],
    )
    salience_model = NatalSalienceModel(
        items=[
            NatalSalience(
                fact_key="sun-house-10",
                salience_band="primary",
                rationale="Fait central pour la lecture Basic.",
                editorial_evidence=[_editorial_evidence()],
            )
        ],
        internal_evidence=[_internal_evidence()],
    )
    theme_model = NatalNarrativeThemeModel(themes=[_theme()])
    plan = BasicNatalReadingPlan(
        locale="fr-FR",
        themes=[_theme()],
        editorial_evidence=[_editorial_evidence()],
        internal_evidence=[_internal_evidence()],
    )

    assert "internal_evidence" in fact_graph.model_dump()
    assert "editorial_evidence" in salience_model.items[0].model_dump()
    assert "public_evidence" in theme_model.themes[0].model_dump()
    assert plan.model_dump()["validator_version"] == "basic-natal-validator-v1"


def test_public_v2_rejects_unknown_fields() -> None:
    """Verifie que le contrat public refuse tout champ non declare."""
    payload = _public_contract().model_dump()
    payload["unexpected"] = "refused"

    with pytest.raises(ValidationError):
        BasicNatalInterpretationV2(**payload)


@pytest.mark.parametrize("marker", FORBIDDEN_PUBLIC_MARKERS)
def test_public_v2_blocks_technical_markers(marker: str) -> None:
    """Verifie que les marqueurs techniques sont refuses partout dans le public."""
    payload = _public_contract().model_dump()
    payload["interpretation"]["themes"][0]["public_evidence"][0][marker] = "leak"

    with pytest.raises(ValidationError):
        BasicNatalInterpretationV2(**payload)


def test_public_v2_requires_non_empty_public_evidence() -> None:
    """Verifie que le contrat public ne peut pas etre rempli par des sources vides."""
    payload = _public_contract().model_dump()
    payload["public_evidence"] = []

    with pytest.raises(ValidationError):
        BasicNatalInterpretationV2(**payload)


def test_eligibility_context_serializes_basic_identity() -> None:
    """Verifie l'identite Basic commune au contexte d'eligibilite."""
    context = EligibilityContext(locale="fr-FR", eligible=True)

    assert context.model_dump() == {
        "locale": "fr-FR",
        "level": "basic",
        "engine_version": "basic-natal-reading-v1",
        "eligible": True,
        "limitations": [],
        "internal_evidence": [],
    }

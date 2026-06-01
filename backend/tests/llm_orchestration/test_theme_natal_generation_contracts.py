# Commentaire global: prouve les garde-fous orchestration des contrats de generation theme natal.
"""Tests de snapshot, schema strict et anti-collision Basic/Premium."""

from __future__ import annotations

import json

import pytest
from pydantic import BaseModel, ValidationError

from app.domain.theme_natal.generation_contracts import (
    THEME_NATAL_GENERATION_CONTRACTS_BY_KEY,
    ThemeNatalGenerationContract,
    resolve_theme_natal_generation_contract,
)
from app.domain.theme_natal.generation_schemas import (
    PUBLIC_PROJECTED_MODELS,
    RAW_PROVIDER_MODELS,
)
from app.domain.theme_natal.product_contract import ThemeNatalOutputVariant


def test_resolved_snapshot_is_not_changed_by_registry_mutation() -> None:
    """Prouve qu'un run conserve son snapshot apres mutation du registre source."""

    contract = ThemeNatalGenerationContract.model_validate(
        THEME_NATAL_GENERATION_CONTRACTS_BY_KEY[
            "theme_natal.reading.basic_full_reading.v1"
        ].model_dump(mode="python")
    )
    registry = {contract.generation_contract_key: contract}

    snapshot = resolve_theme_natal_generation_contract(
        "theme_natal.reading.basic_full_reading.v1",
        registry=registry,
    )
    original_hash = snapshot.generation_contract_hash
    original_raw_schema_name = snapshot.contract.output_contract.raw_schema_name

    contract.output_contract.raw_provider_schema["properties"]["schema_version"]["const"] = (
        "mutated_schema"
    )
    changed_snapshot = resolve_theme_natal_generation_contract(
        "theme_natal.reading.basic_full_reading.v1",
        registry=registry,
    )

    assert snapshot.generation_contract_hash == original_hash
    assert snapshot.contract.output_contract.raw_schema_name == original_raw_schema_name
    assert (
        snapshot.contract.output_contract.raw_provider_schema["properties"]["schema_version"][
            "const"
        ]
        == "theme_natal_basic_full_raw_v1"
    )
    assert changed_snapshot.generation_contract_hash != original_hash


@pytest.mark.parametrize("variant", list(ThemeNatalOutputVariant))
def test_raw_and_public_models_reject_unknown_fields_recursively(
    variant: ThemeNatalOutputVariant,
) -> None:
    """Verifie le refus des champs inconnus a la racine et dans les objets imbriques."""

    raw_model = RAW_PROVIDER_MODELS[variant]
    public_model = PUBLIC_PROJECTED_MODELS[variant]

    _assert_root_and_nested_extra_fields_rejected(
        raw_model,
        _raw_payload(variant),
        _raw_nested_path(variant),
    )
    _assert_root_and_nested_extra_fields_rejected(
        public_model,
        _public_payload(variant),
        _public_nested_path(variant),
    )


def test_basic_contract_avoids_legacy_or_premium_collision_tokens() -> None:
    """Verifie que Basic ne reference pas les anciens contrats ni le wording Premium."""

    basic_contract = THEME_NATAL_GENERATION_CONTRACTS_BY_KEY[
        "theme_natal.reading.basic_full_reading.v1"
    ]
    serialized = json.dumps(basic_contract.model_dump(mode="json"), ensure_ascii=False)

    for forbidden_token in ("AstroResponse_v3", "EXIGENCE PREMIUM", "natal_interpretation"):
        assert forbidden_token not in serialized
    assert (
        basic_contract.output_contract.raw_schema_name
        != THEME_NATAL_GENERATION_CONTRACTS_BY_KEY[
            "theme_natal.reading.premium_full_reading.v1"
        ].output_contract.raw_schema_name
    )
    assert (
        basic_contract.output_contract.public_schema_name
        != THEME_NATAL_GENERATION_CONTRACTS_BY_KEY[
            "theme_natal.reading.premium_full_reading.v1"
        ].output_contract.public_schema_name
    )


def _assert_root_and_nested_extra_fields_rejected(
    model: type[BaseModel],
    payload: dict[str, object],
    nested_path: tuple[str | int, ...],
) -> None:
    """Valide qu'un modele refuse les extras a la racine et dans un enfant."""

    root_payload = dict(payload)
    root_payload["unexpected_field"] = "blocked"
    with pytest.raises(ValidationError):
        model.model_validate(root_payload)

    if not nested_path:
        return

    nested_payload = json.loads(json.dumps(payload))
    target = nested_payload
    for segment in nested_path[:-1]:
        target = target[segment]
    target[nested_path[-1]]["unexpected_nested_field"] = "blocked"
    with pytest.raises(ValidationError):
        model.model_validate(nested_payload)


def _raw_payload(variant: ThemeNatalOutputVariant) -> dict[str, object]:
    """Retourne un payload provider minimal valide pour la variante."""

    evidence = {
        "source_id": "src-1",
        "source_kind": "reading_plan",
        "relevance": "source publique utile",
    }
    if variant is ThemeNatalOutputVariant.FREE_PREVIEW:
        return {
            "schema_version": "theme_natal_free_preview_raw_v1",
            "preview_title": "Apercu natal",
            "preview_summary": "Une synthese lisible du potentiel natal.",
            "highlights": [
                {"title": "Elan", "narrative": "Un angle clair.", "evidence_refs": [evidence]},
                {
                    "title": "Ancrage",
                    "narrative": "Une ressource stable.",
                    "evidence_refs": [evidence],
                },
            ],
            "safety_notes": ["Lecture symbolique."],
        }
    if variant is ThemeNatalOutputVariant.BASIC_FULL_READING:
        sections = [
            _basic_raw_section("identity"),
            _basic_raw_section("resources"),
            _basic_raw_section("relationships"),
            _basic_raw_section("growth"),
        ]
        return {
            "schema_version": "theme_natal_basic_full_raw_v1",
            "title": "Lecture Basic",
            "introduction": "Intro " * 30,
            "sections": sections,
            "conclusion": "Conclusion " * 20,
            "safety_notes": ["Lecture symbolique."],
        }
    chapters = [
        _premium_raw_chapter("identity"),
        _premium_raw_chapter("resources"),
        _premium_raw_chapter("relationships"),
        _premium_raw_chapter("growth"),
        _premium_raw_chapter("timing"),
    ]
    return {
        "schema_version": "theme_natal_premium_full_raw_v1",
        "title": "Lecture Premium",
        "orientation": "Orientation " * 25,
        "chapters": chapters,
        "integration_summary": "Integration " * 20,
        "safety_notes": ["Lecture symbolique."],
    }


def _public_payload(variant: ThemeNatalOutputVariant) -> dict[str, object]:
    """Retourne un payload public minimal valide pour la variante."""

    if variant is ThemeNatalOutputVariant.FREE_PREVIEW:
        return {
            "schema_version": "theme_natal_free_preview_public_v1",
            "title": "Apercu natal",
            "summary": "Une synthese lisible du potentiel natal.",
            "highlights": ["Elan clair", "Ressource stable"],
            "call_to_action": "Decouvrir la lecture complete.",
        }
    if variant is ThemeNatalOutputVariant.BASIC_FULL_READING:
        chapters = [
            _basic_public_chapter("identity"),
            _basic_public_chapter("resources"),
            _basic_public_chapter("relationships"),
            _basic_public_chapter("growth"),
        ]
        return {
            "schema_version": "theme_natal_basic_full_public_v1",
            "title": "Lecture Basic",
            "introduction": "Introduction " * 12,
            "chapters": chapters,
            "conclusion": "Conclusion " * 12,
            "disclaimers": ["Lecture symbolique."],
        }
    chapters = [
        _premium_public_chapter("identity"),
        _premium_public_chapter("resources"),
        _premium_public_chapter("relationships"),
        _premium_public_chapter("growth"),
        _premium_public_chapter("timing"),
    ]
    return {
        "schema_version": "theme_natal_premium_full_public_v1",
        "title": "Lecture Premium",
        "orientation": "Orientation " * 18,
        "chapters": chapters,
        "integration_summary": "Integration " * 18,
        "disclaimers": ["Lecture symbolique."],
    }


def _raw_nested_path(variant: ThemeNatalOutputVariant) -> tuple[str | int, ...]:
    """Retourne le premier objet imbrique raw a modifier."""

    if variant is ThemeNatalOutputVariant.FREE_PREVIEW:
        return ("highlights", 0)
    if variant is ThemeNatalOutputVariant.BASIC_FULL_READING:
        return ("sections", 0)
    return ("chapters", 0)


def _public_nested_path(variant: ThemeNatalOutputVariant) -> tuple[str | int, ...]:
    """Retourne le premier objet imbrique public a modifier."""

    if variant is ThemeNatalOutputVariant.FREE_PREVIEW:
        return ()
    return ("chapters", 0)


def _basic_raw_section(key: str) -> dict[str, object]:
    """Construit une section Basic raw valide."""

    return {
        "key": key,
        "heading": f"Chapitre {key}",
        "narrative": "Texte explicatif " * 15,
        "source_refs": [
            {
                "source_id": f"src-{key}",
                "source_kind": "reading_plan",
                "relevance": "source publique utile",
            }
        ],
        "limitations": ["Reste symbolique."],
    }


def _premium_raw_chapter(key: str) -> dict[str, object]:
    """Construit un chapitre Premium raw valide."""

    return {
        "key": key,
        "heading": f"Chapitre {key}",
        "narrative": "Texte approfondi " * 18,
        "timing_windows": [
            {
                "label": "Prochain cycle",
                "narrative": "Fenetre symbolique.",
                "evidence_refs": [
                    {
                        "source_id": f"timing-{key}",
                        "source_kind": "astrological_fact",
                        "relevance": "repere public",
                    }
                ],
            }
        ],
        "reflection_prompts": ["Quelle ressource activer ?"],
        "source_refs": [
            {
                "source_id": f"src-{key}",
                "source_kind": "reading_plan",
                "relevance": "source publique utile",
            }
        ],
    }


def _basic_public_chapter(key: str) -> dict[str, object]:
    """Construit un chapitre Basic public valide."""

    return {
        "key": key,
        "title": f"Chapitre {key}",
        "text": "Texte public " * 20,
        "source_annex": ["Source publique"],
    }


def _premium_public_chapter(key: str) -> dict[str, object]:
    """Construit un chapitre Premium public valide."""

    return {
        "key": key,
        "title": f"Chapitre {key}",
        "text": "Texte public approfondi " * 16,
        "timing_windows": [{"label": "Prochain cycle", "text": "Fenetre symbolique."}],
        "reflection_prompts": ["Quelle ressource activer ?"],
        "source_annex": ["Source publique"],
    }

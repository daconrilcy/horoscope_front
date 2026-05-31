"""Tests du contexte canonique d'eligibilite horaire Basic."""

from __future__ import annotations

from app.domain.astrology.interpretation.basic_natal_eligibility import (
    build_basic_natal_eligibility_context,
)


def test_full_birth_time_enables_time_dependent_families() -> None:
    """Une heure complete avec fuseau et maisons active toutes les familles horaires."""
    context = build_basic_natal_eligibility_context(_structured_facts())

    assert context.to_payload() == {
        "birth_time_status": "full_birth_time",
        "can_use_houses": True,
        "can_use_angles": True,
        "can_use_house_rulers": True,
        "can_use_lunar_nodes_by_house": True,
        "limitations": [],
    }


def test_approximate_birth_time_keeps_cautious_family_access() -> None:
    """Une heure incertaine conserve les surfaces horaires avec une limite publique."""
    context = build_basic_natal_eligibility_context(_structured_facts(birth_time="approximate"))

    assert context.birth_time_status == "approximate_birth_time"
    assert context.can_use_houses is True
    assert context.can_use_angles is True
    assert context.can_use_house_rulers is True
    assert context.can_use_lunar_nodes_by_house is True
    assert context.limitations == (
        "Lecture avec une heure de naissance incertaine: les maisons et les angles "
        "sont lus avec prudence.",
    )


def test_date_only_disables_house_dependent_families_with_public_limitation() -> None:
    """Une date seule coupe les familles horaires sans exposer d'identifiants techniques."""
    context = build_basic_natal_eligibility_context(
        _structured_facts(birth_time="missing", houses=(), reasons=("no_time",))
    )

    payload = context.to_payload()
    assert payload["birth_time_status"] == "date_only"
    assert payload["can_use_houses"] is False
    assert payload["can_use_angles"] is False
    assert payload["can_use_house_rulers"] is False
    assert payload["can_use_lunar_nodes_by_house"] is False
    assert "maisons" in payload["limitations"][0]
    assert _contains_no_public_technical_markers(payload["limitations"])


def test_missing_timezone_prevents_full_birth_time_confidence() -> None:
    """Un fuseau absent degrade la confiance sans inventer une heure complete."""
    context = build_basic_natal_eligibility_context(
        _structured_facts(birth_timezone="missing", reasons=("missing_timezone",))
    )

    assert context.birth_time_status == "approximate_birth_time"
    assert context.can_use_houses is True
    assert context.can_use_angles is True
    assert context.limitations == (
        "Lecture avec fuseau horaire incomplet: les informations liees aux maisons "
        "et aux angles restent prudentes.",
    )


def test_partial_chart_state_cannot_enable_absent_surfaces() -> None:
    """Un theme partiel ne declare pas les surfaces horaires absentes utilisables."""
    context = build_basic_natal_eligibility_context(_structured_facts(houses=(), dispositors=()))

    assert context.birth_time_status == "full_birth_time"
    assert context.can_use_houses is False
    assert context.can_use_angles is False
    assert context.can_use_house_rulers is False
    assert context.can_use_lunar_nodes_by_house is False


def _structured_facts(
    *,
    birth_time: str = "available",
    birth_timezone: str = "available",
    houses: tuple[dict[str, object], ...] = ({"house_number": 1},),
    dispositors: tuple[str, ...] = ("mars",),
    reasons: tuple[str, ...] = (),
) -> dict[str, object]:
    """Construit une projection minimale centree sur l'eligibilite."""
    missing_data: dict[str, object] = {
        "birth_time": birth_time,
        "birth_timezone": birth_timezone,
        "empty_collections": [] if houses else ["houses"],
    }
    if reasons:
        missing_data["reasons"] = list(reasons)
    return {
        "projection_id": "structured_facts_v1",
        "contract_version": "structured_facts_v1.contract.v1",
        "structural_facts": {
            "houses": list(houses),
        },
        "interpretive_signals": {
            "dispositor_codes": list(dispositors),
        },
        "missing_data": missing_data,
    }


def _contains_no_public_technical_markers(limitations: list[str]) -> bool:
    """Verifie que les limites publiques ne portent pas de termes internes."""
    serialized = " ".join(limitations).lower()
    forbidden = {
        "house_number",
        "birth_time_status",
        "eligibilitycontext",
        "ascendant",
        "mc",
    }
    return all(marker not in serialized for marker in forbidden)

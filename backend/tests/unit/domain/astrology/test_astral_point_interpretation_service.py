"""Tests du service d'interprétation séparée des points astraux."""

from __future__ import annotations

from app.domain.astrology.interpretation.astral_point_interpretation import (
    AstralPointInterpretationKeywords,
    AstralPointInterpretationProfile,
    AstralPointInterpretationService,
)
from app.domain.astrology.natal_calculation import build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from tests.factories.astrology_runtime_reference_factory import complete_reference


class FakeAstralPointProfileLoader:
    """Chargeur de test qui prouve que le service ne recalcule pas les positions."""

    def __init__(self) -> None:
        self.seen_codes: list[str] = []

    def load_profile_for_position(
        self,
        point_position,
        *,
        language_code: str = "en",
        tradition: str = "modern_western",
    ) -> AstralPointInterpretationProfile | None:
        """Retourne un profil générique aligné sur la position fournie."""
        self.seen_codes.append(point_position.code)
        if point_position.code != "north_node":
            return None
        return AstralPointInterpretationProfile(
            profile_id=10,
            point_code=point_position.code,
            variant_code=None,
            language_code=language_code,
            tradition=tradition,
            title="North Node",
            summary="Direction of evolution.",
            micro_note="Growth path.",
            keywords=AstralPointInterpretationKeywords(
                core=("growth",),
                shadow=("fear of change",),
                psychological=("learning",),
                spiritual=("calling",),
                relationship=(),
                career=(),
            ),
        )


def _natal_result_with_points():
    """Construit un résultat natal réaliste depuis le runtime de test."""
    return build_natal_result(
        birth_input=BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        ),
        runtime_reference=complete_reference(),
        ruleset_version="test",
        house_system="equal",
    )


def test_service_builds_interpreted_points_without_mutating_natal_result() -> None:
    """Le service assemble le contexte séparé sans modifier `NatalResult.points[]`."""
    natal_result = _natal_result_with_points()
    before_points = natal_result.model_dump()["points"]
    loader = FakeAstralPointProfileLoader()

    context = AstralPointInterpretationService(loader).build_context(
        natal_result,
        language_code="fr",
        tradition="modern_western",
    )

    assert loader.seen_codes == [point.code for point in natal_result.points]
    assert len(context) == 1
    interpreted = context[0]
    source_position = next(point for point in natal_result.points if point.code == "north_node")
    assert interpreted.code == source_position.code
    assert interpreted.variant_code == source_position.variant_code
    assert interpreted.sign == source_position.sign
    assert interpreted.house == source_position.house
    assert interpreted.core_keywords == ("growth",)
    assert interpreted.prompt_hints == ("learning", "calling")
    assert natal_result.model_dump()["points"] == before_points


def test_service_rejects_specific_profile_variant_mismatch() -> None:
    """La variante spécifique d'un profil ne peut pas masquer une autre position."""
    natal_result = _natal_result_with_points()
    north_node = next(point for point in natal_result.points if point.code == "north_node")
    mismatched_profile = AstralPointInterpretationProfile(
        profile_id=11,
        point_code="north_node",
        variant_code="mean",
        language_code="en",
        tradition="modern_western",
        title="North Node",
        summary=None,
        micro_note=None,
        keywords=AstralPointInterpretationKeywords(
            core=(),
            shadow=(),
            psychological=(),
            spiritual=(),
            relationship=(),
            career=(),
        ),
    )
    loader = FakeAstralPointProfileLoader()
    loader.load_profile_for_position = lambda *_, **__: mismatched_profile  # type: ignore[method-assign]

    try:
        AstralPointInterpretationService(loader).build_context(
            natal_result.model_copy(update={"points": [north_node]})
        )
    except ValueError as error:
        assert "variant does not match position" in str(error)
    else:
        raise AssertionError("variant mismatch should fail explicitly")

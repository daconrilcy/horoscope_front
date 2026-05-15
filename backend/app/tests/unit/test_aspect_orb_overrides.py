"""Tests unitaires pour la résolution hierarchique des orbes et la limitation aux aspects majeurs.

Story 24-2 — Calcul aspects avec orbs et overrides.

Couvre:
- AC1: orb_max respecte la priorité pair_override > luminary_override > default_orb
- AC2: orb_used <= orb_max pour tous les aspects détectés
- AC2: code appartient à {conjunction, sextile, square, trine, opposition}
- AC3: test golden — cas contrôlé avec aspect précis attendu
- Task 3: seuls les aspects majeurs sont calculés (aspects mineurs filtrés)
"""

from __future__ import annotations

import pytest

from app.domain.astrology.calculators.aspects import calculate_major_aspects, resolve_orb
from app.domain.astrology.celestial_runtime_catalog import is_major_aspect_code
from app.domain.astrology.natal_calculation import build_natal_result
from app.domain.astrology.natal_preparation import BirthInput

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_birth_input() -> BirthInput:
    return BirthInput(
        birth_date="1985-03-21",
        birth_time="08:30",
        birth_place="Lyon",
        birth_timezone="Europe/Paris",
        birth_lat=45.75,
        birth_lon=4.85,
        place_resolved_id=2,
    )


def _swisseph_positions_mock_two_planets(
    jdut: float, planet_codes: list[str], **kwargs: object
) -> list[dict[str, object]]:
    """Deux planètes: Soleil à 0°, Mars à 93° — square avec orbe de 3°."""
    return [
        {"planet_code": "sun", "longitude": 0.0, "sign_code": "aries"},
        {"planet_code": "mars", "longitude": 93.0, "sign_code": "cancer"},
    ]


def _swisseph_positions_sun_moon(
    jdut: float, planet_codes: list[str], **kwargs: object
) -> list[dict[str, object]]:
    """Soleil à 0°, Lune à 177° — opposition avec orbe de 3°."""
    return [
        {"planet_code": "sun", "longitude": 0.0, "sign_code": "aries"},
        {"planet_code": "moon", "longitude": 177.0, "sign_code": "libra"},
    ]


def _swisseph_positions_sun_mars_wide_square(
    jdut: float, planet_codes: list[str], **kwargs: object
) -> list[dict[str, object]]:
    """Soleil à 0°, Mars à 97° — square hors default mais dans règle luminaire."""
    return [
        {"planet_code": "sun", "longitude": 0.0, "sign_code": "aries"},
        {"planet_code": "mars", "longitude": 97.0, "sign_code": "cancer"},
    ]


def _swisseph_houses_mock(
    jdut: float, lat: float, lon: float, house_numbers: list[int], **kwargs: object
) -> tuple[list[dict[str, object]], str]:
    return [{"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers], "placidus"


def _make_reference_two_planets(
    aspects: list[dict[str, object]],
    aspect_orb_rules: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    sign_rulerships = {
        "aries": "mars",
        "taurus": "venus",
        "gemini": "mercury",
        "cancer": "moon",
        "leo": "sun",
        "virgo": "mercury",
        "libra": "venus",
        "scorpio": "mars",
        "sagittarius": "jupiter",
        "capricorn": "saturn",
        "aquarius": "saturn",
        "pisces": "jupiter",
    }
    return {
        "version": "1.0.0",
        "planets": [{"code": "sun", "name": "Sun"}, {"code": "mars", "name": "Mars"}],
        "signs": [
            {"code": "aries", "name": "Aries"},
            {"code": "taurus", "name": "Taurus"},
            {"code": "gemini", "name": "Gemini"},
            {"code": "cancer", "name": "Cancer"},
        ],
        "houses": [{"number": n, "name": f"House {n}"} for n in range(1, 13)],
        "aspects": aspects,
        "aspect_orb_rules": aspect_orb_rules or [],
        "sign_rulerships": sign_rulerships,
    }


# ---------------------------------------------------------------------------
# AC1 — Résolution prioritaire: pair_override > luminary_override > default_orb
# ---------------------------------------------------------------------------


class TestOrbPriorityResolution:
    """orb_max suit la chaîne de priorité: pair_override > luminary > default."""

    def test_default_orb_is_used_when_no_overrides(self) -> None:
        """Sans override, orb_max = default_orb_deg."""
        positions = [
            {"planet_code": "jupiter", "longitude": 0.0},
            {"planet_code": "saturn", "longitude": 93.0},
        ]
        aspect_definitions = [
            {"code": "square", "angle": 90.0, "default_orb_deg": 6.0},
        ]

        result = calculate_major_aspects(positions, aspect_definitions)

        assert len(result) == 1
        assert result[0]["orb_max"] == 6.0  # default appliqué

    def test_luminary_override_takes_precedence_over_default(self) -> None:
        """Avec un luminaire et luminary_override, orb_max = luminary_override (> default)."""
        positions = [
            {"planet_code": "sun", "longitude": 0.0},
            {"planet_code": "jupiter", "longitude": 95.0},  # orbe=5 > default(4), <= luminary(7)
        ]
        aspect_definitions = [
            {
                "code": "square",
                "angle": 90.0,
                "default_orb_deg": 4.0,
                "orb_luminaries": 7.0,
            },
        ]

        result = calculate_major_aspects(positions, aspect_definitions)

        assert len(result) == 1
        assert result[0]["orb_max"] == 7.0  # luminary override appliqué
        assert result[0]["orb_used"] == 5.0  # déviation réelle

    def test_pair_override_takes_precedence_over_luminary_override(self) -> None:
        """pair_override prend la priorité maximale même sur luminary_override."""
        positions = [
            {"planet_code": "sun", "longitude": 0.0},  # luminaire
            {"planet_code": "moon", "longitude": 93.0},  # luminaire
        ]
        aspect_definitions = [
            {
                "code": "square",
                "angle": 90.0,
                "default_orb_deg": 5.0,
                "orb_luminaries": 8.0,
                "orb_pair_overrides": {"sun-moon": 10.0},
            },
        ]

        result = calculate_major_aspects(positions, aspect_definitions)

        assert len(result) == 1
        assert result[0]["orb_max"] == 10.0  # pair override = priorité maximale
        # orb_used = déviation réelle (3°), orb_max = 10° → AC2 satisfait
        assert result[0]["orb_used"] <= result[0]["orb_max"]

    def test_luminary_override_not_applied_for_non_luminaries(self) -> None:
        """luminary_override ne s'applique pas si aucune planète n'est un luminaire."""
        positions = [
            {"planet_code": "jupiter", "longitude": 0.0},
            {"planet_code": "saturn", "longitude": 93.0},
        ]
        aspect_definitions = [
            {
                "code": "square",
                "angle": 90.0,
                "default_orb_deg": 4.0,
                "orb_luminaries": 8.0,
            },
        ]

        # orbe=3 <= default(4), mais pas de luminaire → luminary_override non appliqué
        result = calculate_major_aspects(positions, aspect_definitions)

        assert len(result) == 1
        assert result[0]["orb_max"] == 4.0  # default orb, pas luminary_override

    def test_pair_override_applies_to_non_luminary_pair(self) -> None:
        """pair_override fonctionne aussi pour des paires sans luminaire."""
        positions = [
            {"planet_code": "venus", "longitude": 0.0},
            {"planet_code": "mars", "longitude": 96.0},  # orbe=6 > default(5), <= pair_override(7)
        ]
        aspect_definitions = [
            {
                "code": "square",
                "angle": 90.0,
                "default_orb_deg": 5.0,
                "orb_pair_overrides": {"mars-venus": 7.0},
            },
        ]

        result = calculate_major_aspects(positions, aspect_definitions)

        assert len(result) == 1
        assert result[0]["orb_max"] == 7.0  # pair override pour venus-mars
        assert result[0]["orb_used"] == 6.0  # déviation réelle

    def test_orb_rules_angle_priority_beats_luminary_rule(self) -> None:
        """Une règle angle prioritaire gagne sur une règle luminaire plus large."""
        definitions = [
            {
                "code": "square",
                "system_code": "modern",
                "default_orb_deg": 6.0,
                "is_enabled": True,
            }
        ]
        rules = [
            {
                "aspect_code": "square",
                "system_code": "modern",
                "calculation_context": "natal",
                "source_body_type": "luminary",
                "target_body_type": "any",
                "orb_deg": 8.0,
                "priority": 900,
                "is_enabled": True,
            },
            {
                "aspect_code": "square",
                "system_code": "modern",
                "calculation_context": "natal",
                "source_body_type": "angle",
                "target_body_type": "any",
                "orb_deg": 5.0,
                "priority": 850,
                "is_enabled": True,
            },
        ]

        assert resolve_orb("square", "modern", "natal", "moon", "asc", definitions, rules) == 5.0

    def test_traditional_orb_rules_remain_local(self) -> None:
        """Les règles traditional restent résolues comme règles locales."""
        definitions = [
            {
                "code": "square",
                "system_code": "traditional",
                "default_orb_deg": 6.0,
                "is_enabled": True,
            }
        ]
        rules = [
            {
                "aspect_code": "square",
                "system_code": "traditional",
                "calculation_context": "natal",
                "source_body_type": "luminary",
                "target_body_type": "any",
                "orb_deg": 8.0,
                "priority": 800,
                "is_enabled": True,
            }
        ]

        assert (
            resolve_orb("square", "traditional", "natal", "sun", "mars", definitions, rules) == 8.0
        )

    def test_hellenistic_inherits_traditional_orb_rules(self) -> None:
        """hellenistic hérite des règles d'orbes traditional sans copie locale."""
        definitions = [
            {
                "code": "square",
                "system_code": "hellenistic",
                "default_orb_deg": 6.0,
                "is_enabled": True,
            }
        ]
        rules = [
            {
                "aspect_code": "square",
                "system_code": "traditional",
                "calculation_context": "natal",
                "source_body_type": "luminary",
                "target_body_type": "any",
                "orb_deg": 8.0,
                "priority": 800,
                "is_enabled": True,
            }
        ]

        assert (
            resolve_orb(
                "square",
                "hellenistic",
                "natal",
                "sun",
                "mars",
                definitions,
                rules,
                {"hellenistic": "traditional", "traditional": None},
            )
            == 8.0
        )

    def test_medieval_inherits_traditional_orb_rules(self) -> None:
        """medieval hérite des règles d'orbes traditional sans copie locale."""
        definitions = [
            {
                "code": "square",
                "system_code": "medieval",
                "default_orb_deg": 6.0,
                "is_enabled": True,
            }
        ]
        rules = [
            {
                "aspect_code": "square",
                "system_code": "traditional",
                "calculation_context": "natal",
                "source_body_type": "luminary",
                "target_body_type": "any",
                "orb_deg": 8.0,
                "priority": 800,
                "is_enabled": True,
            }
        ]

        assert (
            resolve_orb(
                "square",
                "medieval",
                "natal",
                "sun",
                "mars",
                definitions,
                rules,
                {"medieval": "traditional", "traditional": None},
            )
            == 8.0
        )

    def test_child_rule_overrides_parent_rule(self) -> None:
        """Une règle locale enfant gagne avant la règle parente."""
        definitions = [
            {
                "code": "square",
                "system_code": "hellenistic",
                "default_orb_deg": 6.0,
                "is_enabled": True,
            }
        ]
        rules = [
            {
                "aspect_code": "square",
                "system_code": "traditional",
                "calculation_context": "natal",
                "source_body_type": "luminary",
                "target_body_type": "any",
                "orb_deg": 8.0,
                "priority": 1000,
                "is_enabled": True,
            },
            {
                "aspect_code": "square",
                "system_code": "hellenistic",
                "calculation_context": "natal",
                "source_body_type": "luminary",
                "target_body_type": "any",
                "orb_deg": 4.0,
                "priority": 1,
                "is_enabled": True,
            },
        ]

        assert (
            resolve_orb(
                "square",
                "hellenistic",
                "natal",
                "sun",
                "mars",
                definitions,
                rules,
                {"hellenistic": "traditional", "traditional": None},
            )
            == 4.0
        )

    def test_higher_priority_wins_at_same_inheritance_depth(self) -> None:
        """A profondeur égale, la priorité la plus élevée gagne."""
        definitions = [
            {
                "code": "square",
                "system_code": "modern",
                "default_orb_deg": 6.0,
                "is_enabled": True,
            }
        ]
        rules = [
            {
                "aspect_code": "square",
                "system_code": "modern",
                "calculation_context": "natal",
                "source_body_type": "luminary",
                "target_body_type": "any",
                "orb_deg": 8.0,
                "priority": 700,
                "is_enabled": True,
            },
            {
                "aspect_code": "square",
                "system_code": "modern",
                "calculation_context": "natal",
                "source_body_type": "luminary",
                "target_body_type": "any",
                "orb_deg": 9.0,
                "priority": 900,
                "is_enabled": True,
            },
        ]

        assert resolve_orb("square", "modern", "natal", "sun", "mars", definitions, rules) == 9.0

    def test_more_specific_rule_wins_at_same_priority(self) -> None:
        """A priorité égale, la règle la plus spécifique gagne."""
        definitions = [
            {
                "code": "square",
                "system_code": "modern",
                "default_orb_deg": 6.0,
                "is_enabled": True,
            }
        ]
        rules = [
            {
                "aspect_code": "square",
                "system_code": "modern",
                "calculation_context": "natal",
                "source_body_type": "luminary",
                "target_body_type": "any",
                "orb_deg": 8.0,
                "priority": 800,
                "is_enabled": True,
            },
            {
                "aspect_code": "square",
                "system_code": "modern",
                "calculation_context": "natal",
                "source_body_type": "luminary",
                "source_planet_code": "sun",
                "target_body_type": "any",
                "orb_deg": 9.0,
                "priority": 800,
                "is_enabled": True,
            },
        ]

        assert resolve_orb("square", "modern", "natal", "sun", "mars", definitions, rules) == 9.0

    def test_system_inheritance_cycle_raises_explicit_error(self) -> None:
        """Un cycle d'héritage entre systèmes échoue explicitement."""
        definitions = [
            {
                "code": "square",
                "system_code": "hellenistic",
                "default_orb_deg": 6.0,
                "is_enabled": True,
            }
        ]

        with pytest.raises(ValueError, match="inheritance cycle"):
            resolve_orb(
                "square",
                "hellenistic",
                "natal",
                "sun",
                "mars",
                definitions,
                [],
                {"hellenistic": "traditional", "traditional": "hellenistic"},
            )

    def test_missing_inheritance_metadata_raises_for_child_without_local_rules(self) -> None:
        """Un système sans règle locale n'hérite pas silencieusement sans métadonnées."""
        definitions = [
            {
                "code": "square",
                "system_code": "hellenistic",
                "default_orb_deg": 6.0,
                "is_enabled": True,
            }
        ]
        rules = [
            {
                "aspect_code": "square",
                "system_code": "traditional",
                "calculation_context": "natal",
                "source_body_type": "luminary",
                "target_body_type": "any",
                "orb_deg": 8.0,
                "priority": 800,
                "is_enabled": True,
            }
        ]

        with pytest.raises(ValueError, match="inheritance metadata missing"):
            resolve_orb("square", "hellenistic", "natal", "sun", "mars", definitions, rules)

        with pytest.raises(ValueError, match="inheritance metadata missing"):
            resolve_orb(
                "square",
                "hellenistic",
                "natal",
                "sun",
                "mars",
                definitions,
                rules,
                [],
            )

    def test_disabled_orb_rule_does_not_match(self) -> None:
        """Une règle d'orbe désactivée ne remplace pas le fallback."""
        definitions = [
            {
                "code": "square",
                "system_code": "modern",
                "default_orb_deg": 6.0,
                "is_enabled": True,
            }
        ]
        rules = [
            {
                "aspect_code": "square",
                "system_code": "modern",
                "calculation_context": "natal",
                "source_body_type": "luminary",
                "target_body_type": "any",
                "orb_deg": 8.0,
                "priority": 800,
                "is_enabled": False,
            }
        ]

        assert resolve_orb("square", "modern", "natal", "sun", "mars", definitions, rules) == 6.0

    def test_orb_rules_fallback_to_default_orb_deg(self) -> None:
        """Sans exception ciblée, default_orb_deg reste l'orbe obligatoire."""
        definitions = [
            {
                "code": "square",
                "system_code": "modern",
                "default_orb_deg": 6.0,
                "is_enabled": True,
            }
        ]

        assert resolve_orb("square", "modern", "natal", "mars", "saturn", definitions, []) == 6.0

    def test_calculate_major_aspects_uses_orb_rules_when_provided(self) -> None:
        """Les aspects calculés utilisent les exceptions sans modifier default_orb_deg."""
        positions = [
            {"planet_code": "uranus", "longitude": 0.0},
            {"planet_code": "neptune", "longitude": 94.0},
        ]
        definitions = [{"code": "square", "angle": 90.0, "default_orb_deg": 6.0}]
        rules = [
            {
                "aspect_code": "square",
                "system_code": "modern",
                "calculation_context": "natal",
                "source_body_type": "transpersonal_planet",
                "target_body_type": "transpersonal_planet",
                "orb_deg": 3.0,
                "priority": 700,
                "is_enabled": True,
            }
        ]

        assert calculate_major_aspects(positions, definitions, orb_rules=rules) == []

    def test_calculate_major_aspects_uses_requested_system_for_plain_definitions(self) -> None:
        """Une définition sans system_code reste utilisable pour un système non modern."""
        positions = [
            {"planet_code": "sun", "longitude": 0.0},
            {"planet_code": "mars", "longitude": 95.0},
        ]
        definitions = [{"code": "square", "angle": 90.0, "default_orb_deg": 6.0}]

        result = calculate_major_aspects(
            positions,
            definitions,
            orb_rules=[],
            system_code="traditional",
        )

        assert len(result) == 1
        assert result[0]["orb_max"] == 6.0

    def test_transit_to_natal_rules_are_directional(self) -> None:
        """Une règle prédictive target luminary ne matche pas le sens inversé."""
        definitions = [
            {
                "code": "square",
                "system_code": "modern",
                "default_orb_deg": 6.0,
                "is_enabled": True,
            }
        ]
        rules = [
            {
                "aspect_code": "square",
                "system_code": "modern",
                "calculation_context": "transit_to_natal",
                "source_body_type": "any",
                "target_body_type": "luminary",
                "orb_deg": 2.5,
                "priority": 500,
                "is_enabled": True,
            }
        ]

        assert (
            resolve_orb(
                "square",
                "modern",
                "transit_to_natal",
                "sun",
                "saturn",
                definitions,
                rules,
            )
            == 6.0
        )


# ---------------------------------------------------------------------------
# AC2 — orb_used <= orb_max et code dans les aspects majeurs
# ---------------------------------------------------------------------------


class TestOrbUsedLteOrbMax:
    """Pour tout aspect détecté: orb_used <= orb_max ET code dans les majeurs."""

    def test_orb_used_lte_orb_max_default(self) -> None:
        """orb_used (déviation) <= orb_max (seuil) avec orb par défaut."""
        positions = [
            {"planet_code": "sun", "longitude": 0.0},
            {"planet_code": "mars", "longitude": 94.0},
        ]
        aspect_definitions = [
            {"code": "square", "angle": 90.0, "default_orb_deg": 6.0},
        ]

        result = calculate_major_aspects(positions, aspect_definitions)

        assert len(result) == 1
        assert result[0]["orb_used"] <= result[0]["orb_max"]

    def test_orb_used_lte_orb_max_luminary_override(self) -> None:
        """orb_used <= orb_max avec luminary override."""
        positions = [
            {"planet_code": "sun", "longitude": 0.0},
            {"planet_code": "moon", "longitude": 177.0},
        ]
        aspect_definitions = [
            {
                "code": "opposition",
                "angle": 180.0,
                "default_orb_deg": 6.0,
                "orb_luminaries": 9.0,
            },
        ]

        result = calculate_major_aspects(positions, aspect_definitions)

        assert len(result) == 1
        assert result[0]["orb_used"] <= result[0]["orb_max"]
        assert result[0]["orb_max"] == 9.0

    def test_aspect_code_is_major(self) -> None:
        """Les codes d'aspects détectés appartiennent à l'ensemble des aspects majeurs."""
        positions = [
            {"planet_code": "sun", "longitude": 0.0},
            {"planet_code": "moon", "longitude": 60.0},  # sextile exact
            {"planet_code": "mars", "longitude": 90.0},  # square exact
            {"planet_code": "jupiter", "longitude": 120.0},  # trine exact
            {"planet_code": "saturn", "longitude": 180.0},  # opposition exact
        ]
        aspect_definitions = [
            {"code": "conjunction", "angle": 0.0, "default_orb_deg": 6.0},
            {"code": "sextile", "angle": 60.0, "default_orb_deg": 4.0},
            {"code": "square", "angle": 90.0, "default_orb_deg": 6.0},
            {"code": "trine", "angle": 120.0, "default_orb_deg": 6.0},
            {"code": "opposition", "angle": 180.0, "default_orb_deg": 8.0},
        ]

        result = calculate_major_aspects(positions, aspect_definitions)

        for aspect in result:
            assert is_major_aspect_code(str(aspect["aspect_code"])), (
                f"Aspect code '{aspect['aspect_code']}' non trouvé dans les aspects majeurs"
            )


# ---------------------------------------------------------------------------
# Task 3 — Seuls les aspects majeurs sont calculés
# ---------------------------------------------------------------------------


class TestMajorAspectsFilter:
    """build_natal_result ne calcule que les aspects majeurs (filtre les mineurs)."""

    def test_major_aspect_codes_contains_five_aspects(self) -> None:
        """Le helper owner reconnait exactement les 5 aspects majeurs."""
        candidates = {"conjunction", "sextile", "square", "trine", "opposition"}
        assert {code for code in candidates if is_major_aspect_code(code)} == candidates
        assert not is_major_aspect_code("quincunx")

    def test_minor_aspects_ignored_in_calculation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Les aspects mineurs dans le ruleset sont ignorés — seuls les majeurs sont calculés."""
        ref = _make_reference_two_planets(
            aspects=[
                {"code": "square", "angle": 90.0, "default_orb_deg": 6.0},
                {"code": "semisquare", "angle": 45.0, "default_orb_deg": 2.0},  # aspect mineur
                {"code": "sesquisquare", "angle": 135.0, "default_orb_deg": 2.0},  # aspect mineur
            ]
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock_two_planets,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        result = build_natal_result(
            birth_input=_make_birth_input(),
            reference_data=ref,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=45.75,
            birth_lon=4.85,
        )

        # Seul le square (majeur) doit être présent, pas semisquare/sesquisquare
        aspect_codes = {a.aspect_code for a in result.aspects}
        assert "semisquare" not in aspect_codes
        assert "sesquisquare" not in aspect_codes

    def test_no_aspects_detected_if_only_minor_aspects_in_ruleset(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Aucun aspect calculé si le ruleset ne contient que des aspects mineurs."""
        ref = _make_reference_two_planets(
            aspects=[
                {"code": "semisquare", "angle": 45.0, "default_orb_deg": 2.0},
            ]
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock_two_planets,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        result = build_natal_result(
            birth_input=_make_birth_input(),
            reference_data=ref,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=45.75,
            birth_lon=4.85,
        )

        assert result.aspects == []


# ---------------------------------------------------------------------------
# AC3 — Test golden: cas contrôlé avec aspect précis attendu
# ---------------------------------------------------------------------------


class TestGoldenAspectDetection:
    """Golden test: cas contrôlé avec positions fixes et aspects attendus précis."""

    def test_golden_square_sun_mars_orb3_default(self) -> None:
        """Golden: Soleil 0°, Mars 93° → square détecté, orb=3°, orb_max=6°."""
        positions = [
            {"planet_code": "sun", "longitude": 0.0},
            {"planet_code": "mars", "longitude": 93.0},
        ]
        aspect_definitions = [
            {"code": "square", "angle": 90.0, "default_orb_deg": 6.0},
        ]

        result = calculate_major_aspects(positions, aspect_definitions)

        assert len(result) == 1
        aspect = result[0]
        assert aspect["aspect_code"] == "square"
        # Alphabetical sort: mars < sun
        assert aspect["planet_a"] == "mars"
        assert aspect["planet_b"] == "sun"
        assert aspect["orb"] == 3.0  # déviation exacte: |93 - 0 - 90| = 3
        assert aspect["orb_used"] == 3.0  # AC2: orb_used = déviation réelle
        assert aspect["orb_max"] == 6.0  # AC2: orb_max = seuil résolu
        assert aspect["orb_used"] <= aspect["orb_max"]  # AC2 invariant

    def test_golden_square_not_detected_when_orb_exceeds_threshold(self) -> None:
        """Golden: Soleil 0°, Mars 97° → orbe=7 > threshold=6 → pas de square."""
        positions = [
            {"planet_code": "sun", "longitude": 0.0},
            {"planet_code": "mars", "longitude": 97.0},
        ]
        aspect_definitions = [
            {"code": "square", "angle": 90.0, "default_orb_deg": 6.0},
        ]

        result = calculate_major_aspects(positions, aspect_definitions)

        assert len(result) == 0

    def test_golden_opposition_sun_moon_with_luminary_override(self) -> None:
        """Golden: Soleil 0°, Lune 174° → opposition, orbe=6°, orb_max=9° (luminary)."""
        positions = [
            {"planet_code": "sun", "longitude": 0.0},
            {"planet_code": "moon", "longitude": 174.0},
        ]
        aspect_definitions = [
            {
                "code": "opposition",
                "angle": 180.0,
                "default_orb_deg": 6.0,
                "orb_luminaries": 9.0,
            },
        ]

        result = calculate_major_aspects(positions, aspect_definitions)

        # orbe=6 <= luminary_orb(9) → détecté
        assert len(result) == 1
        aspect = result[0]
        assert aspect["aspect_code"] == "opposition"
        # Alphabetical sort: moon < sun
        assert aspect["planet_a"] == "moon"
        assert aspect["planet_b"] == "sun"
        assert aspect["orb"] == 6.0
        assert aspect["orb_used"] == 6.0
        assert aspect["orb_max"] == 9.0

    def test_golden_trine_with_pair_override_via_build_natal_result(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Golden via build_natal_result: Sun 0°, Mars 93° → square avec orb=3°, orb_max=6°."""
        ref = _make_reference_two_planets(
            aspects=[
                {"code": "square", "angle": 90.0, "default_orb_deg": 6.0},
            ]
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_mock_two_planets,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        result = build_natal_result(
            birth_input=_make_birth_input(),
            reference_data=ref,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=45.75,
            birth_lon=4.85,
        )

        assert len(result.aspects) == 1
        aspect = result.aspects[0]
        assert aspect.aspect_code == "square"
        # Alphabetical sort: mars < sun
        assert aspect.planet_a == "mars"
        assert aspect.planet_b == "sun"
        assert aspect.orb == 3.0
        assert aspect.orb_used == 3.0
        assert aspect.orb_max == 6.0
        assert aspect.orb_used <= aspect.orb_max

    def test_build_natal_result_consumes_reference_aspect_orb_rules(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Le pipeline natal applique les règles seedées du payload de référence."""
        ref = _make_reference_two_planets(
            aspects=[
                {"code": "square", "angle": 90.0, "default_orb_deg": 6.0},
            ],
            aspect_orb_rules=[
                {
                    "aspect_code": "square",
                    "system_code": "modern",
                    "calculation_context": "natal",
                    "source_body_type": "luminary",
                    "target_body_type": "any",
                    "orb_deg": 8.0,
                    "priority": 800,
                    "is_enabled": True,
                }
            ],
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_positions",
            _swisseph_positions_sun_mars_wide_square,
        )
        monkeypatch.setattr(
            "app.domain.astrology.natal_calculation._build_swisseph_houses",
            _swisseph_houses_mock,
        )

        result = build_natal_result(
            birth_input=_make_birth_input(),
            reference_data=ref,
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=45.75,
            birth_lon=4.85,
        )

        assert len(result.aspects) == 1
        assert result.aspects[0].orb == 7.0
        assert result.aspects[0].orb_max == 8.0

    def test_golden_deterministic_sort_order(self) -> None:
        """Golden: les aspects sont triés de manière déterministe (code, planet_a, planet_b)."""
        positions = [
            {"planet_code": "sun", "longitude": 0.0},
            {"planet_code": "moon", "longitude": 180.0},  # opposition exacte
            {"planet_code": "mars", "longitude": 90.0},  # square exact avec sun
        ]
        aspect_definitions = [
            {"code": "square", "angle": 90.0, "default_orb_deg": 6.0},
            {"code": "opposition", "angle": 180.0, "default_orb_deg": 8.0},
        ]

        result = calculate_major_aspects(positions, aspect_definitions)

        # Vérifier l'ordre déterministe: (aspect_code, planet_a, planet_b) alphabétique
        aspect_tuples = [(r["aspect_code"], r["planet_a"], r["planet_b"]) for r in result]
        assert aspect_tuples == sorted(aspect_tuples)

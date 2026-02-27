"""Tests unitaires pour le provider SwissEph de maisons natales.

Story 20-3: Provider maisons SwissEph (Placidus par défaut, extensible)

Couvre :
- Tests structure HouseData : 12 cuspides + ASC/MC normalisés [0, 360) (AC1)
- Test Placidus par défaut — houses_ex appelé avec b"P" (AC2)
- Test topocentrique altitude implicite 0 — set_topo(lon, lat, 0.0) (AC3)
- Test géocentrique — set_topo non appelé (AC3 négatif)
- Test erreur 422 unsupported_house_system (AC4)
- Tests erreurs HousesCalcError normalisées (robustesse)
- Test métrique swisseph_houses_latency_ms

Note : pyswisseph peut ne pas être installé dans l'environnement de test.
      Les tests utilisent patch.dict(sys.modules, ...) pour injecter un mock
      du module swisseph, identique à la stratégie de test_ephemeris_provider.py.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.domain.astrology.houses_provider import (
    _HOUSE_SYSTEM_CODES,
    _SUPPORTED_HOUSE_SYSTEMS,
    HousesCalcError,
    UnsupportedHouseSystemError,
    calculate_houses,
)
from app.infra.observability.metrics import reset_metrics

# ---------------------------------------------------------------------------
# Constantes de référence
# ---------------------------------------------------------------------------

JDUT_J2000 = 2451545.0   # J2000.0 — 1 janvier 2000, 12h TT
LAT_PARIS = 48.8566
LON_PARIS = 2.3522

# Valeurs de retour mock pour swe.houses_ex.
# cusps_raw : 13 éléments — index 0 non utilisé, 1..12 = maisons 1..12
_MOCK_CUSPS_RAW = (
    0.0,    # index 0 — non utilisé
    10.0,   # maison 1
    40.0,   # maison 2
    70.0,   # maison 3
    100.0,  # maison 4
    130.0,  # maison 5
    160.0,  # maison 6
    190.0,  # maison 7
    220.0,  # maison 8
    250.0,  # maison 9
    280.0,  # maison 10
    310.0,  # maison 11
    340.0,  # maison 12
)

# ascmc_raw : 10 éléments — index 0 = ASC, index 1 = MC
_MOCK_ASCMC_RAW = (
    10.0,   # ASC (= cusp maison 1 pour Placidus)
    280.0,  # MC
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_swe_mock(
    *,
    cusps_raw=_MOCK_CUSPS_RAW,
    ascmc_raw=_MOCK_ASCMC_RAW,
    houses_ex_side_effect=None,
    set_topo_side_effect=None,
) -> MagicMock:
    """Crée un mock du module swisseph avec houses_ex configuré."""
    mock_swe = MagicMock()
    if houses_ex_side_effect is not None:
        mock_swe.houses_ex.side_effect = houses_ex_side_effect
    else:
        mock_swe.houses_ex.return_value = (cusps_raw, ascmc_raw)
    if set_topo_side_effect is not None:
        mock_swe.set_topo.side_effect = set_topo_side_effect
    return mock_swe


# ---------------------------------------------------------------------------
# Tests structure HouseData (AC1)
# ---------------------------------------------------------------------------


class TestHouseDataStructure:
    def test_returns_12_cusps(self) -> None:
        """Le résultat doit contenir exactement 12 cuspides."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert len(result.cusps) == 12

    def test_cusps_are_tuple(self) -> None:
        """cusps doit être un tuple immutable."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert isinstance(result.cusps, tuple)

    def test_cusps_normalized_in_0_360(self) -> None:
        """Toutes les cuspides doivent être normalisées dans [0, 360)."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        for i, cusp in enumerate(result.cusps):
            assert 0.0 <= cusp < 360.0, (
                f"Cuspide maison {i + 1} = {cusp} hors [0, 360)"
            )

    def test_asc_normalized_in_0_360(self) -> None:
        """ascendant_longitude doit être normalisé dans [0, 360)."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert 0.0 <= result.ascendant_longitude < 360.0

    def test_mc_normalized_in_0_360(self) -> None:
        """mc_longitude doit être normalisé dans [0, 360)."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert 0.0 <= result.mc_longitude < 360.0

    def test_house_system_field_present(self) -> None:
        """Le champ house_system doit être présent dans le résultat."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert isinstance(result.house_system, str)
        assert result.house_system == "placidus"

    def test_housedata_is_frozen(self) -> None:
        """HouseData doit être immuable (dataclass frozen)."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        with pytest.raises((AttributeError, TypeError)):
            result.ascendant_longitude = 0.0  # type: ignore[misc]

    def test_cusps_values_match_mock_output(self) -> None:
        """Les cuspides doivent correspondre exactement aux valeurs mock."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        # _MOCK_CUSPS_RAW[1..12] = 10, 40, 70, ..., 340 — déjà dans [0, 360)
        expected = tuple(float(_MOCK_CUSPS_RAW[i]) for i in range(1, 13))
        assert result.cusps == expected

    def test_asc_matches_mock_output(self) -> None:
        """ascendant_longitude doit correspondre à ascmc_raw[0]."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert result.ascendant_longitude == float(_MOCK_ASCMC_RAW[0])

    def test_mc_matches_mock_output(self) -> None:
        """mc_longitude doit correspondre à ascmc_raw[1]."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert result.mc_longitude == float(_MOCK_ASCMC_RAW[1])

    def test_accepts_12_item_cusps_array_from_swisseph_binding(self) -> None:
        """Compatibilité runtime: certains bindings renvoient 12 cuspides directes."""
        cusps_12 = _MOCK_CUSPS_RAW[1:13]
        mock_swe = _make_swe_mock(cusps_raw=cusps_12)
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert len(result.cusps) == 12
        assert result.cusps[0] == 10.0
        assert result.cusps[-1] == 340.0

    @pytest.mark.parametrize("raw_val", [-10.0, -0.01, 360.0, 370.5, 720.0])
    def test_longitude_normalization_out_of_range(self, raw_val: float) -> None:
        """Les longitudes brutes hors [0, 360) doivent être normalisées."""
        cusps_raw = (0.0,) + tuple(raw_val for _ in range(12))
        ascmc_raw = (raw_val, raw_val) + (0.0,) * 8
        mock_swe = _make_swe_mock(cusps_raw=cusps_raw, ascmc_raw=ascmc_raw)
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        for cusp in result.cusps:
            assert 0.0 <= cusp < 360.0, f"Cuspide {cusp} hors [0, 360) pour brut={raw_val}"
        assert 0.0 <= result.ascendant_longitude < 360.0
        assert 0.0 <= result.mc_longitude < 360.0


# ---------------------------------------------------------------------------
# Test Placidus par défaut (AC2)
# ---------------------------------------------------------------------------


class TestPlacidusDefault:
    def test_no_house_system_uses_placidus(self) -> None:
        """Sans paramètre house_system, Placidus est appliqué par défaut."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert result.house_system == "placidus"

    def test_houses_ex_called_with_placidus_byte_code(self) -> None:
        """houses_ex doit être appelé avec le code b'P' pour Placidus."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        args, kwargs = mock_swe.houses_ex.call_args
        # Signature: houses_ex(jdut, lat, lon, hsys_code)
        assert b"P" in args, f"b'P' attendu dans les arguments, reçu: {args}"

    def test_explicit_placidus_same_as_default(self) -> None:
        """house_system='placidus' explicite = même comportement que défaut."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(
                JDUT_J2000, LAT_PARIS, LON_PARIS, house_system="placidus"
            )
        assert result.house_system == "placidus"
        args, _ = mock_swe.houses_ex.call_args
        assert b"P" in args

    def test_houses_ex_called_once(self) -> None:
        """houses_ex doit être appelé exactement une fois par appel."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert mock_swe.houses_ex.call_count == 1


# ---------------------------------------------------------------------------
# Test cadre topocentrique — altitude implicite 0 (AC3)
# ---------------------------------------------------------------------------


class TestTopocentricFrame:
    def test_geocentric_default_no_set_topo(self) -> None:
        """En cadre géocentrique (défaut), set_topo ne doit PAS être appelé."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        mock_swe.set_topo.assert_not_called()

    def test_topocentric_with_no_altitude_uses_zero(self) -> None:
        """frame='topocentric' sans altitude → set_topo appelé avec altitude=0."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_houses(
                JDUT_J2000, LAT_PARIS, LON_PARIS,
                frame="topocentric",
                altitude_m=None,
            )
        # set_topo doit être appelé — premier appel avec altitude=0
        assert mock_swe.set_topo.call_count >= 1
        first_call = mock_swe.set_topo.call_args_list[0]
        # swe.set_topo(lon, lat, altitude)
        lon_arg, lat_arg, alt_arg = first_call[0]
        assert alt_arg == 0.0, f"altitude attendue 0.0, reçue {alt_arg}"
        assert lat_arg == LAT_PARIS
        assert lon_arg == LON_PARIS

    def test_topocentric_with_explicit_altitude(self) -> None:
        """frame='topocentric' avec altitude fournie → set_topo utilise cette altitude."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_houses(
                JDUT_J2000, LAT_PARIS, LON_PARIS,
                frame="topocentric",
                altitude_m=150.0,
            )
        first_call = mock_swe.set_topo.call_args_list[0]
        lon_arg, lat_arg, alt_arg = first_call[0]
        assert alt_arg == 150.0

    def test_topocentric_resets_topo_after_calc(self) -> None:
        """set_topo(0.0, 0.0, 0.0) doit être appelé après le calcul."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_houses(
                JDUT_J2000, LAT_PARIS, LON_PARIS,
                frame="topocentric",
            )
        # Dernier appel à set_topo doit être le reset (0, 0, 0)
        last_call = mock_swe.set_topo.call_args_list[-1]
        lon_arg, lat_arg, alt_arg = last_call[0]
        assert lon_arg == 0.0
        assert lat_arg == 0.0
        assert alt_arg == 0.0

    def test_topocentric_reset_called_even_on_houses_ex_error(self) -> None:
        """Le reset set_topo(0,0,0) doit être appelé même si houses_ex échoue."""
        mock_swe = _make_swe_mock(
            houses_ex_side_effect=RuntimeError("swe error")
        )
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(HousesCalcError):
                calculate_houses(
                    JDUT_J2000, LAT_PARIS, LON_PARIS,
                    frame="topocentric",
                )
        # Le reset doit quand même avoir été appelé (via finally)
        last_call = mock_swe.set_topo.call_args_list[-1]
        assert last_call[0] == (0.0, 0.0, 0.0)

    def test_geocentric_explicit(self) -> None:
        """frame='geocentric' explicite → set_topo non appelé."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            calculate_houses(
                JDUT_J2000, LAT_PARIS, LON_PARIS,
                frame="geocentric",
            )
        mock_swe.set_topo.assert_not_called()


# ---------------------------------------------------------------------------
# Test erreur 422 unsupported_house_system (AC4)
# ---------------------------------------------------------------------------


class TestUnsupportedHouseSystem:
    def test_unknown_system_raises_error(self) -> None:
        """Un système totalement inconnu doit lever UnsupportedHouseSystemError."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(UnsupportedHouseSystemError) as exc_info:
                calculate_houses(
                    JDUT_J2000, LAT_PARIS, LON_PARIS,
                    house_system="regiomontanus",
                )
        assert exc_info.value.code == "unsupported_house_system"

    def test_error_message_contains_system_name(self) -> None:
        """Le message d'erreur doit mentionner le système demandé."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(UnsupportedHouseSystemError) as exc_info:
                calculate_houses(
                    JDUT_J2000, LAT_PARIS, LON_PARIS,
                    house_system="campanus",
                )
        assert "campanus" in exc_info.value.message

    def test_equal_reserved_raises_error(self) -> None:
        """'equal' est réservé (dans _HOUSE_SYSTEM_CODES) mais non supporté publiquement."""
        assert "equal" in _HOUSE_SYSTEM_CODES, "equal doit être dans les codes"
        assert "equal" not in _SUPPORTED_HOUSE_SYSTEMS, "equal ne doit pas être supporté"
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(UnsupportedHouseSystemError) as exc_info:
                calculate_houses(
                    JDUT_J2000, LAT_PARIS, LON_PARIS,
                    house_system="equal",
                )
        assert exc_info.value.code == "unsupported_house_system"

    def test_whole_sign_reserved_raises_error(self) -> None:
        """'whole_sign' est réservé (dans _HOUSE_SYSTEM_CODES) mais non supporté publiquement."""
        assert "whole_sign" in _HOUSE_SYSTEM_CODES, "whole_sign doit être dans les codes"
        assert "whole_sign" not in _SUPPORTED_HOUSE_SYSTEMS, "whole_sign ne doit pas être supporté"
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(UnsupportedHouseSystemError) as exc_info:
                calculate_houses(
                    JDUT_J2000, LAT_PARIS, LON_PARIS,
                    house_system="whole_sign",
                )
        assert exc_info.value.code == "unsupported_house_system"

    def test_unsupported_system_does_not_call_houses_ex(self) -> None:
        """houses_ex ne doit PAS être appelé si house_system est non supporté."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(UnsupportedHouseSystemError):
                calculate_houses(
                    JDUT_J2000, LAT_PARIS, LON_PARIS,
                    house_system="regiomontanus",
                )
        mock_swe.houses_ex.assert_not_called()

    def test_only_placidus_is_supported(self) -> None:
        """_SUPPORTED_HOUSE_SYSTEMS doit contenir uniquement 'placidus' en v1."""
        assert _SUPPORTED_HOUSE_SYSTEMS == frozenset({"placidus"})


# ---------------------------------------------------------------------------
# Tests erreurs HousesCalcError (robustesse)
# ---------------------------------------------------------------------------


class TestHousesCalcError:
    def test_import_error_raises_houses_calc_error(self) -> None:
        """Si pyswisseph n'est pas installé → HousesCalcError."""
        with patch(
            "app.domain.astrology.houses_provider._get_swe_module",
            side_effect=HousesCalcError("pyswisseph module is not installed"),
        ):
            with pytest.raises(HousesCalcError) as exc_info:
                calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert exc_info.value.code == "houses_calc_failed"
        assert "not installed" in exc_info.value.message

    def test_houses_ex_exception_raises_houses_calc_error(self) -> None:
        """Exception dans houses_ex → HousesCalcError (stack brute non exposée)."""
        mock_swe = _make_swe_mock(
            houses_ex_side_effect=RuntimeError("internal swe error")
        )
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(HousesCalcError) as exc_info:
                calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert exc_info.value.code == "houses_calc_failed"
        assert "internal swe error" not in exc_info.value.message

    def test_set_topo_exception_raises_houses_calc_error(self) -> None:
        """Exception dans set_topo → HousesCalcError."""
        mock_swe = _make_swe_mock(
            set_topo_side_effect=RuntimeError("topo error")
        )
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(HousesCalcError) as exc_info:
                calculate_houses(
                    JDUT_J2000, LAT_PARIS, LON_PARIS,
                    frame="topocentric",
                )
        assert exc_info.value.code == "houses_calc_failed"

    def test_error_does_not_expose_raw_stack(self) -> None:
        """Le message d'erreur ne doit pas contenir de stack trace brute."""
        mock_swe = _make_swe_mock(
            houses_ex_side_effect=RuntimeError("secret /srv/path/data")
        )
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with pytest.raises(HousesCalcError) as exc_info:
                calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        assert "/srv/path/data" not in exc_info.value.message
        assert "secret" not in exc_info.value.message


# ---------------------------------------------------------------------------
# Tests métriques (3.7)
# ---------------------------------------------------------------------------


class TestMetrics:
    def setup_method(self) -> None:
        reset_metrics()

    def test_metric_recorded_after_successful_calc(self) -> None:
        """observe_duration pour swisseph_houses_latency_ms doit être appelé."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with patch(
                "app.domain.astrology.houses_provider.observe_duration"
            ) as mock_observe:
                calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        mock_observe.assert_called_once()
        metric_name, duration_ms = mock_observe.call_args[0]
        assert metric_name == "swisseph_houses_latency_ms"
        assert isinstance(duration_ms, float)
        assert duration_ms >= 0.0

    def test_metric_not_recorded_on_unsupported_system_error(self) -> None:
        """La métrique ne doit PAS être enregistrée si validation échoue avant calcul."""
        mock_swe = _make_swe_mock()
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            with patch(
                "app.domain.astrology.houses_provider.observe_duration"
            ) as mock_observe:
                with pytest.raises(UnsupportedHouseSystemError):
                    calculate_houses(
                        JDUT_J2000, LAT_PARIS, LON_PARIS,
                        house_system="regiomontanus",
                    )
        mock_observe.assert_not_called()


# ---------------------------------------------------------------------------
# Test convention [start, end) — compatibilité story 20.4 (AC5)
# ---------------------------------------------------------------------------


class TestHouseIntervalCompatibility:
    def test_all_cusps_normalized_for_downstream_interval(self) -> None:
        """Convention [start, end) : toutes les cuspides sont dans [0, 360).

        Story 20.4 utilisera ces cuspides pour assigner les planètes aux maisons
        via la convention [start, end). Ce test vérifie que la normalisation est
        correcte pour éviter tout bug d'intervalle (ex: -0.1 → 359.9).
        """
        # Valeurs brutes limites : 0, 359.99, 360.0 (→ 0), -0.01 (→ 359.99)
        edge_cusps_raw = (
            0.0, 0.0, 359.99, 360.0, -0.01, 45.0, 90.0,
            135.0, 180.0, 225.0, 270.0, 315.0, 350.0,
        )
        edge_ascmc_raw = (0.0, 360.0) + (0.0,) * 8
        mock_swe = _make_swe_mock(
            cusps_raw=edge_cusps_raw, ascmc_raw=edge_ascmc_raw
        )
        with patch.dict("sys.modules", {"swisseph": mock_swe}):
            result = calculate_houses(JDUT_J2000, LAT_PARIS, LON_PARIS)
        for i, cusp in enumerate(result.cusps):
            assert 0.0 <= cusp < 360.0, f"Cuspide maison {i + 1} = {cusp} invalide"
        assert 0.0 <= result.ascendant_longitude < 360.0
        assert 0.0 <= result.mc_longitude < 360.0

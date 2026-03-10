"""Tests unitaires pour temporal_kernel.py — étalement temporel des événements."""

from datetime import datetime, timezone
from math import isclose

import pytest

from app.prediction.schemas import AstroEvent, SamplePoint
from app.prediction.temporal_kernel import (
    _DEFAULT_HALF_WIDTH,
    _FAMILY_HALF_WIDTH,
    spread_event_weights,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_samples(n: int, step_jd: float = 1 / 96) -> list[SamplePoint]:
    """Créé n SamplePoints espacés de step_jd (≈ 15 min par défaut)."""
    base_jd = 2460000.0
    base_dt = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    from datetime import timedelta

    return [
        SamplePoint(
            ut_time=base_jd + i * step_jd,
            local_time=base_dt + timedelta(minutes=i * 15),
        )
        for i in range(n)
    ]


def _make_event(event_type: str, step_index: int, samples: list[SamplePoint]) -> AstroEvent:
    """Créé un AstroEvent centré exactement sur le step donné."""
    return AstroEvent(
        event_type=event_type,
        ut_time=samples[step_index].ut_time,
        local_time=samples[step_index].local_time,
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=0.0,
        priority=1,
        base_weight=1.0,
    )


# ---------------------------------------------------------------------------
# AC1 — Les poids sont normalisés (somme = 1.0)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("event_type", [
    "aspect_exact_to_angle",
    "aspect_exact_to_luminary",
    "aspect_exact_to_personal",
    "aspect_enter_orb",
    "aspect_exit_orb",
    "moon_sign_ingress",
    "asc_sign_change",
    "planetary_hour_change",
    "unknown_future_event",
])
def test_weights_sum_to_one(event_type: str) -> None:
    """Les poids normalisés doivent sommer à 1.0 (conservation d'énergie)."""
    samples = _make_samples(96)
    event = _make_event(event_type, 48, samples)
    result = spread_event_weights(event, samples)
    total = sum(w for _, w in result)
    assert isclose(total, 1.0, rel_tol=1e-9), f"sum={total} for {event_type}"


# ---------------------------------------------------------------------------
# AC2 — La fenêtre dépend du type d'événement
# ---------------------------------------------------------------------------

def test_exact_aspect_to_angle_wider_than_planetary_hour() -> None:
    """aspect_exact_to_angle doit couvrir plus de steps que planetary_hour_change."""
    samples = _make_samples(96)
    event_angle = _make_event("aspect_exact_to_angle", 48, samples)
    event_hour = _make_event("planetary_hour_change", 48, samples)

    spread_angle = spread_event_weights(event_angle, samples)
    spread_hour = spread_event_weights(event_hour, samples)

    assert len(spread_angle) > len(spread_hour)


def test_half_width_governs_coverage() -> None:
    """Le nombre de steps couverts correspond à 2*half_width+1 (clamped)."""
    samples = _make_samples(96)
    for event_type, hw in _FAMILY_HALF_WIDTH.items():
        event = _make_event(event_type, 48, samples)
        result = spread_event_weights(event, samples)
        expected = 2 * hw + 1
        assert len(result) == expected, (
            f"{event_type}: attendu {expected} steps, obtenu {len(result)}"
        )


# ---------------------------------------------------------------------------
# AC3 — Profil montée / plateau / retombée
# ---------------------------------------------------------------------------

def test_center_step_has_highest_weight() -> None:
    """Le step central (peak) doit avoir le poids maximum."""
    samples = _make_samples(96)
    event = _make_event("aspect_exact_to_luminary", 48, samples)
    result = spread_event_weights(event, samples)

    # Tri par index pour retrouver le centre
    sorted_result = sorted(result, key=lambda x: x[0])
    weights = [w for _, w in sorted_result]
    center_pos = next(pos for pos, (idx, _) in enumerate(sorted_result) if idx == 48)

    assert weights[center_pos] == max(weights), "Le step central doit avoir le poids max"


def test_weights_decrease_from_center() -> None:
    """Les poids doivent décroître monotoniquement de part et d'autre du centre."""
    samples = _make_samples(96)
    event = _make_event("aspect_exact_to_personal", 48, samples)
    result = spread_event_weights(event, samples)

    sorted_result = sorted(result, key=lambda x: x[0])
    weights = [w for _, w in sorted_result]

    # Trouver l'index du centre dans la liste triée
    center_pos = next(pos for pos, (idx, _) in enumerate(sorted_result) if idx == 48)

    # Côté gauche : décroissant vers la gauche
    left_weights = weights[:center_pos + 1]
    for i in range(len(left_weights) - 1):
        assert left_weights[i] <= left_weights[i + 1], (
            f"Poids gauche non croissant vers le centre: {left_weights}"
        )

    # Côté droit : décroissant vers la droite
    right_weights = weights[center_pos:]
    for i in range(len(right_weights) - 1):
        assert right_weights[i] >= right_weights[i + 1], (
            f"Poids droite non décroissant: {right_weights}"
        )


# ---------------------------------------------------------------------------
# AC4 — Traçabilité : un seul step reçoit l'événement (centre)
# ---------------------------------------------------------------------------

def test_center_index_is_nearest_step() -> None:
    """Le step de poids maximum correspond au step le plus proche de l'événement."""
    samples = _make_samples(96)
    # Événement centré entre step 10 et 11 — le plus proche est le 10
    mid_ut = (samples[10].ut_time + samples[11].ut_time) / 2 - 0.0001
    event = AstroEvent(
        event_type="aspect_exact_to_personal",
        ut_time=mid_ut,
        local_time=samples[10].local_time,
        body="Mars",
        target="Venus",
        aspect="square",
        orb_deg=0.2,
        priority=2,
        base_weight=0.8,
    )
    result = spread_event_weights(event, samples)

    max_weight_idx = max(result, key=lambda x: x[1])[0]
    assert max_weight_idx == 10, f"Centre attendu=10, obtenu={max_weight_idx}"


# ---------------------------------------------------------------------------
# AC5 — Cas limites : bords du jour
# ---------------------------------------------------------------------------

def test_spread_clipped_at_start() -> None:
    """Un événement en début de journée ne produit pas d'index négatif."""
    samples = _make_samples(96)
    event = _make_event("aspect_exact_to_angle", 0, samples)
    result = spread_event_weights(event, samples)

    indices = [idx for idx, _ in result]
    assert all(idx >= 0 for idx in indices), "Index négatif détecté"
    total = sum(w for _, w in result)
    assert isclose(total, 1.0, rel_tol=1e-9)


def test_spread_clipped_at_end() -> None:
    """Un événement en fin de journée ne dépasse pas le dernier index."""
    samples = _make_samples(96)
    event = _make_event("aspect_exact_to_angle", 95, samples)
    result = spread_event_weights(event, samples)

    indices = [idx for idx, _ in result]
    assert all(idx <= 95 for idx in indices), "Index hors-bornes détecté"
    total = sum(w for _, w in result)
    assert isclose(total, 1.0, rel_tol=1e-9)


def test_empty_samples_returns_empty() -> None:
    """Aucun step disponible → liste vide."""
    event = AstroEvent(
        event_type="aspect_exact_to_personal",
        ut_time=2460000.5,
        local_time=datetime(2026, 1, 1, 12, tzinfo=timezone.utc),
        body="Sun",
        target=None,
        aspect=None,
        orb_deg=None,
        priority=1,
        base_weight=1.0,
    )
    assert spread_event_weights(event, []) == []


def test_single_sample_returns_full_weight() -> None:
    """Un seul step dans la grille reçoit tout le poids."""
    samples = _make_samples(1)
    event = _make_event("aspect_exact_to_angle", 0, samples)
    result = spread_event_weights(event, samples)

    assert len(result) == 1
    assert result[0][0] == 0
    assert isclose(result[0][1], 1.0)


# ---------------------------------------------------------------------------
# Conservation d'énergie : somme totale journalière inchangée
# ---------------------------------------------------------------------------

def test_energy_conservation_multi_event() -> None:
    """La somme des contributions étalées = somme des contributions brutes."""
    samples = _make_samples(96)
    events = [
        _make_event("aspect_exact_to_angle", 20, samples),
        _make_event("planetary_hour_change", 48, samples),
        _make_event("moon_sign_ingress", 70, samples),
    ]
    raw_contributions = {"work": 0.5, "love": -0.3}

    # Simulation : somme brute si chaque événement allait sur 1 step
    expected_total = {cat: len(events) * val for cat, val in raw_contributions.items()}

    # Simulation spread
    spread_totals: dict[str, float] = {}
    for event in events:
        spread = spread_event_weights(event, samples)
        for step_i, weight in spread:
            for cat, contrib in raw_contributions.items():
                spread_totals[cat] = spread_totals.get(cat, 0.0) + contrib * weight

    for cat in raw_contributions:
        assert isclose(spread_totals[cat], expected_total[cat], rel_tol=1e-9), (
            f"Énergie non conservée pour {cat}: attendu={expected_total[cat]}, "
            f"obtenu={spread_totals[cat]}"
        )


# ---------------------------------------------------------------------------
# Default fallback pour event_type inconnu
# ---------------------------------------------------------------------------

def test_unknown_event_type_uses_default_half_width() -> None:
    """Un type inconnu utilise _DEFAULT_HALF_WIDTH."""
    samples = _make_samples(96)
    event = _make_event("totally_unknown_type", 48, samples)
    result = spread_event_weights(event, samples)
    expected_count = 2 * _DEFAULT_HALF_WIDTH + 1
    assert len(result) == expected_count

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from typing import Any

from app.prediction.schemas import AstroEvent

BASE_TIME = datetime(2026, 3, 9, 6, 0, 0)
STEP = timedelta(minutes=15)


@dataclass(frozen=True)
class SimulatedNatalProfile:
    birth_date: date
    birth_place: str
    birth_timezone: str
    birth_lat: float
    birth_lon: float
    current_lat: float
    current_lon: float
    current_timezone: str


def make_step_times(n: int) -> list[datetime]:
    return [BASE_TIME + i * STEP for i in range(n)]


def make_notes(
    n: int,
    default: int = 10,
    variations: dict[int, dict[str, int]] | None = None,
) -> list[dict[str, int]]:
    codes = ["energy", "mood", "work", "love", "money", "health"]
    result = []
    for i in range(n):
        step_notes = {code: default for code in codes}
        if variations and i in variations:
            step_notes.update(variations[i])
        result.append(step_notes)
    return result


def make_event(event_type: str, priority: int, step_index: int) -> AstroEvent:
    event_time = BASE_TIME + step_index * STEP
    return AstroEvent(
        event_type=event_type,
        ut_time=float(step_index),
        local_time=event_time,
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=0.5,
        priority=priority,
        base_weight=1.0,
    )


def _build_fixture(
    *,
    target_date: date,
    simulated_natal_profile: SimulatedNatalProfile,
    notes_by_step: list[dict[str, int]],
    events_by_step: list[list[AstroEvent]],
    step_times: list[datetime],
    expected_pivot_range: tuple[int, int],
    expected_window_range: tuple[int, int],
    baselines: dict[str, dict[str, float]] | None = None,
    mock_engine: bool = False,
) -> dict[str, Any]:
    return {
        "target_date": target_date.isoformat(),
        "simulated_natal_profile": asdict(simulated_natal_profile),
        "notes_by_step": notes_by_step,
        "events_by_step": events_by_step,
        "step_times": step_times,
        "expected_pivot_range": expected_pivot_range,
        "expected_window_range": expected_window_range,
        "baselines": baselines,
        "mock_engine": mock_engine,
    }


def get_calm_day() -> dict[str, Any]:
    """
    Scénario calm_day : tous les delta_notes < 3, aucun événement décisionnel priority >= 65
    → 0 pivot attendu, 0–2 decision_windows
    """
    n_steps = 96
    natal = SimulatedNatalProfile(
        birth_date=date(1992, 11, 18),
        birth_place="Paris",
        birth_timezone="Europe/Paris",
        birth_lat=48.8566,
        birth_lon=2.3522,
        current_lat=48.8566,
        current_lon=2.3522,
        current_timezone="Europe/Paris",
    )
    return _build_fixture(
        target_date=date(2026, 3, 5),
        simulated_natal_profile=natal,
        notes_by_step=make_notes(n_steps, default=10),
        events_by_step=[[] for _ in range(n_steps)],
        step_times=make_step_times(n_steps),
        expected_pivot_range=(0, 0),
        expected_window_range=(0, 0),
        mock_engine=True,  # Force calm for QA test reliability
    )


def get_flat_day_with_micro_trends() -> dict[str, Any]:
    """
    Scénario flat_day_with_micro_trends : journée calme mais avec un signal relatif fort.
    """
    n_steps = 96
    natal = SimulatedNatalProfile(
        birth_date=date(1995, 5, 5),
        birth_place="Marseille",
        birth_timezone="Europe/Paris",
        birth_lat=43.2965,
        birth_lon=5.3698,
        current_lat=43.2965,
        current_lon=5.3698,
        current_timezone="Europe/Paris",
    )

    # Baseline with low mean for love, making 10.0 a strong relative score
    baselines = {
        "love": {
            "mean_raw_score": 5.0,
            "std_raw_score": 2.0,  # Z = (10 - 5) / 2 = 2.5
            "p10": 2.0,
            "p50": 5.0,
            "p90": 8.0,
        },
        "work": {
            "mean_raw_score": 10.0,
            "std_raw_score": 2.0,  # Z = 0
            "p10": 7.0,
            "p50": 10.0,
            "p90": 13.0,
        },
    }

    return _build_fixture(
        target_date=date(2026, 3, 12),
        simulated_natal_profile=natal,
        notes_by_step=make_notes(n_steps, default=10),  # raw_score defaults to ~10.0 in mock engine
        events_by_step=[[] for _ in range(n_steps)],
        step_times=make_step_times(n_steps),
        expected_pivot_range=(0, 0),
        expected_window_range=(0, 0),
        baselines=baselines,
        mock_engine=True,
    )


def get_flat_day_no_signal() -> dict[str, Any]:
    """
    Scénario flat_day_no_signal : journée calme, signal relatif faible.
    """
    n_steps = 96
    natal = SimulatedNatalProfile(
        birth_date=date(1985, 12, 12),
        birth_place="Lille",
        birth_timezone="Europe/Paris",
        birth_lat=50.6292,
        birth_lon=3.0573,
        current_lat=50.6292,
        current_lon=3.0573,
        current_timezone="Europe/Paris",
    )

    # Baseline matching the current scores
    baselines = {
        "love": {"mean_raw_score": 10.0, "std_raw_score": 2.0, "p10": 7.0, "p50": 10.0, "p90": 13.0}
    }

    return _build_fixture(
        target_date=date(2026, 3, 13),
        simulated_natal_profile=natal,
        notes_by_step=make_notes(n_steps, default=10),
        events_by_step=[[] for _ in range(n_steps)],
        step_times=make_step_times(n_steps),
        expected_pivot_range=(0, 0),
        expected_window_range=(0, 0),
        baselines=baselines,
        mock_engine=True,
    )


def get_active_day() -> dict[str, Any]:
    """
    Scénario active_day : plusieurs delta_notes >= 3 sur catégories distinctes
    + plusieurs événements absolus structurants visibles publiquement
    → 2–4 pivots attendus, 2–4 decision_windows
    """
    n_steps = 96
    natal = SimulatedNatalProfile(
        birth_date=date(1990, 1, 1),
        birth_place="Paris",
        birth_timezone="Europe/Paris",
        birth_lat=48.85,
        birth_lon=2.35,
        current_lat=48.85,
        current_lon=2.35,
        current_timezone="Europe/Paris",
    )
    variations = {
        20: {"energy": 14},
        50: {"love": 6},
    }
    events = [[] for _ in range(n_steps)]
    events[30] = [make_event("aspect_exact_to_personal", 70, 30)]
    return _build_fixture(
        target_date=date(2026, 3, 15),
        simulated_natal_profile=natal,
        notes_by_step=make_notes(n_steps, default=10, variations=variations),
        events_by_step=events,
        step_times=make_step_times(n_steps),
        expected_pivot_range=(2, 4),
        expected_window_range=(2, 4),
    )


def get_transition_day() -> dict[str, Any]:
    """
    Scénario transition_day : un événement moon_sign_ingress priority >= 65
    → 1 pivot high_priority_event, 1 decision_window de type pivot
    """
    n_steps = 96
    natal = SimulatedNatalProfile(
        birth_date=date(1988, 7, 22),
        birth_place="Lyon",
        birth_timezone="Europe/Paris",
        birth_lat=45.764,
        birth_lon=4.8357,
        current_lat=45.764,
        current_lon=4.8357,
        current_timezone="Europe/Paris",
    )
    events = [[] for _ in range(n_steps)]
    events[40] = [make_event("moon_sign_ingress", 65, 40)]
    return _build_fixture(
        target_date=date(2026, 3, 7),
        simulated_natal_profile=natal,
        notes_by_step=make_notes(n_steps, default=10),
        events_by_step=events,
        step_times=make_step_times(n_steps),
        expected_pivot_range=(1, 1),
        expected_window_range=(1, 1),
    )


def get_ambiguous_day() -> dict[str, Any]:
    """
    Scénario ambiguous_day : Signaux contradictoires forts.
    Love à 18, Work à 4.
    """
    n_steps = 96
    natal = SimulatedNatalProfile(
        birth_date=date(1980, 10, 10),
        birth_place="Bordeaux",
        birth_timezone="Europe/Paris",
        birth_lat=44.8378,
        birth_lon=-0.5792,
        current_lat=44.8378,
        current_lon=-0.5792,
        current_timezone="Europe/Paris",
    )
    variations = {
        30: {"love": 18, "work": 4},
        60: {"love": 19, "work": 3},
    }
    return _build_fixture(
        target_date=date(2026, 3, 20),
        simulated_natal_profile=natal,
        notes_by_step=make_notes(n_steps, default=10, variations=variations),
        events_by_step=[[] for _ in range(n_steps)],
        step_times=make_step_times(n_steps),
        expected_pivot_range=(1, 3),
        expected_window_range=(1, 3),
    )


def get_intense_neutral_day() -> dict[str, Any]:
    """
    Scénario intense_neutral_day : Beaucoup d'aspects techniques (priorité 50-60)
    mais notes globales stables autour de 10.
    """
    n_steps = 96
    natal = SimulatedNatalProfile(
        birth_date=date(1975, 3, 3),
        birth_place="Nantes",
        birth_timezone="Europe/Paris",
        birth_lat=47.2184,
        birth_lon=-1.5536,
        current_lat=47.2184,
        current_lon=-1.5536,
        current_timezone="Europe/Paris",
    )
    events = [[] for _ in range(n_steps)]
    for i in range(10, 90, 10):
        events[i] = [make_event("aspect_minor", 55, i)]

    return _build_fixture(
        target_date=date(2026, 3, 25),
        simulated_natal_profile=natal,
        notes_by_step=make_notes(n_steps, default=10),
        events_by_step=events,
        step_times=make_step_times(n_steps),
        expected_pivot_range=(0, 2),
        expected_window_range=(0, 2),
    )

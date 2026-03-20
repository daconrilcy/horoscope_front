from datetime import datetime
from unittest.mock import MagicMock

from app.prediction.public_projection import PublicTimeWindowPolicy


def test_time_window_resolve_regime_progression():
    policy = PublicTimeWindowPolicy()
    start = datetime(2026, 3, 18, 14, 0)
    end = datetime(2026, 3, 18, 18, 0)

    regime = policy._resolve_regime(start, end, "rising", [])
    assert regime == "progression"


def test_time_window_resolve_regime_pivot():
    policy = PublicTimeWindowPolicy()
    start = datetime(2026, 3, 18, 14, 0)
    end = datetime(2026, 3, 18, 18, 0)
    turning_points = [{"occurred_at_local": "2026-03-18T15:30:00"}]

    regime = policy._resolve_regime(start, end, "rising", turning_points)
    assert regime == "pivot"


def test_time_window_resolve_regime_recovery_night():
    policy = PublicTimeWindowPolicy()
    start = datetime(2026, 3, 18, 2, 0)
    end = datetime(2026, 3, 18, 6, 0)

    regime = policy._resolve_regime(start, end, "stable", [])
    assert regime == "récupération"


def test_time_window_map_domains():
    policy = PublicTimeWindowPolicy()
    # work, career -> pro_ambition
    # love -> relations_echanges
    internal = ["work", "career", "love"]
    public = policy._map_domains(internal)
    assert public == ["pro_ambition", "relations_echanges"]


def test_time_window_build_four_periods():
    policy = PublicTimeWindowPolicy()
    snapshot = MagicMock()
    snapshot.local_date = datetime(2026, 3, 18)

    # Mock blocks for different periods
    class MockBlock:
        def __init__(self, hour, theme):
            self.start_local = datetime(2026, 3, 18, hour, 0)
            self.end_local = datetime(2026, 3, 18, (hour + 2) % 24, 0)
            if hour + 2 >= 24:
                # Add a day if it wraps
                from datetime import timedelta

                self.end_local += timedelta(days=1)
            self.orientation = "rising"
            self.themes = [theme]

    blocks = [
        MockBlock(23, "dream"),  # Nuit
        MockBlock(8, "work"),  # Matin
        MockBlock(14, "love"),  # Après-midi
        MockBlock(20, "home"),  # Soirée
    ]

    evidence = MagicMock()
    evidence.time_windows = blocks

    result = policy.build(snapshot, [], evidence=evidence)

    assert len(result) == 4
    keys = [r["period_key"] for r in result]
    assert keys == ["nuit", "matin", "apres_midi", "soiree"]

    # Check Morning (Matin)
    matin = next(r for r in result if r["period_key"] == "matin")
    assert matin["time_range"] == "06:00–12:00"
    assert matin["regime"] == "progression"  # rising -> progression
    assert "pro_ambition" in matin["top_domains"]


def test_time_window_empty_blocks_defaults():
    policy = PublicTimeWindowPolicy()
    snapshot = MagicMock()
    snapshot.local_date = datetime(2026, 3, 18)

    result = policy.build(snapshot, [], evidence=None, engine_output=None)
    assert len(result) == 4
    # Default regime for Matin should be mise_en_route according to dev notes
    matin = next(r for r in result if r["period_key"] == "matin")
    assert matin["regime"] == "mise_en_route"

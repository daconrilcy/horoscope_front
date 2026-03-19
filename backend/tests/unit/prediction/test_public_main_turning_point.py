from datetime import datetime
from unittest.mock import MagicMock

from app.prediction.public_projection import PublicMainTurningPointPolicy


def test_main_turning_point_filter_severity():
    policy = PublicMainTurningPointPolicy()

    tp1 = MagicMock()
    tp1.severity = 0.2  # Below 0.3
    tp1.confidence = 0.6

    tp2 = MagicMock()
    tp2.severity = 0.4
    tp2.confidence = 0.4  # Below 0.5

    evidence = MagicMock()
    evidence.turning_points = [tp1, tp2]

    result = policy.build(MagicMock(), evidence=evidence)
    assert result is None


def test_main_turning_point_select_best():
    policy = PublicMainTurningPointPolicy()

    class MockTP:
        def __init__(self, sev, conf, time, ctype, themes):
            self.severity = sev
            self.confidence = conf
            self.local_time = time
            self.change_type = ctype
            self.themes = themes
            self.categories_impacted = []  # explicitly empty

    tp1 = MockTP(0.4, 0.6, datetime(2026, 3, 18, 10, 0), "emergence", ["work"])
    tp2 = MockTP(0.6, 0.7, datetime(2026, 3, 18, 15, 0), "recomposition", ["love"])

    evidence = MagicMock()
    evidence.turning_points = [tp1, tp2]

    result = policy.build(MagicMock(), evidence=evidence)
    assert result["title"] == "Nouvelle donne relationnelle"  # recomposition + love
    assert result["change_type"] == "recomposition"
    assert result["time"] == "15:00"


def test_main_turning_point_map_domains():
    policy = PublicMainTurningPointPolicy()
    internal = ["work", "career", "love", "money"]
    public = policy._map_domains(internal)
    # work, career -> pro_ambition (1)
    # love -> relations_echanges (2)
    # money -> argent_ressources (3)
    assert public == ["pro_ambition", "relations_echanges", "argent_ressources"]
    assert len(public) == 3

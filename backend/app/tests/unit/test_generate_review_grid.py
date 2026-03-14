from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from app.jobs.calibration import generate_review_grid as module


class FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class FakeSession:
    def __init__(self, rows):
        self._rows = rows
        self.closed = False
        self.executed_query = None

    def execute(self, query):
        self.executed_query = query
        return FakeResult(self._rows)

    def close(self):
        self.closed = True


def _record(**kwargs):
    return SimpleNamespace(_mapping=kwargs)


def test_note_to_band_mapping():
    assert module.note_to_band(5) == "fragile"
    assert module.note_to_band(9) == "tendu"
    assert module.note_to_band(12) == "neutre"
    assert module.note_to_band(16) == "porteur"
    assert module.note_to_band(17) == "tres favorable"
    assert module.note_to_band(20) == "tres favorable"
    assert module.note_to_band(None) == "N/A"


def test_generate_grid_markdown_has_required_columns_and_enrichment(monkeypatch):
    fake_session = FakeSession(
        [
            _record(
                local_date=date(2024, 1, 1),
                category_code="love",
                score_raw_day=0.5,
                note_20=15,
                score_power=None,
                score_volatility=None,
                contributors_json='[{"rule_id":"venus_trine"},{"source":"transit|mars"}]',
                calibration_raw_day=0.55,
                calibration_power=1.25,
                calibration_volatility=0.375,
            )
        ]
    )
    monkeypatch.setattr(module, "SessionLocal", lambda: fake_session)

    md = module.generate_grid(
        date(2024, 1, 1),
        date(2024, 1, 1),
        user_id=42,
        profile_label="profile_paris_aries",
    )

    assert fake_session.closed is True
    assert (
        "| Date | Categorie | Raw Day | Note/20 | Bande UX | Power | Volatilite | "
        "Top Contributeurs | Commentaire |"
    ) in md
    assert (
        "| 2024-01-01 | love | 0.5 | 15 | porteur | 1.25 | 0.375 | venus_trine, transit\\|mars |  |"
    ) in md


def test_generate_grid_csv_uses_score_values_and_serializes_headers(monkeypatch):
    fake_session = FakeSession(
        [
            _record(
                local_date=date(2024, 1, 2),
                category_code="work",
                score_raw_day=0.75,
                note_20=18,
                score_power=1.5,
                score_volatility=0.2,
                contributors_json='["saturn","jupiter"]',
                calibration_raw_day=0.7,
                calibration_power=9.0,
                calibration_volatility=9.0,
            )
        ]
    )
    monkeypatch.setattr(module, "SessionLocal", lambda: fake_session)

    content = module.generate_grid(
        date(2024, 1, 2),
        date(2024, 1, 2),
        fmt="csv",
    )

    rows = list(csv.DictReader(content.splitlines()))
    assert rows == [
        {
            "date": "2024-01-02",
            "category": "work",
            "raw_day": "0.75",
            "note_20": "18",
            "band": "tres favorable",
            "power": "1.5",
            "volatility": "0.2",
            "top_contributors": "saturn, jupiter",
            "commentaire": "",
        }
    ]


def test_to_markdown_empty():
    assert module._to_markdown([]) == "Aucune donnee trouvee."


def test_main_writes_default_output_and_returns_zero(monkeypatch, tmp_path):
    monkeypatch.setattr(module, "generate_grid", lambda *args, **kwargs: "content")
    monkeypatch.setattr(module, "_resolve_project_root", lambda: tmp_path)

    exit_code = module.main(["--start", "2024-01-01", "--end", "2024-01-02"])

    assert exit_code == 0
    output_path = tmp_path / "docs" / "calibration" / "review-grid-2024-01-02.md"
    assert output_path.read_text(encoding="utf-8") == "content"


def test_main_rejects_invalid_date_range(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "_resolve_project_root", lambda: tmp_path)

    exit_code = module.main(["--start", "2024-01-02", "--end", "2024-01-01"])

    assert exit_code == 2


def test_default_output_path_uses_docs_calibration(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "_resolve_project_root", lambda: tmp_path)

    result = module._default_output_path("csv", date(2024, 1, 3))

    assert result == Path(tmp_path, "docs", "calibration", "review-grid-2024-01-03.csv")

from __future__ import annotations

import inspect
from dataclasses import dataclass
from datetime import date, datetime, timezone

from app.prediction.block_generator import TimeBlock
from app.prediction.editorial_builder import EditorialOutputBuilder
from app.prediction.explainability import (
    CategoryExplainability,
    ContributorEntry,
    ExplainabilityReport,
)
from app.prediction.schemas import EffectiveContext, EngineOutput
from app.prediction.turning_point_detector import TurningPoint


@dataclass(frozen=True)
class MockScore:
    note_20: int
    power: float
    volatility: float
    sort_order: int = 0


@dataclass(frozen=True)
class MockTimeBlock:
    start_local: datetime
    end_local: datetime
    dominant_categories: list[str]
    tone_code: str
    category_means: dict[str, float]


def create_mock_engine_output(
    scores_dict: dict[str, MockScore | dict[str, float | int]],
    *,
    run_metadata: dict | None = None,
    turning_points: list[TurningPoint] | None = None,
    time_blocks: list[object] | None = None,
) -> EngineOutput:
    return EngineOutput(
        run_metadata=run_metadata or {},
        effective_context=EffectiveContext(
            house_system_requested="placidus",
            house_system_effective="placidus",
            local_date=date(2026, 3, 8),
            timezone="UTC",
            input_hash="hash",
        ),
        category_scores=scores_dict,
        turning_points=turning_points or [],
        time_blocks=time_blocks or [],
    )


def create_mock_explainability(
    categories_contributors: dict[str, list[ContributorEntry]] | None = None,
) -> ExplainabilityReport:
    categories: dict[str, CategoryExplainability] = {}
    if categories_contributors:
        for code, contributors in categories_contributors.items():
            categories[code] = CategoryExplainability(code, contributors)
    return ExplainabilityReport(run_input_hash="hash", categories=categories)


def test_top3_sorted_desc_with_tiebreak() -> None:
    builder = EditorialOutputBuilder()
    scores = {
        "cat1": MockScore(15, 1.0, 0.5, 2),
        "cat2": MockScore(18, 1.0, 0.5, 4),
        "cat3": MockScore(15, 1.0, 0.5, 1),
        "cat4": MockScore(12, 1.0, 0.5, 3),
    }

    output = builder.build(create_mock_engine_output(scores), create_mock_explainability())

    assert [category.code for category in output.top3_categories] == ["cat2", "cat3", "cat1"]


def test_bottom2_lowest_and_disjoint() -> None:
    builder = EditorialOutputBuilder()
    scores = {
        "cat1": MockScore(18, 1.0, 0.5, 1),
        "cat2": MockScore(16, 1.0, 0.5, 2),
        "cat3": MockScore(14, 1.0, 0.5, 3),
        "cat4": MockScore(8, 1.0, 0.5, 4),
        "cat5": MockScore(5, 1.0, 0.5, 5),
    }

    output = builder.build(create_mock_engine_output(scores), create_mock_explainability())

    assert [category.code for category in output.bottom2_categories] == ["cat5", "cat4"]
    assert {category.code for category in output.top3_categories}.isdisjoint(
        {category.code for category in output.bottom2_categories}
    )


def test_main_pivot_max_severity() -> None:
    builder = EditorialOutputBuilder()
    dt = datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc)
    pivots = [
        TurningPoint(dt, "delta_note", ["love"], None, 0.5),
        TurningPoint(dt, "high_priority_event", ["work"], None, 0.9),
        TurningPoint(dt, "top3_change", ["finance"], None, 0.7),
    ]

    output = builder.build(
        create_mock_engine_output({}, turning_points=pivots),
        create_mock_explainability(),
    )

    assert output.main_pivot == pivots[1]


def test_no_pivot_returns_none() -> None:
    builder = EditorialOutputBuilder()

    output = builder.build(
        create_mock_engine_output({}, turning_points=[]),
        create_mock_explainability(),
    )

    assert output.main_pivot is None


def test_best_window_uses_top3_mean_proxy() -> None:
    builder = EditorialOutputBuilder()
    dt1 = datetime(2026, 3, 8, 8, 0, tzinfo=timezone.utc)
    dt2 = datetime(2026, 3, 8, 9, 30, tzinfo=timezone.utc)
    dt3 = datetime(2026, 3, 8, 11, 0, tzinfo=timezone.utc)
    scores = {
        "love": MockScore(16, 1.0, 0.5, 1),
        "work": MockScore(14, 1.0, 0.5, 2),
        "money": MockScore(13, 1.0, 0.5, 3),
        "health": MockScore(6, 1.0, 0.5, 4),
    }
    time_blocks = [
        MockTimeBlock(
            start_local=dt1,
            end_local=dt2,
            dominant_categories=["love"],
            tone_code="positive",
            category_means={"love": 11.0, "work": 10.0, "money": 9.0},
        ),
        MockTimeBlock(
            start_local=dt2,
            end_local=dt3,
            dominant_categories=["work"],
            tone_code="neutral",
            category_means={"love": 17.0, "work": 16.0, "money": 15.0},
        ),
    ]

    output = builder.build(
        create_mock_engine_output(scores, time_blocks=time_blocks),
        create_mock_explainability(),
    )

    assert output.best_window is not None
    assert output.best_window.start_local == dt2
    assert output.best_window.end_local == dt3
    assert output.best_window.dominant_category == "work"


def test_caution_flags_use_ruleset_config() -> None:
    builder = EditorialOutputBuilder()
    scores = {
        "finance": MockScore(7, 1.0, 1.8, 1),
        "health": MockScore(14, 1.0, 0.1, 2),
    }

    output = builder.build(
        create_mock_engine_output(
            scores,
            run_metadata={"caution_category_codes": ["finance"]},
        ),
        create_mock_explainability(),
    )

    assert output.caution_flags == {"finance": True}


def test_no_caution_when_thresholds_not_met() -> None:
    builder = EditorialOutputBuilder()
    scores = {
        "health": MockScore(10, 1.0, 0.5, 1),
        "money": MockScore(12, 1.0, 0.5, 2),
    }

    output = builder.build(create_mock_engine_output(scores), create_mock_explainability())

    assert output.caution_flags["health"] is False
    assert output.caution_flags["money"] is False


def test_overall_tone_positive_negative_and_mixed() -> None:
    builder = EditorialOutputBuilder()

    positive = builder.build(
        create_mock_engine_output(
            {
                "a": MockScore(14, 1.0, 0.5, 1),
                "b": MockScore(15, 1.0, 0.5, 2),
                "c": MockScore(13, 1.0, 0.5, 3),
            }
        ),
        create_mock_explainability(),
    )
    negative = builder.build(
        create_mock_engine_output(
            {
                "a": MockScore(6, 1.0, 0.5, 1),
                "b": MockScore(7, 1.0, 0.5, 2),
                "c": MockScore(5, 1.0, 0.5, 3),
            }
        ),
        create_mock_explainability(),
    )
    mixed = builder.build(
        create_mock_engine_output(
            {
                "a": MockScore(15, 1.0, 0.5, 1),
                "b": MockScore(10, 1.0, 0.5, 2),
                "c": MockScore(12, 1.0, 0.5, 3),
            }
        ),
        create_mock_explainability(),
    )

    assert positive.overall_tone == "positive"
    assert negative.overall_tone == "negative"
    assert mixed.overall_tone == "mixed"


def test_contributors_include_all_available_categories() -> None:
    builder = EditorialOutputBuilder()
    dt = datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc)
    contributor = ContributorEntry("trine", "Venus", "Mars", "trine", 5.0, dt, 0.5, "direct")
    explainability = create_mock_explainability(
        {
            "love": [contributor],
            "finance": [contributor],
        }
    )
    scores = {
        "love": MockScore(15, 1.0, 0.5, 1),
        "work": MockScore(13, 1.0, 0.5, 2),
        "health": MockScore(12, 1.0, 0.5, 3),
    }

    output = builder.build(create_mock_engine_output(scores), explainability)

    assert output.top3_contributors_per_category["love"][0].body == "Venus"
    assert output.top3_contributors_per_category["finance"][0].body == "Venus"
    assert output.top3_contributors_per_category["work"] == []


def test_no_llm_dependency_in_builder_source() -> None:
    source = inspect.getsource(EditorialOutputBuilder).lower()

    assert "openai" not in source
    assert "client.responses" not in source


def test_builder_supports_real_timeblock_objects_with_fallback() -> None:
    builder = EditorialOutputBuilder()
    dt1 = datetime(2026, 3, 8, 8, 0, tzinfo=timezone.utc)
    dt2 = datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc)
    scores = {
        "love": {"note_20": 15, "power": 1.0, "volatility": 0.5, "sort_order": 1},
        "work": {"note_20": 14, "power": 1.0, "volatility": 0.5, "sort_order": 2},
        "money": {"note_20": 13, "power": 1.0, "volatility": 0.5, "sort_order": 3},
    }
    time_blocks = [
        TimeBlock(0, dt1, dt2, ["love"], "positive", []),
    ]

    output = builder.build(
        create_mock_engine_output(scores, time_blocks=time_blocks),
        create_mock_explainability(),
    )

    assert output.best_window is not None
    assert output.best_window.dominant_category == "love"

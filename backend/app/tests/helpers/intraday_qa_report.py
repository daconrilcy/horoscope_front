# backend/app/tests/helpers/intraday_qa_report.py
from dataclasses import dataclass, field
from typing import List

TECHNICAL_DRIVER_CODES = {
    "enter_orb",
    "exit_orb",
    "moon_sign_ingress",
    "asc_sign_change",
    "aspect_enter_orb",
    "aspect_exit_orb",
    "aspect_exact_to_angle",
    "aspect_exact_to_luminary",
    "aspect_exact_to_personal",
}


@dataclass
class IntradayQAReport:
    total_blocks: int
    total_pivots: int
    total_decision_windows: int
    noise_blocks: int
    technical_drivers_found: List[str] = field(default_factory=list)
    identical_consecutive_blocks: int = 0
    total_micro_trends: int = 0


def build_report(response_data: dict) -> IntradayQAReport:
    timeline = response_data.get("timeline", [])
    turning_points = response_data.get("turning_points", [])
    decision_windows = response_data.get("decision_windows", []) or []
    micro_trends = response_data.get("micro_trends", []) or []

    # Codes techniques résiduels détectés dans les decision_windows.
    tech_drivers = []
    for dw in decision_windows:
        cats = dw.get("dominant_categories", [])
        for cat in cats:
            if cat in TECHNICAL_DRIVER_CODES:
                tech_drivers.append(cat)

    # Blocs neutres sans pivot, donc candidats au bruit intraday.
    noise_blocks_count = 0
    for block in timeline:
        if block.get("tone_code") == "neutral":
            is_pivot_block = any(
                tp["occurred_at_local"] == block["start_local"]
                for tp in turning_points
                if block["start_local"] != timeline[0]["start_local"]
            )
            is_pivot_block = is_pivot_block or any(
                tp["occurred_at_local"] == block["end_local"]
                for tp in turning_points
                if block["end_local"] != timeline[-1]["end_local"]
            )

            if not is_pivot_block:
                noise_blocks_count += 1

    # Paires consécutives identiques sans turning point explicite.
    identical_consecutive = 0
    for i in range(len(timeline) - 1):
        curr = timeline[i]
        nxt = timeline[i + 1]
        if curr.get("turning_point") or nxt.get("turning_point"):
            continue
        if curr.get("tone_code") == nxt.get("tone_code") and curr.get(
            "dominant_categories"
        ) == nxt.get("dominant_categories"):
            identical_consecutive += 1

    return IntradayQAReport(
        total_blocks=len(timeline),
        total_pivots=len(turning_points),
        total_decision_windows=len(decision_windows),
        noise_blocks=noise_blocks_count,
        technical_drivers_found=tech_drivers,
        identical_consecutive_blocks=identical_consecutive,
        total_micro_trends=len(micro_trends),
    )


def assert_within_budget(
    report: IntradayQAReport,
    *,
    max_windows: int,
    max_identical_blocks: int,
    max_technical_drivers: int,
    max_micro_trends: int = 3,
):
    errors = []
    if report.total_decision_windows > max_windows:
        errors.append(
            f"Too many decision windows: {report.total_decision_windows} (max: {max_windows})"
        )

    if report.identical_consecutive_blocks > max_identical_blocks:
        errors.append(
            "Too many identical consecutive blocks: "
            f"{report.identical_consecutive_blocks} (max: {max_identical_blocks})"
        )

    if len(report.technical_drivers_found) > max_technical_drivers:
        errors.append(
            "Technical drivers found in decision windows: "
            f"{report.technical_drivers_found} (max: {max_technical_drivers})"
        )

    if report.total_micro_trends > max_micro_trends:
        errors.append(
            f"Too many micro-trends: {report.total_micro_trends} (max: {max_micro_trends})"
        )

    if errors:
        raise AssertionError("\n".join(errors))


def assert_fixture_expectations(
    report: IntradayQAReport,
    *,
    expected_pivot_range: tuple[int, int],
    expected_window_range: tuple[int, int],
) -> None:
    errors = []

    min_pivots, max_pivots = expected_pivot_range
    if not min_pivots <= report.total_pivots <= max_pivots:
        errors.append(
            "Unexpected pivot count: "
            f"{report.total_pivots} (expected between {min_pivots} and {max_pivots})"
        )

    min_windows, max_windows = expected_window_range
    if not min_windows <= report.total_decision_windows <= max_windows:
        errors.append(
            "Unexpected decision window count: "
            f"{report.total_decision_windows} (expected between {min_windows} and {max_windows})"
        )

    if errors:
        raise AssertionError("\n".join(errors))

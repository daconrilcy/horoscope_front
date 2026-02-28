#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings  # noqa: E402
from app.core.ephemeris import bootstrap_swisseph  # noqa: E402
from app.domain.astrology.ephemeris_provider import calculate_planets  # noqa: E402
from app.domain.astrology.houses_provider import calculate_houses  # noqa: E402
from app.domain.astrology.natal_calculation import sign_from_longitude  # noqa: E402
from app.domain.astrology.natal_preparation import BirthInput, prepare_birth_data  # noqa: E402
from app.services.cross_tool_report import (  # noqa: E402
    build_run_report,
    ensure_dev_only_runtime,
    render_markdown_report,
)
from app.tests.golden.pro_fixtures import load_golden_pro_dataset  # noqa: E402


def _build_case_payload(case: object) -> dict[str, object]:
    birth_input = BirthInput(
        birth_date=case.datetime.birth_date,
        birth_time=case.datetime.birth_time,
        birth_place=case.place_resolved.name,
        birth_timezone=case.datetime.birth_timezone,
        birth_lat=case.place_resolved.lat,
        birth_lon=case.place_resolved.lon,
    )
    prepared = prepare_birth_data(birth_input)
    planets_result = calculate_planets(
        prepared.julian_day,
        lat=case.place_resolved.lat,
        lon=case.place_resolved.lon,
        zodiac=case.settings.zodiac,
        frame=case.settings.frame,
        altitude_m=case.place_resolved.altitude_m,
    )
    houses_result = calculate_houses(
        prepared.julian_day,
        lat=case.place_resolved.lat,
        lon=case.place_resolved.lon,
        house_system=case.settings.house_system,
        frame=case.settings.frame,
        altitude_m=case.place_resolved.altitude_m,
    )
    planets = {planet.planet_id: planet for planet in planets_result.planets}

    return {
        "case_id": case.case_id,
        "settings": case.settings.model_dump(),
        "expected": case.expected.model_dump(),
        "actual": {
            "sun": planets["sun"].longitude,
            "moon": planets["moon"].longitude,
            "mercury": planets["mercury"].longitude,
            "asc": houses_result.ascendant_longitude,
            "mc": houses_result.mc_longitude,
            "cusp_1": houses_result.cusps[0],
            "cusp_10": houses_result.cusps[9],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a dev-only cross-tool drift report from golden-pro dataset."
    )
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "artifacts" / "cross-tool"),
        help="Directory where JSON/Markdown reports are written.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown", "both"),
        default="both",
        help="Report output format.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional number of cases to process (0 = all).",
    )
    args = parser.parse_args()

    try:
        ensure_dev_only_runtime(os.environ)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 2

    if settings.swisseph_enabled:
        bootstrap_swisseph(
            data_path=settings.swisseph_data_path,
            path_version=settings.swisseph_path_version,
            required_files=settings.swisseph_required_files,
        )

    dataset = load_golden_pro_dataset()
    selected_cases = dataset.cases if args.limit <= 0 else dataset.cases[: args.limit]
    case_payloads = [_build_case_payload(case) for case in selected_cases]
    report = build_run_report(
        dataset_id=dataset.dataset_id,
        tolerances=dataset.tolerances,
        cases=case_payloads,
    )

    # Log local settings compared (without PII): one aggregate signature per run.
    unique_settings = sorted(
        {
            (
                case.settings.engine,
                case.settings.ephe,
                case.settings.frame,
                case.settings.zodiac,
                case.settings.house_system,
            )
            for case in selected_cases
        }
    )
    report["compared_settings"] = [
        {
            "engine": setting[0],
            "ephe": setting[1],
            "frame": setting[2],
            "zodiac": setting[3],
            "house_system": setting[4],
        }
        for setting in unique_settings
    ]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "cross-tool-drift-report.json"
    markdown_path = output_dir / "cross-tool-drift-report.md"

    if args.format in {"json", "both"}:
        json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"json_report={json_path}")

    if args.format in {"markdown", "both"}:
        markdown_path.write_text(render_markdown_report(report), encoding="utf-8")
        print(f"markdown_report={markdown_path}")

    print(
        "drift_summary",
        json.dumps(report["summary"], ensure_ascii=False, separators=(",", ":")),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

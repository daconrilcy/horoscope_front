import json
from datetime import date
from pathlib import Path

from app.prediction.schemas import EngineInput
from app.tests.regression.helpers import (
    assert_clamps,
    create_orchestrator,
    create_session,
    serialize_output,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def build_base_natal():
    return {
        "planets": [
            {"code": "sun", "longitude": 280.368920},
            {"code": "moon", "longitude": 223.323775},
            {"code": "mercury", "longitude": 271.889275},
            {"code": "venus", "longitude": 250.0},
            {"code": "mars", "longitude": 147.471070},
            {"code": "jupiter", "longitude": 15.0},
            {"code": "saturn", "longitude": 40.395639},
            {"code": "uranus", "longitude": 300.0},
            {"code": "neptune", "longitude": 310.0},
            {"code": "pluto", "longitude": 240.0},
        ],
        "houses": [{"number": h, "cusp_longitude": float((h - 1) * 30)} for h in range(1, 13)],
        "angles": {
            "ASC": {"longitude": 0.0},
            "MC": {"longitude": 270.0},
        },
    }


FIXTURE_CONFIGS = [
    (
        "F01_calm_day",
        date(2026, 3, 7),
        build_base_natal(),
        "Europe/Paris",
        48.85,
        2.35,
        "2.0.0",
        "2.0.0",
    ),
    (
        "F02_moon_house_7",
        date(2026, 3, 7),
        {
            **build_base_natal(),
            "houses": [
                {"number": h, "cusp_longitude": float((h - 1) * 30 + 10)} for h in range(1, 13)
            ],
        },
        "Europe/Paris",
        48.85,
        2.35,
        "2.0.0",
        "2.0.0",
    ),
    (
        "F03_mars_square_mc",
        date(2026, 3, 7),
        {**build_base_natal(), "angles": {"ASC": {"longitude": 0.0}, "MC": {"longitude": 180.0}}},
        "Europe/Paris",
        48.85,
        2.35,
        "2.0.0",
        "2.0.0",
    ),
    (
        "F04_jupiter_trine_sun",
        date(2026, 3, 7),
        {
            **build_base_natal(),
            "planets": [
                p if p["code"] != "sun" else {"code": "sun", "longitude": 15.0 + 120.0}
                for p in build_base_natal()["planets"]
            ],
        },
        "Europe/Paris",
        48.85,
        2.35,
        "2.0.0",
        "2.0.0",
    ),
    (
        "F05_saturn_conj_asc",
        date(2026, 3, 7),
        {**build_base_natal(), "angles": {"ASC": {"longitude": 40.0}, "MC": {"longitude": 310.0}}},
        "Europe/Paris",
        48.85,
        2.35,
        "2.0.0",
        "2.0.0",
    ),
    (
        "F06_moon_sign_ingress",
        date(2026, 3, 7),
        build_base_natal(),
        "Europe/Paris",
        48.85,
        2.35,
        "2.0.0",
        "2.0.0",
    ),
    (
        "F07_mercury_retrograde",
        date(2026, 3, 7),
        build_base_natal(),
        "Europe/Paris",
        48.85,
        2.35,
        "2.0.0",
        "2.0.0",
    ),
    (
        "F08_latitude_60n",
        date(2026, 3, 7),
        build_base_natal(),
        "Europe/Paris",
        60.0,
        2.35,
        "2.0.0",
        "2.0.0",
    ),
    (
        "F09_timezone_utc_8",
        date(2026, 3, 7),
        build_base_natal(),
        "America/Los_Angeles",
        34.05,
        -118.24,
        "2.0.0",
        "2.0.0",
    ),
    (
        "F10_dst_spring",
        date(2026, 3, 29),
        build_base_natal(),
        "Europe/Paris",
        48.85,
        2.35,
        "2.0.0",
        "2.0.0",
    ),
    (
        "F11_dst_autumn",
        date(2026, 10, 25),
        build_base_natal(),
        "Europe/Paris",
        48.85,
        2.35,
        "2.0.0",
        "2.0.0",
    ),
    (
        "F12_provisional_calibration",
        date(2026, 3, 7),
        build_base_natal(),
        "Europe/Paris",
        48.85,
        2.35,
        "2.0.0",
        "2.0.0",
    ),
]


def generate():
    session = create_session()
    orchestrator = create_orchestrator(session)

    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    try:
        for name, local_date, natal, tz, lat, lon, ref_v, ruleset_v in FIXTURE_CONFIGS:
            print(f"Generating fixture: {name}...")
            engine_input = EngineInput(
                natal_chart=natal,
                local_date=local_date,
                timezone=tz,
                latitude=lat,
                longitude=lon,
                reference_version=ref_v,
                ruleset_version=ruleset_v,
                debug_mode=True,
            )

            output = orchestrator.run(engine_input)

            fixture_data = {
                "input": {
                    "natal_chart": natal,
                    "local_date": local_date.isoformat(),
                    "timezone": tz,
                    "latitude": lat,
                    "longitude": lon,
                    "reference_version": ref_v,
                    "ruleset_version": ruleset_v,
                    "debug_mode": True,
                },
                "expected": {
                    "input_hash": output.effective_context.input_hash,
                    "category_scores": output.category_scores,
                    "detected_events_count": len(output.detected_events),
                    "turning_points_count": len(output.turning_points),
                    "sample_count": len(output.sampling_timeline),
                    "is_provisional_calibration": output.run_metadata["is_provisional_calibration"],
                },
            }

            expected = fixture_data["expected"]
            if name == "F06_moon_sign_ingress":
                expected["required_event_types"] = ["moon_sign_ingress"]
            if name == "F07_mercury_retrograde":
                expected["required_event_types"] = ["aspect_exact_to_personal", "aspect_enter_orb"]
            if name == "F10_dst_spring":
                expected["sample_count"] = 92
            if name == "F11_dst_autumn":
                expected["sample_count"] = 100
            if name == "F12_provisional_calibration":
                expected["is_provisional_calibration"] = True

            assert_clamps(orchestrator, engine_input, output)

            # Add snapshots for AC6
            if name in ["F01_calm_day", "F10_dst_spring"]:
                snapshot_name = (
                    "snapshot_full_day_A" if name == "F01_calm_day" else "snapshot_full_day_B"
                )
                snapshot_file = FIXTURES_DIR / f"{snapshot_name}.json"
                print(f"  Creating snapshot: {snapshot_name}...")
                snapshot_data = {
                    "input": fixture_data["input"],
                    "expected_output": serialize_output(output),
                }
                snapshot_file.write_text(json.dumps(snapshot_data, indent=2, ensure_ascii=False))

            fixture_file = FIXTURES_DIR / f"{name}.json"
            fixture_file.write_text(json.dumps(fixture_data, indent=2, ensure_ascii=False))
    finally:
        session.close()
        session.info["engine"].dispose()


if __name__ == "__main__":
    generate()

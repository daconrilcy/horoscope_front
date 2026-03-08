from __future__ import annotations

from collections.abc import Iterator, Mapping

from app.core.config import settings


class CalibrationVersions(Mapping[str, str]):
    _KEYS = ("reference_version", "ruleset_version")

    def __getitem__(self, key: str) -> str:
        if key == "reference_version":
            return settings.active_reference_version
        if key == "ruleset_version":
            return settings.active_ruleset_version
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._KEYS)

    def __len__(self) -> int:
        return len(self._KEYS)

    def to_dict(self) -> dict[str, str]:
        return {key: self[key] for key in self}

CALIBRATION_PROFILES = [
    {
        "label": "profile_paris_aries",
        "natal_chart": {
            "planets": {
                "Sun": 15.5,
                "Moon": 220.3,
                "Mercury": 5.2,
                "Venus": 40.1,
                "Mars": 280.0,
                "Jupiter": 100.0,
                "Saturn": 310.5,
                "Uranus": 50.0,
                "Neptune": 350.0,
                "Pluto": 270.0,
            },
            "house_cusps": [102.0, 132.0, 162.0, 192.0, 222.0, 252.0, 282.0, 312.0, 342.0, 12.0, 42.0, 72.0],
        },
        "timezone": "Europe/Paris",
        "latitude": 48.85,
        "longitude": 2.35,
    },
    {
        "label": "profile_london_scorpio",
        "natal_chart": {
            "planets": {
                "Sun": 220.0,
                "Moon": 45.0,
                "Mercury": 210.0,
                "Venus": 240.0,
                "Mars": 180.0,
                "Jupiter": 30.0,
                "Saturn": 150.0,
                "Uranus": 90.0,
                "Neptune": 270.0,
                "Pluto": 200.0,
            },
            "house_cusps": [45.0, 75.0, 105.0, 135.0, 165.0, 195.0, 225.0, 255.0, 285.0, 315.0, 345.0, 15.0],
        },
        "timezone": "Europe/London",
        "latitude": 51.51,
        "longitude": -0.13,
    },
    {
        "label": "profile_new_york_cancer",
        "natal_chart": {
            "planets": {
                "Sun": 100.0,
                "Moon": 180.0,
                "Mercury": 110.0,
                "Venus": 70.0,
                "Mars": 20.0,
                "Jupiter": 280.0,
                "Saturn": 40.0,
                "Uranus": 150.0,
                "Neptune": 220.0,
                "Pluto": 190.0,
            },
            "house_cusps": [280.0, 310.0, 340.0, 10.0, 40.0, 70.0, 100.0, 130.0, 160.0, 190.0, 220.0, 250.0],
        },
        "timezone": "America/New_York",
        "latitude": 40.71,
        "longitude": -74.01,
    },
    {
        "label": "profile_tokyo_capricorn",
        "natal_chart": {
            "planets": {
                "Sun": 280.0,
                "Moon": 10.0,
                "Mercury": 270.0,
                "Venus": 310.0,
                "Mars": 50.0,
                "Jupiter": 150.0,
                "Saturn": 200.0,
                "Uranus": 20.0,
                "Neptune": 90.0,
                "Pluto": 60.0,
            },
            "house_cusps": [150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0, 0.0, 30.0, 60.0, 90.0, 120.0],
        },
        "timezone": "Asia/Tokyo",
        "latitude": 35.68,
        "longitude": 139.69,
    },
    {
        "label": "profile_stockholm_aquarius",
        "natal_chart": {
            "planets": {
                "Sun": 310.0,
                "Moon": 120.0,
                "Mercury": 320.0,
                "Venus": 280.0,
                "Mars": 150.0,
                "Jupiter": 20.0,
                "Saturn": 70.0,
                "Uranus": 250.0,
                "Neptune": 180.0,
                "Pluto": 150.0,
            },
            "house_cusps": [180.0, 210.0, 240.0, 270.0, 300.0, 330.0, 0.0, 30.0, 60.0, 90.0, 120.0, 150.0],
        },
        "timezone": "Europe/Stockholm",
        "latitude": 59.33,  # latitude > 55°N
        "longitude": 18.07,
    },
]

CALIBRATION_DATE_RANGE = {"start": "2024-01-01", "end": "2024-12-31"}

CALIBRATION_VERSIONS = CalibrationVersions()

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
            "houses": {
                "1": 102.0,
                "2": 132.0,
                "3": 162.0,
                "4": 192.0,
                "5": 222.0,
                "6": 252.0,
                "7": 282.0,
                "8": 312.0,
                "9": 342.0,
                "10": 12.0,
                "11": 42.0,
                "12": 72.0,
            },
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
            "houses": {
                "1": 45.0,
                "2": 75.0,
                "3": 105.0,
                "4": 135.0,
                "5": 165.0,
                "6": 195.0,
                "7": 225.0,
                "8": 255.0,
                "9": 285.0,
                "10": 315.0,
                "11": 345.0,
                "12": 15.0,
            },
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
            "houses": {
                "1": 280.0,
                "2": 310.0,
                "3": 340.0,
                "4": 10.0,
                "5": 40.0,
                "6": 70.0,
                "7": 100.0,
                "8": 130.0,
                "9": 160.0,
                "10": 190.0,
                "11": 220.0,
                "12": 250.0,
            },
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
            "houses": {
                "1": 150.0,
                "2": 180.0,
                "3": 210.0,
                "4": 240.0,
                "5": 270.0,
                "6": 300.0,
                "7": 330.0,
                "8": 0.0,
                "9": 30.0,
                "10": 60.0,
                "11": 90.0,
                "12": 120.0,
            },
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
            "houses": {
                "1": 180.0,
                "2": 210.0,
                "3": 240.0,
                "4": 270.0,
                "5": 300.0,
                "6": 330.0,
                "7": 0.0,
                "8": 30.0,
                "9": 60.0,
                "10": 90.0,
                "11": 120.0,
                "12": 150.0,
            },
        },
        "timezone": "Europe/Stockholm",
        "latitude": 59.33,  # latitude > 55°N
        "longitude": 18.07,
    },
]

CALIBRATION_DATE_RANGE = {"start": "2024-01-01", "end": "2024-12-31"}

CALIBRATION_VERSIONS = CalibrationVersions()

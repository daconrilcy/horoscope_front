import sys
from datetime import date

from app.jobs.calibration.natal_profiles import (
    CALIBRATION_DATE_RANGE,
    CALIBRATION_PROFILES,
    CALIBRATION_VERSIONS,
)

REQUIRED_KEYS = {"label", "natal_chart", "timezone", "latitude", "longitude"}


def validate() -> bool:
    errors: list[str] = []

    if len(CALIBRATION_PROFILES) < 5:
        errors.append(f"Moins de 5 profils ({len(CALIBRATION_PROFILES)} trouvés)")

    labels = [profile.get("label", "?") for profile in CALIBRATION_PROFILES]
    if len(labels) != len(set(labels)):
        errors.append("Labels de profils non uniques")

    for profile in CALIBRATION_PROFILES:
        missing = REQUIRED_KEYS - profile.keys()
        if missing:
            errors.append(
                f"Profil {profile.get('label', '?')}: clés manquantes {sorted(missing)}"
            )

    timezones = {
        profile["timezone"]
        for profile in CALIBRATION_PROFILES
        if "timezone" in profile and profile["timezone"]
    }
    if len(timezones) < 2:
        errors.append("Diversité de fuseaux insuffisante (< 2 valeurs distinctes)")

    start_raw = CALIBRATION_DATE_RANGE.get("start")
    end_raw = CALIBRATION_DATE_RANGE.get("end")
    start: date | None = None
    end: date | None = None

    if not start_raw or not end_raw:
        errors.append("Plage temporelle incomplète: start/end requis")
    else:
        try:
            start = date.fromisoformat(start_raw)
            end = date.fromisoformat(end_raw)
        except ValueError as exc:
            errors.append(f"Plage temporelle invalide: {exc}")
        else:
            if end < start:
                errors.append("Plage temporelle invalide: end avant start")
            elif (end - start).days < 365:
                errors.append("Plage temporelle < 365 jours")

    versions = dict(CALIBRATION_VERSIONS)
    missing_versions = [key for key, value in versions.items() if not value]
    if missing_versions:
        errors.append(f"Versions manquantes: {', '.join(missing_versions)}")

    if errors:
        for error in errors:
            print(f"[ERREUR] {error}")
        return False

    assert start is not None
    assert end is not None
    print(
        f"[OK] Dataset valide — {len(CALIBRATION_PROFILES)} profils, "
        f"{(end - start).days + 1} jours, "
        f"versions {versions}"
    )
    return True


if __name__ == "__main__":
    sys.exit(0 if validate() else 1)

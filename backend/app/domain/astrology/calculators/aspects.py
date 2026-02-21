from itertools import combinations


def _angular_distance(angle_a: float, angle_b: float) -> float:
    diff = abs(angle_a - angle_b) % 360.0
    return min(diff, 360.0 - diff)


def calculate_major_aspects(
    positions: list[dict[str, object]],
    aspect_definitions: list[tuple[str, float]],
    max_orb: float = 6.0,
) -> list[dict[str, object]]:
    aspects: list[dict[str, object]] = []
    for left, right in combinations(positions, 2):
        left_longitude = float(left["longitude"])
        right_longitude = float(right["longitude"])
        distance = _angular_distance(left_longitude, right_longitude)
        for aspect_code, angle in aspect_definitions:
            orb = abs(distance - angle)
            if orb <= max_orb:
                aspects.append(
                    {
                        "aspect_code": aspect_code,
                        "planet_a": str(left["planet_code"]),
                        "planet_b": str(right["planet_code"]),
                        "angle": round(angle, 6),
                        "orb": round(orb, 6),
                    }
                )
    aspects.sort(
        key=lambda item: (
            str(item["aspect_code"]),
            str(item["planet_a"]),
            str(item["planet_b"]),
        )
    )
    return aspects

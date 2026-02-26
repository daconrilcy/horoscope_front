def normalize_360(angle: float) -> float:
    normalized = angle % 360.0
    return normalized if normalized >= 0 else normalized + 360.0


def contains_angle(longitude: float, start: float, end: float) -> bool:
    """Semi-open interval [start, end) with 360->0 wrap support."""
    longitude = normalize_360(longitude)
    start = normalize_360(start)
    end = normalize_360(end)
    if start <= end:
        return start <= longitude < end
    return longitude >= start or longitude < end

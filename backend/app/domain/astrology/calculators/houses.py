from app.domain.astrology.angle_utils import contains_angle

HOUSE_SYSTEM_CODE = "equal"


def assign_house_number(longitude: float, houses: list[dict[str, object]]) -> int:
    if not houses:
        return 1
    ordered = sorted(houses, key=lambda item: int(item["number"]))
    for index, house in enumerate(ordered):
        start = float(house["cusp_longitude"])
        end = float(ordered[(index + 1) % len(ordered)]["cusp_longitude"])
        if contains_angle(longitude, start, end):
            return int(house["number"])
    return int(ordered[0]["number"])


def calculate_houses(julian_day: float, house_numbers: list[int]) -> list[dict[str, object]]:
    ascendant_longitude = (julian_day * 0.5) % 360.0
    houses: list[dict[str, object]] = []
    ordered_numbers = sorted(house_numbers)
    for number in ordered_numbers:
        cusp_longitude = round((ascendant_longitude + (number - 1) * 30.0) % 360.0, 6)
        houses.append({"number": number, "cusp_longitude": cusp_longitude})
    return houses

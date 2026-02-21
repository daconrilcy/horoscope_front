def calculate_houses(julian_day: float, house_numbers: list[int]) -> list[dict[str, object]]:
    ascendant_longitude = (julian_day * 0.5) % 360.0
    houses: list[dict[str, object]] = []
    ordered_numbers = sorted(house_numbers)
    for number in ordered_numbers:
        cusp_longitude = round((ascendant_longitude + (number - 1) * 30.0) % 360.0, 6)
        houses.append({"number": number, "cusp_longitude": cusp_longitude})
    return houses

def calculate_planet_positions(
    julian_day: float,
    planet_codes: list[str],
    sign_codes: list[str],
) -> list[dict[str, object]]:
    positions: list[dict[str, object]] = []
    for index, code in enumerate(planet_codes):
        longitude = round((julian_day * 0.985647 + index * 37.5) % 360.0, 6)
        sign_index = int(longitude // 30)
        sign_code = sign_codes[sign_index % len(sign_codes)] if sign_codes else "unknown"
        house_number = int(((longitude + 15.0) // 30) % 12) + 1
        positions.append(
            {
                "planet_code": code,
                "longitude": longitude,
                "sign_code": sign_code,
                "house_number": house_number,
            }
        )

    return positions

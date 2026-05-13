"""Axes astrologiques canoniques reliant les maisons opposées."""

HOUSE_AXES = {
    1: {"opposite_house": 7, "theme": "self_relationship"},
    2: {"opposite_house": 8, "theme": "resources_sharing"},
    3: {"opposite_house": 9, "theme": "local_distant"},
    4: {"opposite_house": 10, "theme": "private_public"},
    5: {"opposite_house": 11, "theme": "creation_collective"},
    6: {"opposite_house": 12, "theme": "control_surrender"},
}


def resolve_house_axis(house_number: int) -> dict[str, int | str]:
    """Retourne l'axe miroir canonique d'une maison."""
    if house_number in HOUSE_AXES:
        return dict(HOUSE_AXES[house_number])

    opposite_house = house_number - 6
    source_axis = HOUSE_AXES[opposite_house]
    return {
        "opposite_house": opposite_house,
        "theme": source_axis["theme"],
    }

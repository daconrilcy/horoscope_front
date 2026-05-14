"""Teste le seed des profils éditoriaux d'interprétation des aspects."""

import pytest

from app.services.reference_data.aspect_interpretation_seed_service import (
    _validate_unique_profile_keys,
)


def test_aspect_interpretation_source_rejects_duplicate_unique_key() -> None:
    """Le JSON source échoue avant SQL si deux profils ciblent la même clé métier."""
    duplicate_row = {
        "reference_version_id": 1,
        "aspect_code": "conjunction",
        "astral_system_code": "modern",
        "language": "en",
    }

    with pytest.raises(ValueError, match="duplicate aspect interpretation profile key"):
        _validate_unique_profile_keys([duplicate_row, dict(duplicate_row)])


def test_aspect_interpretation_source_rejects_incomplete_unique_key() -> None:
    """Le JSON source échoue si une colonne de clé unique manque."""
    with pytest.raises(ValueError, match="incomplete unique key"):
        _validate_unique_profile_keys(
            [
                {
                    "reference_version_id": 1,
                    "aspect_code": "conjunction",
                    "astral_system_code": "modern",
                }
            ]
        )

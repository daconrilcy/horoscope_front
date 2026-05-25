# Tests du hash canonique des projections persistables.
"""Verifie la stabilite et la divergence du hash de projection."""

from __future__ import annotations

from app.domain.astrology.projections.projection_hash import compute_projection_hash


def test_equal_canonical_payloads_keep_stable_hash() -> None:
    """Deux payloads equivalents avec ordre different gardent le meme hash."""
    left = {"b": [2, 1], "a": {"z": "last", "m": "middle"}}
    right = {"a": {"m": "middle", "z": "last"}, "b": [2, 1]}

    assert compute_projection_hash(left) == compute_projection_hash(right)


def test_meaningful_payload_change_changes_hash() -> None:
    """Un changement factuel du payload modifie le hash."""
    baseline = {"facts": {"sun": "aries"}, "version": "v1"}
    changed = {"facts": {"sun": "taurus"}, "version": "v1"}

    assert compute_projection_hash(baseline) != compute_projection_hash(changed)

"""Temporal influence kernel: spreads an event's contribution across adjacent time steps.

Instead of assigning an event's full contribution to a single 15-minute bucket,
each event is spread over a rising → peak → falling window.  Weights are
normalised to sum to 1.0 so day-level totals are conserved (energy-preserving).

Profile shape: triangular decay around the central (nearest) step.

    weight(d) = max(0, 1 - d / (half_width + 1))

where d = distance in steps from center, half_width = number of steps on each side.

Example — half_width=2:
    d=0  → 1.0   (peak)
    d=1  → 0.67
    d=2  → 0.33
    d≥3  → 0.0
After normalisation these become:  0.5, 0.33, 0.17  (×2 for sides + center).
"""

from __future__ import annotations

from app.prediction.schemas import AstroEvent, SamplePoint

# Taxonomy V2 event families → half-width in 15-min steps.
# Wider windows = more spreading = smoother intraday signal.
_FAMILY_HALF_WIDTH: dict[str, int] = {
    # Exact aspects — strongest structuring events
    "aspect_exact_to_angle": 4,       # ±60 min
    "aspect_exact_to_luminary": 3,    # ±45 min
    "aspect_exact_to_personal": 2,    # ±30 min
    # Orb crossings — secondary structural events
    "aspect_enter_orb": 2,            # ±30 min
    "aspect_exit_orb": 1,             # ±15 min
    # Ingresses — notable but briefer
    "moon_sign_ingress": 2,           # ±30 min
    "asc_sign_change": 3,             # ±45 min
    # Timing — narrow, rhythmic pulse
    "planetary_hour_change": 1,       # ±15 min
}

_DEFAULT_HALF_WIDTH = 1  # fallback for any unknown event type


def spread_event_weights(
    event: AstroEvent,
    samples: list[SamplePoint],
) -> list[tuple[int, float]]:
    """Return normalised (step_index, weight) pairs for temporal spreading.

    Weights sum to exactly 1.0 so that summing spread contributions across
    steps yields the same day total as concentrating them at a single step.

    Args:
        event:   The detected astrological event to spread.
        samples: Ordered list of day-grid sample points.

    Returns:
        List of (step_index, normalised_weight) tuples covering the influence
        window.  The list always contains at least one entry.
    """
    if not samples:
        return []

    center_index = min(
        range(len(samples)),
        key=lambda i: abs(samples[i].ut_time - event.ut_time),
    )

    half_width = _FAMILY_HALF_WIDTH.get(event.event_type, _DEFAULT_HALF_WIDTH)

    raw: list[tuple[int, float]] = []
    lo = max(0, center_index - half_width)
    hi = min(len(samples) - 1, center_index + half_width)
    for i in range(lo, hi + 1):
        distance = abs(i - center_index)
        w = 1.0 - distance / (half_width + 1)
        if w > 0.0:
            raw.append((i, w))

    if not raw:
        return [(center_index, 1.0)]

    total = sum(w for _, w in raw)
    return [(i, w / total) for i, w in raw]

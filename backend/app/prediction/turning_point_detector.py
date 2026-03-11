from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.prediction.schemas import AstroEvent, V3TimeBlock, V3TurningPoint


@dataclass
class TurningPoint:
    local_time: datetime
    reason: str  # "delta_note" | "top3_change" | "high_priority_event"
    categories_impacted: list[str]
    trigger_event: AstroEvent | None
    severity: float
    summary: str = field(default="")
    driver_events: list[Any] = field(default_factory=list)  # Added for explainability (AC3)


class TurningPointDetector:
    PRIORITY_PIVOT_THRESHOLD = 65
    # AC2: raise threshold so minor/technical changes don't become user pivots
    DELTA_NOTE_THRESHOLD = 3
    NON_DECISION_EVENT_TYPES = frozenset({"asc_sign_change"})

    # V3 Thresholds (AC1)
    MIN_V3_AMPLITUDE = 3.0
    MIN_V3_REGIME_AMPLITUDE = 1.5  # Solid threshold for orientation changes
    MIN_V3_DURATION_FOLLOWING = 60  # minutes
    MIN_V3_CONFIDENCE = 0.5

    REASON_PRIORITY = {
        "high_priority_event": 3,
        "delta_note": 2,
        "top3_change": 1,
    }

    REASON_SEVERITY = {
        "high_priority_event": 1.0,
        "delta_note": 0.8,
        "top3_change": 0.6,
    }

    def detect(
        self,
        notes_by_step: list[dict[str, int]],
        events_by_step: list[list[AstroEvent]],
        step_times: list[datetime],
    ) -> list[TurningPoint]:
        pivots = []

        for index in range(1, len(step_times)):
            reasons_found: dict[str, tuple[list[str], AstroEvent | None]] = {}

            # AC2: use DELTA_NOTE_THRESHOLD (3) instead of 2 to filter minor changes
            impacted_categories = []
            for category_code, note in notes_by_step[index].items():
                prev_note = notes_by_step[index - 1].get(category_code, note)
                if abs(note - prev_note) >= self.DELTA_NOTE_THRESHOLD:
                    impacted_categories.append(category_code)

            if impacted_categories:
                reasons_found["delta_note"] = (impacted_categories, None)

            top3_current = self._top3_codes(notes_by_step[index])
            top3_previous = self._top3_codes(notes_by_step[index - 1])
            # AC2: top3_change only fires when the underlying shift is significant
            # (max delta >= threshold), preventing rounding-artifact pivots
            if top3_current != top3_previous:
                all_codes = set(notes_by_step[index]) | set(notes_by_step[index - 1])
                max_delta = max(
                    abs(notes_by_step[index].get(code, 0) - notes_by_step[index - 1].get(code, 0))
                    for code in all_codes
                )
                if max_delta >= self.DELTA_NOTE_THRESHOLD:
                    reasons_found["top3_change"] = (
                        list(top3_current.symmetric_difference(top3_previous)),
                        None,
                    )

            high_priority_events = [
                event
                for event in events_by_step[index]
                if event.priority >= self.PRIORITY_PIVOT_THRESHOLD
                and event.event_type not in self.NON_DECISION_EVENT_TYPES
            ]
            if high_priority_events:
                reasons_found["high_priority_event"] = (
                    [],
                    max(high_priority_events, key=lambda event: event.priority),
                )

            if not reasons_found:
                continue

            best_reason = max(reasons_found, key=lambda reason: self.REASON_PRIORITY[reason])
            all_impacted = set()
            for categories, _ in reasons_found.values():
                all_impacted.update(categories)

            if best_reason == "high_priority_event":
                driver_events = list(high_priority_events)
            else:
                driver_events = list(events_by_step[index])

            pivots.append(
                TurningPoint(
                    local_time=step_times[index],
                    reason=best_reason,
                    categories_impacted=sorted(all_impacted),
                    trigger_event=reasons_found[best_reason][1],
                    severity=self.REASON_SEVERITY[best_reason],
                    driver_events=driver_events,
                )
            )

        return pivots

    def detect_v3(
        self,
        time_blocks: list[V3TimeBlock],
        detected_events: list[AstroEvent],
    ) -> list[V3TurningPoint]:
        """Detect turning points as persistent regime changes (Story 42.10)."""
        pivots = []
        if not time_blocks:
            return pivots

        for i in range(1, len(time_blocks)):
            prev = time_blocks[i - 1]
            curr = time_blocks[i]

            # Trigger logic: orientation change OR significant intensity jump
            regime_changed = prev.orientation != curr.orientation
            intensity_diff = abs(curr.intensity - prev.intensity)

            reason = None
            if regime_changed and intensity_diff >= self.MIN_V3_REGIME_AMPLITUDE:
                reason = "regime_change"
            elif intensity_diff >= self.MIN_V3_AMPLITUDE:
                reason = "intensity_jump"

            if not reason:
                continue

            # AC1 requirements: duration, confidence
            duration_following = (curr.end_local - curr.start_local).total_seconds() / 60
            if duration_following < self.MIN_V3_DURATION_FOLLOWING:
                continue

            confidence = min(prev.confidence, curr.confidence)
            if confidence < self.MIN_V3_CONFIDENCE:
                continue

            # Attach strongest AstroEvents near the transition as drivers (AC4)
            drivers = [
                e
                for e in detected_events
                if abs((e.local_time - curr.start_local).total_seconds()) <= 60 * 60  # 1h window
            ]
            # Prioritize priority then intensity of contribution if possible
            drivers = sorted(drivers, key=lambda e: e.priority, reverse=True)[:5]

            pivots.append(
                V3TurningPoint(
                    local_time=curr.start_local,
                    reason=reason,
                    amplitude=intensity_diff,
                    duration_following=duration_following,
                    confidence=confidence,
                    categories_impacted=curr.dominant_themes,
                    drivers=drivers,
                )
            )

        return pivots

    def _top3_codes(self, notes: dict[str, int]) -> frozenset[str]:
        sorted_cats = sorted(notes.items(), key=lambda item: (-item[1], item[0]))
        return frozenset(code for code, _ in sorted_cats[:3])

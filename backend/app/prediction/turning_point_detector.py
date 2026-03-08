from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.prediction.schemas import AstroEvent


@dataclass
class TurningPoint:
    local_time: datetime
    reason: str  # "delta_note" | "top3_change" | "high_priority_event"
    categories_impacted: list[str]
    trigger_event: AstroEvent | None
    severity: float
    driver_events: list[Any] = field(default_factory=list)  # Added for explainability (AC3)


class TurningPointDetector:
    PRIORITY_PIVOT_THRESHOLD = 65

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

            impacted_categories = []
            for category_code, note in notes_by_step[index].items():
                prev_note = notes_by_step[index - 1].get(category_code, note)
                if abs(note - prev_note) >= 2:
                    impacted_categories.append(category_code)

            if impacted_categories:
                reasons_found["delta_note"] = (impacted_categories, None)

            top3_current = self._top3_codes(notes_by_step[index])
            top3_previous = self._top3_codes(notes_by_step[index - 1])
            if top3_current != top3_previous:
                reasons_found["top3_change"] = (
                    list(top3_current.symmetric_difference(top3_previous)),
                    None,
                )

            high_priority_events = [
                event
                for event in events_by_step[index]
                if event.priority >= self.PRIORITY_PIVOT_THRESHOLD
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

    def _top3_codes(self, notes: dict[str, int]) -> frozenset[str]:
        sorted_cats = sorted(notes.items(), key=lambda item: (-item[1], item[0]))
        return frozenset(code for code, _ in sorted_cats[:3])

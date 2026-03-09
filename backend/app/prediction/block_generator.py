from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.prediction.schemas import AstroEvent
    from app.prediction.turning_point_detector import TurningPoint


@dataclass
class TimeBlock:
    block_index: int
    start_local: datetime
    end_local: datetime
    dominant_categories: list[str] = field(default_factory=list)
    tone_code: str = "neutral"
    driver_events: list[AstroEvent] = field(default_factory=list)
    summary: str = field(default="")


class BlockGenerator:
    def generate(
        self,
        pivots: list[TurningPoint],
        notes_by_step: list[dict[str, int]],
        events_by_step: list[list[AstroEvent]],
        step_times: list[datetime],
        contributions_by_step: list[list[tuple["AstroEvent", dict[str, float]]]],
    ) -> list[TimeBlock]:
        if not step_times:
            return []

        # AC1: signal-driven boundaries -- no fixed hourly grid
        # Day start and day end are the only mandatory boundaries.
        # Pivot times (real signal changes) define block splits.
        boundaries = {step_times[0], step_times[-1] + timedelta(minutes=15)}

        for pivot in pivots:
            boundaries.add(pivot.local_time)

        pivot_times = {pivot.local_time for pivot in pivots}
        sorted_boundaries = sorted(boundaries)
        blocks = []
        for index in range(len(sorted_boundaries) - 1):
            start = sorted_boundaries[index]
            end = sorted_boundaries[index + 1]
            step_indices = [
                step_index
                for step_index, step_time in enumerate(step_times)
                if start <= step_time < end
            ]
            if not step_indices:
                continue

            notes_slice = [notes_by_step[step_index] for step_index in step_indices]
            block_contribs: list[tuple[AstroEvent, dict[str, float]]] = []
            for step_index in step_indices:
                block_contribs.extend(contributions_by_step[step_index])

            dominant_categories = self._dominant_categories(notes_slice)
            tone_code = self._tone_code(notes_slice, dominant_categories)
            driver_events = self._driver_events(block_contribs)
            blocks.append(
                TimeBlock(
                    block_index=0,
                    start_local=start,
                    end_local=end,
                    dominant_categories=dominant_categories,
                    tone_code=tone_code,
                    driver_events=driver_events,
                )
            )

        for index, block in enumerate(blocks):
            block.block_index = index

        # AC2: budget of noise — merge identical consecutive blocks
        if not blocks:
            return []

        merged_blocks = [blocks[0]]
        for i in range(1, len(blocks)):
            last = merged_blocks[-1]
            curr = blocks[i]
            if (
                curr.start_local not in pivot_times
                and last.tone_code == curr.tone_code
                and last.dominant_categories == curr.dominant_categories
            ):
                # Merge curr into last
                last.end_local = curr.end_local
                last.driver_events.extend(curr.driver_events)
                # Keep only top 3 unique driver events
                unique_drivers = []
                seen_signatures = set()
                for event in last.driver_events:
                    sig = (event.event_type, event.ut_time, event.body, event.target, event.aspect)
                    if sig not in seen_signatures:
                        unique_drivers.append(event)
                        seen_signatures.add(sig)
                last.driver_events = unique_drivers[:3]
            else:
                merged_blocks.append(curr)

        for index, block in enumerate(merged_blocks):
            block.block_index = index

        return merged_blocks

    def _dominant_categories(self, notes_slice: list[dict[str, int]]) -> list[str]:
        if not notes_slice:
            return []

        sums: dict[str, int] = {}
        counts: dict[str, int] = {}
        for step_notes in notes_slice:
            for category_code, score in step_notes.items():
                sums[category_code] = sums.get(category_code, 0) + score
                counts[category_code] = counts.get(category_code, 0) + 1

        means = {
            category_code: sums[category_code] / counts[category_code] for category_code in sums
        }
        sorted_cats = sorted(means.items(), key=lambda item: (-item[1], item[0]))
        return [category_code for category_code, _ in sorted_cats[:3]]

    def _tone_code(self, notes_slice: list[dict[str, int]], dominant_cats: list[str]) -> str:
        if not notes_slice or not dominant_cats:
            return "neutral"

        top3_means = []
        for category_code in dominant_cats:
            cat_sum = sum(step.get(category_code, 0) for step in notes_slice)
            top3_means.append(cat_sum / len(notes_slice))

        avg_top3 = sum(top3_means) / len(top3_means)
        spread = max(top3_means) - min(top3_means)

        if avg_top3 >= 13:
            return "positive"
        if avg_top3 <= 7:
            return "negative"
        if spread >= 5:
            return "mixed"
        return "neutral"

    def _driver_events(
        self,
        block_contribs: list[tuple["AstroEvent", dict[str, float]]],
    ) -> list["AstroEvent"]:
        if not block_contribs:
            return []

        impacts_by_signature: dict[tuple, dict[str, object]] = {}
        for event, contrib_dict in block_contribs:
            signature = (
                event.event_type,
                event.ut_time,
                event.body,
                event.target,
                event.aspect,
            )
            if signature not in impacts_by_signature:
                impacts_by_signature[signature] = {"event": event, "impacts": []}
            impacts_by_signature[signature]["impacts"].append(
                sum(abs(value) for value in contrib_dict.values())
            )

        event_means = [
            (entry["event"], sum(entry["impacts"]) / len(entry["impacts"]))
            for entry in impacts_by_signature.values()
        ]
        sorted_events = sorted(event_means, key=lambda item: -item[1])
        return [event for event, _ in sorted_events[:3]]

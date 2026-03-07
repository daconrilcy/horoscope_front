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

class BlockGenerator:
    def generate(
        self,
        pivots: list[TurningPoint],
        notes_by_step: list[dict[str, int]],
        events_by_step: list[list[AstroEvent]],
        step_times: list[datetime],
        contributions_by_step: list[list[tuple["AstroEvent", dict[str, float]]]]
    ) -> list[TimeBlock]:
        # 1. Collect all boundary times
        # Start with standard boundaries every 4 steps
        boundaries = set()
        n = len(step_times)
        for i in range(0, n, 4):
            boundaries.add(step_times[i])
        # End boundary (15 min after last step)
        if step_times:
            boundaries.add(step_times[-1] + timedelta(minutes=15))

        # Add pivots as boundaries
        for p in pivots:
            boundaries.add(p.local_time)

        sorted_boundaries = sorted(list(boundaries))
        
        blocks = []
        for i in range(len(sorted_boundaries) - 1):
            start = sorted_boundaries[i]
            end = sorted_boundaries[i+1]
            
            # Find steps belonging to this block
            # A step t belongs to [start, end)
            step_indices = [idx for idx, t_val in enumerate(step_times) if start <= t_val < end]
            
            if not step_indices:
                continue
                
            # Slice data for these steps
            notes_slice = [notes_by_step[idx] for idx in step_indices]
            events_slice = []
            for idx in step_indices:
                events_slice.extend(events_by_step[idx])
            
            # Contributions: collect all (event, contrib_dict) pairs for this block (AC9)
            block_contribs: list[tuple[AstroEvent, dict[str, float]]] = []
            for idx in step_indices:
                block_contribs.extend(contributions_by_step[idx])

            dominant_cats = self._dominant_categories(notes_slice)
            tone = self._tone_code(notes_slice, dominant_cats)
            drivers = self._driver_events(block_contribs)

            blocks.append(TimeBlock(
                block_index=0,  # re-indexed below
                start_local=start,
                end_local=end,
                dominant_categories=dominant_cats,
                tone_code=tone,
                driver_events=drivers
            ))
            
        # Re-index to ensure sequentiality from 0
        for i, b in enumerate(blocks):
            b.block_index = i
            
        return blocks

    def _dominant_categories(self, notes_slice: list[dict[str, int]]) -> list[str]:
        if not notes_slice:
            return []
        # Calculate mean score for each category across the slice
        sums = {}
        counts = {}
        for step_notes in notes_slice:
            for cat, score in step_notes.items():
                sums[cat] = sums.get(cat, 0) + score
                counts[cat] = counts.get(cat, 0) + 1
        
        means = {cat: sums[cat] / counts[cat] for cat in sums}
        # Top 3
        sorted_cats = sorted(means.items(), key=lambda x: (-x[1], x[0]))
        return [c for c, _ in sorted_cats[:3]]

    def _tone_code(self, notes_slice: list[dict[str, int]], dominant_cats: list[str]) -> str:
        if not notes_slice or not dominant_cats:
            return "neutral"
            
        # "positive" si note moyenne top 3 du bloc >= 13
        # "negative" si <= 7
        # "mixed" si écart entre meilleure et pire note top 3 >= 5
        # "neutral" sinon
        
        # Calculate mean of top 3 categories across the whole slice
        top3_means = []
        for cat in dominant_cats:
            cat_sum = sum(step.get(cat, 0) for step in notes_slice)
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
        """Return top 3 AstroEvents by mean abs(contribution) across block steps (AC9)."""
        if not block_contribs:
            return []

        # AstroEvent contains a dict field (metadata) so it's not hashable — group by id()
        event_by_id: dict[int, "AstroEvent"] = {}
        impacts_by_id: dict[int, list[float]] = {}
        for event, contrib_dict in block_contribs:
            total_abs = sum(abs(v) for v in contrib_dict.values())
            key = id(event)
            if key not in impacts_by_id:
                event_by_id[key] = event
                impacts_by_id[key] = []
            impacts_by_id[key].append(total_abs)

        event_means = [
            (event_by_id[k], sum(impacts) / len(impacts))
            for k, impacts in impacts_by_id.items()
        ]
        sorted_events = sorted(event_means, key=lambda x: -x[1])
        return [e for e, _ in sorted_events[:3]]

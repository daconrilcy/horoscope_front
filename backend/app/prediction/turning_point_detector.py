from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.prediction.schemas import AstroEvent

@dataclass
class TurningPoint:
    local_time: datetime
    reason: str  # "delta_note" | "top3_change" | "high_priority_event"
    categories_impacted: list[str]
    trigger_event: AstroEvent | None
    severity: float

class TurningPointDetector:
    PRIORITY_PIVOT_THRESHOLD = 65
    
    # Severity mapping for tie-breaking
    REASON_PRIORITY = {
        "high_priority_event": 3,
        "delta_note": 2,
        "top3_change": 1
    }
    
    REASON_SEVERITY = {
        "high_priority_event": 1.0,
        "delta_note": 0.8,
        "top3_change": 0.6
    }

    def detect(
        self, 
        notes_by_step: list[dict[str, int]], 
        events_by_step: list[list[AstroEvent]], 
        step_times: list[datetime]
    ) -> list[TurningPoint]:
        pivots = []
        
        for t in range(1, len(step_times)):
            reasons_found = {}  # reason -> (categories, event)
            
            # Rule 1: Delta Note >= 2
            impacted_r1 = []
            for cat, note in notes_by_step[t].items():
                prev_note = notes_by_step[t-1].get(cat, note)
                if abs(note - prev_note) >= 2:
                    impacted_r1.append(cat)
            
            if impacted_r1:
                reasons_found["delta_note"] = (impacted_r1, None)
                
            # Rule 2: Top 3 change
            top3_curr = self._top3_codes(notes_by_step[t])
            top3_prev = self._top3_codes(notes_by_step[t-1])
            if top3_curr != top3_prev:
                # Difference in top 3
                diff = list(top3_curr.symmetric_difference(top3_prev))
                reasons_found["top3_change"] = (diff, None)
                
            # Rule 3: Event priority >= 65
            high_prio_events = [e for e in events_by_step[t] if e.priority >= self.PRIORITY_PIVOT_THRESHOLD]
            if high_prio_events:
                # Take the highest priority event
                best_event = max(high_prio_events, key=lambda e: e.priority)
                reasons_found["high_priority_event"] = ([], best_event)
            
            if reasons_found:
                # Determine most severe reason
                best_reason = max(reasons_found.keys(), key=lambda r: self.REASON_PRIORITY[r])
                
                # Combine categories from all rules if requested? 
                # Story says: "Mettre tous les categories_impacted dans la liste."
                all_impacted = set()
                for cats, _ in reasons_found.values():
                    all_impacted.update(cats)
                
                pivots.append(TurningPoint(
                    local_time=step_times[t],
                    reason=best_reason,
                    categories_impacted=sorted(list(all_impacted)),
                    trigger_event=reasons_found[best_reason][1],
                    severity=self.REASON_SEVERITY[best_reason]
                ))
                
        return pivots

    def _top3_codes(self, notes: dict[str, int]) -> frozenset[str]:
        # Sort by score (desc), then by key for stability
        sorted_cats = sorted(notes.items(), key=lambda x: (-x[1], x[0]))
        return frozenset(c for c, _ in sorted_cats[:3])

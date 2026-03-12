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
        theme_signals: dict[str, Any] | None = None,
    ) -> list[V3TurningPoint]:
        """Detect turning points as persistent regime changes (Story 42.10)."""
        from app.prediction.schemas import V3PrimaryDriver

        pivots = []
        if not time_blocks:
            return pivots

        for i in range(1, len(time_blocks)):
            prev = time_blocks[i - 1]
            curr = time_blocks[i]

            # AC4: Never publish midnight/synthetic boundaries as turning points
            # 00:00 and 24:00 (or near enough) are ignored
            if curr.start_local.hour == 0 and curr.start_local.minute == 0:
                continue
            if curr.start_local.hour == 23 and curr.start_local.minute == 59:
                continue

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

            # Story 43.1: Semantic Fields
            change_type = self._derive_change_type(prev, curr)
            primary_driver = self._select_primary_driver(drivers)

            # Story 44.2: Movement and Category Deltas
            movement = None
            category_deltas = []
            if theme_signals:
                movement = self._calculate_movement(prev, curr, theme_signals)
                category_deltas = self._calculate_category_deltas(prev, curr, theme_signals)

            pivots.append(
                V3TurningPoint(
                    local_time=curr.start_local,
                    reason=reason,
                    amplitude=intensity_diff,
                    duration_following=duration_following,
                    confidence=confidence,
                    categories_impacted=curr.dominant_themes,
                    drivers=drivers,
                    change_type=change_type,
                    previous_categories=list(prev.dominant_themes),
                    next_categories=list(curr.dominant_themes),
                    primary_driver=primary_driver,
                    movement=movement,
                    category_deltas=category_deltas,
                )
            )

        return pivots

    def _calculate_movement(
        self, prev: V3TimeBlock, curr: V3TimeBlock, theme_signals: dict[str, Any]
    ) -> Any | None:
        from app.prediction.schemas import V3Movement

        # Use the sample point exactly at the transition if available, or just before/after
        # For simplicity, we can use the intensity from the blocks themselves as a proxy
        # for previous/next composite if we assume they represent the average or boundary
        # But AC1 says "à partir de l'état juste avant et juste après la bascule".
        
        # Let's find the total composite signal across all themes at prev.end_local and curr.start_local
        # (they are the same point in time for adjacent blocks).
        # Wait, we need the state "just before" and "just after".
        # Let's use the time block boundary as the pivot and compare 15min before vs 15min after.
        
        pivot_time = curr.start_local
        
        def get_total_composite(t: datetime) -> float:
            total = 0.0
            for signal in theme_signals.values():
                # Finding nearest point in timeline
                nearest_time = min(signal.timeline.keys(), key=lambda dt: abs(dt - t))
                total += signal.timeline[nearest_time].composite
            return total

        # Approximate "just before" and "just after" (e.g. middle of previous block and middle of current)
        # Actually, let's use the blocks' intensities if they were derived from composites.
        # But blocks' intensities are 0-20. Composite is raw.
        
        # Story 44.2 AC1: delta_composite = next - previous
        # We'll use the boundary point and look at the trend.
        
        prev_comp = get_total_composite(prev.start_local + (prev.end_local - prev.start_local) / 2)
        next_comp = get_total_composite(curr.start_local + (curr.end_local - curr.start_local) / 2)
        delta = next_comp - prev_comp
        
        # Strength is scaled amplitude (0-10)
        strength = min(10.0, abs(delta) / 2.0) # Heuristic scaling
        
        # Direction
        if delta > 0.5:
            direction = "rising"
        elif delta < -0.5:
            direction = "falling"
        else:
            direction = "recomposition"

        return V3Movement(
            strength=strength,
            previous_composite=prev_comp,
            next_composite=next_comp,
            delta_composite=delta,
            direction=direction,
        )

    def _calculate_category_deltas(
        self, prev: V3TimeBlock, curr: V3TimeBlock, theme_signals: dict[str, Any]
    ) -> list[Any]:
        from app.prediction.schemas import V3CategoryDelta

        deltas = []
        t_prev = prev.start_local + (prev.end_local - prev.start_local) / 2
        t_curr = curr.start_local + (curr.end_local - curr.start_local) / 2

        for code, signal in theme_signals.items():
            nearest_prev = min(signal.timeline.keys(), key=lambda dt: abs(dt - t_prev))
            nearest_curr = min(signal.timeline.keys(), key=lambda dt: abs(dt - t_curr))
            
            val_prev = signal.timeline[nearest_prev].composite
            val_curr = signal.timeline[nearest_curr].composite
            delta_composite = val_curr - val_prev
            
            if abs(delta_composite) < 0.2: # AC4 threshold for micro-variations
                continue
                
            direction = "stable"
            if delta_composite > 0.2:
                direction = "up"
            elif delta_composite < -0.2:
                direction = "down"
                
            deltas.append(
                V3CategoryDelta(
                    code=code,
                    direction=direction,
                    delta_score=delta_composite * 2.0, # Scaled to match score-like range
                    delta_intensity=abs(delta_composite),
                    delta_rank=None, # Rank change requires more complex logic
                )
            )

        # AC2: Sort by absolute amplitude and limit to 3
        deltas.sort(key=lambda d: abs(d.delta_intensity), reverse=True)
        return deltas[:3]

    def _derive_change_type(self, prev: V3TimeBlock, curr: V3TimeBlock) -> str:
        intensity_jump = curr.intensity - prev.intensity
        
        if intensity_jump >= 2.5:
            return "emergence"
        if intensity_jump <= -2.5:
            return "attenuation"
        
        return "recomposition"

    def _select_primary_driver(self, drivers: list[AstroEvent]) -> Any:
        from app.prediction.schemas import V3PrimaryDriver
        
        if not drivers:
            return None
            
        # Priority 1: Public exact ASPECTS
        aspect_event_types = {
            "aspect_exact_to_angle",
            "aspect_exact_to_luminary",
            "aspect_exact_to_personal",
        }
        for d in drivers:
            if d.event_type in aspect_event_types:
                return self._to_primary_driver(d)
                
        # Priority 2: Public Ingresses (Moon)
        for d in drivers:
            if d.event_type == "moon_sign_ingress":
                return self._to_primary_driver(d)
                
        # Priority 3: Other ingresses
        for d in drivers:
            if "ingress" in d.event_type:
                return self._to_primary_driver(d)
                
        # Priority 4: Strongest event
        return self._to_primary_driver(drivers[0])

    def _to_primary_driver(self, event: AstroEvent) -> Any:
        from app.prediction.schemas import V3PrimaryDriver
        
        # Filter metadata to keep only useful bits
        metadata = {}
        for key in ["house", "sign", "orb_exact"]:
            if key in event.metadata:
                metadata[key] = event.metadata[key]
                
        return V3PrimaryDriver(
            event_type=event.event_type,
            body=event.body,
            target=event.target,
            aspect=event.aspect,
            metadata=metadata
        )

    def _top3_codes(self, notes: dict[str, int]) -> frozenset[str]:
        sorted_cats = sorted(notes.items(), key=lambda item: (-item[1], item[0]))
        return frozenset(code for code, _ in sorted_cats[:3])

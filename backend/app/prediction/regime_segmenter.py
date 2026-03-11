from __future__ import annotations

import statistics
from datetime import datetime
from typing import TYPE_CHECKING

from .schemas import V3TimeBlock

if TYPE_CHECKING:
    from .schemas import V3ThemeSignal


class RegimeSegmenter:
    """
    Segments a day into coherent regimes based on V3 signals (Story 42.9).
    
    Instead of a fixed grid, it identifies turning points and stability shifts
    in the continuous signal to produce 4 to 8 readable blocks.
    """

    MIN_SEGMENT_MINUTES = 120  # Aim for at least 2 hours per block
    MAX_SEGMENTS = 8
    MIN_SEGMENTS = 4

    def segment(self, theme_signals: dict[str, V3ThemeSignal]) -> list[V3TimeBlock]:
        if not theme_signals:
            return []

        # 1. Get a unified signal (average of all composite signals)
        # We focus on themes that are active (non-constant baseline)
        active_signals = [
            s.timeline for s in theme_signals.values()
            if any(abs(layer.composite - layer.baseline) > 0.01 for layer in s.timeline.values())
        ]
        if not active_signals:
            # Fallback to all if none are "active" enough
            active_signals = [s.timeline for s in theme_signals.values()]

        if not active_signals:
            return []

        sorted_times = sorted(active_signals[0].keys())
        global_signal = []
        for t in sorted_times:
            vals = [tl[t].composite for tl in active_signals if t in tl]
            global_signal.append(statistics.mean(vals) if vals else 1.0)

        quiet_day = self._is_quiet_day(global_signal)

        # 2. Smooth the signal to remove micro-oscillations
        smoothed = self._smooth(global_signal, window=7)

        # 3. Detect change points
        change_indices = self._detect_change_points(smoothed, sorted_times)
        
        # 4. Merge until we have a reasonable amount of segments
        merged_indices = self._merge_segments(change_indices, smoothed, sorted_times, quiet_day)

        # 5. Create V3TimeBlock objects
        blocks = []
        for i in range(len(merged_indices) - 1):
            start_idx = merged_indices[i]
            end_idx = merged_indices[i + 1]

            start_time = sorted_times[start_idx]
            end_time = sorted_times[end_idx]

            block_signal_smoothed = smoothed[start_idx : end_idx + 1]
            block_signal_raw = global_signal[start_idx : end_idx + 1]

            orientation = self._detect_orientation(block_signal_raw, block_signal_smoothed)
            intensity = self._calculate_intensity(block_signal_smoothed)
            confidence = self._calculate_confidence(block_signal_raw, block_signal_smoothed)

            blocks.append(
                V3TimeBlock(
                    block_index=i,
                    start_local=start_time,
                    end_local=end_time,
                    orientation=orientation,
                    intensity=intensity,
                    confidence=confidence,
                    dominant_themes=self._get_dominant_themes(theme_signals, start_time, end_time),
                )
            )

        return blocks

    def _smooth(self, values: list[float], window: int = 5) -> list[float]:
        if len(values) < window:
            return values
        radius = window // 2
        smoothed = []
        for i in range(len(values)):
            start = max(0, i - radius)
            end = min(len(values), i + radius + 1)
            smoothed.append(statistics.mean(values[start:end]))
        return smoothed

    def _detect_change_points(self, smoothed: list[float], times: list[datetime]) -> list[int]:
        """Detects indices where the signal behavior changes significantly."""
        if len(smoothed) < 2:
            return [0, len(smoothed) - 1] if smoothed else []

        indices = [0]
        derivatives = [smoothed[i + 1] - smoothed[i] for i in range(len(smoothed) - 1)]

        for i in range(1, len(derivatives)):
            # Sign change in derivative (Local extremum)
            if (derivatives[i] > 0 and derivatives[i - 1] < 0) or (
                derivatives[i] < 0 and derivatives[i - 1] > 0
            ):
                indices.append(i)
        
        # Threshold crossing (Zero-crossing of net signal relative to baseline 1.0)
        for i in range(1, len(smoothed)):
            if (smoothed[i] > 1.0 and smoothed[i - 1] <= 1.0) or (
                smoothed[i] < 1.0 and smoothed[i - 1] >= 1.0
            ):
                if i not in indices:
                    indices.append(i)

        if len(smoothed) - 1 not in indices:
            indices.append(len(smoothed) - 1)
        
        return sorted(list(set(indices)))

    def _merge_segments(
        self,
        indices: list[int],
        smoothed: list[float],
        times: list[datetime],
        quiet_day: bool,
    ) -> list[int]:
        """Merges segments that are too short or too numerous."""
        current = list(indices)

        # First pass: merge segments shorter than MIN_SEGMENT_MINUTES.
        i = 1
        while i < len(current) - 1:
            delta = (times[current[i]] - times[current[i - 1]]).total_seconds() / 60
            if delta < self.MIN_SEGMENT_MINUTES:
                # Remove current[i] to merge with next
                current.pop(i)
            else:
                i += 1

        # Second pass: if still > MAX_SEGMENTS, merge the ones with least difference in orientation
        while len(current) - 1 > self.MAX_SEGMENTS:
            best_to_remove = -1
            min_diff = float("inf")
            for j in range(1, len(current) - 1):
                # Slopes
                slope_prev = (
                    smoothed[current[j]] - smoothed[current[j - 1]]
                ) / max(1, current[j] - current[j - 1])
                slope_next = (
                    smoothed[current[j + 1]] - smoothed[current[j]]
                ) / max(1, current[j + 1] - current[j])
                diff = abs(slope_next - slope_prev)
                if diff < min_diff:
                    min_diff = diff
                    best_to_remove = j
            
            if best_to_remove != -1:
                current.pop(best_to_remove)
            else:
                break

        if not quiet_day:
            while len(current) - 1 < self.MIN_SEGMENTS:
                longest_index = self._longest_segment_index(current)
                if longest_index == -1:
                    break
                start = current[longest_index - 1]
                end = current[longest_index]
                if end - start < 2:
                    break
                midpoint = (start + end) // 2
                if midpoint in current or midpoint in {start, end}:
                    break
                current.insert(longest_index, midpoint)

        return current

    def _is_quiet_day(self, values: list[float]) -> bool:
        if not values:
            return True
        peak_deviation = max(abs(value - 1.0) for value in values)
        spread = max(values) - min(values)
        return peak_deviation < 0.12 and spread < 0.2

    def _longest_segment_index(self, indices: list[int]) -> int:
        if len(indices) < 2:
            return -1
        longest_index = -1
        longest_span = -1
        for idx in range(1, len(indices)):
            span = indices[idx] - indices[idx - 1]
            if span > longest_span:
                longest_span = span
                longest_index = idx
        return longest_index

    def _detect_orientation(self, raw: list[float], smoothed: list[float]) -> str:
        if len(smoothed) < 2:
            return "stable"

        start_val = smoothed[0]
        end_val = smoothed[-1]
        diff = end_val - start_val

        # Thresholds tuned for V3 composite signals (centered on 1.0)
        if abs(diff) < 0.10:
            # Check for volatility within the block using the RAW signal
            if len(raw) > 2:
                std = statistics.stdev(raw)
                if std > 0.3: # Volatility is higher in raw signal
                    return "volatile"
            return "stable"

        return "rising" if diff > 0 else "falling"

    def _calculate_intensity(self, signal: list[float]) -> float:
        """Intensity is the average absolute deviation from neutral (1.0), scaled 0-20."""
        if not signal:
            return 0.0
        avg_deviation = statistics.mean([abs(v - 1.0) for v in signal])
        # Calibrate: 0.5 average deviation is a strong 10/20 intensity.
        # Max out at 20.0 for extreme days.
        return min(20.0, avg_deviation * 20.0)

    def _calculate_confidence(self, raw: list[float], smoothed: list[float]) -> float:
        """Confidence is inverse to the residual noise after smoothing."""
        if not raw or not smoothed:
            return 1.0
        residuals = [abs(r - s) for r, s in zip(raw, smoothed)]
        avg_res = statistics.mean(residuals)
        # 0.25 average residual (25% noise) = 0.5 confidence
        return max(0.0, min(1.0, 1.0 - (avg_res * 2.0)))

    def _get_dominant_themes(
        self, theme_signals: dict[str, V3ThemeSignal], start: datetime, end: datetime
    ) -> list[str]:
        impacts = {}
        for code, signal in theme_signals.items():
            segment_vals = [
                layer.composite for t, layer in signal.timeline.items() if start <= t < end
            ]
            if segment_vals:
                # Impact is the energy (deviation from neutral) in this segment
                impacts[code] = statistics.mean([abs(v - 1.0) for v in segment_vals])

        sorted_impacts = sorted(impacts.items(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_impacts[:3]]

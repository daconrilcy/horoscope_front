from typing import Mapping

from app.infra.db.repositories.prediction_schemas import CalibrationData
from app.prediction.aggregator import DayAggregation

DEFAULT_CALIBRATION = CalibrationData(p05=-1.5, p25=-0.5, p50=0.0, p75=0.5, p95=1.5, sample_size=0)


class PercentileCalibrator:
    """
    Convertit un score raw_day en une note de 1 à 20 par interpolation
    piecewise linéaire sur 5 percentiles.
    """

    # Notes cibles aux ancres P5, P25, P50, P75, P95
    PERCENTILE_TARGETS = [2.0, 6.0, 10.0, 14.0, 19.0]

    def calibrate(self, raw_day: float, calibration: CalibrationData | None) -> int:
        """
        Calibre une valeur raw en note [1, 20].
        """
        cal = calibration or DEFAULT_CALIBRATION

        anchors = [
            cal.p05 if cal.p05 is not None else DEFAULT_CALIBRATION.p05,
            cal.p25 if cal.p25 is not None else DEFAULT_CALIBRATION.p25,
            cal.p50 if cal.p50 is not None else DEFAULT_CALIBRATION.p50,
            cal.p75 if cal.p75 is not None else DEFAULT_CALIBRATION.p75,
            cal.p95 if cal.p95 is not None else DEFAULT_CALIBRATION.p95,
        ]
        targets = self.PERCENTILE_TARGETS

        if raw_day < anchors[0]:
            return 1
        if raw_day > anchors[-1]:
            return 20

        anchor_groups = self._group_equal_anchors(anchors)
        for start, end in anchor_groups:
            if raw_day == anchors[start]:
                return self._exact_score_for_anchor_group(start, end, targets)

        group_scores = [
            (anchors[start], self._interpolation_score_for_anchor_group(start, end, targets))
            for start, end in anchor_groups
        ]

        for i in range(len(group_scores) - 1):
            x0, y0 = group_scores[i]
            x1, y1 = group_scores[i + 1]
            if x0 < raw_day < x1:
                t = (raw_day - x0) / (x1 - x0)
                return max(1, min(20, round(y0 + t * (y1 - y0))))

        # Calibration entièrement dégénérée ou valeur non couverte par interpolation.
        return group_scores[len(group_scores) // 2][1]

    def calibrate_all(
        self,
        day_aggregation: DayAggregation,
        calibrations: Mapping[str, CalibrationData | None],
    ) -> dict[str, int]:
        """
        Calibre toutes les catégories d'un DayAggregation en notes 1-20.
        """
        results = {}
        for category, cat_agg in day_aggregation.categories.items():
            cal = calibrations.get(category)
            results[category] = self.calibrate(cat_agg.raw_day, cal)
        return results

    def _group_equal_anchors(self, anchors: list[float]) -> list[tuple[int, int]]:
        groups: list[tuple[int, int]] = []
        start = 0
        for idx in range(1, len(anchors)):
            if anchors[idx] != anchors[start]:
                groups.append((start, idx - 1))
                start = idx
        groups.append((start, len(anchors) - 1))
        return groups

    def _exact_score_for_anchor_group(self, start: int, end: int, targets: list[float]) -> int:
        if start <= 2 <= end:
            return 10
        if start == 0 and end == 0:
            return 1
        if start == 4 and end == 4:
            return 20
        return self._interpolation_score_for_anchor_group(start, end, targets)

    def _interpolation_score_for_anchor_group(
        self, start: int, end: int, targets: list[float]
    ) -> int:
        if start <= 2 <= end:
            return 10
        if end < 2:
            return round(targets[end])
        if start > 2:
            return round(targets[start])
        return round(targets[(start + end) // 2])

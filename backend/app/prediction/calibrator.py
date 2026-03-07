from typing import Mapping
from app.infra.db.repositories.prediction_schemas import CalibrationData
from app.prediction.aggregator import DayAggregation

DEFAULT_CALIBRATION = CalibrationData(
    p05=-1.5, p25=-0.5, p50=0.0, p75=0.5, p95=1.5, sample_size=0
)


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

        if raw_day <= anchors[0]:
            return 1
        if raw_day >= anchors[-1]:
            return 20

        for i in range(len(anchors) - 1):
            x0, x1 = anchors[i], anchors[i + 1]
            y0, y1 = targets[i], targets[i + 1]
            if x0 <= raw_day <= x1 and x1 > x0:
                t = (raw_day - x0) / (x1 - x0)
                return max(1, min(20, round(y0 + t * (y1 - y0))))

        # Fallback : calibration dégénérée (percentiles égaux)
        return 10

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

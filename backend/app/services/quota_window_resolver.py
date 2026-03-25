from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class QuotaWindow:
    window_start: datetime  # timezone-aware UTC
    window_end: datetime | None  # None uniquement si reset_mode="lifetime"


class QuotaWindowResolver:
    UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
    WEEK_ANCHOR = datetime(1969, 12, 29, tzinfo=timezone.utc)  # Lundi précédant l'époque

    @staticmethod
    def compute_window(
        period_unit: str, period_value: int, reset_mode: str, ref_dt: datetime
    ) -> QuotaWindow:
        if ref_dt.tzinfo is None:
            raise ValueError("ref_dt must be timezone-aware")

        ref_dt_utc = ref_dt.astimezone(timezone.utc)

        if reset_mode == "rolling":
            raise ValueError("rolling windows not supported in this version")

        if reset_mode == "lifetime" or period_unit == "lifetime":
            return QuotaWindow(window_start=QuotaWindowResolver.UNIX_EPOCH, window_end=None)

        if period_unit == "day":
            days_since_epoch = (ref_dt_utc.date() - QuotaWindowResolver.UNIX_EPOCH.date()).days
            slot = days_since_epoch // period_value
            window_start = QuotaWindowResolver.UNIX_EPOCH + timedelta(days=slot * period_value)
            window_end = window_start + timedelta(days=period_value)
            return QuotaWindow(window_start=window_start, window_end=window_end)

        if period_unit == "week":
            # (ref_dt_utc.date() - WEEK_ANCHOR.date()).days // 7 gives weeks since anchor
            weeks_since_anchor = (
                ref_dt_utc.date() - QuotaWindowResolver.WEEK_ANCHOR.date()
            ).days // 7
            slot = weeks_since_anchor // period_value
            window_start = QuotaWindowResolver.WEEK_ANCHOR + timedelta(weeks=slot * period_value)
            window_end = window_start + timedelta(weeks=period_value)
            return QuotaWindow(window_start=window_start, window_end=window_end)

        if period_unit == "month":
            total_months = ref_dt_utc.year * 12 + (ref_dt_utc.month - 1)
            slot = total_months // period_value
            start_month_total = slot * period_value
            start_year, start_month_idx = divmod(start_month_total, 12)
            window_start = datetime(start_year, start_month_idx + 1, 1, tzinfo=timezone.utc)

            end_month_total = start_month_total + period_value
            end_year, end_month_idx = divmod(end_month_total, 12)
            window_end = datetime(end_year, end_month_idx + 1, 1, tzinfo=timezone.utc)
            return QuotaWindow(window_start=window_start, window_end=window_end)

        if period_unit == "year":
            slot = ref_dt_utc.year // period_value
            window_start = datetime(slot * period_value, 1, 1, tzinfo=timezone.utc)
            window_end = datetime((slot + 1) * period_value, 1, 1, tzinfo=timezone.utc)
            return QuotaWindow(window_start=window_start, window_end=window_end)

        raise ValueError(f"Unsupported period_unit: {period_unit}")

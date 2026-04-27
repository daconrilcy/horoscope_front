"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import csv
import io
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.core.api_constants import VALID_VIEWS
from app.services.llm_observability.consumption_service import (
    CanonicalConsumptionAggregate,
    CanonicalConsumptionFilters,
    Granularity,
    LlmCanonicalConsumptionService,
)

ConsumptionView = str
from app.services.api_contracts.admin.llm.consumption import CanonicalConsumptionViewRow


def _normalize_view(view: str) -> ConsumptionView:
    value = (view or "").strip().lower()
    if value not in VALID_VIEWS:
        return "user"
    return value


def _safe_sort_value(row: CanonicalConsumptionViewRow, field: str) -> Any:
    value = getattr(row, field, None)
    if value is None:
        return (1, "")
    if isinstance(value, datetime):
        return (0, value)
    if isinstance(value, (int, float)):
        return (0, value)
    return (0, str(value).lower())


def _group_key(row: CanonicalConsumptionAggregate, view: ConsumptionView) -> tuple[Any, ...]:
    if view == "subscription":
        return (row.period_start_utc, row.subscription_plan)
    if view == "feature":
        return (row.period_start_utc, row.feature, row.subfeature)
    return (row.period_start_utc, row.user_id)


def _build_rows(
    *,
    aggregates: list[CanonicalConsumptionAggregate],
    view: ConsumptionView,
    granularity: Granularity,
    user_emails: dict[int, str],
) -> list[CanonicalConsumptionViewRow]:
    grouped: dict[tuple[Any, ...], list[CanonicalConsumptionAggregate]] = {}
    for aggregate in aggregates:
        grouped.setdefault(_group_key(aggregate, view), []).append(aggregate)

    result: list[CanonicalConsumptionViewRow] = []
    for entries in grouped.values():
        sample = entries[0]
        request_count = sum(item.call_count for item in entries)
        input_tokens = sum(item.tokens_in for item in entries)
        output_tokens = sum(item.tokens_out for item in entries)
        total_tokens = sum(item.total_tokens for item in entries)
        estimated_cost = float(sum(Decimal(str(item.cost_usd_estimated)) for item in entries))
        # Filled later from raw llm_call_logs to avoid invalid math on pre-aggregated percentiles.
        avg_latency_ms = 0.0
        weighted_error_rate = (
            sum(item.error_rate * item.call_count for item in entries) / request_count
            if request_count
            else 0.0
        )

        row = CanonicalConsumptionViewRow(
            period_start_utc=sample.period_start_utc,
            granularity=granularity,
            request_count=request_count,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=round(estimated_cost, 8),
            avg_latency_ms=round(avg_latency_ms, 2),
            error_rate=round(weighted_error_rate, 6),
        )

        if view == "subscription":
            row.subscription_plan = sample.subscription_plan
        elif view == "feature":
            row.feature = sample.feature
            row.subfeature = sample.subfeature
        else:
            row.user_id = sample.user_id
            row.user_email = user_emails.get(sample.user_id) if sample.user_id is not None else None

        result.append(row)
    return result


def _resolve_exact_average_latencies(
    *,
    db: Session,
    rows: list[CanonicalConsumptionViewRow],
    view: ConsumptionView,
    filters: CanonicalConsumptionFilters,
) -> None:
    grouped_latencies = LlmCanonicalConsumptionService.get_average_latency_index(
        db=db,
        filters=filters,
        view=view,  # type: ignore[arg-type]
    )

    for row in rows:
        if view == "user":
            key = (row.period_start_utc, row.user_id)
        elif view == "subscription":
            key = (row.period_start_utc, row.subscription_plan)
        else:
            key = (row.period_start_utc, row.feature, row.subfeature)
        row.avg_latency_ms = grouped_latencies.get(key, 0.0)


def _apply_search(
    rows: list[CanonicalConsumptionViewRow], search: str | None
) -> list[CanonicalConsumptionViewRow]:
    if not search:
        return rows
    needle = search.strip().lower()
    if not needle:
        return rows
    filtered: list[CanonicalConsumptionViewRow] = []
    for row in rows:
        haystack = " ".join(
            str(value or "")
            for value in (
                row.user_email,
                row.user_id,
                row.subscription_plan,
                row.feature,
                row.subfeature,
                row.period_start_utc.isoformat(),
            )
        ).lower()
        if needle in haystack:
            filtered.append(row)
    return filtered


def _rows_to_csv(rows: list[CanonicalConsumptionViewRow], view: ConsumptionView) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    headers = [
        "period_start_utc",
        "granularity",
        "request_count",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "estimated_cost",
        "avg_latency_ms",
        "error_rate",
    ]
    if view == "user":
        headers.extend(["user_id", "user_email"])
    elif view == "subscription":
        headers.append("subscription_plan")
    else:
        headers.extend(["feature", "subfeature"])
    writer.writerow(headers)
    for row in rows:
        values = [
            row.period_start_utc.isoformat(),
            row.granularity,
            row.request_count,
            row.input_tokens,
            row.output_tokens,
            row.total_tokens,
            row.estimated_cost,
            row.avg_latency_ms,
            row.error_rate,
        ]
        if view == "user":
            values.extend([row.user_id, row.user_email or ""])
        elif view == "subscription":
            values.append(row.subscription_plan or "")
        else:
            values.extend([row.feature or "", row.subfeature or ""])
        writer.writerow(values)
    return output.getvalue()

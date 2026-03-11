from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from app.prediction.decision_window_builder import DecisionWindowBuilder
from app.prediction.editorial_template_engine import EditorialTemplateEngine

if TYPE_CHECKING:
    from .persisted_snapshot import PersistedPredictionSnapshot

MAJOR_ASPECT_NOTE_THRESHOLD = 12.0
PUBLIC_PIVOT_EVENT_TYPES = frozenset(
    {
        "aspect_exact_to_angle",
        "aspect_exact_to_luminary",
        "aspect_exact_to_personal",
        "asc_sign_change",
        "moon_sign_ingress",
    }
)


class PublicPredictionAssembler:
    """
    Assembles the public API response for a daily prediction.
    AC1/AC4 Compliance: Uses typed snapshot for projection.
    """

    def assemble(
        self,
        snapshot: PersistedPredictionSnapshot,
        cat_id_to_code: dict[int, str],
        *,
        engine_output: Any | None = None,
        was_reused: bool = False,
        reference_version: str,
        ruleset_version: str,
    ) -> dict[str, Any]:
        # 1. Categories
        categories = PublicCategoryPolicy().build(snapshot, cat_id_to_code)
        category_note_by_code = {c["code"]: c["note_20"] for c in categories}

        # 2. Decision Windows
        decision_windows = PublicDecisionWindowPolicy().build(
            snapshot, cat_id_to_code, category_note_by_code, engine_output=engine_output
        )

        is_flat_day = _is_flat_day(snapshot, decision_windows)

        # 3. Turning Points
        turning_points = PublicTurningPointPolicy().build(
            snapshot,
            decision_windows or [],
            is_flat_day=is_flat_day,
        )

        # 4. Timeline
        turning_point_times = [
            datetime.fromisoformat(tp["occurred_at_local"])
            if isinstance(tp["occurred_at_local"], str)
            else tp["occurred_at_local"]
            for tp in turning_points
            if tp.get("occurred_at_local")
        ]
        timeline = PublicTimelinePolicy().build(
            snapshot, category_note_by_code, turning_point_times
        )

        # 5. Summary
        summary = PublicSummaryPolicy().build(
            snapshot,
            cat_id_to_code,
            decision_windows,
            turning_points,
            is_flat_day=is_flat_day,
            engine_output=engine_output,
        )

        # 6. Micro Trends (Story 41.14)
        micro_trends = None
        if summary.get("flat_day") and snapshot.relative_scores:
            micro_trends = PublicMicroTrendPolicy().build(snapshot)

        # 7. Meta
        house_system_effective = snapshot.house_system_effective
        if house_system_effective is None and engine_output is not None:
            core_output = _resolve_core_engine_output(engine_output)
            house_system_effective = getattr(
                getattr(core_output, "effective_context", None),
                "house_system_effective",
                None,
            )

        meta = {
            "date_local": snapshot.local_date.isoformat(),
            "timezone": snapshot.timezone,
            "computed_at": snapshot.computed_at.isoformat(),
            "reference_version": reference_version,
            "ruleset_version": ruleset_version,
            "was_reused": was_reused,
            "house_system_effective": house_system_effective,
            "is_provisional_calibration": snapshot.is_provisional_calibration,
            "calibration_label": snapshot.calibration_label,
        }

        return {
            "meta": meta,
            "summary": summary,
            "categories": categories,
            "timeline": timeline,
            "turning_points": turning_points,
            "decision_windows": decision_windows,
            "micro_trends": micro_trends,
        }


class PublicMicroTrendPolicy:
    """
    Builds micro-trends for flat days based on relative scores.
    AC3/AC4 Compliance: Nuance-focused wording, limit to 3 trends.
    """

    MICRO_TREND_LABELS = {
        "fr": {
            "positive": [
                "Légère fluidité dans le domaine {cat}",
                "Nuance plutôt porteuse pour {cat}",
                "Un climat un peu plus dégagé en {cat}",
            ],
            "negative": [
                "Petite nuance de réserve en {cat}",
                "Climat un poil plus exigeant pour {cat}",
                "Discrète vigilance suggérée en {cat}",
            ],
        }
    }

    def build(self, snapshot: PersistedPredictionSnapshot) -> list[dict[str, Any]]:
        trends = []
        labels = EditorialTemplateEngine.CATEGORY_LABELS["fr"]

        candidates = [
            rel
            for rel in snapshot.relative_scores.values()
            if rel.is_available and self._meets_signal_threshold(rel)
        ]
        candidates.sort(
            key=lambda rel: (
                -self._signal_strength(rel),
                rel.category_code,
            )
        )

        for rel in candidates[:3]:  # AC3: limit to 3
            cat_name = labels.get(rel.category_code, rel.category_code).lower()

            # Select wording based on sign
            is_pos = self._signal_polarity(rel) >= 0
            pool = self.MICRO_TREND_LABELS["fr"]["positive" if is_pos else "negative"]
            # Use rank to vary wording or just take first for simplicity
            idx = (rel.relative_rank - 1) % len(pool) if rel.relative_rank else 0
            wording = pool[idx].format(cat=cat_name)

            trends.append(
                {
                    "category_code": rel.category_code,
                    "z_score": (
                        round(rel.relative_z_score, 2)
                        if rel.relative_z_score is not None
                        else None
                    ),
                    "percentile": round(rel.relative_percentile or 0.0, 3),
                    "rank": rel.relative_rank or 99,
                    "wording": wording,
                }
            )

        return trends

    def _meets_signal_threshold(self, relative_score: Any) -> bool:
        if relative_score.relative_z_score is not None:
            return abs(relative_score.relative_z_score) >= 0.5
        if relative_score.relative_percentile is None:
            return False
        return (
            relative_score.relative_percentile >= 0.7
            or relative_score.relative_percentile <= 0.3
        )

    def _signal_strength(self, relative_score: Any) -> float:
        if relative_score.relative_z_score is not None:
            return abs(relative_score.relative_z_score)
        percentile = relative_score.relative_percentile or 0.5
        return abs(percentile - 0.5) * 2

    def _signal_polarity(self, relative_score: Any) -> float:
        if relative_score.relative_z_score is not None:
            return relative_score.relative_z_score
        return (relative_score.relative_percentile or 0.5) - 0.5


class PublicCategoryPolicy:
    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        cat_id_to_code: dict[int, str],
    ) -> list[dict[str, Any]]:
        categories = []
        for s in snapshot.category_scores:
            code = cat_id_to_code.get(s.category_id, "unknown")

            categories.append({
                "code": code,
                "note_20": s.note_20,
                "raw_score": s.raw_score,
                "power": s.power,
                "volatility": s.volatility,
                "rank": s.rank,
                "is_provisional": s.is_provisional,
                "summary": s.summary,
            })
        return sorted(categories, key=lambda c: c["rank"])


class PublicDecisionWindowPolicy:
    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        cat_id_to_code: dict[int, str],
        category_note_by_code: dict[str, float],
        *,
        engine_output: Any | None = None,
    ) -> list[dict[str, Any]] | None:
        # Use Engine Output if available (live compute)
        raw_windows = []
        core_output = _resolve_core_engine_output(engine_output)
        if core_output is not None:
            raw_dws = getattr(core_output, "decision_windows", None) or []
            raw_windows = [
                {
                    "start_local": dw.start_local.isoformat(),
                    "end_local": dw.end_local.isoformat(),
                    "window_type": dw.window_type,
                    "score": dw.score,
                    "confidence": dw.confidence,
                    "dominant_categories": list(dw.dominant_categories),
                }
                for dw in raw_dws
            ]

        # Otherwise rebuild from snapshot
        if not raw_windows:
            raw_windows = self._rebuild_from_snapshot(snapshot, cat_id_to_code)

        if not raw_windows:
            return None

        normalized = self._normalize(snapshot, raw_windows, category_note_by_code)
        return normalized or None

    def _rebuild_from_snapshot(
        self, snapshot: PersistedPredictionSnapshot, cat_id_to_code: dict[int, str]
    ) -> list[dict[str, Any]]:
        if not snapshot.time_blocks:
            return []

        category_scores = {
            cat_id_to_code.get(score.category_id, "unknown"): {
                "note_20": float(score.note_20),
                "volatility": score.volatility,
            }
            for score in snapshot.category_scores
            if score.category_id in cat_id_to_code
        }

        # Adapt snapshot blocks to what DecisionWindowBuilder expects.
        from types import SimpleNamespace

        blocks = [
            SimpleNamespace(
                start_local=b.start_at_local,
                end_local=b.end_at_local,
                tone_code=b.tone_code,
                dominant_categories=b.dominant_categories,
            )
            for b in snapshot.time_blocks
        ]

        turning_points = [
            SimpleNamespace(local_time=tp.occurred_at_local) for tp in snapshot.turning_points
        ]

        rebuilt = DecisionWindowBuilder().build(blocks, turning_points, category_scores)
        if not rebuilt:
            return []

        return [
            {
                "start_local": window.start_local.isoformat(),
                "end_local": window.end_local.isoformat(),
                "window_type": window.window_type,
                "score": window.score,
                "confidence": window.confidence,
                "dominant_categories": list(window.dominant_categories),
            }
            for window in rebuilt
        ]

    def _normalize(
        self,
        snapshot: PersistedPredictionSnapshot,
        raw_windows: list[dict[str, Any]],
        category_note_by_code: dict[str, float],
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        sorted_raw = sorted(
            raw_windows,
            key=lambda item: item["start_local"],
        )

        for window in sorted_raw:
            dominant_categories = self._filter_major_categories(
                window["dominant_categories"],
                category_note_by_code,
            )
            if not dominant_categories:
                if not self._should_keep_public_pivot_window(snapshot, window):
                    continue
                dominant_categories = list(dict.fromkeys(window["dominant_categories"]))[:2]

            if normalized:
                previous = normalized[-1]
                if (
                    previous["end_local"] == window["start_local"]
                    and previous["window_type"] == window["window_type"]
                    and previous["dominant_categories"] == dominant_categories
                ):
                    normalized[-1] = {
                        **previous,
                        "end_local": window["end_local"],
                        "score": max(previous["score"], window["score"]),
                        "confidence": max(previous["confidence"], window["confidence"]),
                    }
                    continue

            normalized.append(
                {
                    **window,
                    "dominant_categories": dominant_categories,
                }
            )

        return normalized

    def _should_keep_public_pivot_window(
        self,
        snapshot: PersistedPredictionSnapshot,
        window: dict[str, Any],
    ) -> bool:
        if window.get("window_type") != "pivot":
            return False

        window_start = window.get("start_local")
        for turning_point in snapshot.turning_points:
            if not _same_local_moment(turning_point.occurred_at_local, window_start):
                continue
            if any(
                driver.get("event_type") in PUBLIC_PIVOT_EVENT_TYPES
                for driver in turning_point.drivers
            ):
                return True
        return False

    def _filter_major_categories(
        self, categories: list[str], category_note_by_code: dict[str, float]
    ) -> list[str]:
        unique_categories: list[str] = []
        for category in categories:
            if category in unique_categories:
                continue
            if float(category_note_by_code.get(category, 10)) <= MAJOR_ASPECT_NOTE_THRESHOLD:
                continue
            unique_categories.append(category)
        return unique_categories[:3]


class PublicTurningPointPolicy:
    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        decision_windows: list[dict[str, Any]],
        *,
        is_flat_day: bool = False,
    ) -> list[dict[str, Any]]:
        if is_flat_day:
            return []

        if not decision_windows:
            return [
                {
                    "occurred_at_local": tp.occurred_at_local.isoformat(),
                    "severity": float(tp.severity),
                    "summary": tp.summary,
                    "drivers": tp.drivers,
                }
                for tp in sorted(snapshot.turning_points, key=lambda item: item.occurred_at_local)
            ]

        if snapshot.turning_points:
            public_turning_points: list[dict[str, Any]] = []
            pivot_window_starts = [
                window["start_local"]
                for window in decision_windows
                if window.get("window_type") == "pivot"
            ]
            for tp in sorted(snapshot.turning_points, key=lambda item: item.occurred_at_local):
                occurred_at = tp.occurred_at_local.isoformat()
                if pivot_window_starts and not any(
                    _same_local_moment(tp.occurred_at_local, window_start)
                    for window_start in pivot_window_starts
                ):
                    continue
                prev_cats = self._get_active_categories(
                    decision_windows,
                    occurred_at,
                    include_end=True,
                    include_start=False,
                )
                next_cats = self._get_active_categories(
                    decision_windows,
                    occurred_at,
                    include_end=False,
                    include_start=True,
                )
                summary = tp.summary
                if summary in {None, "delta_note", "top3_change", "high_priority_event"}:
                    summary = self._build_summary(occurred_at, prev_cats, next_cats)

                public_turning_points.append(
                    {
                        "occurred_at_local": occurred_at,
                        "severity": float(tp.severity),
                        "summary": summary,
                        "drivers": tp.drivers,
                    }
                )

            return public_turning_points

        # Otherwise synthesize pivots from interior boundaries only.
        sorted_windows = sorted(
            decision_windows,
            key=lambda window: window["start_local"],
        )
        boundaries = sorted(
            {w["start_local"] for w in sorted_windows} | {w["end_local"] for w in sorted_windows}
        )

        public_turning_points: list[dict[str, Any]] = []

        for boundary in boundaries[1:-1]:
            prev_cats = self._get_active_categories(
                sorted_windows,
                boundary,
                include_end=True,
                include_start=False,
            )
            next_cats = self._get_active_categories(
                sorted_windows,
                boundary,
                include_end=False,
                include_start=True,
            )

            if prev_cats == next_cats:
                continue

            drivers = []
            for tp in snapshot.turning_points:
                if tp.occurred_at_local.isoformat() == boundary:
                    drivers.extend(tp.drivers)

            public_turning_points.append(
                {
                    "occurred_at_local": boundary,
                    "severity": 1.0 if prev_cats and next_cats else 0.8,
                    "summary": self._build_summary(boundary, prev_cats, next_cats),
                    "drivers": drivers,
                }
            )

        return public_turning_points

    def _get_active_categories(
        self,
        windows: list[dict[str, Any]],
        boundary: str,
        *,
        include_start: bool,
        include_end: bool,
    ) -> list[str]:
        for window in windows:
            start = window["start_local"]
            end = window["end_local"]
            after_start = boundary > start or (include_start and boundary == start)
            before_end = boundary < end or (include_end and boundary == end)
            if after_start and before_end:
                return list(window["dominant_categories"])
        return []

    def _build_summary(self, occurred_at: str, prev_cats: list[str], next_cats: list[str]) -> str:
        time_label = datetime.fromisoformat(occurred_at).strftime("%H:%M")
        labels = EditorialTemplateEngine.CATEGORY_LABELS["fr"]

        def fmt(cats):
            return ", ".join(labels.get(c, c) for c in cats)

        if not prev_cats and next_cats:
            return f"À {time_label}, des aspects majeurs émergent : {fmt(next_cats)}."
        if prev_cats and not next_cats:
            return f"À {time_label}, les aspects majeurs s'estompent : {fmt(prev_cats)}."
        return f"À {time_label}, un basculement critique : {fmt(next_cats)}."


class PublicTimelinePolicy:
    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        category_note_by_code: dict[str, float],
        turning_point_times: list[datetime],
    ) -> list[dict[str, Any]]:
        blocks = []
        for b in snapshot.time_blocks:
            dominant_categories = self._filter_major_categories(
                b.dominant_categories,
                category_note_by_code,
            )
            blocks.append(
                {
                    "start_local": b.start_at_local.isoformat(),
                    "end_local": b.end_at_local.isoformat(),
                    "tone_code": b.tone_code,
                    "dominant_categories": dominant_categories,
                    "summary": self._build_summary(
                        b.start_at_local,
                        b.end_at_local,
                        dominant_categories,
                        b.tone_code,
                    ),
                    "turning_point": self._contains_turning_point(
                        b.start_at_local,
                        b.end_at_local,
                        turning_point_times,
                    ),
                }
            )
        return sorted(blocks, key=lambda b: b["start_local"])

    def _filter_major_categories(
        self, categories: list[str], category_note_by_code: dict[str, float]
    ) -> list[str]:
        unique_categories: list[str] = []
        for category in categories:
            if category in unique_categories:
                continue
            if float(category_note_by_code.get(category, 10)) <= MAJOR_ASPECT_NOTE_THRESHOLD:
                continue
            unique_categories.append(category)
        return unique_categories[:3]

    def _build_summary(
        self,
        start: datetime,
        end: datetime,
        cats: list[str],
        tone: str | None,
    ) -> str:
        s_lbl = start.strftime("%H:%M")
        e_lbl = end.strftime("%H:%M")
        if not cats:
            return f"Entre {s_lbl} et {e_lbl}, pas d'aspect majeur."

        tone_lbl = EditorialTemplateEngine.TONE_LABELS["fr"].get(
            tone or "neutral",
            "équilibrée",
        )
        labels = EditorialTemplateEngine.CATEGORY_LABELS["fr"]
        cat_lbl = ", ".join(labels.get(c, c) for c in cats)
        return f"Entre {s_lbl} et {e_lbl}, tonalité {tone_lbl} — {cat_lbl}."

    def _contains_turning_point(
        self,
        start: datetime,
        end: datetime,
        tp_times: list[datetime],
    ) -> bool:
        def to_wall(dt: datetime) -> datetime:
            return dt.replace(tzinfo=None) if dt.tzinfo else dt

        s_wall = to_wall(start)
        e_wall = to_wall(end)

        for tp in tp_times:
            tp_wall = to_wall(tp)
            if s_wall <= tp_wall < e_wall:
                return True
        return False


class PublicSummaryPolicy:
    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        cat_id_to_code: dict[int, str],
        decision_windows: list[dict[str, Any]] | None,
        turning_points: list[dict[str, Any]],
        *,
        is_flat_day: bool = False,
        engine_output: Any | None = None,
    ) -> dict[str, Any]:
        editorial = _resolve_editorial_output(engine_output)

        scores = sorted(snapshot.category_scores, key=lambda s: s.rank or 99)
        top_categories = [cat_id_to_code.get(s.category_id, "unknown") for s in scores[:3]]

        bottom_scores = sorted(
            snapshot.category_scores,
            key=lambda s: (s.note_20, s.rank or 99),
        )
        bottom_categories = [
            cat_id_to_code.get(s.category_id, "unknown") for s in bottom_scores[:2]
        ]

        best_window = None
        if decision_windows and editorial and editorial.best_window:
            best_window = {
                "start_local": editorial.best_window.start_local.isoformat(),
                "end_local": editorial.best_window.end_local.isoformat(),
                "dominant_category": editorial.best_window.dominant_category,
            }

        if best_window is None and decision_windows:
            cand = max(decision_windows, key=lambda w: (w["score"], w["confidence"]))
            if cand.get("dominant_categories"):
                best_window = {
                    "start_local": cand["start_local"],
                    "end_local": cand["end_local"],
                    "dominant_category": cand["dominant_categories"][0],
                }

        tps = sorted(turning_points, key=lambda tp: float(tp["severity"] or 0), reverse=True)
        main_tp = (
            {
                "occurred_at_local": tps[0]["occurred_at_local"],
                "severity": float(tps[0]["severity"]),
                "summary": tps[0]["summary"],
            }
            if tps
            else None
        )

        cal_note = None
        low_var = False
        if snapshot.is_provisional_calibration:
            cal_note = (
                "Les scores sont calculés sans données historiques : ils reflètent "
                "des tendances relatives à la journée, pas des statistiques absolues."
            )
            top3_notes = [s.note_20 for s in scores[:3]]
            if top3_notes and (max(top3_notes) - min(top3_notes) < 3):
                low_var = True

        # Relative fields (AC1)
        relative_top = None
        rel_summary = None
        if is_flat_day and snapshot.relative_scores:
            micro_trends = PublicMicroTrendPolicy().build(snapshot)
            relative_top = [trend["category_code"] for trend in micro_trends]
            rel_summary = self._build_relative_summary(micro_trends)

        return {
            "overall_tone": snapshot.overall_tone,
            "overall_summary": snapshot.overall_summary,
            "calibration_note": cal_note,
            "top_categories": top_categories,
            "bottom_categories": bottom_categories,
            "best_window": best_window,
            "main_turning_point": main_tp,
            "low_score_variance": low_var,
            "flat_day": is_flat_day,
            "relative_top_categories": relative_top,
            "relative_summary": rel_summary,
        }

    def _build_relative_summary(self, micro_trends: list[dict[str, Any]]) -> str | None:
        if not micro_trends:
            return None

        labels = EditorialTemplateEngine.CATEGORY_LABELS["fr"]
        positive_codes = [
            trend["category_code"]
            for trend in micro_trends
            if (trend.get("z_score") or 0.0) > 0
            or (
                trend.get("z_score") is None
                and float(trend.get("percentile") or 0.0) >= 0.5
            )
        ]
        negative_codes = [
            trend["category_code"]
            for trend in micro_trends
            if trend["category_code"] not in positive_codes
        ]

        def _format_names(codes: list[str]) -> str:
            names = [labels.get(code, code).lower() for code in codes]
            if len(names) == 1:
                return names[0]
            if len(names) == 2:
                return f"{names[0]} et {names[1]}"
            return f"{', '.join(names[:-1])} et {names[-1]}"

        parts: list[str] = ["Journée globalement calme."]
        if positive_codes:
            parts.append(
                "Parmi les nuances du jour, léger avantage relatif pour "
                f"{_format_names(positive_codes)}."
            )
        if negative_codes:
            parts.append(
                f"À l'inverse, ambiance un peu plus retenue en {_format_names(negative_codes)}."
            )
        return " ".join(parts)


def _is_flat_day(
    snapshot: PersistedPredictionSnapshot,
    decision_windows: list[dict[str, Any]] | None,
) -> bool:
    if decision_windows:
        return False
    if not snapshot.time_blocks or not snapshot.category_scores:
        return False
    return all(
        float(score.note_20) <= MAJOR_ASPECT_NOTE_THRESHOLD
        for score in snapshot.category_scores
    )


def _resolve_core_engine_output(engine_output: Any | None) -> Any | None:
    if engine_output is None:
        return None
    return getattr(engine_output, "core", engine_output)


def _resolve_editorial_output(engine_output: Any | None) -> Any | None:
    if engine_output is None:
        return None
    editorial_bundle = getattr(engine_output, "editorial", None)
    if editorial_bundle is None:
        return None
    return getattr(editorial_bundle, "data", editorial_bundle)


def _same_local_moment(left: datetime, right: str | datetime | None) -> bool:
    if right is None:
        return False

    right_dt = datetime.fromisoformat(right) if isinstance(right, str) else right

    def to_wall(dt: datetime) -> datetime:
        return dt.replace(tzinfo=None) if dt.tzinfo else dt

    return to_wall(left) == to_wall(right_dt)

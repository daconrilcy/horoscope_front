from __future__ import annotations

import json
from datetime import datetime
from types import SimpleNamespace
from typing import Any

from app.prediction.decision_window_builder import DecisionWindowBuilder
from app.prediction.editorial_template_engine import EditorialTemplateEngine

MAJOR_ASPECT_NOTE_THRESHOLD = 7.0


class PublicPredictionAssembler:
    """
    Assembles the public API response for a daily prediction.
    """

    def assemble(
        self,
        full_run: dict[str, Any],
        cat_id_to_code: dict[int, str],
        *,
        engine_output: Any | None = None,
        was_reused: bool = False,
        reference_version: str,
        ruleset_version: str,
        run_date_local: str,
        run_timezone: str,
        run_computed_at: str,
        run_is_provisional: bool | None = False,
        run_calibration_label: str | None = None,
    ) -> dict[str, Any]:
        # 1. Categories
        categories = PublicCategoryPolicy().build(full_run, cat_id_to_code)
        category_note_by_code = {c["code"]: c["note_20"] for c in categories}

        # 2. Decision Windows
        decision_windows = PublicDecisionWindowPolicy().build(
            full_run, cat_id_to_code, category_note_by_code, engine_output=engine_output
        )

        # 3. Turning Points
        turning_points = PublicTurningPointPolicy().build(
            full_run, decision_windows or []
        )

        # 4. Timeline
        turning_point_times = [
            datetime.fromisoformat(tp["occurred_at_local"])
            for tp in turning_points
            if tp.get("occurred_at_local")
        ]
        timeline = PublicTimelinePolicy().build(
            full_run, category_note_by_code, turning_point_times
        )

        # 5. Summary
        summary = PublicSummaryPolicy().build(
            full_run,
            cat_id_to_code,
            decision_windows,
            turning_points,
            engine_output=engine_output,
            is_provisional=bool(run_is_provisional),
        )

        # 6. Meta
        house_system_effective = full_run.get("house_system_effective")
        if house_system_effective is None and engine_output is not None:
            effective_context = getattr(
                _resolve_core_engine_output(engine_output),
                "effective_context",
                None,
            )
            house_system_effective = getattr(
                effective_context,
                "house_system_effective",
                None,
            )
        meta = {
            "date_local": run_date_local,
            "timezone": run_timezone,
            "computed_at": run_computed_at,
            "reference_version": reference_version,
            "ruleset_version": ruleset_version,
            "was_reused": was_reused,
            "house_system_effective": house_system_effective,
            "is_provisional_calibration": bool(run_is_provisional),
            "calibration_label": run_calibration_label,
        }

        return {
            "meta": meta,
            "summary": summary,
            "categories": categories,
            "timeline": timeline,
            "turning_points": turning_points,
            "decision_windows": decision_windows,
        }


class PublicCategoryPolicy:
    def build(
        self,
        full_run: dict[str, Any],
        cat_id_to_code: dict[int, str],
    ) -> list[dict[str, Any]]:
        categories = [
            {
                "code": cat_id_to_code.get(s["category_id"], "unknown"),
                "note_20": float(s["note_20"] or 0),
                "raw_score": float(s["raw_score"] or 0),
                "power": float(s["power"] or 0),
                "volatility": float(s["volatility"] or 0),
                "rank": int(s["rank"] or 0),
                "is_provisional": s.get("is_provisional"),
                "summary": s.get("summary"),
            }
            for s in full_run.get("category_scores", [])
        ]
        return sorted(categories, key=lambda c: c["rank"])


class PublicDecisionWindowPolicy:
    def build(
        self,
        full_run: dict[str, Any],
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
        
        # Otherwise rebuild from persisted blocks
        if not raw_windows:
            raw_windows = self._rebuild_from_persistence(full_run, cat_id_to_code)

        if not raw_windows:
            return None

        # AC4 - Semantic Normalization (deduplication and filtering)
        return self._normalize(raw_windows, category_note_by_code)

    def _rebuild_from_persistence(
        self, full_run: dict[str, Any], cat_id_to_code: dict[int, str]
    ) -> list[dict[str, Any]]:
        raw_blocks = full_run.get("time_blocks", [])
        if not raw_blocks:
            return []

        category_scores = {
            cat_id_to_code.get(score["category_id"], "unknown"): {
                "note_20": float(score.get("note_20") or 0),
                "volatility": float(score.get("volatility") or 0),
            }
            for score in full_run.get("category_scores", [])
            if score.get("category_id") in cat_id_to_code
        }

        blocks = [
            SimpleNamespace(
                start_local=datetime.fromisoformat(block["start_at_local"]),
                end_local=datetime.fromisoformat(block["end_at_local"]),
                tone_code=block.get("tone_code") or "neutral",
                dominant_categories=self._load_json_list(
                    block.get("dominant_categories_json"),
                    field_name="time_blocks.dominant_categories_json",
                ),
            )
            for block in raw_blocks
            if block.get("start_at_local") and block.get("end_at_local")
        ]
        if not blocks:
            return []

        turning_points = [
            SimpleNamespace(local_time=datetime.fromisoformat(tp["occurred_at_local"]))
            for tp in full_run.get("turning_points", [])
            if tp.get("occurred_at_local")
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
        self, raw_windows: list[dict[str, Any]], category_note_by_code: dict[str, float]
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        sorted_raw = sorted(
            raw_windows,
            key=lambda item: datetime.fromisoformat(item["start_local"]),
        )
        
        for window in sorted_raw:
            dominant_categories = self._filter_major_categories(
                window["dominant_categories"],
                category_note_by_code,
            )
            if not dominant_categories:
                continue

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

            normalized.append({
                **window,
                "dominant_categories": dominant_categories,
            })

        return normalized

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

    def _load_json_list(self, raw_value: str | None, *, field_name: str) -> list[Any]:
        if not raw_value:
            return []
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON payload for {field_name}") from exc
        if not isinstance(parsed, list):
            raise ValueError(f"Expected a JSON list for {field_name}")
        return parsed


class PublicTurningPointPolicy:
    def build(
        self, full_run: dict[str, Any], decision_windows: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        # AC3/AC4 - If no windows, return raw ones
        if not decision_windows:
            return [
                {
                    "occurred_at_local": tp["occurred_at_local"],
                    "severity": float(tp["severity"] or 0),
                    "summary": tp.get("summary"),
                    "drivers": self._load_json_list(
                        tp.get("driver_json"),
                        field_name="turning_points.driver_json",
                    ),
                }
                for tp in full_run.get("turning_points", [])
            ]

        # Otherwise align with decision windows boundaries
        sorted_windows = sorted(
            decision_windows,
            key=lambda window: datetime.fromisoformat(window["start_local"]),
        )
        boundaries = sorted(
            {w["start_local"] for w in sorted_windows} | {w["end_local"] for w in sorted_windows},
            key=datetime.fromisoformat,
        )

        raw_turning_points = full_run.get("turning_points", [])
        public_turning_points: list[dict[str, Any]] = []
        
        for boundary in boundaries:
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
            for tp in raw_turning_points:
                if tp.get("occurred_at_local") == boundary:
                    drivers.extend(
                        self._load_json_list(
                            tp.get("driver_json"),
                            field_name="turning_points.driver_json",
                        )
                    )

            public_turning_points.append({
                "occurred_at_local": boundary,
                "severity": 1.0 if prev_cats and next_cats else 0.8,
                "summary": self._build_summary(boundary, prev_cats, next_cats),
                "drivers": drivers,
            })

        return public_turning_points

    def _get_active_categories(
        self,
        windows: list[dict[str, Any]],
        boundary: str,
        *,
        include_start: bool,
        include_end: bool,
    ) -> list[str]:
        boundary_dt = datetime.fromisoformat(boundary)
        for window in windows:
            start_dt = datetime.fromisoformat(window["start_local"])
            end_dt = datetime.fromisoformat(window["end_local"])
            after_start = boundary_dt > start_dt or (include_start and boundary_dt == start_dt)
            before_end = boundary_dt < end_dt or (include_end and boundary_dt == end_dt)
            if after_start and before_end:
                return list(window["dominant_categories"])
        return []

    def _build_summary(self, occurred_at: str, prev_cats: list[str], next_cats: list[str]) -> str:
        time_label = datetime.fromisoformat(occurred_at).strftime("%H:%M")
        labels = EditorialTemplateEngine.CATEGORY_LABELS["fr"]
        def fmt(cats): return ", ".join(labels.get(c, c) for c in cats)
        
        if not prev_cats and next_cats:
            return f"À {time_label}, des aspects majeurs émergent : {fmt(next_cats)}."
        if prev_cats and not next_cats:
            return f"À {time_label}, les aspects majeurs s'estompent : {fmt(prev_cats)}."
        return f"À {time_label}, un basculement critique : {fmt(next_cats)}."

    def _load_json_list(self, raw_value: str | None, *, field_name: str) -> list[Any]:
        if not raw_value:
            return []
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON payload for {field_name}") from exc
        if not isinstance(parsed, list):
            raise ValueError(f"Expected a JSON list for {field_name}")
        return parsed


class PublicTimelinePolicy:
    def build(
        self,
        full_run: dict[str, Any],
        category_note_by_code: dict[str, float],
        turning_point_times: list[datetime],
    ) -> list[dict[str, Any]]:
        blocks = []
        for raw_block in full_run.get("time_blocks", []):
            dominant_categories = self._filter_major_categories(
                self._load_json_list(
                    raw_block.get("dominant_categories_json"),
                    field_name="time_blocks.dominant_categories_json",
                ),
                category_note_by_code,
            )
            blocks.append({
                "start_local": raw_block["start_at_local"],
                "end_local": raw_block["end_at_local"],
                "tone_code": raw_block.get("tone_code") or "neutral",
                "dominant_categories": dominant_categories,
                "summary": self._build_summary(
                    raw_block["start_at_local"],
                    raw_block["end_at_local"],
                    dominant_categories,
                    raw_block.get("tone_code"),
                ),
                "turning_point": self._contains_turning_point(
                    raw_block["start_at_local"],
                    raw_block["end_at_local"],
                    turning_point_times,
                ),
            })
        return sorted(blocks, key=lambda b: datetime.fromisoformat(b["start_local"]))

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

    def _build_summary(self, start: str, end: str, cats: list[str], tone: str | None) -> str:
        s_lbl = datetime.fromisoformat(start).strftime("%H:%M")
        e_lbl = datetime.fromisoformat(end).strftime("%H:%M")
        if not cats:
            return f"Entre {s_lbl} et {e_lbl}, pas d'aspect majeur."
        
        tone_lbl = EditorialTemplateEngine.TONE_LABELS["fr"].get(tone or "neutral", "équilibrée")
        labels = EditorialTemplateEngine.CATEGORY_LABELS["fr"]
        cat_lbl = ", ".join(labels.get(c, c) for c in cats)
        return f"Entre {s_lbl} et {e_lbl}, tonalité {tone_lbl} — {cat_lbl}."

    def _contains_turning_point(self, start: str, end: str, tp_times: list[datetime]) -> bool:
        s_dt = datetime.fromisoformat(start)
        e_dt = datetime.fromisoformat(end)
        
        def to_wall(dt: datetime) -> datetime:
            return dt.replace(tzinfo=None) if dt.tzinfo else dt
        
        for tp in tp_times:
            # AC - Unified comparison: if one is aware and other is naive, use wall time
            if (s_dt.tzinfo is not None) == (tp.tzinfo is not None):
                if s_dt <= tp < e_dt:
                    return True
            else:
                if to_wall(s_dt) <= to_wall(tp) < to_wall(e_dt):
                    return True
        return False

    def _load_json_list(self, raw_value: str | None, *, field_name: str) -> list[Any]:
        if not raw_value:
            return []
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON payload for {field_name}") from exc
        if not isinstance(parsed, list):
            raise ValueError(f"Expected a JSON list for {field_name}")
        return parsed


class PublicSummaryPolicy:
    def build(
        self,
        full_run: dict[str, Any],
        cat_id_to_code: dict[int, str],
        decision_windows: list[dict[str, Any]] | None,
        turning_points: list[dict[str, Any]],
        *,
        engine_output: Any | None = None,
        is_provisional: bool = False,
    ) -> dict[str, Any]:
        editorial = _resolve_editorial_output(engine_output)
        
        scores = sorted(full_run.get("category_scores", []), key=lambda s: s["rank"] or 99)
        top_categories = [cat_id_to_code.get(s["category_id"], "unknown") for s in scores[:3]]
        
        bottom_scores = sorted(
            full_run.get("category_scores", []),
            key=lambda score: (float(score.get("note_20") or 0), int(score.get("rank") or 99)),
        )
        bottom_categories = [
            cat_id_to_code.get(score["category_id"], "unknown")
            for score in bottom_scores[:2]
        ]

        best_window = None
        if editorial and editorial.best_window:
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
        main_tp = {
            "occurred_at_local": tps[0]["occurred_at_local"],
            "severity": float(tps[0]["severity"]),
            "summary": tps[0]["summary"],
        } if tps else None

        cal_note = None
        low_var = False
        if is_provisional or full_run.get("is_provisional_calibration"):
            cal_note = (
                "Les scores sont calculés sans données historiques : ils reflètent "
                "des tendances relatives à la journée, pas des statistiques absolues."
            )
            top3_notes = [float(s.get("note_20") or 0) for s in scores[:3]]
            if top3_notes and (max(top3_notes) - min(top3_notes) < 3):
                low_var = True

        return {
            "overall_tone": full_run.get("overall_tone"),
            "overall_summary": full_run.get("overall_summary"),
            "calibration_note": cal_note,
            "top_categories": top_categories,
            "bottom_categories": bottom_categories,
            "best_window": best_window,
            "main_turning_point": main_tp,
            "low_score_variance": low_var,
        }


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

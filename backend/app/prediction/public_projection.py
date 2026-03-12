from __future__ import annotations

from datetime import datetime
from numbers import Real
from typing import TYPE_CHECKING, Any

from app.prediction.decision_window_builder import DecisionWindowBuilder
from app.prediction.editorial_template_engine import EditorialTemplateEngine

if TYPE_CHECKING:
    from .persisted_snapshot import PersistedPredictionSnapshot
    from .schemas import V3EvidencePack

MAJOR_ASPECT_NOTE_THRESHOLD = 12.0
PUBLIC_PIVOT_EVENT_TYPES = frozenset(
    {
        "aspect_exact_to_angle",
        "aspect_exact_to_luminary",
        "aspect_exact_to_personal",
        "moon_sign_ingress",
    }
)


class PublicPredictionAssembler:
    """
    Assembles the public API response for a daily prediction.
    AC1/AC4 Compliance: Uses typed snapshot and evidence pack for projection.
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
        # AC1 Story 42.16: Resolve evidence pack
        evidence = self._resolve_evidence_pack(snapshot, engine_output)

        # 1. Categories
        categories = PublicCategoryPolicy().build(snapshot, cat_id_to_code, evidence=evidence)
        category_note_by_code = {c["code"]: c["note_20"] for c in categories}

        # 2. Decision Windows
        decision_windows = PublicDecisionWindowPolicy().build(
            snapshot,
            cat_id_to_code,
            category_note_by_code,
            engine_output=engine_output,
            evidence=evidence,
        )

        is_flat_day = _is_flat_day(snapshot, decision_windows, categories)

        # 3. Turning Points
        turning_points = PublicTurningPointPolicy().build(
            snapshot, decision_windows or [], is_flat_day=is_flat_day, evidence=evidence
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
        micro_trends = None
        if is_flat_day and snapshot.relative_scores:
            micro_trends = PublicMicroTrendPolicy().build(snapshot)

        summary = PublicSummaryPolicy().build(
            snapshot,
            cat_id_to_code,
            decision_windows,
            turning_points,
            is_flat_day=is_flat_day,
            engine_output=engine_output,
            micro_trends=micro_trends,
            evidence=evidence,
        )

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
            "v3_evidence_version": evidence.version if evidence else None,
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

    def _resolve_evidence_pack(
        self, snapshot: PersistedPredictionSnapshot, engine_output: Any | None
    ) -> V3EvidencePack | None:
        """Extracts V3 evidence pack from engine output or snapshot."""
        from .schemas import V3EvidencePack

        if engine_output is not None:
            v3_core = getattr(engine_output, "v3_core", None)
            evidence_pack = getattr(v3_core, "evidence_pack", None)
            if isinstance(evidence_pack, V3EvidencePack):
                return evidence_pack

        v3_metrics = getattr(snapshot, "v3_metrics", None)
        if isinstance(v3_metrics, dict):
            evidence = v3_metrics.get("evidence_pack")
            if isinstance(evidence, dict):
                return _deserialize_evidence_pack(evidence)

        return None


class PublicMicroTrendPolicy:
    """
    Builds micro-trends for flat days based on relative scores.
    AC2 Compliance: Significant deviation from baseline required.
    AC3/AC4 Compliance: Nuance-focused wording, limit to 3 trends.
    """

    MICRO_TREND_LABELS = {
        "fr": {
            "positive": [
                "Légère fluidité : {cat}",
                "Nuance plutôt porteuse : {cat}",
                "Climat un peu plus dégagé : {cat}",
            ],
            "negative": [
                "Petite nuance de réserve : {cat}",
                "Climat un poil plus exigeant : {cat}",
                "Discrète vigilance suggérée : {cat}",
            ],
        },
        "en": {
            "positive": [
                "Slightly smoother: {cat}",
                "Positive nuance: {cat}",
                "A bit more clear: {cat}",
            ],
            "negative": [
                "Slightly reserved: {cat}",
                "A bit more demanding: {cat}",
                "Discrete caution suggested: {cat}",
            ],
        },
    }

    def build(
        self, snapshot: PersistedPredictionSnapshot, lang: str = "fr"
    ) -> list[dict[str, Any]]:
        trends = []
        labels = EditorialTemplateEngine.CATEGORY_LABELS.get(
            lang, EditorialTemplateEngine.CATEGORY_LABELS["fr"]
        )

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
            pool = self.MICRO_TREND_LABELS.get(lang, self.MICRO_TREND_LABELS["fr"])[
                "positive" if is_pos else "negative"
            ]
            # Use rank to vary wording or just take first for simplicity
            idx = (rel.relative_rank - 1) % len(pool) if rel.relative_rank else 0
            wording = pool[idx].format(cat=cat_name)

            trends.append(
                {
                    "category_code": rel.category_code,
                    "z_score": (
                        round(rel.relative_z_score, 2) if rel.relative_z_score is not None else None
                    ),
                    "percentile": round(rel.relative_percentile or 0.0, 3),
                    "rank": rel.relative_rank or 99,
                    "wording": wording,
                }
            )

        return trends

    def _meets_signal_threshold(self, relative_score: Any) -> bool:
        # V3 Logic: Use absolute day baseline (z_abs or pct_abs)
        z_abs = getattr(relative_score, "z_abs", None)
        if isinstance(z_abs, Real):
            return abs(z_abs) >= 1.5

        pct_abs = getattr(relative_score, "pct_abs", None)
        if isinstance(pct_abs, Real):
            return pct_abs >= 0.8 or pct_abs <= 0.2

        # Legacy Fallback
        rel_z = getattr(relative_score, "relative_z_score", None)
        if isinstance(rel_z, Real) and abs(rel_z) >= 1.0:
            return True

        rel_pct = getattr(relative_score, "relative_percentile", None)
        if not isinstance(rel_pct, Real):
            return False
        return rel_pct >= 0.75 or rel_pct <= 0.25

    def _signal_strength(self, relative_score: Any) -> float:
        z_abs = getattr(relative_score, "z_abs", None)
        if isinstance(z_abs, Real):
            return abs(z_abs)

        rel_z = getattr(relative_score, "relative_z_score", None)
        if isinstance(rel_z, Real):
            return max(abs(rel_z), self._percentile_strength(relative_score))

        pct_abs = getattr(relative_score, "pct_abs", None)
        if isinstance(pct_abs, Real):
            return abs(pct_abs - 0.5) * 2

        return self._percentile_strength(relative_score)

    def _signal_polarity(self, relative_score: Any) -> float:
        z_abs = getattr(relative_score, "z_abs", None)
        if isinstance(z_abs, Real):
            return z_abs

        rel_z = getattr(relative_score, "relative_z_score", None)
        if isinstance(rel_z, Real) and rel_z != 0:
            return rel_z

        pct_abs = getattr(relative_score, "pct_abs", None)
        if isinstance(pct_abs, Real):
            return pct_abs - 0.5

        rel_pct = getattr(relative_score, "relative_percentile", None)
        if isinstance(rel_pct, Real):
            return rel_pct - 0.5

        return 0.0

    def _percentile_strength(self, relative_score: Any) -> float:
        rel_pct = getattr(relative_score, "relative_percentile", None)
        if not isinstance(rel_pct, Real):
            return 0.0
        return abs(rel_pct - 0.5) * 2


class PublicCategoryPolicy:
    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        cat_id_to_code: dict[int, str],
        evidence: V3EvidencePack | None = None,
    ) -> list[dict[str, Any]]:
        categories = []

        if evidence:
            for code, theme in evidence.themes.items():
                categories.append(
                    {
                        "code": code,
                        "note_20": round(theme.score_20),
                        "raw_score": theme.level,
                        "power": theme.intensity / 20.0,
                        "volatility": 1.0 - theme.stability / 20.0,
                        "score_20": theme.score_20,
                        "intensity_20": theme.intensity,
                        "confidence_20": theme.stability,
                        "rarity_percentile": theme.rarity,
                        "level_day": theme.level,
                        "dominance_day": theme.dominance,
                        "stability_day": theme.stability,
                        "intensity_day": theme.intensity,
                        "rank": 99,  # Will be re-ranked if needed
                        "is_provisional": snapshot.is_provisional_calibration,
                        "summary": None,
                    }
                )
            # Re-rank by score
            sorted_cats = sorted(categories, key=lambda c: c["score_20"], reverse=True)
            for i, c in enumerate(sorted_cats):
                c["rank"] = i + 1
            return sorted_cats

        # Fallback to snapshot
        for s in snapshot.category_scores:
            code = cat_id_to_code.get(s.category_id, "unknown")
            categories.append(
                {
                    "code": code,
                    "note_20": s.note_20,
                    "raw_score": s.raw_score,
                    "power": s.power,
                    "volatility": s.volatility,
                    "score_20": s.score_20,
                    "intensity_20": s.intensity_20,
                    "confidence_20": s.confidence_20,
                    "rarity_percentile": s.rarity_percentile,
                    "level_day": s.level_day,
                    "dominance_day": s.dominance_day,
                    "stability_day": s.stability_day,
                    "intensity_day": s.intensity_day,
                    "rank": s.rank,
                    "is_provisional": s.is_provisional,
                    "summary": s.summary,
                }
            )
        return sorted(categories, key=lambda c: c["rank"])


class PublicDecisionWindowPolicy:
    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        cat_id_to_code: dict[int, str],
        category_note_by_code: dict[str, float],
        *,
        engine_output: Any | None = None,
        evidence: V3EvidencePack | None = None,
    ) -> list[dict[str, Any]] | None:
        # Prioritize evidence pack
        if evidence:
            raw_windows = [
                {
                    "start_local": w.start_local.isoformat(),
                    "end_local": w.end_local.isoformat(),
                    "window_type": w.type,
                    "score": w.score,
                    "confidence": w.confidence,
                    "dominant_categories": list(w.themes),
                    "intensity": w.intensity,
                }
                for w in evidence.time_windows
            ]
            return self._normalize(snapshot, raw_windows, category_note_by_code) or None

        # Fallback to Engine Output
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
                    "orientation": getattr(dw, "orientation", None),
                    "intensity": getattr(dw, "intensity", None),
                }
                for dw in raw_dws
            ]
            return self._normalize(snapshot, raw_windows, category_note_by_code) or None

        # Otherwise rebuild from snapshot
        raw_windows = self._rebuild_from_snapshot(snapshot, cat_id_to_code)
        if not raw_windows:
            return None

        return self._normalize(snapshot, raw_windows, category_note_by_code) or None

    def _rebuild_from_snapshot(
        self, snapshot: PersistedPredictionSnapshot, cat_id_to_code: dict[int, str]
    ) -> list[dict[str, Any]]:
        if not snapshot.time_blocks:
            return []
        if self._is_low_signal_snapshot(snapshot):
            return []

        category_scores = {
            cat_id_to_code.get(score.category_id, "unknown"): {
                "note_20": float(score.note_20),
                "volatility": score.volatility,
            }
            for score in snapshot.category_scores
            if score.category_id in cat_id_to_code
        }

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

    def _is_low_signal_snapshot(self, snapshot: PersistedPredictionSnapshot) -> bool:
        if not snapshot.category_scores:
            return True
        if any(getattr(s, "intensity_20", None) is not None for s in snapshot.category_scores):
            return all(
                float(getattr(s, "intensity_20", 0.0) or 0.0) < 3.0
                for s in snapshot.category_scores
            )
        if any(
            float(score.note_20) > MAJOR_ASPECT_NOTE_THRESHOLD for score in snapshot.category_scores
        ):
            return False
        return all((block.tone_code or "neutral") == "neutral" for block in snapshot.time_blocks)

    def _normalize(
        self,
        snapshot: PersistedPredictionSnapshot,
        raw_windows: list[dict[str, Any]],
        category_note_by_code: dict[str, float],
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        sorted_raw = sorted(raw_windows, key=lambda item: item["start_local"])

        for window in sorted_raw:
            dominant_categories = self._filter_major_categories(
                window["dominant_categories"],
                category_note_by_code,
            )
            if window.get("window_type") == "pivot":
                keep_public_pivot = self._should_keep_public_pivot_window(snapshot, window)
                if not keep_public_pivot and not dominant_categories:
                    continue
            if not dominant_categories:
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

            normalized.append({**window, "dominant_categories": dominant_categories})
        return normalized

    def _should_keep_public_pivot_window(
        self, snapshot: PersistedPredictionSnapshot, window: dict[str, Any]
    ) -> bool:
        if window.get("window_type") != "pivot":
            return False

        window_start = window.get("start_local")
        for tp in snapshot.turning_points:
            if not _same_local_moment(tp.occurred_at_local, window_start):
                continue

            if any(d.get("event_type") in PUBLIC_PIVOT_EVENT_TYPES for d in tp.drivers):
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
        evidence: V3EvidencePack | None = None,
    ) -> list[dict[str, Any]]:
        if is_flat_day:
            return []

        if evidence:
            return [
                {
                    "occurred_at_local": tp.local_time.isoformat(),
                    "severity": tp.amplitude / 10.0,  # Scaled
                    "summary": f"Bascule durable ({tp.reason})",
                    "drivers": [{"event_type": d} for d in tp.drivers],
                    # Story 43.1
                    "change_type": tp.change_type,
                    "previous_categories": tp.previous_categories,
                    "next_categories": tp.next_categories,
                    "primary_driver": self._serialize_primary_driver(tp.primary_driver),
                    # Story 44.1
                    "movement": self._serialize_movement(tp.movement),
                    "category_deltas": [self._serialize_category_delta(cd) for cd in tp.category_deltas],
                }
                for tp in evidence.turning_points
            ]

        # Fallback: Restore nuance for legacy runs (Story 41.x logic)
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

        # Use windows to filter pivots
        public_turning_points: list[dict[str, Any]] = []
        pivot_window_starts = [
            window["start_local"]
            for window in decision_windows
            if window.get("window_type") == "pivot"
        ]

        for tp in sorted(snapshot.turning_points, key=lambda item: item.occurred_at_local):
            occurred_at = tp.occurred_at_local.isoformat()
            # Only keep if it matches a pivot window start
            if pivot_window_starts and not any(
                _same_local_moment(tp.occurred_at_local, ws) for ws in pivot_window_starts
            ):
                continue

            public_turning_points.append(
                {
                    "occurred_at_local": occurred_at,
                    "severity": float(tp.severity),
                    "summary": tp.summary,
                    "drivers": tp.drivers,
                }
            )

        return public_turning_points

    def _serialize_primary_driver(self, pd: Any | None) -> dict[str, Any] | None:
        if not pd:
            return None
        return {
            "event_type": pd.event_type,
            "body": pd.body,
            "target": pd.target,
            "aspect": pd.aspect,
            "metadata": pd.metadata,
        }

    def _serialize_movement(self, m: Any | None) -> dict[str, Any] | None:
        if not m:
            return None
        return {
            "strength": float(m.strength),
            "previous_composite": float(m.previous_composite),
            "next_composite": float(m.next_composite),
            "delta_composite": float(m.delta_composite),
            "direction": m.direction,
        }

    def _serialize_category_delta(self, cd: Any) -> dict[str, Any]:
        return {
            "code": cd.code,
            "direction": cd.direction,
            "delta_score": float(cd.delta_score),
            "delta_intensity": float(cd.delta_intensity),
            "delta_rank": cd.delta_rank,
        }


class PublicTimelinePolicy:
    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        category_note_by_code: dict[str, float],
        turning_point_times: list[datetime],
    ) -> list[dict[str, Any]]:
        blocks: list[dict[str, Any]] = []
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
                        b.start_at_local, b.end_at_local, dominant_categories, b.tone_code
                    ),
                    "turning_point": self._contains_turning_point(
                        b.start_at_local, b.end_at_local, turning_point_times
                    ),
                }
            )
        return self._merge_adjacent_blocks(sorted(blocks, key=lambda block: block["start_local"]))

    def _merge_adjacent_blocks(self, blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not blocks:
            return []

        merged = [blocks[0]]
        for block in blocks[1:]:
            previous = merged[-1]
            if (
                not previous["turning_point"]
                and not block["turning_point"]
                and previous["end_local"] == block["start_local"]
                and previous["tone_code"] == block["tone_code"]
                and previous["dominant_categories"] == block["dominant_categories"]
            ):
                merged[-1] = {
                    **previous,
                    "end_local": block["end_local"],
                    "summary": self._build_summary(
                        datetime.fromisoformat(previous["start_local"]),
                        datetime.fromisoformat(block["end_local"]),
                        previous["dominant_categories"],
                        previous["tone_code"],
                    ),
                }
                continue
            merged.append(block)
        return merged

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
        self, start: datetime, end: datetime, cats: list[str], tone: str | None
    ) -> str:
        s_lbl, e_lbl = start.strftime("%H:%M"), end.strftime("%H:%M")
        if not cats:
            return f"Entre {s_lbl} et {e_lbl}, pas d'aspect majeur."

        tone_lbl = EditorialTemplateEngine.TONE_LABELS["fr"].get(tone or "neutral", "équilibrée")
        cat_lbl = ", ".join(EditorialTemplateEngine.CATEGORY_LABELS["fr"].get(c, c) for c in cats)
        return f"Entre {s_lbl} et {e_lbl}, tonalité {tone_lbl} — {cat_lbl}."

    def _contains_turning_point(
        self, start: datetime, end: datetime, tp_times: list[datetime]
    ) -> bool:
        s_wall, e_wall = start.replace(tzinfo=None), end.replace(tzinfo=None)
        for tp in tp_times:
            tp_wall = tp.replace(tzinfo=None)
            if s_wall <= tp_wall < e_wall:
                return True
        return False


class PublicSummaryPolicy:
    _SUMMARY_TONE_LABELS = {
        "positive": "très porteuse",
        "mixed": "contrastée",
        "neutral": "équilibrée",
        "negative": "exigeante",
    }

    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        cat_id_to_code: dict[int, str],
        decision_windows: list[dict[str, Any]] | None,
        turning_points: list[dict[str, Any]],
        *,
        is_flat_day: bool = False,
        engine_output: Any | None = None,
        micro_trends: list[dict[str, Any]] | None = None,
        evidence: V3EvidencePack | None = None,
    ) -> dict[str, Any]:
        editorial = _resolve_editorial_output(engine_output)
        top_categories, bottom_categories = self._resolve_ranked_categories(
            snapshot,
            cat_id_to_code,
            evidence=evidence,
        )
        overall_tone = self._resolve_overall_tone(snapshot, evidence)
        overall_summary = self._resolve_overall_summary(
            snapshot,
            top_categories,
            overall_tone,
            evidence=evidence,
        )

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
            cal_note = "Les scores sont calculés sans données historiques."
            scores = sorted(snapshot.category_scores, key=lambda s: s.rank or 99)
            top3_notes = [s.note_20 for s in scores[:3]]
            if top3_notes and (max(top3_notes) - min(top3_notes) < 3):
                low_var = True

        relative_top = (
            [trend["category_code"] for trend in micro_trends]
            if is_flat_day and micro_trends
            else None
        )
        rel_summary = (
            self._build_relative_summary(micro_trends) if is_flat_day and micro_trends else None
        )

        return {
            "overall_tone": overall_tone,
            "overall_summary": overall_summary,
            "calibration_note": cal_note,
            "top_categories": top_categories,
            "bottom_categories": bottom_categories,
            "best_window": self._extract_best_window(decision_windows, editorial),
            "main_turning_point": main_tp,
            "low_score_variance": low_var,
            "flat_day": is_flat_day,
            "relative_top_categories": relative_top,
            "relative_summary": rel_summary,
        }

    def _resolve_ranked_categories(
        self,
        snapshot: PersistedPredictionSnapshot,
        cat_id_to_code: dict[int, str],
        *,
        evidence: V3EvidencePack | None,
    ) -> tuple[list[str], list[str]]:
        if evidence and evidence.themes:
            sorted_themes = sorted(
                evidence.themes.values(),
                key=lambda theme: theme.score_20,
                reverse=True,
            )
            top_categories = [theme.code for theme in sorted_themes[:3]]
            bottom_categories = [
                theme.code
                for theme in sorted(sorted_themes, key=lambda item: item.score_20)[:2]
            ]
            return top_categories, bottom_categories

        scores = sorted(snapshot.category_scores, key=lambda s: s.rank or 99)
        top_categories = [cat_id_to_code.get(s.category_id, "unknown") for s in scores[:3]]
        bottom_scores = sorted(snapshot.category_scores, key=lambda s: (s.note_20, s.rank or 99))
        bottom_categories = [
            cat_id_to_code.get(s.category_id, "unknown") for s in bottom_scores[:2]
        ]
        return top_categories, bottom_categories

    def _resolve_overall_tone(
        self,
        snapshot: PersistedPredictionSnapshot,
        evidence: V3EvidencePack | None,
    ) -> str | None:
        if evidence:
            tone = evidence.day_profile.get("overall_tone") or evidence.day_profile.get("tone")
            if isinstance(tone, str) and tone:
                return tone
        return snapshot.overall_tone

    def _resolve_overall_summary(
        self,
        snapshot: PersistedPredictionSnapshot,
        top_categories: list[str],
        overall_tone: str | None,
        *,
        evidence: V3EvidencePack | None,
    ) -> str | None:
        if evidence:
            explicit_summary = evidence.day_profile.get("overall_summary")
            if isinstance(explicit_summary, str) and explicit_summary.strip():
                return explicit_summary
            return self._build_v3_overall_summary(
                local_date=snapshot.local_date,
                overall_tone=overall_tone or "neutral",
                top_categories=top_categories,
            )
        return snapshot.overall_summary

    def _build_v3_overall_summary(
        self,
        *,
        local_date,
        overall_tone: str,
        top_categories: list[str],
    ) -> str:
        tone_label = self._SUMMARY_TONE_LABELS.get(
            overall_tone,
            self._SUMMARY_TONE_LABELS["neutral"],
        )
        labels = EditorialTemplateEngine.CATEGORY_LABELS["fr"]
        top_labels = ", ".join(labels.get(code, code) for code in top_categories[:3])
        if top_labels:
            return (
                f"Votre journée du {local_date.isoformat()} s'annonce {tone_label}.\n"
                f"Vos points forts : {top_labels}."
            )
        return f"Votre journée du {local_date.isoformat()} s'annonce {tone_label}."

    def _extract_best_window(self, decision_windows, editorial) -> dict[str, Any] | None:
        if not decision_windows:
            return None
        if editorial and editorial.best_window:
            ew = {
                "start_local": editorial.best_window.start_local.isoformat(),
                "end_local": editorial.best_window.end_local.isoformat(),
                "dominant_category": editorial.best_window.dominant_category,
            }
            if any(
                w["start_local"] == ew["start_local"] and w["end_local"] == ew["end_local"]
                for w in decision_windows
            ):
                return ew
        candidates = [w for w in decision_windows if w["window_type"] in ("favorable", "pivot")]
        if candidates:
            cand = max(candidates, key=lambda w: (w["score"], w.get("confidence", 0.5)))
            if cand.get("dominant_categories"):
                return {
                    "start_local": cand["start_local"],
                    "end_local": cand["end_local"],
                    "dominant_category": cand["dominant_categories"][0],
                }
        return None

    def _build_relative_summary(self, micro_trends: list[dict[str, Any]]) -> str | None:
        if not micro_trends:
            return None
        labels = EditorialTemplateEngine.CATEGORY_LABELS["fr"]
        positive_codes = [t["category_code"] for t in micro_trends if (t.get("z_score") or 0.0) > 0]
        negative_codes = [
            t["category_code"] for t in micro_trends if t["category_code"] not in positive_codes
        ]

        def _format_names(codes):
            names = [labels.get(c, c).lower() for c in codes]
            if len(names) == 1:
                return names[0]
            return f"{', '.join(names[:-1])} et {names[-1]}"

        parts = ["Journée globalement calme."]
        if positive_codes:
            parts.append(f"Léger avantage relatif pour {_format_names(positive_codes)}.")
        if negative_codes:
            parts.append(f"Ambiance un peu plus retenue en {_format_names(negative_codes)}.")
        return " ".join(parts)


def _is_flat_day(
    snapshot: PersistedPredictionSnapshot,
    decision_windows: list[dict[str, Any]] | None,
    categories: list[dict[str, Any]],
) -> bool:
    if decision_windows:
        return False
    if not snapshot.time_blocks or not categories:
        return False
    v3_scores = [s for s in categories if s.get("intensity_20") is not None]
    if v3_scores:
        return all(float(s["intensity_20"]) < 3.0 for s in v3_scores) and all(
            float(s.get("stability_day") or 0.0) >= 14.0 for s in v3_scores
        )
    return all(float(score["note_20"]) <= MAJOR_ASPECT_NOTE_THRESHOLD for score in categories)


def _deserialize_evidence_pack(payload: dict[str, Any]) -> V3EvidencePack:
    from .schemas import (
        V3CategoryDelta,
        V3EvidencePack,
        V3EvidenceTheme,
        V3EvidenceTurningPoint,
        V3EvidenceWindow,
        V3Movement,
        V3PrimaryDriver,
    )

    themes = {
        code: V3EvidenceTheme(
            code=theme["code"],
            score_20=float(theme["score_20"]),
            level=float(theme["level"]),
            intensity=float(theme["intensity"]),
            dominance=float(theme["dominance"]),
            stability=float(theme["stability"]),
            rarity=float(theme["rarity"]),
            is_major=bool(theme["is_major"]),
        )
        for code, theme in payload.get("themes", {}).items()
    }
    time_windows = [
        V3EvidenceWindow(
            start_local=datetime.fromisoformat(window["start_local"]),
            end_local=datetime.fromisoformat(window["end_local"]),
            type=window["type"],
            score=float(window["score"]),
            intensity=float(window["intensity"]),
            confidence=float(window["confidence"]),
            themes=list(window.get("themes", [])),
        )
        for window in payload.get("time_windows", [])
    ]
    turning_points = []
    for tp in payload.get("turning_points", []):
        pd_raw = tp.get("primary_driver")
        pd = None
        if pd_raw:
            pd = V3PrimaryDriver(
                event_type=pd_raw["event_type"],
                body=pd_raw.get("body"),
                target=pd_raw.get("target"),
                aspect=pd_raw.get("aspect"),
                metadata=dict(pd_raw.get("metadata", {})),
            )

        mv_raw = tp.get("movement")
        mv = None
        if mv_raw:
            mv = V3Movement(
                strength=float(mv_raw["strength"]),
                previous_composite=float(mv_raw["previous_composite"]),
                next_composite=float(mv_raw["next_composite"]),
                delta_composite=float(mv_raw["delta_composite"]),
                direction=mv_raw["direction"],
            )

        cat_deltas = [
            V3CategoryDelta(
                code=cd["code"],
                direction=cd["direction"],
                delta_score=float(cd["delta_score"]),
                delta_intensity=float(cd["delta_intensity"]),
                delta_rank=cd.get("delta_rank"),
            )
            for cd in tp.get("category_deltas", [])
        ]

        turning_points.append(
            V3EvidenceTurningPoint(
                local_time=datetime.fromisoformat(tp["local_time"]),
                reason=tp["reason"],
                amplitude=float(tp["amplitude"]),
                confidence=float(tp["confidence"]),
                themes=list(tp.get("themes", [])),
                drivers=list(tp.get("drivers", [])),
                # Story 43.1
                change_type=tp.get("change_type", "recomposition"),
                previous_categories=list(tp.get("previous_categories", [])),
                next_categories=list(tp.get("next_categories", [])),
                primary_driver=pd,
                # Story 44.1
                movement=mv,
                category_deltas=cat_deltas,
            )
        )

    return V3EvidencePack(
        version=payload["version"],
        generated_at=datetime.fromisoformat(payload["generated_at"]),
        day_profile=dict(payload.get("day_profile", {})),
        themes=themes,
        time_windows=time_windows,
        turning_points=turning_points,
        v3_natal_structural=dict(payload.get("v3_natal_structural", {})),
        v3_layer_diagnostics=dict(payload.get("v3_layer_diagnostics", {})),
        metadata=dict(payload.get("metadata", {})),
    )


def _resolve_core_engine_output(engine_output: Any | None) -> Any | None:
    if engine_output is None:
        return None
    return getattr(engine_output, "core", engine_output)


def _resolve_editorial_output(engine_output: Any | None) -> Any | None:
    if engine_output is None:
        return None
    eb = getattr(engine_output, "editorial", None)
    return getattr(eb, "data", eb) if eb else None


def _same_local_moment(left: datetime, right: str | datetime | None) -> bool:
    if right is None:
        return False
    rdt = datetime.fromisoformat(right) if isinstance(right, str) else right
    return left.replace(tzinfo=None) == rdt.replace(tzinfo=None)

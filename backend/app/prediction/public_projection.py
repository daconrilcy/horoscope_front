from __future__ import annotations

from datetime import datetime, time
from numbers import Real
from typing import TYPE_CHECKING, Any

from app.core.config import settings
from app.prediction.decision_window_builder import DecisionWindowBuilder
from app.prediction.editorial_template_engine import EditorialTemplateEngine
from app.prediction.public_astro_daily_events import PublicAstroDailyEventsPolicy
from app.prediction.public_astro_vocabulary import (
    HOUSE_SIGNIFICATIONS,
    get_aspect_label,
    get_aspect_tonality,
    get_effect_label,
    get_fixed_star_name_fr,
    get_planet_name_fr,
    get_sign_name_fr,
)
from app.prediction.public_domain_taxonomy import (
    DISPLAY_ORDER,
    PUBLIC_DOMAINS,
    aggregate_public_domain_score,
    map_internal_to_public,
)
from app.prediction.public_label_catalog import (
    get_action_hint,
    get_best_window_why,
    get_climate_label,
    get_do_avoid,
    get_recommended_actions,
    get_regime_label,
    get_turning_point_title,
)
from app.prediction.public_score_mapper import (
    PublicDomainScore,
    rank_domains,
    to_level,
    to_score_10,
)

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

    async def assemble(
        self,
        snapshot: PersistedPredictionSnapshot,
        cat_id_to_code: dict[int, str],
        *,
        engine_output: Any | None = None,
        was_reused: bool = False,
        reference_version: str,
        ruleset_version: str,
        astrologer_profile_key: str = "standard",
        lang: str = "fr",
        prompt_context: Any | None = None,
    ) -> dict[str, Any]:
        # AC1 Story 42.16: Resolve evidence pack
        evidence = self._resolve_evidence_pack(snapshot, engine_output)

        # 1. Categories (V4: Public domains, keep internal for retrocompat)
        internal_categories = PublicCategoryPolicy().build(
            snapshot, cat_id_to_code, evidence=evidence
        )
        category_note_by_code = {c["code"]: c["note_20"] for c in internal_categories}

        # New: Public Domains (V4)
        public_domains = PublicDomainRankingPolicy().build(internal_categories)

        # 2. Decision Windows
        decision_windows = PublicDecisionWindowPolicy().build(
            snapshot,
            cat_id_to_code,
            category_note_by_code,
            engine_output=engine_output,
            evidence=evidence,
        )

        is_flat_day = _is_flat_day(snapshot, decision_windows, internal_categories)

        # 3. Turning Points
        turning_points = PublicTurningPointPolicy().build(
            snapshot, decision_windows or [], is_flat_day=is_flat_day, evidence=evidence
        )

        # New: Best Window (V4)
        best_window = PublicBestWindowPolicy().build(
            snapshot,
            decision_windows=decision_windows,
            turning_points=turning_points,
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

        # New: Day Climate (V4)
        day_climate = PublicDayClimatePolicy().build(
            snapshot,
            domain_ranking=public_domains,
            decision_windows=decision_windows,
            evidence=evidence,
        )
        if best_window:
            day_climate["best_window_ref"] = best_window["time_range"]

        # New: Time Windows (V4)
        time_windows = PublicTimeWindowPolicy().build(
            snapshot,
            turning_points=turning_points,
            engine_output=engine_output,
            evidence=evidence,
        )

        # New: Main Turning Point (V4)
        main_turning_point = PublicMainTurningPointPolicy().build(
            snapshot,
            engine_output=engine_output,
            evidence=evidence,
        )

        # New: Astro Foundation (V4)
        astro_foundation = PublicAstroFoundationPolicy().build(
            snapshot,
            day_climate=day_climate,
            domain_ranking=public_domains,
            engine_output=engine_output,
            evidence=evidence,
        )

        # New: Astro Daily Events (V4)
        astro_daily_events = PublicAstroDailyEventsPolicy().build(
            snapshot,
            engine_output=engine_output,
            evidence=evidence,
        )

        # 8. LLM Narration (V4) - Story 60.16
        daily_synthesis = None
        astro_events_intro = None
        daily_advice = None
        has_llm_narrative = False
        persisted_llm_narrative = getattr(snapshot, "llm_narrative", None)

        if isinstance(persisted_llm_narrative, dict):
            has_llm_narrative = self._apply_persisted_llm_narrative(
                persisted_llm_narrative,
                time_windows=time_windows,
                turning_points=turning_points,
                main_turning_point=main_turning_point,
            )
            if has_llm_narrative:
                daily_synthesis = self._safe_text(persisted_llm_narrative.get("daily_synthesis"))
                astro_events_intro = self._safe_text(
                    persisted_llm_narrative.get("astro_events_intro")
                )
                advice_payload = persisted_llm_narrative.get("daily_advice")
                if isinstance(advice_payload, dict):
                    advice = self._safe_text(advice_payload.get("advice"))
                    emphasis = self._safe_text(advice_payload.get("emphasis"))
                    if advice or emphasis:
                        daily_advice = {"advice": advice, "emphasis": emphasis}

        if not has_llm_narrative and settings.llm_narrator_enabled and prompt_context:
            from app.prediction.llm_narrator import LLMNarrator

            narrator = LLMNarrator()

            narrator_res = await narrator.narrate(
                astro_daily_events=astro_daily_events,
                time_windows=time_windows,
                common_context=prompt_context,
                astrologer_profile_key=astrologer_profile_key,
                lang=lang,
                day_climate=day_climate,
                best_window=best_window,
                turning_point=main_turning_point,
                domain_ranking=public_domains,
            )

            if narrator_res:
                has_llm_narrative = True
                daily_synthesis = narrator_res.daily_synthesis
                astro_events_intro = narrator_res.astro_events_intro
                if narrator_res.daily_advice:
                    daily_advice = {
                        "advice": narrator_res.daily_advice.advice,
                        "emphasis": narrator_res.daily_advice.emphasis,
                    }

                # Inject into time windows
                for w in time_windows:
                    pk = w["period_key"]
                    if pk in narrator_res.time_window_narratives:
                        w["narrative"] = narrator_res.time_window_narratives[pk]

                # Inject into turning points
                for i, tp in enumerate(turning_points):
                    if i < len(narrator_res.turning_point_narratives):
                        tp["narrative"] = narrator_res.turning_point_narratives[i]

                if main_turning_point and narrator_res.main_turning_point_narrative:
                    main_turning_point["narrative"] = narrator_res.main_turning_point_narrative

        # 9. Meta
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
            "payload_version": "v4",
        }

        return {
            "meta": meta,
            "summary": summary,
            "day_climate": day_climate,
            "daily_synthesis": daily_synthesis,
            "astro_events_intro": astro_events_intro,
            "daily_advice": daily_advice,
            "has_llm_narrative": has_llm_narrative,
            "best_window": best_window,
            "time_windows": time_windows,
            "turning_point": main_turning_point,
            "astro_foundation": astro_foundation,
            "astro_daily_events": astro_daily_events,
            "categories": internal_categories,  # Keep for retrocompat
            "categories_internal": internal_categories,
            "domain_ranking": public_domains,
            "timeline": timeline,
            "turning_points": turning_points,
            "decision_windows": decision_windows,
            "micro_trends": micro_trends,
        }

    def _apply_persisted_llm_narrative(
        self,
        payload: dict[str, Any],
        *,
        time_windows: list[dict[str, Any]],
        turning_points: list[dict[str, Any]],
        main_turning_point: dict[str, Any] | None,
    ) -> bool:
        applied = False

        window_payload = payload.get("time_window_narratives")
        if isinstance(window_payload, dict):
            for window in time_windows:
                period_key = window.get("period_key")
                narrative = self._safe_text(window_payload.get(period_key))
                if narrative:
                    window["narrative"] = narrative
                    applied = True

        turning_point_payload = payload.get("turning_point_narratives")
        if isinstance(turning_point_payload, list):
            for index, turning_point in enumerate(turning_points):
                if index >= len(turning_point_payload):
                    break
                narrative = self._safe_text(turning_point_payload[index])
                if narrative:
                    turning_point["narrative"] = narrative
                    applied = True

        if main_turning_point is not None:
            main_narrative = self._safe_text(payload.get("main_turning_point_narrative"))
            if main_narrative:
                main_turning_point["narrative"] = main_narrative
                applied = True

        if self._safe_text(payload.get("daily_synthesis")):
            applied = True
        if self._safe_text(payload.get("astro_events_intro")):
            applied = True
        advice_payload = payload.get("daily_advice")
        if isinstance(advice_payload, dict) and (
            self._safe_text(advice_payload.get("advice"))
            or self._safe_text(advice_payload.get("emphasis"))
        ):
            applied = True

        return applied

    def _safe_text(self, value: Any) -> str:
        if isinstance(value, str):
            return value.strip()
        return ""

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
                try:
                    return _deserialize_evidence_pack(evidence)
                except (KeyError, ValueError, TypeError):
                    pass

        return None


class PublicAstroFoundationPolicy:
    """
    Builds the astrological foundations section (Story 60.7).
    Exposes key movements, activated houses, and dominant aspects.
    """

    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        *,
        day_climate: dict[str, Any],
        domain_ranking: list[dict[str, Any]],
        engine_output: Any | None = None,
        evidence: V3EvidencePack | None = None,
    ) -> dict[str, Any] | None:
        # 1. Resolve Astro Events
        events = []
        if evidence and hasattr(evidence, "metadata") and "astro_events" in evidence.metadata:
            events = evidence.metadata["astro_events"]
        elif engine_output is not None:
            # Fallback to engine_output
            core = _resolve_core_engine_output(engine_output)
            if hasattr(core, "events"):
                events = core.events

        if not events:
            return None

        # 2. Key Movements (Priority >= 50, max 5)
        key_movements = []
        significant_events = [e for e in events if getattr(e, "priority", 0) >= 50]
        significant_events.sort(key=lambda e: getattr(e, "priority", 0), reverse=True)

        for e in significant_events[:5]:
            key_movements.append(
                {
                    "planet": get_planet_name_fr(e.body),
                    "event_type": e.event_type,
                    "target": get_planet_name_fr(e.target) if e.target else None,
                    "orb_deg": round(e.orb_deg, 1) if hasattr(e, "orb_deg") else None,
                    "effect_label": get_effect_label(e.event_type),
                }
            )

        # 3. Activated Houses (max 3)
        activated_houses = []
        # Logical shortcut: houses are linked to internal categories.
        # We'll take top public domains and show their primary house significations.
        top_public = domain_ranking[:3]
        # In a real scenario, we'd query the domain_router weights.
        # For simplicity and AC compliance, we map public domains to representative houses.
        DOMAIN_TO_HOUSE = {
            "pro_ambition": 10,
            "relations_echanges": 7,
            "energie_bienetre": 1,
            "argent_ressources": 2,
            "vie_personnelle": 5,
        }
        seen_houses = set()
        for d in top_public:
            h_num = DOMAIN_TO_HOUSE.get(d["key"])
            if h_num and h_num not in seen_houses:
                sig = HOUSE_SIGNIFICATIONS[h_num]
                activated_houses.append(
                    {
                        "house_number": h_num,
                        "house_label": sig["label"],
                        "domain_label": sig["domain"],
                    }
                )
                seen_houses.add(h_num)

        # 4. Dominant Aspects (max 4)
        dominant_aspects = []
        aspect_events = [e for e in events if e.event_type == "aspect"]
        aspect_events.sort(key=lambda e: getattr(e, "orb_deg", 10.0))

        for e in aspect_events[:4]:
            dominant_aspects.append(
                {
                    "aspect_type": get_aspect_label(e.aspect),
                    "planet_a": get_planet_name_fr(e.body),
                    "planet_b": get_planet_name_fr(e.target) if e.target else None,
                    "tonality": get_aspect_tonality(e.aspect),
                    "effect_label": get_effect_label("aspect"),
                }
            )

        # 5. Headline & Bridge
        first_mvmt = key_movements[0]["planet"] if key_movements else "Le ciel"
        climate_label = day_climate.get("label", "cette journée").lower()
        headline = f"{first_mvmt} influence votre dynamique — {climate_label}."

        top_dom_label = domain_ranking[0]["label"].lower() if domain_ranking else "votre journée"
        interpretation_bridge = (
            f"La configuration céleste actuelle met l'accent sur {top_dom_label}, "
            "expliquant les opportunités identifiées."
        )

        return {
            "headline": headline,
            "key_movements": key_movements,
            "activated_houses": activated_houses,
            "dominant_aspects": dominant_aspects,
            "interpretation_bridge": interpretation_bridge,
        }


class PublicBestWindowPolicy:
    """
    Builds the best opportunity window for the day (Story 60.6).
    Selects the most favorable window and projects it for the public.
    """

    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        *,
        decision_windows: list[dict[str, Any]] | None,
        turning_points: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        if not decision_windows:
            return None

        # 1. Filter & Select (AC6: window_type="favorable", highest score)
        favorable = [dw for dw in decision_windows if dw.get("window_type") == "favorable"]
        if not favorable:
            return None

        # Sort by score descending, then confidence
        favorable.sort(key=lambda x: (x["score"], x.get("confidence", 0)), reverse=True)
        best = favorable[0]

        # 2. Build Public Object
        start = datetime.fromisoformat(best["start_local"])
        end = datetime.fromisoformat(best["end_local"])
        time_range = f"{start.strftime('%H:%M')}–{end.strftime('%H:%M')}"

        # Intensity-based label (AC2)
        try:
            intensity = float(best.get("intensity") or 10.0)
        except (TypeError, ValueError):
            intensity = 10.0
        label = "Moment favorable"
        if intensity >= 14.0:
            label = "Pic du jour"
        elif intensity >= 10.0:
            label = "Votre meilleur créneau"
        else:
            label = "Fenêtre d'opportunité"

        # Domain-based why and actions
        dominant = best.get("dominant_categories", [])
        primary_domain = None
        if dominant:
            primary_domain = map_internal_to_public(dominant[0])

        why = get_best_window_why(primary_domain)
        actions = get_recommended_actions(primary_domain)

        # Pivot detection (AC5)
        is_pivot = False
        if best.get("window_type") == "pivot":
            is_pivot = True
        else:
            # Check if any turning point falls inside
            s_wall = start.replace(tzinfo=None)
            e_wall = end.replace(tzinfo=None)
            for tp in turning_points:
                tp_time_str = tp.get("occurred_at_local")
                if not tp_time_str:
                    continue
                tp_time = datetime.fromisoformat(tp_time_str).replace(tzinfo=None)
                if s_wall <= tp_time < e_wall:
                    is_pivot = True
                    break

        return {
            "time_range": time_range,
            "label": label,
            "why": why,
            "recommended_actions": actions,
            "is_pivot": is_pivot,
        }


class PublicMainTurningPointPolicy:
    """
    Builds the main narrative turning point for the day (Story 60.5).
    Selects the most significant change and projects it for the public.
    """

    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        *,
        engine_output: Any | None = None,
        evidence: V3EvidencePack | None = None,
    ) -> dict[str, Any] | None:
        # 1. Resolve Turning Points
        raw_tps = []
        if evidence:
            raw_tps = evidence.turning_points
        else:
            core_output = _resolve_core_engine_output(engine_output)
            if core_output is not None:
                raw_tps = getattr(core_output, "turning_points", [])

        if not raw_tps:
            return None

        # 2. Filter & Sort (AC8: severity >= 0.3, confidence >= 0.5)
        significant = []
        for tp in raw_tps:
            severity = getattr(tp, "severity", getattr(tp, "amplitude", 0.0))
            confidence = getattr(tp, "confidence", 0.0)
            if float(severity) >= 0.3 and float(confidence) >= 0.5:
                significant.append(tp)

        if not significant:
            return None

        # Sort by severity descending, then time ascending (earliest wins on tie)
        def _sort_key(x: Any) -> tuple[float, Any]:
            sev = float(getattr(x, "severity", getattr(x, "amplitude", 0.0)))
            return (-sev, x.local_time)

        significant.sort(key=_sort_key)
        best = significant[0]

        # 3. Project for Public
        change_type = getattr(best, "change_type", "recomposition")
        impacted = (
            getattr(best, "categories_impacted", None)
            or getattr(best, "impacted_categories", None)
            or getattr(best, "themes", None)
            or []
        )

        affected_domains = self._map_domains(impacted)
        primary_domain = affected_domains[0] if affected_domains else None

        title = get_turning_point_title(change_type, primary_domain)
        do_hint, avoid_hint = get_do_avoid(change_type, primary_domain)

        what_changes = self._build_what_changes(best, primary_domain)

        return {
            "time": best.local_time.strftime("%H:%M"),
            "title": title,
            "change_type": change_type,
            "affected_domains": affected_domains,
            "what_changes": what_changes,
            "do": do_hint,
            "avoid": avoid_hint,
        }

    def _map_domains(self, internal_themes: list[str]) -> list[str]:
        public_keys = []
        for code in internal_themes:
            pk = map_internal_to_public(code)
            if pk and pk not in public_keys:
                public_keys.append(pk)
        return public_keys[:3]

    def _build_what_changes(self, tp: Any, primary_domain: str | None) -> str:
        change_type = getattr(tp, "change_type", "recomposition")
        from app.prediction.public_domain_taxonomy import PUBLIC_DOMAINS

        domain_label = (
            PUBLIC_DOMAINS[primary_domain].label_fr.lower()
            if primary_domain in PUBLIC_DOMAINS
            else "votre focus"
        )

        if change_type == "emergence":
            return f"L'énergie monte et {domain_label} devient prioritaire."
        if change_type == "recomposition":
            return f"Le focus de votre journée se déplace vers {domain_label}."
        if change_type == "attenuation":
            return "La tension retombe et laisse place à une phase d'intégration."

        summary = getattr(tp, "summary", None)
        if isinstance(summary, str) and "theme_rotation" not in summary:
            return summary
        return "Changement de dynamique dans votre journée."


PERIOD_SLOTS = [
    {"key": "nuit", "hour_start": 22, "hour_end": 6, "default_regime": "récupération"},
    {"key": "matin", "hour_start": 6, "hour_end": 12, "default_regime": "mise_en_route"},
    {"key": "apres_midi", "hour_start": 12, "hour_end": 18, "default_regime": "fluidité"},
    {"key": "soiree", "hour_start": 18, "hour_end": 22, "default_regime": "recentrage"},
]


class PublicTimeWindowPolicy:
    """
    Builds the narrative time windows for the day (Story 60.14).
    Produces 4 fixed periods (Night, Morning, Afternoon, Evening).
    """

    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        turning_points: list[dict[str, Any]],
        *,
        engine_output: Any | None = None,
        evidence: V3EvidencePack | None = None,
    ) -> list[dict[str, Any]]:
        from collections import Counter

        # 0. Resolve Astro Events for per-period enrichment
        all_events = self._resolve_events(evidence, engine_output, snapshot)

        # 1. Resolve Time Blocks (V3)
        v3_blocks = []
        if evidence:
            v3_blocks = evidence.time_windows
        else:
            core_output = _resolve_core_engine_output(engine_output)
            if core_output is not None:
                v3_blocks = getattr(core_output, "time_blocks", [])

        # 2. Build 4 Windows
        windows = []
        l_date = snapshot.local_date
        if isinstance(l_date, datetime):
            l_date = l_date.date()

        for slot in PERIOD_SLOTS:
            key = slot["key"]
            h_start = slot["hour_start"]
            h_end = slot["hour_end"]

            # A. Filter blocks whose start falls in the period
            slot_blocks = []
            for b in v3_blocks:
                start = getattr(b, "start_local", None) or getattr(b, "start_at_local", None)
                if start is None:
                    continue

                if h_start < h_end:
                    is_in_slot = h_start <= start.hour < h_end
                else:  # Overnight (22 to 6)
                    is_in_slot = start.hour >= h_start or start.hour < h_end

                if is_in_slot:
                    slot_blocks.append(b)

            # B. Aggregate Orientation (Mode)
            orientation = "stable"
            if slot_blocks:
                orientations = [getattr(b, "orientation", "stable") for b in slot_blocks]
                counts = Counter(orientations)
                orientation = counts.most_common(1)[0][0]

            # C. Aggregate Themes
            all_themes = []
            for b in slot_blocks:
                themes = getattr(b, "dominant_themes", []) or getattr(b, "themes", [])
                all_themes.extend(themes)

            theme_counts = Counter(all_themes)
            top_internal_themes = [t for t, c in theme_counts.most_common(5)]
            top_domains = self._map_domains(top_internal_themes)

            # D. Resolve Regime
            rep_end = datetime.combine(l_date, time(h_end % 24, 0))
            if h_start < h_end:
                # Normal slot: use actual start so TPs in the first half are detected
                rep_start = datetime.combine(l_date, time(h_start, 0))
            else:
                # Overnight slot (nuit 22→06): keep midpoint to stay within same date
                # and to trigger the 0–5h night-recovery check in _resolve_regime
                duration = (h_end - h_start) % 24
                mid_hour = (h_start + duration // 2) % 24
                rep_start = datetime.combine(l_date, time(mid_hour, 0))

            regime = self._resolve_regime(rep_start, rep_end, orientation, turning_points)

            # E. Default Fallback
            if not slot_blocks and regime == "fluidité":
                regime = slot["default_regime"]

            # F. Label & Action
            label = get_regime_label(regime)
            action_hint = get_action_hint(regime)

            # G. Astrological events in this period (sorted by priority, max 3)
            slot_events = self._filter_events_in_period(all_events, h_start, h_end)
            slot_events.sort(key=lambda ev: getattr(ev, "priority", 0), reverse=True)
            astro_events: list[str] = []
            seen_texts: set[str] = set()
            for ev in slot_events:
                text = self._format_event_text(ev)
                if text and text not in seen_texts:
                    astro_events.append(text)
                    seen_texts.add(text)
                    if len(astro_events) >= 3:
                        break

            windows.append(
                {
                    "period_key": key,
                    "time_range": f"{h_start:02d}:00–{h_end:02d}:00",
                    "label": label,
                    "regime": regime,
                    "top_domains": top_domains,
                    "action_hint": action_hint,
                    "astro_events": astro_events,
                }
            )

        return windows

    def _resolve_regime(
        self, start: datetime, end: datetime, orientation: str, turning_points: list[dict[str, Any]]
    ) -> str:
        # Priority 1: Pivot if turning point inside
        for tp in turning_points:
            tp_time_str = tp.get("occurred_at_local")
            if not tp_time_str:
                continue
            tp_time = datetime.fromisoformat(tp_time_str).replace(tzinfo=None)
            s_wall = start.replace(tzinfo=None)
            e_wall = end.replace(tzinfo=None)
            if s_wall <= tp_time < e_wall:
                return "pivot"

        # Priority 2: Recovery for night
        hour_start = start.hour
        if 0 <= hour_start <= 5:
            return "récupération"

        # Priority 3: Orientation mapping
        ORIENTATION_TO_REGIME = {
            "rising": "progression",
            "falling": "retombée",
            "volatile": "prudence",
            "stable": "fluidité",
        }
        regime = ORIENTATION_TO_REGIME.get(orientation, "fluidité")

        # Special cases based on time
        if regime == "fluidité" and 6 <= hour_start <= 9:
            return "mise_en_route"

        hour_end = end.hour
        if regime in ("fluidité", "retombée") and 21 <= hour_end <= 23:
            return "recentrage"

        return regime

    def _resolve_events(
        self, evidence: Any, engine_output: Any, snapshot: Any | None = None
    ) -> list[Any]:
        events: list[Any] = []
        if evidence and hasattr(evidence, "metadata") and "astro_events" in evidence.metadata:
            events = evidence.metadata["astro_events"]
        elif engine_output is not None:
            core = _resolve_core_engine_output(engine_output)
            if core is not None:
                events = (
                    getattr(core, "events", None) or getattr(core, "detected_events", None) or []
                )

        # Fallback for cached predictions: load from persisted v3_metrics
        if not events and snapshot is not None:
            v3_metrics = getattr(snapshot, "v3_metrics", None)
            if isinstance(v3_metrics, dict):
                raw_events = v3_metrics.get("detected_events", [])
                if raw_events:
                    from types import SimpleNamespace

                    events = [
                        SimpleNamespace(**e) if isinstance(e, dict) else e for e in raw_events
                    ]

        return events

    def _filter_events_in_period(self, events: list[Any], h_start: int, h_end: int) -> list[Any]:
        result = []
        for e in events:
            dt = getattr(e, "local_time", None) or getattr(e, "occurred_at_local", None)
            if dt is None:
                continue
            if isinstance(dt, str):
                try:
                    dt = datetime.fromisoformat(dt)
                except ValueError:
                    continue
            h = dt.hour
            in_period = (h_start <= h < h_end) if h_start < h_end else (h >= h_start or h < h_end)
            if in_period:
                result.append(e)
        return result

    def _format_event_text(self, e: Any) -> str | None:
        ev_type = getattr(e, "event_type", None)
        body = getattr(e, "body", None)
        target = getattr(e, "target", None)
        aspect = getattr(e, "aspect", None)

        if ev_type == "solar_return":
            return "Retour Solaire"
        if ev_type == "lunar_return":
            return "Retour Lunaire"
        if ev_type == "moon_sign_ingress" and body and target:
            planet = get_planet_name_fr(body)
            sign = get_sign_name_fr(target)
            dt = getattr(e, "local_time", None) or getattr(e, "occurred_at_local", None)
            if isinstance(dt, str):
                try:
                    dt = datetime.fromisoformat(dt)
                except ValueError:
                    dt = None
            time_str = f" ({dt.strftime('%H:%M')})" if dt else ""
            return f"{planet} → {sign}{time_str}"
        if ev_type == "fixed_star_conjunction" and body and target:
            return f"{get_planet_name_fr(body)} ☌ {get_fixed_star_name_fr(target)}"
        if ev_type == "node_conjunction" and body and target:
            return f"{get_planet_name_fr(body)} ☌ {get_planet_name_fr(target)}"
        if ev_type == "progression_aspect" and body and aspect and target:
            label = get_aspect_label(aspect)
            return f"{get_planet_name_fr(body)} {label} {get_planet_name_fr(target)} (progressé)"
        if ev_type == "sky_aspect" and body and aspect and target:
            label = get_aspect_label(aspect)
            p1 = get_planet_name_fr(body)
            p2 = get_planet_name_fr(target)
            return f"{p1} {label} {p2}"
        if (
            ev_type
            in {
                "aspect",
                "aspect_exact_to_angle",
                "aspect_exact_to_luminary",
                "aspect_exact_to_personal",
            }
            and body
            and aspect
            and target
            and body != target
        ):
            label = get_aspect_label(aspect)
            p1 = get_planet_name_fr(body)
            p2 = get_planet_name_fr(target)
            return f"{p1} {label} {p2}"
        if ev_type == "transit_to_natal" and body and aspect and target:
            label = get_aspect_label(aspect)
            return f"{get_planet_name_fr(body)} {label} {get_planet_name_fr(target)} natal"
        return None

    def _map_domains(self, internal_themes: list[str]) -> list[str]:
        public_keys = []
        for code in internal_themes:
            pk = map_internal_to_public(code)
            if pk and pk not in public_keys:
                public_keys.append(pk)
        return public_keys[:2]


class PublicDayClimatePolicy:
    """
    Builds the hero climate summary for the day (Story 60.3).
    Separates global climate narration from domain ranking.
    """

    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        domain_ranking: list[dict[str, Any]],
        decision_windows: list[dict[str, Any]] | None,
        evidence: V3EvidencePack | None = None,
    ) -> dict[str, Any]:
        # 1. Resolve Tone
        tone = snapshot.overall_tone or "neutral"
        if evidence:
            tone = (
                evidence.day_profile.get("overall_tone") or evidence.day_profile.get("tone") or tone
            )

        # 2. Resolve Intensity & Stability (normalized 0-10)
        intensity = 5.0  # nominal
        stability = 5.0  # nominal

        if evidence and evidence.themes:
            # Try to get from day_profile
            avg_i = evidence.day_profile.get("avg_intensity") or evidence.day_profile.get(
                "intensity"
            )
            avg_s = evidence.day_profile.get("avg_stability") or evidence.day_profile.get(
                "stability"
            )

            if avg_i is None:
                avg_i = sum(t.intensity for t in evidence.themes.values()) / len(evidence.themes)
            if avg_s is None:
                avg_s = sum(t.stability for t in evidence.themes.values()) / len(evidence.themes)

            intensity = round(avg_i / 2.0, 1)
            stability = round(avg_s / 2.0, 1)
        else:
            # Fallback values based on tone if no V3 evidence
            tone_map = {
                "positive": (6.5, 7.5),
                "mixed": (7.0, 4.0),
                "neutral": (4.0, 8.0),
                "negative": (7.5, 3.5),
            }
            intensity, stability = tone_map.get(tone, (5.0, 5.0))

        # 3. Label from catalog
        label = get_climate_label(tone, intensity)

        # 4. Top Domains (top 3, keeping ties with the third score)
        sorted_domains = sorted(
            domain_ranking,
            key=lambda item: (-float(item.get("score_10", 0.0)), int(item.get("display_order", 99))),
        )
        if len(sorted_domains) <= 3:
            top_domains = [d["key"] for d in sorted_domains]
        else:
            third_score = float(sorted_domains[2].get("score_10", 0.0))
            top_domains = [
                d["key"] for d in sorted_domains if float(d.get("score_10", 0.0)) >= third_score
            ][:4]

        # 5. Watchout (weakest domain if score < 5.0)
        watchout = None
        if domain_ranking:
            weakest = min(domain_ranking, key=lambda item: float(item.get("score_10", 0.0)))
            if weakest["score_10"] < 5.0:
                watchout = weakest["key"]

        # 6. Best window reference
        best_window_ref = None
        if decision_windows:
            # Filter for favorable windows
            fav = [w for w in decision_windows if w["window_type"] == "favorable"]
            if fav:
                # Sort by score then confidence
                fav.sort(key=lambda w: (w["score"], w["confidence"]), reverse=True)
                best = fav[0]
                start = datetime.fromisoformat(best["start_local"])
                end = datetime.fromisoformat(best["end_local"])
                best_window_ref = f"{start.strftime('%H:%M')}–{end.strftime('%H:%M')}"

        # 7. Short synthetic summary
        summary = self._build_short_summary(tone, top_domains, label)

        return {
            "label": label,
            "tone": tone,
            "intensity": intensity,
            "stability": stability,
            "summary": summary,
            "top_domains": top_domains,
            "watchout": watchout,
            "best_window_ref": best_window_ref,
        }

    def _build_short_summary(self, tone: str, top_domains: list[str], label: str) -> str:
        if not top_domains:
            return f"{label}."

        # Map keys to readable names (FR)
        from app.prediction.public_domain_taxonomy import PUBLIC_DOMAINS

        names = [PUBLIC_DOMAINS[k].label_fr.lower() for k in top_domains if k in PUBLIC_DOMAINS]
        joined_names = self._join_domain_names(names)

        if tone == "positive":
            return f"{label} avec un bel accent sur {joined_names}."
        if tone == "mixed":
            return f"{label}, contrastant entre {joined_names}."
        if tone == "negative":
            return f"{label}, vigilance requise sur {joined_names}."

        return f"{label}, focus sur {joined_names}."

    def _join_domain_names(self, names: list[str]) -> str:
        if not names:
            return ""
        if len(names) == 1:
            return names[0]
        if len(names) == 2:
            return f"{names[0]} et {names[1]}"
        return f"{', '.join(names[:-1])} et {names[-1]}"


class PublicDomainRankingPolicy:
    """
    Builds the public domain ranking by aggregating internal category scores.
    AC: Fusion of 12 internal domains into 5 public ones.
    Rule: Take the max() score for each public domain.
    """

    def build(self, internal_categories: list[dict[str, Any]]) -> list[dict[str, Any]]:
        internal_scores = {
            c["code"]: c["score_20"] if c.get("score_20") is not None else c["note_20"]
            for c in internal_categories
        }
        aggregated = aggregate_public_domain_score(internal_scores)

        public_scores = []
        for key in DISPLAY_ORDER:
            entry = PUBLIC_DOMAINS[key]
            note_20 = aggregated.get(key)
            if note_20 is None:
                continue

            score_10 = to_score_10(note_20)
            level = to_level(score_10)

            public_scores.append(
                PublicDomainScore(
                    key=key,
                    label=entry.label_fr,
                    score_10=score_10,
                    level=level,
                    rank=99,  # Placeholder
                    note_20_internal=note_20,
                    internal_codes=entry.internal_codes,
                    display_order=entry.display_order,
                    signal_label=None,
                )
            )

        # Rank domains
        ranked = rank_domains(public_scores)

        # Convert back to dict for API (and re-sort by display_order for fixed UI order)
        as_dict = [
            {
                "key": d.key,
                "label": d.label,
                "internal_codes": d.internal_codes,
                "display_order": d.display_order,
                "score_10": d.score_10,
                "level": d.level,
                "rank": d.rank,
                "note_20_internal": d.note_20_internal,
                "signal_label": d.signal_label,
            }
            for d in ranked
        ]
        return sorted(as_dict, key=lambda x: x["display_order"])


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
                        "note_20": round(theme.score_20, 1),
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
        if evidence:
            return [
                {
                    "occurred_at_local": tp.local_time.isoformat(),
                    "severity": tp.amplitude / 10.0,  # Scaled
                    "summary": self._build_public_turning_point_summary(tp),
                    "drivers": [{"label": d} for d in tp.drivers],
                    "impacted_categories": list(tp.themes),
                    # Story 43.1
                    "change_type": tp.change_type,
                    "previous_categories": tp.previous_categories,
                    "next_categories": tp.next_categories,
                    "primary_driver": self._serialize_primary_driver(tp.primary_driver),
                    # Story 44.1
                    "movement": self._serialize_movement(tp.movement),
                    "category_deltas": [
                        self._serialize_category_delta(cd) for cd in tp.category_deltas
                    ],
                }
                for tp in evidence.turning_points
            ]

        if is_flat_day:
            return []

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

    def _build_public_turning_point_summary(self, tp: Any) -> str:
        change_type = getattr(tp, "change_type", "recomposition")
        if change_type == "emergence":
            return "Une dynamique prend clairement de l'ampleur."
        if change_type == "attenuation":
            return "L'intensité retombe et laisse plus d'espace pour intégrer."
        return "La journée change d'axe et demande un nouvel ajustement."

    def _serialize_primary_driver(self, pd: Any | None) -> dict[str, Any] | None:
        if not pd:
            return None
        return {
            "event_type": pd.event_type,
            "body": pd.body,
            "target": pd.target,
            "aspect": pd.aspect,
            "orb_deg": float(pd.orb_deg) if pd.orb_deg is not None else None,
            "phase": pd.phase,
            "priority": pd.priority,
            "base_weight": float(pd.base_weight) if pd.base_weight is not None else None,
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
                theme.code for theme in sorted(sorted_themes, key=lambda item: item.score_20)[:2]
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
                orb_deg=(float(pd_raw["orb_deg"]) if pd_raw.get("orb_deg") is not None else None),
                phase=pd_raw.get("phase"),
                priority=pd_raw.get("priority"),
                base_weight=(
                    float(pd_raw["base_weight"]) if pd_raw.get("base_weight") is not None else None
                ),
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

    generated_at_raw = payload.get("generated_at")
    generated_at = datetime.fromisoformat(generated_at_raw) if generated_at_raw else datetime.now()

    return V3EvidencePack(
        version=payload.get("version", "unknown"),
        generated_at=generated_at,
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

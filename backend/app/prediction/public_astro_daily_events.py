from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from app.prediction.public_astro_vocabulary import (
    get_aspect_label,
    get_fixed_star_name_fr,
    get_planet_name_fr,
    get_sign_name_fr,
)

if TYPE_CHECKING:
    from .persisted_snapshot import PersistedPredictionSnapshot
    from .schemas import V3EvidencePack


class PublicAstroDailyEventsPolicy:
    """
    Builds the factual astro daily events module (Story 60.13).
    Extracts ingresses, aspects and planet positions without interpretation.
    """

    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        *,
        engine_output: Any | None = None,
        evidence: V3EvidencePack | None = None,
    ) -> dict[str, Any] | None:
        # 1. Resolve Astro Events
        events = self._resolve_astro_events(evidence, engine_output)

        # 2. Extract Ingresses
        ingresses = []
        for e in events:
            if getattr(e, "event_type", None) == "moon_sign_ingress" and getattr(e, "target", None):
                text = f"{get_planet_name_fr(e.body)} entre en {get_sign_name_fr(e.target)}"
                time = None
                # Check for occurred_at_local (datetime or string)
                dt = getattr(e, "occurred_at_local", None) or getattr(e, "local_time", None)
                if dt:
                    if isinstance(dt, str):
                        dt = datetime.fromisoformat(dt)
                    time = dt.strftime("%H:%M")

                ingresses.append({"text": text, "time": time})

        # 3. Extract Aspects (max 4)
        aspects = []
        # AC1: "aspects exacts du jour" (max 4)
        # Using same event types as PUBLIC_PIVOT_EVENT_TYPES in public_projection.py
        aspect_event_types = {
            "aspect",
            "aspect_exact_to_angle",
            "aspect_exact_to_luminary",
            "aspect_exact_to_personal",
        }
        aspect_events = [
            e
            for e in events
            if getattr(e, "event_type", None) in aspect_event_types
            and getattr(e, "target", None)
            and getattr(e, "body", None) != getattr(e, "target", None)  # exclude self-aspects
        ]

        # Sort by priority or proximity if available
        aspect_events.sort(key=lambda e: getattr(e, "priority", 0), reverse=True)

        seen_aspects = set()
        for e in aspect_events:
            aspect_label = get_aspect_label(e.aspect)
            planet_a = get_planet_name_fr(e.body)
            planet_b = get_planet_name_fr(e.target)
            aspect_text = f"{planet_a} {aspect_label} {planet_b}"

            if aspect_text not in seen_aspects:
                aspects.append(aspect_text)
                seen_aspects.add(aspect_text)
                if len(aspects) >= 4:
                    break

        # 4. Extract Planet Positions (Slow planets: Soleil, Lune, Mercure, Vénus, Mars)
        # AC3: positions from transit events or snapshot sign fields
        planet_positions = self._extract_planet_positions(snapshot, events, evidence)

        # 5. Story 60.15 Enriched Events
        returns = self._extract_returns(events)
        progressions = self._extract_progressions(events)
        nodes = self._extract_nodes(events)
        sky_aspects = self._extract_sky_aspects(events)
        fixed_stars = self._extract_fixed_stars(events)

        if (
            not ingresses
            and not aspects
            and not planet_positions
            and not returns
            and not progressions
            and not nodes
            and not sky_aspects
            and not fixed_stars
        ):
            return None

        result: dict[str, Any] = {
            "ingresses": ingresses,
            "aspects": aspects,
        }
        if planet_positions:
            result["planet_positions"] = planet_positions
        if returns:
            result["returns"] = returns
        if progressions:
            result["progressions"] = progressions
        if nodes:
            result["nodes"] = nodes
        if sky_aspects:
            result["sky_aspects"] = sky_aspects
        if fixed_stars:
            result["fixed_stars"] = fixed_stars

        return result

    def _extract_returns(self, events: list[Any]) -> list[str]:
        # AC7: Retours (Solaire/Lunaire)
        found = []
        for e in events:
            ev_type = getattr(e, "event_type", None)
            if ev_type == "solar_return":
                found.append("Retour Solaire (votre anniversaire astrologique)")
            elif ev_type == "lunar_return":
                found.append("Retour Lunaire (la Lune retrouve sa place natale)")
        return found

    def _extract_progressions(self, events: list[Any]) -> list[str]:
        # AC9: Progressions Secondaires
        found = []
        for e in events:
            if getattr(e, "event_type", None) == "progression_aspect":
                p_name = get_planet_name_fr(e.body)
                asp_label = get_aspect_label(e.aspect)
                target_name = get_planet_name_fr(e.target)
                found.append(f"{p_name} {asp_label} {target_name} (progression)")
        return found

    def _extract_nodes(self, events: list[Any]) -> list[str]:
        # AC10: Nœuds Lunaires
        found = []
        for e in events:
            if getattr(e, "event_type", None) == "node_conjunction":
                p_name = get_planet_name_fr(e.body)
                target_name = get_planet_name_fr(e.target)
                # Formatter: "Planète Conjonction Nœud" ou "Nœud Conjonction Planète"
                found.append(f"{p_name} Conjonction {target_name}")
        return found

    def _extract_sky_aspects(self, events: list[Any]) -> list[str]:
        # AC11: Aspects du Ciel (Sky-to-Sky)
        found = []
        for e in events:
            if getattr(e, "event_type", None) == "sky_aspect":
                p1 = get_planet_name_fr(e.body)
                asp = get_aspect_label(e.aspect)
                p2 = get_planet_name_fr(e.target)
                found.append(f"{p1} {asp} {p2}")
        return found

    def _extract_fixed_stars(self, events: list[Any]) -> list[str]:
        # AC12: Étoiles Fixes
        found = []
        for e in events:
            if getattr(e, "event_type", None) == "fixed_star_conjunction":
                p_name = get_planet_name_fr(e.body)
                star_name = get_fixed_star_name_fr(e.target)
                found.append(f"{p_name} conjoint à l'étoile {star_name}")
        return found

    def _resolve_astro_events(
        self, evidence: V3EvidencePack | None, engine_output: Any | None
    ) -> list[Any]:
        events = []
        if evidence and hasattr(evidence, "metadata") and "astro_events" in evidence.metadata:
            events = evidence.metadata["astro_events"]
        elif engine_output is not None:
            # Resolve events from engine output (avoid circular imports)
            core = getattr(engine_output, "core", engine_output)
            if hasattr(core, "events"):
                events = core.events
            elif hasattr(core, "detected_events"):
                events = core.detected_events
        return events

    def _extract_planet_positions(
        self,
        snapshot: PersistedPredictionSnapshot,
        events: list[Any],
        evidence: V3EvidencePack | None,
    ) -> list[str] | None:
        # Lentes selon AC: Soleil, Lune, Mercure, Vénus, Mars
        targets = {"sun", "moon", "mercury", "venus", "mars"}
        positions: dict[str, str] = {}

        # 1. Try from evidence metadata if present
        if evidence and "planet_positions" in evidence.metadata:
            raw_pos = evidence.metadata["planet_positions"]
            if isinstance(raw_pos, dict):
                for p, sign in raw_pos.items():
                    if p in targets:
                        positions[p] = f"{get_planet_name_fr(p)} en {get_sign_name_fr(sign)}"

        # 2. Try from events (transit_to_natal often carry sign info)
        if not positions or len(positions) < len(targets):
            for e in events:
                if getattr(e, "event_type", None) == "transit_to_natal" and e.body in targets:
                    meta = getattr(e, "metadata", None)
                    sign = getattr(e, "body_sign", None) or (
                        meta.get("body_sign") if isinstance(meta, dict) else None
                    )
                    if sign and e.body not in positions:
                        label = f"{get_planet_name_fr(e.body)} en {get_sign_name_fr(sign)}"
                        positions[e.body] = label

        # 3. Try from snapshot v3_metrics if available
        if (
            (not positions or len(positions) < len(targets))
            and snapshot is not None
            and snapshot.v3_metrics
        ):
            v3_pos = snapshot.v3_metrics.get("planet_positions")
            if isinstance(v3_pos, dict):
                for p, sign in v3_pos.items():
                    if p in targets and p not in positions:
                        positions[p] = f"{get_planet_name_fr(p)} en {get_sign_name_fr(sign)}"

        if not positions:
            return None

        # Return in specific order
        ordered = []
        for p in ["sun", "moon", "mercury", "venus", "mars"]:
            if p in positions:
                ordered.append(positions[p])

        return ordered if ordered else None

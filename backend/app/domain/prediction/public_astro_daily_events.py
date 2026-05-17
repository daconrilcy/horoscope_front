"""Expose les evenements astrologiques publics depuis les sources canoniques."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from app.domain.astrology.planet_catalog import planet_codes
from app.domain.prediction.astro_label_formatter import AstroLabelFormatter

if TYPE_CHECKING:
    from .persisted_snapshot import PersistedPredictionSnapshot
    from .schemas import V3EvidencePack

PUBLIC_ASTRO_ASPECT_EVENT_TYPES = frozenset(
    {
        "aspect",
        "aspect_exact_to_angle",
        "aspect_exact_to_luminary",
        "aspect_exact_to_personal",
    }
)
PUBLIC_POSITION_PLANET_CODES = frozenset(planet_codes()[:5])
PUBLIC_POSITION_PLANET_ORDER = planet_codes()[:5]


def resolve_public_astro_events(
    evidence: V3EvidencePack | None,
    engine_output: Any | None,
    snapshot: Any | None = None,
) -> list[Any]:
    """Retourne les evenements astro publics depuis les sources auditees."""
    events: list[Any] = []
    if evidence and hasattr(evidence, "metadata") and "astro_events" in evidence.metadata:
        events = evidence.metadata["astro_events"]
    elif engine_output is not None:
        core = getattr(engine_output, "core", engine_output)
        if core is not None:
            events = getattr(core, "events", None) or getattr(core, "detected_events", None) or []

    if not events and snapshot is not None:
        v3_metrics = getattr(snapshot, "v3_metrics", None)
        if isinstance(v3_metrics, dict):
            raw_events = v3_metrics.get("detected_events", [])
            if raw_events:
                events = [
                    SimpleNamespace(**event) if isinstance(event, dict) else event
                    for event in raw_events
                ]

    return events


class PublicAstroDailyEventsPolicy:
    """Construit le module factuel des evenements astrologiques quotidiens."""

    def build(
        self,
        snapshot: PersistedPredictionSnapshot,
        *,
        astro_vocabulary: AstroLabelFormatter,
        engine_output: Any | None = None,
        evidence: V3EvidencePack | None = None,
    ) -> dict[str, Any] | None:
        vocabulary = astro_vocabulary
        # 1. Resolve Astro Events
        events = resolve_public_astro_events(evidence, engine_output, snapshot)

        # 2. Extract Ingresses
        ingresses = []
        for e in events:
            if getattr(e, "event_type", None) == "moon_sign_ingress" and getattr(e, "target", None):
                text = f"{vocabulary.planet(e.body)} entre en {vocabulary.sign(e.target)}"
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
        aspect_events = [
            e
            for e in events
            if getattr(e, "event_type", None) in PUBLIC_ASTRO_ASPECT_EVENT_TYPES
            and getattr(e, "target", None)
            and getattr(e, "body", None) != getattr(e, "target", None)  # exclude self-aspects
        ]

        # Sort by priority or proximity if available
        aspect_events.sort(key=lambda e: getattr(e, "priority", 0), reverse=True)

        seen_aspects = set()
        for e in aspect_events:
            aspect_label = vocabulary.aspect(e.aspect)
            planet_a = vocabulary.planet(e.body)
            planet_b = vocabulary.planet(e.target)
            aspect_text = f"{planet_a} {aspect_label} {planet_b}"

            if aspect_text not in seen_aspects:
                aspects.append(aspect_text)
                seen_aspects.add(aspect_text)
                if len(aspects) >= 4:
                    break

        # 4. Extract Planet Positions
        # AC3: positions from transit events or snapshot sign fields
        planet_positions = self._extract_planet_positions(snapshot, events, evidence, vocabulary)

        # 5. Story 60.15 Enriched Events
        returns = self._extract_returns(events)
        progressions = self._extract_progressions(events, vocabulary)
        nodes = self._extract_nodes(events, vocabulary)
        sky_aspects = self._extract_sky_aspects(events, vocabulary)
        fixed_stars = self._extract_fixed_stars(events, vocabulary)

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

    def _extract_progressions(
        self, events: list[Any], vocabulary: AstroLabelFormatter
    ) -> list[str]:
        # AC9: Progressions Secondaires
        found = []
        for e in events:
            if getattr(e, "event_type", None) == "progression_aspect":
                p_name = vocabulary.planet(e.body)
                asp_label = vocabulary.aspect(e.aspect)
                target_name = vocabulary.planet(e.target)
                found.append(f"{p_name} {asp_label} {target_name} (progression)")
        return found

    def _extract_nodes(self, events: list[Any], vocabulary: AstroLabelFormatter) -> list[str]:
        # AC10: Nœuds Lunaires
        found = []
        for e in events:
            if getattr(e, "event_type", None) == "node_conjunction":
                p_name = vocabulary.planet(e.body)
                target_name = vocabulary.planet(e.target)
                conjunction = vocabulary.aspect("conjunction")
                found.append(f"{p_name} {conjunction} {target_name}")
        return found

    def _extract_sky_aspects(self, events: list[Any], vocabulary: AstroLabelFormatter) -> list[str]:
        # AC11: Aspects du Ciel (Sky-to-Sky)
        found = []
        for e in events:
            if getattr(e, "event_type", None) == "sky_aspect":
                p1 = vocabulary.planet(e.body)
                asp = vocabulary.aspect(e.aspect)
                p2 = vocabulary.planet(e.target)
                found.append(f"{p1} {asp} {p2}")
        return found

    def _extract_fixed_stars(self, events: list[Any], vocabulary: AstroLabelFormatter) -> list[str]:
        # AC12: Étoiles Fixes
        found = []
        for e in events:
            if getattr(e, "event_type", None) == "fixed_star_conjunction":
                p_name = vocabulary.planet(e.body)
                star_name = self._resolve_fixed_star_name(e)
                found.append(f"{p_name} conjoint à l'étoile {star_name}")
        return found

    def _resolve_fixed_star_name(self, event: Any) -> str:
        """Lit le nom d'étoile déjà porté par l'événement enrichi."""
        metadata = getattr(event, "metadata", None)
        if isinstance(metadata, dict):
            display_name = str(metadata.get("star_display_name") or "").strip()
            if display_name:
                return display_name
        return str(getattr(event, "target", "") or "").strip()

    def _resolve_astro_events(
        self,
        evidence: V3EvidencePack | None,
        engine_output: Any | None,
        snapshot: Any | None = None,
    ) -> list[Any]:
        return resolve_public_astro_events(evidence, engine_output, snapshot)

    def _extract_planet_positions(
        self,
        snapshot: PersistedPredictionSnapshot,
        events: list[Any],
        evidence: V3EvidencePack | None,
        vocabulary: AstroLabelFormatter,
    ) -> list[str] | None:
        targets = PUBLIC_POSITION_PLANET_CODES
        positions: dict[str, str] = {}

        # 1. Try from evidence metadata if present
        if evidence and "planet_positions" in evidence.metadata:
            raw_pos = evidence.metadata["planet_positions"]
            if isinstance(raw_pos, dict):
                for p, sign in raw_pos.items():
                    if p in targets:
                        positions[p] = f"{vocabulary.planet(p)} en {vocabulary.sign(sign)}"

        # 2. Try from events (transit_to_natal often carry sign info)
        if not positions or len(positions) < len(targets):
            for e in events:
                if getattr(e, "event_type", None) == "transit_to_natal" and e.body in targets:
                    meta = getattr(e, "metadata", None)
                    sign = getattr(e, "body_sign", None) or (
                        meta.get("body_sign") if isinstance(meta, dict) else None
                    )
                    if sign and e.body not in positions:
                        label = f"{vocabulary.planet(e.body)} en {vocabulary.sign(sign)}"
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
                        positions[p] = f"{vocabulary.planet(p)} en {vocabulary.sign(sign)}"

        if not positions:
            return None

        # Return in specific order
        ordered = []
        for p in PUBLIC_POSITION_PLANET_ORDER:
            if p in positions:
                ordered.append(positions[p])

        return ordered if ordered else None

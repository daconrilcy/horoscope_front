# Assemblage client-safe de la projection transit publique.
"""Construit la projection transit client par plan sans exposer le runtime brut."""

from __future__ import annotations

from app.domain.astrology.projections.projection_hash import compute_projection_hash
from app.services.api_contracts.public.transit_projection import (
    TransitProjectionContent,
    TransitProjectionFact,
    TransitProjectionResponse,
)

_PLAN_ORDER: dict[str, int] = {"free": 0, "basic": 1, "premium": 2}

_SECTIONS_BY_PLAN: dict[str, dict[str, str]] = {
    "free": {
        "orientation_generale": "Lecture courte des transits actifs.",
        "periode_active_simplifiee": "Fenetre large exprimee sans detail technique.",
        "theme_du_moment": "Theme dominant formule pour un usage client.",
        "limite_de_lecture": "Projection limitee aux faits valides.",
    },
    "basic": {
        "fenetres_de_timing": "Fenetre de timing vulgarisee lorsque la preuve le permet.",
        "transits_principaux_vulgarises": "Transits dominants reformules sans objet runtime.",
        "conseil_pratique": "Conseil d'action non technique.",
        "points_de_vigilance": "Points de vigilance exprimes sans diagnostic interne.",
    },
    "premium": {
        "sequence_temporelle": "Sequence client plus detaillee avec limites affichees.",
        "nuances_et_arbitrages": "Nuances narratives issues des faits prepares.",
        "priorites_d_action": "Priorites d'action formulees pour le client.",
        "lecture_des_cycles": "Lecture des cycles sans preuve interne brute.",
        "limites_explicites": "Limites de doctrine et de donnees affichees sans payload interne.",
    },
}


class TransitClientProjectionService:
    """Assemble une projection transit stable selon le plan autorisé."""

    def build(
        self,
        *,
        plan_code: str,
        proof_refs: tuple[str, ...],
        degraded_reason: str | None = None,
    ) -> TransitProjectionResponse:
        """Retourne le payload client-safe autorisé pour le plan demandé."""
        normalized_plan = _normalize_plan(plan_code)
        sections = _sections_for_plan(normalized_plan)
        status = "degraded" if degraded_reason else "available"
        payload_for_hash = {
            "projection_id": "transit_client_projection_v1",
            "status": status,
            "plan_code": normalized_plan,
            "content": sections,
            "supporting_facts": _supporting_facts(),
            "proof_refs": list(proof_refs),
            "degraded_reason": degraded_reason,
        }
        return TransitProjectionResponse(
            projection_id="transit_client_projection_v1",
            status=status,
            plan_code=normalized_plan,
            content=TransitProjectionContent(sections=sections, depth=normalized_plan),
            supporting_facts=[
                TransitProjectionFact(**fact) for fact in payload_for_hash["supporting_facts"]
            ],
            proof_refs=list(proof_refs),
            projection_hash=compute_projection_hash(payload_for_hash),
            degraded_reason=degraded_reason,
            upgrade_hint=_upgrade_hint(normalized_plan),
        )

    def unavailable(self, *, plan_code: str, reason: str) -> TransitProjectionResponse:
        """Produit un état indisponible explicite sans fallback narratif."""
        normalized_plan = _normalize_plan(plan_code)
        payload_for_hash = {
            "projection_id": "transit_client_projection_v1",
            "status": "unavailable",
            "plan_code": normalized_plan,
            "content": {},
            "supporting_facts": [],
            "proof_refs": [],
            "degraded_reason": reason,
        }
        return TransitProjectionResponse(
            projection_id="transit_client_projection_v1",
            status="unavailable",
            plan_code=normalized_plan,
            content=TransitProjectionContent(sections={}, depth=normalized_plan),
            supporting_facts=[],
            proof_refs=[],
            projection_hash=compute_projection_hash(payload_for_hash),
            degraded_reason=reason,
            upgrade_hint=_upgrade_hint(normalized_plan),
        )


def _normalize_plan(plan_code: str) -> str:
    """Normalise les plans inconnus vers le plan le plus restrictif."""
    if plan_code in _PLAN_ORDER:
        return plan_code
    return "free"


def _sections_for_plan(plan_code: str) -> dict[str, str]:
    """Applique la profondeur cumulée free, basic puis premium."""
    allowed_rank = _PLAN_ORDER[plan_code]
    sections: dict[str, str] = {}
    for candidate, rank in _PLAN_ORDER.items():
        if rank <= allowed_rank:
            sections.update(_SECTIONS_BY_PLAN[candidate])
    return sections


def _supporting_facts() -> list[dict[str, str]]:
    """Expose uniquement des références client lisibles."""
    return [
        {
            "ref_id": "transit-window:active-period",
            "label": "Periode active validee",
            "source": "projection_validation_evidence",
        },
        {
            "ref_id": "transit-theme:dominant",
            "label": "Theme dominant prepare",
            "source": "client_projection_contract",
        },
    ]


def _upgrade_hint(plan_code: str) -> str | None:
    """Indique la montée de plan utile sans révéler de contenu interdit."""
    if plan_code == "free":
        return "basic_unlocks_timing_windows"
    if plan_code == "basic":
        return "premium_unlocks_sequence_and_cycles"
    return None

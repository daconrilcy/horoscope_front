"""Mapper interne des dignités calculées vers la table d'audit."""

from __future__ import annotations

from dataclasses import asdict

from app.domain.astrology.dignities.contracts import PlanetDignityResult
from app.infra.db.repositories.dignity_reference_repository import ChartPlanetDignityResultInput


def build_chart_planet_dignity_audit_input(
    *,
    chart_result_id: int,
    chart_id: str,
    input_hash: str,
    ruleset_version: str,
    dignity: PlanetDignityResult,
) -> ChartPlanetDignityResultInput:
    """Construit le DTO d'audit depuis un resultat de dignite deja calcule."""
    return ChartPlanetDignityResultInput(
        chart_result_id=chart_result_id,
        planet_code=dignity.planet_code,
        score_profile_code=dignity.score_profile,
        astral_system_code=dignity.tradition,
        reference_version=dignity.reference_version,
        essential_score=dignity.essential_score,
        accidental_score=dignity.accidental_score,
        total_score=dignity.total_score,
        functional_strength_score=dignity.functional_strength_score,
        expression_quality_score=dignity.expression_quality_score,
        intensity_score=dignity.intensity_score,
        essential_breakdown_json=[asdict(item) for item in dignity.essential_breakdown],
        accidental_breakdown_json=[asdict(item) for item in dignity.accidental_breakdown],
        condition_summary_json=_build_condition_summary(dignity),
        calculation_context_json={
            "source": "ChartResultService.persist_trace",
            "source_field": "NatalResult.dignities",
            "chart_id": chart_id,
            "chart_result_id": chart_result_id,
            "input_hash": input_hash,
            "ruleset_version": ruleset_version,
            "score_profile": dignity.score_profile,
            "tradition": dignity.tradition,
            "reference_version": dignity.reference_version,
        },
    )


def _build_condition_summary(dignity: PlanetDignityResult) -> dict[str, object]:
    """Assemble les faits de secte deja presents dans le resultat calcule."""
    summary: dict[str, object] = {
        "sect": dignity.sect,
        "chart_sect": asdict(dignity.chart_sect),
    }
    if dignity.sect_condition is not None:
        summary["sect_condition"] = asdict(dignity.sect_condition)
    return summary

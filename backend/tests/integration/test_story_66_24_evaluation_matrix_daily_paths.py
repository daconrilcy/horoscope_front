from pathlib import Path

import yaml

from tests.evaluation.report_generator import generate_markdown_report


def _load_evaluation_matrix() -> list[dict]:
    path = Path(__file__).parents[1] / "evaluation" / "evaluation_matrix.yaml"
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)["matrix"]


def test_daily_paths_are_present_in_evaluation_matrix() -> None:
    """
    Story 66.24 AC1/AC8:
    Les chemins daily actifs doivent être présents explicitement dans la matrice.
    Story 66.28: Seul horoscope_daily est désormais requis comme nominal_canonical.
    """
    matrix = _load_evaluation_matrix()

    by_feature: dict[str, list[dict]] = {}
    for case in matrix:
        by_feature.setdefault(case["feature"], []).append(case)

    assert "horoscope_daily" in by_feature
    # daily_prediction must not be a required feature anymore
    assert any(
        case["pipeline_kind"] == "nominal_canonical" for case in by_feature["horoscope_daily"]
    )


def test_report_marks_campaign_complete_when_all_required_paths_pass() -> None:
    """
    Story 66.24 AC8:
    Une campagne complète et passante doit produire un statut global PASSED.
    """
    results = [
        {
            "case": "chat/premium/ample/full",
            "pipeline_kind": "nominal_canonical",
            "pipeline_ok": True,
            "placeholders": True,
            "context_quality": True,
            "persona": True,
            "output_contract": True,
            "length_budget": True,
            "differentiation_plan": True,
        },
        {
            "case": "guidance/free/synthetique/minimal",
            "pipeline_kind": "nominal_canonical",
            "pipeline_ok": True,
            "placeholders": True,
            "context_quality": True,
            "persona": True,
            "output_contract": True,
            "length_budget": True,
            "differentiation_plan": True,
        },
        {
            "case": "natal/premium/ample/full",
            "pipeline_kind": "nominal_canonical",
            "pipeline_ok": True,
            "placeholders": True,
            "context_quality": True,
            "persona": True,
            "output_contract": True,
            "length_budget": True,
            "differentiation_plan": True,
        },
        {
            "case": "horoscope_daily/premium/ample/full",
            "pipeline_kind": "nominal_canonical",
            "pipeline_ok": True,
            "placeholders": True,
            "context_quality": True,
            "persona": True,
            "output_contract": True,
            "length_budget": True,
            "differentiation_plan": True,
        },
    ]

    report = generate_markdown_report(results)

    assert "## Gating Status: 🟢 PASSED" in report
    assert "Missing Mandatory Features" not in report


def test_report_blocks_campaign_when_horoscope_daily_is_missing() -> None:
    """
    Story 66.24 AC8:
    L'absence d'un chemin daily actif doit empêcher le statut complet.
    Story 66.28: On vérifie maintenant sur horoscope_daily.
    """
    results = [
        {
            "case": "chat/premium/ample/full",
            "pipeline_kind": "nominal_canonical",
            "pipeline_ok": True,
            "placeholders": True,
            "context_quality": True,
            "persona": True,
            "output_contract": True,
            "length_budget": True,
            "differentiation_plan": True,
        },
        {
            "case": "guidance/free/synthetique/minimal",
            "pipeline_kind": "nominal_canonical",
            "pipeline_ok": True,
            "placeholders": True,
            "context_quality": True,
            "persona": True,
            "output_contract": True,
            "length_budget": True,
            "differentiation_plan": True,
        },
        {
            "case": "natal/premium/ample/full",
            "pipeline_kind": "nominal_canonical",
            "pipeline_ok": True,
            "placeholders": True,
            "context_quality": True,
            "persona": True,
            "output_contract": True,
            "length_budget": True,
            "differentiation_plan": True,
        },
    ]

    report = generate_markdown_report(results)

    assert "## Gating Status: 🔴 INCOMPLETE (Missing paths)" in report
    assert "horoscope_daily" in report

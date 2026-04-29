"""Story 66.40 — registre legacy résiduel, blocage progressif, télémétrie, alignement doc."""

from pathlib import Path
from unittest.mock import patch

import pytest

from app.domain.llm.governance.feature_taxonomy import SUPPORTED_FAMILIES
from app.domain.llm.governance.legacy_residual_registry import (
    assert_deprecated_use_case_registered,
    effective_progressive_blocklist,
    get_registry_schema_version,
    load_legacy_residual_registry,
    render_maintenance_report,
    validate_doc_registry_version,
    validate_registry_integrity,
)
from app.domain.llm.prompting.catalog import DEPRECATED_USE_CASE_MAPPING
from app.domain.llm.runtime.contracts import FallbackType, GatewayError
from app.domain.llm.runtime.fallback_governance import FallbackGovernanceRegistry


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def test_registry_covers_all_fallback_types_and_catalog():
    root = load_legacy_residual_registry()
    assert root.schema_version
    assert len(root.fallback_paths) == len(FallbackType)
    for uc in DEPRECATED_USE_CASE_MAPPING:
        assert_deprecated_use_case_registered(uc)


def test_governance_matrix_forbidden_families_match_supported_perimeter():
    matrix = FallbackGovernanceRegistry.GOVERNANCE_MATRIX
    expected = set(SUPPORTED_FAMILIES)
    for fb in (
        FallbackType.USE_CASE_FIRST,
        FallbackType.RESOLVE_MODEL,
        FallbackType.PROVIDER_OPENAI,
    ):
        assert matrix[fb]["forbidden_families"] == expected


def test_progressive_blocklist_raises_gateway_error(monkeypatch):
    monkeypatch.setenv("LLM_LEGACY_PROGRESSIVE_BLOCKLIST", "fb.legacy_wrapper")
    assert "fb.legacy_wrapper" in effective_progressive_blocklist()
    with pytest.raises(GatewayError) as exc:
        FallbackGovernanceRegistry.track_fallback(
            FallbackType.LEGACY_WRAPPER,
            call_site="test:block",
            feature="x",
            is_nominal=False,
        )
    assert "fb.legacy_wrapper" in str(exc.value)
    monkeypatch.delenv("LLM_LEGACY_PROGRESSIVE_BLOCKLIST", raising=False)


def test_progressive_blocklist_emits_telemetry_before_gateway_error(monkeypatch):
    """Visibilité ops : métriques avant GatewayError (blocage progressif)."""
    monkeypatch.setenv("LLM_LEGACY_PROGRESSIVE_BLOCKLIST", "fb.legacy_wrapper")
    with (
        patch("app.domain.llm.runtime.fallback_governance.increment_counter") as mock_gov,
        patch("app.domain.llm.runtime.observability_service.increment_counter") as mock_obs,
    ):
        with pytest.raises(GatewayError):
            FallbackGovernanceRegistry.track_fallback(
                FallbackType.LEGACY_WRAPPER,
                call_site="test:block-telemetry",
                feature="x",
                is_nominal=False,
            )
    obs_names = [c.args[0] for c in mock_obs.call_args_list]
    assert "llm_legacy_residual_blocked_attempt_total" in obs_names
    assert "llm_governance_event_total" in obs_names
    gov_names = [c.args[0] for c in mock_gov.call_args_list]
    assert gov_names == []
    monkeypatch.delenv("LLM_LEGACY_PROGRESSIVE_BLOCKLIST", raising=False)


def test_stable_id_unique_across_all_registry_sections():
    root = load_legacy_residual_registry()
    dup_sid = root.fallback_paths[0].stable_id
    ga0 = root.governed_aliases[0]
    bad = root.model_copy(
        update={
            "governed_aliases": [
                ga0.model_copy(update={"stable_id": dup_sid}),
                *list(root.governed_aliases)[1:],
            ]
        }
    )
    with pytest.raises(RuntimeError, match="doublon"):
        validate_registry_integrity(bad)


def test_maintenance_report_lists_entries():
    report = render_maintenance_report()
    assert "fb.use_case_first" in report
    assert get_registry_schema_version() in report


def test_doc_registry_version_matches_code():
    doc_path = _repo_root() / "docs" / "llm-prompt-generation-by-feature.md"
    content = doc_path.read_text(encoding="utf-8")
    assert validate_doc_registry_version(content) == []


def test_legacy_residual_telemetry_emitted():
    with (
        patch("app.domain.llm.runtime.fallback_governance.increment_counter") as mock_gov,
        patch("app.domain.llm.runtime.observability_service.increment_counter") as mock_obs,
    ):
        FallbackGovernanceRegistry.track_fallback(
            FallbackType.LEGACY_WRAPPER,
            call_site="test:telemetry",
            feature="other_family",
            is_nominal=False,
        )
    names = [c.args[0] for c in mock_gov.call_args_list] + [
        c.args[0] for c in mock_obs.call_args_list
    ]
    assert "llm_gateway_fallback_usage_total" in names
    assert "llm_legacy_residual_activation_total" in names


def test_incomplete_deprecated_use_case_rejected_by_model():
    from pydantic import ValidationError

    from app.domain.llm.governance.legacy_residual_registry import DeprecatedUseCaseRecord

    with pytest.raises(ValidationError, match="Champ obligatoire vide"):
        DeprecatedUseCaseRecord(
            stable_id="uc.bad",
            use_case_key="x",
            registry_status="deprecated",
            owner="",
            justification="y",
            perimeter="z",
            review_or_extinction_date="2026-01-01",
        )

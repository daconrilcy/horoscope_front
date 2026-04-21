"""Story 66.42 — registre central, alignements et anti-réintroduction."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

import app.domain.llm.governance.prompt_governance_registry as gov_registry_module
from app.domain.llm.configuration.assembly_resolver import (
    PLACEHOLDER_ALLOWLIST,
    validate_placeholders,
)
from app.domain.llm.governance.prompt_governance_registry import (
    PromptGovernanceRegistry,
    PromptGovernanceRegistryData,
)
from app.domain.llm.prompting.catalog import DEPRECATED_USE_CASE_MAPPING
from app.domain.llm.prompting.prompt_renderer import PromptRenderer
from app.ops.llm.semantic_invariants_registry import (
    GOVERNED_LEGACY_FEATURE_ALIASES_TO_CANONICAL,
    GOVERNED_NOMINAL_FAMILIES,
)

_CANONICAL_PROMPT_GOV_REGISTRY_JSON = (
    Path(__file__).resolve().parents[2]
    / "app"
    / "domain"
    / "llm"
    / "governance"
    / "data"
    / "prompt_governance_registry.json"
)


def _write_registry_fixture(data: dict) -> Path:
    fd, raw_path = tempfile.mkstemp(prefix="gov-reg-", suffix=".json")
    path = Path(raw_path)
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f)
    finally:
        import os

        os.close(fd)
    return path


def test_horoscope_daily_family_resolves_for_placeholders() -> None:
    reg = PromptGovernanceRegistry.load()
    assert reg.resolve_placeholder_family("horoscope_daily") == "horoscope_daily"
    invalid, violations = reg.validate_placeholders_in_template(
        "X {{question}} {{locale}}", "horoscope_daily", source="test"
    )
    assert invalid == []
    assert violations == []


def test_unknown_placeholder_blocked_for_guidance() -> None:
    reg = PromptGovernanceRegistry.load()
    invalid, violations = reg.validate_placeholders_in_template(
        "Hello {{forbidden_var}}", "guidance", source="test"
    )
    assert "forbidden_var" in invalid
    assert any(v.rule_id == "GOV_PH_NOT_IN_REGISTRY" for v in violations)


def test_deprecated_use_case_mapping_matches_registry_json() -> None:
    data_path = _CANONICAL_PROMPT_GOV_REGISTRY_JSON
    raw = json.loads(data_path.read_text(encoding="utf-8"))
    from_json = raw["deprecated_use_case_mapping"]
    assert set(from_json.keys()) == set(DEPRECATED_USE_CASE_MAPPING.keys())
    for k, v in DEPRECATED_USE_CASE_MAPPING.items():
        assert v == from_json[k]


def test_semantic_invariants_aligned_with_registry() -> None:
    reg = PromptGovernanceRegistry.load()
    assert GOVERNED_NOMINAL_FAMILIES == frozenset(reg.canonical_families)
    assert GOVERNED_LEGACY_FEATURE_ALIASES_TO_CANONICAL == reg.legacy_nominal_feature_aliases_map()


def test_placeholder_allowlist_is_registry_derived() -> None:
    reg = PromptGovernanceRegistry.load()
    for fam, defs in PLACEHOLDER_ALLOWLIST.items():
        assert [d.name for d in defs] == [d.name for d in reg.get_placeholder_defs(fam)]


def test_validate_placeholders_backward_compatible_api() -> None:
    assert validate_placeholders("Hello {{last_user_msg}}", "guidance") == []
    assert validate_placeholders("Hello {{forbidden_var}}", "guidance") == ["forbidden_var"]


def test_incomplete_governed_exception_rejected() -> None:
    base = json.loads((_CANONICAL_PROMPT_GOV_REGISTRY_JSON).read_text(encoding="utf-8"))
    base["governed_exceptions"] = [
        {
            "id": "BAD",
            "owner": "",
            "justification": "x",
            "scope": "test",
            "status": "active",
            "review_by": "2026-12-31",
        }
    ]
    with pytest.raises(ValidationError):
        PromptGovernanceRegistryData.model_validate(base)


def test_event_description_allowed_for_guidance_family() -> None:
    reg = PromptGovernanceRegistry.load()
    invalid, _v = reg.validate_placeholders_in_template(
        "Event: {{event_description}}", "guidance", source="test"
    )
    assert invalid == []


def test_chat_allows_natal_chart_summary_runtime_render() -> None:
    rendered = PromptRenderer.render(
        "Hello {{natal_chart_summary}} {{locale}} {{use_case}}",
        {
            "natal_chart_summary": "Sun in Aries",
            "locale": "fr-FR",
            "use_case": "chat_astrologer",
        },
        required_variables=["natal_chart_summary"],
        feature="chat",
    )
    assert "Sun in Aries" in rendered


def test_renderer_universal_placeholders_follow_registry() -> None:
    reg = PromptGovernanceRegistry.load()
    assert "last_user_msg" in reg.universal_placeholders
    rendered = PromptRenderer.render(
        "U={{last_user_msg}}",
        variables={},
        required_variables=[],
        feature="chat",
    )
    assert rendered == "U="


def test_governed_exception_allows_placeholder_when_scope_matches() -> None:
    base = json.loads((_CANONICAL_PROMPT_GOV_REGISTRY_JSON).read_text(encoding="utf-8"))
    base["governed_exceptions"] = [
        {
            "id": "EXC-CHAT-NATAL-SUMMARY",
            "owner": "platform-arch",
            "justification": "Compat transitoire chat_astrologer",
            "scope": "placeholder:natal_chart_summary;family:chat;rule:GOV_PH_NOT_IN_REGISTRY",
            "status": "active",
            "review_by": "2026-12-31",
        }
    ]
    base["placeholders_by_family"]["chat"] = [
        p for p in base["placeholders_by_family"]["chat"] if p["name"] != "natal_chart_summary"
    ]
    p = _write_registry_fixture(base)
    try:
        reg = PromptGovernanceRegistry.load(p)
        invalid, violations = reg.validate_placeholders_in_template(
            "X {{natal_chart_summary}}", "chat", source="test"
        )
        assert invalid == []
        assert violations == []
    finally:
        p.unlink(missing_ok=True)


def test_governed_exception_does_not_apply_with_other_family() -> None:
    base = json.loads((_CANONICAL_PROMPT_GOV_REGISTRY_JSON).read_text(encoding="utf-8"))
    base["governed_exceptions"] = [
        {
            "id": "EXC-CHAT-ONLY",
            "owner": "platform-arch",
            "justification": "Compat transitoire chat_astrologer",
            "scope": "placeholder:natal_chart_summary;family:chat;rule:GOV_PH_NOT_IN_REGISTRY",
            "status": "active",
            "review_by": "2026-12-31",
        }
    ]
    p = _write_registry_fixture(base)
    try:
        reg = PromptGovernanceRegistry.load(p)
        invalid, _violations = reg.validate_placeholders_in_template(
            "X {{natal_chart_summary}}", "guidance", source="test"
        )
        assert invalid == ["natal_chart_summary"]
    finally:
        p.unlink(missing_ok=True)


def test_governed_exception_applies_at_runtime_rendering(monkeypatch: pytest.MonkeyPatch) -> None:
    base = json.loads((_CANONICAL_PROMPT_GOV_REGISTRY_JSON).read_text(encoding="utf-8"))
    base["governed_exceptions"] = [
        {
            "id": "EXC-CHAT-RUNTIME",
            "owner": "platform-arch",
            "justification": "Compat transitoire runtime",
            "scope": "placeholder:natal_chart_summary;family:chat;rule:GOV_PH_NOT_IN_REGISTRY",
            "status": "active",
            "review_by": "2026-12-31",
        }
    ]
    base["placeholders_by_family"]["chat"] = [
        p for p in base["placeholders_by_family"]["chat"] if p["name"] != "natal_chart_summary"
    ]
    p = _write_registry_fixture(base)
    try:
        reg = PromptGovernanceRegistry.load(p)
        monkeypatch.setattr(
            gov_registry_module,
            "get_prompt_governance_registry",
            lambda: reg,
        )
        monkeypatch.setattr(
            gov_registry_module,
            "PLACEHOLDER_ALLOWLIST",
            {fam: list(defs) for fam, defs in reg._placeholder_defs_by_family.items()},
        )
        rendered = PromptRenderer.render(
            "Hello {{natal_chart_summary}} {{locale}} {{use_case}}",
            {
                "natal_chart_summary": "Sun in Aries",
                "locale": "fr-FR",
                "use_case": "chat_astrologer",
            },
            required_variables=["natal_chart_summary"],
            feature="chat",
        )
        assert "Sun in Aries" in rendered
        allowed, exc_id = reg.is_placeholder_governed_for_feature(
            placeholder="natal_chart_summary", feature="chat"
        )
        assert allowed
        assert exc_id == "EXC-CHAT-RUNTIME"
    finally:
        p.unlink(missing_ok=True)


def test_governed_exception_scope_invalid_key_rejected() -> None:
    base = json.loads((_CANONICAL_PROMPT_GOV_REGISTRY_JSON).read_text(encoding="utf-8"))
    base["governed_exceptions"] = [
        {
            "id": "EXC-BAD-KEY",
            "owner": "platform-arch",
            "justification": "invalid token key",
            "scope": "placeholder:natal_chart_summary;famly:chat;rule:GOV_PH_NOT_IN_REGISTRY",
            "status": "active",
            "review_by": "2026-12-31",
        }
    ]
    with pytest.raises(ValidationError):
        PromptGovernanceRegistryData.model_validate(base)


def test_governed_exception_scope_missing_family_rejected() -> None:
    base = json.loads((_CANONICAL_PROMPT_GOV_REGISTRY_JSON).read_text(encoding="utf-8"))
    base["governed_exceptions"] = [
        {
            "id": "EXC-MISSING-FAMILY",
            "owner": "platform-arch",
            "justification": "missing family token",
            "scope": "placeholder:natal_chart_summary;rule:GOV_PH_NOT_IN_REGISTRY",
            "status": "active",
            "review_by": "2026-12-31",
        }
    ]
    with pytest.raises(ValidationError):
        PromptGovernanceRegistryData.model_validate(base)


def test_governed_exception_scope_unknown_family_rejected() -> None:
    base = json.loads((_CANONICAL_PROMPT_GOV_REGISTRY_JSON).read_text(encoding="utf-8"))
    base["governed_exceptions"] = [
        {
            "id": "EXC-UNKNOWN-FAMILY",
            "owner": "platform-arch",
            "justification": "unknown family token",
            "scope": (
                "placeholder:natal_chart_summary;family:unknown_family;rule:GOV_PH_NOT_IN_REGISTRY"
            ),
            "status": "active",
            "review_by": "2026-12-31",
        }
    ]
    with pytest.raises(ValidationError):
        PromptGovernanceRegistryData.model_validate(base)


def test_governed_exception_scope_unknown_rule_rejected() -> None:
    base = json.loads((_CANONICAL_PROMPT_GOV_REGISTRY_JSON).read_text(encoding="utf-8"))
    base["governed_exceptions"] = [
        {
            "id": "EXC-UNKNOWN-RULE",
            "owner": "platform-arch",
            "justification": "unknown rule token",
            "scope": "placeholder:natal_chart_summary;family:chat;rule:GOV_PH_NOT_IN_REGSTRY",
            "status": "active",
            "review_by": "2026-12-31",
        }
    ]
    with pytest.raises(ValidationError):
        PromptGovernanceRegistryData.model_validate(base)


def test_governed_exception_scope_family_alias_and_lower_rule_are_normalized() -> None:
    base = json.loads((_CANONICAL_PROMPT_GOV_REGISTRY_JSON).read_text(encoding="utf-8"))
    base["governed_exceptions"] = [
        {
            "id": "EXC-NORMALIZED",
            "owner": "platform-arch",
            "justification": "normalize alias and rule casing",
            "scope": (
                "placeholder:legacy_only_ph;family:daily_prediction;rule:gov_ph_not_in_registry"
            ),
            "status": "active",
            "review_by": "2026-12-31",
        }
    ]
    p = _write_registry_fixture(base)
    try:
        reg = PromptGovernanceRegistry.load(p)
        allowed, exc_id = reg.is_placeholder_governed_for_feature(
            placeholder="legacy_only_ph",
            feature="horoscope_daily",
        )
        assert allowed
        assert exc_id == "EXC-NORMALIZED"
    finally:
        p.unlink(missing_ok=True)

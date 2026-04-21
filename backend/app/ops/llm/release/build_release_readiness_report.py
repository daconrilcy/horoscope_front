"""Aggregate local LLM release readiness evidence into a single report."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_BACKEND_ROOT = Path(__file__).resolve().parents[4]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.domain.llm.governance.legacy_residual_registry import (
    effective_progressive_blocklist,
    load_legacy_residual_registry,
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_optional_json(path_str: str | None) -> dict[str, Any] | None:
    if not path_str:
        return None
    path = Path(path_str)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _unwrap_data(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if payload is None:
        return None
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    return payload


def _status(flag: bool) -> str:
    return "green" if flag else "red"


def _bool(value: Any) -> bool:
    return bool(value)


def build_report(
    *,
    candidate: dict[str, Any] | None,
    doc_conformity: dict[str, Any] | None,
    chaos: dict[str, Any] | None,
    qualification: dict[str, Any] | None,
    golden: dict[str, Any] | None,
    smoke: dict[str, Any] | None,
) -> dict[str, Any]:
    registry = load_legacy_residual_registry()
    blocklist = sorted(effective_progressive_blocklist(root=registry))

    qualification = _unwrap_data(qualification)
    golden = _unwrap_data(golden)
    smoke = _unwrap_data(smoke)

    candidate_snapshot = (candidate or {}).get("candidate_snapshot", {})
    validation_report = (candidate or {}).get("validation_report", {})
    snapshot_id = candidate_snapshot.get("id")
    snapshot_version = candidate_snapshot.get("version")
    manifest_entry_id = candidate_snapshot.get("default_manifest_entry_id")

    qualification_ok = (
        qualification is not None
        and qualification.get("active_snapshot_id") == snapshot_id
        and qualification.get("active_snapshot_version") == snapshot_version
        and qualification.get("manifest_entry_id") == manifest_entry_id
        and qualification.get("verdict") in {"go", "go-with-constraints"}
    )
    golden_ok = (
        golden is not None
        and golden.get("active_snapshot_id") == snapshot_id
        and golden.get("active_snapshot_version") == snapshot_version
        and golden.get("manifest_entry_id") == manifest_entry_id
        and golden.get("verdict") == "pass"
    )
    smoke_ok = (
        smoke is not None
        and smoke.get("active_snapshot_id") == snapshot_id
        and smoke.get("active_snapshot_version") == snapshot_version
        and smoke.get("manifest_entry_id") == manifest_entry_id
        and smoke.get("status") == "pass"
        and not smoke.get("forbidden_fallback_detected", False)
    )
    chaos_ok = (
        chaos is not None
        and chaos.get("report_kind") == "provider_runtime_chaos_invariants"
        and _bool(chaos.get("all_passed"))
    )
    doc_ok = doc_conformity is not None and doc_conformity.get("status") == "ok"
    candidate_ok = (
        candidate is not None
        and _bool(snapshot_id)
        and _bool(snapshot_version)
        and _bool(manifest_entry_id)
    )
    snapshot_validation_ok = candidate is not None and _bool(validation_report.get("is_valid"))
    legacy_blocklist_ok = len(blocklist) > 0

    blockers: list[str] = []
    if not candidate_ok:
        blockers.append("No exploitable candidate snapshot artifact.")
    if not snapshot_validation_ok:
        blockers.append("Candidate snapshot validation is missing or failed.")
    if not qualification_ok:
        blockers.append("Qualification evidence is missing, stale, not correlated, or failed.")
    if not golden_ok:
        blockers.append("Golden regression evidence is missing, stale, not correlated, or failed.")
    if not smoke_ok:
        blockers.append("Post-activation smoke evidence is missing, not correlated, or failed.")
    if not legacy_blocklist_ok:
        blockers.append("Progressive legacy blocklist is still empty.")
    if not chaos_ok:
        blockers.append("Chaos report is missing or not fully green.")
    if not doc_ok:
        blockers.append("Doc/code conformity evidence is missing or failed.")

    return {
        "generated_at": _utcnow(),
        "decision": "go" if not blockers else "no-go",
        "candidate_snapshot": candidate_snapshot,
        "checks": {
            "candidate_snapshot": _status(candidate_ok),
            "snapshot_validation": _status(snapshot_validation_ok),
            "qualification": _status(qualification_ok),
            "golden": _status(golden_ok),
            "smoke": _status(smoke_ok),
            "chaos": _status(chaos_ok),
            "doc_conformity": _status(doc_ok),
            "legacy_progressive_blocklist": _status(legacy_blocklist_ok),
        },
        "effective_progressive_blocklist": blocklist,
        "registry_schema_version": registry.schema_version,
        "blockers": blockers,
        "source_artifacts": {
            "candidate": candidate is not None,
            "qualification": qualification is not None,
            "golden": golden is not None,
            "smoke": smoke is not None,
            "chaos": chaos is not None,
            "doc_conformity": doc_conformity is not None,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build an LLM release readiness report from evidence artifacts."
    )
    parser.add_argument(
        "--candidate",
        default=str(_BACKEND_ROOT.parent / "artifacts" / "llm-release-candidate.json"),
    )
    parser.add_argument(
        "--doc-conformity",
        default=str(_BACKEND_ROOT.parent / "artifacts" / "llm-doc-conformity.json"),
    )
    parser.add_argument(
        "--chaos",
        default=str(_BACKEND_ROOT.parent / "artifacts" / "chaos" / "story-66-43-chaos-report.json"),
    )
    parser.add_argument("--qualification", default=None)
    parser.add_argument("--golden", default=None)
    parser.add_argument("--smoke", default=None)
    parser.add_argument(
        "--output",
        default=str(_BACKEND_ROOT.parent / "artifacts" / "llm-release-readiness.json"),
    )
    args = parser.parse_args()

    report = build_report(
        candidate=_load_optional_json(args.candidate),
        doc_conformity=_load_optional_json(args.doc_conformity),
        chaos=_load_optional_json(args.chaos),
        qualification=_load_optional_json(args.qualification),
        golden=_load_optional_json(args.golden),
        smoke=_load_optional_json(args.smoke),
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

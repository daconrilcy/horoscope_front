"""Helpers de lecture des snapshots de release LLM admin."""

from __future__ import annotations

from typing import Any, Literal

from app.api.v1.schemas.routers.admin.llm.prompts import (
    ProofSummary,
    SnapshotDiffEntry,
    SnapshotTimelineItem,
)
from app.infra.db.models.llm.llm_release import LlmReleaseSnapshotModel


def _normalize_event_type(status: str | None) -> str:
    status_text = str(status or "").strip().lower()
    mapping = {
        "candidate": "created",
        "qualified": "validated",
        "activated": "activated",
        "monitoring": "monitoring",
        "degraded": "degraded",
        "rollback_recommended": "rollback_recommended",
        "rolled_back": "rolled_back",
    }
    return mapping.get(status_text, "backend_unmapped")


def _extract_proof_summaries(snapshot: LlmReleaseSnapshotModel) -> list[ProofSummary]:
    """Construit les preuves de qualification, golden, smoke et readiness d'un snapshot."""
    manifest = snapshot.manifest or {}
    targets = manifest.get("targets") or {}
    release_health = manifest.get("release_health") or {}
    history = release_health.get("history") or []
    known_manifest_entry_ids = set(str(entry_id) for entry_id in targets.keys())

    qualification_signal: dict[str, Any] | None = None
    golden_signal: dict[str, Any] | None = None
    smoke_signal: dict[str, Any] | None = None

    for event in history:
        if not isinstance(event, dict):
            continue
        signals = event.get("signals") or {}
        if not isinstance(signals, dict):
            continue
        if signals.get("qualification_verdict") is not None:
            qualification_signal = event
        if signals.get("golden_verdict") is not None:
            golden_signal = event
        if signals.get("active_snapshot_id") is not None:
            smoke_signal = event

    qualification_signals = (qualification_signal or {}).get("signals", {})
    golden_signals = (golden_signal or {}).get("signals", {})
    qualification_verdict = (
        str(qualification_signals.get("qualification_verdict")) if qualification_signal else None
    )
    golden_verdict = str(golden_signals.get("golden_verdict")) if golden_signal else None
    qualification_snapshot_id = (
        str(qualification_signals.get("active_snapshot_id"))
        if qualification_signals.get("active_snapshot_id")
        else None
    )
    golden_snapshot_id = (
        str(golden_signals.get("active_snapshot_id"))
        if golden_signals.get("active_snapshot_id")
        else None
    )
    qualification_manifest_entry_id = (
        str(qualification_signals.get("qualification_manifest_entry_id"))
        if qualification_signals.get("qualification_manifest_entry_id")
        else None
    )
    golden_manifest_entry_id = (
        str(golden_signals.get("golden_manifest_entry_id"))
        if golden_signals.get("golden_manifest_entry_id")
        else None
    )
    smoke_status = (
        str((smoke_signal or {}).get("signals", {}).get("status")) if smoke_signal else None
    )
    smoke_manifest_entry_id = (
        str((smoke_signal or {}).get("signals", {}).get("manifest_entry_id"))
        if smoke_signal and (smoke_signal.get("signals") or {}).get("manifest_entry_id")
        else None
    )
    qualification_correlated = (
        qualification_verdict is not None
        and qualification_snapshot_id == str(snapshot.id)
        and (
            qualification_manifest_entry_id is None
            or qualification_manifest_entry_id in known_manifest_entry_ids
        )
    )
    golden_correlated = (
        golden_verdict is not None
        and golden_snapshot_id == str(snapshot.id)
        and (
            golden_manifest_entry_id is None or golden_manifest_entry_id in known_manifest_entry_ids
        )
    )

    qualification = ProofSummary(
        proof_type="qualification",
        status="present" if qualification_verdict else "missing",
        verdict=qualification_verdict,
        generated_at=str((qualification_signal or {}).get("timestamp"))
        if qualification_signal
        else None,
        manifest_entry_id=qualification_manifest_entry_id,
        correlated=qualification_correlated,
    )
    golden = ProofSummary(
        proof_type="golden",
        status="present" if golden_verdict else "missing",
        verdict=golden_verdict,
        generated_at=str((golden_signal or {}).get("timestamp")) if golden_signal else None,
        manifest_entry_id=golden_manifest_entry_id,
        correlated=golden_correlated,
    )
    smoke_correlated = (
        smoke_manifest_entry_id is not None and smoke_manifest_entry_id in known_manifest_entry_ids
    )
    smoke = ProofSummary(
        proof_type="smoke",
        status=("present" if smoke_status else "missing"),
        verdict=smoke_status,
        generated_at=str((smoke_signal or {}).get("timestamp")) if smoke_signal else None,
        manifest_entry_id=smoke_manifest_entry_id,
        correlated=smoke_correlated,
    )
    readiness_status = "missing"
    readiness_verdict: str | None = None
    if (
        qualification.status == "present"
        and golden.status == "present"
        and smoke.status == "present"
    ):
        if qualification.verdict in {"go", "go-with-constraints"} and golden.verdict == "pass":
            readiness_verdict = (
                "valid"
                if qualification_correlated and golden_correlated and smoke_correlated
                else "uncorrelated"
            )
            readiness_status = "present"
        else:
            readiness_verdict = "invalid"
            readiness_status = "present"
    readiness = ProofSummary(
        proof_type="readiness",
        status=readiness_status,
        verdict=readiness_verdict,
        generated_at=smoke.generated_at or golden.generated_at or qualification.generated_at,
        manifest_entry_id=smoke.manifest_entry_id,
        correlated=qualification_correlated and golden_correlated and smoke_correlated,
    )

    return [qualification, golden, smoke, readiness]


def _build_snapshot_timeline_events(
    snapshot: LlmReleaseSnapshotModel,
) -> list[SnapshotTimelineItem]:
    """Transforme l'historique de release en timeline admin stable."""
    manifest = snapshot.manifest or {}
    release_health = manifest.get("release_health") or {}
    history = release_health.get("history") or []
    proof_summaries = _extract_proof_summaries(snapshot)
    manifest_entry_count = len((manifest.get("targets") or {}).keys())
    current_status = str(snapshot.status)
    release_health_status = str(release_health.get("status") or snapshot.status)
    history_events = [event for event in history if isinstance(event, dict)]

    timeline_events: list[SnapshotTimelineItem] = []
    timeline_events.append(
        SnapshotTimelineItem(
            event_type="created",
            snapshot_id=str(snapshot.id),
            snapshot_version=snapshot.version,
            occurred_at=snapshot.created_at.isoformat(),
            current_status=current_status,
            release_health_status=release_health_status,
            status_history=history_events,
            reason="Snapshot created.",
            from_snapshot_id=None,
            to_snapshot_id=str(snapshot.id),
            manifest_entry_count=manifest_entry_count,
            proof_summaries=proof_summaries,
        )
    )
    if snapshot.validated_at:
        timeline_events.append(
            SnapshotTimelineItem(
                event_type="validated",
                snapshot_id=str(snapshot.id),
                snapshot_version=snapshot.version,
                occurred_at=snapshot.validated_at.isoformat(),
                current_status=current_status,
                release_health_status=release_health_status,
                status_history=history_events,
                reason="Snapshot validated.",
                from_snapshot_id=None,
                to_snapshot_id=str(snapshot.id),
                manifest_entry_count=manifest_entry_count,
                proof_summaries=proof_summaries,
            )
        )

    for history_event in history_events:
        status = str(history_event.get("status") or "")
        event_type = _normalize_event_type(status)
        signals = history_event.get("signals") or {}
        if not isinstance(signals, dict):
            signals = {}
        from_snapshot_id: str | None = None
        to_snapshot_id: str | None = str(snapshot.id)
        if event_type == "rolled_back":
            from_snapshot_id = str(snapshot.id)
            to_snapshot_id = (
                str(signals.get("restored_snapshot_id"))
                if signals.get("restored_snapshot_id")
                else str(snapshot.id)
            )
        timeline_events.append(
            SnapshotTimelineItem(
                event_type=event_type,  # type: ignore[arg-type]
                snapshot_id=str(snapshot.id),
                snapshot_version=snapshot.version,
                occurred_at=str(history_event.get("timestamp") or snapshot.created_at.isoformat()),
                current_status=current_status,
                release_health_status=release_health_status,
                status_history=history_events,
                reason=(
                    str(history_event.get("reason"))
                    if history_event.get("reason") is not None
                    else None
                ),
                from_snapshot_id=from_snapshot_id,
                to_snapshot_id=to_snapshot_id,
                manifest_entry_count=manifest_entry_count,
                proof_summaries=proof_summaries,
            )
        )

    return timeline_events


def _snapshot_diff_entries(
    *,
    from_snapshot: LlmReleaseSnapshotModel,
    to_snapshot: LlmReleaseSnapshotModel,
) -> list[SnapshotDiffEntry]:
    """Compare deux snapshots actifs pour la vue admin de diff."""
    from_targets = (from_snapshot.manifest or {}).get("targets") or {}
    to_targets = (to_snapshot.manifest or {}).get("targets") or {}
    all_manifest_entry_ids = sorted(set(from_targets.keys()) | set(to_targets.keys()))
    entries: list[SnapshotDiffEntry] = []

    for manifest_entry_id in all_manifest_entry_ids:
        from_bundle = from_targets.get(manifest_entry_id) or {}
        to_bundle = to_targets.get(manifest_entry_id) or {}

        from_assembly = from_bundle.get("assembly") or {}
        to_assembly = to_bundle.get("assembly") or {}
        from_profile = from_bundle.get("profile") or {}
        to_profile = to_bundle.get("profile") or {}

        from_output_contract = (
            from_assembly.get("output_schema_id") if isinstance(from_assembly, dict) else None
        )
        to_output_contract = (
            to_assembly.get("output_schema_id") if isinstance(to_assembly, dict) else None
        )
        assembly_changed = from_assembly != to_assembly
        execution_profile_changed = from_profile != to_profile
        output_contract_changed = from_output_contract != to_output_contract

        if manifest_entry_id not in from_targets:
            category: Literal["added", "removed", "changed", "unchanged"] = "added"
        elif manifest_entry_id not in to_targets:
            category = "removed"
        elif assembly_changed or execution_profile_changed or output_contract_changed:
            category = "changed"
        else:
            category = "unchanged"

        entries.append(
            SnapshotDiffEntry(
                manifest_entry_id=str(manifest_entry_id),
                category=category,
                assembly_changed=assembly_changed,
                execution_profile_changed=execution_profile_changed,
                output_contract_changed=output_contract_changed,
                from_snapshot_id=str(from_snapshot.id),
                to_snapshot_id=str(to_snapshot.id),
            )
        )

    return entries

"""Build and validate an LLM release candidate snapshot.

This script produces a machine-readable artifact that can be used as the
starting point for a correlated release evidence pack.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.datetime_provider import datetime_provider

_BACKEND_ROOT = Path(__file__).resolve().parents[4]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.infra.db.models.llm.llm_release import LlmReleaseSnapshotModel  # noqa: E402
from app.infra.db.session import SessionLocal  # noqa: E402
from app.ops.llm.services import ReleaseService  # noqa: E402


def _utcnow() -> datetime:
    return datetime_provider.utcnow()


@dataclass(frozen=True)
class CandidateArtifact:
    generated_at: str
    candidate_snapshot: dict[str, Any]
    validation_report: dict[str, Any]
    activation_payload_template: dict[str, Any]


def _serialize_snapshot(snapshot: LlmReleaseSnapshotModel) -> dict[str, Any]:
    targets = list((snapshot.manifest or {}).get("targets", {}).keys())
    default_manifest_entry_id = targets[0] if targets else None
    return {
        "id": str(snapshot.id),
        "version": snapshot.version,
        "status": str(snapshot.status),
        "created_by": snapshot.created_by,
        "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
        "validated_at": snapshot.validated_at.isoformat() if snapshot.validated_at else None,
        "activated_at": snapshot.activated_at.isoformat() if snapshot.activated_at else None,
        "target_count": len(targets),
        "manifest_entry_ids": targets,
        "default_manifest_entry_id": default_manifest_entry_id,
    }


def _build_activation_template(snapshot: LlmReleaseSnapshotModel) -> dict[str, Any]:
    targets = list((snapshot.manifest or {}).get("targets", {}).keys())
    manifest_entry_id = targets[0] if targets else "REQUIRED_MANIFEST_ENTRY_ID"
    placeholder_ts = _utcnow().isoformat()
    return {
        "qualification_report": {
            "active_snapshot_id": str(snapshot.id),
            "active_snapshot_version": snapshot.version,
            "manifest_entry_id": manifest_entry_id,
            "verdict": "go",
            "generated_at": placeholder_ts,
        },
        "golden_report": {
            "active_snapshot_id": str(snapshot.id),
            "active_snapshot_version": snapshot.version,
            "manifest_entry_id": manifest_entry_id,
            "verdict": "pass",
            "generated_at": placeholder_ts,
        },
        "smoke_result": {
            "status": "pass",
            "active_snapshot_id": str(snapshot.id),
            "active_snapshot_version": snapshot.version,
            "manifest_entry_id": manifest_entry_id,
            "forbidden_fallback_detected": False,
            "details": {
                "environment": "staging",
                "mechanism": "activate_snapshot_like_prod",
            },
        },
        "monitoring_thresholds": {
            "error_rate": 0.02,
            "p95_latency_ms": 1500.0,
            "fallback_rate": 0.01,
        },
        "rollback_policy": "recommend-only",
        "max_evidence_age_minutes": 60,
    }


async def _run(version: str, comment: str | None) -> CandidateArtifact:
    db = SessionLocal()
    try:
        service = ReleaseService(db)
        snapshot = await service.build_snapshot(
            version=version,
            created_by="release_readiness",
            comment=comment,
        )
        validation = await service.validate_snapshot(snapshot.id)
        db.refresh(snapshot)

        validation_payload = {
            "is_valid": validation.is_valid,
            "error_count": len(validation.errors),
            "errors": [
                {
                    "code": error.error_code,
                    "message": error.message,
                    "details": error.details,
                }
                for error in validation.errors
            ],
        }
        return CandidateArtifact(
            generated_at=_utcnow().isoformat(),
            candidate_snapshot=_serialize_snapshot(snapshot),
            validation_report=validation_payload,
            activation_payload_template=_build_activation_template(snapshot),
        )
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and validate an LLM release candidate snapshot."
    )
    parser.add_argument(
        "--version",
        default=f"release-candidate-{_utcnow().strftime('%Y%m%d-%H%M%S')}",
        help="Version label to assign to the candidate snapshot.",
    )
    parser.add_argument("--comment", default=None, help="Optional release note/comment.")
    parser.add_argument(
        "--output",
        default=str(_BACKEND_ROOT.parent / "artifacts" / "llm-release-candidate.json"),
        help="Path to the JSON artifact to write.",
    )
    args = parser.parse_args()

    artifact = __import__("asyncio").run(_run(version=args.version, comment=args.comment))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(asdict(artifact), indent=2), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

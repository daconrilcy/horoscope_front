"""Build correlated smoke evidence for release activation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.core.datetime_provider import datetime_provider


def _utcnow() -> str:
    return datetime_provider.utcnow().isoformat()


def _load_json(path_str: str) -> dict[str, Any]:
    return json.loads(Path(path_str).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build correlated smoke evidence from a candidate snapshot."
    )
    parser.add_argument(
        "--candidate",
        default="artifacts/llm-release-candidate.json",
    )
    parser.add_argument("--manifest-entry-id", default=None)
    parser.add_argument("--status", default="pass")
    parser.add_argument("--forbidden-fallback-detected", action="store_true")
    parser.add_argument("--environment", default="staging")
    parser.add_argument("--mechanism", default="activate_snapshot_like_prod")
    parser.add_argument(
        "--output",
        default="artifacts/llm-smoke-evidence.json",
    )
    args = parser.parse_args()

    candidate = _load_json(args.candidate)
    snapshot = candidate["candidate_snapshot"]
    manifest_entry_id = args.manifest_entry_id or snapshot["default_manifest_entry_id"]

    payload = {
        "status": args.status,
        "active_snapshot_id": snapshot["id"],
        "active_snapshot_version": snapshot["version"],
        "manifest_entry_id": manifest_entry_id,
        "forbidden_fallback_detected": args.forbidden_fallback_detected,
        "generated_at": _utcnow(),
        "details": {
            "environment": args.environment,
            "mechanism": args.mechanism,
        },
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

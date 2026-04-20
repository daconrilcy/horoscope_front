"""Run a golden regression campaign correlated to a release candidate snapshot."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

_BACKEND_ROOT = Path(__file__).resolve().parents[4]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.infra.db.models.llm_prompt import LlmUseCaseConfigModel
from app.infra.db.models.llm_release import LlmReleaseSnapshotModel
from app.infra.db.session import SessionLocal
from app.llm_orchestration.services.golden_regression_service import GoldenRegressionService

DEFAULT_GOLDEN_PATHS = {
    "natal": "tests/fixtures/golden/natal_test.yaml",
}
MANIFEST_GOLDEN_PATHS = {
    "natal:interpretation:premium:fr-FR": "tests/fixtures/golden/natal_premium_test.yaml",
}


def _load_candidate(path_str: str) -> dict[str, Any]:
    return json.loads(Path(path_str).read_text(encoding="utf-8"))


def _resolve_target_bundle(
    db, snapshot_id: uuid.UUID, manifest_entry_id: str
) -> tuple[LlmReleaseSnapshotModel, dict[str, Any]]:
    snapshot = db.get(LlmReleaseSnapshotModel, snapshot_id)
    if snapshot is None:
        raise ValueError(f"Snapshot {snapshot_id} not found.")
    targets = (snapshot.manifest or {}).get("targets", {})
    if manifest_entry_id not in targets:
        raise ValueError(f"Manifest entry {manifest_entry_id!r} not found in snapshot.")
    return snapshot, targets[manifest_entry_id]


def _resolve_use_case_and_prompt(bundle: dict[str, Any]) -> tuple[str, str]:
    assembly = bundle.get("assembly") or {}
    feature_template = assembly.get("_feature_template") or {}
    use_case_key = feature_template.get("use_case_key")
    prompt_version_id = assembly.get("feature_template_ref")
    if not use_case_key or not prompt_version_id:
        raise ValueError("Snapshot bundle does not expose use_case_key / prompt_version_id.")
    return str(use_case_key), str(prompt_version_id)


def _resolve_golden_set_path(
    use_case: LlmUseCaseConfigModel | None,
    *,
    family: str,
    use_case_key: str,
    manifest_entry_id: str,
) -> str:
    manifest_override = MANIFEST_GOLDEN_PATHS.get(manifest_entry_id)
    if manifest_override:
        return manifest_override
    if use_case is not None and use_case.golden_set_path:
        return str(use_case.golden_set_path)
    fallback = DEFAULT_GOLDEN_PATHS.get(family)
    if fallback:
        return fallback
    raise ValueError(
        f"Use case {use_case_key!r} does not expose a golden_set_path and no family "
        f"fallback is configured for {family!r}."
    )


def _build_correlated_fixture_set(
    golden_set_path: str,
    *,
    manifest_entry_id: str,
    use_case_key: str,
) -> str:
    import yaml

    feature, subfeature, plan, locale = manifest_entry_id.split(":", maxsplit=3)
    resolved_path = GoldenRegressionService._resolve_path(golden_set_path)
    fixtures_raw = yaml.safe_load(resolved_path.read_text(encoding="utf-8"))
    fixtures = fixtures_raw if isinstance(fixtures_raw, list) else [fixtures_raw]

    selected_fixture: dict[str, Any] | None = None
    for fixture in fixtures:
        baseline_obs = (fixture or {}).get("baseline", {}).get("obs_snapshot", {})
        if baseline_obs.get("manifest_entry_id") == manifest_entry_id:
            selected_fixture = dict(fixture or {})
            break

        fixture_input = dict((fixture or {}).get("input", {}))
        if (
            selected_fixture is None
            and fixture_input.get("feature") == feature
            and fixture_input.get("subfeature") == subfeature
        ):
            selected_fixture = dict(fixture or {})

    if selected_fixture is None:
        raise ValueError(
            f"No fixture in {golden_set_path!r} can be correlated to {manifest_entry_id!r}."
        )

    fixture_input = dict(selected_fixture.get("input", {}))
    fixture_input["feature"] = feature
    fixture_input["subfeature"] = subfeature
    fixture_input["plan"] = plan
    fixture_input["locale"] = locale
    fixture_input["use_case"] = use_case_key
    selected_fixture["input"] = fixture_input

    baseline = dict(selected_fixture.get("baseline", {}))
    baseline_obs = dict(baseline.get("obs_snapshot", {}))
    baseline_obs["manifest_entry_id"] = manifest_entry_id
    baseline["obs_snapshot"] = baseline_obs
    selected_fixture["baseline"] = baseline

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".yaml",
        delete=False,
    ) as handle:
        yaml.safe_dump([selected_fixture], handle, sort_keys=False, allow_unicode=False)
        return handle.name


async def _run(
    *,
    candidate_path: str,
    manifest_entry_id: str | None,
) -> dict[str, Any]:
    candidate = _load_candidate(candidate_path)
    snapshot_meta = candidate["candidate_snapshot"]
    snapshot_id = uuid.UUID(snapshot_meta["id"])
    selected_manifest_entry_id = manifest_entry_id or snapshot_meta["default_manifest_entry_id"]

    db = SessionLocal()
    try:
        snapshot, bundle = _resolve_target_bundle(db, snapshot_id, selected_manifest_entry_id)
        use_case_key, prompt_version_id = _resolve_use_case_and_prompt(bundle)
        family = str((bundle.get("assembly") or {}).get("feature", use_case_key))

        use_case = db.get(LlmUseCaseConfigModel, use_case_key)
        golden_set_path = _resolve_golden_set_path(
            use_case,
            family=family,
            use_case_key=use_case_key,
            manifest_entry_id=selected_manifest_entry_id,
        )
        correlated_golden_set_path = _build_correlated_fixture_set(
            golden_set_path,
            manifest_entry_id=selected_manifest_entry_id,
            use_case_key=use_case_key,
        )

        try:
            report = await GoldenRegressionService.run_campaign(
                use_case_key=use_case_key,
                prompt_version_id=prompt_version_id,
                golden_set_path=correlated_golden_set_path,
                db=db,
                active_snapshot_id=snapshot.id,
                active_snapshot_version=snapshot.version,
            )
            return report.model_dump(mode="json")
        finally:
            Path(correlated_golden_set_path).unlink(missing_ok=True)
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run golden regression correlated to a candidate snapshot."
    )
    parser.add_argument(
        "--candidate",
        default=str(_BACKEND_ROOT.parent / "artifacts" / "llm-release-candidate.json"),
    )
    parser.add_argument("--manifest-entry-id", default=None)
    parser.add_argument(
        "--output",
        default=str(_BACKEND_ROOT.parent / "artifacts" / "llm-golden-evidence.json"),
    )
    args = parser.parse_args()

    report = __import__("asyncio").run(
        _run(candidate_path=args.candidate, manifest_entry_id=args.manifest_entry_id)
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

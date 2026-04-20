"""Run a lightweight correlated LLM qualification against a candidate snapshot."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import uuid
from pathlib import Path
from typing import Any

_BACKEND_ROOT = Path(__file__).resolve().parents[4]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.infra.db.models.llm_prompt import LlmUseCaseConfigModel
from app.infra.db.models.llm_release import LlmReleaseSnapshotModel
from app.infra.db.session import SessionLocal
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionContext,
    ExecutionFlags,
    ExecutionUserInput,
    LLMExecutionRequest,
)
from app.llm_orchestration.services.golden_regression_service import GoldenRegressionService
from app.llm_orchestration.services.performance_qualification_service import (
    PerformanceQualificationService,
)

DEFAULT_GOLDEN_PATHS = {
    "natal": "tests/fixtures/golden/natal_test.yaml",
}
MANIFEST_GOLDEN_PATHS = {
    "natal:interpretation:premium:fr-FR": "tests/fixtures/golden/natal_premium_test.yaml",
}
CONTEXT_KEYS = {
    "history",
    "natal_data",
    "chart_json",
    "precision_level",
    "astro_context",
    "conversation_id",
    "persona_id",
    "evidence_catalog",
    "validation_strict",
}


def _load_candidate(path_str: str) -> dict[str, Any]:
    return json.loads(Path(path_str).read_text(encoding="utf-8"))


def _percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    idx = int(round((len(sorted_values) - 1) * p))
    return sorted_values[idx]


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


def _resolve_fixture_input(
    golden_set_path: str,
    *,
    use_case_key: str,
    manifest_entry_id: str,
) -> dict[str, Any]:
    feature, subfeature, plan, locale = manifest_entry_id.split(":", maxsplit=3)
    resolved_path = GoldenRegressionService._resolve_path(golden_set_path)
    fixtures_raw = json.loads(json.dumps([]))
    if resolved_path.suffix.lower() in {".yaml", ".yml"}:
        import yaml

        fixtures_raw = yaml.safe_load(resolved_path.read_text(encoding="utf-8"))
    fixtures = fixtures_raw if isinstance(fixtures_raw, list) else [fixtures_raw]
    fallback_fixture: dict[str, Any] | None = None
    for fixture in fixtures:
        baseline_obs = (fixture or {}).get("baseline", {}).get("obs_snapshot", {})
        if baseline_obs.get("manifest_entry_id") == manifest_entry_id:
            payload = dict((fixture or {}).get("input", {}))
            payload.setdefault("use_case", use_case_key)
            payload.setdefault("locale", locale)
            return payload
        fixture_input = dict((fixture or {}).get("input", {}))
        if (
            fallback_fixture is None
            and fixture_input.get("feature") == feature
            and fixture_input.get("subfeature") == subfeature
        ):
            fallback_fixture = fixture_input

    if fallback_fixture is not None:
        fallback_fixture["feature"] = feature
        fallback_fixture["subfeature"] = subfeature
        fallback_fixture["plan"] = plan
        fallback_fixture["locale"] = locale
        fallback_fixture.setdefault("use_case", use_case_key)
        return fallback_fixture

    raise ValueError(
        f"No fixture in {golden_set_path!r} resolves to manifest entry {manifest_entry_id!r}."
    )


def _split_fixture_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    user_input = dict(payload)
    context: dict[str, Any] = {}
    for key in CONTEXT_KEYS:
        if key in user_input:
            context[key] = user_input.pop(key)
    return user_input, context


def _build_execution_request(
    *,
    use_case_key: str,
    user_input: dict[str, Any],
    context: dict[str, Any],
    prompt_version_id: str,
    snapshot_id: uuid.UUID,
    snapshot_version: str,
    manifest_entry_id: str,
    request_id: str,
) -> LLMExecutionRequest:
    execution_user_input = ExecutionUserInput(
        use_case=str(user_input.get("use_case") or use_case_key),
        locale=str(user_input.get("locale") or "fr-FR"),
        feature=user_input.get("feature"),
        subfeature=user_input.get("subfeature"),
        plan=user_input.get("plan"),
        message=user_input.get("message"),
        question=user_input.get("question"),
        situation=user_input.get("situation"),
        conversation_id=user_input.get("conversation_id"),
        persona_id_override=user_input.get("persona_id"),
    )
    execution_context = ExecutionContext(
        history=context.get("history", []),
        natal_data=context.get("natal_data"),
        chart_json=context.get("chart_json"),
        precision_level=context.get("precision_level"),
        astro_context=context.get("astro_context"),
        extra_context={
            key: value
            for key, value in {
                **context,
                "_override_prompt_version_id": prompt_version_id,
                "_active_snapshot_id": str(snapshot_id),
                "_active_snapshot_version": snapshot_version,
                "_manifest_entry_id": manifest_entry_id,
            }.items()
            if key
            not in {
                "history",
                "natal_data",
                "chart_json",
                "precision_level",
                "astro_context",
            }
        },
    )
    execution_flags = ExecutionFlags(
        evidence_catalog=context.get("evidence_catalog"),
        validation_strict=bool(context.get("validation_strict", False)),
    )
    return LLMExecutionRequest(
        user_input=execution_user_input,
        context=execution_context,
        flags=execution_flags,
        request_id=request_id,
        trace_id=f"{request_id}-trace",
    )


async def _run(
    *,
    candidate_path: str,
    manifest_entry_id: str | None,
    iterations: int,
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

        fixture_payload = _resolve_fixture_input(
            golden_set_path,
            use_case_key=use_case_key,
            manifest_entry_id=selected_manifest_entry_id,
        )
        user_input, context = _split_fixture_payload(fixture_payload)
        user_input["use_case"] = use_case_key

        gateway = LLMGateway()
        latencies_ms: list[float] = []
        success_count = 0
        protection_count = 0
        error_count = 0
        started = time.perf_counter()

        for attempt in range(iterations):
            req_id = f"qualification-{attempt + 1}"
            try:
                start = time.perf_counter()
                await gateway.execute_request(
                    _build_execution_request(
                        use_case_key=use_case_key,
                        user_input=user_input,
                        context=context,
                        prompt_version_id=prompt_version_id,
                        snapshot_id=snapshot.id,
                        snapshot_version=snapshot.version,
                        manifest_entry_id=selected_manifest_entry_id,
                        request_id=req_id,
                    ),
                    db=db,
                )
                latencies_ms.append((time.perf_counter() - start) * 1000)
                success_count += 1
            except Exception as exc:  # noqa: BLE001
                latencies_ms.append((time.perf_counter() - start) * 1000)
                status_code = getattr(exc, "status_code", None)
                if status_code == 429:
                    protection_count += 1
                else:
                    error_count += 1

        elapsed_seconds = max(time.perf_counter() - started, 0.001)
        sorted_latencies = sorted(latencies_ms)
        report = await PerformanceQualificationService.evaluate_run_async(
            family=family,
            profile="smoke",
            total_requests=iterations,
            success_count=success_count,
            protection_count=protection_count,
            error_count=error_count,
            latency_p50_ms=_percentile(sorted_latencies, 0.50),
            latency_p95_ms=_percentile(sorted_latencies, 0.95),
            latency_p99_ms=_percentile(sorted_latencies, 0.99),
            throughput_rps=iterations / elapsed_seconds,
            db=db,
            active_snapshot_id=snapshot.id,
            active_snapshot_version=snapshot.version,
            manifest_entry_id=selected_manifest_entry_id,
            environment="local",
        )
        payload = report.model_dump(mode="json")
        payload["sample"] = {
            "iterations": iterations,
            "use_case_key": use_case_key,
            "prompt_version_id": prompt_version_id,
            "avg_latency_ms": statistics.fmean(latencies_ms) if latencies_ms else 0.0,
        }
        return payload
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a correlated LLM qualification campaign against a candidate snapshot."
    )
    parser.add_argument(
        "--candidate",
        default=str(_BACKEND_ROOT.parent / "artifacts" / "llm-release-candidate.json"),
    )
    parser.add_argument("--manifest-entry-id", default=None)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument(
        "--output",
        default=str(_BACKEND_ROOT.parent / "artifacts" / "llm-qualification-evidence.json"),
    )
    args = parser.parse_args()

    payload = __import__("asyncio").run(
        _run(
            candidate_path=args.candidate,
            manifest_entry_id=args.manifest_entry_id,
            iterations=args.iterations,
        )
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

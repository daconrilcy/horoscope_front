from __future__ import annotations

import logging
import os
import re
import uuid
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.llm_release import LlmReleaseSnapshotModel
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.golden_regression_registry import (
    GOLDEN_REGISTRY,
    GoldenRegressionThresholds,
)
from app.llm_orchestration.models import (
    GoldenRegressionReport,
    GoldenRegressionResult,
)

logger = logging.getLogger(__name__)


class GoldenRegressionService:
    _PLACEHOLDER_PATTERN = re.compile(r"\{\{[^{}]+\}\}")

    @staticmethod
    def _resolve_path(path_str: str) -> Path:
        candidate = Path(path_str)
        if candidate.exists():
            return candidate

        backend_root = Path(__file__).resolve().parents[3]
        backend_relative = backend_root / candidate
        if backend_relative.exists():
            return backend_relative

        return candidate

    @staticmethod
    def _canonicalize(data: Any) -> Any:
        """
        Normalise les données volatiles pour éviter les faux positifs (Story 66.36 AC17).
        En pratique, on compare surtout les structures (shape).
        """
        if isinstance(data, dict):
            # Sort keys for deterministic comparison
            return {k: GoldenRegressionService._canonicalize(v) for k, v in sorted(data.items())}
        if isinstance(data, list):
            # We don't sort all lists as order might matter,
            # but we could sort if specifically requested.
            return [GoldenRegressionService._canonicalize(x) for x in data]
        return data

    @staticmethod
    def _get_shape(data: Any) -> Any:
        """Extrait la structure des données (types et présence de clés)."""
        if isinstance(data, dict):
            return {
                k: GoldenRegressionService._get_shape(v)
                for k, v in GoldenRegressionService._canonicalize(data).items()
            }
        if isinstance(data, list):
            if not data:
                return "list[]"
            # Represent list as the shape of its first element
            return [GoldenRegressionService._get_shape(data[0])]
        return type(data).__name__

    @staticmethod
    def _normalize_scalar(value: Any) -> Any:
        if hasattr(value, "value"):
            return value.value
        return value

    @classmethod
    def _collect_placeholder_paths(cls, data: Any, path: str = "$") -> List[str]:
        placeholders: List[str] = []
        if isinstance(data, dict):
            for key, value in data.items():
                placeholders.extend(cls._collect_placeholder_paths(value, f"{path}.{key}"))
            return placeholders
        if isinstance(data, list):
            for index, value in enumerate(data):
                placeholders.extend(cls._collect_placeholder_paths(value, f"{path}[{index}]"))
            return placeholders
        if isinstance(data, str) and cls._PLACEHOLDER_PATTERN.search(data):
            placeholders.append(path)
        return placeholders

    @classmethod
    def _compare_structure(
        cls,
        result: Any,
        baseline: Dict[str, Any],
    ) -> tuple[Dict[str, Any], bool]:
        diffs: Dict[str, Any] = {}
        invalid = False

        if "validation_status" not in baseline:
            diffs["validation_status"] = {
                "error": "Missing baseline validation_status",
                "severity": "invalid",
            }
            invalid = True
        else:
            actual_validation_status = getattr(result.meta, "validation_status", None)
            expected_validation_status = baseline.get("validation_status")
            if actual_validation_status != expected_validation_status:
                diffs["validation_status"] = {
                    "actual": actual_validation_status,
                    "expected": expected_validation_status,
                    "severity": "blocking",
                }

        if "output_shape" not in baseline:
            diffs["output_shape"] = {
                "error": "Missing baseline output_shape",
                "severity": "invalid",
            }
            invalid = True
        else:
            actual_canonical = cls._canonicalize(result.structured_output)
            actual_shape = cls._get_shape(actual_canonical)
            expected_shape = cls._canonicalize(baseline.get("output_shape"))
            if actual_shape != expected_shape:
                diffs["output_shape"] = {
                    "actual": actual_shape,
                    "expected": expected_shape,
                    "severity": "blocking",
                }

        placeholder_paths = cls._collect_placeholder_paths(result.structured_output)
        if placeholder_paths:
            diffs["placeholder_survivors"] = {
                "actual": placeholder_paths,
                "expected": [],
                "severity": "blocking",
            }

        return diffs, invalid

    @staticmethod
    def _compare_obs(
        actual: Any, expected: Any, thresholds: GoldenRegressionThresholds
    ) -> Dict[str, Any]:
        """Compare le snapshot d'observabilité selon les seuils (AC8, AC18)."""
        diffs = {}
        if not actual:
            return {
                "snapshot": {
                    "error": "Missing actual observability snapshot",
                    "severity": "invalid",
                }
            }

        # 1. Strict fields (blocking if mismatch)
        for field in thresholds.strict_obs_fields:
            act_val = GoldenRegressionService._normalize_scalar(getattr(actual, field, None))
            exp_val = GoldenRegressionService._normalize_scalar(expected.get(field))
            if act_val != exp_val:
                diffs[field] = {"actual": act_val, "expected": exp_val, "severity": "blocking"}

        # 2. Thresholded fields (constrained if mismatch)
        for field, tolerance in thresholds.thresholded_obs_fields.items():
            act_val = GoldenRegressionService._normalize_scalar(getattr(actual, field, None))
            exp_val = GoldenRegressionService._normalize_scalar(expected.get(field))
            if act_val is not None and exp_val is not None:
                try:
                    diff_abs = abs(act_val - exp_val)
                    if diff_abs > (exp_val * tolerance):
                        diffs[field] = {
                            "actual": act_val,
                            "expected": exp_val,
                            "severity": "constrained",
                        }
                except (TypeError, ValueError):
                    if act_val != exp_val:
                        diffs[field] = {
                            "actual": act_val,
                            "expected": exp_val,
                            "severity": "constrained",
                        }

        return diffs

    @staticmethod
    def _derive_family(use_case_key: str, fixture: Dict[str, Any]) -> str:
        fixture_family = fixture.get("family")
        if fixture_family in GOLDEN_REGISTRY:
            return fixture_family

        input_payload = fixture.get("input", {})
        feature = input_payload.get("feature")
        if feature in GOLDEN_REGISTRY:
            return feature

        match = re.match(r"^([a-z]+)", use_case_key)
        if match:
            candidate_family = match.group(1)
            if candidate_family in GOLDEN_REGISTRY:
                return candidate_family
        return "default"

    @classmethod
    def _resolve_manifest_entry_id(
        cls,
        manifest: object,
        fixtures: List[Dict[str, Any]],
        use_case_key: str,
    ) -> str:
        if not isinstance(manifest, Mapping):
            raise ValueError("Golden regression rejected: active snapshot manifest is invalid.")

        targets = manifest.get("targets")
        if not isinstance(targets, Mapping) or not targets:
            raise ValueError(
                "Golden regression rejected: active snapshot manifest does not expose targets."
            )

        candidate_keys: set[str] = set()
        for fixture in fixtures:
            baseline_obs = fixture.get("baseline", {}).get("obs_snapshot", {})
            explicit_key = baseline_obs.get("manifest_entry_id")
            if explicit_key:
                if explicit_key not in targets:
                    raise ValueError(
                        "Golden regression rejected: fixture manifest_entry_id is not present "
                        "in active snapshot manifest."
                    )
                candidate_keys.add(str(explicit_key))
                continue

            input_payload = fixture.get("input", {})
            family = cls._derive_family(use_case_key, fixture)
            subfeature = input_payload.get("subfeature")
            plan = input_payload.get("plan")
            locale = input_payload.get("locale", "fr-FR")
            exact_key = f"{family}:{subfeature}:{plan}:{locale}"
            if exact_key in targets:
                candidate_keys.add(exact_key)
                continue

            loose_matches = [
                key
                for key in targets
                if key.startswith(f"{family}:") and key.endswith(f":{plan}:{locale}")
            ]
            if len(loose_matches) == 1:
                candidate_keys.add(loose_matches[0])

        if not candidate_keys:
            if len(targets) == 1:
                return str(next(iter(targets)))
            raise ValueError(
                "Golden regression rejected: manifest_entry_id could not be resolved from "
                "fixtures against active snapshot manifest."
            )

        if len(candidate_keys) != 1:
            raise ValueError(
                "Golden regression rejected: fixtures resolve to multiple manifest entries."
            )

        return next(iter(candidate_keys))

    @classmethod
    async def _resolve_release_context(
        cls,
        db: Session,
        fixtures: List[Dict[str, Any]],
        use_case_key: str,
        active_snapshot_id: Optional[uuid.UUID],
        active_snapshot_version: Optional[str],
    ) -> tuple[uuid.UUID, str, str]:
        from app.llm_orchestration.services.release_service import ReleaseService

        resolved_snapshot_id = active_snapshot_id or await ReleaseService.get_active_release_id(db)
        if not resolved_snapshot_id:
            raise ValueError(
                "Golden regression rejected: no active snapshot ID could be resolved."
            )

        stmt = select(LlmReleaseSnapshotModel).where(
            LlmReleaseSnapshotModel.id == resolved_snapshot_id
        )
        snapshot = db.execute(stmt).scalar_one_or_none()
        if snapshot is None:
            raise ValueError("Golden regression rejected: active snapshot could not be loaded.")

        resolved_snapshot_version = active_snapshot_version or snapshot.version
        if not resolved_snapshot_version:
            raise ValueError(
                "Golden regression rejected: no active snapshot version could be resolved."
            )

        manifest_entry_id = cls._resolve_manifest_entry_id(
            snapshot.manifest,
            fixtures,
            use_case_key,
        )
        return resolved_snapshot_id, resolved_snapshot_version, manifest_entry_id

    @staticmethod
    def _check_legacy(
        result: Any, actual: Any, thresholds: GoldenRegressionThresholds
    ) -> List[str]:
        """Détecte les chemins legacy interdits (AC10)."""
        errors = []
        if not actual:
            return ["Missing observability snapshot"]

        path_val = actual.execution_path_kind
        if hasattr(path_val, "value"):
            path_val = path_val.value

        if any(
            path_val == (p.value if hasattr(p, "value") else p)
            for p in thresholds.forbidden_execution_paths
        ):
            errors.append(f"Forbidden legacy execution path: {path_val}")

        fallback_val = actual.fallback_kind
        if fallback_val:
            if hasattr(fallback_val, "value"):
                fallback_val = fallback_val.value
            if any(
                fallback_val == (f.value if hasattr(f, "value") else f)
                for f in thresholds.forbidden_fallbacks
            ):
                errors.append(f"Forbidden legacy fallback kind: {fallback_val}")

        execution_profile_source = getattr(result.meta, "execution_profile_source", None)
        if execution_profile_source in thresholds.forbidden_execution_profile_sources:
            errors.append(
                f"Forbidden legacy execution profile source: {execution_profile_source}"
            )

        return errors

    @classmethod
    async def run_campaign(
        cls,
        use_case_key: str,
        prompt_version_id: str,
        golden_set_path: str,
        db: Session,
        active_snapshot_id: Optional[uuid.UUID] = None,
        active_snapshot_version: Optional[str] = None,
    ) -> GoldenRegressionReport:
        """
        Exécute une campagne de non-régression golden (Story 66.36).
        """
        resolved_path = cls._resolve_path(golden_set_path)
        if not resolved_path.exists():
            logger.warning("golden_set_not_found path=%s", golden_set_path)
            return GoldenRegressionReport(
                environment="local",
                verdict="invalid",
                total=0,
                passed=0,
                failed=0,
                constrained=0,
                results=[],
            )

        fixtures = []
        if resolved_path.is_dir():
            for filename in os.listdir(resolved_path):
                if filename.endswith(".yaml") or filename.endswith(".yml"):
                    with (resolved_path / filename).open("r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        fixtures.extend(data if isinstance(data, list) else [data])
        else:
            with resolved_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                fixtures = data if isinstance(data, list) else [data]

        try:
            (
                resolved_snapshot_id,
                resolved_snapshot_version,
                resolved_manifest_entry_id,
            ) = await cls._resolve_release_context(
                db=db,
                fixtures=fixtures,
                use_case_key=use_case_key,
                active_snapshot_id=active_snapshot_id,
                active_snapshot_version=active_snapshot_version,
            )
        except ValueError as exc:
            logger.warning(
                "golden_regression_invalid_context use_case=%s reason=%s",
                use_case_key,
                exc,
            )
            return GoldenRegressionReport(
                environment="local",
                verdict="invalid",
                total=len(fixtures),
                passed=0,
                failed=0,
                constrained=0,
                results=[
                    GoldenRegressionResult(
                        fixture_id="campaign",
                        family="default",
                        verdict="invalid",
                        details=str(exc),
                    )
                ],
            )

        gateway = LLMGateway()
        results = []
        passed_count = 0
        failed_count = 0
        constrained_count = 0
        invalid_count = 0

        for fixture in fixtures:
            fixture_id = fixture.get("fixture_id", fixture.get("id", "unknown"))
            user_input = dict(fixture.get("input", {}))
            baseline = fixture.get("baseline", {})
            family = cls._derive_family(use_case_key, fixture)
            thresholds = GOLDEN_REGISTRY.get(family, GOLDEN_REGISTRY["default"])

            # Ensure minimal input
            if "locale" not in user_input:
                user_input["locale"] = "fr-FR"
            if "use_case" not in user_input:
                user_input["use_case"] = use_case_key

            try:
                # Execution with override
                context = {
                    "_override_prompt_version_id": prompt_version_id,
                    "is_golden_replay": True,
                }

                result = await gateway.execute(
                    use_case=use_case_key,
                    user_input=user_input,
                    context=context,
                    request_id=f"golden-{fixture_id}",
                    trace_id=f"golden-campaign-{use_case_key}",
                    db=db,
                )

                # 1. Structural diff (AC6)
                diffs_structure, invalid_structure = cls._compare_structure(result, baseline)

                # 2. Observability diff (AC8)
                actual_obs = result.meta.obs_snapshot
                expected_obs = baseline.get("obs_snapshot", {})
                # Canonicalize expected obs for comparison
                if isinstance(expected_obs, dict):
                    expected_obs = cls._canonicalize(expected_obs)

                diffs_obs = cls._compare_obs(actual_obs, expected_obs, thresholds)

                # 3. Anti-legacy check (AC10)
                legacy_errors = cls._check_legacy(result, actual_obs, thresholds)

                # Verdict for this fixture
                verdict: Literal["pass", "fail", "constrained", "invalid"] = "pass"

                has_invalid_obs = any(d.get("severity") == "invalid" for d in diffs_obs.values())
                has_blocking_obs = any(d.get("severity") == "blocking" for d in diffs_obs.values())
                has_constrained_obs = any(
                    d.get("severity") == "constrained" for d in diffs_obs.values()
                )
                has_blocking_structure = any(
                    d.get("severity") == "blocking" for d in diffs_structure.values()
                )
                if invalid_structure or has_invalid_obs:
                    verdict = "invalid"
                elif legacy_errors or has_blocking_obs or has_blocking_structure:
                    verdict = "fail"
                elif has_constrained_obs:
                    verdict = "constrained"

                if verdict == "pass":
                    passed_count += 1
                elif verdict == "fail":
                    failed_count += 1
                elif verdict == "constrained":
                    constrained_count += 1
                else:
                    invalid_count += 1

                results.append(
                    GoldenRegressionResult(
                        fixture_id=fixture_id,
                        family=family,
                        verdict=verdict,
                        diffs_structure=diffs_structure,
                        diffs_obs=diffs_obs,
                        legacy_errors=legacy_errors,
                    )
                )

            except Exception:
                failed_count += 1
                results.append(
                    GoldenRegressionResult(
                        fixture_id=fixture_id,
                        family=family,
                        verdict="fail",
                        details="Execution error during golden regression campaign.",
                    )
                )

        # Global verdict
        global_verdict: Literal["pass", "fail", "constrained", "invalid"] = "pass"
        if invalid_count > 0:
            global_verdict = "invalid"
        elif failed_count > 0:
            global_verdict = "fail"
        elif constrained_count > 0:
            global_verdict = "constrained"

        return GoldenRegressionReport(
            active_snapshot_id=resolved_snapshot_id,
            active_snapshot_version=resolved_snapshot_version,
            manifest_entry_id=resolved_manifest_entry_id,
            environment="local",
            verdict=global_verdict,
            total=len(fixtures),
            passed=passed_count,
            failed=failed_count,
            constrained=constrained_count,
            results=results,
            generated_at=datetime.now(timezone.utc),
        )

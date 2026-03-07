from __future__ import annotations

import logging
import os
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import EvalFixtureResult, EvalReport

logger = logging.getLogger(__name__)


def _resolve_fixtures_path(fixtures_path: str) -> Path:
    candidate = Path(fixtures_path)
    if candidate.exists():
        return candidate

    backend_root = Path(__file__).resolve().parents[3]
    backend_relative = backend_root / candidate
    if backend_relative.exists():
        return backend_relative

    return candidate


async def run_eval(
    use_case_key: str,
    prompt_version_id: str,
    fixtures_path: str,
    db: Session,
) -> EvalReport:
    """
    Runs an evaluation harness for a specific prompt version using offline fixtures.
    """
    resolved_fixtures_path = _resolve_fixtures_path(fixtures_path)

    if not resolved_fixtures_path.exists():
        # Return empty report if no fixtures found
        return EvalReport(
            use_case=use_case_key,
            prompt_version_id=prompt_version_id,
            total=0,
            passed=0,
            failed=0,
            failure_rate=0.0,
            blocked_publication=False,
            results=[],
        )

    fixtures = []
    if resolved_fixtures_path.is_dir():
        for filename in os.listdir(resolved_fixtures_path):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                with (resolved_fixtures_path / filename).open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, list):
                        fixtures.extend(data)
                    else:
                        fixtures.append(data)
    else:
        with resolved_fixtures_path.open("r", encoding="utf-8") as f:
            fixtures = yaml.safe_load(f)

    gateway = LLMGateway()
    results = []
    passed_count = 0

    for fixture in fixtures:
        fixture_id = fixture.get("id", "unknown")
        # M5: Avoid mutating the original fixture dict
        user_input = dict(fixture.get("input", {}))
        expected_schema_valid = fixture.get("expected_schema_valid", True)
        expected_fields = fixture.get("expected_fields", {})

        # Ensure locale and use_case are in input
        if "locale" not in user_input:
            user_input["locale"] = "fr-FR"
        if "use_case" not in user_input:
            user_input["use_case"] = use_case_key

        try:
            # We use the override prompt version
            context = {"_override_prompt_version_id": prompt_version_id}

            # Execute gateway
            result = await gateway.execute(
                use_case=use_case_key,
                user_input=user_input,
                context=context,
                request_id=f"eval-{fixture_id}",
                trace_id=f"eval-{use_case_key}",
                db=db,
            )

            validation_errors = []
            field_mismatches = []

            # Check schema validity
            is_valid = result.meta.validation_status in ["valid", "repair_success"]
            if is_valid != expected_schema_valid:
                validation_errors.append(
                    f"Schema validity mismatch: expected {expected_schema_valid}, got {is_valid} ({result.meta.validation_status})"  # noqa: E501
                )

            # Check expected fields
            if result.structured_output:
                for field, constraints in expected_fields.items():
                    val = result.structured_output.get(field)
                    if val is None:
                        field_mismatches.append({"field": field, "error": "Missing field"})
                        continue

                    if "min_length" in constraints and isinstance(val, str):
                        if len(val) < constraints["min_length"]:
                            field_mismatches.append(
                                {
                                    "field": field,
                                    "error": f"Value too short: {len(val)} < {constraints['min_length']}",  # noqa: E501
                                }
                            )

                    if "min_items" in constraints and isinstance(val, list):
                        if len(val) < constraints["min_items"]:
                            field_mismatches.append(
                                {
                                    "field": field,
                                    "error": f"Too few items: {len(val)} < {constraints['min_items']}",  # noqa: E501
                                }
                            )

            status = "passed" if not validation_errors and not field_mismatches else "failed"
            if status == "passed":
                passed_count += 1

            results.append(
                EvalFixtureResult(
                    fixture_id=fixture_id,
                    status=status,
                    validation_errors=validation_errors,
                    field_mismatches=field_mismatches,
                )
            )

        except Exception as e:
            results.append(
                EvalFixtureResult(
                    fixture_id=fixture_id,
                    status="failed",
                    validation_errors=[f"Execution error: {str(e)}"],
                )
            )

    total = len(fixtures)
    failed_count = total - passed_count
    failure_rate = (failed_count / total) if total > 0 else 0.0

    return EvalReport(
        use_case=use_case_key,
        prompt_version_id=prompt_version_id,
        total=total,
        passed=passed_count,
        failed=failed_count,
        failure_rate=failure_rate,
        blocked_publication=False,  # Will be set by caller
        results=results,
    )

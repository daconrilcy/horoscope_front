from __future__ import annotations

import json
from typing import Any, List, Optional

from jsonschema import Draft7Validator
from pydantic import BaseModel


class ValidationResult(BaseModel):
    valid: bool
    parsed: Optional[dict[str, Any]] = None
    errors: List[str] = []
    warnings: List[str] = []


def validate_output(raw_output: str, json_schema: dict[str, Any]) -> ValidationResult:
    """
    Validates LLM output against a JSON Schema.
    Includes special handling for the 'evidence' field pattern.
    """
    try:
        # 1. Parse JSON
        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError as e:
            return ValidationResult(valid=False, errors=[f"JSON syntax error: {str(e)}"])

        # 2. Validate against schema
        validator = Draft7Validator(json_schema)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

        error_messages = []
        for error in errors:
            path = ".".join([str(p) for p in error.path]) or "root"
            error_messages.append(f"[{path}] {error.message}")

        if error_messages:
            return ValidationResult(valid=False, parsed=data, errors=error_messages)

        # 3. Specific validation for 'evidence' (pattern check + space check)
        warnings = []
        if "evidence" in data and isinstance(data["evidence"], list):
            # The pattern is already checked by jsonschema if provided in schema,
            # but we add a warning for free text (spaces) as requested.
            for i, item in enumerate(data["evidence"]):
                if not isinstance(item, str):
                    continue
                if " " in item:
                    warnings.append(
                        f"evidence[{i}] contains spaces: '{item}'. Identifiers must be UPPER_SNAKE_CASE."  # noqa: E501
                    )

        return ValidationResult(valid=True, parsed=data, warnings=warnings)

    except Exception as e:
        return ValidationResult(valid=False, errors=[f"Unexpected validation error: {str(e)}"])

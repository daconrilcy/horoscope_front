from __future__ import annotations

from typing import Any, List

from jsonschema import Draft7Validator
from pydantic import BaseModel


class InputValidationResult(BaseModel):
    valid: bool
    errors: List[str] = []


def validate_input(
    user_input: dict[str, Any], input_schema: dict[str, Any] | None
) -> InputValidationResult:
    """
    Validates user input against a JSON Schema.
    """
    if input_schema is None:
        return InputValidationResult(valid=True)

    try:
        validator = Draft7Validator(input_schema)
        errors = sorted(validator.iter_errors(user_input), key=lambda e: e.path)

        error_messages = []
        for error in errors:
            path = ".".join([str(p) for p in error.path]) or "root"
            error_messages.append(f"[{path}] {error.message}")

        if error_messages:
            return InputValidationResult(valid=False, errors=error_messages)

        return InputValidationResult(valid=True)

    except Exception as e:
        return InputValidationResult(
            valid=False, errors=[f"Unexpected input validation error: {str(e)}"]
        )

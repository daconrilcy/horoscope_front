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


def validate_output(
    raw_output: str,
    json_schema: dict[str, Any],
    evidence_catalog: Optional[List[str]] = None,
    strict: bool = False,
) -> ValidationResult:
    """
    Validates LLM output against a JSON Schema.
    Includes special handling for the 'evidence' field pattern.

    Args:
        raw_output: The raw JSON string from LLM.
        json_schema: The schema to validate against.
        evidence_catalog: Optional list of authorized identifiers for 'evidence'.
        strict: If True, evidence catalog misses or bidirectional rule violations
                are treated as errors instead of warnings.
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

        # 3. Specific validation for 'evidence' (pattern check + catalog + bidirectional)
        warnings = []
        evidence = data.get("evidence", [])
        if isinstance(evidence, list):
            # 3.1 Catalog check (hallucination detection)
            if evidence_catalog is not None:
                catalog_set = set(evidence_catalog)
                for item in evidence:
                    if not isinstance(item, str):
                        continue
                    if item not in catalog_set:
                        msg = f"Hallucinated evidence: '{item}' not in catalog."
                        if strict:
                            error_messages.append(msg)
                        else:
                            warnings.append(msg)

            # 3.2 Bidirectional Rule (Story 30.5 M4)
            # Every evidence item must be mentioned in text fields.
            # We search in: summary, highlights, advice, and sections[].content
            text_blobs = []
            if "summary" in data:
                text_blobs.append(data["summary"])
            if "highlights" in data:
                text_blobs.extend(data["highlights"])
            if "advice" in data:
                text_blobs.extend(data["advice"])
            if "sections" in data and isinstance(data["sections"], list):
                for s in data["sections"]:
                    if "content" in s:
                        text_blobs.append(s["content"])

            full_text = "\n".join(text_blobs).lower()
            # Most evidence are UPPER_SNAKE_CASE in evidence, but can be natural in text
            # However, the rule says "mentioned", and for some models they use codes.
            # If the prompt says "mention identifiers", we check for them.
            for item in evidence:
                if not isinstance(item, str):
                    continue
                # For natal, we often have SUN_LEO but text says "Soleil en Lion".
                # But GPT-5 rules say "Identifier mentioned".
                # To be safe and avoid false positives, we check for identifier presence
                # OR natural mapping if possible.
                # Here we implement strict identifier presence check if strict=True.
                if item.lower() not in full_text:
                    msg = f"Orphan evidence: '{item}' present in evidence but never mentioned in text."  # noqa: E501
                    if strict:
                        # Only fail if strict, as this rule is experimental
                        error_messages.append(msg)
                    else:
                        warnings.append(msg)

            # 3.3 Space check (historical constraint)
            for i, item in enumerate(evidence):
                if not isinstance(item, str):
                    continue
                if " " in item:
                    warnings.append(f"[evidence.{i}] Item contains spaces: '{item}'")

        if error_messages:
            return ValidationResult(valid=False, parsed=data, errors=error_messages)

        return ValidationResult(valid=True, parsed=data, warnings=warnings)

    except Exception as e:
        return ValidationResult(valid=False, errors=[f"Unexpected validation error: {str(e)}"])

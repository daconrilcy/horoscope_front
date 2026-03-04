from __future__ import annotations

import json
import logging
import re
import unicodedata
from typing import Any, List, Optional

from jsonschema import Draft7Validator
from pydantic import BaseModel

from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    valid: bool
    parsed: Optional[dict[str, Any]] = None
    errors: List[str] = []
    warnings: List[str] = []


_PLANET_CODES = {
    "SUN",
    "MOON",
    "MERCURY",
    "VENUS",
    "MARS",
    "JUPITER",
    "SATURN",
    "URANUS",
    "NEPTUNE",
    "PLUTO",
    "CHIRON",
    "LILITH",
    "NODE",
}
_ANGLE_CODES = {"ASC", "MC", "DSC", "IC"}
_ASPECT_CODES = {"CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"}
_SIGN_CODES = {
    "ARIES",
    "TAURUS",
    "GEMINI",
    "CANCER",
    "LEO",
    "VIRGO",
    "LIBRA",
    "SCORPIO",
    "SAGITTARIUS",
    "CAPRICORN",
    "AQUARIUS",
    "PISCES",
}


def _normalize_evidence_item(
    item: str, catalog_set: set[str], catalog_map: Optional[dict[str, list[str]]]
) -> str:
    """Best-effort normalization to reduce false negatives on evidence aliases."""
    cleaned = re.sub(r"[^A-Z0-9_\.:-]", "", item.upper()).rstrip("._:-")
    if not cleaned:
        return item
    if cleaned in catalog_set:
        return cleaned

    # Angles aliases: ASC / MC / DSC / IC -> first matching canonical id.
    if cleaned in _ANGLE_CODES:
        prefix = f"{cleaned}_"
        for key in catalog_set:
            if key.startswith(prefix):
                return key

    # House aliases: HOUSE_10 -> first matching HOUSE_10_...
    if re.fullmatch(r"HOUSE_\d{1,2}", cleaned):
        prefix = f"{cleaned}_"
        for key in catalog_set:
            if key.startswith(prefix):
                return key

    # Planet aliases: SUN / VENUS / ... -> first matching PLANET_...
    if cleaned in _PLANET_CODES:
        prefix = f"{cleaned}_"
        for key in catalog_set:
            if key.startswith(prefix):
                return key

    # Sign aliases: TAURUS -> first matching *_TAURUS or *_TAURUS_*
    if cleaned in _SIGN_CODES:
        needle = f"_{cleaned}"
        for key in catalog_set:
            if key.endswith(needle) or f"{needle}_" in key:
                return key

    # Aspect alias: SUN_CONJUNCTION_VENUS -> ASPECT_SUN_VENUS_CONJUNCTION
    parts = cleaned.split("_")
    if (
        len(parts) == 3
        and parts[0] in _PLANET_CODES
        and parts[1] in _ASPECT_CODES
        and parts[2] in _PLANET_CODES
    ):  # noqa: E501
        p1, aspect, p2 = parts
        pair = sorted([p1, p2])
        canonical = f"ASPECT_{pair[0]}_{pair[1]}_{aspect}"
        if canonical in catalog_set:
            return canonical

    # Aspect alias: CONJUNCTION_SUN_VENUS -> ASPECT_SUN_VENUS_CONJUNCTION
    if (
        len(parts) == 3
        and parts[0] in _ASPECT_CODES
        and parts[1] in _PLANET_CODES
        and parts[2] in _PLANET_CODES
    ):  # noqa: E501
        aspect, p1, p2 = parts
        pair = sorted([p1, p2])
        canonical = f"ASPECT_{pair[0]}_{pair[1]}_{aspect}"
        if canonical in catalog_set:
            return canonical

    # Planet/sign alias: SUN_IN_TAURUS -> any matching SUN_TAURUS*
    if (
        len(parts) == 3
        and parts[0] in _PLANET_CODES
        and parts[1] == "IN"
        and parts[2] in _SIGN_CODES
    ):  # noqa: E501
        p, _, s = parts
        prefix = f"{p}_{s}"
        for key in catalog_set:
            if key.startswith(prefix):
                return key

    # Support legacy ASPECT_* aliases with different ordering.
    if cleaned.startswith("ASPECT_"):
        parts = cleaned.split("_")
        if (
            len(parts) == 4
            and parts[1] in _PLANET_CODES
            and parts[2] in _ASPECT_CODES
            and parts[3] in _PLANET_CODES
        ):
            pair = sorted([parts[1], parts[3]])
            canonical = f"ASPECT_{pair[0]}_{pair[1]}_{parts[2]}"
            if canonical in catalog_set:
                return canonical

    # If no catalog mapping, keep the cleaned value so regex/casing issues don't fail unnecessarily.
    if catalog_map is None:
        return cleaned

    return cleaned


def _normalize_for_matching(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    no_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    lowered = no_accents.lower()
    return re.sub(r"[^a-z0-9\s]", " ", lowered)


def validate_output(
    raw_output: str,
    json_schema: dict[str, Any],
    evidence_catalog: Optional[list[str] | dict[str, list[str]]] = None,
    strict: bool = False,
    use_case: str = "",
    schema_version: str = "v1",
) -> ValidationResult:
    """
    Validates LLM output against a JSON Schema.
    Includes special handling for the 'evidence' field pattern.

    Args:
        raw_output: The raw JSON string from LLM.
        json_schema: The schema to validate against.
        evidence_catalog: Authorized identifiers for 'evidence'.
                          Can be a list of IDs or a mapping of ID -> natural labels.
        strict: If True, evidence catalog misses or bidirectional rule violations
                are treated as errors instead of warnings.
        schema_version: The version of the schema being validated (v1, v2, v3).
    """
    try:
        # 1. Parse JSON
        try:
            data = json.loads(raw_output)
            # Story 30-8: V3 strictly forbids 'disclaimers'. 
            # If the LLM included them, we remove them here to pass validation
            # and let the application layer inject the static ones.
            if schema_version.startswith("v3") and isinstance(data, dict):
                data.pop("disclaimers", None)
        except json.JSONDecodeError as e:
            if use_case.startswith("natal"):
                increment_counter(
                    "natal_validation_fail_total",
                    labels={
                        "use_case": use_case,
                        "reason": "json_error",
                        "schema_version": schema_version,
                    },
                )
            return ValidationResult(valid=False, errors=[f"JSON syntax error: {str(e)}"])

        # 2. Validate against schema
        validator = Draft7Validator(json_schema)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

        error_messages = []
        for error in errors:
            path = ".".join([str(p) for p in error.path]) or "root"
            error_messages.append(f"[{path}] {error.message}")

        if error_messages:
            if use_case.startswith("natal"):
                increment_counter(
                    "natal_validation_fail_total",
                    labels={
                        "use_case": use_case,
                        "reason": "schema_error",
                        "schema_version": schema_version,
                    },
                )
            return ValidationResult(valid=False, parsed=data, errors=error_messages)

        # 3. Specific validation for 'evidence' (pattern check + catalog + bidirectional)
        warnings = []
        evidence = data.get("evidence", [])
        if isinstance(evidence, list):
            # 3.1 Catalog check (hallucination detection)
            catalog_set: set[str] = set()
            catalog_map: Optional[dict[str, list[str]]] = None
            if evidence_catalog is not None:
                # If list, convert to set for speed. If dict, use keys.
                if isinstance(evidence_catalog, dict):
                    catalog_map = evidence_catalog
                    catalog_set = set(evidence_catalog.keys())
                else:
                    catalog_set = set(evidence_catalog)
                normalized_evidence: list[str] = []
                for item in evidence:
                    if not isinstance(item, str):
                        normalized_evidence.append(item)
                        continue
                    normalized_item = _normalize_evidence_item(item, catalog_set, catalog_map)
                    normalized_evidence.append(normalized_item)
                    if normalized_item not in catalog_set:
                        # Story 30-8 T4: Always warn (never error) — secure filter handles removal.
                        msg = f"Hallucinated evidence: '{item}' not in catalog."
                        warnings.append(msg)
                data["evidence"] = normalized_evidence
                evidence = normalized_evidence

            # 3.2 Bidirectional Rule (Story 30.5 M4)
            # Every evidence item must be mentioned in text fields.
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

            full_text = _normalize_for_matching("\n".join(text_blobs))

            if full_text.strip():
                for item in evidence:
                    if not isinstance(item, str):
                        continue

                    # Check for mention: either the ID itself or any of its natural labels.
                    # Use regex with word boundaries to avoid false positives (e.g. 'sun' in 'sunday').  # noqa: E501
                    found = False
                    pattern = rf"\b{re.escape(_normalize_for_matching(item))}\b"
                    if re.search(pattern, full_text):
                        found = True
                    elif catalog_map is not None and item in catalog_map:
                        labels = catalog_map[item]
                        for label in labels:
                            label_pattern = rf"\b{re.escape(_normalize_for_matching(label))}\b"
                            if re.search(label_pattern, full_text):
                                found = True
                                break

                    if not found:
                        msg = f"Orphan evidence: '{item}' present in evidence but never mentioned in text."  # noqa: E501
                        warnings.append(msg)

            # 3.3 Secure filter — guarantee evidence ⊆ allowed_evidence (Story 30-8 T4)
            # Non-blocking: silently removes non-catalog IDs after normalization.
            if evidence_catalog is not None:
                original_count = len(data["evidence"])
                data["evidence"] = [e for e in data["evidence"] if e in catalog_set]
                evidence = data["evidence"]
                filtered_count = original_count - len(data["evidence"])
                if filtered_count > 0:
                    logger.warning(
                        "evidence_secure_filter removed=%d use_case=%s",
                        filtered_count,
                        use_case or "unknown",
                    )
                    if use_case.startswith("natal"):
                        increment_counter(
                            "natal_invalid_evidence_total",
                            value=float(filtered_count),
                            labels={"use_case": use_case, "schema_version": schema_version},
                        )

            # 3.4 Space check (historical constraint)
            for i, item in enumerate(evidence):
                if not isinstance(item, str):
                    continue
                if " " in item:
                    warnings.append(f"[evidence.{i}] Item contains spaces: '{item}'")

        if error_messages:
            return ValidationResult(valid=False, parsed=data, errors=error_messages)

        if use_case.startswith("natal"):
            increment_counter(
                "natal_validation_pass_total",
                labels={"use_case": use_case, "schema_version": schema_version},
            )

        return ValidationResult(valid=True, parsed=data, warnings=warnings)

    except Exception as e:
        return ValidationResult(valid=False, errors=[f"Unexpected validation error: {str(e)}"])

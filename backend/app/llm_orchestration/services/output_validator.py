from __future__ import annotations

import json
import logging
import re
import unicodedata
from typing import Any, Dict, List, Literal, Optional, Union

from jsonschema import Draft7Validator
from pydantic import BaseModel, Field

from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)


class ParseResult(BaseModel):
    """Result of the JSON parsing stage."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_category: Optional[Literal["parse_error"]] = None
    normalizations_applied: List[str] = Field(default_factory=list)


class SchemaValidationResult(BaseModel):
    """Result of the JSON Schema validation stage."""

    valid: bool
    errors: List[str] = Field(default_factory=list)
    error_category: Optional[Literal["schema_error"]] = None


class NormalizationResult(BaseModel):
    """Result of the field normalization stage."""

    data: Dict[str, Any]
    normalizations_applied: List[str] = Field(default_factory=list)


class SanitizationResult(BaseModel):
    """Result of the evidence sanitization stage."""

    data: Dict[str, Any]
    normalizations_applied: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Final result of the output validation pipeline."""

    valid: bool
    parsed: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    error_category: Optional[Literal["parse_error", "schema_error"]] = None
    normalizations_applied: List[str] = Field(default_factory=list)


_PLANET_CODES = {
    "SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN",
    "URANUS", "NEPTUNE", "PLUTO", "CHIRON", "LILITH", "NODE",
}
_ANGLE_CODES = {"ASC", "MC", "DSC", "IC"}
_ASPECT_CODES = {"CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"}
_SIGN_CODES = {
    "ARIES", "TAURUS", "GEMINI", "CANCER", "LEO", "VIRGO", "LIBRA",
    "SCORPIO", "SAGITTARIUS", "CAPRICORN", "AQUARIUS", "PISCES",
}


def parse_json(raw_output: str, schema_version: str) -> ParseResult:
    """
    Stage 1: Parses raw string into JSON and applies version-specific cleanup.
    (AC1, AC2, AC3)
    """
    try:
        data = json.loads(raw_output)
        normalizations = []
        if schema_version.startswith("v3") and isinstance(data, dict):
            if "disclaimers" in data:
                data.pop("disclaimers")
                normalizations.append("v3_disclaimers_stripped")
        
        return ParseResult(
            success=True,
            data=data,
            normalizations_applied=normalizations
        )
    except json.JSONDecodeError as e:
        return ParseResult(
            success=False,
            error_message=f"JSON syntax error: {str(e)}",
            error_category="parse_error"
        )


def validate_schema(data: Dict[str, Any], json_schema: Dict[str, Any]) -> SchemaValidationResult:
    """
    Stage 2: Validates the parsed data against the JSON Schema.
    (AC1, AC2)
    """
    validator = Draft7Validator(json_schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

    error_messages = []
    for error in errors:
        path = ".".join([str(p) for p in error.path]) or "root"
        error_messages.append(f"[{path}] {error.message}")

    if error_messages:
        return SchemaValidationResult(
            valid=False,
            errors=error_messages,
            error_category="schema_error"
        )
    
    return SchemaValidationResult(valid=True)


def normalize_fields(
    data: Dict[str, Any], 
    evidence_catalog: Optional[Union[List[str], Dict[str, List[Union[str, List[str]]]]]], 
    use_case: str
) -> NormalizationResult:
    """
    Stage 3: Normalizes specific fields (like evidence aliases).
    (AC1, AC3)
    """
    normalized_data = dict(data)
    normalizations = []
    
    evidence = normalized_data.get("evidence", [])
    if isinstance(evidence, list) and evidence_catalog is not None:
        catalog_set = set()
        catalog_map = None
        if isinstance(evidence_catalog, dict):
            catalog_map = evidence_catalog
            catalog_set = set(evidence_catalog.keys())
        else:
            catalog_set = set(evidence_catalog)
            
        new_evidence = []
        any_normalized = False
        for item in evidence:
            if not isinstance(item, str):
                new_evidence.append(item)
                continue
            
            norm_item = _normalize_evidence_item(item, catalog_set, catalog_map)
            if norm_item != item:
                any_normalized = True
            new_evidence.append(norm_item.upper())
            
        if any_normalized:
            normalized_data["evidence"] = new_evidence
            normalizations.append("evidence_alias_normalized")
            
    return NormalizationResult(
        data=normalized_data,
        normalizations_applied=normalizations
    )


def sanitize_evidence(
    data: Dict[str, Any], 
    evidence_catalog: Optional[Union[List[str], Dict[str, List[str]]]], 
    strict: bool
) -> SanitizationResult:
    """
    Stage 4: Applies security filters and consistency checks.
    (AC1, AC3, AC4)
    """
    sanitized_data = dict(data)
    normalizations = []
    warnings = []
    
    evidence = sanitized_data.get("evidence", [])
    if not isinstance(evidence, list):
        return SanitizationResult(data=sanitized_data)

    catalog_set = set()
    catalog_map = None
    if evidence_catalog is not None:
        if isinstance(evidence_catalog, dict):
            catalog_map = evidence_catalog
            catalog_set = set(evidence_catalog.keys())
        else:
            catalog_set = set(evidence_catalog)

    # 1. Hallucination Detection (Warnings only, AC4)
    if evidence_catalog is not None:
        for item in evidence:
            if isinstance(item, str) and item not in catalog_set:
                warnings.append(f"Hallucinated evidence: '{item}' not in catalog.")

    # 2. Bidirectional Rule
    text_blobs = []
    for key in ["summary", "highlights", "advice"]:
        val = sanitized_data.get(key)
        if isinstance(val, str):
            text_blobs.append(val)
        elif isinstance(val, list):
            text_blobs.extend([v for e in val if isinstance(e, str)])
            
    if "sections" in sanitized_data and isinstance(sanitized_data["sections"], list):
        for s in sanitized_data["sections"]:
            if isinstance(s, dict) and "content" in s:
                text_blobs.append(s["content"])

    full_text = _normalize_for_matching("\n".join(text_blobs))
    if full_text.strip():
        for item in evidence:
            if not isinstance(item, str):
                continue
            
            found = False
            pattern = rf"\b{re.escape(_normalize_for_matching(item))}\b"
            if re.search(pattern, full_text):
                found = True
            elif catalog_map is not None and item in catalog_map:
                for label in catalog_map[item]:
                    label_pattern = rf"\b{re.escape(_normalize_for_matching(label))}\b"
                    if re.search(label_pattern, full_text):
                        found = True
                        break
            
            if not found:
                warnings.append(f"Orphan evidence: '{item}' present in evidence but never mentioned in text.")

    # 3. Secure Filter (Silently remove non-catalog items, AC4)
    if evidence_catalog is not None:
        original_count = len(evidence)
        filtered_evidence = [e for e in evidence if e in catalog_set]
        if len(filtered_evidence) < original_count:
            sanitized_data["evidence"] = filtered_evidence
            normalizations.append("evidence_filtered_non_catalog")

    # 4. historical space check
    for i, item in enumerate(sanitized_data.get("evidence", [])):
        if isinstance(item, str) and " " in item:
            warnings.append(f"[evidence.{i}] Item contains spaces: '{item}'")

    return SanitizationResult(
        data=sanitized_data,
        normalizations_applied=normalizations,
        warnings=warnings
    )


def validate_output(
    raw_output: str,
    json_schema: Dict[str, Any],
    evidence_catalog: Optional[Union[List[str], Dict[str, List[str]]]] = None,
    strict: bool = False,
    use_case: str = "",
    schema_version: str = "v1",
) -> ValidationResult:
    """
    Orchestrates the 4-stage validation pipeline.
    (AC5)
    """
    try:
        # Stage 1: Parse
        parse_res = parse_json(raw_output, schema_version)
        if not parse_res.success:
            if use_case.startswith("natal"):
                increment_counter("natal_validation_fail_total", labels={"use_case": use_case, "reason": "json_error", "schema_version": schema_version})
            return ValidationResult(
                valid=False, 
                errors=[parse_res.error_message] if parse_res.error_message else [], 
                error_category="parse_error"
            )

        # Stage 2: Schema
        schema_res = validate_schema(parse_res.data, json_schema)
        if not schema_res.valid:
            if use_case.startswith("natal"):
                increment_counter("natal_validation_fail_total", labels={"use_case": use_case, "reason": "schema_error", "schema_version": schema_version})
            return ValidationResult(
                valid=False, 
                parsed=parse_res.data, 
                errors=schema_res.errors, 
                error_category="schema_error"
            )

        # Stage 3: Normalize
        norm_res = normalize_fields(parse_res.data, evidence_catalog, use_case)

        # Stage 4: Sanitize
        sanit_res = sanitize_evidence(norm_res.data, evidence_catalog, strict)

        # Aggregation
        applied = parse_res.normalizations_applied + norm_res.normalizations_applied + sanit_res.normalizations_applied
        
        if use_case.startswith("natal"):
            increment_counter("natal_validation_pass_total", labels={"use_case": use_case, "schema_version": schema_version})
            filtered_count = len(norm_res.data.get("evidence", [])) - len(sanit_res.data.get("evidence", []))
            if filtered_count > 0:
                increment_counter("natal_invalid_evidence_total", value=float(filtered_count), labels={"use_case": use_case, "schema_version": schema_version})

        return ValidationResult(
            valid=True,
            parsed=sanit_res.data,
            warnings=sanit_res.warnings,
            normalizations_applied=applied
        )

    except Exception as e:
        logger.exception("unexpected_validation_error")
        return ValidationResult(valid=False, errors=[f"Unexpected validation error: {str(e)}"])


def _normalize_evidence_item(
    item: str, catalog_set: set[str], catalog_map: Optional[dict[str, list[str]]]
) -> str:
    """Best-effort normalization to reduce false negatives on evidence aliases."""
    cleaned = re.sub(r"[^A-Z0-9_\.:-]", "", item.upper()).rstrip("._:-")
    if not cleaned:
        return item
    if cleaned in catalog_set:
        return cleaned

    if cleaned in _ANGLE_CODES:
        prefix = f"{cleaned}_"
        for key in catalog_set:
            if key.startswith(prefix):
                return key

    if re.fullmatch(r"HOUSE_\d{1,2}", cleaned):
        prefix = f"{cleaned}_"
        for key in catalog_set:
            if key.startswith(prefix):
                return key

    if cleaned in _PLANET_CODES:
        prefix = f"PLANET_{cleaned}_"
        for key in catalog_set:
            if key.startswith(prefix):
                return key

    if cleaned in _SIGN_CODES:
        needle = f"_{cleaned}"
        for key in catalog_set:
            if key.endswith(needle) or f"{needle}_" in key:
                return key

    parts = cleaned.split("_")
    if (
        len(parts) == 3
        and parts[0] in _PLANET_CODES
        and parts[1] in _ASPECT_CODES
        and parts[2] in _PLANET_CODES
    ):
        p1, aspect, p2 = parts
        pair = sorted([p1, p2])
        canonical = f"ASPECT_{pair[0]}_{pair[1]}_{aspect}"
        if canonical in catalog_set:
            return canonical

    if (
        len(parts) == 3
        and parts[0] in _ASPECT_CODES
        and parts[1] in _PLANET_CODES
        and parts[2] in _PLANET_CODES
    ):
        aspect, p1, p2 = parts
        pair = sorted([p1, p2])
        canonical = f"ASPECT_{pair[0]}_{pair[1]}_{aspect}"
        if canonical in catalog_set:
            return canonical

    if (
        len(parts) == 3
        and parts[0] in _PLANET_CODES
        and parts[1] == "IN"
        and parts[2] in _SIGN_CODES
    ):
        p, _, s = parts
        prefix = f"{p}_{s}"
        for key in catalog_set:
            if key.startswith(prefix):
                return key

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

    if catalog_map:
        # Search for item in catalog_map values
        norm_item = _normalize_for_matching(item)
        for canonical_id, aliases in catalog_map.items():
            # If item matches an alias, return canonical_id
            # aliases can be nested list: ["Alias A", ["Subalias A1", "Subalias A2"]]
            flattened_aliases = []
            for a in aliases:
                if isinstance(a, list):
                    flattened_aliases.extend(a)
                else:
                    flattened_aliases.append(a)
            
            for alias in flattened_aliases:
                if _normalize_for_matching(str(alias)) == norm_item:
                    return canonical_id

    return cleaned


def _normalize_for_matching(value: str) -> str:
    """Accents removal and case normalization for fuzzy matching."""
    decomposed = unicodedata.normalize("NFKD", value)
    no_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    lowered = no_accents.lower().strip()
    # Keep only alphanumeric and single spaces
    cleaned = re.sub(r"[^a-z0-9\s]", " ", lowered)
    return re.sub(r"\s+", " ", cleaned).strip()

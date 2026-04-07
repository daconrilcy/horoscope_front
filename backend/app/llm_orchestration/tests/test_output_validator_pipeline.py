import pytest
import json
from app.llm_orchestration.services.output_validator import (
    parse_json, 
    validate_schema, 
    normalize_fields, 
    sanitize_evidence, 
    validate_output,
    ValidationResult
)

def test_parse_json_invalid():
    res = parse_json("NOT JSON", "v1")
    assert res.success is False
    assert res.error_category == "parse_error"

def test_parse_json_v3_disclaimers():
    raw = '{"title": "test", "disclaimers": "should be gone"}'
    res = parse_json(raw, "v3")
    assert res.success is True
    assert "disclaimers" not in res.data
    assert "v3_disclaimers_stripped" in res.normalizations_applied

def test_validate_schema_valid():
    schema = {"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"]}
    res = validate_schema({"a": "hello"}, schema)
    assert res.valid is True

def test_validate_schema_invalid():
    schema = {"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"]}
    res = validate_schema({"b": "wrong"}, schema)
    assert res.valid is False
    assert res.error_category == "schema_error"
    assert "[root] 'a' is a required property" in res.errors

def test_normalize_fields_evidence_alias():
    catalog = ["PLANET_SUN_POSITION"]
    data = {"evidence": ["SUN"]}
    res = normalize_fields(data, catalog, "natal")
    assert res.data["evidence"] == ["PLANET_SUN_POSITION"]
    assert "evidence_alias_normalized" in res.normalizations_applied

def test_sanitize_evidence_filtering():
    catalog = ["OK"]
    data = {"evidence": ["OK", "HALLUCINATED"]}
    res = sanitize_evidence(data, catalog, strict=True)
    assert res.data["evidence"] == ["OK"]
    assert "evidence_filtered_non_catalog" in res.normalizations_applied
    assert any("Hallucinated" in w for w in res.warnings)

def test_sanitize_evidence_orphan():
    catalog = ["OK"]
    data = {"evidence": ["OK"], "summary": "Nothing here"}
    res = sanitize_evidence(data, catalog, strict=True)
    assert any("Orphan" in w for w in res.warnings)

def test_validate_output_integration():
    schema = {"type": "object", "properties": {"evidence": {"type": "array"}}}
    catalog = ["PLANET_SUN_POSITION"]
    raw = '{"evidence": ["SUN"]}'
    
    # We need to include 'SUN' in text to avoid Orphan warning for a perfectly clean test,
    # or just accept the warning.
    raw = '{"evidence": ["SUN"], "summary": "The sun is bright"}'
    
    res = validate_output(raw, schema, evidence_catalog=catalog, schema_version="v1")
    
    assert res.valid is True
    assert res.parsed["evidence"] == ["PLANET_SUN_POSITION"]
    assert "evidence_alias_normalized" in res.normalizations_applied

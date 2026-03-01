from app.llm_orchestration.services.output_validator import validate_output


def test_validate_output_valid():
    schema = {
        "type": "object",
        "required": ["message"],
        "properties": {"message": {"type": "string"}},
    }
    raw = '{"message": "hello"}'
    result = validate_output(raw, schema)
    assert result.valid is True
    assert result.parsed["message"] == "hello"


def test_validate_output_invalid_json():
    schema = {"type": "object"}
    raw = '{"message": "hello"'  # missing brace
    result = validate_output(raw, schema)
    assert result.valid is False
    assert "JSON syntax error" in result.errors[0]


def test_validate_output_schema_violation():
    schema = {"type": "object", "required": ["count"], "properties": {"count": {"type": "integer"}}}
    raw = '{"count": "not_an_int"}'
    result = validate_output(raw, schema)
    assert result.valid is False
    assert "[count]" in result.errors[0]


def test_validate_output_evidence_warning():
    schema = {
        "type": "object",
        "properties": {"evidence": {"type": "array", "items": {"type": "string"}}},
    }
    raw = '{"evidence": ["VALID_ID", "Invalid ID with spaces"]}'
    result = validate_output(raw, schema)
    assert result.valid is True  # valid against schema
    assert len(result.warnings) == 1
    assert "contains spaces" in result.warnings[0]

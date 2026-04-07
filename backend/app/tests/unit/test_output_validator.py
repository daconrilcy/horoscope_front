from app.llm_orchestration.services.output_validator import validate_output


def test_normalize_fields_nested_lists():
    """Test normalization with nested lists in catalog_map (defensive logic)."""
    from app.llm_orchestration.services.output_validator import normalize_fields
    
    data = {"evidence": ["Alias A", "Alias B"]}
    # Nested list: ["Alias A", ["Subalias A1", "Subalias A2"]]
    catalog = {
        "ID_A": ["Alias A", ["Subalias A1", "Subalias A2"]],
        "ID_B": ["Alias B"]
    }
    
    res = normalize_fields(data, evidence_catalog=catalog, use_case="test")
    assert res.data["evidence"] == ["ID_A", "ID_B"]
    assert "evidence_alias_normalized" in res.normalizations_applied


def test_validate_output_valid():
    schema = {
        "type": "object",
        "required": ["message"],
        "properties": {"message": {"type": "string"}},
    }
    raw = '{"message": "hello"}'
    result = validate_output(raw, schema, schema_version="v1")
    assert result.valid is True
    assert result.parsed["message"] == "hello"


def test_validate_output_invalid_json():
    schema = {"type": "object"}
    raw = '{"message": "hello"'  # missing brace
    result = validate_output(raw, schema, schema_version="v1")
    assert result.valid is False
    assert "JSON syntax error" in result.errors[0]


def test_validate_output_schema_violation():
    schema = {"type": "object", "required": ["count"], "properties": {"count": {"type": "integer"}}}
    raw = '{"count": "not_an_int"}'
    result = validate_output(raw, schema, schema_version="v1")
    assert result.valid is False
    assert "[count]" in result.errors[0]


def test_validate_output_evidence_warning():
    schema = {
        "type": "object",
        "properties": {"evidence": {"type": "array", "items": {"type": "string"}}},
    }
    raw = '{"evidence": ["VALID_ID", "Invalid ID with spaces"]}'
    result = validate_output(raw, schema, schema_version="v1")
    assert result.valid is True  # valid against schema
    assert len(result.warnings) == 1
    assert "contains spaces" in result.warnings[0]


def test_validate_output_evidence_aliases_strict_mode():
    schema = {
        "type": "object",
        "required": ["summary", "evidence"],
        "properties": {
            "summary": {"type": "string"},
            "evidence": {"type": "array", "items": {"type": "string"}},
        },
    }
    raw = '{"summary":"Soleil en Taureau. Aspect entre Soleil et Venus.","evidence":["SUN","TAURUS","SUN_CONJUNCTION_VENUS"]}'  # noqa: E501
    catalog = {
        "SUN_TAURUS": ["Soleil en Taureau"],
        "ASPECT_SUN_VENUS_CONJUNCTION": ["aspect entre Soleil et Venus"],
    }

    result = validate_output(
        raw, schema, evidence_catalog=catalog, strict=True, schema_version="v1"
    )
    assert result.valid is True
    # SUN is too ambiguous to normalize -> filtered in strict mode
    # TAURUS is mapped to SUN_TAURUS (because it is the only key ending in _TAURUS)
    # SUN_CONJUNCTION_VENUS is mapped to ASPECT_SUN_VENUS_CONJUNCTION
    assert result.parsed["evidence"] == ["SUN_TAURUS", "ASPECT_SUN_VENUS_CONJUNCTION"]


def test_validate_output_evidence_unknown_strict_mode_filters():
    """Story 30-8 T4: hallucinated evidence in strict mode is filtered (not rejected)."""
    schema = {
        "type": "object",
        "required": ["summary", "evidence"],
        "properties": {
            "summary": {"type": "string"},
            "evidence": {"type": "array", "items": {"type": "string"}},
        },
    }
    raw = '{"summary":"Texte neutre","evidence":["UNKNOWN_EVIDENCE"]}'
    result = validate_output(
        raw,
        schema,
        evidence_catalog={"SUN_TAURUS": ["Soleil en Taureau"]},
        strict=True,
        schema_version="v1",
    )  # noqa: E501
    assert result.valid is True  # No longer fails — evidence is filtered
    assert "UNKNOWN_EVIDENCE" not in result.parsed["evidence"]  # Filtered out
    assert any("Hallucinated evidence" in w for w in result.warnings)  # Becomes a warning


def test_validate_output_evidence_alias_conjunction_prefix_strict_mode():
    schema = {
        "type": "object",
        "required": ["summary", "evidence"],
        "properties": {
            "summary": {"type": "string"},
            "evidence": {"type": "array", "items": {"type": "string"}},
        },
    }
    raw = '{"summary":"Aspect entre Soleil et Venus.","evidence":["CONJUNCTION_SUN_VENUS"]}'
    catalog = {"ASPECT_SUN_VENUS_CONJUNCTION": ["aspect entre Soleil et Venus"]}
    result = validate_output(
        raw, schema, evidence_catalog=catalog, strict=True, schema_version="v1"
    )
    assert result.valid is True
    assert result.parsed["evidence"] == ["ASPECT_SUN_VENUS_CONJUNCTION"]


def test_validate_output_orphan_is_warning_even_in_strict():
    schema = {
        "type": "object",
        "required": ["summary", "evidence"],
        "properties": {
            "summary": {"type": "string"},
            "evidence": {"type": "array", "items": {"type": "string"}},
        },
    }
    raw = '{"summary":"Texte sans mention directe.","evidence":["SUN_TAURUS"]}'
    catalog = {"SUN_TAURUS": ["Soleil en Taureau"]}
    result = validate_output(
        raw, schema, evidence_catalog=catalog, strict=True, schema_version="v1"
    )
    assert result.valid is True
    assert any("Orphan evidence" in w for w in result.warnings)

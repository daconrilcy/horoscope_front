from app.domain.llm.runtime.repair_prompter import build_repair_prompt

_SCHEMA_V3 = {
    "type": "object",
    "required": ["title", "summary", "sections", "highlights", "advice", "evidence"],
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string", "minLength": 900},
        "sections": {"type": "array", "minItems": 5},
        "highlights": {"type": "array", "minItems": 5},
        "advice": {"type": "array", "minItems": 5},
        "evidence": {"type": "array"},
    },
}


def test_build_repair_prompt():
    schema = {
        "type": "object",
        "required": ["message", "count"],
        "properties": {"message": {"type": "string"}, "count": {"type": "integer"}},
    }
    errors = ["[count] 'not_an_int' is not of type 'integer'"]
    raw = '{"message": "hello", "count": "not_an_int"}'

    prompt = build_repair_prompt(raw, errors, schema)

    assert "La réponse précédente n'est pas conforme" in prompt
    assert "'not_an_int' is not of type 'integer'" in prompt
    assert "- message (string)" in prompt
    assert "- count (integer)" in prompt
    assert '{"message": "hello", "count": "not_an_int"}' in prompt


def test_no_density_block_for_type_errors():
    """Non-density errors should NOT include v3 density guidance block."""
    errors = ["[count] 'not_an_int' is not of type 'integer'"]
    prompt = build_repair_prompt("{}", errors, _SCHEMA_V3)
    assert "CONTRAINTES DE DENSITÉ" not in prompt


def test_density_block_for_too_short_error():
    """'too short' error triggers v3 density guidance."""
    errors = ["[summary] 'abc' is too short"]
    prompt = build_repair_prompt("{}", errors, _SCHEMA_V3)
    assert "CONTRAINTES DE DENSITÉ" in prompt
    assert "900 caractères" in prompt
    assert "280 caractères" in prompt


def test_density_block_for_minItems_error():
    """'minItems' keyword in error triggers density guidance."""
    errors = ["[sections] [] is too short"]
    prompt = build_repair_prompt("{}", errors, _SCHEMA_V3)
    assert "CONTRAINTES DE DENSITÉ" in prompt
    assert "5 sections" in prompt


def test_density_block_for_multiple_density_errors():
    """Multiple density errors — guidance still appears once."""
    errors = [
        "[summary] 'x' is too short",
        "[sections] [] is too short",
        "[highlights] [] is too short",
    ]
    prompt = build_repair_prompt("{}", errors, _SCHEMA_V3)
    count = prompt.count("CONTRAINTES DE DENSITÉ")
    assert count == 1


def test_repair_is_single_pass_guard_documented():
    """Confirm build_repair_prompt does NOT recurse — it only returns a string."""
    errors = ["[summary] 'x' is too short"]
    result = build_repair_prompt("{}", errors, _SCHEMA_V3)
    assert isinstance(result, str)
    assert "EXCLUSIVEMENT avec le bloc JSON" in result

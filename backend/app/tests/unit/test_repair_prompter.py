from app.llm_orchestration.services.repair_prompter import build_repair_prompt


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

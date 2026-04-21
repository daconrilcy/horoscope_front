from app.ops.llm.bootstrap.use_cases_seed import CHAT_RESPONSE_V1


def test_chat_response_v1_suggested_replies_has_no_min_items() -> None:
    # Story 30-17 fix: minItems should be absent to avoid raw_fallback on empty suggestions
    suggested_replies = CHAT_RESPONSE_V1["properties"]["suggested_replies"]
    assert "minItems" not in suggested_replies, "minItems constraint should be removed"
    assert suggested_replies.get("type") == "array"


def test_chat_response_v1_required_matches_properties() -> None:
    required = set(CHAT_RESPONSE_V1["required"])
    properties = set(CHAT_RESPONSE_V1["properties"].keys())
    assert required == properties


def test_chat_response_v1_contains_expected_keys() -> None:
    assert CHAT_RESPONSE_V1["required"] == [
        "message",
        "suggested_replies",
        "intent",
        "confidence",
        "safety_notes",
    ]

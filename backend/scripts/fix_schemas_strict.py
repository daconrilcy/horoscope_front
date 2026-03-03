"""
Migration: fix JSON schemas for strict=true compatibility with the Responses API.

The Responses API requires ALL properties to be listed in `required` when strict=true.
Optional arrays become required but can be empty (no minItems constraint).
Optional scalar fields become nullable using {"type": ["string", "null"]}.

Run with:
    python -m scripts.fix_schemas_strict
"""

from sqlalchemy import select

from app.infra.db.models import LlmOutputSchemaModel
from app.infra.db.session import SessionLocal

FIXED_SCHEMAS = {
    "AstroResponse_v1": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "title",
            "summary",
            "sections",
            "highlights",
            "advice",
            "evidence",
            "disclaimers",
        ],
        "properties": {
            "title": {"type": "string", "minLength": 1, "maxLength": 120},
            "summary": {"type": "string", "minLength": 1, "maxLength": 1200},
            "sections": {
                "type": "array",
                "minItems": 2,
                "maxItems": 8,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["key", "heading", "content"],
                    "properties": {
                        "key": {
                            "type": "string",
                            "enum": [
                                "overall",
                                "career",
                                "relationships",
                                "inner_life",
                                "daily_life",
                                "strengths",
                                "challenges",
                                "tarot_spread",
                                "event_context",
                            ],
                        },
                        "heading": {"type": "string", "minLength": 1, "maxLength": 80},
                        "content": {"type": "string", "minLength": 1, "maxLength": 2500},
                    },
                },
            },
            "highlights": {
                "type": "array",
                "minItems": 3,
                "maxItems": 10,
                "items": {"type": "string", "minLength": 1, "maxLength": 160},
            },
            "advice": {
                "type": "array",
                "minItems": 3,
                "maxItems": 10,
                "items": {"type": "string", "minLength": 1, "maxLength": 160},
            },
            "evidence": {
                "type": "array",
                "minItems": 2,
                "maxItems": 40,
                "items": {"type": "string", "pattern": r"^[A-Z0-9_\.:-]{3,60}$"},
            },
            "disclaimers": {
                "type": "array",
                "maxItems": 3,
                "items": {"type": "string", "maxLength": 200},
            },
        },
    },
    "ChatResponse_v1": {
        "type": "object",
        "additionalProperties": False,
        "required": ["message", "suggested_replies", "intent", "confidence", "safety_notes"],
        "properties": {
            "message": {"type": "string", "minLength": 1, "maxLength": 2500},
            "suggested_replies": {
                "type": "array",
                "maxItems": 5,
                "items": {"type": "string", "minLength": 1, "maxLength": 80},
            },
            "intent": {
                "type": ["string", "null"],
                "enum": [
                    "clarify_question",
                    "ask_birth_data",
                    "explain_natal_basics",
                    "offer_natal_interpretation",
                    "offer_tarot_reading",
                    "offer_event_guidance",
                    "handoff_to_support",
                    "close_conversation",
                    None,
                ],
            },
            "confidence": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
            "safety_notes": {
                "type": "array",
                "maxItems": 3,
                "items": {"type": "string", "maxLength": 200},
            },
        },
    },
}


def run():
    db = SessionLocal()
    try:
        for name, schema in FIXED_SCHEMAS.items():
            stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == name)
            record = db.execute(stmt).scalar_one_or_none()
            if record is None:
                print(f"  SKIP {name}: not found in DB")
                continue
            record.json_schema = schema
            db.add(record)
            print(f"  UPDATED {name}")
        db.commit()
        print("Migration complete.")
    except Exception:
        db.rollback()
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    run()

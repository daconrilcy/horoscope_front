"""
Seed : création du schema AstroResponse_v2 et mise à jour du use case natal_interpretation.

Ce script est idempotent :
- INSERT ou UPDATE AstroResponse_v2 dans llm_output_schemas
- UPDATE natal_interpretation.output_schema_id → id de AstroResponse_v2

NE PAS modifier natal_interpretation_short (reste sur AstroResponse_v1).

Run with:
    python -m scripts.seed_30_2_astroresponse_v2
"""

import logging
from sqlalchemy import select
from app.infra.db.models import LlmOutputSchemaModel, LlmUseCaseConfigModel
from app.infra.db.session import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ASTRO_RESPONSE_V2_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["title", "summary", "sections", "highlights", "advice", "evidence", "disclaimers"],
    "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 160},
        "summary": {"type": "string", "minLength": 1, "maxLength": 2800},
        "sections": {
            "type": "array",
            "minItems": 2,
            "maxItems": 10,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["key", "heading", "content"],
                "properties": {
                    "key": {
                        "type": "string",
                        "enum": [
                            "overall", "career", "relationships", "inner_life",
                            "daily_life", "strengths", "challenges",
                            "tarot_spread", "event_context"
                        ]
                    },
                    "heading": {"type": "string", "minLength": 1, "maxLength": 100},
                    "content": {"type": "string", "minLength": 1, "maxLength": 6500}
                }
            }
        },
        "highlights": {
            "type": "array",
            "minItems": 3,
            "maxItems": 12,
            "items": {"type": "string", "minLength": 1, "maxLength": 360}
        },
        "advice": {
            "type": "array",
            "minItems": 3,
            "maxItems": 12,
            "items": {"type": "string", "minLength": 1, "maxLength": 360}
        },
        "evidence": {
            "type": "array",
            "minItems": 0,
            "maxItems": 80,
            "items": {"type": "string", "pattern": r"^[A-Z0-9_\.:-]{3,80}$"}
        },
        "disclaimers": {
            "type": "array",
            "minItems": 0,
            "maxItems": 3,
            "items": {"type": "string", "minLength": 1, "maxLength": 300}
        }
    }
}


def seed():
    db = SessionLocal()
    try:
        # 1. Insert or update AstroResponse_v2
        stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == "AstroResponse_v2")
        existing_schema = db.execute(stmt).scalar_one_or_none()

        if existing_schema is None:
            new_schema = LlmOutputSchemaModel(
                name="AstroResponse_v2",
                json_schema=ASTRO_RESPONSE_V2_SCHEMA,
                version=1,
            )
            db.add(new_schema)
            db.flush()
            v2_id = str(new_schema.id)
            logger.info("Created AstroResponse_v2 with id=%s", v2_id)
        else:
            existing_schema.json_schema = ASTRO_RESPONSE_V2_SCHEMA
            v2_id = str(existing_schema.id)
            logger.info("Updated AstroResponse_v2 schema (id=%s)", v2_id)

        # 2. Update natal_interpretation use case to point to v2
        stmt_uc = select(LlmUseCaseConfigModel).where(
            LlmUseCaseConfigModel.key == "natal_interpretation"
        )
        uc = db.execute(stmt_uc).scalar_one_or_none()
        if uc is None:
            logger.warning("Use case 'natal_interpretation' not found. Run seed_29_prompts.py first.")
        else:
            old_id = uc.output_schema_id
            uc.output_schema_id = v2_id
            logger.info(
                "Updated natal_interpretation.output_schema_id: %s → %s",
                old_id, v2_id
            )

        # 3. Verify natal_interpretation_short stays on v1
        stmt_short = select(LlmUseCaseConfigModel).where(
            LlmUseCaseConfigModel.key == "natal_interpretation_short"
        )
        uc_short = db.execute(stmt_short).scalar_one_or_none()
        if uc_short:
            logger.info(
                "natal_interpretation_short remains on schema_id=%s (v1, unchanged)",
                uc_short.output_schema_id
            )

        db.commit()
        logger.info("Seed completed successfully.")
    except Exception:
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()

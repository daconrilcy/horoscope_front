"""
Seed: patch ChatResponse_v1 — supprime minItems sur suggested_replies (Story 30-17).

Problème résolu :
  suggested_replies.minItems=1 déclenchait une ValidationError quand le LLM
  retournait [] (valide sémantiquement pour une ouverture type "bonjour"),
  forçant le gateway à tomber en raw_fallback et perdre le contrat de style
  conversationnel (titres markdown, listes d'aspects, etc.).

Fix :
  Supprime minItems sur suggested_replies → [] devient valide → structured_output
  quasi systématique → style naturel garanti par le prompt.
"""

from __future__ import annotations

import logging
import sys

from sqlalchemy import select

from app.infra.db.models.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.session import SessionLocal
from app.llm_orchestration.seeds.use_cases_seed import CHAT_RESPONSE_V1

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def seed() -> None:
    db = SessionLocal()
    try:
        schema = db.execute(
            select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == "ChatResponse_v1")
        ).scalar_one_or_none()

        if schema is None:
            logger.error("ChatResponse_v1 schema not found in DB. Run use_cases_seed first.")
            sys.exit(1)

        current = schema.json_schema or {}
        current_min_items = (
            current.get("properties", {})
            .get("suggested_replies", {})
            .get("minItems")
        )

        if current_min_items is None:
            logger.info("ChatResponse_v1.suggested_replies.minItems already absent. Skipping.")
            return

        logger.info(
            "Patching ChatResponse_v1: removing suggested_replies.minItems=%s", current_min_items
        )
        schema.json_schema = CHAT_RESPONSE_V1
        db.commit()
        logger.info("ChatResponse_v1 schema updated successfully.")
    except Exception:
        db.rollback()
        logger.exception("Failed to patch ChatResponse_v1 schema.")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()

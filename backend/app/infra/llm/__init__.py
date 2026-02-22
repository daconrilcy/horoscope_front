"""
LLM infrastructure module.

DEPRECATED: LLMClient has been removed. Use the AI Engine module instead:
- app.services.ai_engine_adapter.AIEngineAdapter
- app.ai_engine.services.chat_service
- app.ai_engine.services.generate_service

This module now only exports the anonymizer utility.
"""

from app.infra.llm.anonymizer import anonymize_text

__all__ = ["anonymize_text"]

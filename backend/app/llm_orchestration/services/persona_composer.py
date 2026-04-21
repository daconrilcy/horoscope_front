"""Legacy shim: canonical persona composer lives in app.domain.llm.prompting.personas."""

from app.domain.llm.prompting.personas import compose_persona_block

__all__ = ["compose_persona_block"]

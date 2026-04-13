from contextvars import ContextVar
from typing import Optional

# Story 66.35: Context variable to track simulated LLM errors during qualification
simulation_error: ContextVar[Optional[str]] = ContextVar("llm_simulation_error", default=None)

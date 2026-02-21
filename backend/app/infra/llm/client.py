from __future__ import annotations


class LLMClient:
    def generate_reply(self, prompt: str, timeout_seconds: int) -> str:
        lowered = prompt.lower()
        if "simulate_timeout" in lowered:
            raise TimeoutError("llm timeout")
        if "simulate_unavailable" in lowered:
            raise ConnectionError("llm unavailable")
        return f"Guidance astrologique: {prompt.strip()}"

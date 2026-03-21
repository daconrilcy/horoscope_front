from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any

import openai

from app.prompts.catalog import resolve_model

logger = logging.getLogger(__name__)


@dataclass
class NarratorResult:
    daily_synthesis: str
    astro_events_intro: str
    time_window_narratives: dict[
        str, str
    ]  # {"nuit": ..., "matin": ..., "apres_midi": ..., "soiree": ...}
    turning_point_narratives: list[str]  # une entrée par TP


class LLMNarrator:
    """
    Narrates astrological data using OpenAI (Story 60.16).
    """

    TIMEOUT_SECONDS = 30.0

    async def narrate(
        self,
        time_windows: list[dict[str, Any]],
        common_context: Any,  # PromptCommonContext
        astrologer_profile_key: str = "standard",
        lang: str = "fr",
        astro_daily_events: dict[str, Any] | None = None,
    ) -> NarratorResult | None:
        from app.prediction.astrologer_prompt_builder import AstrologerPromptBuilder

        try:
            prompt = AstrologerPromptBuilder().build(
                common_context=common_context,
                time_windows=time_windows,
                astro_daily_events=astro_daily_events,
                astrologer_profile_key=astrologer_profile_key,
                lang=lang,
            )

            client = openai.AsyncOpenAI()  # uses OPENAI_API_KEY from env
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=resolve_model("daily_prediction"),
                    messages=[
                        {"role": "system", "content": self._system_prompt(lang)},
                        {"role": "user", "content": prompt},
                    ],
                    max_completion_tokens=4000,
                ),
                timeout=self.TIMEOUT_SECONDS,
            )

            choice = response.choices[0]
            raw = (choice.message.content or "").strip()
            if not raw:
                logger.warning(
                    "llm_narrator.empty_response model=%s finish_reason=%s refusal=%s",
                    resolve_model("daily_prediction"),
                    choice.finish_reason,
                    getattr(choice.message, "refusal", None),
                )
                return None
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw)

            return NarratorResult(
                daily_synthesis=data.get("daily_synthesis", ""),
                astro_events_intro=data.get("astro_events_intro", ""),
                time_window_narratives=data.get("time_window_narratives", {}),
                turning_point_narratives=data.get("turning_point_narratives", []),
            )

        except Exception as e:
            logger.warning("llm_narrator.failed error=%s", str(e))
            return None

    def _system_prompt(self, lang: str) -> str:
        lang_instruction = "Réponds en français." if lang == "fr" else "Answer in English."
        return (
            "Tu es un astrologue expert, bienveillant et précis. "
            f"{lang_instruction} "
            "Génère uniquement du JSON valide avec les clés : "
            "daily_synthesis (string), astro_events_intro (string), "
            "time_window_narratives (objet avec clés nuit/matin/apres_midi/soiree), "
            "turning_point_narratives (liste de strings). "
            "Sois concis : 1-2 phrases par champ. Pas de markdown."
        )

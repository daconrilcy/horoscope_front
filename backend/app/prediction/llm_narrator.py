from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from typing import Any

import openai

from app.prompts.catalog import PROMPT_CATALOG, resolve_model

logger = logging.getLogger(__name__)


@dataclass
class NarratorAdvice:
    advice: str
    emphasis: str


@dataclass
class NarratorResult:
    daily_synthesis: str
    astro_events_intro: str
    time_window_narratives: dict[
        str, str
    ]  # {"nuit": ..., "matin": ..., "apres_midi": ..., "soiree": ...}
    turning_point_narratives: list[str]  # une entrée par TP
    daily_advice: NarratorAdvice | None = None
    main_turning_point_narrative: str | None = None


class LLMNarrator:
    """
    Narrates astrological data using OpenAI (Story 60.16).
    """

    TIMEOUT_SECONDS = 60.0
    MAX_COMPLETION_TOKENS = PROMPT_CATALOG["daily_prediction"].max_tokens
    MIN_DAILY_SYNTHESIS_SENTENCES = 10
    MAX_NARRATION_ATTEMPTS = 2

    async def narrate(
        self,
        time_windows: list[dict[str, Any]],
        common_context: Any,  # PromptCommonContext
        astrologer_profile_key: str = "standard",
        lang: str = "fr",
        astro_daily_events: dict[str, Any] | None = None,
        day_climate: dict[str, Any] | None = None,
        best_window: dict[str, Any] | None = None,
        turning_point: dict[str, Any] | None = None,
        domain_ranking: list[dict[str, Any]] | None = None,
        variant_code: str | None = None,
    ) -> NarratorResult | None:
        from app.prediction.astrologer_prompt_builder import AstrologerPromptBuilder

        try:
            # 1. Resolve model name based on variant_code (Story 64.2)
            # variant_code expected: "summary_only" | "full"
            use_case = "daily_prediction"
            if variant_code == "summary_only":
                use_case = "horoscope_daily_free"
            elif variant_code == "full":
                use_case = "horoscope_daily_full"

            model = resolve_model(use_case)

            base_prompt = AstrologerPromptBuilder().build(
                common_context=common_context,
                time_windows=time_windows,
                astro_daily_events=astro_daily_events,
                astrologer_profile_key=astrologer_profile_key,
                lang=lang,
                day_climate=day_climate,
                best_window=best_window,
                turning_point=turning_point,
                domain_ranking=domain_ranking,
            )

            client = openai.AsyncOpenAI()  # uses OPENAI_API_KEY from env
            result: NarratorResult | None = None
            for attempt in range(1, self.MAX_NARRATION_ATTEMPTS + 1):
                prompt = self._build_attempt_prompt(base_prompt, attempt)
                result = await self._request_narration(
                    client=client,
                    model=model,
                    prompt=prompt,
                    lang=lang,
                )
                if result is None:
                    return None
                sentence_count = self._count_sentences(result.daily_synthesis)
                if sentence_count >= self.MIN_DAILY_SYNTHESIS_SENTENCES:
                    return result
                logger.warning(
                    "llm_narrator.short_synthesis model=%s attempt=%s sentence_count=%s",
                    model,
                    attempt,
                    sentence_count,
                )

            return result

        except asyncio.TimeoutError:
            # Fallback to generic name for log if use_case resolution failed early
            logger.warning(
                "llm_narrator.timeout model=%s timeout_seconds=%s",
                model if "model" in locals() else "unknown",
                self.TIMEOUT_SECONDS,
            )
            return None
        except Exception as e:
            logger.warning("llm_narrator.failed error=%s", str(e))
            return None

    def _system_prompt(self, lang: str) -> str:
        lang_instruction = "Réponds en français." if lang == "fr" else "Answer in English."
        return (
            "Tu es un astrologue expert, précis et pédagogue. "
            f"{lang_instruction} "
            "Génère uniquement du JSON valide avec les clés : "
            "daily_synthesis (string), astro_events_intro (string), "
            "time_window_narratives (objet avec clés nuit/matin/apres_midi/soiree), "
            "turning_point_narratives (liste de strings), "
            "main_turning_point_narrative (string), "
            "daily_advice (objet avec advice et emphasis). "
            "Apporte de la valeur : explique ce qui se joue, pourquoi astrologiquement, "
            "et quelle attitude adopter. Évite les banalités et le remplissage. "
            "Pas de markdown."
        )

    async def _request_narration(
        self,
        *,
        client: openai.AsyncOpenAI,
        model: str,
        prompt: str,
        lang: str,
    ) -> NarratorResult | None:
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self._system_prompt(lang)},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=self.MAX_COMPLETION_TOKENS,
            ),
            timeout=self.TIMEOUT_SECONDS,
        )

        choice = response.choices[0]
        raw = (choice.message.content or "").strip()
        if not raw:
            logger.warning(
                "llm_narrator.empty_response model=%s finish_reason=%s refusal=%s",
                model,
                choice.finish_reason,
                getattr(choice.message, "refusal", None),
            )
            return None
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.warning(
                (
                    "llm_narrator.invalid_json model=%s finish_reason=%s "
                    "error=%s raw_length=%s raw_tail=%r"
                ),
                model,
                choice.finish_reason,
                str(exc),
                len(raw),
                raw[-240:],
            )
            return None

        advice_data = data.get("daily_advice")
        return NarratorResult(
            daily_synthesis=self._as_string(data.get("daily_synthesis")),
            astro_events_intro=self._as_string(data.get("astro_events_intro")),
            time_window_narratives=self._normalize_window_narratives(
                data.get("time_window_narratives")
            ),
            turning_point_narratives=self._normalize_turning_point_narratives(
                data.get("turning_point_narratives")
            ),
            daily_advice=self._normalize_daily_advice(advice_data),
            main_turning_point_narrative=self._as_string(data.get("main_turning_point_narrative"))
            or None,
        )

    def _build_attempt_prompt(self, base_prompt: str, attempt: int) -> str:
        if attempt <= 1:
            return base_prompt
        return (
            f"{base_prompt}\n\n"
            "CORRECTION OBLIGATOIRE : lors de la tentative précédente, "
            "daily_synthesis était trop courte. "
            "Régénère tout le JSON et assure-toi que daily_synthesis comporte "
            "strictement entre 10 et 12 phrases complètes."
        )

    def _count_sentences(self, text: str) -> int:
        if not text:
            return 0
        return len([part for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()])

    def _as_string(self, value: Any) -> str:
        if isinstance(value, str):
            return value.strip()
        return ""

    def _normalize_window_narratives(self, value: Any) -> dict[str, str]:
        if not isinstance(value, dict):
            return {}
        allowed_keys = {"nuit", "matin", "apres_midi", "soiree"}
        return {
            key: self._as_string(text)
            for key, text in value.items()
            if key in allowed_keys and self._as_string(text)
        }

    def _normalize_turning_point_narratives(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [text for item in value if (text := self._as_string(item))]

    def _normalize_daily_advice(self, value: Any) -> NarratorAdvice | None:
        if not isinstance(value, dict):
            return None
        advice = self._as_string(value.get("advice"))
        emphasis = self._as_string(value.get("emphasis"))
        if not advice and not emphasis:
            return None
        return NarratorAdvice(advice=advice, emphasis=emphasis)

"""
Seed: prompt chat astrologue (Story 30-14 follow-up quality hardening).

Goals:
- Natural conversational flow (no repeated full natal recap on every turn)
- Concise answers by default, depth only when user asks
- Strong persona consistency via {{persona_name}}
"""

from __future__ import annotations

import logging

from sqlalchemy import select

from app.infra.db.models import LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.infra.db.session import SessionLocal
from app.llm_orchestration.services.prompt_lint import PromptLint
from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2, utc_now

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


CHAT_ASTROLOGER_PROMPT_V3 = """Langue : français ({{locale}}). Contexte : use_case={{use_case}}.

Tu incarnes {{persona_name}}, astrologue professionnel.

Objectif conversationnel:
- Répondre de façon naturelle, claire et utile.
- Priorité au message utilisateur courant (ne répète pas tout le thème à chaque tour).
- Par défaut: réponse courte (3-7 phrases max). Approfondis seulement sur demande explicite.
- Au premier échange, pars du contexte minimal fourni et réponds d'abord simplement à la demande.
- Si un détour par le thème natal, l'horoscope du jour ou les transits serait utile, propose-le
  après ta première réponse au lieu de l'imposer immédiatement.

Règles de style:
- Ton humain, direct et chaleureux, sans jargon inutile.
- Pas de listes numérotées lourdes sauf si l'utilisateur les demande.
- Si l'utilisateur dit juste "bonjour" ou une phrase brève, réponds brièvement et pose une
  question de clarification ciblée.
- Si le premier message est flou, vide de sens ou quasi incompréhensible ("chch", "??", etc.),
  ne réponds pas comme un robot et ne proposes pas tout de suite un menu d'options:
  dis simplement que tu n'as pas bien saisi et invite à reformuler naturellement.

Règles métier:
- Utilise les éléments du thème natal seulement si pertinents pour la question posée.
- Si la question est prédictive ("vais-je..."), reformule en tendances + fenêtre plausible +
  leviers concrets, sans certitude absolue.
- Aucune promesse ferme, aucun diagnostic médical/légal/financier.

Format de sortie : JSON strict ChatResponse_v1
- message: réponse principale
- suggested_replies: 1 à 3 suggestions courtes et actionnables
- intent: choisir l'intent le plus pertinent ou null
- confidence: valeur entre 0 et 1
- safety_notes: tableau vide sauf nécessité de prudence explicite
"""


def seed() -> None:
    db = SessionLocal()
    try:
        use_case_key = "chat_astrologer"
        uc = db.execute(
            select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == use_case_key)
        ).scalar_one_or_none()
        if not uc:
            logger.error("Use case '%s' not found. Run use_cases_seed first.", use_case_key)
            return

        lint_res = PromptLint.lint_prompt(
            CHAT_ASTROLOGER_PROMPT_V3,
            use_case_required_placeholders=["persona_name"],
        )
        if not lint_res.passed:
            raise RuntimeError(f"Lint FAILED for {use_case_key}: {lint_res.errors}")
        if lint_res.warnings:
            logger.info("Lint advisories for %s: %s", use_case_key, lint_res.warnings)

        current_published = db.execute(
            select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.use_case_key == use_case_key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
        ).scalar_one_or_none()

        if (
            current_published
            and current_published.developer_prompt == CHAT_ASTROLOGER_PROMPT_V3
            and current_published.model == "gpt-4o-mini"
            and current_published.max_output_tokens == 1200
        ):
            logger.info("Prompt chat_astrologer already up-to-date. Skipping.")
            return

        if current_published:
            current_published.status = PromptStatus.ARCHIVED

        new_prompt = LlmPromptVersionModel(
            use_case_key=use_case_key,
            status=PromptStatus.PUBLISHED,
            developer_prompt=CHAT_ASTROLOGER_PROMPT_V3,
            model="gpt-4o-mini",
            temperature=0.5,
            max_output_tokens=1200,
            created_by="system",
            published_at=utc_now(),
        )
        db.add(new_prompt)
        db.commit()
        PromptRegistryV2.invalidate_cache(use_case_key)
        logger.info("Published new chat_astrologer prompt version.")
    except Exception:
        db.rollback()
        logger.exception("Failed to seed chat_astrologer prompt.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

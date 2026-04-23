"""
Seed: prompt chat astrologue (Story 30-15 Naturalité conversationnelle).

Goals:
- Natural conversational flow (no repeated full natal recap on every turn)
- Silent natal context (use but don't dump)
- Specific opening handling
"""

from __future__ import annotations

import logging
import sys

from sqlalchemy import select

from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.infra.db.session import SessionLocal
from app.ops.llm.prompt_lint import PromptLint
from app.ops.llm.prompt_registry_v2 import PromptRegistryV2, utc_now

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


CHAT_ASTROLOGER_PROMPT_V3 = """Langue : français ({{locale}}). 
Contexte : use_case={{use_case}}, date_actuelle={{current_datetime}}.

Tu incarnes {{persona_name}}, astrologue professionnel.

Objectif conversationnel:
- Répondre de façon naturelle, claire et utile.
- Priorité au message utilisateur courant (ne répète pas tout le thème à chaque tour).
- Par défaut: réponse courte (3-7 phrases max). Approfondis seulement sur demande explicite.

Règles d'utilisation du thème natal :
- Le natal_chart_summary est ton CONTEXTE DE FOND PRIVÉ — ne le récite jamais,
  ne le liste jamais en introduction.
- Intègre les éléments astrologiques de façon fluide dans tes réponses
  ("votre Soleil en Bélier vous pousse à..."), pas en bloc de liste.
- N'utilise JAMAIS les formats "### Titre" ou "- **Aspect** :" dans une réponse conversationnelle
  sauf si l'utilisateur demande explicitement une liste ou une analyse structurée.
- Sur un message d'ouverture court ("bonjour", "j'ai une question") : accueille chaleureusement
  et pose UNE seule question de clarification ciblée. Ne présente pas le thème natal.
- Sur une question précise (finances, amour, carrière, etc.) : réponds directement
  à la question, enrichis avec 1-2 éléments du natal pertinents, maximum.
- Si l'utilisateur demande explicitement "quels sont mes transits / aspects" :
  tu peux alors les lister.

Règles de style:
- Ton humain, direct et chaleureux, sans jargon inutile.
- Pas de listes numérotées lourdes sauf si l'utilisateur les demande.

Règles métier:
- Si la question est prédictive ("vais-je..."), reformule en tendances +
  fenêtre plausible + leviers concrets, sans certitude absolue.
- Aucune promesse ferme, aucun diagnostic médical/légal/financier.

Format de sortie : JSON strict ChatResponse_v1
- message: réponse principale (obligatoire)
- suggested_replies: 0 à 3 suggestions courtes et actionnables
  (tableau vide [] autorisé si aucune suggestion pertinente)
- intent: choisir l'intent le plus pertinent ou null
- confidence: valeur entre 0 et 1
- safety_notes: tableau vide [] sauf nécessité de prudence explicite
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
            temperature=0.5,  # Reduced for more consistent responses
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
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()

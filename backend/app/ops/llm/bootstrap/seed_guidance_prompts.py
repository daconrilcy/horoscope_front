from __future__ import annotations

import logging

from sqlalchemy import select

from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.infra.db.session import SessionLocal
from app.ops.llm.services import PromptLint, PromptRegistryV2, utc_now

logger = logging.getLogger(__name__)

GUIDANCE_PROMPTS_TO_SEED = [
    {
        "use_case_key": "guidance_daily",
        "display_name": "Guidance Quotidienne",
        "description": "Conseils astrologiques pour la journée.",
        "required_prompt_placeholders": ["natal_chart_summary"],
        "developer_prompt": (
            "Langue de reponse : francais ({{locale}}). Contexte : use_case={{use_case}}.\n"
            "Tu produis une guidance astrologique quotidienne prudente et actionnable.\n"
            "Base-toi en priorite sur le resume natal suivant :\n"
            "{{natal_chart_summary}}\n\n"
            "Contexte conversationnel recent :\n{{context_lines}}\n\n"
            "Date courante : {{current_datetime}}.\n"
            "Reponds en JSON strict AstroResponse_v1. Le champ summary doit donner une lecture "
            "quotidienne claire. Les champs highlights et advice doivent rester concrets, "
            "courts et non fatalistes. N'invente aucune donnee astrologique absente."
        ),
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_output_tokens": 2000,
    },
    {
        "use_case_key": "guidance_weekly",
        "display_name": "Guidance Hebdomadaire",
        "description": "Conseils astrologiques pour la semaine.",
        "required_prompt_placeholders": ["natal_chart_summary"],
        "developer_prompt": (
            "Langue de reponse : francais ({{locale}}). Contexte : use_case={{use_case}}.\n"
            "Tu produis une guidance astrologique hebdomadaire prudente et utile.\n"
            "Base-toi sur le resume natal suivant :\n"
            "{{natal_chart_summary}}\n\n"
            "Contexte conversationnel recent :\n{{context_lines}}\n\n"
            "Reponds en JSON strict AstroResponse_v1. Le summary doit presenter la dynamique "
            "de la semaine. Les highlights et advice doivent proposer des reperes pratiques "
            "sans promesse absolue. N'invente aucune donnee astrologique absente."
        ),
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_output_tokens": 2200,
    },
    {
        "use_case_key": "guidance_contextual",
        "display_name": "Guidance Contextuelle",
        "description": "Lecture astrologique prudente d'une situation ou consultation thematique.",
        "required_prompt_placeholders": ["situation", "objective", "natal_chart_summary"],
        "developer_prompt": (
            "Langue de reponse : francais ({{locale}}). Contexte : use_case={{use_case}}.\n"
            "Tu produis une guidance contextuelle prudente, non fataliste et orientee decision.\n"
            "Situation : {{situation}}\n"
            "Objectif : {{objective}}\n"
            "Horizon temporel : {{time_horizon}}\n\n"
            "Resume natal disponible :\n{{natal_chart_summary}}\n\n"
            "Contexte conversationnel recent :\n{{context_lines}}\n\n"
            "Reponds en JSON strict AstroResponse_v1. Le summary doit etre directement utile "
            "pour la situation de l'utilisateur. Les highlights et advice doivent rester "
            "concrets, prudents et actionnables. N'invente aucune donnee astrologique absente."
        ),
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_output_tokens": 2600,
    },
    {
        "use_case_key": "event_guidance",
        "display_name": "Guidance Evenementielle",
        "description": "Analyse d'un evenement specifique via l'astrologie.",
        "required_prompt_placeholders": ["chart_json", "event_description"],
        "developer_prompt": (
            "Langue de reponse : francais ({{locale}}). Contexte : use_case={{use_case}}.\n"
            "Tu analyses l'evenement suivant avec prudence : {{event_description}}\n\n"
            "Theme natal disponible :\n{{chart_json}}\n\n"
            "Reponds en JSON strict AstroResponse_v1. Le summary doit resumer la dynamique "
            "principale. Les highlights et advice doivent rester specifiques a l'evenement, "
            "prudents et non fatalistes. N'invente aucune donnee astrologique absente."
        ),
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_output_tokens": 2600,
    },
]


def seed_guidance_prompts() -> None:
    """Seeds published prompt versions for canonical guidance use cases."""
    db = SessionLocal()
    keys_to_invalidate: set[str] = set()
    try:
        for config in GUIDANCE_PROMPTS_TO_SEED:
            key = config["use_case_key"]
            stmt_uc = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == key)
            uc = db.execute(stmt_uc).scalar_one_or_none()

            if not uc:
                uc = LlmUseCaseConfigModel(
                    key=key,
                    display_name=config["display_name"],
                    description=config["description"],
                    safety_profile="astrology",
                    persona_strategy="optional",
                    required_prompt_placeholders=config["required_prompt_placeholders"],
                )
                db.add(uc)
            else:
                uc.display_name = config["display_name"]
                uc.description = config["description"]
                uc.required_prompt_placeholders = config["required_prompt_placeholders"]

            db.flush()

            lint_res = PromptLint.lint_prompt(
                config["developer_prompt"],
                use_case_required_placeholders=config["required_prompt_placeholders"],
            )
            if not lint_res.passed:
                raise RuntimeError(f"Lint FAILED for {key}: {lint_res.errors}")

            stmt_p = select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.use_case_key == key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
            current = db.execute(stmt_p).scalar_one_or_none()

            if (
                current
                and current.developer_prompt == config["developer_prompt"]
                and current.max_output_tokens == config["max_output_tokens"]
                and current.temperature == config["temperature"]
                and current.model == config["model"]
            ):
                continue

            if current:
                current.status = PromptStatus.ARCHIVED

            db.add(
                LlmPromptVersionModel(
                    use_case_key=key,
                    status=PromptStatus.PUBLISHED,
                    developer_prompt=config["developer_prompt"],
                    model=config["model"],
                    temperature=config["temperature"],
                    max_output_tokens=config["max_output_tokens"],
                    created_by="system",
                    published_at=utc_now(),
                )
            )
            keys_to_invalidate.add(key)

        db.commit()

        for key in keys_to_invalidate:
            PromptRegistryV2.invalidate_cache(key)
    except Exception:
        db.rollback()
        logger.exception("seed_guidance_prompts_failed")
        raise
    finally:
        db.close()

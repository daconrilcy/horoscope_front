from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.infra.db.models.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def seed_llm_registry(db: Session, admin_user_id: str = "system-seed") -> None:
    """
    Seed the LLM Registry with initial use cases and prompts.
    """
    use_cases = [
        {
            "key": "natal_interpretation",
            "display_name": "Interprétation du thème natal",
            "description": "Analyse complète du thème natal (Soleil, Lune, Ascendant, Aspects, Maisons)",  # noqa: E501
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_output_tokens": 1800,
            "developer_prompt": """Tu es un astrologue expert et bienveillant. Tu vas interpréter le thème natal de l'utilisateur.

Langue de réponse: {{locale}}
Thème natal:
{{natal_chart_summary}}

Instructions de structure:
1. Commence par une synthèse en 2-3 phrases
2. Développe les points clés du thème (Soleil, Lune, Ascendant, aspects majeurs)
3. Propose des conseils actionnables et positifs
4. Termine par une note de prudence

Important:
- Reste bienveillant et non-alarmiste
- Utilise 'tendance', 'potentiel', jamais de certitudes absolues
- Ne fais aucun diagnostic médical, juridique ou financier
- Use case reference: {{use_case}}""",  # noqa: E501
        },
        {
            "key": "guidance_daily",
            "display_name": "Guidance quotidienne",
            "description": "Conseils astrologiques pour la journée en cours",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_output_tokens": 1000,
            "developer_prompt": """Génère une guidance quotidienne pour {{locale}}.

Situation actuelle: {{situation}}
Contexte natal: {{natal_chart_summary}}

Reste focalisé sur des conseils pratiques pour la journée. {{use_case}}""",
        },
        {
            "key": "chat",
            "display_name": "Chat Assistant",
            "description": "Conversation interactive avec l'assistant astrologique",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_output_tokens": 1000,
            "developer_prompt": """Tu es un assistant astrologique expert pour {{locale}}.
Context: {{natal_chart_summary}}
Dernier message utilisateur: {{last_user_msg}}

Réponds de manière concise et pertinente. {{use_case}}""",
        },
    ]

    for uc_data in use_cases:
        # 1. Create or update Use Case Config
        uc = db.get(LlmUseCaseConfigModel, uc_data["key"])
        if not uc:
            uc = LlmUseCaseConfigModel(
                key=uc_data["key"],
                display_name=uc_data["display_name"],
                description=uc_data["description"],
            )
            db.add(uc)
            db.flush()

        # 2. Check if a prompt already exists for this use case
        existing_prompt = (
            db.query(LlmPromptVersionModel)
            .filter(LlmPromptVersionModel.use_case_key == uc.key)
            .first()
        )

        if not existing_prompt:
            # 3. Create initial published prompt
            prompt = LlmPromptVersionModel(
                id=uuid.uuid4(),
                use_case_key=uc.key,
                status=PromptStatus.PUBLISHED,
                developer_prompt=uc_data["developer_prompt"],
                model=uc_data["model"],
                temperature=uc_data["temperature"],
                max_output_tokens=uc_data["max_output_tokens"],
                created_by=admin_user_id,
                published_at=utc_now(),
            )
            db.add(prompt)

    db.commit()

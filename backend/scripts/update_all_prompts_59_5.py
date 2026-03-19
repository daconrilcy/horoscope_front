"""Script to update all prompts with Common Context header (Story 59.5)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.infra.db.session import SessionLocal


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


COMMON_HEADER = """## Contexte de base — {{ use_case_name }}
Date du jour : {{ today_date }}
Période couverte : {{ period_covered }}
Astrologue : {{ astrologer_profile.name }} — {{ astrologer_profile.description }}
Précision du thème natal : {{ precision_level }}

{% if natal_interpretation %}
### Thème natal interprété
{{ natal_interpretation }}
{% elif natal_data %}
### Données natales (non encore interprétées)
Soleil : {{ natal_data.planets.sun.sign }} maison {{ natal_data.planets.sun.house }}
Lune : {{ natal_data.planets.moon.sign }} maison {{ natal_data.planets.moon.house }}
Ascendant : {{ natal_data.houses[0].sign }}
{% endif %}

---
"""


def update_all_prompts(db: Session):
    stmt = select(LlmUseCaseConfigModel)
    use_cases = db.execute(stmt).scalars().all()

    for uc in use_cases:
        print(f"Updating prompt for {uc.key}...")

        # Get current active prompt
        v_stmt = select(LlmPromptVersionModel).where(
            LlmPromptVersionModel.use_case_key == uc.key,
            LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
        )
        old_prompt = db.execute(v_stmt).scalar_one_or_none()

        if not old_prompt:
            print(f"Skipping {uc.key} (no published prompt found)")
            continue

        if "## Contexte de base" in old_prompt.developer_prompt:
            print(f"Skipping {uc.key} (already has common context)")
            continue

        # Archive old version
        old_prompt.status = PromptStatus.ARCHIVED

        # New prompt content
        new_content = COMMON_HEADER + "\n" + old_prompt.developer_prompt

        # Handle natal_interpretation special case
        if uc.key == "natal_interpretation":
            # For natal interpretation, we don't want to include natal_interpretation
            # in the context (as it's being produced).
            # But our header already handles it via if natal_interpretation.
            pass

        # Create new version
        new_prompt = LlmPromptVersionModel(
            id=uuid.uuid4(),
            use_case_key=uc.key,
            status=PromptStatus.PUBLISHED,
            developer_prompt=new_content,
            model=old_prompt.model,
            temperature=old_prompt.temperature,
            max_output_tokens=old_prompt.max_output_tokens,
            created_by="system-59-5",
            published_at=utc_now(),
        )
        db.add(new_prompt)
        db.flush()

        print(f"Updated {uc.key} to new version {new_prompt.id}")

    db.commit()


if __name__ == "__main__":
    with SessionLocal() as session:
        update_all_prompts(session)
        print("All prompts updated with Common Context.")

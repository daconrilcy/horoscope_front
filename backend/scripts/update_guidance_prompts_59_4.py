"""Script to update guidance prompts with astro context block (Story 59.4)."""

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

NEW_GUIDANCE_PROMPT = """Tu es un astrologue expert. Génère une guidance pour {{locale}}.

## Contexte natal
{{natal_chart_summary}}

{% if context.astro_context %}
## Données astrales du {{ context.astro_context.period_covered.label }}
Précision : {{ context.astro_context.precision_level }}
Phase lunaire : {{ context.astro_context.lunar_phase }}

Transits actifs :
{% for t in context.astro_context.transits_active %}
- {{ t.planet }} {{ t.aspect }} {{ t.natal_point }} (orb {{ t.orb }}°
{%- if t.applying %}, s'applique{% endif %})
{% endfor %}

Aspects dominants du jour :
{% for a in context.astro_context.dominant_aspects %}
- {{ a.planet_a }} {{ a.aspect_type }} {{ a.planet_b }} (orb {{ a.orb }}°)
{% endfor %}
{% endif %}

Instructions:
- Reste focalisé sur des conseils pratiques et concrets.
- Utilise les données astrales du jour pour personnaliser la lecture.
- Ne fais aucun diagnostic médical ou financier.
- Use case reference: {{use_case}}"""

def update_prompts(db: Session):
    for key in ["guidance_daily", "guidance_weekly"]:
        print(f"Updating prompt for {key}...")
        
        # 1. Archive old versions
        db.query(LlmPromptVersionModel).filter(
            LlmPromptVersionModel.use_case_key == key,
            LlmPromptVersionModel.status == PromptStatus.PUBLISHED
        ).update({"status": PromptStatus.ARCHIVED})
        
        # 2. Create new published version
        new_prompt = LlmPromptVersionModel(
            id=uuid.uuid4(),
            use_case_key=key,
            status=PromptStatus.PUBLISHED,
            developer_prompt=NEW_GUIDANCE_PROMPT,
            model="gpt-4o-mini", # Default
            temperature=0.7,
            max_output_tokens=2000,
            created_by="system-59-4",
            published_at=utc_now(),
        )
        db.add(new_prompt)
        db.flush()
        
        # 3. Update use case active version
        uc_stmt = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == key)
        uc = db.execute(uc_stmt).scalar_one_or_none()
        if uc:
            print(f"Updated {key} to new version {new_prompt.id}")
        else:
            print(f"WARNING: Use case {key} not found")

    db.commit()

if __name__ == "__main__":
    with SessionLocal() as session:
        update_prompts(session)
        print("Guidance prompts update completed.")

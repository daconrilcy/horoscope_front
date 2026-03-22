from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models import (
    AstrologerProfileModel,
    AstrologerPromptProfileModel,
    LlmPersonaModel,
)
from app.infra.db.session import SessionLocal
from scripts.seed_astrologers_6_profiles import ASTROLOGERS, _build_prompt_content

logger = logging.getLogger(__name__)

ASTROLOGER_ENRICHED_DATA = {str(item["id"]): item for item in ASTROLOGERS}


def backfill_astrologers(db: Session) -> None:
    # 1. Get all personas
    personas = db.execute(select(LlmPersonaModel)).scalars().all()

    for persona in personas:
        persona_id_str = str(persona.id)
        enriched = ASTROLOGER_ENRICHED_DATA.get(persona_id_str)

        # 2. Handle AstrologerProfile
        stmt_profile = select(AstrologerProfileModel).where(
            AstrologerProfileModel.persona_id == persona.id
        )
        profile = db.execute(stmt_profile).scalar_one_or_none()

        if not profile:
            if enriched:
                profile = AstrologerProfileModel(
                    persona_id=persona.id,
                    first_name=enriched["first_name"],
                    last_name=enriched["last_name"],
                    display_name=enriched["display_name"],
                    gender=enriched["gender"],
                    photo_url=enriched["photo_url"],
                    public_style_label=enriched["public_style_label"],
                    bio_short=enriched["bio_short"],
                    bio_long=persona.description or "",
                    admin_category=enriched["admin_category"],
                    specialties=enriched["specialties"],
                    sort_order=enriched["sort_order"],
                    is_public=persona.enabled,
                )
            else:
                # Fallback for non-canonical personas
                names = persona.name.split(" ", 1)
                first = names[0]
                last = names[1] if len(names) > 1 else ""
                profile = AstrologerProfileModel(
                    persona_id=persona.id,
                    first_name=first,
                    last_name=last,
                    display_name=persona.name,
                    gender="other",
                    public_style_label="Standard",
                    bio_short=(
                        persona.description[:497] + "..."
                        if persona.description and len(persona.description) > 500
                        else (persona.description or "")
                    ),
                    bio_long=persona.description or "",
                    admin_category="legacy",
                    specialties=[],
                    is_public=persona.enabled,
                )
            db.add(profile)
            logger.info(f"Created profile for persona: {persona.name}")
        else:
            logger.info(f"Profile already exists for persona: {persona.name}")

        # 3. Handle AstrologerPromptProfile
        stmt_prompt = select(AstrologerPromptProfileModel).where(
            AstrologerPromptProfileModel.persona_id == persona.id,
            AstrologerPromptProfileModel.is_active,
        )
        prompt_profile = db.execute(stmt_prompt).scalar_one_or_none()

        if not prompt_profile:
            # Build initial prompt content from legacy fields
            content = (
                _build_prompt_content(enriched)
                if enriched
                else (
                    f"Tone: {persona.tone}\nVerbosity: {persona.verbosity}\n"
                    + (
                        f"Style Markers: {', '.join(persona.style_markers)}\n"
                        if persona.style_markers
                        else ""
                    )
                    + (
                        f"Boundaries: {', '.join(persona.boundaries)}\n"
                        if persona.boundaries
                        else ""
                    )
                )
            )

            prompt_profile = AstrologerPromptProfileModel(
                persona_id=persona.id,
                prompt_content=content,
                version="1.0.0-backfill",
                is_active=True,
            )
            db.add(prompt_profile)
            logger.info(f"Created prompt profile for persona: {persona.name}")

    db.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with SessionLocal() as session:
        backfill_astrologers(session)
        print("Astrologers backfill completed.")

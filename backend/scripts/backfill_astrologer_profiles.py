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
                    provider_type=enriched.get("provider_type", "ia"),
                    age=enriched["age"],
                    photo_url=enriched["photo_url"],
                    public_style_label=enriched["public_style_label"],
                    bio_short=enriched["bio_short"],
                    bio_long=persona.description or "",
                    admin_category=enriched["admin_category"],
                    specialties=enriched["specialties"],
                    professional_background=enriched["professional_background"],
                    key_skills=enriched["key_skills"],
                    behavioral_style=enriched["behavioral_style"],
                    sort_order=enriched["sort_order"],
                    is_public=persona.enabled,
                )
                db.add(profile)
                logger.info(f"Created profile for persona: {persona.name}")
            else:
                logger.info(
                    "Skipped non-canonical astrologer profile creation for persona: %s (%s)",
                    persona.name,
                    persona.id,
                )
                profile = None
        else:
            if enriched:
                profile.first_name = enriched["first_name"]
                profile.last_name = enriched["last_name"]
                profile.display_name = enriched["display_name"]
                profile.gender = enriched["gender"]
                profile.provider_type = enriched.get("provider_type", "ia")
                profile.age = enriched["age"]
                profile.photo_url = enriched["photo_url"]
                profile.public_style_label = enriched["public_style_label"]
                profile.bio_short = enriched["bio_short"]
                profile.bio_long = persona.description or enriched["description"]
                profile.admin_category = enriched["admin_category"]
                profile.specialties = enriched["specialties"]
                profile.professional_background = enriched["professional_background"]
                profile.key_skills = enriched["key_skills"]
                profile.behavioral_style = enriched["behavioral_style"]
                profile.sort_order = enriched["sort_order"]
                profile.is_public = persona.enabled
            else:
                profile.professional_background = profile.professional_background or []
                profile.key_skills = profile.key_skills or []
                profile.behavioral_style = profile.behavioral_style or []
                profile.provider_type = profile.provider_type or "ia"
                profile.is_public = bool(profile.photo_url) and persona.enabled
            logger.info(f"Updated profile for persona: {persona.name}")

        # 3. Handle AstrologerPromptProfile
        if profile is None and not enriched:
            continue

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

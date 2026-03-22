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

logger = logging.getLogger(__name__)

# Enriched data for the 6 canonical astrologers
ASTROLOGER_ENRICHED_DATA = {
    "c0a80101-8edb-4e1a-8f1a-8f1a8f1a8f1a": {
        "first_name": "Astrologue",
        "last_name": "Standard",
        "display_name": "Guide Pédagogique",
        "gender": "other",
        "photo_url": "/assets/astrologers/standard.jpg",
        "public_style_label": "Pédagogue",
        "bio_short": "Profil pédagogique généraliste pour débutants. Calme, stable et rassurant.",
        "admin_category": "standard",
        "specialties": ["Thème Natal", "Bases", "Orientation"],
        "sort_order": 1,
    },
    "de6d4827-63d4-40dc-8012-6de96f2e58f4": {
        "first_name": "Sélène",
        "last_name": "Mystique",
        "display_name": "Sélène Mystique",
        "gender": "female",
        "photo_url": "/assets/astrologers/selene.jpg",
        "public_style_label": "Mystique",
        "bio_short": "Profil intuitif et symbolique. Contemplative et sensible aux archétypes.",
        "admin_category": "mystical",
        "specialties": ["Spiritualité", "Cycles Lunaires", "Relations"],
        "sort_order": 2,
    },
    "f4f49f86-1ecf-4f3d-bbbf-2cf34ca71623": {
        "first_name": "Orion",
        "last_name": "Analyste",
        "display_name": "Orion l'Analyste",
        "gender": "male",
        "photo_url": "/assets/astrologers/orion.jpg",
        "public_style_label": "Analytique",
        "bio_short": "Profil analytique et méthodique. Rigoureux et orienté preuves.",
        "admin_category": "rational",
        "specialties": ["Transits", "Carrière", "Organisation"],
        "sort_order": 3,
    },
    "f2879652-1f13-4f4e-8d68-57f13d5ba670": {
        "first_name": "Luna",
        "last_name": "Empathie",
        "display_name": "Luna Empathie",
        "gender": "female",
        "photo_url": "/assets/astrologers/luna.jpg",
        "public_style_label": "Chaleureux",
        "bio_short": "Profil d'accompagnement émotionnel. Chaleureuse et bienveillante.",
        "admin_category": "warm",
        "specialties": ["Relations", "Estime de soi", "Famille"],
        "sort_order": 4,
    },
    "3a4fc82a-4286-48f6-babe-cab39992f5c4": {
        "first_name": "Atlas",
        "last_name": "Direct",
        "display_name": "Atlas Direct",
        "gender": "male",
        "photo_url": "/assets/astrologers/atlas.jpg",
        "public_style_label": "Pragmatique",
        "bio_short": "Profil pragmatique et décisionnel. Franc et orienté résultats.",
        "admin_category": "direct",
        "specialties": ["Business", "Timing", "Objectifs"],
        "sort_order": 5,
    },
    "a38fbb78-14d6-4f54-b625-cf6f40b95f92": {
        "first_name": "Nox",
        "last_name": "Profondeur",
        "display_name": "Nox Profondeur",
        "gender": "non_binary",
        "photo_url": "/assets/astrologers/nox.jpg",
        "public_style_label": "Introspectif",
        "bio_short": "Profil introspectif de profondeur. Nuancé, patient et réflexif.",
        "admin_category": "introspective",
        "specialties": ["Ombre", "Transformation", "Psychologie"],
        "sort_order": 6,
    },
}


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
                    is_public=persona.enabled
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
                    is_public=persona.enabled
                )
            db.add(profile)
            logger.info(f"Created profile for persona: {persona.name}")
        else:
            logger.info(f"Profile already exists for persona: {persona.name}")

        # 3. Handle AstrologerPromptProfile
        stmt_prompt = select(AstrologerPromptProfileModel).where(
            AstrologerPromptProfileModel.persona_id == persona.id,
            AstrologerPromptProfileModel.is_active
        )
        prompt_profile = db.execute(stmt_prompt).scalar_one_or_none()
        
        if not prompt_profile:
            # Build initial prompt content from legacy fields
            content = f"Tone: {persona.tone}\nVerbosity: {persona.verbosity}\n"
            if persona.style_markers:
                content += f"Style Markers: {', '.join(persona.style_markers)}\n"
            if persona.boundaries:
                content += f"Boundaries: {', '.join(persona.boundaries)}\n"
            
            prompt_profile = AstrologerPromptProfileModel(
                persona_id=persona.id,
                prompt_content=content,
                version="1.0.0-backfill",
                is_active=True
            )
            db.add(prompt_profile)
            logger.info(f"Created prompt profile for persona: {persona.name}")

    db.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with SessionLocal() as session:
        backfill_astrologers(session)
        print("Astrologers backfill completed.")

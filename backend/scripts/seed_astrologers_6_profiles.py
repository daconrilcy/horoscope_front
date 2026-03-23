from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models import (
    AstrologerProfileModel,
    AstrologerPromptProfileModel,
    LlmPersonaModel,
)
from app.infra.db.session import SessionLocal

logger = logging.getLogger(__name__)

ASTROLOGERS = [
    {
        "id": "c0a80101-8edb-4e1a-8f1a-8f1a8f1a8f1a",
        "name": "Astrologue Standard",
        "display_name": "Étienne Garnier",
        "first_name": "Étienne",
        "last_name": "Garnier",
        "gender": "male",
        "provider_type": "ia",
        "age": 55,
        "photo_url": "/assets/astrologers/etienne.png",
        "public_style_label": "Pédagogue",
        "location": "Lyon, France",
        "quote": "L'astrologie n'est pas une fatalité, c'est une météo pour mieux naviguer.",
        "mission_statement": "Rendre l'astrologie accessible et utile au quotidien pour chacun.",
        "ideal_for": "Débutants cherchant une approche rassurante et structurée.",
        "metrics": {"experience_years": 15, "consultations_count": 1200, "average_rating": 4.8},
        "specialties_details": [
            {
                "title": "Bases du thème", 
                "description": "Comprendre sa structure de naissance sans jargon."
            },
            {
                "title": "Orientation", 
                "description": "Identifier ses forces naturelles et ses zones de talent."
            },
        ],
        "bio_short": (
            "Astrologue généraliste pédagogique, spécialisé dans l’accompagnement "
            "des débutants et la vulgarisation claire de l’astrologie."
        ),
        "admin_category": "standard",
        "specialties": ["Débutants", "Bases", "Onboarding"],
        "professional_background": [
            "20 ans professeur (philosophie / pédagogie)",
            "12 ans astrologue généraliste",
            "Création de programmes d’initiation à l’astrologie",
        ],
        "key_skills": ["Vulgarisation", "Thème natal", "Pédagogie"],
        "behavioral_style": ["Calme", "Rassurant", "Méthodique"],
        "sort_order": 1,
        "description": (
            "Étienne est un ancien professeur de philosophie passionné par la transmission."
        ),
        "tone": "calm",
        "verbosity": "medium",
        "style_markers": ["langage simple", "pedagogie"],
        "boundaries": ["eviter le jargon"],
        "allowed_topics": ["theme natal", "bases"],
        "disallowed_topics": ["diagnostic medical"],
        "formatting": {"sections": True, "bullets": True, "emojis": False},
        "enabled": True,
    },
    {
        "id": "de6d4827-63d4-40dc-8012-6de96f2e58f4",
        "name": "Selene Mystique",
        "display_name": "Sélène Ardent",
        "first_name": "Sélène",
        "last_name": "Ardent",
        "gender": "female",
        "provider_type": "ia",
        "age": 44,
        "photo_url": "/assets/astrologers/selene.png",
        "public_style_label": "Mystique",
        "location": "Montpellier, France",
        "quote": "Nous sommes faits de poussière d'étoiles et de cycles lunaires.",
        "mission_statement": "Reconnecter les âmes à leurs rythmes célestes profonds.",
        "ideal_for": "Profils intuitifs en quête de sens et de reconnexion émotionnelle.",
        "metrics": {"experience_years": 12, "consultations_count": 950, "average_rating": 4.9},
        "specialties_details": [
            {
                "title": "Cycles Lunaires", 
                "description": "Vivre en harmonie avec les phases de la Lune."
            },
            {
                "title": "Astrologie Karmique", 
                "description": "Explorer les mémoires et le chemin de l'âme."
            },
        ],
        "bio_short": (
            "Astrologue intuitive et symbolique, centrée sur les cycles "
            "et l'intégration émotionnelle."
        ),
        "admin_category": "mystical",
        "specialties": ["Spiritualité", "Cycles Lunaires", "Relations"],
        "professional_background": ["Études en symbolisme", "12 ans astrologie intuitive"],
        "key_skills": ["Lecture symbolique", "Rituels"],
        "behavioral_style": ["Imagé", "Poétique"],
        "sort_order": 2,
        "description": "Sélène explore la dimension poétique et archétypale du ciel.",
        "tone": "mystical",
        "verbosity": "long",
        "style_markers": ["images symboliques", "rituels"],
        "boundaries": ["pas de predictions categoriques"],
        "allowed_topics": ["theme natal", "spiritualite"],
        "disallowed_topics": ["diagnostic medical"],
        "formatting": {"sections": True, "bullets": False, "emojis": True},
        "enabled": True,
    },
    {
        "id": "f4f49f86-1ecf-4f3d-bbbf-2cf34ca71623",
        "name": "Orion Analyste",
        "display_name": "Orion Vasseur",
        "first_name": "Orion",
        "last_name": "Vasseur",
        "gender": "male",
        "provider_type": "ia",
        "age": 39,
        "photo_url": "/assets/astrologers/orion.png",
        "public_style_label": "Analytique",
        "location": "Paris, France",
        "quote": "La précision des astres au service de la stratégie de vie.",
        "mission_statement": "Apporter une rigueur d'ingénieur à l'analyse du ciel.",
        "ideal_for": "Profils cartésiens qui veulent des preuves et de la structure.",
        "metrics": {"experience_years": 10, "consultations_count": 1100, "average_rating": 4.7},
        "specialties_details": [
            {
                "title": "Audit de thème", 
                "description": "Vérifier la cohérence des dominantes astrales."
            },
            {
                "title": "Transits techniques", 
                "description": "Anticiper les périodes charnières avec précision."
            },
        ],
        "bio_short": (
            "Astrologue technique et méthodique, spécialisé dans la lecture "
            "structurée du thème."
        ),
        "admin_category": "rational",
        "specialties": ["Transits", "Carrière", "Organisation"],
        "professional_background": ["Ingénieur data", "10 ans astrologie technique"],
        "key_skills": ["Analyse", "Logique"],
        "behavioral_style": ["Méthodique", "Factuel"],
        "sort_order": 3,
        "description": "Orion traite le thème astral comme une architecture logique.",
        "tone": "rational",
        "verbosity": "short",
        "style_markers": ["precision", "structure"],
        "boundaries": ["ne pas extrapoler"],
        "allowed_topics": ["theme natal", "transits"],
        "disallowed_topics": ["diagnostic medical"],
        "formatting": {"sections": True, "bullets": True, "emojis": False},
        "enabled": True,
    },
    {
        "id": "f2879652-1f13-4f4e-8d68-57f13d5ba670",
        "name": "Luna Empathie",
        "display_name": "Luna Caron",
        "first_name": "Luna",
        "last_name": "Caron",
        "gender": "female",
        "provider_type": "ia",
        "age": 36,
        "photo_url": "/assets/astrologers/luna.png",
        "public_style_label": "Chaleureux",
        "location": "Bordeaux, France",
        "quote": "Le cœur a ses raisons que les astres nous aident à comprendre.",
        "mission_statement": "Accompagner les transitions de vie avec douceur et bienveillance.",
        "ideal_for": "Personnes traversant des remises en question relationnelles.",
        "metrics": {"experience_years": 7, "consultations_count": 800, "average_rating": 5.0},
        "specialties_details": [
            {
                "title": "Relationnel", 
                "description": "Décoder les dynamiques de couple et d'attachement."
            },
            {
                "title": "Estime de soi", 
                "description": "Utiliser son thème pour se réconcilier avec soi-même."
            },
        ],
        "bio_short": (
            "Astrologue relationnelle, chaleureuse et centrée sur la "
            "sécurité intérieure."
        ),
        "admin_category": "warm",
        "specialties": ["Relations", "Estime de soi", "Famille"],
        "professional_background": ["Accompagnement psy", "7 ans astrologue"],
        "key_skills": ["Empathie", "CNV"],
        "behavioral_style": ["Chaleureux", "Bienveillant"],
        "sort_order": 4,
        "description": "Luna aide à transformer les blocages émotionnels grâce au ciel.",
        "tone": "warm",
        "verbosity": "medium",
        "style_markers": ["ecoute active", "bienveillance"],
        "boundaries": ["pas de culpabilisation"],
        "allowed_topics": ["relations", "estime de soi"],
        "disallowed_topics": ["diagnostic medical"],
        "formatting": {"sections": True, "bullets": True, "emojis": False},
        "enabled": True,
    },
    {
        "id": "3a4fc82a-4286-48f6-babe-cab39992f5c4",
        "name": "Atlas Direct",
        "display_name": "Atlas Morel",
        "first_name": "Atlas",
        "last_name": "Morel",
        "gender": "male",
        "provider_type": "ia",
        "age": 42,
        "photo_url": "/assets/astrologers/atlas.png",
        "public_style_label": "Pragmatique",
        "location": "Bruxelles, Belgique",
        "quote": "L'astrologie est un outil de décision, pas une excuse.",
        "mission_statement": "Optimiser le timing de vos ambitions professionnelles.",
        "ideal_for": "Entrepreneurs et profils actifs qui veulent des résultats concrets.",
        "metrics": {"experience_years": 8, "consultations_count": 1300, "average_rating": 4.6},
        "specialties_details": [
            {
                "title": "Timing Business", 
                "description": "Choisir le meilleur moment pour lancer un projet."
            },
            {
                "title": "Arbitrage", 
                "description": "Trancher entre plusieurs options grâce aux cycles."
            },
        ],
        "bio_short": (
            "Astrologue orienté décision et performance, spécialisé en arbitrage "
            "professionnel."
        ),
        "admin_category": "direct",
        "specialties": ["Business", "Timing", "Objectifs"],
        "professional_background": ["Cabinet de conseil", "8 ans astrologue"],
        "key_skills": ["Decision", "Timing"],
        "behavioral_style": ["Direct", "Action-oriented"],
        "sort_order": 5,
        "description": "Atlas ne fait pas de détours : il cherche l'efficacité.",
        "tone": "direct",
        "verbosity": "short",
        "style_markers": ["franchise", "priorisation"],
        "boundaries": ["pas d alarmisme"],
        "allowed_topics": ["carriere", "objectifs"],
        "disallowed_topics": ["diagnostic medical"],
        "formatting": {"sections": True, "bullets": True, "emojis": False},
        "enabled": True,
    },
    {
        "id": "a38fbb78-14d6-4f54-b625-cf6f40b95f92",
        "name": "Nox Profondeur",
        "display_name": "Nox Delcourt",
        "first_name": "Nox",
        "last_name": "Delcourt",
        "gender": "non_binary",
        "provider_type": "ia",
        "age": 48,
        "photo_url": "/assets/astrologers/nox.png",
        "public_style_label": "Introspectif",
        "location": "Berlin, Allemagne",
        "quote": "C'est dans l'ombre du thème que se cache la vraie lumière.",
        "mission_statement": "Explorer les profondeurs de la psyché à travers le prisme astral.",
        "ideal_for": "Ceux qui n'ont pas peur de regarder leurs parts d'ombre.",
        "metrics": {"experience_years": 15, "consultations_count": 600, "average_rating": 4.9},
        "specialties_details": [
            {
                "title": "Shadow Work", 
                "description": "Intégrer les parts refoulées de sa personnalité."
            },
            {
                "title": "Métamorphose", 
                "description": "Accompagner les crises de vie transformatrices."
            },
        ],
        "bio_short": (
            "Astrologue introspectif de profondeur, orienté transformation et "
            "cycles de vie."
        ),
        "admin_category": "introspective",
        "specialties": ["Ombre", "Transformation", "Psychologie"],
        "professional_background": ["Psychanalyse", "15 ans astrologue"],
        "key_skills": ["Shadow work", "Transformation"],
        "behavioral_style": ["Lent", "Nuancé"],
        "sort_order": 6,
        "description": "Nox accompagne ceux qui cherchent une vérité brute et profonde.",
        "tone": "warm",
        "verbosity": "long",
        "style_markers": ["introspection", "nuance"],
        "boundaries": ["pas de therapie de remplacement"],
        "allowed_topics": ["vie interieure", "transformation"],
        "disallowed_topics": ["diagnostic medical"],
        "formatting": {"sections": True, "bullets": False, "emojis": False},
        "enabled": True,
    },
]


def _build_prompt_content(data: dict[str, object]) -> str:
    dedicated_prompt = str(data.get("prompt_content", "")).strip()
    if dedicated_prompt:
        return dedicated_prompt

    lines = [
        f"Adopte un ton {data['tone']}.",
        f"Longueur de réponse attendue : {data['verbosity']}.",
    ]
    style_markers = [str(marker) for marker in data.get("style_markers", [])]
    if style_markers:
        lines.append(f"Style : {', '.join(style_markers)}.")
    boundaries = [str(boundary) for boundary in data.get("boundaries", [])]
    if boundaries:
        lines.append("Contraintes éditoriales :")
        lines.extend(f"- {boundary}" for boundary in boundaries)
    allowed_topics = [str(topic) for topic in data.get("allowed_topics", [])]
    if allowed_topics:
        lines.append(f"Topics autorisés : {', '.join(allowed_topics)}.")
    disallowed_topics = [str(topic) for topic in data.get("disallowed_topics", [])]
    if disallowed_topics:
        lines.append(f"Topics exclus : {', '.join(disallowed_topics)}.")
    return "\n".join(lines)


def seed_astrologers(db: Session) -> None:
    canonical_ids_by_name = {item["name"]: uuid.UUID(item["id"]) for item in ASTROLOGERS}
    canonical_persona_ids = {uuid.UUID(item["id"]) for item in ASTROLOGERS}

    for data in ASTROLOGERS:
        stmt = select(LlmPersonaModel).where(LlmPersonaModel.id == uuid.UUID(data["id"]))
        persona = db.execute(stmt).scalar_one_or_none()

        if not persona:
            persona = LlmPersonaModel(
                id=uuid.UUID(data["id"]),
                name=data["name"],
                description=data["description"],
                tone=data["tone"],
                verbosity=data["verbosity"],
                style_markers=data["style_markers"],
                boundaries=data["boundaries"],
                allowed_topics=data["allowed_topics"],
                disallowed_topics=data["disallowed_topics"],
                formatting=data["formatting"],
                enabled=data["enabled"],
            )
            db.add(persona)
            logger.info(f"Created persona: {data['name']}")
        else:
            persona.name = data["name"]
            persona.description = data["description"]
            persona.tone = data["tone"]
            persona.verbosity = data["verbosity"]
            persona.style_markers = data["style_markers"]
            persona.boundaries = data["boundaries"]
            persona.allowed_topics = data["allowed_topics"]
            persona.disallowed_topics = data["disallowed_topics"]
            persona.formatting = data["formatting"]
            persona.enabled = data["enabled"]
            logger.info(f"Updated persona: {data['name']}")

        db.flush()

        # Update or create AstrologerProfile
        stmt_profile = select(AstrologerProfileModel).where(
            AstrologerProfileModel.persona_id == persona.id
        )
        profile = db.execute(stmt_profile).scalar_one_or_none()
        if not profile:
            profile = AstrologerProfileModel(
                persona_id=persona.id,
                first_name=data["first_name"],
                last_name=data["last_name"],
                display_name=data["display_name"],
                gender=data["gender"],
                provider_type=data.get("provider_type", "ia"),
                age=data["age"],
                photo_url=data["photo_url"],
                public_style_label=data["public_style_label"],
                location=data.get("location"),
                quote=data.get("quote"),
                mission_statement=data.get("mission_statement"),
                ideal_for=data.get("ideal_for"),
                metrics=data.get("metrics", {}),
                specialties_details=data.get("specialties_details", []),
                bio_short=data["bio_short"],
                bio_long=data["description"],
                admin_category=data["admin_category"],
                specialties=data["specialties"],
                professional_background=data["professional_background"],
                key_skills=data["key_skills"],
                behavioral_style=data["behavioral_style"],
                is_public=data["enabled"],
                sort_order=data["sort_order"],
            )
            db.add(profile)
            logger.info(f"Created profile for: {data['name']}")
        else:
            profile.first_name = data["first_name"]
            profile.last_name = data["last_name"]
            profile.display_name = data["display_name"]
            profile.gender = data["gender"]
            profile.provider_type = data.get("provider_type", "ia")
            profile.age = data["age"]
            profile.photo_url = data["photo_url"]
            profile.public_style_label = data["public_style_label"]
            profile.location = data.get("location")
            profile.quote = data.get("quote")
            profile.mission_statement = data.get("mission_statement")
            profile.ideal_for = data.get("ideal_for")
            profile.metrics = data.get("metrics", {})
            profile.specialties_details = data.get("specialties_details", [])
            profile.bio_short = data["bio_short"]
            profile.bio_long = data["description"]
            profile.admin_category = data["admin_category"]
            profile.specialties = data["specialties"]
            profile.professional_background = data["professional_background"]
            profile.key_skills = data["key_skills"]
            profile.behavioral_style = data["behavioral_style"]
            profile.is_public = data["enabled"]
            profile.sort_order = data["sort_order"]
            logger.info(f"Updated profile for: {data['name']}")

        prompt_stmt = (
            select(AstrologerPromptProfileModel)
            .where(AstrologerPromptProfileModel.persona_id == persona.id)
            .order_by(
                AstrologerPromptProfileModel.is_active.desc(),
                AstrologerPromptProfileModel.updated_at.desc(),
            )
        )
        prompt_profiles = db.execute(prompt_stmt).scalars().all()
        prompt_content = _build_prompt_content(data)
        active_prompt = next((prompt for prompt in prompt_profiles if prompt.is_active), None)

        if active_prompt is None:
            active_prompt = AstrologerPromptProfileModel(
                persona_id=persona.id,
                prompt_content=prompt_content,
                version="1.0.0-seed",
                is_active=True,
            )
            db.add(active_prompt)
            logger.info(f"Created active prompt profile for: {data['name']}")
        else:
            active_prompt.prompt_content = prompt_content
            active_prompt.version = "1.0.0-seed"
            active_prompt.is_active = True
            logger.info(f"Updated active prompt profile for: {data['name']}")

        for prompt_profile in prompt_profiles:
            if prompt_profile is not active_prompt and prompt_profile.is_active:
                prompt_profile.is_active = False
                logger.info(
                    "Disabled duplicate active prompt profile for: %s (%s)",
                    data["name"],
                    prompt_profile.id,
                )

    db.flush()

    # Disable duplicate legacy personas that share a seeded canonical name.
    for name, canonical_id in canonical_ids_by_name.items():
        duplicates = (
            db.execute(select(LlmPersonaModel).where(LlmPersonaModel.name == name)).scalars().all()
        )
        for duplicate in duplicates:
            if duplicate.id != canonical_id and duplicate.enabled:
                duplicate.enabled = False
                logger.info("Disabled duplicate persona: %s (%s)", duplicate.name, duplicate.id)

    stale_profiles = (
        db.execute(select(AstrologerProfileModel))
        .scalars()
        .all()
    )
    for stale_profile in stale_profiles:
        if stale_profile.persona_id in canonical_persona_ids:
            continue
        if stale_profile.photo_url:
            continue
        if stale_profile.is_public:
            stale_profile.is_public = False
            logger.info(
                "Hidden stale astrologer profile without photo: %s (%s)",
                stale_profile.display_name,
                stale_profile.persona_id,
            )

    db.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with SessionLocal() as session:
        seed_astrologers(session)
        print("Astrologers seed completed.")

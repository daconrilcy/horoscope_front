"""Initialise le catalogue canonique des consultations thematiques."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.consultation_template import ConsultationTemplateModel
from app.infra.db.session import SessionLocal

CONSULTATION_TEMPLATE_SEEDS: tuple[dict[str, Any], ...] = (
    {
        "key": "period",
        "icon_ref": "📅",
        "title": "Où j’en suis en ce moment",
        "subtitle": (
            "Faites le point sur la période que vous traversez et les dynamiques "
            "qui vous influencent."
        ),
        "description": (
            "Une analyse complète des transits actuels sur votre thème natal pour "
            "comprendre le climat du moment."
        ),
        "prompt_content": "Comprendre le climat astrologique de la periode demandee.",
        "metadata_config": {
            "tags": ["Introspection", "Bilan actuel"],
            "required_data": ["birth_profile"],
            "fallback_allowed": True,
        },
        "sort_order": 10,
    },
    {
        "key": "career",
        "icon_ref": "💼",
        "title": "Ma vie pro & mes décisions",
        "subtitle": "Éclairez vos choix professionnels, vos opportunités et vos prochaines étapes.",
        "description": (
            "Une lecture orientée sur votre carrière, vos ambitions et les "
            "périodes favorables pour agir professionnellement."
        ),
        "prompt_content": "Eclairer une interaction ou une decision liee au travail.",
        "metadata_config": {
            "tags": ["Carrière", "Ambition"],
            "required_data": ["birth_profile"],
            "fallback_allowed": True,
            "interaction_eligible": True,
        },
        "sort_order": 20,
    },
    {
        "key": "orientation",
        "icon_ref": "🗺️",
        "title": "Ce qui me correspond vraiment",
        "subtitle": (
            "Mieux comprendre vos forces, vos aspirations et la direction qui vous ressemble."
        ),
        "description": (
            "Un voyage au cœur de votre thème pour identifier votre mission de vie "
            "et vos potentiels innés."
        ),
        "prompt_content": "Clarifier une direction de vie ou une decision structurante.",
        "metadata_config": {
            "tags": ["Mission de vie", "Potentiels"],
            "required_data": ["birth_profile"],
            "fallback_allowed": False,
        },
        "sort_order": 30,
    },
    {
        "key": "relationship",
        "icon_ref": "🤝",
        "title": "Cette relation est-elle faite pour moi ?",
        "subtitle": (
            "Explorez la dynamique d’une relation amoureuse, personnelle ou professionnelle."
        ),
        "description": (
            "Une étude de synastrie ou de dynamique relationnelle pour éclairer "
            "vos liens avec autrui."
        ),
        "prompt_content": "Lire la dynamique relationnelle de maniere prudente et non fataliste.",
        "metadata_config": {
            "tags": ["Relations", "Synastrie"],
            "required_data": ["birth_profile"],
            "fallback_allowed": True,
            "interaction_eligible": True,
            "default_interaction": True,
        },
        "sort_order": 40,
    },
    {
        "key": "timing",
        "icon_ref": "⏱️",
        "title": "Est-ce le bon moment ?",
        "subtitle": "Identifiez les périodes les plus favorables pour agir, lancer ou décider.",
        "description": (
            "L'astrologie comme outil d'aide à la décision temporelle pour vos projets importants."
        ),
        "prompt_content": (
            "Identifier le bon tempo d action avec une lecture astrologique prudente."
        ),
        "metadata_config": {
            "tags": ["Timing", "Décision"],
            "required_data": ["birth_profile", "location"],
            "fallback_allowed": False,
        },
        "sort_order": 50,
    },
)


def seed_consultation_templates() -> None:
    """Cree ou met a jour les consultations canoniques avec des objectifs courts."""
    db: Session = SessionLocal()
    try:
        for t_data in CONSULTATION_TEMPLATE_SEEDS:
            # Check if exists
            existing = db.query(ConsultationTemplateModel).filter_by(key=t_data["key"]).first()
            if existing:
                print(f"Updating template: {t_data['key']}")
                for attr, value in t_data.items():
                    setattr(existing, attr, value)
                existing.updated_at = datetime_provider.utcnow()
            else:
                print(f"Creating template: {t_data['key']}")
                new_t = ConsultationTemplateModel(id=uuid.uuid4(), **t_data)
                db.add(new_t)

        db.commit()
        print("Seed completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_consultation_templates()

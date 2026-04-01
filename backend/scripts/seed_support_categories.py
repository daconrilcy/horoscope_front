from datetime import datetime, timezone

from sqlalchemy import select

from app.infra.db.models.support_ticket_category import SupportTicketCategoryModel
from app.infra.db.session import SessionLocal


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


CATEGORIES = [
    {
        "code": "subscription_problem",
        "label_fr": "Problème avec mon abonnement",
        "label_en": "Subscription issue",
        "label_es": "Problema con mi suscripción",
        "display_order": 1,
    },
    {
        "code": "billing_issue",
        "label_fr": "Problème de facturation",
        "label_en": "Billing issue",
        "label_es": "Problema de facturación",
        "display_order": 2,
    },
    {
        "code": "bug",
        "label_fr": "Bug / dysfonctionnement",
        "label_en": "Bug / technical issue",
        "label_es": "Error / problema técnico",
        "display_order": 3,
    },
    {
        "code": "account_access",
        "label_fr": "Problème d'accès à mon compte",
        "label_en": "Account access issue",
        "label_es": "Problema de acceso a la cuenta",
        "display_order": 4,
    },
    {
        "code": "feature_question",
        "label_fr": "Question sur une fonctionnalité",
        "label_en": "Feature question",
        "label_es": "Pregunta sobre una fonctionnalité",
        "display_order": 5,
    },
    {
        "code": "data_privacy",
        "label_fr": "Demande relative à mes données",
        "label_en": "Data & privacy request",
        "label_es": "Solicitud de datos y privacidad",
        "display_order": 6,
    },
    {
        "code": "other",
        "label_fr": "Autre demande",
        "label_en": "Other request",
        "label_es": "Otra solicitud",
        "display_order": 7,
    },
]


def seed_support_categories():
    with SessionLocal() as session:
        for cat_data in CATEGORIES:
            stmt = select(SupportTicketCategoryModel).where(SupportTicketCategoryModel.code == cat_data["code"])
            result = session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                print(f"Updating category: {cat_data['code']}")
                existing.label_fr = cat_data["label_fr"]
                existing.label_en = cat_data["label_en"]
                existing.label_es = cat_data["label_es"]
                existing.display_order = cat_data["display_order"]
            else:
                print(f"Creating category: {cat_data['code']}")
                new_cat = SupportTicketCategoryModel(
                    code=cat_data["code"],
                    label_fr=cat_data["label_fr"],
                    label_en=cat_data["label_en"],
                    label_es=cat_data["label_es"],
                    display_order=cat_data["display_order"],
                    created_at=utc_now(),
                )
                session.add(new_cat)

        session.commit()
    print("Seed completed successfully.")


if __name__ == "__main__":
    seed_support_categories()

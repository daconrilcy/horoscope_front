from sqlalchemy.orm import Session

from app.infra.db.models.consultation_template import ConsultationTemplateModel


class ConsultationCatalogueService:
    """
    Service pour gérer le catalogue des consultations types.
    Gère la récupération depuis la DB et la compatibilité des clés legacy.
    """
    
    @staticmethod
    def get_catalogue(db: Session) -> list[ConsultationTemplateModel]:
        """
        Récupère la liste des consultations actives ordonnées par sort_order.
        """
        return (
            db.query(ConsultationTemplateModel)
            .filter_by(is_active=True)
            .order_by(ConsultationTemplateModel.sort_order.asc())
            .all()
        )

    @staticmethod
    def map_legacy_key(key: str) -> str:
        """
        Assure la compatibilité entre les anciennes clés et les nouvelles clés canoniques.
        AC2: work -> career, relation -> relationship
        """
        mapping = {
            "work": "career",
            "relation": "relationship"
        }
        return mapping.get(key, key)

    @staticmethod
    def get_template_by_key(db: Session, key: str) -> ConsultationTemplateModel | None:
        """
        Récupère un template spécifique par sa clé, avec support legacy.
        """
        canonical_key = ConsultationCatalogueService.map_legacy_key(key)
        return db.query(ConsultationTemplateModel).filter_by(
            key=canonical_key, is_active=True
        ).first()

from sqlalchemy.orm import Session

from app.infra.db.models.consultation_template import ConsultationTemplateModel


class ConsultationCatalogueService:
    """
    Service pour gérer le catalogue des consultations types.
    Expose uniquement les clés canoniques stockées en base.
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
    def get_template_by_key(db: Session, key: str) -> ConsultationTemplateModel | None:
        """
        Récupère un template spécifique par sa clé canonique.
        """
        return db.query(ConsultationTemplateModel).filter_by(key=key, is_active=True).first()

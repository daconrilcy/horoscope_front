import logging

from sqlalchemy import delete

from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel
from app.infra.db.session import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def clear_chats():
    db = SessionLocal()
    try:
        # Supprimer d'abord les messages (clé étrangère sur conversation)
        num_messages = db.execute(delete(ChatMessageModel)).rowcount
        logger.info(f"Suppression de {num_messages} messages de chat.")

        num_conversations = db.execute(delete(ChatConversationModel)).rowcount
        logger.info(f"Suppression de {num_conversations} conversations de chat.")

        db.commit()
        logger.info("Base de données des chats vidée avec succès.")
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors du vidage des chats : {e}")
    finally:
        db.close()


if __name__ == "__main__":
    clear_chats()

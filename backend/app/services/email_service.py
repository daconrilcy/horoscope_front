import logging
import os
from datetime import datetime, timedelta, timezone

import jwt
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.email_log import EmailLogModel
from app.infra.db.models.user import UserModel
from app.services.email_provider import get_email_provider

logger = logging.getLogger(__name__)

# Basic Setup for Jinja2
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
jinja_env = Environment(
    loader=FileSystemLoader(template_dir), autoescape=select_autoescape(["html", "xml"])
)


class EmailService:
    @staticmethod
    def _render_template(template_name: str, **kwargs) -> str:
        template = jinja_env.get_template(f"emails/{template_name}")
        kwargs.setdefault("year", datetime.now().year)
        kwargs.setdefault("app_url", os.getenv("VITE_PRODUCTION_URL", "http://localhost:5173"))
        return template.render(**kwargs)

    @staticmethod
    def generate_unsubscribe_token(user_id: int, email_type: str = "marketing") -> str:
        """
        AC1: Generates a signed JWT token for unsubscription.
        """
        secret_key = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
        payload = {
            "user_id": user_id,
            "email_type": email_type,
            "exp": datetime.now(timezone.utc) + timedelta(days=30),
        }
        return jwt.encode(payload, secret_key, algorithm="HS256")

    @staticmethod
    def get_unsubscribe_link(user_id: int) -> str:
        """
        AC1: Generates the full unsubscription URL.
        """
        token = EmailService.generate_unsubscribe_token(user_id)
        base_url = os.getenv("APP_URL", "http://localhost:8000")
        return f"{base_url}/api/email/unsubscribe?token={token}"

    @staticmethod
    async def send_welcome_email(
        db: Session, user_id: int, email: str, firstname: str | None = None
    ) -> bool:
        """
        Sends a welcome email to a new user with idempotence check.
        """
        return await EmailService._send_email(
            db=db,
            user_id=user_id,
            email=email,
            email_type="welcome",
            template_name="welcome.html",
            subject="Bienvenue dans votre univers astrologique ✨",
            template_vars={"firstname": firstname, "email": email}
        )

    @staticmethod
    async def _send_email(
        db: Session, 
        user_id: int | None, 
        email: str, 
        email_type: str, 
        template_name: str, 
        subject: str,
        template_vars: dict
    ) -> bool:
        """
        Internal method to send email with idempotence and logging.
        """
        # AC3: Idempotence check
        if user_id:
            user_data = db.execute(
                select(UserModel.email_unsubscribed).where(UserModel.id == user_id)
            ).first()
            
            # AC4: Skip marketing if unsubscribed
            if user_data and user_data[0] and email_type == "marketing":
                logger.info(f"Skipping marketing email for unsubscribed user {user_id}")
                return True

            existing = db.execute(
                select(EmailLogModel).where(
                    EmailLogModel.user_id == user_id,
                    EmailLogModel.email_type == email_type,
                    EmailLogModel.status == "sent"
                )
            ).scalars().first()
            
            if existing:
                logger.info(f"Email {email_type} already sent to user {user_id}. Skipping.")
                return True

        enable_email = os.getenv("ENABLE_EMAIL", "false").lower() == "true"
        
        # Log attempt
        log_entry = EmailLogModel(
            user_id=user_id,
            email_type=email_type,
            recipient_email=email,
            status="pending"
        )
        db.add(log_entry)
        db.commit()

        try:
            html_content = EmailService._render_template(template_name, **template_vars)
            
            if not enable_email:
                logger.info(f"[EMAIL DISABLED] To: {email}, Type: {email_type}")
                log_entry.status = "skipped"
                log_entry.error_message = "Email globally disabled (ENABLE_EMAIL=false)"
                db.commit()
                return True

            provider = get_email_provider()
            message_id = await provider.send(to=email, subject=subject, html=html_content)
            
            log_entry.status = "sent"
            log_entry.provider_message_id = message_id
            db.commit()
            return True

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to send {email_type} email to {email}: {error_msg}")
            log_entry.status = "failed"
            log_entry.error_message = error_msg
            db.commit()
            return False

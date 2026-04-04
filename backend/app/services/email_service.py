import logging
import os
from datetime import datetime, timedelta, timezone

import jwt
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
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
        kwargs.setdefault("app_url", settings.app_url)
        return template.render(**kwargs)

    @staticmethod
    def generate_unsubscribe_token(user_id: int, email_type: str = "marketing") -> str:
        """
        AC1: Generates a signed JWT token for unsubscription.
        """
        payload = {
            "user_id": user_id,
            "email_type": email_type,
            "exp": datetime.now(timezone.utc) + timedelta(days=30),
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")

    @staticmethod
    def get_unsubscribe_link(user_id: int) -> str:
        """
        AC1: Generates the full unsubscription URL.
        """
        token = EmailService.generate_unsubscribe_token(user_id)
        return f"{settings.backend_url}/api/email/unsubscribe?token={token}"

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
            template_vars={"firstname": firstname, "email": email},
        )

    @staticmethod
    def schedule_onboarding_sequence(
        db: Session, user_id: int, email: str, firstname: str | None = None
    ):
        """
        AC2: Schedule 4 onboarding emails (J1, J3, J5, J7).
        """
        from datetime import datetime, timedelta, timezone

        from app.core.scheduler import scheduler

        # AC2.5: Skip scheduling if already unsubscribed
        user = db.get(UserModel, user_id)
        if user and user.email_unsubscribed:
            logger.info(f"Skipping onboarding sequence scheduling for unsubscribed user {user_id}")
            return

        base_time = datetime.now(timezone.utc)

        # J1: Education
        scheduler.add_job(
            EmailService.send_education_email_task,
            "date",
            run_date=base_time + timedelta(days=1),
            args=[user_id, email, firstname],
            id=f"email_j1_{user_id}",
            replace_existing=True,
        )

        # J3: Social Proof
        scheduler.add_job(
            EmailService.send_social_proof_email_task,
            "date",
            run_date=base_time + timedelta(days=3),
            args=[user_id, email, firstname],
            id=f"email_j3_{user_id}",
            replace_existing=True,
        )

        # J5: Objections
        scheduler.add_job(
            EmailService.send_objections_email_task,
            "date",
            run_date=base_time + timedelta(days=5),
            args=[user_id, email, firstname],
            id=f"email_j5_{user_id}",
            replace_existing=True,
        )

        # J7: Upgrade
        scheduler.add_job(
            EmailService.send_upgrade_email_task,
            "date",
            run_date=base_time + timedelta(days=7),
            args=[user_id, email, firstname],
            id=f"email_j7_{user_id}",
            replace_existing=True,
        )

    @staticmethod
    async def send_education_email_task(user_id: int, email: str, firstname: str | None):
        from app.infra.db.session import SessionLocal

        with SessionLocal() as db:
            await EmailService._send_email(
                db=db,
                user_id=user_id,
                email=email,
                email_type="onboarding_j1_education",
                template_name="education.html",
                subject="Comment lire votre horoscope personnalisé 🔭",
                template_vars={
                    "firstname": firstname,
                    "unsubscribe_url": EmailService.get_unsubscribe_link(user_id),
                },
            )

    @staticmethod
    async def send_social_proof_email_task(user_id: int, email: str, firstname: str | None):
        from app.infra.db.session import SessionLocal

        with SessionLocal() as db:
            await EmailService._send_email(
                db=db,
                user_id=user_id,
                email=email,
                email_type="onboarding_j3_social_proof",
                template_name="social_proof.html",
                subject="Ils ont trouvé leur voie avec Astrorizon ✨",
                template_vars={
                    "firstname": firstname,
                    "unsubscribe_url": EmailService.get_unsubscribe_link(user_id),
                },
            )

    @staticmethod
    async def send_objections_email_task(user_id: int, email: str, firstname: str | None):
        from app.infra.db.session import SessionLocal

        with SessionLocal() as db:
            await EmailService._send_email(
                db=db,
                user_id=user_id,
                email=email,
                email_type="onboarding_j5_objections",
                template_name="objections.html",
                subject="Vos questions sur Astrorizon 🤔",
                template_vars={
                    "firstname": firstname,
                    "unsubscribe_url": EmailService.get_unsubscribe_link(user_id),
                },
            )

    @staticmethod
    async def send_upgrade_email_task(user_id: int, email: str, firstname: str | None):
        from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
        from app.infra.db.session import SessionLocal

        with SessionLocal() as db:
            # AC2.6: Skip if already subscribed
            # Check user_subscriptions for active status
            sub = (
                db.execute(
                    select(UserSubscriptionModel).where(
                        UserSubscriptionModel.user_id == user_id,
                        UserSubscriptionModel.status == "active",
                    )
                )
                .scalars()
                .first()
            )

            if sub:
                logger.info(
                    f"User {user_id} already has an active subscription. Skipping upgrade email."
                )
                return

            # AC16: Dynamic price from canonical source
            plan = (
                db.execute(select(BillingPlanModel).where(BillingPlanModel.code == "premium"))
                .scalars()
                .first()
            )
            price = str(plan.monthly_price_cents // 100) if plan else "29"

            await EmailService._send_email(
                db=db,
                user_id=user_id,
                email=email,
                email_type="onboarding_j7_upgrade",
                template_name="upgrade.html",
                subject="Débloquez vos insights premium 🌟",
                template_vars={
                    "firstname": firstname,
                    "price": price,
                    "per_month": "/mois",
                    "unsubscribe_url": EmailService.get_unsubscribe_link(user_id),
                },
            )

    @staticmethod
    async def _send_email(
        db: Session,
        user_id: int | None,
        email: str,
        email_type: str,
        template_name: str,
        subject: str,
        template_vars: dict,
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
            marketing_types = {
                "marketing",
                "onboarding_j1_education",
                "onboarding_j3_social_proof",
                "onboarding_j5_objections",
                "onboarding_j7_upgrade",
            }
            if user_data and user_data[0] and email_type in marketing_types:
                logger.info(f"Skipping marketing email for unsubscribed user {user_id}")
                return True

            existing = (
                db.execute(
                    select(EmailLogModel).where(
                        EmailLogModel.user_id == user_id,
                        EmailLogModel.email_type == email_type,
                        EmailLogModel.status == "sent",
                    )
                )
                .scalars()
                .first()
            )

            if existing:
                logger.info(f"Email {email_type} already sent to user {user_id}. Skipping.")
                return True

        enable_email = os.getenv("ENABLE_EMAIL", "false").lower() == "true"

        # Log attempt
        log_entry = EmailLogModel(
            user_id=user_id, email_type=email_type, recipient_email=email, status="pending"
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

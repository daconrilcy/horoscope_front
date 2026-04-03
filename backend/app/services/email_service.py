import logging
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.core.config import settings

logger = logging.getLogger(__name__)

# Basic Setup for Jinja2
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
jinja_env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(['html', 'xml'])
)

class EmailService:
    @staticmethod
    def _render_template(template_name: str, **kwargs) -> str:
        template = jinja_env.get_template(f"emails/{template_name}")
        kwargs.setdefault("year", datetime.now().year)
        kwargs.setdefault("app_url", os.getenv("VITE_PRODUCTION_URL", "http://localhost:5173"))
        kwargs.setdefault("app_name", settings.email_from_name)
        return template.render(**kwargs)

    @staticmethod
    def _get_text_content(template_name: str, **kwargs) -> str:
        """
        Provides a plain text version of the email.
        In a real scenario, we might want a separate .txt template.
        For now, we'll provide a basic mapping for welcome.html.
        """
        if template_name == "welcome.html":
            firstname = kwargs.get("firstname")
            email = kwargs.get("email")
            app_url = os.getenv("VITE_PRODUCTION_URL", "http://localhost:5173")
            greeting = f"Bienvenue, {firstname}" if firstname else "Bonjour"
            return (
                f"{greeting} ✨\n\n"
                f"Votre compte Astrorizon a été créé avec succès pour l'adresse {email}.\n\n"
                "Nous sommes ravis de vous accompagner dans votre exploration astrologique. "
                "La première étape consiste à configurer votre profil natal pour obtenir des "
                "prévisions d'une précision inégalée.\n\n"
                f"Calculer mon thème natal : {app_url}/profile\n\n"
                "Besoin d'aide ? Notre support est à votre écoute. Répondez simplement à cet email "
                "ou consultez notre centre d'aide dans l'application.\n\n"
                "À très vite sous les étoiles,\nL'équipe Astrorizon"
            )
        return ""

    @staticmethod
    def send_welcome_email(user_id: int, email: str, firstname: str | None = None) -> bool:
        """
        Sends a welcome email to a new user.
        """
        enable_email = settings.enable_email
        provider = settings.email_provider

        subject = "Bienvenue dans votre univers astrologique ✨"
        
        try:
            html_content = EmailService._render_template("welcome.html", email=email, firstname=firstname)
            text_content = EmailService._get_text_content("welcome.html", email=email, firstname=firstname)
            
            if not enable_email or provider == "noop":
                logger.info(f"[EMAIL NOOP] To: {email}, Subject: {subject}")
                logger.debug(f"[EMAIL CONTENT HTML]\n{html_content}")
                logger.debug(f"[EMAIL CONTENT TEXT]\n{text_content}")
                return True

            if provider == "brevo":
                return EmailService._send_via_brevo(email, subject, html_content, text_content)
            
            logger.warning(f"Email provider {provider} not implemented.")
            return False

        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {str(e)}", exc_info=True)
            return False

    @staticmethod
    def _send_via_brevo(email: str, subject: str, html_content: str, text_content: str) -> bool:
        api_key = settings.brevo_api_key
        if not api_key:
            logger.error("BREVO_API_KEY not found in settings.")
            return False

        try:
            import sib_api_v3_sdk
            from sib_api_v3_sdk.rest import ApiException

            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = api_key
            
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            
            sender = {"name": settings.email_from_name, "email": settings.email_from}
            to = [{"email": email}]
            
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to,
                html_content=html_content,
                text_content=text_content,
                sender=sender,
                subject=subject
            )

            api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email sent successfully to {email} via Brevo")
            return True

        except ImportError:
            logger.error("sib-api-v3-sdk not installed. Please install it to use Brevo provider.")
            return False
        except ApiException as e:
            logger.error(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email via Brevo: {str(e)}")
            return False

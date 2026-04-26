import logging
import os
from typing import Protocol

logger = logging.getLogger(__name__)


class EmailProvider(Protocol):
    async def send(self, to: str, subject: str, html: str) -> str:
        """
        Sends an email and returns the provider message ID.
        Raises an exception if the send fails.
        """
        ...


class NoopEmailProvider:
    async def send(self, to: str, subject: str, html: str) -> str:
        logger.debug(f"[NOOP EMAIL] To: {to}, Subject: {subject}")
        # Return a fake message ID
        import uuid

        return f"noop-{uuid.uuid4()}"


class BrevoEmailProvider:
    async def send(self, to: str, subject: str, html: str) -> str:
        api_key = os.getenv("BREVO_API_KEY")
        if not api_key:
            raise ValueError("BREVO_API_KEY not found in environment variables.")

        import sib_api_v3_sdk
        from sib_api_v3_sdk.rest import ApiException

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = api_key

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        sender = {"name": "Astrorizon", "email": os.getenv("EMAIL_FROM", "hello@astrorizon.ai")}

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to}], html_content=html, sender=sender, subject=subject
        )

        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            return api_response.message_id
        except ApiException as e:
            logger.error(f"Brevo API error: {e}")
            raise


def get_email_provider() -> EmailProvider:
    provider_name = os.getenv("EMAIL_PROVIDER", "noop").lower()

    if provider_name == "brevo":
        return BrevoEmailProvider()

    return NoopEmailProvider()

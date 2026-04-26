"""Namespace canonique des services email."""

from app.services.email.provider import EmailProvider, get_email_provider
from app.services.email.service import EmailService

__all__ = ["EmailProvider", "EmailService", "get_email_provider"]

"""Centralise l'anonymisation des charges utiles LLM avant log, audit ou persistance."""

from __future__ import annotations

import hashlib

from app.core.config import settings
from app.core.pii_patterns import (
    ADDRESS_FIELD_REGEX,
    EMAIL_REGEX,
    GENERIC_ID_FIELD_REGEX,
    ID_FIELD_REGEX,
    IDENTIFIER_PHRASE_REGEX,
    NAME_FIELD_REGEX,
    PHONE_REGEX,
    UUID_REGEX,
)
from app.infra.observability.metrics import increment_counter


class LLMAnonymizationError(Exception):
    """Signale un échec d'anonymisation avant exposition d'un contenu sensible."""


def _token(prefix: str, value: str) -> str:
    """Construit un jeton stable salé afin de préserver la corrélation sans exposer la donnée."""
    salted_value = f"{settings.llm_anonymization_salt}:{value}"
    digest = hashlib.sha256(salted_value.encode("utf-8")).hexdigest()[:8]
    return f"[redacted_{prefix}_{digest}]"


def anonymize_text(text: str) -> str:
    """Anonymise les identifiants directs et corrélables présents dans un texte libre."""
    try:
        without_emails = EMAIL_REGEX.sub(lambda match: _token("email", match.group(0)), text)
        without_uuids = UUID_REGEX.sub(lambda match: _token("id", match.group(0)), without_emails)
        without_phones = PHONE_REGEX.sub(
            lambda match: _token("phone", match.group(0)),
            without_uuids,
        )
        without_names = NAME_FIELD_REGEX.sub(
            lambda match: f"{match.group(1)}={_token('name', match.group(2).strip())}",
            without_phones,
        )
        without_addresses = ADDRESS_FIELD_REGEX.sub(
            lambda match: f"{match.group(1)}={_token('address', match.group(2).strip())}",
            without_names,
        )
        without_known_ids = ID_FIELD_REGEX.sub(
            lambda match: f"{match.group(1)}={_token('id', match.group(2).strip())}",
            without_addresses,
        )
        without_generic_ids = GENERIC_ID_FIELD_REGEX.sub(
            lambda match: f"{match.group(1)}={_token('id', match.group(2).strip())}",
            without_known_ids,
        )
        anonymized = IDENTIFIER_PHRASE_REGEX.sub(
            lambda match: f"{match.group(1)} est {_token('id', match.group(2).strip())}",
            without_generic_ids,
        )
        increment_counter("llm_anonymization_events_total", 1.0)
        return anonymized
    except Exception as error:
        increment_counter("llm_anonymization_failures_total", 1.0)
        raise LLMAnonymizationError("failed to anonymize llm payload") from error

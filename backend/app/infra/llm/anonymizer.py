from __future__ import annotations

import hashlib
import re

from app.core.config import settings
from app.infra.observability.metrics import increment_counter

EMAIL_REGEX = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
PHONE_REGEX = re.compile(r"\b(?:\+?\d[\s.-]?){7,}\d\b")
UUID_REGEX = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
NAME_FIELD_REGEX = re.compile(
    r"\b(name|nom|prenom|first_name|last_name)\s*[:=]\s*([^\n,;]+)",
    re.IGNORECASE,
)
ADDRESS_FIELD_REGEX = re.compile(
    r"\b(address|adresse|street|city|postal_code|zip)\s*[:=]\s*([^\n,;]+)",
    re.IGNORECASE,
)
ID_FIELD_REGEX = re.compile(
    r"\b(user_id|account_id|customer_id|id_utilisateur)\s*[:=]\s*([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)
GENERIC_ID_FIELD_REGEX = re.compile(
    r"\b(id|identifier|identifiant)\s*[:=]\s*([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)
IDENTIFIER_PHRASE_REGEX = re.compile(
    r"\b(identifiant(?:\s+interne)?|identifier)\s+(?:est|is)\s+([A-Za-z0-9_-]+)\b",
    re.IGNORECASE,
)


class LLMAnonymizationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def _token(prefix: str, value: str) -> str:
    salted_value = f"{settings.llm_anonymization_salt}:{value}"
    digest = hashlib.sha256(salted_value.encode("utf-8")).hexdigest()[:8]
    return f"[redacted_{prefix}_{digest}]"


def anonymize_text(text: str) -> str:
    try:
        without_emails = EMAIL_REGEX.sub(lambda m: _token("email", m.group(0)), text)
        without_uuids = UUID_REGEX.sub(lambda m: _token("id", m.group(0)), without_emails)
        without_phones = PHONE_REGEX.sub(lambda m: _token("phone", m.group(0)), without_uuids)
        without_names = NAME_FIELD_REGEX.sub(
            lambda m: f"{m.group(1)}={_token('name', m.group(2).strip())}",
            without_phones,
        )
        without_addresses = ADDRESS_FIELD_REGEX.sub(
            lambda m: f"{m.group(1)}={_token('address', m.group(2).strip())}",
            without_names,
        )
        without_known_ids = ID_FIELD_REGEX.sub(
            lambda m: f"{m.group(1)}={_token('id', m.group(2).strip())}",
            without_addresses,
        )
        without_generic_ids = GENERIC_ID_FIELD_REGEX.sub(
            lambda m: f"{m.group(1)}={_token('id', m.group(2).strip())}",
            without_known_ids,
        )
        without_identifier_phrases = IDENTIFIER_PHRASE_REGEX.sub(
            lambda m: f"{m.group(1)} est {_token('id', m.group(2).strip())}",
            without_generic_ids,
        )
        increment_counter("llm_anonymization_events_total", 1.0)
        return without_identifier_phrases
    except Exception as error:
        increment_counter("llm_anonymization_failures_total", 1.0)
        raise LLMAnonymizationError("failed to anonymize llm payload") from error

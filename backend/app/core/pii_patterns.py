"""Définit les motifs regex partagés pour détecter les données sensibles courantes."""

from __future__ import annotations

import re

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

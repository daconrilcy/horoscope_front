from __future__ import annotations

import json
from typing import Any, Dict

from cryptography.fernet import Fernet

from app.core.config import settings


def get_fernet() -> Fernet:
    return Fernet(settings.llm_replay_encryption_key.encode())


def encrypt_input(user_input: Dict[str, Any]) -> bytes:
    """
    Encrypts user input using AES-256 (Fernet).
    """
    serialized = json.dumps(user_input, sort_keys=True)
    return get_fernet().encrypt(serialized.encode("utf-8"))


def decrypt_input(encrypted_data: bytes) -> Dict[str, Any]:
    """
    Decrypts user input.
    """
    decrypted = get_fernet().decrypt(encrypted_data)
    return json.loads(decrypted.decode("utf-8"))

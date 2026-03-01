from unittest.mock import patch

import pytest

from app.llm_orchestration.models import GatewayError
from app.llm_orchestration.services.crypto_utils import decrypt_input, encrypt_input
from app.llm_orchestration.services.replay_service import replay


def test_encryption_roundtrip():
    data = {"secret": "data", "number": 42}
    encrypted = encrypt_input(data)
    decrypted = decrypt_input(encrypted)
    assert decrypted == data
    assert encrypted != b'{"secret": "data", "number": 42}'


@pytest.mark.asyncio
async def test_replay_refuses_in_prod(db):
    with patch("app.llm_orchestration.services.replay_service.settings") as mock_settings:
        mock_settings.app_env = "production"
        with pytest.raises(GatewayError) as exc:
            await replay(db, "any-req", "any-prompt")
        assert "disabled in production" in str(exc.value)


@pytest.mark.asyncio
async def test_replay_not_found(db):
    with pytest.raises(GatewayError) as exc:
        await replay(db, "non-existent", "any-prompt")
    assert "Call log not found" in str(exc.value)

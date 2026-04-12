from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.startup.llm_coherence_validation import run_llm_coherence_startup_validation

VALIDATE_PATH = (
    "app.startup.llm_coherence_validation.ConfigCoherenceValidator.scan_active_configurations"
)


@pytest.mark.asyncio
async def test_llm_coherence_startup_validation_strict_ok(caplog):
    session = MagicMock()
    with patch(VALIDATE_PATH, new=AsyncMock(return_value=[])) as mock_scan:
        with caplog.at_level("INFO", logger="app.startup.llm_coherence_validation"):
            await run_llm_coherence_startup_validation("strict", session)

    mock_scan.assert_awaited_once()
    assert "all active configurations are coherent" in caplog.text


@pytest.mark.asyncio
async def test_llm_coherence_startup_validation_warn_does_not_block(caplog):
    session = MagicMock()
    fake_error = MagicMock(error_code="missing_execution_profile", message="boom")
    fake_result = MagicMock(errors=[fake_error])
    fake_config = MagicMock(feature="chat", subfeature="astrologer", plan="free")

    with patch(
        VALIDATE_PATH, new=AsyncMock(return_value=[(fake_config, fake_result)])
    ) as mock_scan:
        with caplog.at_level("WARNING", logger="app.startup.llm_coherence_validation"):
            await run_llm_coherence_startup_validation("warn", session)

    mock_scan.assert_awaited_once()
    assert "llm_coherence_violation" in caplog.text
    assert "completed with 1 warnings" in caplog.text


@pytest.mark.asyncio
async def test_llm_coherence_startup_validation_strict_blocks(caplog):
    session = MagicMock()
    fake_error = MagicMock(error_code="missing_execution_profile", message="boom")
    fake_result = MagicMock(errors=[fake_error])
    fake_config = MagicMock(feature="chat", subfeature="astrologer", plan="free")

    with patch(
        VALIDATE_PATH, new=AsyncMock(return_value=[(fake_config, fake_result)])
    ) as mock_scan:
        with caplog.at_level("ERROR", logger="app.startup.llm_coherence_validation"):
            with pytest.raises(RuntimeError, match="Startup blocked"):
                await run_llm_coherence_startup_validation("strict", session)

    mock_scan.assert_awaited_once()
    assert "llm_coherence_violation" in caplog.text

import logging
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.llm_orchestration.services.config_coherence_validator import ConfigCoherenceValidator

logger = logging.getLogger(__name__)


async def run_llm_coherence_startup_validation(
    mode: str, session: Union[AsyncSession, Session]
) -> None:
    """
    Scan all active published LLM configurations for coherence at startup.
    (Story 66.31 AC10)
    """
    if mode == "off":
        logger.info("llm_coherence_startup_validation mode=off - skipping")
        return

    logger.info(
        "llm_coherence_startup_validation mode=%s - scanning active snapshot "
        "or published configurations",
        mode,
    )

    validator = ConfigCoherenceValidator(session)
    results = await validator.scan_active_configurations()

    invalid_count = len(results)
    if invalid_count == 0:
        logger.info(
            "llm_coherence_startup_validation success - all active configurations are coherent"
        )
        return

    # Report failures
    for config, result in results:
        for error in result.errors:
            log_msg = (
                f"llm_coherence_violation feature={config.feature} "
                f"subfeature={config.subfeature} plan={config.plan} "
                f"error_code={error.error_code} message={error.message}"
            )
            if mode == "strict":
                logger.error(log_msg)
            else:
                logger.warning(log_msg)

    if mode == "strict":
        error_msg = (
            f"Startup blocked: {invalid_count} incoherent LLM configurations "
            "detected in strict mode."
        )
        logger.critical(error_msg)
        raise RuntimeError(error_msg)
    else:
        logger.warning("llm_coherence_startup_validation completed with %d warnings", invalid_count)

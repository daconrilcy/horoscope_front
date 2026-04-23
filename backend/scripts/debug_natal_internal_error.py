from __future__ import annotations

import argparse
import asyncio
import logging
import traceback
import uuid

from sqlalchemy import select

from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.session import SessionLocal
from app.services.natal_interpretation_service_v2 import NatalInterpretationServiceV2
from app.services.user_birth_profile_service import UserBirthProfileService
from app.services.user_natal_chart_service import UserNatalChartService


def _setup_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


async def _run(
    *,
    user_id: int,
    locale: str,
    persona_id: str | None,
    request_id: str,
    force_refresh: bool,
) -> None:
    logger = logging.getLogger("debug_natal_internal_error")
    db = SessionLocal()
    try:
        logger.info("Loading latest chart + profile for user_id=%s", user_id)
        chart = UserNatalChartService.get_latest_for_user(db, user_id)
        profile = UserBirthProfileService.get_for_user(db, user_id)
        logger.info("Chart loaded: chart_id=%s", chart.chart_id)
        logger.info(
            "Birth profile loaded: date=%s time=%s place=%s tz=%s",
            profile.birth_date,
            profile.birth_time,
            profile.birth_place,
            profile.birth_timezone,
        )

        resolved_persona_id = persona_id
        if not resolved_persona_id:
            stmt = select(LlmPersonaModel.id).where(LlmPersonaModel.name == "Astrologue Standard")
            pid = db.execute(stmt).scalar_one_or_none()
            if pid:
                resolved_persona_id = str(pid)
                logger.info("Using default persona Astrologue Standard: %s", resolved_persona_id)

        if not resolved_persona_id:
            raise RuntimeError("No persona_id provided and default persona not found.")

        # Validate UUID format early for clearer diagnostics.
        uuid.UUID(str(resolved_persona_id))

        logger.info(
            "Calling NatalInterpretationServiceV2.interpret(level=complete, force_refresh=%s)",
            force_refresh,
        )
        resp = await NatalInterpretationServiceV2.interpret(
            db=db,
            user_id=user_id,
            chart_id=chart.chart_id,
            natal_result=chart.result,
            birth_profile=profile,
            level="complete",
            persona_id=resolved_persona_id,
            locale=locale,
            question=None,
            request_id=request_id,
            trace_id=request_id,
            force_refresh=force_refresh,
            module=None,
        )

        logger.info("SUCCESS request_id=%s", request_id)
        logger.info(
            "meta.use_case=%s schema_version=%s validation=%s",
            resp.data.meta.use_case,
            resp.data.meta.schema_version,
            resp.data.meta.validation_status,
        )
        logger.info(
            "sections=%s highlights=%s advice=%s",
            len(resp.data.interpretation.sections),
            len(resp.data.interpretation.highlights),
            len(resp.data.interpretation.advice),
        )
    except Exception as exc:
        logger.error("FAILED request_id=%s exception=%s", request_id, exc)
        traceback.print_exc()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Debug direct natal interpretation call with detailed logs."
    )
    parser.add_argument("--user-id", type=int, default=4)
    parser.add_argument("--locale", type=str, default="fr-FR")
    parser.add_argument("--persona-id", type=str, default="")
    parser.add_argument("--request-id", type=str, default="debug-direct-natal-001")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    _setup_logging(args.debug)
    asyncio.run(
        _run(
            user_id=args.user_id,
            locale=args.locale,
            persona_id=args.persona_id or None,
            request_id=args.request_id,
            force_refresh=args.force_refresh,
        )
    )


if __name__ == "__main__":
    main()

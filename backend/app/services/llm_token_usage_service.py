from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.services.entitlement_types import QuotaDefinition, UsageState
from app.services.quota_usage_service import QuotaUsageService

logger = logging.getLogger(__name__)


class LlmTokenUsageService:
    @staticmethod
    def record_usage(
        db: Session,
        *,
        user_id: int,
        feature_code: str,
        quota: QuotaDefinition | None,
        provider_model: str,
        tokens_in: int,
        tokens_out: int,
        request_id: str,
        llm_call_log_id: uuid.UUID | None = None,
        ref_dt: datetime | None = None,
    ) -> UsageState | None:
        """
        Records LLM token usage for a user.
        Atomically increments the usage counter (if quota provided) and creates a detailed usage log.
        """
        if ref_dt is None:
            ref_dt = datetime.now(timezone.utc)

        tokens_total = tokens_in + tokens_out
        usage_state = None

        # 1. Increment the usage counter (within transaction) if quota is provided
        if quota:
            usage_state = QuotaUsageService.consume(
                db,
                user_id=user_id,
                feature_code=feature_code,
                quota=quota,
                amount=tokens_total,
                ref_dt=ref_dt,
            )

        # 2. Create the usage log (within transaction)
        usage_log = UserTokenUsageLogModel(
            user_id=user_id,
            feature_code=feature_code,
            provider_model=provider_model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            tokens_total=tokens_total,
            request_id=request_id,
            llm_call_log_id=llm_call_log_id,
            created_at=ref_dt,
        )
        db.add(usage_log)

        # Flush to ensure constraints are checked and IDs are generated
        db.flush()

        logger.info(
            "Recorded %d tokens for user %d (feature: %s, request_id: %s, quota_applied: %s)",
            tokens_total,
            user_id,
            feature_code,
            request_id,
            bool(quota),
        )

        return usage_state

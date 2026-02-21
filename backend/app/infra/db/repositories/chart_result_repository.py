from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.infra.db.models.chart_result import ChartResultModel


class ChartResultRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        user_id: int | None,
        chart_id: str,
        reference_version: str,
        ruleset_version: str,
        input_hash: str,
        result_payload: dict[str, object],
    ) -> ChartResultModel:
        model = ChartResultModel(
            user_id=user_id,
            chart_id=chart_id,
            reference_version=reference_version,
            ruleset_version=ruleset_version,
            input_hash=input_hash,
            result_payload=result_payload,
        )
        self.db.add(model)
        self.db.flush()
        return model

    def get_by_chart_id(self, chart_id: str) -> ChartResultModel | None:
        return self.db.scalar(select(ChartResultModel).where(ChartResultModel.chart_id == chart_id))

    def get_latest_by_user_id(self, user_id: int) -> ChartResultModel | None:
        return self.db.scalar(
            select(ChartResultModel)
            .where(ChartResultModel.user_id == user_id)
            .order_by(desc(ChartResultModel.created_at), desc(ChartResultModel.id))
            .limit(1)
        )

    def get_recent_by_user_id(self, user_id: int, limit: int = 50) -> list[ChartResultModel]:
        rows = self.db.scalars(
            select(ChartResultModel)
            .where(ChartResultModel.user_id == user_id)
            .order_by(desc(ChartResultModel.created_at), desc(ChartResultModel.id))
            .limit(limit)
        )
        return list(rows)

    def get_previous_comparable_for_chart(
        self,
        *,
        user_id: int,
        chart_id: str,
        input_hash: str,
        reference_version: str,
        ruleset_version: str,
    ) -> ChartResultModel | None:
        return self.db.scalar(
            select(ChartResultModel)
            .where(ChartResultModel.user_id == user_id)
            .where(ChartResultModel.chart_id != chart_id)
            .where(ChartResultModel.input_hash == input_hash)
            .where(ChartResultModel.reference_version == reference_version)
            .where(ChartResultModel.ruleset_version == ruleset_version)
            .order_by(desc(ChartResultModel.created_at), desc(ChartResultModel.id))
            .limit(1)
        )

    def get_legacy_candidates(self, limit: int = 500) -> list[ChartResultModel]:
        rows = self.db.scalars(
            select(ChartResultModel)
            .where(ChartResultModel.user_id.is_(None))
            .order_by(desc(ChartResultModel.created_at), desc(ChartResultModel.id))
            .limit(limit)
        )
        return list(rows)

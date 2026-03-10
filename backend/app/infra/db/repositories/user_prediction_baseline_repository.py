from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.infra.db.models.user_prediction_baseline import UserPredictionBaselineModel
from app.prediction.persisted_baseline import PersistedUserBaseline


class UserPredictionBaselineRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_baseline(
        self,
        user_id: int,
        category_id: int,
        reference_version_id: int,
        ruleset_id: int,
        house_system_effective: str,
        window_days: int,
        window_start_date: date,
        window_end_date: date,
    ) -> PersistedUserBaseline | None:
        model = self.db.scalar(
            select(UserPredictionBaselineModel)
            .options(selectinload(UserPredictionBaselineModel.category))
            .where(
                UserPredictionBaselineModel.user_id == user_id,
                UserPredictionBaselineModel.category_id == category_id,
                UserPredictionBaselineModel.reference_version_id == reference_version_id,
                UserPredictionBaselineModel.ruleset_id == ruleset_id,
                UserPredictionBaselineModel.house_system_effective == house_system_effective,
                UserPredictionBaselineModel.window_days == window_days,
                UserPredictionBaselineModel.window_start_date == window_start_date,
                UserPredictionBaselineModel.window_end_date == window_end_date,
            )
        )
        return self._to_persisted(model) if model else None

    def get_baselines_for_user(
        self,
        user_id: int,
        reference_version_id: int,
        ruleset_id: int,
        house_system_effective: str,
        window_days: int,
        window_start_date: date,
        window_end_date: date,
    ) -> list[PersistedUserBaseline]:
        models = self.db.scalars(
            select(UserPredictionBaselineModel)
            .options(selectinload(UserPredictionBaselineModel.category))
            .where(
                UserPredictionBaselineModel.user_id == user_id,
                UserPredictionBaselineModel.reference_version_id == reference_version_id,
                UserPredictionBaselineModel.ruleset_id == ruleset_id,
                UserPredictionBaselineModel.house_system_effective == house_system_effective,
                UserPredictionBaselineModel.window_days == window_days,
                UserPredictionBaselineModel.window_start_date == window_start_date,
                UserPredictionBaselineModel.window_end_date == window_end_date,
            )
        ).all()
        return [self._to_persisted(m) for m in models]

    def get_latest_baselines_for_user(
        self,
        user_id: int,
        reference_version_id: int,
        ruleset_id: int,
        house_system_effective: str,
        window_days: int,
        as_of_date: date,
    ) -> list[PersistedUserBaseline]:
        models = self.db.scalars(
            select(UserPredictionBaselineModel)
            .options(selectinload(UserPredictionBaselineModel.category))
            .where(
                UserPredictionBaselineModel.user_id == user_id,
                UserPredictionBaselineModel.reference_version_id == reference_version_id,
                UserPredictionBaselineModel.ruleset_id == ruleset_id,
                UserPredictionBaselineModel.house_system_effective == house_system_effective,
                UserPredictionBaselineModel.window_days == window_days,
                UserPredictionBaselineModel.window_end_date <= as_of_date,
            )
            .order_by(
                UserPredictionBaselineModel.window_end_date.desc(),
                UserPredictionBaselineModel.window_start_date.desc(),
            )
        ).all()

        if not models:
            return []

        latest_end_date = models[0].window_end_date
        latest_start_date = models[0].window_start_date
        latest_models = [
            model
            for model in models
            if model.window_end_date == latest_end_date
            and model.window_start_date == latest_start_date
        ]
        return [self._to_persisted(model) for model in latest_models]

    def upsert_baseline(
        self,
        user_id: int,
        category_id: int,
        reference_version_id: int,
        ruleset_id: int,
        house_system_effective: str,
        window_days: int,
        window_start_date: date,
        window_end_date: date,
        stats: dict[str, float | int],
    ) -> PersistedUserBaseline:
        model = self._get_baseline_model(
            user_id=user_id,
            category_id=category_id,
            reference_version_id=reference_version_id,
            ruleset_id=ruleset_id,
            house_system_effective=house_system_effective,
            window_days=window_days,
            window_start_date=window_start_date,
            window_end_date=window_end_date,
        )

        if model is None:
            try:
                with self.db.begin_nested():
                    model = UserPredictionBaselineModel(
                        user_id=user_id,
                        category_id=category_id,
                        reference_version_id=reference_version_id,
                        ruleset_id=ruleset_id,
                        house_system_effective=house_system_effective,
                        window_days=window_days,
                        window_start_date=window_start_date,
                        window_end_date=window_end_date,
                    )
                    self.db.add(model)
                    self._apply_stats(model, stats)
                    self.db.flush()
            except IntegrityError:
                model = self._get_baseline_model(
                    user_id=user_id,
                    category_id=category_id,
                    reference_version_id=reference_version_id,
                    ruleset_id=ruleset_id,
                    house_system_effective=house_system_effective,
                    window_days=window_days,
                    window_start_date=window_start_date,
                    window_end_date=window_end_date,
                )
                if model is None:
                    raise
                self._apply_stats(model, stats)
                self.db.flush()
        else:
            self._apply_stats(model, stats)
            self.db.flush()

        # Ensure category is loaded for _to_persisted
        if not model.category:
            self.db.expire(model, ["category"])
            # Re-fetch to populate category
            model = self.db.scalar(
                select(UserPredictionBaselineModel)
                .options(selectinload(UserPredictionBaselineModel.category))
                .where(UserPredictionBaselineModel.id == model.id)
            )

        return self._to_persisted(model)

    def get_users_needing_baseline(
        self,
        reference_version_id: int,
        ruleset_id: int,
        house_system_effective: str,
        window_days: int = 365,
    ) -> list[int]:
        """
        Finds user IDs who either:
        1. Have a birth profile but no baseline for the given versions/window.
        2. Have a baseline that is older than their birth profile update.
        """
        from sqlalchemy import and_

        from app.infra.db.models.chart_result import ChartResultModel
        from app.infra.db.models.user_birth_profile import UserBirthProfileModel

        latest_chart_subquery = (
            select(
                ChartResultModel.user_id.label("user_id"),
                func.max(ChartResultModel.created_at).label("latest_chart_created_at"),
            )
            .where(ChartResultModel.user_id.is_not(None))
            .group_by(ChartResultModel.user_id)
            .subquery()
        )

        baseline_filters = and_(
            UserPredictionBaselineModel.user_id == UserBirthProfileModel.user_id,
            UserPredictionBaselineModel.reference_version_id == reference_version_id,
            UserPredictionBaselineModel.ruleset_id == ruleset_id,
            UserPredictionBaselineModel.house_system_effective == house_system_effective,
            UserPredictionBaselineModel.window_days == window_days,
        )

        chart_is_current = (
            latest_chart_subquery.c.latest_chart_created_at >= UserBirthProfileModel.updated_at
        )

        # Users with a current natal chart but no baseline for these versions and house system.
        stmt_missing = (
            select(UserBirthProfileModel.user_id)
            .join(
                latest_chart_subquery,
                latest_chart_subquery.c.user_id == UserBirthProfileModel.user_id,
            )
            .outerjoin(
                UserPredictionBaselineModel,
                baseline_filters,
            )
            .where(UserPredictionBaselineModel.id.is_(None), chart_is_current)
        )
        users_missing = self.db.scalars(stmt_missing).all()

        # Users with a current natal chart and a stale baseline.
        stmt_obsolete = (
            select(UserBirthProfileModel.user_id)
            .join(
                latest_chart_subquery,
                latest_chart_subquery.c.user_id == UserBirthProfileModel.user_id,
            )
            .join(
                UserPredictionBaselineModel,
                baseline_filters,
            )
            .where(
                UserBirthProfileModel.updated_at > UserPredictionBaselineModel.computed_at,
                chart_is_current,
            )
            .distinct()
        )
        users_obsolete = self.db.scalars(stmt_obsolete).all()

        return list(set(users_missing) | set(users_obsolete))

    def _apply_stats(
        self,
        model: UserPredictionBaselineModel,
        stats: dict[str, float | int],
    ) -> None:
        model.mean_raw_score = float(stats["mean_raw_score"])
        model.std_raw_score = float(stats["std_raw_score"])
        model.mean_note_20 = float(stats["mean_note_20"])
        model.std_note_20 = float(stats["std_note_20"])
        model.p10 = float(stats["p10"])
        model.p50 = float(stats["p50"])
        model.p90 = float(stats["p90"])
        model.sample_size_days = int(stats["sample_size_days"])
        model.computed_at = datetime.now(UTC)

    def _get_baseline_model(
        self,
        *,
        user_id: int,
        category_id: int,
        reference_version_id: int,
        ruleset_id: int,
        house_system_effective: str,
        window_days: int,
        window_start_date: date,
        window_end_date: date,
    ) -> UserPredictionBaselineModel | None:
        return self.db.scalar(
            select(UserPredictionBaselineModel).where(
                UserPredictionBaselineModel.user_id == user_id,
                UserPredictionBaselineModel.category_id == category_id,
                UserPredictionBaselineModel.reference_version_id == reference_version_id,
                UserPredictionBaselineModel.ruleset_id == ruleset_id,
                UserPredictionBaselineModel.house_system_effective == house_system_effective,
                UserPredictionBaselineModel.window_days == window_days,
                UserPredictionBaselineModel.window_start_date == window_start_date,
                UserPredictionBaselineModel.window_end_date == window_end_date,
            )
        )

    def _to_persisted(self, model: UserPredictionBaselineModel) -> PersistedUserBaseline:
        return PersistedUserBaseline(
            id=model.id,
            user_id=model.user_id,
            category_id=model.category_id,
            category_code=model.category.code if model.category else "unknown",
            reference_version_id=model.reference_version_id,
            ruleset_id=model.ruleset_id,
            house_system_effective=model.house_system_effective,
            window_days=model.window_days,
            window_start_date=model.window_start_date,
            window_end_date=model.window_end_date,
            mean_raw_score=model.mean_raw_score,
            std_raw_score=model.std_raw_score,
            mean_note_20=model.mean_note_20,
            std_note_20=model.std_note_20,
            p10=model.p10,
            p50=model.p50,
            p90=model.p90,
            sample_size_days=model.sample_size_days,
            computed_at=model.computed_at,
        )

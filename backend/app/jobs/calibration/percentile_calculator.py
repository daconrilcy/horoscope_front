# backend/app/jobs/calibration/percentile_calculator.py
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.infra.db.models.prediction_reference import PredictionCategoryModel
from app.infra.db.models.prediction_ruleset import CategoryCalibrationModel, PredictionRulesetModel
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.repositories.calibration_repository import CalibrationRepository

logger = logging.getLogger(__name__)


@dataclass
class PercentileResult:
    category_code: str
    p05: float
    p25: float
    p50: float
    p75: float
    p95: float
    sample_size: int
    mean: float
    min: float
    max: float
    outlier_count: int
    outliers: list[float] = field(default_factory=list)


def compute_percentile(data: list[float], p: float) -> float:
    """Calcule le p-ième percentile par interpolation linéaire (méthode type 7)."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n == 0:
        raise ValueError("Cannot compute percentile of empty dataset")
    if n == 1:
        return sorted_data[0]
    idx = (p / 100) * (n - 1)
    lo = int(idx)
    hi = min(lo + 1, n - 1)
    return sorted_data[lo] + (idx - lo) * (sorted_data[hi] - sorted_data[lo])


def compute_percentiles(category_code: str, raw_scores: list[float]) -> PercentileResult:
    if not raw_scores:
        raise ValueError(
            f"Dataset vide pour {category_code} — impossible de calculer les percentiles"
        )

    p05 = compute_percentile(raw_scores, 5)
    p25 = compute_percentile(raw_scores, 25)
    p50 = compute_percentile(raw_scores, 50)
    p75 = compute_percentile(raw_scores, 75)
    p95 = compute_percentile(raw_scores, 95)

    # Vérification monotonie
    if not (p05 <= p25 <= p50 <= p75 <= p95):
        raise ValueError(
            f"Percentiles non monotones pour {category_code}: {p05} {p25} {p50} {p75} {p95}"
        )

    mean = sum(raw_scores) / len(raw_scores)
    variance = sum((x - mean) ** 2 for x in raw_scores) / len(raw_scores)
    stddev = variance**0.5
    outliers = [x for x in raw_scores if abs(x - mean) > 3 * stddev]

    return PercentileResult(
        category_code=category_code,
        p05=p05,
        p25=p25,
        p50=p50,
        p75=p75,
        p95=p95,
        sample_size=len(raw_scores),
        mean=mean,
        min=min(raw_scores),
        max=max(raw_scores),
        outlier_count=len(outliers),
        outliers=outliers,
    )


class PercentileCalculatorService:
    def __init__(self, db: Session, calibration_repo: CalibrationRepository) -> None:
        self.db = db
        self.calibration_repo = calibration_repo

    def run(
        self,
        reference_version: str,
        ruleset_version: str,
        valid_from: date,
        valid_to: date,
    ) -> list[PercentileResult]:
        # 1. Resolve ruleset_id and reference_version_id
        ruleset = self.db.scalar(
            select(PredictionRulesetModel).where(PredictionRulesetModel.version == ruleset_version)
        )
        if not ruleset:
            raise ValueError(f"Ruleset non trouvé: {ruleset_version}")

        reference_version_model = self.db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == reference_version)
        )
        if reference_version_model is None:
            raise ValueError(f"Version de référence introuvable: {reference_version}")
        if ruleset.reference_version_id != reference_version_model.id:
            raise ValueError(
                f"Le ruleset {ruleset_version} attend la référence "
                f"{reference_version_model.version} (id={reference_version_model.id}), "
                f"mais pointe vers l'id "
                f"{ruleset.reference_version_id}."
            )

        # 2. Get all raw scores by category
        scores_by_cat = self.calibration_repo.get_raw_scores_by_category(
            reference_version, ruleset_version
        )
        if not scores_by_cat:
            logger.warning(f"Aucun score trouvé pour {reference_version}/{ruleset_version}")
            return []

        # 3. Resolve category IDs for the given reference_version_id
        categories = self.db.scalars(
            select(PredictionCategoryModel).where(
                PredictionCategoryModel.reference_version_id == ruleset.reference_version_id
            )
        ).all()
        cat_map = {cat.code: cat.id for cat in categories}

        results = []
        try:
            for cat_code, scores in scores_by_cat.items():
                if cat_code not in cat_map:
                    logger.warning(
                        f"Catégorie {cat_code} ignorée "
                        f"(absente de la référence {reference_version})"
                    )
                    continue

                cat_id = cat_map[cat_code]
                result = compute_percentiles(cat_code, scores)
                results.append(result)

                # 4. Upsert calibration
                self._upsert_calibration(ruleset.id, cat_id, result, valid_from, valid_to)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return results

    def _upsert_calibration(
        self,
        ruleset_id: int,
        category_id: int,
        result: PercentileResult,
        valid_from: date,
        valid_to: date,
    ) -> None:
        # Delete existing entries for this (ruleset, category, valid_from)
        self.db.execute(
            delete(CategoryCalibrationModel).where(
                CategoryCalibrationModel.ruleset_id == ruleset_id,
                CategoryCalibrationModel.category_id == category_id,
                CategoryCalibrationModel.valid_from == valid_from,
            )
        )

        calibration = CategoryCalibrationModel(
            ruleset_id=ruleset_id,
            category_id=category_id,
            p05=result.p05,
            p25=result.p25,
            p50=result.p50,
            p75=result.p75,
            p95=result.p95,
            calibration_label="provisional",
            sample_size=result.sample_size,
            valid_from=valid_from,
            valid_to=valid_to,
        )
        self.db.add(calibration)
        self.db.flush()

    def generate_report(
        self, results: list[PercentileResult], output_path: Path, metadata: dict
    ) -> None:
        report = {
            "generated_at": datetime.now().isoformat(),
            **metadata,
            "categories": {
                res.category_code: {
                    "sample_size": res.sample_size,
                    "min": res.min,
                    "max": res.max,
                    "mean": res.mean,
                    "p05": res.p05,
                    "p25": res.p25,
                    "p50": res.p50,
                    "p75": res.p75,
                    "p95": res.p95,
                    "outlier_count": res.outlier_count,
                    "outliers": res.outliers,
                }
                for res in results
            },
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"Rapport généré: {output_path}")

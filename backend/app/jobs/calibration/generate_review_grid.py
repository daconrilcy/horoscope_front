import argparse
import csv
import io
import json
import logging
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from sqlalchemy import and_, literal, select

from app.infra.db.models.calibration import CalibrationRawDayModel
from app.infra.db.models.daily_prediction import (
    DailyPredictionCategoryScoreModel,
    DailyPredictionRunModel,
)
from app.infra.db.models.prediction_reference import PredictionCategoryModel
from app.infra.db.session import SessionLocal

logger = logging.getLogger(__name__)

DOCS_DIR = Path("docs/calibration")
REVIEW_HEADERS = (
    ("date", "Date"),
    ("category", "Categorie"),
    ("raw_day", "Raw Day"),
    ("note_20", "Note/20"),
    ("band", "Bande UX"),
    ("power", "Power"),
    ("volatility", "Volatilite"),
    ("top_contributors", "Top Contributeurs"),
    ("commentaire", "Commentaire"),
)


def note_to_band(note: int | None) -> str:
    if note is None:
        return "N/A"
    if note <= 5:
        return "fragile"
    if note <= 9:
        return "tendu"
    if note <= 12:
        return "neutre"
    if note <= 16:
        return "porteur"
    return "tres favorable"


def _format_optional_number(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _escape_markdown_cell(value: object) -> str:
    text = str(value)
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _to_markdown(rows: Sequence[dict[str, object]]) -> str:
    if not rows:
        return "Aucune donnee trouvee."

    headers = [label for _, label in REVIEW_HEADERS]
    keys = [key for key, _ in REVIEW_HEADERS]
    md = "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    for row in rows:
        line = [_escape_markdown_cell(row.get(key, "")) for key in keys]
        md += "| " + " | ".join(line) + " |\n"

    return md


def _to_csv(rows: Sequence[dict[str, object]]) -> str:
    if not rows:
        return ""

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[key for key, _ in REVIEW_HEADERS])
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def _load_contributors(raw_value: str | None) -> list[object]:
    if not raw_value:
        return []

    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError:
        logger.warning("contributors_json malformed; empty contributors list used")
        return []

    if isinstance(parsed, list):
        return parsed

    logger.warning("contributors_json must contain a JSON list; empty contributors list used")
    return []


def _extract_top_contributors(raw_value: str | None) -> str:
    top_list: list[str] = []
    for contributor in _load_contributors(raw_value)[:3]:
        if isinstance(contributor, dict):
            top_list.append(
                str(
                    contributor.get("rule_id")
                    or contributor.get("event_type_code")
                    or contributor.get("source")
                    or "unknown"
                )
            )
        else:
            top_list.append(str(contributor))
    return ", ".join(top_list)


def _resolve_project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _default_output_path(output_format: str, end_date: date) -> Path:
    output_dir = _resolve_project_root() / DOCS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    extension = "md" if output_format == "md" else "csv"
    return output_dir / f"review-grid-{end_date.isoformat()}.{extension}"


def _build_query(
    *,
    start: date,
    end: date,
    user_id: int | None,
    profile_label: str | None,
):
    calibration_raw_day = literal(None)
    calibration_power = literal(None)
    calibration_volatility = literal(None)

    query = (
        select(
            DailyPredictionRunModel.local_date.label("local_date"),
            PredictionCategoryModel.code.label("category_code"),
            DailyPredictionCategoryScoreModel.raw_score.label("score_raw_day"),
            DailyPredictionCategoryScoreModel.note_20.label("note_20"),
            DailyPredictionCategoryScoreModel.power.label("score_power"),
            DailyPredictionCategoryScoreModel.volatility.label("score_volatility"),
            DailyPredictionCategoryScoreModel.contributors_json.label("contributors_json"),
            calibration_raw_day.label("calibration_raw_day"),
            calibration_power.label("calibration_power"),
            calibration_volatility.label("calibration_volatility"),
        )
        .select_from(DailyPredictionCategoryScoreModel)
        .join(
            DailyPredictionRunModel,
            DailyPredictionCategoryScoreModel.run_id == DailyPredictionRunModel.id,
        )
        .join(
            PredictionCategoryModel,
            DailyPredictionCategoryScoreModel.category_id == PredictionCategoryModel.id,
        )
        .where(
            DailyPredictionRunModel.local_date >= start,
            DailyPredictionRunModel.local_date <= end,
        )
    )

    if user_id is not None:
        query = query.where(DailyPredictionRunModel.user_id == user_id)

    if profile_label:
        query = query.add_columns()
        query = query.outerjoin(
            CalibrationRawDayModel,
            and_(
                CalibrationRawDayModel.local_date == DailyPredictionRunModel.local_date,
                CalibrationRawDayModel.category_code == PredictionCategoryModel.code,
                CalibrationRawDayModel.profile_label == profile_label,
            ),
        ).with_only_columns(
            DailyPredictionRunModel.local_date.label("local_date"),
            PredictionCategoryModel.code.label("category_code"),
            DailyPredictionCategoryScoreModel.raw_score.label("score_raw_day"),
            DailyPredictionCategoryScoreModel.note_20.label("note_20"),
            DailyPredictionCategoryScoreModel.power.label("score_power"),
            DailyPredictionCategoryScoreModel.volatility.label("score_volatility"),
            DailyPredictionCategoryScoreModel.contributors_json.label("contributors_json"),
            CalibrationRawDayModel.raw_score.label("calibration_raw_day"),
            CalibrationRawDayModel.power.label("calibration_power"),
            CalibrationRawDayModel.volatility.label("calibration_volatility"),
        )

    return query.order_by(DailyPredictionRunModel.local_date, PredictionCategoryModel.sort_order)


def generate_grid(
    start: date,
    end: date,
    user_id: int | None = None,
    profile_label: str | None = None,
    fmt: str = "md",
) -> str:
    rows: list[dict[str, object]] = []
    db = SessionLocal()

    try:
        query = _build_query(start=start, end=end, user_id=user_id, profile_label=profile_label)
        result = db.execute(query).all()

        for record in result:
            data = record._mapping
            raw_day = data["score_raw_day"]
            if raw_day is None:
                raw_day = data["calibration_raw_day"]

            power = data["score_power"]
            if power is None:
                power = data["calibration_power"]

            volatility = data["score_volatility"]
            if volatility is None:
                volatility = data["calibration_volatility"]

            rows.append(
                {
                    "date": data["local_date"].isoformat(),
                    "category": data["category_code"],
                    "raw_day": _format_optional_number(raw_day),
                    "note_20": data["note_20"] if data["note_20"] is not None else "",
                    "band": note_to_band(data["note_20"]),
                    "power": _format_optional_number(power),
                    "volatility": _format_optional_number(volatility),
                    "top_contributors": _extract_top_contributors(data["contributors_json"]),
                    "commentaire": "",
                }
            )
    finally:
        db.close()

    if fmt == "csv":
        return _to_csv(rows)
    return _to_markdown(rows)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genere une grille de revue pour la calibration.")
    parser.add_argument("--start", required=True, help="Date de debut (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="Date de fin (YYYY-MM-DD)")
    parser.add_argument("--user-id", type=int, help="ID de l'utilisateur a filtrer")
    parser.add_argument(
        "--profile-label",
        help="Label de profil de calibration pour enrichir depuis calibration_raw_days",
    )
    parser.add_argument("--format", default="md", choices=["md", "csv"], help="Format de sortie")
    parser.add_argument("--output", help="Chemin du fichier de sortie (optionnel)")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)

    try:
        start_date = date.fromisoformat(args.start)
        end_date = date.fromisoformat(args.end)
    except ValueError as exc:
        logger.error("Format de date invalide: %s", exc)
        return 2

    if end_date < start_date:
        logger.error("La date de fin doit etre superieure ou egale a la date de debut.")
        return 2

    try:
        content = generate_grid(
            start_date,
            end_date,
            user_id=args.user_id,
            profile_label=args.profile_label,
            fmt=args.format,
        )
        out_path = Path(args.output) if args.output else _default_output_path(args.format, end_date)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        logger.info("Grille generee avec succes: %s", out_path)
        return 0
    except Exception:
        logger.exception("La generation de la grille a echoue.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

import argparse
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infra.db.models.user_natal_interpretation import UserNatalInterpretationModel
from app.infra.db.session import SessionLocal


def _format_dt(value: datetime | None) -> str:
    if value is None:
        return "-"
    return value.isoformat()


def _print_group_rows(
    db: Session,
    *,
    user_id: int,
    chart_id: str,
    level: str,
    persona_id: str | None,
) -> None:
    stmt = select(
        UserNatalInterpretationModel.id,
        UserNatalInterpretationModel.created_at,
        UserNatalInterpretationModel.use_case,
        UserNatalInterpretationModel.prompt_version_id,
    ).where(
        UserNatalInterpretationModel.user_id == user_id,
        UserNatalInterpretationModel.chart_id == chart_id,
        UserNatalInterpretationModel.level == level,
    )
    if persona_id is None:
        stmt = stmt.where(UserNatalInterpretationModel.persona_id.is_(None))
    else:
        stmt = stmt.where(UserNatalInterpretationModel.persona_id == persona_id)

    stmt = stmt.order_by(
        UserNatalInterpretationModel.created_at.desc(),
        UserNatalInterpretationModel.id.desc(),
    )

    rows = db.execute(stmt).all()
    for row in rows:
        print(
            "    - id={id} created_at={created_at} use_case={use_case} "
            "prompt_version_id={prompt_id}".format(
                id=row.id,
                created_at=_format_dt(row.created_at),
                use_case=row.use_case,
                prompt_id=row.prompt_version_id,
            )
        )


def _print_null_persona_duplicates(db: Session, *, max_groups: int, show_ids: bool) -> int:
    count_expr = func.count(UserNatalInterpretationModel.id)
    stmt = (
        select(
            UserNatalInterpretationModel.user_id,
            UserNatalInterpretationModel.chart_id,
            UserNatalInterpretationModel.level,
            count_expr.label("row_count"),
            func.min(UserNatalInterpretationModel.created_at).label("oldest_created_at"),
            func.max(UserNatalInterpretationModel.created_at).label("newest_created_at"),
        )
        .where(UserNatalInterpretationModel.persona_id.is_(None))
        .group_by(
            UserNatalInterpretationModel.user_id,
            UserNatalInterpretationModel.chart_id,
            UserNatalInterpretationModel.level,
        )
        .having(count_expr > 1)
        .order_by(count_expr.desc(), UserNatalInterpretationModel.user_id.asc())
        .limit(max_groups)
    )

    rows = db.execute(stmt).all()
    print("\n[NULL persona_id] duplicates on (user_id, chart_id, level)")
    if not rows:
        print("  none")
        return 0

    for row in rows:
        print(
            "  user_id={user_id} chart_id={chart_id} level={level} rows={rows} "
            "oldest={oldest} newest={newest}".format(
                user_id=row.user_id,
                chart_id=row.chart_id,
                level=row.level,
                rows=row.row_count,
                oldest=_format_dt(row.oldest_created_at),
                newest=_format_dt(row.newest_created_at),
            )
        )
        if show_ids:
            _print_group_rows(
                db,
                user_id=row.user_id,
                chart_id=row.chart_id,
                level=row.level,
                persona_id=None,
            )
    return len(rows)


def _print_non_null_persona_duplicates(db: Session, *, max_groups: int, show_ids: bool) -> int:
    count_expr = func.count(UserNatalInterpretationModel.id)
    stmt = (
        select(
            UserNatalInterpretationModel.user_id,
            UserNatalInterpretationModel.chart_id,
            UserNatalInterpretationModel.level,
            UserNatalInterpretationModel.persona_id,
            count_expr.label("row_count"),
            func.min(UserNatalInterpretationModel.created_at).label("oldest_created_at"),
            func.max(UserNatalInterpretationModel.created_at).label("newest_created_at"),
        )
        .where(UserNatalInterpretationModel.persona_id.is_not(None))
        .group_by(
            UserNatalInterpretationModel.user_id,
            UserNatalInterpretationModel.chart_id,
            UserNatalInterpretationModel.level,
            UserNatalInterpretationModel.persona_id,
        )
        .having(count_expr > 1)
        .order_by(count_expr.desc(), UserNatalInterpretationModel.user_id.asc())
        .limit(max_groups)
    )

    rows = db.execute(stmt).all()
    print("\n[NON-NULL persona_id] duplicates on (user_id, chart_id, level, persona_id)")
    if not rows:
        print("  none")
        return 0

    for row in rows:
        persona_id_str = str(row.persona_id) if row.persona_id is not None else "-"
        print(
            "  user_id={user_id} chart_id={chart_id} level={level} "
            "persona_id={persona_id} rows={rows} oldest={oldest} newest={newest}".format(
                user_id=row.user_id,
                chart_id=row.chart_id,
                level=row.level,
                persona_id=persona_id_str,
                rows=row.row_count,
                oldest=_format_dt(row.oldest_created_at),
                newest=_format_dt(row.newest_created_at),
            )
        )
        if show_ids:
            _print_group_rows(
                db,
                user_id=row.user_id,
                chart_id=row.chart_id,
                level=row.level,
                persona_id=persona_id_str,
            )
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "List potential duplicate rows in user_natal_interpretations "
            "before applying uniqueness migration."
        )
    )
    parser.add_argument(
        "--max-groups",
        type=int,
        default=100,
        help="Maximum number of duplicate groups printed per category (default: 100).",
    )
    parser.add_argument(
        "--show-ids",
        action="store_true",
        help="Show individual duplicate rows (ids/use_case/prompt_version_id) for each group.",
    )
    parser.add_argument(
        "--fail-on-duplicates",
        action="store_true",
        help="Exit with code 1 if any duplicate group is detected.",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        print("Diagnostics for table: user_natal_interpretations")
        print(f"max_groups={args.max_groups} show_ids={args.show_ids}")

        null_group_count = _print_null_persona_duplicates(
            db, max_groups=args.max_groups, show_ids=args.show_ids
        )
        non_null_group_count = _print_non_null_persona_duplicates(
            db, max_groups=args.max_groups, show_ids=args.show_ids
        )
        total_groups = null_group_count + non_null_group_count
        print(
            "\nSummary: duplicate_groups={total} "
            "null_persona_groups={null_groups} "
            "non_null_persona_groups={non_null_groups}".format(
                total=total_groups,
                null_groups=null_group_count,
                non_null_groups=non_null_group_count,
            )
        )

        if args.fail_on_duplicates and total_groups > 0:
            raise SystemExit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

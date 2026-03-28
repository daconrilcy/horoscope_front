from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from scripts import archive_b2b_legacy_usage_counters as archive_script
from scripts import verify_b2b_usage_migration as verify_script


def _row(**kwargs: object) -> object:
    return type("Row", (), kwargs)()


def _db_with_execute_results(*results: list[object]) -> MagicMock:
    db = MagicMock()
    db.execute.side_effect = [MagicMock(all=MagicMock(return_value=result)) for result in results]
    return db


def test_verify_detects_compensated_aggregate_mismatch(capsys: pytest.CaptureFixture[str]) -> None:
    window_start = datetime(2026, 3, 1, tzinfo=timezone.utc)
    db = _db_with_execute_results(
        [(10,)],  # distinct old user ids
        [(10,)],  # mapped user ids
        [  # account mapping
            _row(id=1, admin_user_id=10),
        ],
        [  # old aggregates
            _row(
                user_id=10,
                feature_code="b2b_api_access",
                quota_key="calls",
                window_start=window_start,
                used_count=5,
            )
        ],
        [  # new aggregates with same total but wrong key split
            _row(
                enterprise_account_id=1,
                feature_code="b2b_api_access",
                quota_key="calls",
                window_start=window_start,
                used_count=3,
            ),
            _row(
                enterprise_account_id=1,
                feature_code="b2b_api_access",
                quota_key="bonus",
                window_start=window_start,
                used_count=2,
            ),
        ],
    )
    db.scalar.side_effect = [
        1,  # old_row_count
        5,  # old_used_sum
        2,  # new_row_count
        5,  # new_used_sum
        1,  # count accounts for user 10
    ]

    ok = verify_script.run_verification(db, verbose=True)

    assert ok is False
    output = capsys.readouterr().out
    assert "aggregate_mismatch_count: 2" in output
    assert "account_id=1 quota_key=calls" in output
    assert "account_id=1 quota_key=bonus" in output
    assert "MISMATCH" in output


def test_archive_aborts_with_explicit_message(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    db = MagicMock()
    session = MagicMock()
    session.__enter__.return_value = db
    session.__exit__.return_value = None

    monkeypatch.setattr(archive_script, "SessionLocal", MagicMock(return_value=session))
    monkeypatch.setattr(archive_script, "run_verification", MagicMock(return_value=False))

    with pytest.raises(SystemExit) as excinfo:
        archive_script.main(dry_run=False, force=False)

    assert excinfo.value.code == 1
    output = capsys.readouterr().out
    assert (
        "❌ ABORT — vérification migration incomplète. "
        "Relancer verify_b2b_usage_migration.py ou utiliser --force si intentionnel."
    ) in output

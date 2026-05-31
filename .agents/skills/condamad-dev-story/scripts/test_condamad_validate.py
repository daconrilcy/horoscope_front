#!/usr/bin/env python3
"""Tests cibles pour le validateur de capsule CONDAMAD."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import condamad_validate


class FinalConsistencyTests(unittest.TestCase):
    def test_story_status_row_matches_capsule_path_or_id(self) -> None:
        registry = (
            "| ID | Slug | Title | Status | Path |\n"
            "|---|---|---|---|---|\n"
            "| CS-123 | audit-runtime | Audit runtime | ready-to-review | "
            "`_condamad/stories/CS-123-audit-runtime/00-story.md` |\n"
        )

        rows = condamad_validate.story_status_rows(registry, "CS-123-audit-runtime")

        self.assertEqual(len(rows), 1)
        self.assertIn("ready-to-review", rows[0])

    def test_blocked_title_does_not_fail_ready_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            stories = root / "_condamad" / "stories"
            capsule = stories / "CS-123-audit-runtime"
            generated = capsule / "generated"
            generated.mkdir(parents=True)
            (stories / "story-status.md").write_text(
                "| ID | Slug | Title | Status | Path |\n"
                "|---|---|---|---|---|\n"
                "| CS-123 | audit-runtime | Handle blocked states | "
                "ready-to-review | "
                "`_condamad/stories/CS-123-audit-runtime/00-story.md` |\n",
                encoding="utf-8",
            )
            (generated / "10-final-evidence.md").write_text(
                "# Final Evidence\n\n"
                "## Story status\n\n"
                "- Validation outcome: PASS\n"
                "- Ready for review: yes\n",
                encoding="utf-8",
            )

            errors = condamad_validate.validate_final_consistency(capsule)

        self.assertEqual(errors, [])

    def test_ready_to_dev_history_outside_story_status_does_not_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            stories = root / "_condamad" / "stories"
            capsule = stories / "CS-123-audit-runtime"
            generated = capsule / "generated"
            generated.mkdir(parents=True)
            (stories / "story-status.md").write_text(
                "| ID | Slug | Title | Status | Path |\n"
                "|---|---|---|---|---|\n"
                "| CS-123 | audit-runtime | Audit runtime | ready-to-review | "
                "`_condamad/stories/CS-123-audit-runtime/00-story.md` |\n",
                encoding="utf-8",
            )
            (generated / "10-final-evidence.md").write_text(
                "# Final Evidence\n\n"
                "## Story status\n\n"
                "- Validation outcome: PASS\n"
                "- Ready for review: yes\n\n"
                "## Diff review\n\n"
                "Updated story-status.md from ready-to-dev to ready-to-review.\n",
                encoding="utf-8",
            )

            errors = condamad_validate.validate_final_consistency(capsule)

        self.assertEqual(errors, [])

    def test_ready_to_dev_in_story_status_block_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            stories = root / "_condamad" / "stories"
            capsule = stories / "CS-123-audit-runtime"
            generated = capsule / "generated"
            generated.mkdir(parents=True)
            (stories / "story-status.md").write_text(
                "| ID | Slug | Title | Status | Path |\n"
                "|---|---|---|---|---|\n"
                "| CS-123 | audit-runtime | Audit runtime | ready-to-review | "
                "`_condamad/stories/CS-123-audit-runtime/00-story.md` |\n",
                encoding="utf-8",
            )
            (generated / "10-final-evidence.md").write_text(
                "# Final Evidence\n\n"
                "## Story status\n\n"
                "- Status: ready-to-dev\n\n"
                "## Diff review\n\n"
                "No notes.\n",
                encoding="utf-8",
            )

            errors = condamad_validate.validate_final_consistency(capsule)

        self.assertTrue(
            any("ready-to-dev" in error for error in errors),
            f"Expected ready-to-dev error, got: {errors}",
        )

    def test_ready_to_dev_story_file_status_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            stories = root / "_condamad" / "stories"
            capsule = stories / "CS-123-audit-runtime"
            generated = capsule / "generated"
            generated.mkdir(parents=True)
            (capsule / "00-story.md").write_text(
                "# CS-123\nStatus: ready-to-dev\n",
                encoding="utf-8",
            )
            (stories / "story-status.md").write_text(
                "| ID | Slug | Title | Status | Path |\n"
                "|---|---|---|---|---|\n"
                "| CS-123 | audit-runtime | Audit runtime | ready-to-review | "
                "`_condamad/stories/CS-123-audit-runtime/00-story.md` |\n",
                encoding="utf-8",
            )
            (generated / "10-final-evidence.md").write_text(
                "# Final Evidence\n\n"
                "## Story status\n\n"
                "- Validation outcome: PASS\n"
                "- Ready for review: yes\n",
                encoding="utf-8",
            )

            errors = condamad_validate.validate_final_consistency(capsule)

        self.assertTrue(
            any("00-story.md Status" in error for error in errors),
            f"Expected story status error, got: {errors}",
        )


if __name__ == "__main__":
    unittest.main()

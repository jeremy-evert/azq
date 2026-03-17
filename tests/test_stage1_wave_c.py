import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from azq import cli
from azq.finis import goal_manager, storage


@contextlib.contextmanager
def working_directory(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


class FixedDate:
    @staticmethod
    def today():
        return "2026-03-17"


class Stage1WaveCRegressionTests(unittest.TestCase):
    def test_parse_legacy_goals_json_normalizes_json_records(self):
        raw_text = json.dumps(
            [
                {
                    "goal_id": "FINIS_004",
                    "goal": "Preserve legacy wording",
                    "status": "active",
                    "derived_from": "spark-123",
                }
            ]
        )

        normalized = storage.parse_legacy_goals_json(raw_text)

        self.assertEqual(
            normalized,
            [
                {
                    "goal_id": "FINIS_004",
                    "title": "Preserve legacy wording",
                    "status": "active",
                    "created": "",
                    "description": "",
                    "derived_from": ["spark-123"],
                }
            ],
        )

    def test_goal_markdown_round_trip_preserves_canonical_fields(self):
        record = {
            "goal_id": "FINIS_007",
            "title": "Stabilize Stage 1",
            "status": "active",
            "created": "2026-03-17",
            "description": "First line.\nSecond line.",
            "derived_from": ["spark-a", "spark-b"],
        }

        markdown = storage.serialize_goal_markdown(record)
        parsed = storage.parse_goal_markdown(markdown)

        self.assertEqual(parsed, record)

    def test_next_goal_id_uses_highest_existing_canonical_goal_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                storage.write_goal(
                    {
                        "goal_id": "FINIS_002",
                        "title": "Second",
                        "status": "active",
                        "created": "2026-03-17",
                        "description": "",
                        "derived_from": [],
                    }
                )
                storage.write_goal(
                    {
                        "goal_id": "FINIS_010",
                        "title": "Tenth",
                        "status": "active",
                        "created": "2026-03-17",
                        "description": "",
                        "derived_from": [],
                    }
                )

                self.assertEqual(storage.next_goal_id(), "FINIS_011")

    def test_migrate_legacy_goals_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                storage.FINIS_DIR.mkdir(parents=True, exist_ok=True)
                storage.LEGACY_GOALS_FILE.write_text(
                    json.dumps(
                        [
                            {
                                "goal_id": "FINIS_001",
                                "goal": "First migrated goal",
                                "status": "active",
                                "created": "2026-03-01",
                            },
                            {
                                "goal_id": "FINIS_002",
                                "goal": "Second migrated goal",
                                "status": "completed",
                                "created": "2026-03-02",
                                "derived_from": ["spark-2"],
                            },
                        ]
                    ),
                    encoding="utf-8",
                )

                first = storage.migrate_legacy_goals()
                second = storage.migrate_legacy_goals()

                self.assertEqual(first["migrated"], 2)
                self.assertEqual(first["skipped"], 0)
                self.assertEqual(second["migrated"], 0)
                self.assertEqual(second["skipped"], 2)
                self.assertEqual(
                    [path.name for path in storage.list_goal_files()],
                    ["FINIS_001.md", "FINIS_002.md"],
                )

    def test_goal_add_writes_canonical_goal_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                output = io.StringIO()

                with mock.patch("azq.finis.goal_manager.date", FixedDate), mock.patch(
                    "builtins.input",
                    side_effect=["Write the Wave C tests", "Cover the canonical flow"],
                ), mock.patch("sys.argv", ["azq", "goal", "add"]), contextlib.redirect_stdout(
                    output
                ):
                    cli.main()

                record = storage.load_goal("FINIS_001")
                self.assertIsNotNone(record)
                self.assertEqual(
                    record,
                    {
                        "goal_id": "FINIS_001",
                        "title": "Write the Wave C tests",
                        "status": "active",
                        "created": "2026-03-17",
                        "description": "Cover the canonical flow",
                        "derived_from": [],
                    },
                )
                self.assertIn("Goal created", output.getvalue())
                self.assertFalse(storage.LEGACY_GOALS_FILE.exists())

    def test_goal_close_updates_status_in_place(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                storage.write_goal(
                    {
                        "goal_id": "FINIS_001",
                        "title": "Close me",
                        "status": "active",
                        "created": "2026-03-17",
                        "description": "Baseline record",
                        "derived_from": ["spark-1"],
                    }
                )

                with mock.patch("sys.argv", ["azq", "goal", "close", "FINIS_001"]):
                    cli.main()

                self.assertEqual(
                    storage.load_goal("FINIS_001"),
                    {
                        "goal_id": "FINIS_001",
                        "title": "Close me",
                        "status": "completed",
                        "created": "2026-03-17",
                        "description": "Baseline record",
                        "derived_from": ["spark-1"],
                    },
                )

    def test_goal_archive_updates_status_in_place(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                storage.write_goal(
                    {
                        "goal_id": "FINIS_001",
                        "title": "Archive me",
                        "status": "active",
                        "created": "2026-03-17",
                        "description": "Baseline record",
                        "derived_from": ["spark-2"],
                    }
                )

                with mock.patch("sys.argv", ["azq", "goal", "archive", "FINIS_001"]):
                    cli.main()

                self.assertEqual(
                    storage.load_goal("FINIS_001"),
                    {
                        "goal_id": "FINIS_001",
                        "title": "Archive me",
                        "status": "archived",
                        "created": "2026-03-17",
                        "description": "Baseline record",
                        "derived_from": ["spark-2"],
                    },
                )

    def test_write_goal_preserves_derived_from_as_canonical_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                storage.write_goal(
                    {
                        "goal_id": "FINIS_005",
                        "title": "Track source lineage",
                        "status": "active",
                        "created": "2026-03-17",
                        "description": "",
                        "derived_from": "spark-5",
                    }
                )

                self.assertEqual(
                    storage.load_goal("FINIS_005")["derived_from"], ["spark-5"]
                )

    def test_fine_writes_canonical_goal_with_derived_from_backlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                spark_dir = Path("data/scintilla/sparks")
                spark_dir.mkdir(parents=True, exist_ok=True)
                spark_dir.joinpath("2026-03-17_0900.json").write_text(
                    json.dumps(
                        [
                            {
                                "spark": "I want to lock the Stage 1 baseline with regression tests"
                            }
                        ]
                    ),
                    encoding="utf-8",
                )
                output = io.StringIO()

                with mock.patch("azq.finis.fine.date", FixedDate), mock.patch(
                    "builtins.input", side_effect=["y"]
                ), mock.patch("sys.argv", ["azq", "fine"]), contextlib.redirect_stdout(
                    output
                ):
                    cli.main()

                self.assertEqual(
                    storage.load_goal("FINIS_001"),
                    {
                        "goal_id": "FINIS_001",
                        "title": "Lock the Stage 1 baseline with regression tests",
                        "status": "active",
                        "created": "2026-03-17",
                        "description": "",
                        "derived_from": ["2026-03-17_0900"],
                    },
                )
                self.assertIn("Goals written to data/finis/goals/", output.getvalue())
                self.assertFalse(storage.LEGACY_GOALS_FILE.exists())


if __name__ == "__main__":
    unittest.main()

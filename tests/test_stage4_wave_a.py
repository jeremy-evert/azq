import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import azq.cli as cli
from azq.finis import storage


@contextlib.contextmanager
def working_directory(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


class FixedDate:
    @classmethod
    def today(cls):
        class _D:
            def __str__(self):
                return "2026-03-20"

        return _D()


class Stage4WaveARegressionTests(unittest.TestCase):
    def test_fine_allows_live_false_positive_candidates_to_reach_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                spark_dir = Path("data/scintilla/sparks")
                spark_dir.mkdir(parents=True, exist_ok=True)
                spark_dir.joinpath("2026-03-20_121334.json").write_text(
                    json.dumps(
                        [
                            {
                                "spark": "we need to fix azq to make the alignment match better"
                            },
                            {
                                "spark": "the docs do not all agree, and we need a usable spark ingress path"
                            },
                        ]
                    ),
                    encoding="utf-8",
                )
                storage.write_goal(
                    {
                        "goal_id": "FINIS_010",
                        "title": "Stabilize the Scintilla and Finis engines of AZQ",
                        "status": "active",
                        "created": "2026-03-09",
                        "description": "",
                        "derived_from": [],
                    }
                )
                storage.write_goal(
                    {
                        "goal_id": "FINIS_020",
                        "title": "They recommended a 15 line guard rail that prevents corrupted goals",
                        "status": "active",
                        "created": "2026-03-09",
                        "description": "",
                        "derived_from": ["2026-03-09_090431"],
                    }
                )
                storage.write_goal(
                    {
                        "goal_id": "FINIS_022",
                        "title": "It's small, but it makes the system dramatically more durable",
                        "status": "active",
                        "created": "2026-03-09",
                        "description": "",
                        "derived_from": ["2026-03-09_090431"],
                    }
                )
                storage.write_goal(
                    {
                        "goal_id": "FINIS_025",
                        "title": "add azq goals --all to show all active, completed, and archived goals.",
                        "status": "active",
                        "created": "2026-03-09",
                        "description": "",
                        "derived_from": [],
                    }
                )
                output = io.StringIO()

                with mock.patch("builtins.input", side_effect=["n", "n"]), mock.patch(
                    "sys.argv", ["azq", "fine"]
                ), contextlib.redirect_stdout(output):
                    cli.main()

                self.assertEqual(
                    [path.name for path in storage.list_review_files()],
                    [
                        "REVIEW_2026-03-20_121334_001.json",
                        "REVIEW_2026-03-20_121334_002.json",
                    ],
                )
                self.assertEqual(
                    storage.load_review("REVIEW_2026-03-20_121334_001")["candidate_goal_text"],
                    "We need to fix azq to make the alignment match better",
                )
                self.assertEqual(
                    storage.load_review("REVIEW_2026-03-20_121334_002")["candidate_goal_text"],
                    "The docs do not all agree, and we need a usable spark ingress path",
                )
                self.assertIn("Reviews written to data/finis/reviews/", output.getvalue())
                self.assertNotIn("No candidate goals to review.", output.getvalue())

    def test_fine_still_filters_clearly_duplicate_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                spark_dir = Path("data/scintilla/sparks")
                spark_dir.mkdir(parents=True, exist_ok=True)
                spark_dir.joinpath("2026-03-20_121334.json").write_text(
                    json.dumps(
                        [
                            {
                                "spark": "I want to lock Finis review lineage"
                            }
                        ]
                    ),
                    encoding="utf-8",
                )
                storage.write_goal(
                    {
                        "goal_id": "FINIS_010",
                        "title": "Lock Finis review lineage",
                        "status": "active",
                        "created": "2026-03-09",
                        "description": "",
                        "derived_from": [],
                    }
                )
                output = io.StringIO()

                with mock.patch("builtins.input", side_effect=[]), mock.patch(
                    "sys.argv", ["azq", "fine"]
                ), contextlib.redirect_stdout(output):
                    cli.main()

                self.assertEqual(storage.list_review_files(), [])
                self.assertIn("No candidate goals to review.", output.getvalue())
                self.assertEqual(storage.load_goal("FINIS_010")["title"], "Lock Finis review lineage")

    def test_fine_writes_review_artifact_with_distinct_review_boundary_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                spark_dir = Path("data/scintilla/sparks")
                spark_dir.mkdir(parents=True, exist_ok=True)
                spark_dir.joinpath("2026-03-20_121334.json").write_text(
                    json.dumps(
                        [
                            {
                                "spark": "I want to stabilize Finis review boundaries"
                            }
                        ]
                    ),
                    encoding="utf-8",
                )
                output = io.StringIO()

                with mock.patch("builtins.input", side_effect=["n"]), mock.patch(
                    "sys.argv", ["azq", "fine"]
                ), contextlib.redirect_stdout(output):
                    cli.main()

                review_files = storage.list_review_files()
                self.assertEqual(
                    [path.name for path in review_files],
                    ["REVIEW_2026-03-20_121334_001.json"],
                )
                review_record = storage.load_review("REVIEW_2026-03-20_121334_001")
                self.assertIsNotNone(review_record)
                self.assertEqual(
                    review_record["raw_spark_text"],
                    "I want to stabilize Finis review boundaries",
                )
                self.assertEqual(
                    review_record["candidate_goal_text"],
                    "Stabilize Finis review boundaries",
                )
                self.assertEqual(review_record["review_status"], "pending")
                self.assertEqual(review_record["accepted_goal_id"], "")
                self.assertEqual(
                    review_record["spark_source"], "2026-03-20_121334"
                )
                self.assertIn(
                    "Reviews written to data/finis/reviews/", output.getvalue()
                )
                self.assertIsNone(storage.load_goal("FINIS_001"))

    def test_fine_acceptance_preserves_canonical_goal_behavior_and_records_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                spark_dir = Path("data/scintilla/sparks")
                spark_dir.mkdir(parents=True, exist_ok=True)
                spark_dir.joinpath("2026-03-20_121334.json").write_text(
                    json.dumps(
                        [
                            {
                                "spark": "I want to lock Finis review lineage"
                            }
                        ]
                    ),
                    encoding="utf-8",
                )
                output = io.StringIO()

                with mock.patch("azq.finis.fine.date", FixedDate), mock.patch(
                    "builtins.input", side_effect=["y"]
                ), mock.patch(
                    "sys.argv", ["azq", "fine"]
                ), contextlib.redirect_stdout(output):
                    cli.main()

                self.assertEqual(
                    storage.load_goal("FINIS_001"),
                    {
                        "goal_id": "FINIS_001",
                        "title": "Lock Finis review lineage",
                        "status": "active",
                        "created": "2026-03-20",
                        "description": "",
                        "derived_from": ["2026-03-20_121334"],
                    },
                )
                review_record = storage.load_review("REVIEW_2026-03-20_121334_001")
                self.assertIsNotNone(review_record)
                self.assertEqual(review_record["review_status"], "accepted")
                self.assertEqual(review_record["accepted_goal_id"], "FINIS_001")
                self.assertEqual(
                    review_record["raw_spark_text"],
                    "I want to lock Finis review lineage",
                )
                self.assertEqual(
                    review_record["candidate_goal_text"],
                    "Lock Finis review lineage",
                )
                self.assertIn("Goals written to data/finis/goals/", output.getvalue())


if __name__ == "__main__":
    unittest.main()

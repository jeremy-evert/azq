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

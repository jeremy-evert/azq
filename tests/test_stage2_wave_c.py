import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from azq import cli
from azq.finis import storage as finis_storage
from azq.formam import storage as formam_storage


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


class Stage2WaveCRegressionTests(unittest.TestCase):
    def test_normalize_deliverable_record_uses_canonical_schema(self):
        normalized = formam_storage.normalize_deliverable_record(
            {
                "deliverable_id": "DELIV_004",
                "goal_id": "FINIS_001",
                "title": "Canonical artifact",
                "artifact_description": "Visible structure",
                "dependencies": "DELIV_001",
            }
        )

        self.assertEqual(
            normalized,
            {
                "deliverable_id": "DELIV_004",
                "goal_id": "FINIS_001",
                "title": "Canonical artifact",
                "artifact_description": "Visible structure",
                "dependencies": ["DELIV_001"],
                "status": "drafted",
                "created": "",
            },
        )

    def test_parse_deliverable_record_round_trip_preserves_canonical_fields(self):
        record = {
            "deliverable_id": "DELIV_007",
            "goal_id": "FINIS_003",
            "title": "Round-trip deliverable",
            "artifact_description": "First line.\nSecond line.",
            "dependencies": ["DELIV_001", "DELIV_005"],
            "status": "drafted",
            "created": "2026-03-17",
        }

        markdown = formam_storage.serialize_deliverable_markdown(record)
        parsed = formam_storage.parse_deliverable_record(markdown)

        self.assertEqual(parsed, record)
        self.assertEqual(parsed["goal_id"], "FINIS_003")
        self.assertNotIn("goal_ids", parsed)

    def test_next_deliverable_id_uses_highest_existing_deliv_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                formam_storage.write_deliverable(
                    {
                        "deliverable_id": "DELIV_002",
                        "goal_id": "FINIS_001",
                        "title": "Second",
                        "artifact_description": "",
                        "dependencies": [],
                        "status": "drafted",
                        "created": "2026-03-17",
                    }
                )
                formam_storage.write_deliverable(
                    {
                        "deliverable_id": "DELIV_010",
                        "goal_id": "FINIS_001",
                        "title": "Tenth",
                        "artifact_description": "",
                        "dependencies": [],
                        "status": "drafted",
                        "created": "2026-03-17",
                    }
                )

                self.assertEqual(formam_storage.next_deliverable_id(), "DELIV_011")

    def test_validate_parent_goal_reads_canonical_finis_goal_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                finis_storage.write_goal(
                    {
                        "goal_id": "FINIS_001",
                        "title": "Active goal",
                        "status": "active",
                        "created": "2026-03-17",
                        "description": "Canonical parent",
                        "derived_from": [],
                    }
                )
                finis_storage.write_goal(
                    {
                        "goal_id": "FINIS_002",
                        "title": "Closed goal",
                        "status": "completed",
                        "created": "2026-03-17",
                        "description": "",
                        "derived_from": [],
                    }
                )

                self.assertEqual(
                    formam_storage.validate_parent_goal(
                        "FINIS_001", active_only=True
                    )["title"],
                    "Active goal",
                )

                with self.assertRaises(formam_storage.CanonicalGoalValidationError):
                    formam_storage.validate_parent_goal("FINIS_999", active_only=True)

                with self.assertRaises(formam_storage.CanonicalGoalValidationError):
                    formam_storage.validate_parent_goal("FINIS_002", active_only=True)

    def test_parse_goal_map_record_round_trip_preserves_canonical_fields(self):
        record = {
            "goal_id": "FINIS_001",
            "deliverable_ids": ["DELIV_001", "DELIV_002"],
            "dependency_edges": ["DELIV_001 -> DELIV_002"],
            "status": "mapped",
            "created": "2026-03-17",
            "notes": "Visible map notes",
        }

        markdown = formam_storage.serialize_goal_map_markdown(record)
        parsed = formam_storage.parse_goal_map_record(markdown)

        self.assertEqual(parsed, record)

    def test_form_build_list_show_and_map_cli_flow_writes_canonical_artifacts(self):
        # Exercise the main Stage 2 CLI flow explicitly:
        # form build, form list, form show, and form map.
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                finis_storage.write_goal(
                    {
                        "goal_id": "FINIS_001",
                        "title": "Build the baseline",
                        "status": "active",
                        "created": "2026-03-17",
                        "description": "Define the first visible artifact.",
                        "derived_from": ["spark-1"],
                    }
                )

                build_output = io.StringIO()
                with mock.patch("azq.formam.build.date", FixedDate), mock.patch(
                    "sys.argv", ["azq", "form", "build", "FINIS_001"]
                ), contextlib.redirect_stdout(build_output):
                    cli.main()

                deliverable = formam_storage.load_deliverable("DELIV_001")
                self.assertIsNotNone(deliverable)
                self.assertEqual(deliverable["goal_id"], "FINIS_001")
                self.assertEqual(deliverable["dependencies"], [])
                self.assertNotIn("goal_ids", deliverable)
                self.assertIn("Built DELIV_001 for FINIS_001", build_output.getvalue())

                goal_deliverables = formam_storage.load_deliverables_for_goal("FINIS_001")
                self.assertEqual(len(goal_deliverables), 1)
                self.assertEqual(goal_deliverables[0]["deliverable_id"], "DELIV_001")
                self.assertEqual(
                    [item["deliverable_id"] for item in formam_storage.load_all_deliverables()],
                    ["DELIV_001"],
                )

                list_output = io.StringIO()
                with mock.patch("sys.argv", ["azq", "form", "list"]), contextlib.redirect_stdout(
                    list_output
                ):
                    cli.main()
                list_text = list_output.getvalue()
                self.assertIn("Deliverables", list_text)
                self.assertIn("DELIV_001", list_text)
                self.assertIn("FINIS_001", list_text)

                show_output = io.StringIO()
                with mock.patch(
                    "sys.argv", ["azq", "form", "show", "DELIV_001"]
                ), contextlib.redirect_stdout(show_output):
                    cli.main()
                show_text = show_output.getvalue()
                self.assertIn("Deliverable: DELIV_001", show_text)
                self.assertIn("Goal: FINIS_001", show_text)
                self.assertIn("Artifact Description", show_text)

                map_output = io.StringIO()
                with mock.patch("azq.formam.maps.date", FixedDate), mock.patch(
                    "sys.argv", ["azq", "form", "map", "FINIS_001"]
                ), contextlib.redirect_stdout(map_output):
                    cli.main()

                goal_map = formam_storage.load_goal_map("FINIS_001")
                self.assertIsNotNone(goal_map)
                self.assertEqual(goal_map["goal_id"], "FINIS_001")
                self.assertEqual(goal_map["deliverable_ids"], ["DELIV_001"])
                self.assertEqual(goal_map["dependency_edges"], [])
                self.assertIn("Refreshed goal map for FINIS_001", map_output.getvalue())


if __name__ == "__main__":
    unittest.main()

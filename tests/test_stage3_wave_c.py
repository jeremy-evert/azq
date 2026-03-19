import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from azq import cli
from azq.agenda import dags as agenda_dags
from azq.agenda import storage as agenda_storage
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
        return "2026-03-18"


class Stage3WaveCRegressionTests(unittest.TestCase):
    def test_normalize_task_record_uses_canonical_agenda_schema(self):
        normalized = agenda_storage.normalize_task_record(
            {
                "task_id": "TASK_004",
                "parent_deliverable_id": "DELIV_003",
                "description": "First line.\nSecond line.",
                "depends_on": "TASK_001",
                "intent_summary": "Protect the Stage 3 baseline",
            }
        )

        self.assertEqual(
            normalized,
            {
                "task_id": "TASK_004",
                "deliverable_id": "DELIV_003",
                "title": "First line.",
                "status": "ready",
                "task_intent": {
                    "kind": "explicit",
                    "summary": "Protect the Stage 3 baseline",
                },
                "description": "First line.\nSecond line.",
                "dependencies": ["TASK_001"],
                "execution_notes": "",
                "created": "",
            },
        )

    def test_task_markdown_round_trip_preserves_canonical_fields(self):
        record = {
            "task_id": "TASK_007",
            "deliverable_id": "DELIV_005",
            "title": "Round-trip task title",
            "status": "ready",
            "task_intent": {
                "kind": "stub",
                "summary": "Initial Agenda task for DELIV_005",
            },
            "description": "First line.\nSecond line.",
            "dependencies": ["TASK_001", "TASK_003"],
            "execution_notes": "Visible execution note.",
            "created": "2026-03-18",
        }

        markdown = agenda_storage.serialize_task_markdown(record)
        parsed = agenda_storage.parse_task_markdown(markdown)

        self.assertEqual(parsed, record)
        self.assertEqual(markdown.count("- deliverable_id:"), 1)
        self.assertNotIn("parent_deliverable_id", markdown)

    def test_next_task_id_uses_highest_existing_canonical_task_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                finis_storage.write_goal(
                    {
                        "goal_id": "FINIS_001",
                        "title": "Goal",
                        "status": "active",
                        "created": "2026-03-18",
                        "description": "",
                        "derived_from": [],
                    }
                )
                formam_storage.write_deliverable(
                    {
                        "deliverable_id": "DELIV_001",
                        "goal_id": "FINIS_001",
                        "title": "Deliverable",
                        "artifact_description": "",
                        "dependencies": [],
                        "status": "drafted",
                        "created": "2026-03-18",
                    }
                )
                agenda_storage.write_task(
                    {
                        "task_id": "TASK_002",
                        "deliverable_id": "DELIV_001",
                        "title": "",
                        "status": "ready",
                        "task_intent": {"kind": "stub", "summary": "Second"},
                        "description": "Second task",
                        "dependencies": [],
                        "execution_notes": "",
                        "created": "2026-03-18",
                    }
                )
                agenda_storage.write_task(
                    {
                        "task_id": "TASK_010",
                        "deliverable_id": "DELIV_001",
                        "title": "",
                        "status": "ready",
                        "task_intent": {"kind": "stub", "summary": "Tenth"},
                        "description": "Tenth task",
                        "dependencies": [],
                        "execution_notes": "",
                        "created": "2026-03-18",
                    }
                )

                self.assertEqual(agenda_storage.next_task_id(), "TASK_011")

    def test_validate_parent_deliverable_reads_canonical_formam_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                finis_storage.write_goal(
                    {
                        "goal_id": "FINIS_001",
                        "title": "Parent goal",
                        "status": "active",
                        "created": "2026-03-18",
                        "description": "Canonical parent goal",
                        "derived_from": [],
                    }
                )
                formam_storage.write_deliverable(
                    {
                        "deliverable_id": "DELIV_001",
                        "goal_id": "FINIS_001",
                        "title": "Canonical deliverable",
                        "artifact_description": "Visible artifact boundary",
                        "dependencies": [],
                        "status": "drafted",
                        "created": "2026-03-18",
                    }
                )

                validated = agenda_storage.validate_parent_deliverable("DELIV_001")
                self.assertEqual(validated["goal_id"], "FINIS_001")
                self.assertEqual(validated["deliverable_id"], "DELIV_001")

                with self.assertRaises(
                    agenda_storage.CanonicalDeliverableValidationError
                ):
                    agenda_storage.validate_parent_deliverable("DELIV_999")

    def test_dag_json_round_trip_and_goal_level_repository_reads_are_canonical(self):
        record = {
            "goal_id": "FINIS_004",
            "deliverable_ids": ["DELIV_001"],
            "task_ids": ["TASK_001", "TASK_002"],
            "dependency_edges": [{"from_task_id": "TASK_001", "to_task_id": "TASK_002"}],
            "status": "draft",
            "created": "2026-03-18",
            "notes": "Canonical Agenda DAG artifact",
        }

        json_text = agenda_storage.serialize_dag_json(record)
        parsed = agenda_storage.parse_dag_json(json_text)

        self.assertEqual(parsed["graph_id"], "GOAL_FINIS_004_DAG")
        self.assertEqual(parsed["goal_id"], "FINIS_004")
        self.assertEqual(
            parsed["dependency_edges"],
            [
                {
                    "edge_id": "TASK_001->TASK_002",
                    "from_task_id": "TASK_001",
                    "to_task_id": "TASK_002",
                }
            ],
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                agenda_storage.write_dag(record)
                loaded = agenda_storage.load_goal_dag("FINIS_004")

                self.assertEqual(loaded, parsed)
                self.assertEqual(
                    agenda_storage.load_all_dags(),
                    [parsed],
                )

    def test_refresh_agenda_dag_writes_goal_level_artifact_for_parent_goal(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                finis_storage.write_goal(
                    {
                        "goal_id": "FINIS_009",
                        "title": "Refresh DAG baseline",
                        "status": "active",
                        "created": "2026-03-18",
                        "description": "",
                        "derived_from": [],
                    }
                )
                formam_storage.write_deliverable(
                    {
                        "deliverable_id": "DELIV_007",
                        "goal_id": "FINIS_009",
                        "title": "Deliverable for DAG refresh",
                        "artifact_description": "Protect the canonical DAG artifact.",
                        "dependencies": [],
                        "status": "drafted",
                        "created": "2026-03-18",
                    }
                )
                agenda_storage.write_task(
                    {
                        "task_id": "TASK_001",
                        "deliverable_id": "DELIV_007",
                        "title": "",
                        "status": "ready",
                        "task_intent": {"kind": "stub", "summary": "First"},
                        "description": "First task",
                        "dependencies": [],
                        "execution_notes": "",
                        "created": "2026-03-18",
                    }
                )
                agenda_storage.write_task(
                    {
                        "task_id": "TASK_002",
                        "deliverable_id": "DELIV_007",
                        "title": "",
                        "status": "ready",
                        "task_intent": {"kind": "stub", "summary": "Second"},
                        "description": "Second task",
                        "dependencies": ["TASK_001"],
                        "execution_notes": "",
                        "created": "2026-03-18",
                    }
                )

                with mock.patch("azq.agenda.dags.date", FixedDate):
                    result = agenda_dags.refresh_agenda_dag("DELIV_007")

                self.assertEqual(result["deliverable"]["goal_id"], "FINIS_009")
                self.assertEqual(result["dag_path"], agenda_storage.dag_file_path("FINIS_009"))
                self.assertEqual(result["dag"]["deliverable_ids"], ["DELIV_007"])
                self.assertEqual(result["dag"]["task_ids"], ["TASK_001", "TASK_002"])
                self.assertEqual(
                    result["dag"]["dependency_edges"],
                    [
                        {
                            "edge_id": "TASK_001->TASK_002",
                            "from_task_id": "TASK_001",
                            "to_task_id": "TASK_002",
                        }
                    ],
                )
                stored_dag = agenda_storage.load_goal_dag("FINIS_009")
                self.assertIsNotNone(stored_dag)
                self.assertEqual(stored_dag["graph_id"], "GOAL_FINIS_009_DAG")
                self.assertEqual(stored_dag["goal_id"], result["dag"]["goal_id"])
                self.assertEqual(
                    stored_dag["deliverable_ids"], result["dag"]["deliverable_ids"]
                )
                self.assertEqual(stored_dag["task_ids"], result["dag"]["task_ids"])

    def test_agenda_build_list_show_and_dag_cli_flow_writes_canonical_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            with working_directory(repo_root):
                finis_storage.write_goal(
                    {
                        "goal_id": "FINIS_001",
                        "title": "Ship the Stage 3 baseline",
                        "status": "active",
                        "created": "2026-03-18",
                        "description": "Protect the canonical Agenda loop.",
                        "derived_from": ["spark-1"],
                    }
                )
                formam_storage.write_deliverable(
                    {
                        "deliverable_id": "DELIV_001",
                        "goal_id": "FINIS_001",
                        "title": "Canonical deliverable",
                        "artifact_description": "Protect the canonical Agenda loop.",
                        "dependencies": [],
                        "status": "drafted",
                        "created": "2026-03-18",
                    }
                )

                build_output = io.StringIO()
                with mock.patch("azq.agenda.build.date", FixedDate), mock.patch(
                    "sys.argv", ["azq", "agenda", "build", "DELIV_001"]
                ), contextlib.redirect_stdout(build_output):
                    cli.main()

                built_task = agenda_storage.load_task("TASK_001")
                self.assertIsNotNone(built_task)
                self.assertEqual(built_task["deliverable_id"], "DELIV_001")
                self.assertEqual(
                    built_task["task_intent"],
                    {"kind": "stub", "summary": "Initial Agenda task for DELIV_001"},
                )
                task_text = agenda_storage.task_file_path("TASK_001").read_text(
                    encoding="utf-8"
                )
                self.assertEqual(task_text.count("- deliverable_id:"), 1)
                self.assertNotIn("parent_deliverable_id", task_text)
                self.assertIn("Built TASK_001 for DELIV_001", build_output.getvalue())

                list_output = io.StringIO()
                with mock.patch("sys.argv", ["azq", "agenda", "list"]), contextlib.redirect_stdout(
                    list_output
                ):
                    cli.main()

                list_text = list_output.getvalue()
                self.assertIn("TASK_001", list_text)
                self.assertIn("DELIV_001", list_text)
                self.assertIn("ready", list_text)

                show_output = io.StringIO()
                with mock.patch("sys.argv", ["azq", "agenda", "show", "TASK_001"]), contextlib.redirect_stdout(
                    show_output
                ):
                    cli.main()

                show_text = show_output.getvalue()
                self.assertIn("Task TASK_001", show_text)
                self.assertIn("deliverable_id: DELIV_001", show_text)
                self.assertIn("Protect the canonical Agenda loop.", show_text)

                dag_output = io.StringIO()
                with mock.patch("azq.agenda.dags.date", FixedDate), mock.patch(
                    "sys.argv", ["azq", "agenda", "dag", "DELIV_001"]
                ), contextlib.redirect_stdout(dag_output):
                    cli.main()

                dag_record = agenda_storage.load_goal_dag("FINIS_001")
                self.assertIsNotNone(dag_record)
                self.assertEqual(dag_record["goal_id"], "FINIS_001")
                self.assertEqual(dag_record["deliverable_ids"], ["DELIV_001"])
                self.assertEqual(dag_record["task_ids"], ["TASK_001"])
                self.assertEqual(
                    agenda_storage.dag_file_path("FINIS_001").name,
                    "GOAL_FINIS_001_DAG.json",
                )
                self.assertIn("Refreshed agenda DAG for DELIV_001", dag_output.getvalue())


if __name__ == "__main__":
    unittest.main()

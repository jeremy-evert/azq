"""Canonical storage helpers for Agenda DAG JSON artifacts."""

import json
from pathlib import Path
from typing import Any, Optional

from azq.agenda.paths import (
    dag_file_path as canonical_dag_file_path,
    ensure_dags_dir as ensure_canonical_dags_dir,
    list_dag_files as list_canonical_dag_files,
)
from azq.agenda.schemas import canonical_graph_id, normalize_dag_record


def ensure_dags_dir() -> Path:
    """Create the DAG artifact directory owned by this module."""
    return ensure_canonical_dags_dir()


def dag_file_path(goal_id: str) -> Path:
    """Map an exact goal id to its canonical DAG artifact path."""
    return canonical_dag_file_path(goal_id)


def list_dag_files() -> list[Path]:
    """Return DAG artifact files in stable filename order."""
    return list_canonical_dag_files()


def _validate_canonical_dag_record(dag_record: dict[str, Any]) -> dict[str, Any]:
    """Normalize and validate one DAG record before persistence."""
    record = normalize_dag_record(dag_record)
    goal_id = str(record["goal_id"]).strip()
    if not goal_id:
        raise ValueError("Cannot write canonical DAG artifact without a goal_id.")

    expected_graph_id = canonical_graph_id(goal_id)
    if record["graph_id"] != expected_graph_id:
        raise ValueError(
            "Cannot use canonical DAG artifact for goal_id "
            f"{goal_id!r} with non-canonical graph_id {record['graph_id']!r}."
        )

    return record


def serialize_dag_json(dag_record: dict[str, Any]) -> str:
    """Serialize a canonical DAG record into diff-friendly JSON."""
    record = _validate_canonical_dag_record(dag_record)
    return json.dumps(record, indent=2, sort_keys=True) + "\n"


def serialize_dag_record(dag_record: dict[str, Any]) -> str:
    """Backward-compatible alias for canonical DAG JSON."""
    return serialize_dag_json(dag_record)


def dag_to_json(dag_record: dict[str, Any]) -> str:
    """Alias for callers expecting a DAG-to-JSON helper."""
    return serialize_dag_json(dag_record)


def parse_dag_json(json_text: str) -> dict[str, Any]:
    """Parse a canonical DAG JSON artifact back into a record."""
    try:
        raw_record = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid DAG JSON artifact: {exc.msg}.") from exc

    if not isinstance(raw_record, dict):
        raise ValueError("DAG JSON artifact must decode to an object.")

    return _validate_canonical_dag_record(raw_record)


def parse_dag_record(json_text: str) -> dict[str, Any]:
    """Backward-compatible alias for canonical DAG JSON parsing."""
    return parse_dag_json(json_text)


def dag_from_json(json_text: str) -> dict[str, Any]:
    """Alias for callers expecting a JSON-to-DAG helper."""
    return parse_dag_json(json_text)


def load_dag(goal_id: str) -> Optional[dict[str, Any]]:
    """Load one canonical DAG artifact by exact goal id."""
    dag_path = dag_file_path(goal_id)
    if not dag_path.is_file():
        return None
    return parse_dag_json(dag_path.read_text(encoding="utf-8"))


def load_goal_dag(goal_id: str) -> Optional[dict[str, Any]]:
    """Backward-compatible helper for exact goal-id DAG lookup."""
    return load_dag(goal_id)


def load_all_dags() -> list[dict[str, Any]]:
    """Load all canonical DAG artifacts in deterministic filename order."""
    dags: list[dict[str, Any]] = []
    for dag_path in list_dag_files():
        dags.append(parse_dag_json(dag_path.read_text(encoding="utf-8")))
    return dags


def write_dag(dag_record: dict[str, Any]) -> Path:
    """Write one canonical DAG artifact to its exact JSON file."""
    record = _validate_canonical_dag_record(dag_record)
    dag_path = dag_file_path(record["goal_id"])
    ensure_dags_dir()
    dag_path.write_text(serialize_dag_json(record), encoding="utf-8")
    return dag_path


def save_dag(dag_record: dict[str, Any]) -> Path:
    """Backward-compatible alias for canonical DAG writes."""
    return write_dag(dag_record)


# Public DAG-storage helpers re-exported by ``azq.agenda.storage``.
__all__ = [
    "ensure_dags_dir",
    "dag_file_path",
    "list_dag_files",
    "serialize_dag_record",
    "serialize_dag_json",
    "dag_to_json",
    "parse_dag_record",
    "parse_dag_json",
    "dag_from_json",
    "load_dag",
    "load_goal_dag",
    "load_all_dags",
    "write_dag",
    "save_dag",
]

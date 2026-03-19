"""Thin command-layer writer for canonical Agenda DAG refreshes."""

from datetime import date
from typing import Any, Optional

from azq.agenda.dag_storage import load_dag, write_dag
from azq.agenda.lineage import resolve_deliverable_lineage
from azq.agenda.task_storage import (
    load_tasks_for_deliverable,
)

DEFAULT_AGENDA_DAG_NOTES = (
    "Canonical Agenda DAG generated from current deliverable task dependencies."
)


def derive_task_dependency_edges(
    tasks: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Derive conservative task edges from exact-deliverable task dependencies.

    Edges stay conservative and inspectable:
    - only exact task ids present in ``tasks`` become edges
    - self-references are ignored
    - duplicate edges collapse while preserving deterministic task order
    """

    task_ids = {
        str(task.get("task_id", "")).strip()
        for task in tasks
        if str(task.get("task_id", "")).strip()
    }

    dependency_edges: list[dict[str, str]] = []
    seen_edges: set[tuple[str, str]] = set()

    for task in tasks:
        task_id = str(task.get("task_id", "")).strip()
        if not task_id:
            continue

        for dependency in list(task.get("dependencies", []) or []):
            dependency_id = str(dependency).strip()
            edge_key = (dependency_id, task_id)
            if (
                not dependency_id
                or dependency_id == task_id
                or dependency_id not in task_ids
                or edge_key in seen_edges
            ):
                continue

            seen_edges.add(edge_key)
            dependency_edges.append(
                {
                    "edge_id": f"{dependency_id}->{task_id}",
                    "from_task_id": dependency_id,
                    "to_task_id": task_id,
                }
            )

    return dependency_edges


def build_agenda_dag_record(
    deliverable_record: dict[str, Any],
    tasks: list[dict[str, Any]],
    *,
    existing_dag: Optional[dict[str, Any]] = None,
    created: Optional[str] = None,
) -> dict[str, Any]:
    """Build one canonical goal-level DAG record from exact-deliverable tasks."""

    deliverable_id = str(deliverable_record["deliverable_id"]).strip()
    goal_id = str(deliverable_record["goal_id"]).strip()
    dag_created = created or str(date.today())
    if existing_dag is not None:
        dag_created = existing_dag.get("created", dag_created) or dag_created

    return {
        "goal_id": goal_id,
        "deliverable_ids": [deliverable_id],
        "task_ids": [task["task_id"] for task in tasks if str(task.get("task_id", "")).strip()],
        "dependency_edges": derive_task_dependency_edges(tasks),
        "status": (
            existing_dag.get("status", "draft")
            if existing_dag is not None
            else "draft"
        ),
        "created": dag_created,
        "notes": (
            existing_dag.get("notes", DEFAULT_AGENDA_DAG_NOTES)
            if existing_dag is not None
            else DEFAULT_AGENDA_DAG_NOTES
        ),
    }


def refresh_agenda_dag(deliverable_id: str) -> dict[str, Any]:
    """Validate one exact deliverable and refresh its parent goal DAG artifact."""

    lineage = resolve_deliverable_lineage(deliverable_id)
    deliverable_record = lineage["deliverable"]
    goal_id = lineage["goal_id"]
    tasks = load_tasks_for_deliverable(deliverable_record["deliverable_id"])
    existing_dag = load_dag(goal_id)
    dag_record = build_agenda_dag_record(
        deliverable_record,
        tasks,
        existing_dag=existing_dag,
    )
    dag_path = write_dag(dag_record)

    print(f"Refreshed agenda DAG for {deliverable_record['deliverable_id']}")
    print(f"DAG: {dag_path}")

    return {
        "deliverable": deliverable_record,
        "tasks": tasks,
        "dag": dag_record,
        "dag_path": dag_path,
    }


def build_agenda_dag(deliverable_id: str) -> dict[str, Any]:
    """Backward-compatible alias for the deliverable-scoped DAG command."""
    return refresh_agenda_dag(deliverable_id)


def agenda_dag(deliverable_id: str) -> dict[str, Any]:
    """Alternate alias matching the requested Agenda command name."""
    return refresh_agenda_dag(deliverable_id)


build_dag_for_deliverable = refresh_agenda_dag


__all__ = [
    "DEFAULT_AGENDA_DAG_NOTES",
    "derive_task_dependency_edges",
    "build_agenda_dag_record",
    "refresh_agenda_dag",
    "build_agenda_dag",
    "agenda_dag",
    "build_dag_for_deliverable",
]

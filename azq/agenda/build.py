"""Thin command-layer writer for initial Agenda task creation."""

from datetime import date
from typing import Any

from azq.agenda.task_storage import (
    next_task_id,
    validate_parent_deliverable,
    write_task,
)


def _stub_task_description(deliverable_record: dict[str, Any]) -> str:
    """Build one deterministic stub task description from a deliverable."""
    deliverable_id = str(deliverable_record.get("deliverable_id", "")).strip()
    title = str(deliverable_record.get("title", "")).strip()
    artifact_description = str(
        deliverable_record.get("artifact_description", "")
    ).strip()

    if artifact_description:
        return artifact_description
    if title:
        return f"Advance deliverable {deliverable_id}: {title}"
    return f"Advance deliverable {deliverable_id}"


def build_stub_task_record(
    deliverable_record: dict[str, Any], task_id: str, *, created: str
) -> dict[str, Any]:
    """Build one deterministic stub task record from validated deliverable data."""
    deliverable_id = str(deliverable_record["deliverable_id"]).strip()
    goal_id = str(deliverable_record.get("goal_id", "")).strip()

    return {
        "task_id": task_id,
        "deliverable_id": deliverable_id,
        "title": "",
        "status": "ready",
        "task_intent": {
            "kind": "stub",
            "summary": f"Initial Agenda task for {deliverable_id}",
        },
        "description": _stub_task_description(deliverable_record),
        "dependencies": [],
        "execution_notes": "",
        "created": created,
        "goal_id": goal_id,
    }


def build_agenda(deliverable_id: str) -> dict[str, Any]:
    """Create one canonical stub task for an exact parent deliverable."""
    deliverable_record = validate_parent_deliverable(deliverable_id)
    created = str(date.today())
    task_id = next_task_id()

    task_record = build_stub_task_record(deliverable_record, task_id, created=created)
    task_path = write_task(task_record)

    result = {
        "deliverable": deliverable_record,
        "task": task_record,
        "task_path": task_path,
    }

    print(f"Built {task_id} for {deliverable_record['deliverable_id']}")
    print(f"Task: {task_path}")
    return result


build_tasks_for_deliverable = build_agenda
agenda_build = build_agenda


__all__ = [
    "build_stub_task_record",
    "build_agenda",
    "build_tasks_for_deliverable",
    "agenda_build",
]

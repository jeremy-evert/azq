"""Thin presentation helpers for canonical Agenda task listings."""

from typing import Any

from azq.agenda import storage as agenda_storage

NO_TASKS_MESSAGE = "No tasks defined."


def load_all_tasks() -> list[dict[str, Any]]:
    """Load canonical tasks through the shared Agenda storage layer."""
    return agenda_storage.load_all_tasks()


def _display_width(tasks: list[dict[str, Any]], field: str, minimum: int) -> int:
    """Compute a stable column width for terminal-readable task output."""
    return max(
        minimum,
        max((len(str(task.get(field, ""))) for task in tasks), default=0),
    )


def _short_description(task: dict[str, Any], *, max_length: int = 72) -> str:
    """Build a short readable summary from the canonical description field."""
    description = str(task.get("description", "")).strip()
    if not description:
        return "(no description)"

    summary = " ".join(line.strip() for line in description.splitlines() if line.strip())
    if len(summary) <= max_length:
        return summary

    return f"{summary[: max_length - 3].rstrip()}..."


def list_tasks() -> list[dict[str, Any]]:
    """Print a read-only listing of canonical Agenda tasks."""
    tasks = load_all_tasks()

    if not tasks:
        print(NO_TASKS_MESSAGE)
        return []

    task_width = _display_width(tasks, "task_id", len("TASK"))
    deliverable_width = _display_width(tasks, "deliverable_id", len("DELIVERABLE"))
    status_width = _display_width(tasks, "status", len("STATUS"))

    print("\nTasks\n")
    print(
        f"{'TASK':<{task_width}}  "
        f"{'DELIVERABLE':<{deliverable_width}}  "
        f"{'STATUS':<{status_width}}  "
        "DESCRIPTION"
    )

    for task in tasks:
        print(
            f"{task['task_id']:<{task_width}}  "
            f"{task['deliverable_id']:<{deliverable_width}}  "
            f"{task['status']:<{status_width}}  "
            f"{_short_description(task)}"
        )

    return tasks


__all__ = [
    "NO_TASKS_MESSAGE",
    "load_all_tasks",
    "list_tasks",
]

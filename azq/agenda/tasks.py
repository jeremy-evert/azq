"""Thin presentation helpers for canonical Agenda task listings and inspection."""

from typing import Any, Optional

from azq.agenda import storage as agenda_storage

NO_TASKS_MESSAGE = "No tasks defined."
TASK_NOT_FOUND_MESSAGE = "Task not found: {task_id}"


def load_all_tasks() -> list[dict[str, Any]]:
    """Load canonical tasks through the shared Agenda storage layer."""
    return agenda_storage.load_all_tasks()


def load_task(task_id: str) -> Optional[dict[str, Any]]:
    """Load one canonical task by exact task id through shared storage."""
    return agenda_storage.load_task(task_id)


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


def _print_task_list(label: str, values: list[Any]) -> None:
    """Print one canonical list field in a readable inspection format."""
    print(f"{label}:")
    if not values:
        print("- []")
        return

    for value in values:
        print(f"- {value}")


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


def show_task(task_id: str) -> Optional[dict[str, Any]]:
    """Print one canonical task record by exact task id."""
    exact_task_id = str(task_id).strip()
    task = load_task(exact_task_id)

    if task is None:
        print(TASK_NOT_FOUND_MESSAGE.format(task_id=exact_task_id or task_id))
        return None

    print(f"\nTask {task['task_id']}\n")
    print(f"deliverable_id: {task['deliverable_id']}")
    print(f"status: {task['status']}")
    print(f"created: {task['created']}")
    _print_task_list("dependencies", task.get("dependencies", []))
    print("description:")
    print(task.get("description", "") or "(none)")
    print("execution_notes:")
    print(task.get("execution_notes", "") or "(none)")
    return task


__all__ = [
    "NO_TASKS_MESSAGE",
    "TASK_NOT_FOUND_MESSAGE",
    "load_task",
    "load_all_tasks",
    "list_tasks",
    "show_task",
]

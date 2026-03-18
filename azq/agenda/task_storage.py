"""Canonical storage helpers for Agenda task Markdown files."""

from pathlib import Path
from typing import Any, Optional

from azq.agenda import paths
from azq.agenda.schemas import (
    DEPENDENCIES_HEADING,
    DESCRIPTION_HEADING,
    EXECUTION_NOTES_HEADING,
    TASK_ID_PATTERN,
    TASK_INTENT_HEADING,
    normalize_task_record,
    task_id_number,
)


def ensure_tasks_dir() -> Path:
    """Create the tasks directory owned by this module."""
    return paths.ensure_tasks_dir()


def task_file_path(task_id: str) -> Path:
    """Map an exact task id to its Markdown file path."""
    return paths.task_file_path(task_id)


def list_task_files() -> list[Path]:
    """Return task files in stable filename order."""
    return paths.list_task_files()


def serialize_task_markdown(task_record: dict[str, Any]) -> str:
    """Serialize a canonical task record into diff-friendly Markdown."""
    record = normalize_task_record(task_record)
    task_intent = record["task_intent"]
    lines = [
        f"# {record['task_id']}",
        "",
        f"- deliverable_id: {record['deliverable_id']}",
        f"- title: {record['title']}",
        f"- status: {record['status']}",
        f"- created: {record['created']}",
        "",
        TASK_INTENT_HEADING,
        "",
        f"- kind: {task_intent['kind']}",
        f"- summary: {task_intent['summary']}",
        "",
        DEPENDENCIES_HEADING,
        "",
    ]

    dependencies = record["dependencies"]
    if dependencies:
        for dependency in dependencies:
            lines.append(f"- {dependency}")
    else:
        lines.append("- []")

    lines.extend(["", DESCRIPTION_HEADING, ""])

    description = record["description"]
    if description:
        lines.extend(str(description).splitlines())

    lines.extend(["", EXECUTION_NOTES_HEADING, ""])

    execution_notes = record["execution_notes"]
    if execution_notes:
        lines.extend(str(execution_notes).splitlines())

    lines.append("")
    return "\n".join(lines)


def serialize_task_record(task_record: dict[str, Any]) -> str:
    """Backward-compatible alias for canonical task Markdown."""
    return serialize_task_markdown(task_record)


def task_to_markdown(task_record: dict[str, Any]) -> str:
    """Alias for callers expecting a task-to-Markdown helper."""
    return serialize_task_markdown(task_record)


def _consume_blank_lines(lines: list[str], index: int) -> int:
    while index < len(lines) and lines[index].strip() == "":
        index += 1
    return index


def _parse_metadata_line(line: str, *, label: str) -> str:
    stripped = line.strip()
    prefix = f"- {label}:"
    if not stripped.startswith(prefix):
        raise ValueError(f"Expected metadata line for {label!r}, got: {line!r}")
    return stripped[len(prefix) :].lstrip()


def _parse_task_intent_section(lines: list[str], index: int) -> tuple[dict[str, str], int]:
    if index >= len(lines) or lines[index].strip() != TASK_INTENT_HEADING:
        raise ValueError(f"Task markdown is missing the {TASK_INTENT_HEADING!r} section.")

    index = _consume_blank_lines(lines, index + 1)
    kind = ""
    summary = ""

    while index < len(lines):
        stripped = lines[index].strip()
        if stripped == "":
            index += 1
            continue
        if stripped == DEPENDENCIES_HEADING:
            break
        if stripped.startswith("- kind:"):
            kind = stripped[len("- kind:") :].lstrip()
        elif stripped.startswith("- summary:"):
            summary = stripped[len("- summary:") :].lstrip()
        else:
            raise ValueError(f"Unrecognized task intent line: {lines[index]!r}")
        index += 1

    return {"kind": kind, "summary": summary}, index


def _parse_list_section(
    lines: list[str], index: int, *, heading: str
) -> tuple[list[str], int]:
    if index >= len(lines) or lines[index].strip() != heading:
        raise ValueError(f"Task markdown is missing the {heading!r} section.")

    index = _consume_blank_lines(lines, index + 1)
    values: list[str] = []

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped == "":
            index += 1
            continue
        if stripped.startswith("## "):
            break
        if stripped == "- []":
            index += 1
            continue
        if not stripped.startswith("- "):
            raise ValueError(f"Unrecognized list item in {heading!r}: {line!r}")
        values.append(stripped[2:])
        index += 1

    return values, index


def _parse_text_section(
    lines: list[str], index: int, *, heading: str, next_heading: Optional[str] = None
) -> tuple[str, int]:
    if index >= len(lines) or lines[index].strip() != heading:
        raise ValueError(f"Task markdown is missing the {heading!r} section.")

    index += 1
    content_lines: list[str] = []

    while index < len(lines):
        stripped = lines[index].strip()
        if next_heading is not None and stripped == next_heading:
            break
        content_lines.append(lines[index])
        index += 1

    while content_lines and content_lines[0].strip() == "":
        content_lines.pop(0)
    while content_lines and content_lines[-1].strip() == "":
        content_lines.pop()

    return "\n".join(content_lines), index


def parse_task_markdown(markdown_text: str) -> dict[str, Any]:
    """Parse a canonical Markdown task file back into a record."""
    lines = markdown_text.splitlines()
    if not lines:
        raise ValueError("Task markdown is empty.")

    header = lines[0].strip()
    if not header.startswith("# "):
        raise ValueError("Task markdown must start with a '# <task_id>' header.")

    task_id = header[2:].strip()
    if not task_id:
        raise ValueError("Task markdown header must include a task id.")

    index = _consume_blank_lines(lines, 1)
    deliverable_id = _parse_metadata_line(lines[index], label="deliverable_id")
    index += 1
    title = _parse_metadata_line(lines[index], label="title")
    index += 1
    status = _parse_metadata_line(lines[index], label="status")
    index += 1
    created = _parse_metadata_line(lines[index], label="created")
    index += 1
    index = _consume_blank_lines(lines, index)

    task_intent, index = _parse_task_intent_section(lines, index)
    index = _consume_blank_lines(lines, index)
    dependencies, index = _parse_list_section(lines, index, heading=DEPENDENCIES_HEADING)
    index = _consume_blank_lines(lines, index)
    description, index = _parse_text_section(
        lines,
        index,
        heading=DESCRIPTION_HEADING,
        next_heading=EXECUTION_NOTES_HEADING,
    )
    execution_notes, index = _parse_text_section(
        lines,
        index,
        heading=EXECUTION_NOTES_HEADING,
    )

    return normalize_task_record(
        {
            "task_id": task_id,
            "deliverable_id": deliverable_id,
            "title": title,
            "status": status,
            "task_intent": task_intent,
            "description": description,
            "dependencies": dependencies,
            "execution_notes": execution_notes,
            "created": created,
        }
    )


def parse_task_record(markdown_text: str) -> dict[str, Any]:
    """Backward-compatible alias for canonical task Markdown parsing."""
    return parse_task_markdown(markdown_text)


def task_from_markdown(markdown_text: str) -> dict[str, Any]:
    """Alias for callers expecting a Markdown-to-task helper."""
    return parse_task_markdown(markdown_text)


def load_task(task_id: str) -> Optional[dict[str, Any]]:
    """Load one canonical task record by exact task id."""
    task_path = task_file_path(task_id)
    if not task_path.is_file():
        return None
    return parse_task_markdown(task_path.read_text(encoding="utf-8"))


def load_all_tasks() -> list[dict[str, Any]]:
    """Load all canonical task files in deterministic order."""
    tasks: list[dict[str, Any]] = []
    for task_path in list_task_files():
        tasks.append(parse_task_markdown(task_path.read_text(encoding="utf-8")))
    return tasks


def load_tasks_for_deliverable(deliverable_id: str) -> list[dict[str, Any]]:
    """Load canonical tasks whose deliverable_id matches exactly."""
    return [
        task for task in load_all_tasks() if task["deliverable_id"] == deliverable_id
    ]


def load_deliverable_tasks(deliverable_id: str) -> list[dict[str, Any]]:
    """Backward-compatible helper for exact deliverable_id task lookup."""
    return load_tasks_for_deliverable(deliverable_id)


def next_task_id() -> str:
    """Compute the next stable TASK id from canonical task files."""
    highest_task_number = 0

    for task_path in list_task_files():
        task_number = task_id_number(task_path.stem)
        if task_number is not None:
            highest_task_number = max(highest_task_number, task_number)

    return f"{paths.TASK_FILE_PREFIX}{highest_task_number + 1:03d}"


def write_task(task_record: dict[str, Any]) -> Path:
    """Write one canonical task record to its exact Markdown file."""
    record = normalize_task_record(task_record)
    task_id = str(record["task_id"]).strip()
    if not TASK_ID_PATTERN.fullmatch(task_id):
        raise ValueError(
            f"Cannot write canonical task file for invalid task_id {task_id!r}."
        )

    task_path = task_file_path(task_id)
    ensure_tasks_dir()
    task_path.write_text(serialize_task_markdown(record), encoding="utf-8")
    return task_path


def save_task(task_record: dict[str, Any]) -> Path:
    """Backward-compatible alias for canonical task writes."""
    return write_task(task_record)


__all__ = [
    "ensure_tasks_dir",
    "task_file_path",
    "list_task_files",
    "serialize_task_record",
    "serialize_task_markdown",
    "task_to_markdown",
    "parse_task_record",
    "parse_task_markdown",
    "task_from_markdown",
    "load_task",
    "load_all_tasks",
    "load_tasks_for_deliverable",
    "load_deliverable_tasks",
    "next_task_id",
    "write_task",
    "save_task",
]

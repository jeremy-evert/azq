"""Canonical storage helpers for visible Agenda task log artifacts."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from azq.agenda import paths

LOG_HEADER_SUFFIX = " Log"
ENTRIES_HEADING = "## Entries"


def ensure_logs_dir() -> Path:
    """Create the canonical task log directory owned by this module."""
    return paths.ensure_logs_dir()


def task_log_file_path(task_id: str) -> Path:
    """Map an exact task id to its canonical task log artifact path."""
    return paths.task_log_file_path(task_id)


def log_file_path(task_id: str) -> Path:
    """Backward-compatible alias for the canonical task log path helper."""
    return task_log_file_path(task_id)


def list_task_log_files() -> list[Path]:
    """Return canonical task log artifacts in stable filename order."""
    return paths.list_task_log_files()


def _resolve_task_id(task_or_record: Any) -> str:
    if isinstance(task_or_record, str):
        task_id = task_or_record.strip()
    elif isinstance(task_or_record, dict):
        task_id = str(task_or_record.get("task_id", "")).strip()
    else:
        task_id = str(getattr(task_or_record, "task_id", "")).strip()

    if not task_id:
        raise ValueError("Cannot write a task log without an exact task_id.")

    return task_id


def _log_timestamp(timestamp: Optional[str] = None) -> str:
    if timestamp is not None:
        normalized = str(timestamp).strip()
        if not normalized:
            raise ValueError("Task log timestamps cannot be blank.")
        return normalized

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _entry_lines(event: str, note: str, *, timestamp: str) -> list[str]:
    normalized_event = str(event).strip()
    if not normalized_event:
        raise ValueError("Task log entries require a non-empty event.")

    lines = [f"### {timestamp} {normalized_event}", ""]
    note_text = str(note).strip()
    if note_text:
        lines.extend(note_text.splitlines())
    else:
        lines.append("-")
    lines.append("")
    return lines


def _initial_log_text(task_id: str) -> str:
    return "\n".join(
        [
            f"# {task_id}{LOG_HEADER_SUFFIX}",
            "",
            f"- task_id: {task_id}",
            "- layer: supporting artifact",
            "",
            ENTRIES_HEADING,
            "",
        ]
    )


def ensure_task_log(task_or_record: Any) -> Path:
    """Create the visible per-task log artifact if it does not yet exist."""
    task_id = _resolve_task_id(task_or_record)
    log_path = task_log_file_path(task_id)
    ensure_logs_dir()

    if not log_path.exists():
        log_path.write_text(_initial_log_text(task_id), encoding="utf-8")

    return log_path


def append_task_log_entry(
    task_or_record: Any, event: str, note: str, *, timestamp: Optional[str] = None
) -> Path:
    """Append one visible event entry to a task-local log artifact."""
    log_path = ensure_task_log(task_or_record)
    entry_lines = _entry_lines(event, note, timestamp=_log_timestamp(timestamp))
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(entry_lines))
    return log_path


def write_task_log(
    task_or_record: Any, event: str, note: str, *, timestamp: Optional[str] = None
) -> Path:
    """Backward-compatible alias for appending one canonical task log entry."""
    return append_task_log_entry(task_or_record, event, note, timestamp=timestamp)


def create_task_log(
    task_or_record: Any,
    event: Optional[str] = None,
    note: Optional[str] = None,
    *,
    timestamp: Optional[str] = None,
) -> Path:
    """Create a task log and optionally append an initial visible entry."""
    log_path = ensure_task_log(task_or_record)
    if event is None and note is None:
        return log_path
    return append_task_log_entry(
        task_or_record,
        event or "noted",
        note or "",
        timestamp=timestamp,
    )


def append_started_task_log(
    task_or_record: Any, note: str, *, timestamp: Optional[str] = None
) -> Path:
    """Append a visible started entry for one task."""
    return append_task_log_entry(task_or_record, "started", note, timestamp=timestamp)


def append_completed_task_log(
    task_or_record: Any, note: str, *, timestamp: Optional[str] = None
) -> Path:
    """Append a visible completed entry for one task."""
    return append_task_log_entry(task_or_record, "completed", note, timestamp=timestamp)


__all__ = [
    "LOG_HEADER_SUFFIX",
    "ENTRIES_HEADING",
    "ensure_logs_dir",
    "task_log_file_path",
    "log_file_path",
    "list_task_log_files",
    "ensure_task_log",
    "append_task_log_entry",
    "write_task_log",
    "create_task_log",
    "append_started_task_log",
    "append_completed_task_log",
]

"""Canonical schema primitives for Agenda task records.

Task normalization lives here so later file-backed repository logic can rely on
one durable task-record shape without mixing schema concerns into task or DAG
storage code.
"""

import re
from typing import Any, Optional

TASK_ID_PATTERN = re.compile(r"^TASK_(\d+)$")


def task_id_number(task_id: str) -> Optional[int]:
    """Extract the numeric suffix from a canonical TASK id."""
    match = TASK_ID_PATTERN.fullmatch(task_id)
    if match is None:
        return None
    return int(match.group(1))


def _normalize_task_dependencies(task_record: dict[str, Any]) -> list[Any]:
    """Normalize task dependency input into a stable list field."""
    dependencies = task_record.get("dependencies", task_record.get("depends_on"))
    if dependencies is None:
        return []
    if isinstance(dependencies, list):
        return list(dependencies)
    if isinstance(dependencies, tuple):
        return list(dependencies)
    return [dependencies]


def _normalize_task_intent(task_record: dict[str, Any]) -> dict[str, str]:
    """Normalize task intent input into a small stable metadata object.

    Fallbacks stay conservative so generated or noisy task inputs remain
    inspectable instead of silently growing speculative structure:
    - dict-shaped intent keeps only ``kind`` and ``summary``
    - string-like intent becomes an explicit summary
    - missing intent becomes an ``unspecified`` kind with an empty summary
    """

    raw_intent = task_record.get("task_intent", task_record.get("intent"))
    if isinstance(raw_intent, dict):
        kind = str(
            raw_intent.get("kind", raw_intent.get("type", "unspecified"))
        ).strip()
        summary = str(
            raw_intent.get(
                "summary",
                raw_intent.get(
                    "description",
                    raw_intent.get("title", raw_intent.get("intent", "")),
                ),
            )
        ).strip()
        return {
            "kind": kind or "unspecified",
            "summary": summary,
        }

    if raw_intent is None:
        raw_intent = task_record.get("intent_summary")

    if raw_intent is None:
        return {
            "kind": "unspecified",
            "summary": "",
        }

    return {
        "kind": "explicit",
        "summary": str(raw_intent).strip(),
    }


def normalize_task_record(task_record: dict[str, Any]) -> dict[str, Any]:
    """Convert partial task-shaped data into the canonical Agenda schema.

    Fallbacks stay conservative so stub tasks remain explicit:
    - ``deliverable_id`` accepts legacy-like parent aliases but defaults empty
    - ``title`` prefers an explicit title, then legacy ``task``, then the
      first non-empty line of ``description``
    - ``dependencies`` always becomes a list
    - ``status`` defaults to ``ready``
    - ``execution_notes`` and ``created`` become empty strings when missing
    - ``task_intent`` becomes a stable metadata object
    """

    description = str(task_record.get("description", "")).strip()
    title = str(task_record.get("title", task_record.get("task", ""))).strip()
    if not title and description:
        title = description.splitlines()[0].strip()

    return {
        "task_id": str(task_record.get("task_id", "")).strip(),
        "deliverable_id": str(
            task_record.get(
                "deliverable_id",
                task_record.get(
                    "parent_deliverable_id",
                    task_record.get("deliverable", ""),
                ),
            )
        ).strip(),
        "title": title,
        "status": str(task_record.get("status", "ready")).strip() or "ready",
        "task_intent": _normalize_task_intent(task_record),
        "description": description,
        "dependencies": _normalize_task_dependencies(task_record),
        "execution_notes": str(task_record.get("execution_notes", "")).strip(),
        "created": str(task_record.get("created", "")).strip(),
    }


__all__ = [
    "TASK_ID_PATTERN",
    "task_id_number",
    "normalize_task_record",
]

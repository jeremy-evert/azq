"""Shared Agenda lineage helpers for exact task ancestry resolution.

Stage 3 keeps one explicit live policy:
- tasks store ``deliverable_id`` as their direct canonical parent backlink
- goal lineage is resolved exactly through that deliverable link
- task records do not treat a second stored ``goal_id`` as canonical

This module owns the shared seam so Agenda readers and writers do not rebuild
task ancestry through separate ad hoc paths.
"""

from typing import Any

from azq.finis import storage as finis_storage
from azq.formam import storage as formam_storage


def resolve_deliverable_lineage(deliverable_id: str) -> dict[str, Any]:
    """Resolve one exact deliverable and its exact parent goal."""
    canonical_deliverable_id = str(deliverable_id).strip()
    if not canonical_deliverable_id:
        raise ValueError("Task parent deliverable_id is required.")

    deliverable_record = formam_storage.load_deliverable(canonical_deliverable_id)
    if deliverable_record is None:
        raise ValueError(
            "Cannot resolve Agenda lineage: canonical parent deliverable "
            f"{canonical_deliverable_id} does not exist."
        )

    goal_id = str(deliverable_record.get("goal_id", "")).strip()
    if not goal_id:
        raise ValueError(
            "Cannot resolve Agenda lineage: deliverable "
            f"{canonical_deliverable_id} is missing goal_id."
        )

    goal_record = finis_storage.load_goal(goal_id)
    if goal_record is None:
        raise ValueError(
            "Cannot resolve Agenda lineage: canonical parent goal "
            f"{goal_id} for deliverable {canonical_deliverable_id} does not exist."
        )

    return {
        "deliverable_id": canonical_deliverable_id,
        "goal_id": goal_id,
        "deliverable": deliverable_record,
        "goal": goal_record,
    }


def resolve_task_lineage(task_record: dict[str, Any]) -> dict[str, Any]:
    """Resolve exact task ancestry through the canonical deliverable seam."""
    deliverable_id = str(task_record.get("deliverable_id", "")).strip()
    lineage = resolve_deliverable_lineage(deliverable_id)

    return {
        "task_id": str(task_record.get("task_id", "")).strip(),
        "deliverable_id": lineage["deliverable_id"],
        "goal_id": lineage["goal_id"],
        "deliverable": lineage["deliverable"],
        "goal": lineage["goal"],
    }


def apply_task_lineage(task_record: dict[str, Any]) -> dict[str, Any]:
    """Attach computed goal lineage to one canonical task record."""
    record = dict(task_record)
    lineage = resolve_task_lineage(record)
    record["deliverable_id"] = lineage["deliverable_id"]
    record["goal_id"] = lineage["goal_id"]
    return record


__all__ = [
    "resolve_deliverable_lineage",
    "resolve_task_lineage",
    "apply_task_lineage",
]

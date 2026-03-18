"""Thin command-layer writer for initial Formam deliverable creation."""

from datetime import date
from typing import Any, Optional

from azq.formam.deliverable_storage import (
    load_goal_deliverables,
    next_deliverable_id,
    validate_parent_goal,
    write_deliverable,
)
from azq.formam.storage import load_goal_map, write_goal_map

INITIAL_GOAL_MAP_NOTES = (
    "Initial Formam stub map generated from canonical deliverables."
)


def build_stub_deliverable_record(
    goal_record: dict[str, Any], deliverable_id: str, *, created: str
) -> dict[str, Any]:
    """Build one deterministic stub deliverable from validated goal data."""
    goal_id = goal_record["goal_id"]
    goal_title = goal_record["title"]
    goal_description = str(goal_record.get("description", "")).strip()

    if goal_description:
        artifact_description = goal_description
    else:
        artifact_description = (
            f"Stub deliverable for {goal_id}: define the first visible artifact "
            f"boundary for {goal_title}"
        )

    return {
        "deliverable_id": deliverable_id,
        "goal_id": goal_id,
        "title": goal_title,
        "artifact_description": artifact_description,
        "dependencies": [],
        "status": "drafted",
        "created": created,
    }


def build_goal_map_record(
    goal_record: dict[str, Any],
    deliverables: list[dict[str, Any]],
    *,
    created: str,
    existing_map: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build one minimal canonical goal map from current goal deliverables."""
    goal_id = goal_record["goal_id"]
    deliverable_ids = [deliverable["deliverable_id"] for deliverable in deliverables]

    if existing_map is None:
        status = "draft"
        notes = INITIAL_GOAL_MAP_NOTES
        map_created = created
    else:
        status = existing_map.get("status", "draft")
        notes = existing_map.get("notes", INITIAL_GOAL_MAP_NOTES)
        map_created = existing_map.get("created", created)

    return {
        "goal_id": goal_id,
        "deliverable_ids": deliverable_ids,
        "dependency_edges": [],
        "status": status,
        "created": map_created,
        "notes": notes,
    }


def build_form(goal_id: str) -> dict[str, Any]:
    """Create one stub deliverable and refresh its canonical goal map."""
    goal_record = validate_parent_goal(goal_id, active_only=True)
    created = str(date.today())
    deliverable_id = next_deliverable_id()

    deliverable_record = build_stub_deliverable_record(
        goal_record, deliverable_id, created=created
    )
    deliverable_path = write_deliverable(deliverable_record)

    goal_deliverables = load_goal_deliverables(goal_record["goal_id"])
    existing_goal_map = load_goal_map(goal_record["goal_id"])
    goal_map_record = build_goal_map_record(
        goal_record,
        goal_deliverables,
        created=created,
        existing_map=existing_goal_map,
    )
    goal_map_path = write_goal_map(goal_map_record)

    result = {
        "goal": goal_record,
        "deliverable": deliverable_record,
        "goal_map": goal_map_record,
        "deliverable_path": deliverable_path,
        "goal_map_path": goal_map_path,
    }

    print(f"Built {deliverable_id} for {goal_record['goal_id']}")
    print(f"Deliverable: {deliverable_path}")
    print(f"Goal map: {goal_map_path}")
    return result


__all__ = [
    "INITIAL_GOAL_MAP_NOTES",
    "build_stub_deliverable_record",
    "build_goal_map_record",
    "build_form",
]

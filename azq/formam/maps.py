"""Thin command-layer writer for canonical Formam goal maps."""

from datetime import date
from typing import Any, Optional

from azq.formam.storage import (
    derive_goal_map_dependency_edges,
    load_deliverables_for_goal,
    load_goal_map,
    validate_parent_goal,
    write_goal_map,
)

DEFAULT_GOAL_MAP_NOTES = (
    "Canonical Formam goal map generated from current deliverable relationships."
)


def build_goal_map_record(
    goal_record: dict[str, Any],
    deliverables: list[dict[str, Any]],
    *,
    existing_map: Optional[dict[str, Any]] = None,
    created: Optional[str] = None,
) -> dict[str, Any]:
    """Build one canonical goal map record from exact-goal deliverables."""
    map_created = created or str(date.today())
    if existing_map is not None:
        map_created = existing_map.get("created", map_created) or map_created

    return {
        "goal_id": goal_record["goal_id"],
        "deliverable_ids": [
            deliverable["deliverable_id"] for deliverable in deliverables
        ],
        "dependency_edges": derive_goal_map_dependency_edges(deliverables),
        "status": "mapped",
        "created": map_created,
        "notes": (
            existing_map.get("notes", DEFAULT_GOAL_MAP_NOTES)
            if existing_map is not None
            else DEFAULT_GOAL_MAP_NOTES
        ),
    }


def refresh_goal_map(goal_id: str) -> dict[str, Any]:
    """Validate one exact goal and refresh its canonical visible map artifact."""
    goal_record = validate_parent_goal(goal_id)
    deliverables = load_deliverables_for_goal(goal_record["goal_id"])
    existing_map = load_goal_map(goal_record["goal_id"])
    goal_map_record = build_goal_map_record(
        goal_record,
        deliverables,
        existing_map=existing_map,
    )
    goal_map_path = write_goal_map(goal_map_record)

    print(f"Refreshed goal map for {goal_record['goal_id']}")
    print(f"Goal map: {goal_map_path}")

    return {
        "goal": goal_record,
        "deliverables": deliverables,
        "goal_map": goal_map_record,
        "goal_map_path": goal_map_path,
    }


def build_goal_map(goal_id: str) -> dict[str, Any]:
    """Backward-compatible alias for the Formam map command entrypoint."""
    return refresh_goal_map(goal_id)


def form_map(goal_id: str) -> dict[str, Any]:
    """Alternate alias matching the CLI command name."""
    return refresh_goal_map(goal_id)


__all__ = [
    "DEFAULT_GOAL_MAP_NOTES",
    "build_goal_map_record",
    "refresh_goal_map",
    "build_goal_map",
    "form_map",
]

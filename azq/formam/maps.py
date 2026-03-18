"""Thin command-layer writer for canonical Formam goal maps."""

from datetime import date
from typing import Any, Optional

from azq.formam.deliverable_storage import (
    load_deliverables_for_goal,
    validate_parent_goal,
)
from azq.formam.map_storage import (
    load_goal_map,
    write_goal_map,
)

DEFAULT_GOAL_MAP_NOTES = (
    "Canonical Formam goal map generated from current deliverable relationships."
)


def derive_goal_map_dependency_edges(
    deliverables: list[dict[str, Any]],
) -> list[str]:
    """Derive stable human-readable edges from canonical deliverable dependencies.

    Edges stay conservative:
    - only exact deliverable ids present in ``deliverables`` become edges
    - self-references are ignored
    - duplicate edges collapse while preserving deterministic order
    """

    deliverable_ids = {
        str(deliverable.get("deliverable_id", "")).strip()
        for deliverable in deliverables
        if str(deliverable.get("deliverable_id", "")).strip()
    }

    dependency_edges: list[str] = []
    seen_edges: set[str] = set()

    for deliverable in deliverables:
        deliverable_id = str(deliverable.get("deliverable_id", "")).strip()
        if not deliverable_id:
            continue

        dependencies = list(deliverable.get("dependencies", []) or [])
        for dependency in dependencies:
            dependency_id = str(dependency).strip()
            if (
                not dependency_id
                or dependency_id == deliverable_id
                or dependency_id not in deliverable_ids
            ):
                continue

            edge = f"{dependency_id} -> {deliverable_id}"
            if edge in seen_edges:
                continue

            seen_edges.add(edge)
            dependency_edges.append(edge)

    return dependency_edges


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
    "derive_goal_map_dependency_edges",
    "build_goal_map_record",
    "refresh_goal_map",
    "build_goal_map",
    "form_map",
]

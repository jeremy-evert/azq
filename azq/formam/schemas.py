"""Canonical schema primitives for Formam deliverables and goal maps."""

import re
from typing import Any, Optional

ARTIFACT_DESCRIPTION_HEADING = "## Artifact Description"
DELIVERABLES_HEADING = "## Deliverables"
DEPENDENCY_EDGES_HEADING = "## Dependency Edges"
NOTES_HEADING = "## Notes"
DELIVERABLE_ID_PATTERN = re.compile(r"^DELIV_(\d+)$")


def deliverable_id_number(deliverable_id: str) -> Optional[int]:
    """Extract the numeric suffix from a canonical DELIV deliverable id."""
    match = DELIVERABLE_ID_PATTERN.fullmatch(deliverable_id)
    if match is None:
        return None
    return int(match.group(1))


def normalize_deliverable_record(
    deliverable_record: dict[str, Any],
) -> dict[str, Any]:
    """Convert partial deliverable-shaped data into the Stage 2 schema.

    Fallbacks stay conservative so stub deliverables remain explicit rather
    than silently gaining invented structure:
    - ``artifact_description`` becomes an empty string when missing
    - ``dependencies`` always becomes a list
    - ``status`` defaults to ``drafted``
    - ``created`` becomes an empty string when missing
    """

    dependencies = deliverable_record.get("dependencies")
    if dependencies is None:
        canonical_dependencies: list[Any] = []
    elif isinstance(dependencies, list):
        canonical_dependencies = list(dependencies)
    else:
        canonical_dependencies = [dependencies]

    return {
        "deliverable_id": deliverable_record.get("deliverable_id", ""),
        "goal_id": deliverable_record.get("goal_id", ""),
        "title": deliverable_record.get("title", ""),
        "artifact_description": deliverable_record.get("artifact_description", ""),
        "dependencies": canonical_dependencies,
        "status": deliverable_record.get("status", "drafted"),
        "created": deliverable_record.get("created", ""),
    }


def normalize_goal_map_record(goal_map_record: dict[str, Any]) -> dict[str, Any]:
    """Convert partial goal-map-shaped data into the Stage 2 map schema.

    Fallbacks stay conservative so sparse map artifacts remain inspectable
    without inventing structure that does not yet exist:
    - ``deliverable_ids`` always becomes a list
    - ``dependency_edges`` always becomes a list
    - ``status`` defaults to ``draft``
    - ``created`` becomes an empty string when missing
    - ``notes`` becomes an empty string when missing
    """

    deliverable_ids = goal_map_record.get("deliverable_ids")
    if deliverable_ids is None:
        canonical_deliverable_ids: list[Any] = []
    elif isinstance(deliverable_ids, list):
        canonical_deliverable_ids = list(deliverable_ids)
    else:
        canonical_deliverable_ids = [deliverable_ids]

    dependency_edges = goal_map_record.get("dependency_edges")
    if dependency_edges is None:
        canonical_dependency_edges: list[Any] = []
    elif isinstance(dependency_edges, list):
        canonical_dependency_edges = list(dependency_edges)
    else:
        canonical_dependency_edges = [dependency_edges]

    return {
        "goal_id": goal_map_record.get("goal_id", ""),
        "deliverable_ids": canonical_deliverable_ids,
        "dependency_edges": canonical_dependency_edges,
        "status": goal_map_record.get("status", "draft"),
        "created": goal_map_record.get("created", ""),
        "notes": goal_map_record.get("notes", ""),
    }


__all__ = [
    "ARTIFACT_DESCRIPTION_HEADING",
    "DELIVERABLES_HEADING",
    "DEPENDENCY_EDGES_HEADING",
    "NOTES_HEADING",
    "DELIVERABLE_ID_PATTERN",
    "deliverable_id_number",
    "normalize_deliverable_record",
    "normalize_goal_map_record",
]

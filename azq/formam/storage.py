"""Filesystem-backed Formam storage facade.

Stage 2 keeps the shared public storage surface here while path ownership and
schema primitives live in focused sibling modules. Deliverable persistence now
lives in ``deliverable_storage`` and goal-map persistence in ``map_storage``;
this module re-exports both for compatibility.
"""

from pathlib import Path
from typing import Any, Optional

from azq.formam.deliverable_storage import (
    CanonicalGoalValidationError,
    DELIVERABLES_DIR,
    _deliverable_id_number,
    deliverable_from_markdown,
    deliverable_to_markdown,
    ensure_deliverables_dir,
    ensure_form_dirs,
    load_all_deliverables,
    load_deliverable,
    load_deliverables_for_goal,
    load_goal_deliverables,
    normalize_deliverable_record,
    next_deliverable_id,
    parse_deliverable_markdown,
    parse_deliverable_record,
    serialize_deliverable_markdown,
    serialize_deliverable_record,
    validate_canonical_goal,
    validate_parent_goal,
    write_deliverable,
)
from azq.formam.map_storage import (
    goal_map_file_path,
    goal_map_from_markdown,
    goal_map_to_markdown,
    list_goal_map_files,
    load_all_goal_maps,
    write_goal_map as _write_goal_map,
)
from azq.formam.map_storage import (
    load_goal_map as _load_goal_map,
)
from azq.formam.map_storage import (
    parse_goal_map_markdown as _parse_goal_map_markdown,
)
from azq.formam.map_storage import (
    parse_goal_map_record as _parse_goal_map_record,
)
from azq.formam.map_storage import (
    serialize_goal_map_markdown as _serialize_goal_map_markdown,
)
from azq.formam.map_storage import (
    serialize_goal_map_record as _serialize_goal_map_record,
)
from azq.formam.paths import (
    DATA_DIR,
    DELIVERABLE_FILE_GLOB,
    DELIVERABLE_FILE_SUFFIX,
    FORM_DIR,
    MAPS_DIR,
    MAP_FILE_GLOB,
    MAP_FILE_PREFIX,
    MAP_FILE_SUFFIX,
    deliverable_file_path,
    ensure_maps_dir,
    list_deliverable_files,
)
from azq.formam.schemas import (
    ARTIFACT_DESCRIPTION_HEADING,
    DELIVERABLES_HEADING,
    DELIVERABLE_ID_PATTERN,
    DEPENDENCY_EDGES_HEADING,
    NOTES_HEADING,
    normalize_goal_map_record,
)


def _compat_goal_map_record(goal_map_record: dict[str, Any]) -> dict[str, Any]:
    """Preserve the legacy storage facade edge shape for existing callers."""
    record = normalize_goal_map_record(goal_map_record)
    dependency_edges: list[Any] = []

    for edge in record["dependency_edges"]:
        if isinstance(edge, dict):
            from_id = str(edge.get("from", "")).strip()
            to_id = str(edge.get("to", "")).strip()
            if from_id and to_id:
                dependency_edges.append(f"{from_id} -> {to_id}")
                continue
        dependency_edges.append(str(edge))

    record["dependency_edges"] = dependency_edges
    return record


def serialize_goal_map_markdown(goal_map_record: dict[str, Any]) -> str:
    """Serialize a canonical goal-map record into diff-friendly Markdown."""
    return _serialize_goal_map_markdown(goal_map_record)


def serialize_goal_map_record(goal_map_record: dict[str, Any]) -> str:
    """Backward-compatible alias for canonical goal-map Markdown."""
    return _serialize_goal_map_record(goal_map_record)


def goal_map_to_markdown(goal_map_record: dict[str, Any]) -> str:
    """Alias for callers expecting a goal-map-to-Markdown helper."""
    return _serialize_goal_map_markdown(goal_map_record)


def parse_goal_map_markdown(markdown_text: str) -> dict[str, Any]:
    """Parse a canonical Markdown goal-map file back into a record."""
    return _compat_goal_map_record(_parse_goal_map_markdown(markdown_text))


def parse_goal_map_record(markdown_text: str) -> dict[str, Any]:
    """Backward-compatible alias for canonical goal-map Markdown parsing."""
    return _compat_goal_map_record(_parse_goal_map_record(markdown_text))


def goal_map_from_markdown(markdown_text: str) -> dict[str, Any]:
    """Alias for callers expecting a Markdown-to-goal-map helper."""
    return parse_goal_map_markdown(markdown_text)


def load_goal_map(goal_id: str) -> Optional[dict[str, Any]]:
    """Load one canonical goal map record by exact goal id."""
    goal_map_record = _load_goal_map(goal_id)
    if goal_map_record is None:
        return None
    return _compat_goal_map_record(goal_map_record)


def write_goal_map(goal_map_record: dict[str, Any]) -> Path:
    """Write one canonical goal map record to its exact Markdown file."""
    return _write_goal_map(goal_map_record)


__all__ = [
    "DATA_DIR",
    "FORM_DIR",
    "DELIVERABLES_DIR",
    "MAPS_DIR",
    "DELIVERABLE_FILE_SUFFIX",
    "DELIVERABLE_FILE_GLOB",
    "MAP_FILE_PREFIX",
    "MAP_FILE_SUFFIX",
    "MAP_FILE_GLOB",
    "ARTIFACT_DESCRIPTION_HEADING",
    "DELIVERABLES_HEADING",
    "DEPENDENCY_EDGES_HEADING",
    "NOTES_HEADING",
    "DELIVERABLE_ID_PATTERN",
    "ensure_form_dirs",
    "ensure_deliverables_dir",
    "ensure_maps_dir",
    "deliverable_file_path",
    "goal_map_file_path",
    "list_deliverable_files",
    "list_goal_map_files",
    "_deliverable_id_number",
    "normalize_deliverable_record",
    "normalize_goal_map_record",
    "serialize_deliverable_record",
    "serialize_deliverable_markdown",
    "deliverable_to_markdown",
    "serialize_goal_map_record",
    "serialize_goal_map_markdown",
    "goal_map_to_markdown",
    "parse_deliverable_record",
    "parse_deliverable_markdown",
    "deliverable_from_markdown",
    "parse_goal_map_record",
    "parse_goal_map_markdown",
    "goal_map_from_markdown",
    "load_deliverable",
    "load_goal_map",
    "load_all_goal_maps",
    "load_all_deliverables",
    "load_goal_deliverables",
    "load_deliverables_for_goal",
    "CanonicalGoalValidationError",
    "validate_canonical_goal",
    "validate_parent_goal",
    "next_deliverable_id",
    "write_deliverable",
    "write_goal_map",
]

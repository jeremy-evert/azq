"""Filesystem-backed Formam storage facade.

Stage 2 keeps the shared public storage surface here while path ownership and
schema primitives live in focused sibling modules. Deliverable persistence now
lives in ``deliverable_storage`` and is re-exported here for compatibility.
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
    goal_map_file_path,
    list_deliverable_files,
    list_goal_map_files,
)
from azq.formam.schemas import (
    ARTIFACT_DESCRIPTION_HEADING,
    DELIVERABLES_HEADING,
    DELIVERABLE_ID_PATTERN,
    DEPENDENCY_EDGES_HEADING,
    NOTES_HEADING,
    normalize_goal_map_record,
)


def serialize_goal_map_markdown(goal_map_record: dict[str, Any]) -> str:
    """Serialize a canonical goal-map record into diff-friendly Markdown."""
    record = normalize_goal_map_record(goal_map_record)
    lines = [
        f"# Goal Map: {record['goal_id']}",
        "",
        f"- status: {record['status']}",
        f"- created: {record['created']}",
        "",
        DELIVERABLES_HEADING,
        "",
    ]

    deliverable_ids = record["deliverable_ids"]
    if deliverable_ids:
        for item in deliverable_ids:
            lines.append(f"- {item}")
    else:
        lines.append("- []")

    lines.extend(["", DEPENDENCY_EDGES_HEADING, ""])

    dependency_edges = record["dependency_edges"]
    if dependency_edges:
        for item in dependency_edges:
            lines.append(f"- {item}")
    else:
        lines.append("- []")

    lines.extend(["", NOTES_HEADING, ""])

    notes = record["notes"]
    if notes:
        lines.extend(str(notes).splitlines())

    lines.append("")
    return "\n".join(lines)


def serialize_goal_map_record(goal_map_record: dict[str, Any]) -> str:
    """Backward-compatible alias for canonical goal-map Markdown."""
    return serialize_goal_map_markdown(goal_map_record)


def goal_map_to_markdown(goal_map_record: dict[str, Any]) -> str:
    """Alias for callers expecting a goal-map-to-Markdown helper."""
    return serialize_goal_map_markdown(goal_map_record)


def _parse_goal_map_list_section(
    lines: list[str], start_index: int, next_heading: str
) -> tuple[list[str], int]:
    """Parse a simple Markdown bullet-list section used by goal maps."""
    items: list[str] = []
    index = start_index

    while index < len(lines):
        stripped = lines[index].strip()
        if stripped == "":
            index += 1
            continue
        if stripped == next_heading:
            break
        if stripped == "- []":
            index += 1
            continue
        if not stripped.startswith("- "):
            raise ValueError(f"Unrecognized goal map list item: {lines[index]!r}")
        items.append(stripped[2:])
        index += 1

    return items, index


def parse_goal_map_markdown(markdown_text: str) -> dict[str, Any]:
    """Parse a canonical Markdown goal-map file back into a record."""
    lines = markdown_text.splitlines()
    if not lines:
        raise ValueError("Goal map markdown is empty.")

    header = lines[0].strip()
    if not header.startswith("# Goal Map: "):
        raise ValueError(
            "Goal map markdown must start with a '# Goal Map: <goal_id>' header."
        )

    goal_id = header[len("# Goal Map: ") :].strip()
    if not goal_id:
        raise ValueError("Goal map markdown header must include a goal id.")

    metadata: dict[str, str] = {}
    index = 1

    while index < len(lines) and lines[index].strip() == "":
        index += 1

    while index < len(lines):
        stripped = lines[index].strip()
        if stripped == DELIVERABLES_HEADING:
            index += 1
            break
        if stripped == "":
            index += 1
            continue
        if not stripped.startswith("- ") or ":" not in stripped:
            raise ValueError(f"Unrecognized goal map metadata line: {lines[index]!r}")
        field_name, field_value = stripped[2:].split(":", 1)
        metadata[field_name] = field_value.lstrip()
        index += 1

    deliverable_ids, index = _parse_goal_map_list_section(
        lines, index, DEPENDENCY_EDGES_HEADING
    )
    if index >= len(lines) or lines[index].strip() != DEPENDENCY_EDGES_HEADING:
        raise ValueError(
            f"Goal map markdown is missing required {DEPENDENCY_EDGES_HEADING!r} section."
        )

    dependency_edges, index = _parse_goal_map_list_section(
        lines, index + 1, NOTES_HEADING
    )
    if index >= len(lines) or lines[index].strip() != NOTES_HEADING:
        raise ValueError(
            f"Goal map markdown is missing required {NOTES_HEADING!r} section."
        )

    notes_lines = lines[index + 1 :]
    while notes_lines and notes_lines[0].strip() == "":
        notes_lines.pop(0)
    while notes_lines and notes_lines[-1].strip() == "":
        notes_lines.pop()

    return normalize_goal_map_record(
        {
            "goal_id": goal_id,
            "deliverable_ids": deliverable_ids,
            "dependency_edges": dependency_edges,
            "status": metadata.get("status", "draft"),
            "created": metadata.get("created", ""),
            "notes": "\n".join(notes_lines),
        }
    )


def parse_goal_map_record(markdown_text: str) -> dict[str, Any]:
    """Backward-compatible alias for canonical goal-map Markdown parsing."""
    return parse_goal_map_markdown(markdown_text)


def goal_map_from_markdown(markdown_text: str) -> dict[str, Any]:
    """Alias for callers expecting a Markdown-to-goal-map helper."""
    return parse_goal_map_markdown(markdown_text)


def load_goal_map(goal_id: str) -> Optional[dict[str, Any]]:
    """Load one canonical goal map record by exact goal id."""
    goal_map_path = goal_map_file_path(goal_id)
    if not goal_map_path.is_file():
        return None
    return parse_goal_map_markdown(goal_map_path.read_text(encoding="utf-8"))


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

        dependencies = normalize_deliverable_record(deliverable)["dependencies"]
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



def write_goal_map(goal_map_record: dict[str, Any]) -> Path:
    """Write one canonical goal map record to its exact Markdown file."""
    record = normalize_goal_map_record(goal_map_record)
    goal_id = str(record["goal_id"]).strip()
    if not goal_id:
        raise ValueError("Cannot write canonical goal map file without a goal_id.")

    goal_map_path = goal_map_file_path(goal_id)
    ensure_maps_dir()
    goal_map_path.write_text(serialize_goal_map_markdown(record), encoding="utf-8")
    return goal_map_path


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
    "load_all_deliverables",
    "load_goal_deliverables",
    "load_deliverables_for_goal",
    "derive_goal_map_dependency_edges",
    "CanonicalGoalValidationError",
    "validate_canonical_goal",
    "validate_parent_goal",
    "next_deliverable_id",
    "write_deliverable",
    "write_goal_map",
]

"""Canonical storage helpers for Formam goal-map Markdown files."""

from pathlib import Path
from typing import Any, Optional

from azq.formam.paths import DATA_DIR as DEFAULT_DATA_DIR
from azq.formam.paths import DELIVERABLES_DIR as DEFAULT_DELIVERABLES_DIR
from azq.formam.paths import FORM_DIR as DEFAULT_FORM_DIR
from azq.formam.paths import MAPS_DIR as DEFAULT_MAPS_DIR
from azq.formam.schemas import (
    DELIVERABLES_HEADING,
    DEPENDENCY_EDGES_HEADING,
    NOTES_HEADING,
    normalize_goal_map_record,
)

DATA_DIR = DEFAULT_DATA_DIR
FORM_DIR = DEFAULT_FORM_DIR
DELIVERABLES_DIR = DEFAULT_DELIVERABLES_DIR
MAPS_DIR = DEFAULT_MAPS_DIR
MAP_FILE_PREFIX = "GOAL_"
MAP_FILE_SUFFIX = "_MAP.md"


def ensure_form_dirs() -> tuple[Path, Path]:
    """Create the Formam directories owned by this module."""
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    return DELIVERABLES_DIR, MAPS_DIR


def ensure_maps_dir() -> Path:
    """Create the goal-map directory owned by this module."""
    ensure_form_dirs()
    return MAPS_DIR


def goal_map_file_path(goal_id: str) -> Path:
    """Map an exact goal id to its canonical Formam map file path."""
    return MAPS_DIR / f"{MAP_FILE_PREFIX}{goal_id}{MAP_FILE_SUFFIX}"


def list_goal_map_files() -> list[Path]:
    """Return canonical goal map files in stable filename order."""
    if not MAPS_DIR.exists():
        return []

    return sorted(
        path
        for path in MAPS_DIR.glob(f"{MAP_FILE_PREFIX}*{MAP_FILE_SUFFIX}")
        if path.is_file()
    )


def _normalize_goal_map_record(goal_map_record: dict[str, Any]) -> dict[str, Any]:
    """Normalize map-shaped input while preserving sparse Stage 2 behavior."""
    record = dict(goal_map_record)
    if "deliverable_ids" not in record and "deliverables" in record:
        record["deliverable_ids"] = [
            str(deliverable.get("deliverable_id", "")).strip()
            for deliverable in record.get("deliverables", [])
            if str(deliverable.get("deliverable_id", "")).strip()
        ]
    return normalize_goal_map_record(record)


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


def _serialize_dependency_edge(edge: Any) -> str:
    """Render one dependency edge into a stable human-readable Markdown line."""
    if isinstance(edge, dict):
        from_id = str(edge.get("from", "")).strip()
        to_id = str(edge.get("to", "")).strip()
        if from_id and to_id:
            return f"{from_id} -> {to_id}"
    return str(edge).strip()


def _parse_dependency_edge(edge_text: str) -> Any:
    """Parse one dependency edge from a Markdown list item."""
    left, separator, right = edge_text.partition("->")
    if separator:
        from_id = left.strip()
        to_id = right.strip()
        if from_id and to_id:
            return {"from": from_id, "to": to_id}
    return edge_text


def serialize_goal_map_markdown(goal_map_record: dict[str, Any]) -> str:
    """Serialize a canonical goal-map record into diff-friendly Markdown."""
    record = _normalize_goal_map_record(goal_map_record)
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
            lines.append(f"- {_serialize_dependency_edge(item)}")
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

    dependency_edge_lines, index = _parse_goal_map_list_section(
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

    return _normalize_goal_map_record(
        {
            "goal_id": goal_id,
            "deliverable_ids": deliverable_ids,
            "dependency_edges": [
                _parse_dependency_edge(edge_text) for edge_text in dependency_edge_lines
            ],
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


def load_all_goal_maps() -> list[dict[str, Any]]:
    """Load all canonical goal maps in deterministic filename order."""
    goal_maps: list[dict[str, Any]] = []
    for goal_map_path in list_goal_map_files():
        goal_maps.append(parse_goal_map_markdown(goal_map_path.read_text(encoding="utf-8")))
    return goal_maps


def write_goal_map(goal_map_record: dict[str, Any]) -> Path:
    """Write one canonical goal map record to its exact Markdown file."""
    record = _normalize_goal_map_record(goal_map_record)
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
    "MAP_FILE_PREFIX",
    "MAP_FILE_SUFFIX",
    "ensure_form_dirs",
    "ensure_maps_dir",
    "goal_map_file_path",
    "list_goal_map_files",
    "normalize_goal_map_record",
    "serialize_goal_map_record",
    "serialize_goal_map_markdown",
    "goal_map_to_markdown",
    "parse_goal_map_record",
    "parse_goal_map_markdown",
    "goal_map_from_markdown",
    "load_goal_map",
    "load_all_goal_maps",
    "write_goal_map",
]

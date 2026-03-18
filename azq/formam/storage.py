"""Filesystem scaffolding for canonical Formam storage.

Stage 2 introduces Formam as the boundary that owns deliverable and map
storage decisions. This module is intentionally small and import-safe so later
tasks can build on one shared definition of the Formam data locations.
"""

from pathlib import Path
from typing import Any

DATA_DIR = Path("data")
FORM_DIR = DATA_DIR / "form"
DELIVERABLES_DIR = FORM_DIR / "deliverables"
MAPS_DIR = FORM_DIR / "maps"
DELIVERABLE_FILE_SUFFIX = ".md"
DELIVERABLE_FILE_GLOB = f"DELIV_*{DELIVERABLE_FILE_SUFFIX}"
MAP_FILE_PREFIX = "GOAL_"
MAP_FILE_SUFFIX = "_MAP.md"
MAP_FILE_GLOB = f"{MAP_FILE_PREFIX}*{MAP_FILE_SUFFIX}"
ARTIFACT_DESCRIPTION_HEADING = "## Artifact Description"


def ensure_form_dirs() -> tuple[Path, Path]:
    """Create the canonical Formam directories when they do not yet exist."""
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    return DELIVERABLES_DIR, MAPS_DIR


def ensure_deliverables_dir() -> Path:
    """Create the canonical deliverables directory when it does not yet exist."""
    ensure_form_dirs()
    return DELIVERABLES_DIR


def ensure_maps_dir() -> Path:
    """Create the canonical maps directory when it does not yet exist."""
    ensure_form_dirs()
    return MAPS_DIR


def deliverable_file_path(deliverable_id: str) -> Path:
    """Map an exact deliverable id to its canonical Markdown file path."""
    return DELIVERABLES_DIR / f"{deliverable_id}{DELIVERABLE_FILE_SUFFIX}"


def goal_map_file_path(goal_id: str) -> Path:
    """Map an exact goal id to its canonical Formam map file path."""
    return MAPS_DIR / f"{MAP_FILE_PREFIX}{goal_id}{MAP_FILE_SUFFIX}"


def list_deliverable_files() -> list[Path]:
    """Return canonical deliverable files in stable filename order."""
    if not DELIVERABLES_DIR.exists():
        return []

    return sorted(
        path for path in DELIVERABLES_DIR.glob(DELIVERABLE_FILE_GLOB) if path.is_file()
    )


def list_goal_map_files() -> list[Path]:
    """Return canonical goal map files in stable filename order."""
    if not MAPS_DIR.exists():
        return []

    return sorted(path for path in MAPS_DIR.glob(MAP_FILE_GLOB) if path.is_file())


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
def serialize_deliverable_markdown(deliverable_record: dict[str, Any]) -> str:
    """Serialize a canonical deliverable record into diff-friendly Markdown."""
    record = normalize_deliverable_record(deliverable_record)
    lines = [
        f"# {record['deliverable_id']}",
        "",
        f"- goal_id: {record['goal_id']}",
        f"- title: {record['title']}",
        f"- status: {record['status']}",
        f"- created: {record['created']}",
    ]

    dependencies = record["dependencies"]
    if dependencies:
        lines.append("- dependencies:")
        for item in dependencies:
            lines.append(f"  - {item}")
    else:
        lines.append("- dependencies: []")

    lines.extend(["", ARTIFACT_DESCRIPTION_HEADING, ""])

    artifact_description = record["artifact_description"]
    if artifact_description:
        lines.extend(str(artifact_description).splitlines())

    lines.append("")
    return "\n".join(lines)


def serialize_deliverable_record(deliverable_record: dict[str, Any]) -> str:
    """Backward-compatible alias for canonical deliverable Markdown."""
    return serialize_deliverable_markdown(deliverable_record)


def deliverable_to_markdown(deliverable_record: dict[str, Any]) -> str:
    """Alias for callers expecting a deliverable-to-Markdown helper."""
    return serialize_deliverable_markdown(deliverable_record)


def parse_deliverable_markdown(markdown_text: str) -> dict[str, Any]:
    """Parse a canonical Markdown deliverable file back into a record."""
    lines = markdown_text.splitlines()
    if not lines:
        raise ValueError("Deliverable markdown is empty.")

    header = lines[0].strip()
    if not header.startswith("# "):
        raise ValueError(
            "Deliverable markdown must start with a '# <deliverable_id>' header."
        )

    deliverable_id = header[2:].strip()
    if not deliverable_id:
        raise ValueError("Deliverable markdown header must include a deliverable id.")

    metadata: dict[str, str] = {}
    dependencies: list[str] = []
    index = 1

    while index < len(lines) and lines[index].strip() == "":
        index += 1

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped == ARTIFACT_DESCRIPTION_HEADING:
            index += 1
            break

        if stripped == "":
            index += 1
            continue

        if stripped == "- dependencies: []":
            index += 1
            continue

        if stripped == "- dependencies:":
            index += 1
            while index < len(lines):
                dependency_line = lines[index]
                dependency_stripped = dependency_line.strip()
                if dependency_stripped == "":
                    index += 1
                    continue
                if dependency_stripped == ARTIFACT_DESCRIPTION_HEADING:
                    break
                if not dependency_line.startswith("  - "):
                    raise ValueError(
                        "Deliverable markdown dependencies must use '  - <value>'."
                    )
                dependencies.append(dependency_line[4:])
                index += 1
            continue

        if not stripped.startswith("- ") or ":" not in stripped:
            raise ValueError(f"Unrecognized deliverable metadata line: {line!r}")

        field_name, field_value = stripped[2:].split(":", 1)
        metadata[field_name] = field_value.lstrip()
        index += 1

    artifact_description_lines = lines[index:]
    while artifact_description_lines and artifact_description_lines[0].strip() == "":
        artifact_description_lines.pop(0)
    while artifact_description_lines and artifact_description_lines[-1].strip() == "":
        artifact_description_lines.pop()

    return normalize_deliverable_record(
        {
            "deliverable_id": deliverable_id,
            "goal_id": metadata.get("goal_id", ""),
            "title": metadata.get("title", ""),
            "artifact_description": "\n".join(artifact_description_lines),
            "dependencies": dependencies,
            "status": metadata.get("status", "drafted"),
            "created": metadata.get("created", ""),
        }
    )


def parse_deliverable_record(markdown_text: str) -> dict[str, Any]:
    """Backward-compatible alias for canonical deliverable Markdown parsing."""
    return parse_deliverable_markdown(markdown_text)


def deliverable_from_markdown(markdown_text: str) -> dict[str, Any]:
    """Alias for callers expecting a Markdown-to-deliverable helper."""
    return parse_deliverable_markdown(markdown_text)


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
    "ensure_form_dirs",
    "ensure_deliverables_dir",
    "ensure_maps_dir",
    "deliverable_file_path",
    "goal_map_file_path",
    "list_deliverable_files",
    "list_goal_map_files",
    "normalize_deliverable_record",
    "serialize_deliverable_record",
    "serialize_deliverable_markdown",
    "deliverable_to_markdown",
    "parse_deliverable_record",
    "parse_deliverable_markdown",
    "deliverable_from_markdown",
]

"""Canonical storage helpers for Formam deliverable Markdown files."""

import re
from pathlib import Path
from typing import Any, Optional

from azq.finis import storage as finis_storage
from azq.formam.paths import DATA_DIR as DEFAULT_DATA_DIR
from azq.formam.paths import DELIVERABLES_DIR as DEFAULT_DELIVERABLES_DIR
from azq.formam.paths import FORM_DIR as DEFAULT_FORM_DIR
from azq.formam.paths import MAPS_DIR as DEFAULT_MAPS_DIR
from azq.formam.schemas import (
    ARTIFACT_DESCRIPTION_HEADING,
    DELIVERABLE_ID_PATTERN,
    deliverable_id_number,
    normalize_deliverable_record,
)

DATA_DIR = DEFAULT_DATA_DIR
FORM_DIR = DEFAULT_FORM_DIR
DELIVERABLES_DIR = DEFAULT_DELIVERABLES_DIR
MAPS_DIR = DEFAULT_MAPS_DIR
DELIVERABLE_FILE_SUFFIX = ".md"
LEGACY_DELIVERABLE_ID_PATTERN = re.compile(r"^FORM_(\d+)$")


class CanonicalGoalValidationError(ValueError):
    """Raised when a Formam parent goal cannot be validated canonically."""

    def __init__(
        self,
        goal_id: str,
        message: str,
        *,
        code: str,
        active_only: bool = False,
        goal_record: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.goal_id = goal_id
        self.code = code
        self.active_only = active_only
        self.goal_record = goal_record


def _deliverable_id_number(deliverable_id: str) -> Optional[int]:
    """Backward-compatible alias for the shared deliverable id parser."""
    return deliverable_id_number(deliverable_id)


def ensure_form_dirs() -> tuple[Path, Path]:
    """Create the Formam directories owned by this module."""
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    return DELIVERABLES_DIR, MAPS_DIR


def ensure_deliverables_dir() -> Path:
    """Create the deliverables directory owned by this module."""
    ensure_form_dirs()
    return DELIVERABLES_DIR


def deliverable_file_path(deliverable_id: str) -> Path:
    """Map an exact deliverable id to its Markdown file path."""
    return DELIVERABLES_DIR / f"{deliverable_id}{DELIVERABLE_FILE_SUFFIX}"


def list_deliverable_files() -> list[Path]:
    """Return deliverable files in stable filename order.

    Stage 2 now allocates canonical ``DELIV_###`` ids, but this storage layer
    still reads and writes legacy ``FORM_###`` files for compatibility.
    """

    if not DELIVERABLES_DIR.exists():
        return []

    deliverable_paths: list[Path] = []
    for path in DELIVERABLES_DIR.glob(f"*{DELIVERABLE_FILE_SUFFIX}"):
        if not path.is_file():
            continue
        stem = path.stem
        if DELIVERABLE_ID_PATTERN.fullmatch(stem) or LEGACY_DELIVERABLE_ID_PATTERN.fullmatch(
            stem
        ):
            deliverable_paths.append(path)

    return sorted(deliverable_paths)


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


def load_deliverable(deliverable_id: str) -> Optional[dict[str, Any]]:
    """Load one canonical deliverable record by exact deliverable id."""
    deliverable_path = deliverable_file_path(deliverable_id)
    if not deliverable_path.is_file():
        return None
    return parse_deliverable_markdown(deliverable_path.read_text(encoding="utf-8"))


def load_all_deliverables() -> list[dict[str, Any]]:
    """Load all canonical deliverable files in deterministic order."""
    deliverables: list[dict[str, Any]] = []
    for deliverable_path in list_deliverable_files():
        deliverables.append(
            parse_deliverable_markdown(deliverable_path.read_text(encoding="utf-8"))
        )
    return deliverables


def load_goal_deliverables(goal_id: str) -> list[dict[str, Any]]:
    """Load canonical deliverables whose goal_id matches exactly."""
    return [
        deliverable
        for deliverable in load_all_deliverables()
        if deliverable["goal_id"] == goal_id
    ]


def load_deliverables_for_goal(goal_id: str) -> list[dict[str, Any]]:
    """Backward-compatible helper for exact goal_id deliverable lookup."""
    return load_goal_deliverables(goal_id)


def validate_canonical_goal(
    goal_id: str, *, active_only: bool = False
) -> dict[str, Any]:
    """Validate an exact canonical parent goal through the Finis storage layer.

    The ``active_only`` flag is explicit so future command modules can inspect
    or opt into the stricter rule instead of inheriting hidden policy.
    """

    canonical_goal_id = str(goal_id).strip()
    if not canonical_goal_id:
        raise CanonicalGoalValidationError(
            canonical_goal_id,
            "Deliverable parent goal_id is required.",
            code="missing_goal_id",
            active_only=active_only,
        )

    goal_record = finis_storage.load_goal(canonical_goal_id)
    if goal_record is None:
        raise CanonicalGoalValidationError(
            canonical_goal_id,
            f"Cannot create deliverable: canonical parent goal {canonical_goal_id} does not exist.",
            code="missing_goal",
            active_only=active_only,
        )

    if active_only and goal_record.get("status") != "active":
        raise CanonicalGoalValidationError(
            canonical_goal_id,
            f"Cannot create deliverable: canonical parent goal {canonical_goal_id} is not active.",
            code="inactive_goal",
            active_only=True,
            goal_record=goal_record,
        )

    return goal_record


def validate_parent_goal(goal_id: str, *, active_only: bool = False) -> dict[str, Any]:
    """Validate an exact canonical parent goal before any Formam write occurs."""
    return validate_canonical_goal(goal_id, active_only=active_only)


def next_deliverable_id() -> str:
    """Compute the next stable DELIV id from canonical deliverable files."""
    highest_deliverable_number = 0

    for deliverable_path in list_deliverable_files():
        deliverable_number = _deliverable_id_number(deliverable_path.stem)
        if deliverable_number is not None:
            highest_deliverable_number = max(
                highest_deliverable_number, deliverable_number
            )

    return f"DELIV_{highest_deliverable_number + 1:03d}"


def write_deliverable(deliverable_record: dict[str, Any]) -> Path:
    """Write one canonical deliverable record to its exact Markdown file."""
    record = normalize_deliverable_record(deliverable_record)
    deliverable_id = str(record["deliverable_id"]).strip()
    if not (
        DELIVERABLE_ID_PATTERN.fullmatch(deliverable_id)
        or LEGACY_DELIVERABLE_ID_PATTERN.fullmatch(deliverable_id)
    ):
        raise ValueError(
            f"Cannot write canonical deliverable file for invalid deliverable_id {deliverable_id!r}."
        )

    deliverable_path = deliverable_file_path(deliverable_id)
    ensure_deliverables_dir()
    deliverable_path.write_text(
        serialize_deliverable_markdown(record), encoding="utf-8"
    )
    return deliverable_path


__all__ = [
    "CanonicalGoalValidationError",
    "DELIVERABLES_DIR",
    "_deliverable_id_number",
    "deliverable_from_markdown",
    "deliverable_to_markdown",
    "ensure_form_dirs",
    "ensure_deliverables_dir",
    "load_all_deliverables",
    "load_deliverable",
    "load_deliverables_for_goal",
    "load_goal_deliverables",
    "normalize_deliverable_record",
    "next_deliverable_id",
    "parse_deliverable_markdown",
    "parse_deliverable_record",
    "serialize_deliverable_markdown",
    "serialize_deliverable_record",
    "validate_canonical_goal",
    "validate_parent_goal",
    "write_deliverable",
]

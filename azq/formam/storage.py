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
    "ensure_form_dirs",
    "ensure_deliverables_dir",
    "ensure_maps_dir",
    "deliverable_file_path",
    "goal_map_file_path",
    "list_deliverable_files",
    "list_goal_map_files",
    "normalize_deliverable_record",
]

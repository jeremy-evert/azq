"""Filesystem scaffolding for canonical Finis goal storage.

Stage 1 moves Finis persistence toward one goal record per file under
``data/finis/goals/`` while preserving ``data/finis/goals.json`` as a legacy
input during migration. This module currently owns the shared path decisions,
basic filesystem helpers, and legacy-to-canonical goal normalization used by
later tasks.
"""

from pathlib import Path
from typing import Any

DATA_DIR = Path("data")
FINIS_DIR = DATA_DIR / "finis"
GOALS_DIR = FINIS_DIR / "goals"
LEGACY_GOALS_FILE = FINIS_DIR / "goals.json"
GOAL_FILE_PREFIX = "FINIS_"
GOAL_FILE_SUFFIX = ".md"
GOAL_FILE_GLOB = f"{GOAL_FILE_PREFIX}*{GOAL_FILE_SUFFIX}"


def ensure_goals_dir() -> Path:
    """Create the canonical goals directory when it does not yet exist."""
    GOALS_DIR.mkdir(parents=True, exist_ok=True)
    return GOALS_DIR


def list_goal_files() -> list[Path]:
    """Return canonical goal files in stable filename order."""
    if not GOALS_DIR.exists():
        return []

    return sorted(path for path in GOALS_DIR.glob(GOAL_FILE_GLOB) if path.is_file())


def goal_file_path(goal_id: str) -> Path:
    """Map an exact goal id to its canonical Markdown file path."""
    return GOALS_DIR / f"{goal_id}{GOAL_FILE_SUFFIX}"


def normalize_goal_record(legacy_goal: dict[str, Any]) -> dict[str, Any]:
    """Convert a legacy JSON-shaped goal record into the Stage 1 schema.

    Fallbacks are intentionally conservative so migration preserves historical
    values instead of inventing cleaned replacements:
    - ``title`` prefers an existing canonical value, then legacy ``goal``
    - missing ``created`` and ``description`` become empty strings
    - missing ``derived_from`` becomes an empty list
    """

    derived_from = legacy_goal.get("derived_from")
    if derived_from is None:
        canonical_derived_from: list[Any] = []
    elif isinstance(derived_from, list):
        canonical_derived_from = list(derived_from)
    else:
        canonical_derived_from = [derived_from]

    return {
        "goal_id": legacy_goal.get("goal_id", ""),
        "title": legacy_goal.get("title", legacy_goal.get("goal", "")),
        "status": legacy_goal.get("status", "active"),
        "created": legacy_goal.get("created", ""),
        "description": legacy_goal.get("description", ""),
        "derived_from": canonical_derived_from,
    }


__all__ = [
    "DATA_DIR",
    "FINIS_DIR",
    "GOALS_DIR",
    "LEGACY_GOALS_FILE",
    "GOAL_FILE_PREFIX",
    "GOAL_FILE_SUFFIX",
    "GOAL_FILE_GLOB",
    "ensure_goals_dir",
    "list_goal_files",
    "goal_file_path",
    "normalize_goal_record",
]

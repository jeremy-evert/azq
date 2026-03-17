"""Filesystem scaffolding for canonical Finis goal storage.

Stage 1 moves Finis persistence toward one goal record per file under
``data/finis/goals/`` while preserving ``data/finis/goals.json`` as a legacy
input during migration. This module currently owns only the shared path
decisions and basic filesystem helpers required for later tasks.
"""

from pathlib import Path

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
]

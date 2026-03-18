"""Filesystem-backed Agenda storage facade.

Stage 3 starts with a single visible storage boundary for Agenda so narrower
task, DAG, and log storage modules can grow behind this facade later without
changing the package import surface.
"""

from pathlib import Path

DATA_DIR = Path("data")
AGENDA_DIR = DATA_DIR / "agenda"
TASKS_DIR = AGENDA_DIR / "tasks"
DAGS_DIR = AGENDA_DIR / "dags"
LOGS_DIR = AGENDA_DIR / "logs"


def ensure_tasks_dir() -> Path:
    """Create the Agenda tasks directory when it does not yet exist."""
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    return TASKS_DIR


def ensure_dags_dir() -> Path:
    """Create the Agenda DAGs directory when it does not yet exist."""
    DAGS_DIR.mkdir(parents=True, exist_ok=True)
    return DAGS_DIR


def ensure_logs_dir() -> Path:
    """Create the Agenda logs directory when it does not yet exist."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return LOGS_DIR


def ensure_agenda_dirs() -> tuple[Path, Path, Path]:
    """Create the canonical Agenda storage directories."""
    return (
        ensure_tasks_dir(),
        ensure_dags_dir(),
        ensure_logs_dir(),
    )


__all__ = [
    "DATA_DIR",
    "AGENDA_DIR",
    "TASKS_DIR",
    "DAGS_DIR",
    "LOGS_DIR",
    "ensure_agenda_dirs",
    "ensure_tasks_dir",
    "ensure_dags_dir",
    "ensure_logs_dir",
]

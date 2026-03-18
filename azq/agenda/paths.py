"""Canonical filesystem paths for Agenda task, DAG, and log artifacts."""

from pathlib import Path

DATA_DIR = Path("data")
AGENDA_DIR = DATA_DIR / "agenda"
TASKS_DIR = AGENDA_DIR / "tasks"
DAGS_DIR = AGENDA_DIR / "dags"
LOGS_DIR = AGENDA_DIR / "logs"
TASK_FILE_PREFIX = "TASK_"
TASK_FILE_SUFFIX = ".md"
TASK_FILE_GLOB = f"{TASK_FILE_PREFIX}*{TASK_FILE_SUFFIX}"
DAG_FILE_PREFIX = "GOAL_"
DAG_FILE_SUFFIX = "_DAG.json"
DAG_FILE_GLOB = f"{DAG_FILE_PREFIX}*{DAG_FILE_SUFFIX}"
TASK_LOG_FILE_SUFFIX = "_LOG.md"


def ensure_agenda_dirs() -> tuple[Path, Path, Path]:
    """Create the canonical Agenda directories when they do not yet exist."""
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    DAGS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return TASKS_DIR, DAGS_DIR, LOGS_DIR


def ensure_tasks_dir() -> Path:
    """Create the canonical tasks directory when it does not yet exist."""
    ensure_agenda_dirs()
    return TASKS_DIR


def ensure_dags_dir() -> Path:
    """Create the canonical DAGs directory when it does not yet exist."""
    ensure_agenda_dirs()
    return DAGS_DIR


def ensure_logs_dir() -> Path:
    """Create the canonical task logs directory when it does not yet exist."""
    ensure_agenda_dirs()
    return LOGS_DIR


def task_file_path(task_id: str) -> Path:
    """Map an exact task id to its canonical Markdown task record path."""
    return TASKS_DIR / f"{task_id}{TASK_FILE_SUFFIX}"


def dag_file_path(goal_id: str) -> Path:
    """Map an exact goal id to its canonical DAG artifact path."""
    return DAGS_DIR / f"{DAG_FILE_PREFIX}{goal_id}{DAG_FILE_SUFFIX}"


def task_log_file_path(task_id: str) -> Path:
    """Map an exact task id to its canonical task log path."""
    return LOGS_DIR / f"{task_id}{TASK_LOG_FILE_SUFFIX}"


def list_task_files() -> list[Path]:
    """Return canonical task record files in stable filename order."""
    if not TASKS_DIR.exists():
        return []

    return sorted(path for path in TASKS_DIR.glob(TASK_FILE_GLOB) if path.is_file())


def list_dag_files() -> list[Path]:
    """Return canonical DAG artifact files in stable filename order."""
    if not DAGS_DIR.exists():
        return []

    return sorted(path for path in DAGS_DIR.glob(DAG_FILE_GLOB) if path.is_file())


__all__ = [
    "DATA_DIR",
    "AGENDA_DIR",
    "TASKS_DIR",
    "DAGS_DIR",
    "LOGS_DIR",
    "TASK_FILE_PREFIX",
    "TASK_FILE_SUFFIX",
    "TASK_FILE_GLOB",
    "DAG_FILE_PREFIX",
    "DAG_FILE_SUFFIX",
    "DAG_FILE_GLOB",
    "TASK_LOG_FILE_SUFFIX",
    "ensure_agenda_dirs",
    "ensure_tasks_dir",
    "ensure_dags_dir",
    "ensure_logs_dir",
    "task_file_path",
    "dag_file_path",
    "task_log_file_path",
    "list_task_files",
    "list_dag_files",
]

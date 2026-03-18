"""Filesystem-backed Agenda storage facade.

Stage 3 starts with a single visible storage boundary for Agenda so narrower
task, DAG, and log storage modules can grow behind this facade later without
changing the package import surface. Canonical path ownership lives in
``azq.agenda.paths`` and is re-exported here where useful.
"""

from azq.agenda.paths import (
    AGENDA_DIR,
    DAGS_DIR,
    DAG_FILE_PREFIX,
    DAG_FILE_SUFFIX,
    DATA_DIR,
    LOGS_DIR,
    TASKS_DIR,
    TASK_FILE_GLOB,
    TASK_FILE_SUFFIX,
    TASK_LOG_FILE_SUFFIX,
    dag_file_path,
    ensure_agenda_dirs,
    ensure_dags_dir,
    ensure_logs_dir,
    ensure_tasks_dir,
    list_task_files,
    task_file_path,
    task_log_file_path,
)


__all__ = [
    "DATA_DIR",
    "AGENDA_DIR",
    "TASKS_DIR",
    "DAGS_DIR",
    "LOGS_DIR",
    "TASK_FILE_SUFFIX",
    "TASK_FILE_GLOB",
    "DAG_FILE_PREFIX",
    "DAG_FILE_SUFFIX",
    "TASK_LOG_FILE_SUFFIX",
    "ensure_agenda_dirs",
    "ensure_tasks_dir",
    "ensure_dags_dir",
    "ensure_logs_dir",
    "task_file_path",
    "dag_file_path",
    "task_log_file_path",
    "list_task_files",
]

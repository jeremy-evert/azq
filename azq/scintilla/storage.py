"""Shared filesystem helpers for canonical Scintilla storage.

This module owns the current on-disk Scintilla layout under
``data/scintilla/`` and provides one seam for exact spark artifact discovery.
Stage 3 Wave D keeps the existing CLI surface while reducing duplicated path
logic across capture, transcription, spark listing, spark inspection, search,
and destructive delete flows.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path("data")
SCINTILLA_DIR = DATA_DIR / "scintilla"
AUDIO_DIR = SCINTILLA_DIR / "audio"
TRANSCRIPTS_DIR = SCINTILLA_DIR / "transcripts"
SPARKS_DIR = SCINTILLA_DIR / "sparks"
SPARK_FILE_SUFFIX = ".json"
SPARK_FILE_GLOB = f"*{SPARK_FILE_SUFFIX}"


def ensure_scintilla_dirs() -> Path:
    """Create the canonical Scintilla directories when absent."""
    for directory in (AUDIO_DIR, TRANSCRIPTS_DIR, SPARKS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    return SCINTILLA_DIR


def ensure_scintilla_directories() -> Path:
    """Backward-compatible alias for callers expecting a longer helper name."""
    return ensure_scintilla_dirs()


def ensure_directories() -> Path:
    """Generic alias for the canonical Scintilla directory scaffold helper."""
    return ensure_scintilla_dirs()


def audio_file_path(spark_id: str) -> Path:
    """Map an exact spark id to its canonical audio artifact path."""
    return AUDIO_DIR / f"{spark_id}.wav"


def transcript_file_path(spark_id: str) -> Path:
    """Map an exact spark id to its canonical transcript artifact path."""
    return TRANSCRIPTS_DIR / f"{spark_id}.txt"


def spark_file_path(spark_id: str) -> Path:
    """Map an exact spark id to its canonical spark artifact path."""
    return SPARKS_DIR / f"{spark_id}{SPARK_FILE_SUFFIX}"


def spark_artifact_paths(spark_id: str) -> dict[str, Path]:
    """Return the canonical artifact bundle for one exact spark id."""
    return {
        "audio": audio_file_path(spark_id),
        "transcript": transcript_file_path(spark_id),
        "sparks": spark_file_path(spark_id),
    }


def allocate_spark_id() -> str:
    """Allocate a new spark id without overwriting an existing bundle."""
    ensure_scintilla_dirs()

    base_id = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    spark_id = base_id
    suffix = 1

    while any(path.exists() for path in spark_artifact_paths(spark_id).values()):
        spark_id = f"{base_id}_{suffix:02d}"
        suffix += 1

    return spark_id


def list_spark_files() -> list[Path]:
    """Return canonical spark files in stable filename order."""
    if not SPARKS_DIR.exists():
        return []

    return sorted(path for path in SPARKS_DIR.glob(SPARK_FILE_GLOB) if path.is_file())


def load_spark_file(spark_file: Path) -> list[dict[str, Any]]:
    """Load one spark artifact file and return its JSON payload."""
    payload = json.loads(spark_file.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Spark artifact {spark_file} must contain a list.")
    return payload


def load_spark_artifact(spark_id: str) -> Optional[list[dict[str, Any]]]:
    """Load the exact spark artifact for one spark id when present."""
    spark_file = spark_file_path(spark_id)
    if not spark_file.is_file():
        return None
    return load_spark_file(spark_file)


__all__ = [
    "DATA_DIR",
    "SCINTILLA_DIR",
    "AUDIO_DIR",
    "TRANSCRIPTS_DIR",
    "SPARKS_DIR",
    "SPARK_FILE_SUFFIX",
    "SPARK_FILE_GLOB",
    "ensure_scintilla_dirs",
    "ensure_scintilla_directories",
    "ensure_directories",
    "audio_file_path",
    "transcript_file_path",
    "spark_file_path",
    "spark_artifact_paths",
    "allocate_spark_id",
    "list_spark_files",
    "load_spark_file",
    "load_spark_artifact",
]

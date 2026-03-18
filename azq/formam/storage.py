"""Filesystem scaffolding for canonical Formam storage.

Stage 2 introduces Formam as the boundary that owns deliverable and map
storage decisions. This module is intentionally small and import-safe so later
tasks can build on one shared definition of the Formam data locations.
"""

from pathlib import Path

DATA_DIR = Path("data")
FORM_DIR = DATA_DIR / "form"
DELIVERABLES_DIR = FORM_DIR / "deliverables"
MAPS_DIR = FORM_DIR / "maps"


def ensure_form_dirs() -> tuple[Path, Path]:
    """Create the canonical Formam directories when they do not yet exist."""
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    return DELIVERABLES_DIR, MAPS_DIR


__all__ = [
    "DATA_DIR",
    "FORM_DIR",
    "DELIVERABLES_DIR",
    "MAPS_DIR",
    "ensure_form_dirs",
]

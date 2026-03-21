"""Filesystem scaffolding for canonical Finis goal storage.

Stage 1 moves Finis persistence toward one goal record per file under
``data/finis/goals/`` while preserving ``data/finis/goals.json`` as a legacy
input during migration. This module currently owns the shared path decisions,
basic filesystem helpers, and legacy-to-canonical goal normalization used by
later tasks.
"""

import json
from pathlib import Path
import re
from typing import Any, Optional

DATA_DIR = Path("data")
FINIS_DIR = DATA_DIR / "finis"
GOALS_DIR = FINIS_DIR / "goals"
REVIEWS_DIR = FINIS_DIR / "reviews"
LEGACY_GOALS_FILE = FINIS_DIR / "goals.json"
GOAL_FILE_PREFIX = "FINIS_"
GOAL_FILE_SUFFIX = ".md"
GOAL_FILE_GLOB = f"{GOAL_FILE_PREFIX}*{GOAL_FILE_SUFFIX}"
REVIEW_FILE_SUFFIX = ".json"
REVIEW_FILE_GLOB = f"*{REVIEW_FILE_SUFFIX}"
DESCRIPTION_HEADING = "## Description"
GOAL_ID_PATTERN = re.compile(rf"^{GOAL_FILE_PREFIX}(\d+)$")


class LegacyGoalsError(ValueError):
    """Raised when legacy goals.json cannot be read as migration input."""


def ensure_goals_dir() -> Path:
    """Create the canonical goals directory when it does not yet exist."""
    GOALS_DIR.mkdir(parents=True, exist_ok=True)
    return GOALS_DIR


def ensure_reviews_dir() -> Path:
    """Create the Finis reviews directory when it does not yet exist."""
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    return REVIEWS_DIR


def list_goal_files() -> list[Path]:
    """Return canonical goal files in stable filename order."""
    if not GOALS_DIR.exists():
        return []

    return sorted(path for path in GOALS_DIR.glob(GOAL_FILE_GLOB) if path.is_file())


def list_review_files() -> list[Path]:
    """Return Finis review artifact files in stable filename order."""
    if not REVIEWS_DIR.exists():
        return []

    return sorted(
        path for path in REVIEWS_DIR.glob(REVIEW_FILE_GLOB) if path.is_file()
    )


def goal_file_path(goal_id: str) -> Path:
    """Map an exact goal id to its canonical Markdown file path."""
    return GOALS_DIR / f"{goal_id}{GOAL_FILE_SUFFIX}"


def review_file_path(review_id: str) -> Path:
    """Map an exact review id to its canonical Finis review file path."""
    return REVIEWS_DIR / f"{str(review_id).strip()}{REVIEW_FILE_SUFFIX}"


def _goal_id_number(goal_id: str) -> Optional[int]:
    """Extract the numeric suffix from a canonical FINIS goal id."""
    match = GOAL_ID_PATTERN.fullmatch(goal_id)
    if match is None:
        return None
    return int(match.group(1))


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


def normalize_review_record(review_record: dict[str, Any]) -> dict[str, Any]:
    """Normalize one Finis review record into the Wave A review schema.

    Wave A keeps the review contract intentionally small so review state can be
    made durable without redesigning canonical goal storage.
    """

    return {
        "review_id": str(review_record.get("review_id", "")).strip(),
        "spark_source": str(review_record.get("spark_source", "")).strip(),
        "raw_spark_text": str(review_record.get("raw_spark_text", "")),
        "candidate_goal_text": str(review_record.get("candidate_goal_text", "")),
        "human_revision_text": str(review_record.get("human_revision_text", "")),
        "review_status": str(review_record.get("review_status", "pending")).strip() or "pending",
        "accepted_goal_id": str(review_record.get("accepted_goal_id", "")).strip(),
    }


def parse_legacy_goals_json(
    raw_text: str, *, source: Path = LEGACY_GOALS_FILE
) -> list[dict[str, Any]]:
    """Parse legacy goals.json text into normalized Stage 1 goal records."""
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise LegacyGoalsError(
            f"Legacy goals JSON at {source} is malformed: {exc.msg} "
            f"(line {exc.lineno}, column {exc.colno})."
        ) from exc

    if not isinstance(parsed, list):
        raise LegacyGoalsError(
            f"Legacy goals JSON at {source} must contain a top-level list."
        )

    normalized_goals: list[dict[str, Any]] = []
    for index, item in enumerate(parsed):
        if not isinstance(item, dict):
            raise LegacyGoalsError(
                f"Legacy goals JSON at {source} contains a non-object record at "
                f"index {index}."
            )
        normalized_goals.append(normalize_goal_record(item))

    return normalized_goals


def load_legacy_goals() -> list[dict[str, Any]]:
    """Load legacy goals.json as migration input only.

    Missing legacy storage returns an empty list so callers can distinguish
    "no legacy data present" from parse failures without treating JSON as the
    canonical store.
    """
    if not LEGACY_GOALS_FILE.is_file():
        return []

    return parse_legacy_goals_json(
        LEGACY_GOALS_FILE.read_text(encoding="utf-8"), source=LEGACY_GOALS_FILE
    )


def serialize_goal_markdown(goal_record: dict[str, Any]) -> str:
    """Serialize a canonical goal record into a diff-friendly Markdown file."""
    record = normalize_goal_record(goal_record)
    lines = [
        f"# {record['goal_id']}",
        "",
        f"- title: {record['title']}",
        f"- status: {record['status']}",
        f"- created: {record['created']}",
    ]

    derived_from = record["derived_from"]
    if derived_from:
        lines.append("- derived_from:")
        for item in derived_from:
            lines.append(f"  - {item}")
    else:
        lines.append("- derived_from: []")

    lines.extend(["", DESCRIPTION_HEADING, ""])

    description = record["description"]
    if description:
        lines.extend(str(description).splitlines())

    lines.append("")
    return "\n".join(lines)


def serialize_review_record(review_record: dict[str, Any]) -> str:
    """Serialize one normalized Finis review record into JSON text."""
    return json.dumps(normalize_review_record(review_record), indent=2)


def serialize_goal_record(goal_record: dict[str, Any]) -> str:
    """Backward-compatible alias for canonical goal Markdown serialization."""
    return serialize_goal_markdown(goal_record)


def goal_to_markdown(goal_record: dict[str, Any]) -> str:
    """Alias for callers expecting a goal-to-Markdown helper."""
    return serialize_goal_markdown(goal_record)


def parse_goal_markdown(markdown_text: str) -> dict[str, Any]:
    """Parse a canonical Markdown goal file back into a goal record."""
    lines = markdown_text.splitlines()
    if not lines:
        raise ValueError("Goal markdown is empty.")

    header = lines[0].strip()
    if not header.startswith("# "):
        raise ValueError("Goal markdown must start with a '# <goal_id>' header.")

    goal_id = header[2:].strip()
    if not goal_id:
        raise ValueError("Goal markdown header must include a goal id.")

    metadata: dict[str, str] = {}
    derived_from: list[str] = []
    index = 1

    while index < len(lines) and lines[index].strip() == "":
        index += 1

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped == DESCRIPTION_HEADING:
            index += 1
            break

        if stripped == "":
            index += 1
            continue

        if stripped == "- derived_from: []":
            index += 1
            continue

        if stripped == "- derived_from:":
            index += 1
            while index < len(lines):
                derived_line = lines[index]
                derived_stripped = derived_line.strip()
                if derived_stripped == "":
                    index += 1
                    continue
                if derived_stripped == DESCRIPTION_HEADING:
                    break
                if not derived_line.startswith("  - "):
                    raise ValueError(
                        "Goal markdown derived_from items must use '  - <value>'."
                    )
                derived_from.append(derived_line[4:])
                index += 1
            continue

        if not stripped.startswith("- ") or ":" not in stripped:
            raise ValueError(f"Unrecognized goal metadata line: {line!r}")

        field_name, field_value = stripped[2:].split(":", 1)
        metadata[field_name] = field_value.lstrip()
        index += 1

    description_lines = lines[index:]
    while description_lines and description_lines[0].strip() == "":
        description_lines.pop(0)
    while description_lines and description_lines[-1].strip() == "":
        description_lines.pop()

    return normalize_goal_record(
        {
            "goal_id": goal_id,
            "title": metadata.get("title", ""),
            "status": metadata.get("status", "active"),
            "created": metadata.get("created", ""),
            "description": "\n".join(description_lines),
            "derived_from": derived_from,
        }
    )


def parse_review_record(review_text: str) -> dict[str, Any]:
    """Parse one Finis review artifact into the normalized Wave A schema."""
    try:
        parsed = json.loads(review_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Finis review artifact is malformed JSON: "
            f"{exc.msg} (line {exc.lineno}, column {exc.colno})."
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError("Finis review artifact must contain a top-level object.")

    return normalize_review_record(parsed)


def parse_goal_record(markdown_text: str) -> dict[str, Any]:
    """Backward-compatible alias for canonical goal Markdown parsing."""
    return parse_goal_markdown(markdown_text)


def goal_from_markdown(markdown_text: str) -> dict[str, Any]:
    """Alias for callers expecting a Markdown-to-goal helper."""
    return parse_goal_markdown(markdown_text)


def load_goal(goal_id: str) -> Optional[dict[str, Any]]:
    """Load one canonical goal record by exact goal id."""
    goal_path = goal_file_path(goal_id)
    if not goal_path.is_file():
        return None
    return parse_goal_markdown(goal_path.read_text(encoding="utf-8"))


def load_review(review_id: str) -> Optional[dict[str, Any]]:
    """Load one Finis review record by exact review id."""
    review_path = review_file_path(review_id)
    if not review_path.is_file():
        return None
    return parse_review_record(review_path.read_text(encoding="utf-8"))


def load_all_goals(*, migrate_legacy: bool = False) -> list[dict[str, Any]]:
    """Load all canonical goal files in deterministic order.

    When ``migrate_legacy`` is true, run the Stage 1 one-way migration trigger
    first so callers read from canonical files even when legacy JSON still
    needs to be materialized on disk.
    """
    if migrate_legacy:
        ensure_canonical_goals_migrated()

    goals: list[dict[str, Any]] = []
    for goal_path in list_goal_files():
        goals.append(parse_goal_markdown(goal_path.read_text(encoding="utf-8")))
    return goals


def load_all_reviews() -> list[dict[str, Any]]:
    """Load all Finis review records in deterministic file order."""
    reviews: list[dict[str, Any]] = []
    for review_path in list_review_files():
        reviews.append(parse_review_record(review_path.read_text(encoding="utf-8")))
    return reviews


def next_goal_id() -> str:
    """Compute the next stable FINIS id from canonical goal files."""
    highest_goal_number = 0

    for goal_path in list_goal_files():
        goal_number = _goal_id_number(goal_path.stem)
        if goal_number is not None:
            highest_goal_number = max(highest_goal_number, goal_number)

    return f"{GOAL_FILE_PREFIX}{highest_goal_number + 1:03d}"


def write_goal(goal_record: dict[str, Any]) -> Path:
    """Write one canonical goal record to its exact Markdown file."""
    record = normalize_goal_record(goal_record)
    goal_id = str(record["goal_id"]).strip()
    if not GOAL_ID_PATTERN.fullmatch(goal_id):
        raise LegacyGoalsError(
            f"Cannot write canonical goal file for invalid goal_id {goal_id!r}."
        )

    goal_path = goal_file_path(goal_id)
    ensure_goals_dir()
    goal_path.write_text(serialize_goal_markdown(record), encoding="utf-8")
    return goal_path


def write_review(review_record: dict[str, Any]) -> Path:
    """Write one normalized Finis review record to its exact JSON file."""
    record = normalize_review_record(review_record)
    review_id = record["review_id"]
    if not review_id:
        raise ValueError("Cannot write Finis review artifact without a review_id.")

    review_path = review_file_path(review_id)
    ensure_reviews_dir()
    review_path.write_text(serialize_review_record(record), encoding="utf-8")
    return review_path


def migrate_legacy_goals() -> dict[str, int]:
    """Migrate legacy JSON goals into canonical Markdown goal files.

    Migration is intentionally one-way and additive:
    - reads legacy state only through the dedicated legacy reader
    - preserves each existing ``goal_id`` exactly
    - writes only missing canonical files to avoid duplicate migrated records
    """

    legacy_goals = load_legacy_goals()
    migrated = 0
    skipped = 0

    for legacy_goal in legacy_goals:
        normalized_goal = normalize_goal_record(legacy_goal)
        goal_id = str(normalized_goal["goal_id"]).strip()
        if not GOAL_ID_PATTERN.fullmatch(goal_id):
            raise LegacyGoalsError(
                f"Legacy goal record is missing a valid canonical goal_id: {goal_id!r}."
            )

        goal_path = goal_file_path(goal_id)
        if goal_path.exists():
            skipped += 1
            continue

        write_goal(normalized_goal)
        migrated += 1

    return {
        "legacy_records": len(legacy_goals),
        "migrated": migrated,
        "skipped": skipped,
    }


def ensure_canonical_goals_migrated() -> dict[str, Any]:
    """Run the one canonical legacy-to-files migration path when needed.

    This is the Stage 1 automatic trigger used before active Finis commands.
    It remains inspectable by returning a summary with an explicit ``triggered``
    flag instead of silently mutating storage state.
    """

    legacy_goals = load_legacy_goals()
    if not legacy_goals:
        return {
            "triggered": False,
            "legacy_records": 0,
            "migrated": 0,
            "skipped": 0,
        }

    missing_goal_ids: list[str] = []
    for legacy_goal in legacy_goals:
        normalized_goal = normalize_goal_record(legacy_goal)
        goal_id = str(normalized_goal["goal_id"]).strip()
        if not GOAL_ID_PATTERN.fullmatch(goal_id):
            raise LegacyGoalsError(
                f"Legacy goal record is missing a valid canonical goal_id: {goal_id!r}."
            )
        if not goal_file_path(goal_id).exists():
            missing_goal_ids.append(goal_id)

    if not missing_goal_ids:
        return {
            "triggered": False,
            "legacy_records": len(legacy_goals),
            "migrated": 0,
            "skipped": len(legacy_goals),
        }

    migration_result = migrate_legacy_goals()
    migration_result["triggered"] = True
    return migration_result


__all__ = [
    "DATA_DIR",
    "FINIS_DIR",
    "GOALS_DIR",
    "REVIEWS_DIR",
    "LEGACY_GOALS_FILE",
    "GOAL_FILE_PREFIX",
    "GOAL_FILE_SUFFIX",
    "GOAL_FILE_GLOB",
    "REVIEW_FILE_SUFFIX",
    "REVIEW_FILE_GLOB",
    "DESCRIPTION_HEADING",
    "GOAL_ID_PATTERN",
    "LegacyGoalsError",
    "ensure_goals_dir",
    "ensure_reviews_dir",
    "list_goal_files",
    "list_review_files",
    "goal_file_path",
    "review_file_path",
    "normalize_goal_record",
    "normalize_review_record",
    "parse_legacy_goals_json",
    "load_legacy_goals",
    "serialize_goal_record",
    "serialize_goal_markdown",
    "serialize_review_record",
    "goal_to_markdown",
    "parse_goal_record",
    "parse_goal_markdown",
    "parse_review_record",
    "goal_from_markdown",
    "load_goal",
    "load_review",
    "load_all_goals",
    "load_all_reviews",
    "next_goal_id",
    "write_goal",
    "write_review",
    "migrate_legacy_goals",
    "ensure_canonical_goals_migrated",
]

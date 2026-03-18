"""Thin presentation helpers for canonical Formam deliverable listings."""

from typing import Any, Optional

from azq.formam import storage

NO_DELIVERABLES_MESSAGE = "No deliverables defined."
DELIVERABLE_NOT_FOUND_MESSAGE = "Deliverable not found for exact deliverable_id:"


def load_all_deliverables() -> list[dict[str, Any]]:
    """Load canonical deliverables through the shared Formam storage layer."""
    return storage.load_all_deliverables()


def load_deliverable(deliverable_id: str) -> Optional[dict[str, Any]]:
    """Load one canonical deliverable through the shared Formam storage layer."""
    return storage.load_deliverable(deliverable_id)


def _display_width(deliverables: list[dict[str, Any]], field: str, minimum: int) -> int:
    """Compute a stable column width for terminal-readable deliverable output."""
    return max(
        minimum,
        max((len(str(deliverable.get(field, ""))) for deliverable in deliverables), default=0),
    )


def list_deliverables() -> list[dict[str, Any]]:
    """Print a read-only listing of canonical Formam deliverables."""
    deliverables = load_all_deliverables()

    if not deliverables:
        print(NO_DELIVERABLES_MESSAGE)
        return []

    id_width = _display_width(deliverables, "deliverable_id", len("DELIVERABLE"))
    goal_width = _display_width(deliverables, "goal_id", len("GOAL"))
    status_width = _display_width(deliverables, "status", len("STATUS"))

    print("\nDeliverables\n")
    print(
        f"{'DELIVERABLE':<{id_width}}  "
        f"{'GOAL':<{goal_width}}  "
        f"TITLE  "
        f"{'STATUS':<{status_width}}"
    )

    for deliverable in deliverables:
        print(
            f"{deliverable['deliverable_id']:<{id_width}}  "
            f"{deliverable['goal_id']:<{goal_width}}  "
            f"{deliverable['title']}  "
            f"{deliverable['status']:<{status_width}}"
        )

    return deliverables


def show_deliverable(deliverable_id: str) -> Optional[dict[str, Any]]:
    """Print one canonical deliverable by exact deliverable_id."""
    deliverable = load_deliverable(deliverable_id)
    if deliverable is None:
        print(f"{DELIVERABLE_NOT_FOUND_MESSAGE} {deliverable_id}")
        return None

    print(f"\nDeliverable: {deliverable['deliverable_id']}\n")
    print(f"Goal: {deliverable['goal_id']}")
    print(f"Title: {deliverable['title']}")
    print(f"Status: {deliverable['status']}")
    print(f"Created: {deliverable['created']}")
    print()
    print("Artifact Description")
    print("--------------------")

    artifact_description = deliverable["artifact_description"]
    if artifact_description:
        print(artifact_description)
    else:
        print("(none)")

    print()
    print("Dependencies")
    print("------------")

    dependencies = deliverable["dependencies"]
    if dependencies:
        for dependency in dependencies:
            print(f"- {dependency}")
    else:
        print("(none)")

    return deliverable


__all__ = [
    "DELIVERABLE_NOT_FOUND_MESSAGE",
    "load_deliverable",
    "NO_DELIVERABLES_MESSAGE",
    "load_all_deliverables",
    "list_deliverables",
    "show_deliverable",
]

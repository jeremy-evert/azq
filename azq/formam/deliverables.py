"""Thin presentation helpers for canonical Formam deliverable listings."""

from azq.formam import storage

NO_DELIVERABLES_MESSAGE = "No deliverables defined."


def load_all_deliverables() -> list[dict[str, str]]:
    """Load canonical deliverables through the shared Formam storage layer."""
    return storage.load_all_deliverables()


def _display_width(deliverables: list[dict[str, str]], field: str, minimum: int) -> int:
    """Compute a stable column width for terminal-readable deliverable output."""
    return max(
        minimum,
        max((len(str(deliverable.get(field, ""))) for deliverable in deliverables), default=0),
    )


def list_deliverables() -> list[dict[str, str]]:
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


__all__ = ["NO_DELIVERABLES_MESSAGE", "load_all_deliverables", "list_deliverables"]

"""Formam command routing for the top-level AZQ CLI."""

from azq.finis.cli import ensure_finis_storage_ready


def dispatch(argv: list[str]) -> bool:
    """Handle Formam commands and return True when one was dispatched."""
    if not argv or argv[0] != "form":
        return False

    if len(argv) < 2:
        print("Usage: azq form [build|list|show|map]")
        return True

    sub = argv[1]

    if sub == "build":
        if len(argv) < 3:
            print("Usage: azq form build <goal_id>")
            return True

        ensure_finis_storage_ready()

        from azq.formam.build import build_form

        build_form(argv[2])
        return True

    if sub == "list":
        from azq.formam.deliverables import list_deliverables

        list_deliverables()
        return True

    if sub == "show":
        if len(argv) < 3:
            print("Usage: azq form show <deliverable_id>")
            return True

        from azq.formam.deliverables import show_deliverable

        show_deliverable(argv[2])
        return True

    if sub == "map":
        if len(argv) < 3:
            print("Usage: azq form map <goal_id>")
            return True

        ensure_finis_storage_ready()

        from azq.formam.maps import form_map

        form_map(argv[2])
        return True

    print("Usage: azq form [build|list|show|map]")
    return True
